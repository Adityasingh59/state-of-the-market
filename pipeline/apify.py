"""Get reviews from the Apify actor "The Better App Store Reviews Scraper".

Actor: https://apify.com/betterscrapers/the-better-app-store-reviews-scraper
(actor id KBD93wWVGA0u1JnMz)

Two ways to use it:

1. Run it in the Apify console, export the dataset (JSON or CSV), save the
   files in data/apify/, then import:

       python -m pipeline.apify import data/apify/*.json
       python -m pipeline.apify import data/apify/ynab.json --app ynab   # one app per file

2. Start the run from here. Copy the input JSON from the console's Input tab
   (JSON view) into config/apify_input.json, set APIFY_TOKEN, then:

       python -m pipeline.apify run

Both end by rebuilding data/reviews.csv with the same cleaning as the built-in
scraper (dedupe, 12-month window, 20-char minimum, per-app cap).

The importer does not assume one fixed output layout. It recognises the usual
field names (text/review/content, rating/score, date/updated, ...) and prints
which source field it used for each column, so check that mapping on the
first import.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests

from . import config
from .scrape import COLUMNS, merge

ACTOR_ID = "KBD93wWVGA0u1JnMz"
API = "https://api.apify.com/v2"
APIFY_DIR = config.DATA_DIR / "apify"
INPUT_FILE = config.CONFIG_DIR / "apify_input.json"

# Candidate source fields for each output column, in priority order.
ALIASES = {
    "id": ["id", "reviewId", "review_id", "reviewID"],
    "title": ["title", "reviewTitle", "review_title"],
    "text": ["text", "review", "content", "body", "reviewText", "review_text", "comment"],
    "rating": ["rating", "score", "stars", "ratingValue", "rate"],
    "date": ["date", "updatedAt", "updated_at", "updated", "reviewDate", "review_date", "at", "publishedAt", "createdAt", "published"],
    "version": ["version", "appVersion", "app_version", "reviewCreatedVersion"],
    "country": ["country", "countryCode", "country_code", "storefront", "store_country"],
    "app": ["appId", "app_id", "appID", "trackId", "applicationId", "appUrl", "app_url", "url",
            "appName", "app_name", "appTitle", "startUrl"],
}


def _flatten(item: dict, prefix: str = "") -> dict:
    out = {}
    for k, v in item.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(_flatten(v, key + "."))
        else:
            out[key] = v
    return out


def read_export(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, dtype=str).to_dict("records")
    text = text.strip()
    if text.startswith("["):
        return json.loads(text)
    return [json.loads(line) for line in text.splitlines() if line.strip()]  # JSONL


def pick(columns: list[str], field: str) -> str | None:
    lower = {c.lower(): c for c in columns}
    for name in ALIASES[field]:
        if name.lower() in lower:
            return lower[name.lower()]
    # Fall back to flattened names such as "review.text" or "user.rating".
    for name in ALIASES[field]:
        for c in columns:
            if c.lower().endswith("." + name.lower()):
                return c
    return None


def match_app(value, apps: list[dict]) -> str | None:
    """Map whatever the export uses for the app (id, URL, name) to our slug."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    v = str(value).lower()
    for a in apps:
        if a.get("appstore_id") and re.search(rf"(^|\D){a['appstore_id']}(\D|$)", v):
            return a["slug"]
        if a.get("play_package") and a["play_package"].lower() in v:
            return a["slug"]
    for a in apps:
        name = a["name"].lower()
        if v == name or v == a["slug"] or name in v:
            return a["slug"]
    return None


def to_rows(items: list[dict], forced_app: str | None, apps: list[dict]) -> tuple[pd.DataFrame, dict]:
    df = pd.DataFrame([_flatten(i) for i in items])
    cols = list(df.columns)
    mapping = {f: pick(cols, f) for f in ALIASES}
    if mapping["text"] is None or mapping["rating"] is None or mapping["date"] is None:
        raise SystemExit(
            f"Could not find review text, rating and date fields. Columns in the export: {cols}\n"
            "Add the right names to ALIASES in pipeline/apify.py."
        )

    if forced_app:
        slugs = pd.Series(forced_app, index=df.index)
    elif mapping["app"]:
        slugs = df[mapping["app"]].map(lambda v: match_app(v, apps))
    else:
        raise SystemExit("The export has no app field. Import one file per app with --app <slug>.")

    title = df[mapping["title"]].fillna("").astype(str) if mapping["title"] else ""
    body = df[mapping["text"]].fillna("").astype(str)
    text = (title + ". " + body).where(title.str.len() > 0, body) if mapping["title"] else body
    ids = df[mapping["id"]].astype(str) if mapping["id"] else pd.Series(
        [hashlib.sha1(f"{t}|{d}".encode()).hexdigest()[:16] for t, d in zip(body, df[mapping["date"]])], index=df.index)

    out = pd.DataFrame({
        "app": slugs,
        "store": "appstore",
        "country": df[mapping["country"]].fillna("").astype(str).str.lower() if mapping["country"] else "",
        "date": pd.to_datetime(df[mapping["date"]], utc=True, errors="coerce", format="mixed"),
        "rating": pd.to_numeric(df[mapping["rating"]], errors="coerce"),
        "text": text.str.strip(),
        "version": df[mapping["version"]].fillna("").astype(str) if mapping["version"] else "",
    })
    out["review_id"] = out["app"].fillna("unknown") + ":a:" + ids
    return out, mapping


