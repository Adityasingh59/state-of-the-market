"""Shared settings: paths, models, prices and the spend cap.

Edit this file (or set the matching environment variables) before a run.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
TAG_DIR = DATA_DIR / "tagged"
REPORT_DIR = ROOT / "reports"
FIG_DIR = REPORT_DIR / "figures"
BRIEF_DIR = REPORT_DIR / "briefs"

APPS_FILE = CONFIG_DIR / "apps.json"
THEMES_FILE = CONFIG_DIR / "themes.json"

REVIEWS_FILE = DATA_DIR / "reviews.csv"          # merged, cleaned reviews
TAGS_FILE = TAG_DIR / "tags_primary.jsonl"       # full tagging run
CHECK_FILE = TAG_DIR / "tags_check.jsonl"        # reliability re-tag
COST_LEDGER = DATA_DIR / "cost_ledger.jsonl"     # one line per API call

# ---------------------------------------------------------------------------
# Spend cap. Every API call is checked against this BEFORE it is sent, using a
# worst-case estimate, so the real total cannot pass it.
# ---------------------------------------------------------------------------
BUDGET_USD = float(os.environ.get("SMM_BUDGET_USD", "58.00"))

# ---------------------------------------------------------------------------
# Models. Tagging and synthesis use the top-tier model; the reliability check
# uses a different model (and a reworded prompt) so agreement is meaningful.
# ---------------------------------------------------------------------------
TAG_MODEL = os.environ.get("SMM_TAG_MODEL", "claude-opus-5-5")
CHECK_MODEL = os.environ.get("SMM_CHECK_MODEL", "claude-sonnet-5-5")
SYNTH_MODEL = os.environ.get("SMM_SYNTH_MODEL", "claude-opus-5-5")

TAG_EFFORT = os.environ.get("SMM_TAG_EFFORT", "low")      # classification: low is enough
SYNTH_EFFORT = os.environ.get("SMM_SYNTH_EFFORT", "high")  # judgment-heavy step

# Server-side refusal fallback (re-runs a declined request on another model in
# the same call). Set SMM_FALLBACKS=0 to turn it off.
USE_FALLBACKS = os.environ.get("SMM_FALLBACKS", "1") != "0"
FALLBACK_BETA = "server-side-fallback-2026-07-01"

# USD per million tokens: (input, output, cache_read, cache_write_5m).
# Check https://platform.claude.com/docs/en/about-claude/pricing before a run.
PRICES: dict[str, tuple[float, float, float, float]] = {
    "claude-opus-5-5": (4.00, 20.00, 0.20, 5.00),
    "claude-sonnet-5-5": (2.00, 10.00, 0.20, 2.50),
    "claude-haiku-5-5": (0.10, 0.50, 0.01, 0.125),
    "claude-opus-5": (5.00, 25.00, 0.50, 6.25),
    "claude-opus-4-8": (5.00, 25.00, 0.50, 6.25),
    "claude-sonnet-5": (2.00, 10.00, 0.20, 2.50),
    "claude-fable-5-1": (10.00, 50.00, 0.25, 12.50),
}
# Used for any model not listed above (for example a fallback model): priced
# as the most expensive tier so the ledger never under-reports.
UNKNOWN_MODEL_PRICE = (10.00, 50.00, 1.00, 12.50)

# Tagging batch shape.
TAG_BATCH_SIZE = int(os.environ.get("SMM_TAG_BATCH_SIZE", "25"))
TAG_CONCURRENCY = int(os.environ.get("SMM_TAG_CONCURRENCY", "6"))
TAG_MAX_TOKENS = 16000
MAX_REVIEW_CHARS = 1500  # long reviews are clipped (noted in the README)

CHECK_SAMPLE_FRACTION = 0.20
RANDOM_SEED = 42


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_apps() -> list[dict]:
    return load_json(APPS_FILE)["apps"]


def load_themes(allow_draft: bool = False) -> list[dict]:
    """Return the frozen theme list. Refuses an unfrozen list unless allowed."""
    data = load_json(THEMES_FILE)
    if not data.get("frozen") and not allow_draft:
        raise SystemExit(
            f"{THEMES_FILE.name} is not frozen. Review the themes, then set "
            '"frozen": true before running full tagging.'
        )
    return data["themes"]


def ensure_dirs() -> None:
    for d in (DATA_DIR, RAW_DIR, TAG_DIR, REPORT_DIR, FIG_DIR, BRIEF_DIR):
        d.mkdir(parents=True, exist_ok=True)
