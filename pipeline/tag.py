"""Tag every review with theme, sentiment, type and segment (step 4).

    python -m pipeline.tag --limit 100     # dry run on 100 reviews, check output + cost
    python -m pipeline.tag                 # full run; safe to stop and re-run

Resumable: reviews already in data/tagged/tags_primary.jsonl are skipped, so a
re-run only fills the gaps. Stops cleanly when the spend cap would be passed.
"""

from __future__ import annotations

import argparse
import json
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

import anthropic
import pandas as pd

from . import config, llm
from .cost import BudgetExceeded, CostTracker

SENTIMENTS = ["positive", "negative", "mixed", "neutral"]
TYPES = ["bug", "feature_request", "complaint", "praise", "pricing", "other"]

# Two wordings of the same task. The reliability check uses variant B with a
# different model, so agreement measures the codebook, not one prompt's habits.
INSTRUCTIONS = {
    "A": """You tag app-store reviews for a market study of {category}.
For EVERY review in the input, return one tag object with the same id.

Fields:
- primary_theme: the single theme the review is mostly about.
- themes: every theme the review clearly mentions (always includes primary_theme).
- sentiment: the reviewer's overall feeling: positive, negative, mixed or neutral.
- type: bug (something broken), feature_request (asks for something missing),
  complaint (unhappy, nothing broken or requested), praise, pricing (cost, plans,
  billing), or other.
- segment: the kind of user, only if the review states it (for example "couple",
  "freelancer", "former Mint user", "small business owner"); otherwise "".
- unmet_need: if the reviewer wants something the app does not do, a short
  phrase naming it (max 12 words); otherwise "".

Use only the theme ids below. Judge from the text; do not guess beyond it.""",
    "B": """Read each customer review of a {category} product and classify it with the
codebook below. Every input id must appear exactly once in your output.

Pick primary_theme as the main subject of the review, and list in themes all codebook
themes the review discusses. sentiment is the overall tone (positive / negative /
mixed / neutral). type is what kind of feedback it is: a defect report (bug), a request
for a missing capability (feature_request), dissatisfaction without a defect or request
(complaint), praise, feedback about price or billing (pricing), or other.
segment names the reviewer's situation only when stated outright, else "". unmet_need
is a phrase of at most 12 words for a capability they want and lack, else "".""",
}


def build_system(themes: list[dict], variant: str) -> str:
    category = config.load_json(config.APPS_FILE).get("category", "consumer apps")
    codebook = "\n".join(f"- {t['id']}: {t['name']}. {t['definition']}" for t in themes)
    return INSTRUCTIONS[variant].format(category=category) + "\n\nTheme codebook:\n" + codebook


