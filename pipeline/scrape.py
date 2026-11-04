"""Pull reviews from the Apple App Store and Google Play, then merge.

    python -m pipeline.scrape                    # all apps, last 12 months
    python -m pipeline.scrape --months 18 --max-per-app 3000
    python -m pipeline.scrape --merge-only       # rebuild data/reviews.csv from data/raw

Apple: the public customer-reviews RSS feed returns at most 10 pages x 50
reviews per country, so we read several English-speaking storefronts.
Google Play: the open-source `google-play-scraper` package, newest first,
until the date cutoff or the per-app target is reached.
"""

from __future__ import annotations

import argparse
import time
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests
from google_play_scraper import Sort, reviews as play_reviews

from . import config

COLUMNS = ["review_id", "app", "store", "country", "date", "rating", "text", "version"]
APPLE_RSS = "https://itunes.apple.com/{cc}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"


def _label(entry: dict, key: str, default=None):
    v = entry.get(key)
    return v.get("label", default) if isinstance(v, dict) else default


def scrape_appstore(slug: str, app_id: str, countries: list[str], cutoff: datetime) -> list[dict]:
    rows: list[dict] = []
    for cc in countries:
        for page in range(1, 11):
            url = APPLE_RSS.format(cc=cc, page=page, app_id=app_id)
            try:
                r = requests.get(url, timeout=20)
                if r.status_code != 200:
                    break
                entries = r.json().get("feed", {}).get("entry", [])
            except (requests.RequestException, ValueError) as e:
                print(f"    {cc} page {page}: {e}")
                break
            if isinstance(entries, dict):
                entries = [entries]
            got = 0
            for e in entries:
                rating = _label(e, "im:rating")
                if rating is None:  # app-metadata entry, not a review
                    continue
                date = pd.to_datetime(_label(e, "updated"), utc=True, errors="coerce")
                if pd.isna(date) or date < cutoff:
                    continue
                title = _label(e, "title", "") or ""
                body = _label(e, "content", "") or ""
                rows.append({
                    "review_id": f"{slug}:a:{_label(e, 'id')}",
                    "app": slug, "store": "appstore", "country": cc,
                    "date": date.isoformat(), "rating": int(rating),
                    "text": f"{title}. {body}".strip() if title else body.strip(),
                    "version": _label(e, "im:version", ""),
                })
                got += 1
            if not entries or got == 0:
                break
            time.sleep(0.4)
    return rows


def scrape_play(slug: str, package: str, lang: str, country: str, cutoff: datetime, target: int) -> list[dict]:
    rows: list[dict] = []
    token = None
    while len(rows) < target:
        try:
            batch, token = play_reviews(
                package, lang=lang, country=country, sort=Sort.NEWEST,
                count=200, continuation_token=token,
            )
        except Exception as e:  # rate limits / layout changes: keep what we have
            print(f"    Play error after {len(rows)} reviews: {e}")
            break
        if not batch:
            break
        reached_cutoff = False
        for x in batch:
            ts = pd.Timestamp(x["at"])
            date = ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")
            if date < cutoff:
                reached_cutoff = True
                continue
            rows.append({
                "review_id": f"{slug}:g:{x['reviewId']}",
                "app": slug, "store": "play", "country": country,
                "date": date.isoformat(), "rating": int(x["score"]),
                "text": (x.get("content") or "").strip(),
                "version": x.get("reviewCreatedVersion") or x.get("appVersion") or "",
            })
        if reached_cutoff or token is None:
            break
        time.sleep(0.5)
    return rows


def merge(max_per_app: int, min_chars: int) -> pd.DataFrame:
    frames = [pd.read_csv(p, dtype={"version": str}) for p in sorted(config.RAW_DIR.glob("*.csv"))]
    if not frames:
        raise SystemExit("No raw files in data/raw. Run the scrape first.")
    df = pd.concat(frames, ignore_index=True)
    n0 = len(df)
    df["text"] = df["text"].fillna("").astype(str).str.strip()
    df = df.drop_duplicates("review_id")
    df = df.drop_duplicates(["app", "text"])          # same review in several storefronts
    df = df[df["text"].str.len() >= min_chars]        # "good", "ok" carry no theme
    # Cap per app with a seeded random sample so the date spread is preserved.
    df = df.sample(frac=1, random_state=config.RANDOM_SEED).groupby("app").head(max_per_app)
    df = df.sort_values(["app", "date"]).reset_index(drop=True)
    df[COLUMNS].to_csv(config.REVIEWS_FILE, index=False)
    print(f"\nMerged {n0} raw rows -> {len(df)} reviews in {config.REVIEWS_FILE}")
    print(df.groupby(["app", "store"]).size().unstack(fill_value=0).to_string())
    print(f"Date range: {df['date'].min()[:10]} to {df['date'].max()[:10]}")
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", type=int, default=12)
    ap.add_argument("--max-per-app", type=int, default=3000)
    ap.add_argument("--min-chars", type=int, default=20)
    ap.add_argument("--apps", nargs="*", help="only these slugs")
    ap.add_argument("--merge-only", action="store_true")
    args = ap.parse_args()

    config.ensure_dirs()
    if not args.merge_only:
        data = config.load_json(config.APPS_FILE)
        cutoff = datetime.now(timezone.utc) - timedelta(days=round(args.months * 30.44))
        for app in data["apps"]:
            if args.apps and app["slug"] not in args.apps:
                continue
            print(f"== {app['name']}")
            if app.get("appstore_id"):
                rows = scrape_appstore(app["slug"], str(app["appstore_id"]), data["appstore_countries"], cutoff)
                pd.DataFrame(rows, columns=COLUMNS).to_csv(config.RAW_DIR / f"{app['slug']}_appstore.csv", index=False)
                print(f"    App Store: {len(rows)}")
            if app.get("play_package") and app.get("android", True):
                # Over-fetch Play so the merged cap still has room after cleaning.
                rows = scrape_play(app["slug"], app["play_package"], data.get("play_lang", "en"),
                                   data.get("play_country", "us"), cutoff, target=args.max_per_app * 2)
                pd.DataFrame(rows, columns=COLUMNS).to_csv(config.RAW_DIR / f"{app['slug']}_play.csv", index=False)
                print(f"    Play: {len(rows)}")
    merge(args.max_per_app, args.min_chars)


if __name__ == "__main__":
    main()
