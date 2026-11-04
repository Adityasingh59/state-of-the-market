"""Look up App Store IDs and Google Play package names for config/apps.json.

    python -m pipeline.find_ids           # print candidates only
    python -m pipeline.find_ids --write   # fill missing IDs with the top hit

Always check the picks by hand: a top search hit can be a different app.
"""

from __future__ import annotations

import argparse
import json

import requests
from google_play_scraper import search as play_search

from . import config


def appstore_candidates(term: str, country: str = "us", limit: int = 5) -> list[dict]:
    r = requests.get(
        "https://itunes.apple.com/search",
        params={"term": term, "entity": "software", "country": country, "limit": limit},
        timeout=20,
    )
    r.raise_for_status()
    return [
        {
            "id": str(x["trackId"]),
            "name": x.get("trackName"),
            "seller": x.get("sellerName"),
            "ratings": x.get("userRatingCount", 0),
        }
        for x in r.json().get("results", [])
    ]


def play_candidates(term: str, lang: str, country: str, n: int = 5) -> list[dict]:
    return [
        {"id": x["appId"], "name": x.get("title"), "seller": x.get("developer"),
         "ratings": x.get("ratings") or 0}
        for x in play_search(term, lang=lang, country=country, n_hits=n)
        if x.get("appId")
    ]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="fill empty IDs with the top hit")
    args = ap.parse_args()

    data = config.load_json(config.APPS_FILE)
    for app in data["apps"]:
        print(f"\n== {app['name']} ({app['slug']})")
        try:
            a = appstore_candidates(app["search"])
        except Exception as e:  # network / parse problems: report and move on
            print(f"  App Store lookup failed: {e}")
            a = []
        try:
            if not app.get("android", True):
                raise RuntimeError("marked iOS only, skipped")
            g = play_candidates(app["search"], data.get("play_lang", "en"), data.get("play_country", "us"))
        except Exception as e:
            print(f"  Play lookup failed: {e}")
            g = []
        for c in a:
            print(f"  [App Store] {c['id']:<12} {c['name']}  ({c['seller']}, {c['ratings']} ratings)")
        for c in g:
            print(f"  [Play]      {c['id']:<40} {c['name']}  ({c['seller']})")
        if args.write:
            if app.get("appstore_id") is None and a:
                app["appstore_id"] = a[0]["id"]
            if app.get("play_package") is None and g and app.get("android", True):
                app["play_package"] = g[0]["id"]
            print(f"  -> using appstore_id={app.get('appstore_id')} play_package={app.get('play_package')}")

    if args.write:
        with open(config.APPS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        print(f"\nWrote {config.APPS_FILE}. Check each pick before scraping.")


if __name__ == "__main__":
    main()
