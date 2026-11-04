"""Counts, the pain-gap view, trends and charts (step 7). No API spend.

    python -m pipeline.analyze

Outputs in reports/: theme_by_app.csv, pain_gap.csv, trend.csv, summary.md and
figures/{heatmap,pain_gap,trend}.png. Every number in summary.md comes from the
tagged data.
"""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from . import config  # noqa: E402
from .data import EXCLUDED_THEMES, MIN_APP_REVIEWS, exploded, load_tagged, pain_gap, theme_app_table, theme_names  # noqa: E402

APP_NAMES = {a["slug"]: a["name"] for a in config.load_apps()}


def heatmap(t: pd.DataFrame, names: dict[str, str], order: list[str]) -> None:
    piv = (t.pivot(index="theme", columns="app", values="pain_rate").reindex(order).fillna(0) * 100)
    fig, ax = plt.subplots(figsize=(1.0 + 0.9 * len(piv.columns), 0.45 * len(piv) + 1.5))
    im = ax.imshow(piv.values, cmap="Reds", aspect="auto")
    ax.set_xticks(range(len(piv.columns)), [APP_NAMES.get(c, c) for c in piv.columns], rotation=35, ha="right")
    ax.set_yticks(range(len(piv)), [names.get(i, i) for i in piv.index])
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v = piv.values[i, j]
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=8,
                    color="white" if v > piv.values.max() * 0.6 else "black")
    ax.set_title("Share of each app's reviews complaining about a theme (%)")
    fig.colorbar(im, ax=ax, shrink=0.6)
    fig.tight_layout()
    fig.savefig(config.FIG_DIR / "heatmap.png", dpi=200)
    plt.close(fig)


def gap_chart(gap: pd.DataFrame) -> None:
    g = gap.head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 0.45 * len(g) + 1.5))
    ax.barh(g["theme_name"], g["worst_app_rate"] * 100, color="#f2c4c4", label="Worst app")
    ax.barh(g["theme_name"], g["best_app_rate"] * 100, color="#c0392b", label="Best app (the floor)")
    for y, (b, app) in enumerate(zip(g["best_app_rate"], g["best_app"])):
        ax.text(b * 100 + 0.2, y, f"{b:.1%} ({APP_NAMES.get(app, app)})", va="center", fontsize=8)
    ax.set_xlabel("% of an app's reviews that complain about the theme")
    ax.set_title("Pain gap: problems even the best app has not solved")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(config.FIG_DIR / "pain_gap.png", dpi=200)
    plt.close(fig)


def trend(df: pd.DataFrame, themes: list[str], names: dict[str, str]) -> pd.DataFrame:
    ex = exploded(df[df["is_pain"]])
    per_month = df.groupby("month").size()
    counts = ex[ex["theme"].isin(themes)].groupby(["month", "theme"]).size().unstack(fill_value=0)
    share = counts.div(per_month, axis=0).fillna(0)
    share = share[per_month.reindex(share.index) >= 50]  # skip near-empty months
    share.to_csv(config.REPORT_DIR / "trend.csv")

    fig, ax = plt.subplots(figsize=(9, 4.5))
    for t in themes:
        if t in share:
            ax.plot(share.index, share[t] * 100, marker="o", ms=3, label=names.get(t, t))
    ax.set_ylabel("% of the month's reviews")
    ax.set_title("Complaints over time, top themes")
    ax.tick_params(axis="x", rotation=45)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(config.FIG_DIR / "trend.png", dpi=200)
    plt.close(fig)

    # Growth: mean share in the last 3 months vs the months before.
    growth = {}
    if len(share) >= 6:
        recent, before = share.iloc[-3:].mean(), share.iloc[:-3].mean()
        for t in share.columns:
            growth[t] = {"recent_share": round(recent[t], 4), "earlier_share": round(before[t], 4),
                         "change_pts": round((recent[t] - before[t]) * 100, 2)}
    return pd.DataFrame(growth).T


def main() -> None:
    config.ensure_dirs()
    df = load_tagged()
    names = theme_names()

    t = theme_app_table(df)
    t = t[~t["theme"].isin(EXCLUDED_THEMES)]
    t.to_csv(config.REPORT_DIR / "theme_by_app.csv", index=False)
    gap = pain_gap(df, names)
    gap.to_csv(config.REPORT_DIR / "pain_gap.csv", index=False)

    by_volume = gap.sort_values("pain_reviews", ascending=False)
    heatmap(t, names, by_volume["theme"].tolist())
    gap_chart(gap)
    growth = trend(df, by_volume["theme"].head(5).tolist(), names)

    rel_path = config.REPORT_DIR / "reliability.json"
    rel = json.loads(rel_path.read_text()) if rel_path.exists() else None

    n_apps = df["app"].nunique()
    small = sorted(a for a, n in df.groupby("app").size().items() if n < MIN_APP_REVIEWS)
    lines = [
        "# Summary numbers",
        "",
        f"- Reviews analyzed: **{len(df):,}** across **{n_apps}** apps "
        f"({', '.join(APP_NAMES.get(a, a) for a in sorted(df['app'].unique()))})",
        f"- Date range: {df['date'].min():%Y-%m-%d} to {df['date'].max():%Y-%m-%d}",
        f"- Stores: " + ", ".join(f"{k} {v:,}" for k, v in df["store"].value_counts().items()),
        f"- Pain reviews (negative/mixed, bug, request or complaint): {df['is_pain'].mean():.1%}",
    ]
    if small:
        lines.append(f"- Left out of best-app comparisons (< {MIN_APP_REVIEWS} reviews): {', '.join(small)}")
    if rel:
        f = rel["fields"]
        lines += [
            f"- Reliability ({rel['n_compared']:,} reviews re-tagged by {rel['check_model']}): "
            f"primary theme agreement {f['primary_theme']['agreement']:.0%} "
            f"(kappa {f['primary_theme']['cohen_kappa']:.2f}), sentiment {f['sentiment']['agreement']:.0%}, "
            f"type {f['type']['agreement']:.0%}",
        ]
    lines += ["", "## Pain gap (sorted by the best app's complaint rate)", "",
              gap.to_markdown(index=False), ""]
    if not growth.empty:
        lines += ["## Growing complaints (last 3 months vs earlier)", "",
                  growth.sort_values("change_pts", ascending=False).to_markdown(), ""]
    (config.REPORT_DIR / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:8]))
    print(f"\nWrote reports/summary.md, CSVs and charts in {config.FIG_DIR}")


if __name__ == "__main__":
    main()
