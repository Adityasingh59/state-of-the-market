# State of the Market: mining app reviews for unmet needs

This project answers one question: **what are users asking for that no app in this category has built?**

It pulls 20,000+ public App Store and Google Play reviews across 8 to 10 competing apps. Claude tags each review against a fixed theme list, a second model re-tags a 20% sample to measure reliability, and the result is a ranked map of unmet needs with evidence for each one.

The default category is personal finance and budgeting apps (YNAB, Monarch, Copilot, Rocket Money and peers). To study a different category, edit `config/apps.json`.

## Pipeline

| Step | Command | API spend | Output |
|---|---|---|---|
| 1. App list | `python -m pipeline.find_ids --write` | none | store IDs in `config/apps.json` |
| 2. Scrape | `python -m pipeline.scrape` | none | `data/raw/*.csv`, `data/reviews.csv` |
| 3. Theme list | `python -m pipeline.draft_themes` | ~$0.10 | `config/themes.json` (draft) |
| 4. Tagging | `python -m pipeline.tag` | most of the budget | `data/tagged/tags_primary.jsonl` |
| 5. Reliability | `python -m pipeline.reliability` | ~20% of tagging | `reports/reliability.json` |
| 6. Synthesis | `python -m pipeline.synthesize` | ~$1 per theme | `reports/briefs/*.md` |
| 7. Analysis | `python -m pipeline.analyze` | none | `reports/summary.md`, `reports/figures/*.png` |
| Spend so far | `python -m pipeline.cost` | none | spend by step |

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # see .env.example for optional settings
```

## Running it

```bash
# 1. Find store IDs, then check every pick by hand (a top search hit can be the wrong app)
python -m pipeline.find_ids --write

# 2. Scrape the last 12 months, up to 3,000 reviews per app
python -m pipeline.scrape --months 12 --max-per-app 3000

# 3. Draft themes from a 200-review sample. Edit config/themes.json,
#    then set "frozen": true. Tagging will not run on an unfrozen list.
python -m pipeline.draft_themes

# 4. Test on 100 reviews and check the cost per review, then run everything.
#    The run can be stopped and restarted: tagged reviews are skipped.
python -m pipeline.tag --limit 100
python -m pipeline.cost
python -m pipeline.tag

# 5 to 7
python -m pipeline.reliability
python -m pipeline.synthesize --top 10
python -m pipeline.analyze
```

## Cost control

`pipeline/cost.py` checks the cap **before** each request:

- It reserves a worst-case cost for the call (every input token at the cache-write rate, plus the full `max_tokens` of output). If that would push spend past `SMM_BUDGET_USD` (default **$58**), the call is not sent and the step stops cleanly.
- After the call returns, the reservation is replaced with the real cost from `response.usage`. One line is written per call to `data/cost_ledger.jsonl`.
- The ledger covers every step and every run, so the cap applies to the whole project.

Prices are in `pipeline/config.py`. Check them against the [pricing page](https://platform.claude.com/docs/en/about-claude/pricing) before a large run. The ledger is an estimate, so also set a spend limit in the Anthropic Console.

If the budget runs short, run the steps in this order: tagging, then reliability, then synthesis. Trends need no API calls.

## Method

**Data.** For each review the pipeline keeps the app, store, storefront country, date, star rating, text (title plus body on the App Store) and app version. The App Store RSS feed returns at most 500 reviews per storefront, so the scraper reads several English-language storefronts. It drops duplicates, drops reviews under 20 characters, and caps each app with a seeded random sample, which keeps the date spread intact. Review text is clipped at 1,500 characters for tagging.

**Tags.** Each review gets:

- `primary_theme` and `themes`, from the frozen list of about 15 themes
- `sentiment`: positive, negative, mixed or neutral
- `type`: bug, feature_request, complaint, praise, pricing or other
- `segment`, only when the reviewer states it
- `unmet_need`, a short phrase naming what the reviewer wants and lacks

Tagging uses structured JSON output (`output_config.format`), so every response matches the schema and theme ids are limited to the frozen list. Reviews are sent 25 per request and 6 requests run in parallel. If a batch fails, it is split in half and retried.

**Reliability.** A 20% random sample is re-tagged by a different model (`claude-sonnet-5-5` by default) using a reworded prompt with the same codebook. `reports/reliability.json` reports percent agreement and Cohen's kappa for primary theme, sentiment and type, the mean Jaccard overlap of theme sets, and per-theme agreement, which flags themes with fuzzy definitions.

**Pain gap.** A review counts as *pain* for a theme when it mentions the theme and is negative or mixed, or is a bug report, feature request or complaint. For each theme and app, the pain rate is the app's pain reviews on that theme divided by all of the app's reviews. The **floor** is the lowest pain rate among apps with at least 200 reviews. A high floor means even the best app in the category has not solved the problem, and that is the unmet-need signal.

**Synthesis.** For each of the top pain themes, the synthesis model gets per-app statistics, the most common unmet-need phrases, and a sample of reviews balanced across apps. It returns the root cause, affected segments, best-handling app, unmet need, a product bet and supporting quotes. Each quote is checked word for word against the review it cites, and quotes that fail the check are dropped.

**Models.** Tagging and synthesis use `claude-opus-5-5`, the reliability check uses `claude-sonnet-5-5`, and model and effort can be changed in `pipeline/config.py` or `.env`. Requests turn on server-side refusal fallback (`fallbacks: "default"`). Turn it off with `SMM_FALLBACKS=0`.

## Limits to state in any write-up

- App-store reviewers are not a random sample of users. Unhappy users and very happy users are over-represented.
- Apple's feed only covers recent reviews per storefront, so App Store counts depend on how often each app is reviewed.
- Report the sample size, date range and agreement rate next to every finding.

## Layout

```
config/apps.json        apps, store IDs, storefronts
config/themes.json      theme codebook (freeze before tagging)
pipeline/config.py      paths, models, prices, budget cap
pipeline/cost.py        cost tracker and hard stop
pipeline/llm.py         Claude call with structured output
pipeline/find_ids.py    store ID lookup
pipeline/scrape.py      App Store RSS + Google Play scraper, merge
pipeline/draft_themes.py
pipeline/tag.py         batched, resumable tagging
pipeline/reliability.py second-model agreement check
pipeline/synthesize.py  evidence-backed theme briefs
pipeline/analyze.py     tables, pain-gap chart, heatmap, trend
```

Scraped data stays in `data/` and is git-ignored. Reports and charts are written to `reports/`.
