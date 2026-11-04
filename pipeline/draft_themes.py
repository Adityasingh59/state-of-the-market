"""Draft the theme list from a 200-review sample (step 3 of the build plan).

    python -m pipeline.draft_themes            # writes config/themes.json, unfrozen

Read the result, merge or rename themes by hand, then set "frozen": true.
Full tagging refuses to run until the list is frozen, so tags stay consistent.
"""

from __future__ import annotations

import argparse
import json
import shutil

import pandas as pd

from . import config, llm
from .cost import CostTracker

SYSTEM = """You are a product analyst building a codebook for tagging app-store reviews.
You will read a sample of reviews from several competing apps in one category and
propose the themes that a tagger should use for every review in the full dataset.

Rules for the codebook:
- 12 to 16 themes, mutually exclusive in meaning, together covering almost all reviews.
- Themes describe what the review is ABOUT (a product area or user problem), not its
  sentiment. "Bank sync breaks" and "love the bank sync" share one theme.
- Each definition is one sentence a different person could apply consistently.
- Use snake_case ids. Always include a final theme with id "other".
- Prefer themes that separate apps from each other or reveal unmet needs."""

SCHEMA = {
    "type": "object",
    "properties": {
        "themes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "definition": {"type": "string"},
                    "sample_count": {"type": "integer"},
                },
                "required": ["id", "name", "definition", "sample_count"],
                "additionalProperties": False,
            },
        },
        "notes": {"type": "string"},
    },
    "required": ["themes", "notes"],
    "additionalProperties": False,
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    args = ap.parse_args()

    df = pd.read_csv(config.REVIEWS_FILE)
    # Even split across apps so one big app does not set the agenda.
    per_app = max(1, args.n // df["app"].nunique())
    sample = df.sample(frac=1, random_state=config.RANDOM_SEED).groupby("app").head(per_app)

    lines = [
        json.dumps({"app": r.app, "rating": int(r.rating), "text": str(r.text)[:800]}, ensure_ascii=False)
        for r in sample.itertuples()
    ]
    user = f"{len(lines)} reviews, one JSON object per line:\n\n" + "\n".join(lines)

    out = llm.call_json(
        tracker=CostTracker(), step="draft_themes", model=config.TAG_MODEL,
        system=SYSTEM, user=user, schema=SCHEMA, effort="high", max_tokens=16000,
    )

    if config.THEMES_FILE.exists():
        shutil.copy(config.THEMES_FILE, config.THEMES_FILE.with_suffix(".previous.json"))
    themes = [{"id": t["id"], "name": t["name"], "definition": t["definition"]} for t in out["themes"]]
    if not any(t["id"] == "other" for t in themes):
        themes.append({"id": "other", "name": "Other", "definition": "Anything that fits none of the themes above."})
    with open(config.THEMES_FILE, "w", encoding="utf-8") as f:
        json.dump({"frozen": False, "notes": out["notes"], "themes": themes}, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(themes)} draft themes to {config.THEMES_FILE} (previous list saved alongside).")
    for t in out["themes"]:
        print(f"  {t['sample_count']:>4}  {t['id']:<24} {t['definition']}")
    print('\nEdit the list, then set "frozen": true and run `python -m pipeline.tag`.')


if __name__ == "__main__":
    main()
