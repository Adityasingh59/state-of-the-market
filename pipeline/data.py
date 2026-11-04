"""Load reviews joined to their tags, plus the shared metric definitions."""

from __future__ import annotations

import json

import pandas as pd

from . import config

# A review counts as "pain" for a theme when it is unhappy about it or asks for
# something there. The same definition feeds the charts and the synthesis.
PAIN_SENTIMENTS = {"negative", "mixed"}
PAIN_TYPES = {"bug", "feature_request", "complaint"}

MIN_APP_REVIEWS = 200  # apps below this are left out of "best app" comparisons


def load_tagged() -> pd.DataFrame:
    reviews = pd.read_csv(config.REVIEWS_FILE)
    with open(config.TAGS_FILE, encoding="utf-8") as f:
        tags = pd.DataFrame([json.loads(line) for line in f if line.strip()])
    df = reviews.merge(tags, on="review_id", how="inner")
    df["date"] = pd.to_datetime(df["date"], utc=True, format="ISO8601")
    df["month"] = df["date"].dt.strftime("%Y-%m")
    df["is_pain"] = df["sentiment"].isin(PAIN_SENTIMENTS) | df["type"].isin(PAIN_TYPES)
    return df


def exploded(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (review, theme mentioned)."""
    return df.explode("themes").rename(columns={"themes": "theme"})


def theme_app_table(df: pd.DataFrame) -> pd.DataFrame:
    """Pain rate per app x theme: pain reviews mentioning the theme / app's reviews."""
    ex = exploded(df[df["is_pain"]])
    pain = ex.groupby(["app", "theme"]).size().rename("pain_reviews").reset_index()
    n_app = df.groupby("app").size().rename("app_reviews")
    pain = pain.join(n_app, on="app")
    pain["pain_rate"] = pain["pain_reviews"] / pain["app_reviews"]
    return pain


def pain_gap(df: pd.DataFrame, theme_names: dict[str, str]) -> pd.DataFrame:
    """Per theme: how common the pain is, and how well the BEST app handles it.

    best_app_rate is the lowest pain rate among apps with enough reviews. A high
    floor means no app in the category has solved it: the unmet-need signal.
    """
    t = theme_app_table(df)
    n_app = df.groupby("app").size()
    big_apps = set(n_app[n_app >= MIN_APP_REVIEWS].index)
    full = (t.pivot(index="theme", columns="app", values="pain_rate")
             .reindex(columns=sorted(big_apps)).fillna(0.0))

    ex = exploded(df)
    rows = []
    for theme in full.index:
        if theme == "other":
            continue
        rates = full.loc[theme]
        mentions = ex[ex["theme"] == theme]
        rows.append({
            "theme": theme,
            "theme_name": theme_names.get(theme, theme),
            "pain_reviews": int(t.loc[t["theme"] == theme, "pain_reviews"].sum()),
            "category_pain_rate": round(t.loc[t["theme"] == theme, "pain_reviews"].sum() / len(df), 4),
            "best_app": rates.idxmin(),
            "best_app_rate": round(rates.min(), 4),
            "worst_app": rates.idxmax(),
            "worst_app_rate": round(rates.max(), 4),
            "feature_requests": int((mentions["type"] == "feature_request").sum()),
            "avg_rating_when_mentioned": round(mentions["rating"].mean(), 2),
        })
    return pd.DataFrame(rows).sort_values("best_app_rate", ascending=False).reset_index(drop=True)


def theme_names() -> dict[str, str]:
    return {t["id"]: t["name"] for t in config.load_themes(allow_draft=True)}