def build_schema(themes: list[dict]) -> dict:
    ids = [t["id"] for t in themes]
    return {
        "type": "object",
        "properties": {
            "tags": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "primary_theme": {"type": "string", "enum": ids},
                        "themes": {"type": "array", "items": {"type": "string", "enum": ids}},
                        "sentiment": {"type": "string", "enum": SENTIMENTS},
                        "type": {"type": "string", "enum": TYPES},
                        "segment": {"type": "string"},
                        "unmet_need": {"type": "string"},
                    },
                    "required": ["id", "primary_theme", "themes", "sentiment", "type", "segment", "unmet_need"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["tags"],
        "additionalProperties": False,
    }


def load_done(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with open(path, encoding="utf-8") as f:
        return {json.loads(line)["review_id"] for line in f if line.strip()}


def run_tagging(
    reviews: pd.DataFrame,
    *,
    out_file: Path,
    model: str,
    variant: str,
    step: str,
    batch_size: int = config.TAG_BATCH_SIZE,
    concurrency: int = config.TAG_CONCURRENCY,
) -> None:
    themes = config.load_themes()
    system = build_system(themes, variant)
    schema = build_schema(themes)
    valid_ids = {t["id"] for t in themes}
    tracker = CostTracker()

    done = load_done(out_file)
    todo = reviews[~reviews["review_id"].isin(done)]
    print(f"{step}: {len(done)} already tagged, {len(todo)} to go, model {model}, "
          f"budget left ${tracker.remaining():.2f}")
    if todo.empty:
        return

    records = todo[["review_id", "app", "rating", "text"]].to_dict("records")
    batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
    write_lock = threading.Lock()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    stats = {"tagged": 0, "missing": 0, "failed_batches": 0}
    stop = threading.Event()
    t0 = time.time()

    def tag_batch(batch: list[dict], depth: int = 0) -> None:
        if stop.is_set():
            return
        lines = [
            json.dumps({"id": r["review_id"], "app": r["app"], "rating": int(r["rating"]),
                        "text": str(r["text"])[: config.MAX_REVIEW_CHARS]}, ensure_ascii=False)
            for r in batch
        ]
        user = f"Tag these {len(batch)} reviews (one JSON object per line):\n\n" + "\n".join(lines)
        try:
            out = llm.call_json(
                tracker=tracker, step=step, model=model, system=system, user=user,
                schema=schema, effort=config.TAG_EFFORT, max_tokens=config.TAG_MAX_TOKENS,
            )
        except BudgetExceeded as e:
            if not stop.is_set():
                print(f"\n{e}")
            stop.set()
            return
        except (llm.ModelOutputError, anthropic.APIError) as e:
            # Split once and retry halves; a single bad review then fails alone.
            if len(batch) > 1 and depth < 2:
                mid = len(batch) // 2
                tag_batch(batch[:mid], depth + 1)
                tag_batch(batch[mid:], depth + 1)
            else:
                stats["failed_batches"] += 1
                print(f"\n  batch of {len(batch)} failed: {e}")
            return

        wanted = {r["review_id"] for r in batch}
        seen: set[str] = set()
        rows = []
        for t in out.get("tags", []):
            rid = t.get("id")
            if rid not in wanted or rid in seen:
                continue
            seen.add(rid)
            themes_list = [x for x in dict.fromkeys(t["themes"]) if x in valid_ids]
            if t["primary_theme"] not in themes_list:
                themes_list.insert(0, t["primary_theme"])
            rows.append({
                "review_id": rid, "run": variant, "model": model,
                "primary_theme": t["primary_theme"], "themes": themes_list,
                "sentiment": t["sentiment"], "type": t["type"],
                "segment": t["segment"].strip(), "unmet_need": t["unmet_need"].strip(),
            })
        with write_lock:
            with open(out_file, "a", encoding="utf-8") as f:
                for row in rows:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
            stats["tagged"] += len(rows)
            stats["missing"] += len(wanted) - len(seen)
            rate = stats["tagged"] / max(time.time() - t0, 1)
            print(f"\r  tagged {stats['tagged']}/{len(records)}  spent ${tracker.spent:.2f}  "
                  f"({rate:.1f}/s)", end="", flush=True)

    # Submit lazily so a budget stop does not leave hundreds of queued batches.
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        it = iter(batches)
        running = set()
        for b in it:
            running.add(pool.submit(tag_batch, b))
            if len(running) >= concurrency * 2:
                finished, running = wait(running, return_when=FIRST_COMPLETED)
                for fut in finished:
                    fut.result()
            if stop.is_set():
                break
        for fut in running:
            fut.result()

    print(f"\n{step} done: {stats['tagged']} tagged, {stats['missing']} not returned, "
          f"{stats['failed_batches']} failed batches. Total spend ${tracker.spent:.2f}.")
    if stats["missing"] or stats["failed_batches"]:
        print("Re-run the same command to retry the gaps.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, help="tag only the first N untagged reviews (test run)")
    ap.add_argument("--apps", nargs="*")
    args = ap.parse_args()

    config.ensure_dirs()
    df = pd.read_csv(config.REVIEWS_FILE)
    if args.apps:
        df = df[df["app"].isin(args.apps)]
    # Interleave apps so a budget stop still leaves every app represented.
    df = df.sample(frac=1, random_state=config.RANDOM_SEED)
    if args.limit:
        df = df[~df["review_id"].isin(load_done(config.TAGS_FILE))].head(args.limit)
    run_tagging(df, out_file=config.TAGS_FILE, model=config.TAG_MODEL, variant="A", step="tag")


if __name__ == "__main__":
    main()
