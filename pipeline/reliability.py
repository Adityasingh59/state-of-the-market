"""Reliability check: re-tag a 20% sample with a second model and prompt (step 5).

    python -m pipeline.reliability                # re-tag sample, then report
    python -m pipeline.reliability --report-only  # recompute the numbers

Writes reports/reliability.json with percent agreement and Cohen's kappa for
primary theme, sentiment and type, plus mean Jaccard overlap of theme sets.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter

import pandas as pd

from . import config
from .tag import run_tagging


def read_jsonl(path) -> pd.DataFrame:
    with open(path, encoding="utf-8") as f:
        return pd.DataFrame([json.loads(line) for line in f if line.strip()])


def cohen_kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def report() -> dict:
    if not config.CHECK_FILE.exists():
        print(f"No reliability tags in {config.CHECK_FILE.name} yet; nothing to compare.")
        return {}
    p = read_jsonl(config.TAGS_FILE).set_index("review_id")
    c = read_jsonl(config.CHECK_FILE).set_index("review_id")
    both = p.join(c, lsuffix="_a", rsuffix="_b", how="inner")
    out: dict = {
        "n_compared": int(len(both)),
        "primary_model": config.TAG_MODEL,
        "check_model": config.CHECK_MODEL,
        "fields": {},
    }
    for field in ("primary_theme", "sentiment", "type"):
        a, b = both[f"{field}_a"].tolist(), both[f"{field}_b"].tolist()
        out["fields"][field] = {
            "agreement": round(sum(x == y for x, y in zip(a, b)) / max(len(a), 1), 4),
            "cohen_kappa": round(cohen_kappa(a, b), 4),
        }
    jac = [
        len(set(x) & set(y)) / len(set(x) | set(y)) if (set(x) | set(y)) else 1.0
        for x, y in zip(both["themes_a"], both["themes_b"])
    ]
    out["fields"]["themes_jaccard_mean"] = round(sum(jac) / max(len(jac), 1), 4)

    # Per-theme agreement on primary theme: of reviews either run put in theme
    # T, the share where both did. Flags themes whose definition is fuzzy.
    per = {}
    for t in sorted(set(both["primary_theme_a"]) | set(both["primary_theme_b"])):
        in_a, in_b = both["primary_theme_a"] == t, both["primary_theme_b"] == t
        union = int((in_a | in_b).sum())
        per[t] = {"n": union, "agreement": round(int((in_a & in_b).sum()) / union, 4) if union else None}
    out["per_theme_primary"] = per

    config.REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.REPORT_DIR / "reliability.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out["fields"], indent=2))
    print(f"Compared {out['n_compared']} reviews. Saved {config.REPORT_DIR / 'reliability.json'}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fraction", type=float, default=config.CHECK_SAMPLE_FRACTION)
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()

    if not args.report_only:
        tagged = read_jsonl(config.TAGS_FILE)["review_id"]
        reviews = pd.read_csv(config.REVIEWS_FILE)
        reviews = reviews[reviews["review_id"].isin(set(tagged))]
        sample = reviews.sample(frac=args.fraction, random_state=config.RANDOM_SEED)
        run_tagging(sample, out_file=config.CHECK_FILE, model=config.CHECK_MODEL,
                    variant="B", step="reliability")
    report()


if __name__ == "__main__":
    main()
