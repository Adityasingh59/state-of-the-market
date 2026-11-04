"""One evidence-backed brief per top pain theme (step 6).

    python -m pipeline.synthesize            # top 10 pain themes
    python -m pipeline.synthesize --top 5

Each brief: root cause, affected segment, which app handles it best, the unmet
need, and a product bet. Quotes are checked against the source reviews: a quote
that is not word-for-word in the cited review is dropped, so nothing is invented.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter

import pandas as pd

from . import config, llm
from .cost import BudgetExceeded, CostTracker
from .data import exploded, load_tagged, pain_gap, theme_names

SYSTEM = """You are a senior product analyst writing one section of a market report
on {category}. You get statistics computed from tagged app-store reviews and a
sample of the underlying reviews for ONE theme.

Write only what the evidence supports:
- Base every claim on the statistics or on reviews in the sample.
- Quotes must be copied exactly from a review's text, with that review's id.
- If the evidence is thin or contradictory, say so and lower confidence.
- best_handling_app must follow from the statistics (lowest pain rate, praise),
  not from general knowledge of the apps."""

SCHEMA = {
    "type": "object",
    "properties": {
        "headline": {"type": "string"},
        "root_cause": {"type": "string"},
        "affected_segments": {"type": "array", "items": {"type": "string"}},
        "best_handling_app": {"type": "string"},
        "best_handling_reason": {"type": "string"},
        "unmet_need": {"type": "string"},
        "product_bet": {"type": "string"},
        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
        "evidence": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "review_id": {"type": "string"},
                    "quote": {"type": "string"},
                    "shows": {"type": "string"},
                },
                "required": ["review_id", "quote", "shows"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["headline", "root_cause", "affected_segments", "best_handling_app",
                 "best_handling_reason", "unmet_need", "product_bet", "confidence", "evidence"],
    "additionalProperties": False,
}


def round_robin(df: pd.DataFrame, n: int) -> pd.DataFrame:
    """Up to n rows, taken evenly across apps."""
    shuffled = df.sample(frac=1, random_state=config.RANDOM_SEED)
    shuffled = shuffled.assign(_k=shuffled.groupby("app").cumcount())
    return shuffled.sort_values("_k").head(n).drop(columns="_k")


def _norm(s: str) -> str:
    return " ".join(str(s).split()).lower()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--pain-sample", type=int, default=120)
    ap.add_argument("--praise-sample", type=int, default=30)
    args = ap.parse_args()

    config.ensure_dirs()
    df = load_tagged()
    names = theme_names()
    gap = pain_gap(df, names)
    top = gap.sort_values("pain_reviews", ascending=False).head(args.top)
    ex = exploded(df)
    n_app = df.groupby("app").size()
    category = config.load_json(config.APPS_FILE).get("category", "consumer apps")
    tracker = CostTracker()
    briefs = []

    for row in top.itertuples():
        theme = row.theme
        m = ex[ex["theme"] == theme]
        per_app = pd.DataFrame({
            "reviews": n_app,
            "pain_mentions": m[m["is_pain"]].groupby("app").size(),
            "praise_mentions": m[m["sentiment"] == "positive"].groupby("app").size(),
            "avg_rating_when_mentioned": m.groupby("app")["rating"].mean().round(2),
        }).fillna(0)
        per_app["pain_rate"] = (per_app["pain_mentions"] / per_app["reviews"]).round(4)
        needs = Counter(x.lower() for x in m["unmet_need"] if isinstance(x, str) and x)
        segments = Counter(x.lower() for x in m["segment"] if isinstance(x, str) and x)

        pain_s = round_robin(m[m["is_pain"]], args.pain_sample)
        praise_s = round_robin(m[m["sentiment"] == "positive"], args.praise_sample)
        sample = pd.concat([pain_s, praise_s]).drop_duplicates("review_id")
        texts = {r.review_id: str(r.text)[:700] for r in sample.itertuples()}
        lines = [json.dumps({"id": r.review_id, "app": r.app, "rating": int(r.rating),
                             "sentiment": r.sentiment, "type": r.type, "text": texts[r.review_id]},
                            ensure_ascii=False) for r in sample.itertuples()]

        user = (
            f"Theme: {names.get(theme, theme)} ({theme})\n"
            f"Total reviews in study: {len(df)} across {df['app'].nunique()} apps, "
            f"{df['date'].min():%Y-%m} to {df['date'].max():%Y-%m}.\n"
            f"Pain reviews mentioning this theme: {row.pain_reviews} "
            f"({row.category_pain_rate:.1%} of all reviews). Feature requests: {row.feature_requests}.\n\n"
            f"Per-app statistics:\n{per_app.to_string()}\n\n"
            f"Most common unmet-need phrases: {needs.most_common(25)}\n"
            f"Stated user segments: {segments.most_common(15)}\n\n"
            f"Review sample ({len(lines)} reviews, one JSON per line):\n" + "\n".join(lines)
        )
        try:
            out = llm.call_json(
                tracker=tracker, step="synthesize", model=config.SYNTH_MODEL,
                system=SYSTEM.format(category=category), user=user, schema=SCHEMA,
                effort=config.SYNTH_EFFORT, max_tokens=16000, note=theme,
            )
        except BudgetExceeded as e:
            print(e)
            break
        except llm.ModelOutputError as e:
            print(f"  {theme}: {e}; skipped")
            continue

        kept = [ev for ev in out["evidence"]
                if ev["review_id"] in texts and _norm(ev["quote"]) in _norm(texts[ev["review_id"]])]
        dropped = len(out["evidence"]) - len(kept)
        brief = {"theme": theme, "theme_name": names.get(theme, theme), **out, "evidence": kept,
                 "stats": {"pain_reviews": int(row.pain_reviews),
                           "category_pain_rate": float(row.category_pain_rate),
                           "best_app_rate": float(row.best_app_rate),
                           "feature_requests": int(row.feature_requests)},
                 "quotes_dropped_unverified": dropped}
        briefs.append(brief)
        write_markdown(brief, per_app)
        print(f"  {theme}: brief written ({len(kept)} verified quotes, {dropped} dropped). "
              f"Spend ${tracker.spent:.2f}")

    with open(config.REPORT_DIR / "briefs.json", "w", encoding="utf-8") as f:
        json.dump(briefs, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(briefs)} briefs to {config.BRIEF_DIR}")


def write_markdown(b: dict, per_app: pd.DataFrame) -> None:
    s = b["stats"]
    lines = [
        f"# {b['theme_name']}: {b['headline']}",
        "",
        f"*{s['pain_reviews']} pain reviews ({s['category_pain_rate']:.1%} of all reviews); "
        f"even the best app sees it in {s['best_app_rate']:.1%} of its reviews. "
        f"Confidence: {b['confidence']}.*",
        "",
        f"**Root cause.** {b['root_cause']}",
        "",
        f"**Who it hurts.** {', '.join(b['affected_segments']) or 'Not stated in reviews.'}",
        "",
        f"**Best-handling app.** {b['best_handling_app']}: {b['best_handling_reason']}",
        "",
        f"**Unmet need.** {b['unmet_need']}",
        "",
        f"**Product bet.** {b['product_bet']}",
        "",
        "## Evidence",
        "",
        *[f"- \"{ev['quote']}\" (`{ev['review_id']}`): {ev['shows']}" for ev in b["evidence"]],
        "",
        "## Per-app numbers",
        "",
        per_app.to_markdown(),  # needs `tabulate` (in requirements.txt)
        "",
    ]
    (config.BRIEF_DIR / f"{b['theme']}.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