def import_files(paths: list[Path], forced_app: str | None, months: int, max_per_app: int, min_chars: int) -> None:
    config.ensure_dirs()
    apps = config.load_apps()
    cutoff = datetime.now(timezone.utc) - timedelta(days=round(months * 30.44))
    frames = []
    for p in paths:
        rows, mapping = to_rows(read_export(p), forced_app, apps)
        print(f"{p.name}: {len(rows)} items. Field mapping: "
              + ", ".join(f"{k}<-{v}" for k, v in mapping.items() if v))
        frames.append(rows)
    df = pd.concat(frames, ignore_index=True)

    unmatched = df["app"].isna().sum()
    if unmatched:
        print(f"  {unmatched} reviews did not match any app in config/apps.json and were skipped. "
              "Fill in appstore_id values, or import per app with --app.")
    bad = df["date"].isna() | df["rating"].isna()
    if bad.sum():
        print(f"  {bad.sum()} reviews had no readable date or rating and were skipped.")
    df = df[df["app"].notna() & ~bad]
    old = (df["date"] < cutoff).sum()
    df = df[df["date"] >= cutoff]
    print(f"  {old} reviews older than {months} months dropped.")

    df["date"] = df["date"].map(lambda d: d.isoformat())
    df["rating"] = df["rating"].round().astype(int)
    for slug, g in df.groupby("app"):
        g[COLUMNS].to_csv(config.RAW_DIR / f"{slug}_appstore.csv", index=False)
        print(f"  {slug}: {len(g)} App Store reviews -> data/raw/{slug}_appstore.csv")
    merge(max_per_app, min_chars)


def run_actor(token: str, poll_seconds: int = 15) -> Path:
    if not INPUT_FILE.exists():
        raise SystemExit(
            f"Missing {INPUT_FILE}. In the Apify console open the actor's Input tab, switch to "
            "JSON, set it up for your apps, and paste it into that file."
        )
    run_input = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{API}/acts/{ACTOR_ID}/runs", json=run_input, headers=headers, timeout=60)
    r.raise_for_status()
    run = r.json()["data"]
    print(f"Started run {run['id']} (console: https://console.apify.com/actors/runs/{run['id']})")
    while run["status"] in ("READY", "RUNNING"):
        time.sleep(poll_seconds)
        run = requests.get(f"{API}/actor-runs/{run['id']}", headers=headers, timeout=60).json()["data"]
        print(f"  status {run['status']}")
    if run["status"] != "SUCCEEDED":
        raise SystemExit(f"Run ended with status {run['status']}.")
    items = requests.get(f"{API}/datasets/{run['defaultDatasetId']}/items",
                         params={"format": "json", "clean": "true"}, headers=headers, timeout=300)
    items.raise_for_status()
    APIFY_DIR.mkdir(parents=True, exist_ok=True)
    out = APIFY_DIR / f"run_{run['id']}.json"
    out.write_text(items.text, encoding="utf-8")
    print(f"Saved {len(items.json())} items to {out}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    imp = sub.add_parser("import", help="import exported dataset files")
    imp.add_argument("files", nargs="+", type=Path)
    imp.add_argument("--app", help="slug from config/apps.json, when a file holds one app")
    sub.add_parser("run", help="start the actor with config/apify_input.json, then import")
    for p in (imp, sub.choices["run"]):
        p.add_argument("--months", type=int, default=12)
        p.add_argument("--max-per-app", type=int, default=3000)
        p.add_argument("--min-chars", type=int, default=20)
    args = ap.parse_args()

    if args.cmd == "run":
        token = os.environ.get("APIFY_TOKEN")
        if not token:
            sys.exit("Set APIFY_TOKEN (Apify console > Settings > API & Integrations).")
        files, forced = [run_actor(token)], None
    else:
        files, forced = args.files, args.app
    import_files(files, forced, args.months, args.max_per_app, args.min_chars)


if __name__ == "__main__":
    main()
