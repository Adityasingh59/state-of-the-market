# State of Budgeting Apps: what users still can't get, from 8 apps' reviews

*4 November 2026. 7,396 App Store and Google Play reviews scraped for 8 budgeting apps (5 Nov 2025 to 3 Nov 2026). 3,392 of them were tagged.*

## Summary

1. **Broken bank sync is the problem no app has solved.** It's the only theme in the top four for all 8 apps, and it's above 5% of reviews in every one. The median is 16.7% of an app's reviews, ranging from 9.3% for Goodbudget, which is mostly manual entry, to 32.7% for Simplifi. One review in five (676 of 3,392) is about sync, and those reviews average 2.5 stars against 3.4 for the rest.
2. **Updates are breaking long-time users' routines.** 257 complaint reviews (7.6%) blame a recent update or redesign. They cluster in YNAB (72), EveryDollar (62) and Monarch (43). Ease-of-use complaints reach 32.9% of YNAB's reviews.
3. **Users can't reach a human for support.** Support and trust complaints exceed 5% in 7 of 8 apps, and reach 18.8% for PocketGuard and Simplifi. The recurring ask is a real person, not a chatbot.
4. **App-specific gaps sit on top of that.** Rocket Money's subscription cancelling underdelivers (16.2% of its reviews). Goodbudget and EveryDollar have bugs and budget-math problems (33.7% and 21.2% performance complaints). Copilot is iOS only.

**Product bet: sync you can trust.** Warn users the moment a connection fails. Refill missing history after a reconnect. Remove duplicates automatically. And say up front which banks work. It's the one gap every app shares, and much of the duplicate, missing-data and wrong-balance trouble traces back to it.

*Pricing is left out on purpose. Price complaints appear for every paid app and don't point to a product gap. They are kept in the tags but excluded from the rankings and charts.*

## The data

| App | Reviews scraped | Tagged | Avg rating (tagged) | Share of tagged that are pain |
|---|---|---|---|---|
| Rocket Money | 3,000 | 1,207 | 3.22 | 52% |
| Monarch Money | 1,402 | 689 | 3.43 | 53% |
| YNAB | 1,003 | 422 | 3.20 | 60% |
| EveryDollar | 796 | 349 | 3.26 | 61% |
| Copilot Money (iOS only) | 495 | 262 | 3.71 | 50% |
| Simplifi by Quicken | 410 | 223 | 2.62 | 74% |
| PocketGuard | 204 | 154 | 2.98 | 64% |
| Goodbudget | 86 | 86 | 2.78 | 74% |
| **Total** | **7,396** | **3,392** | | **57%** |

Of the tagged reviews, 1,783 are from Google Play and 1,609 from the App Store.

**Pain rate by theme:** the share of an app's tagged reviews that are negative or mixed about a theme, or report a bug, a missing feature or a complaint there.

| Theme | Copilot | EveryDollar | Goodbudget | Monarch | PocketGuard | Rocket | Simplifi | YNAB | Median |
|---|---|---|---|---|---|---|---|---|---|
| **Bank connection and sync** | 20.2% | 13.2% | 9.3% | 19.4% | **27.9%** | 11.4% | **32.7%** | 14.0% | **16.7%** |
| Ease of use and design | 11.5% | 14.6% | 15.1% | 6.4% | 8.4% | 6.2% | 11.2% | **32.9%** | 11.4% |
| Customer support and trust | 12.2% | 8.0% | 4.7% | 10.3% | **18.8%** | 15.4% | **18.8%** | 9.5% | 11.3% |
| Performance and stability | 9.9% | 21.2% | **33.7%** | 7.8% | 10.4% | 8.3% | 15.7% | 11.6% | 11.0% |
| Budgeting method | 6.1% | 15.5% | **24.4%** | 5.1% | 4.5% | 2.0% | 7.2% | 9.5% | 6.7% |
| Bills and subscriptions | 3.1% | 1.7% | 1.2% | 2.3% | 1.3% | **16.2%** | 9.4% | 0.2% | 2.0% |

Charts: `figures/pain_gap.png`, `figures/heatmap.png`. Tables: `pain_gap.csv`, `theme_by_app.csv`.

## Theme briefs

### 1. Bank sync, the floor no one has fixed

The complaints repeat across apps: accounts silently disconnect, transactions arrive days late or not at all, reconnecting creates duplicates or wipes history, and some banks aren't supported at all. Several reviews say support blamed Plaid, a third party or a "known issue".

- "The team unfortunately never advises customers that they are having issues" (PocketGuard, `pocketguard:a:14485863334`)
- "No notice in the app that it happened" (Copilot, `copilot:a:14709853188`)
- "very often you need to reconnect your accounts and then the double transactions appear" (Copilot, `copilot:a:13811964764`)
- "every 1-2 months, I get like 50-100 DUPLICATE TRANSACTIONS that I then have to manually delete, 1 by 1" (EveryDollar, `everydollar:a:14085323678`)
- "all my historical data was removed" (Simplifi, `simplifi:a:13663923632`)
- "oh this is a known issue from months ago with absolutely no update what so ever" (Simplifi, `simplifi:g:27234668-e3e1-40c9-8214-768870f1ab48`)
- "I hate that I now spend at least an hour every week to manually enter transactions" (YNAB, `ynab:g:fc0b217d-83dc-429c-994a-6820249c7626`)
- "stop spending time on that AI nonsense nobody asked for. Fix your core issues first - missing transactions, breaking connections" (Monarch, `monarch:g:1e3fe6af-6b47-4095-b649-f0d9a1f138b7`)

**Why it matters:** "its value depends entirely on being able to sync with your financial institution" (PocketGuard, `pocketguard:a:14553856626`). When sync breaks, every budget, report and alert built on it is wrong.

**The unmet need**, in users' words:
- tell me when a connection fails
- refill the gap after I reconnect
- remove duplicates for me
- tell me before I pay whether my bank, credit union, Venmo, Cash App or store card works
- support non-US banks and multiple currencies

### 2. Updates that break what worked

- "More scrolling and more taps for what used to take one tap" (YNAB, `ynab:a:14158438732`)
- "locked out their customers from their OWN budgets with their latest update" (EveryDollar, `everydollar:g:762973c6-7716-44ad-9f0b-f0239202fa9b`)
- "But since it's last upgrade nothing works" (Goodbudget, `goodbudget:g:27a0cf11-aa5d-4792-b32c-9764d74a8c51`)
- "Why release an update when 2/3 of the tools aren’t even completed?" (PocketGuard, `pocketguard:a:14453021311`)

**The unmet need:** stability for loyal users. That means testing before release, a way to keep the old layout, and no locking of data the user still wants to edit.

### 3. Support that can't escalate

- "a Chatbot is not enough to help me" (Simplifi, `simplifi:a:14667818169`)

When a bank link or the budget's numbers break, users want a ticket that a person actually picks up.

### 4. App-specific gaps

- **Rocket Money:** subscription detection and cancellation miss many subscriptions (16.2% overall; higher among App Store reviewers).
- **Goodbudget and EveryDollar:** envelope totals and budget math break after updates, and EveryDollar's locked past months draw repeated complaints.
- **YNAB:** churn in the interface (32.9% ease-of-use complaints). Users ask for the progress bars back and fewer taps.
- **Copilot:** iOS only, and users ask for Android. It also has gaps tracking income categories and investment contributions.

### Who's happiest

Copilot has the highest average rating (3.71) and the lowest share of complaints (50%). Former Mint users and couples are the most vocal segments: Mint is still the benchmark they compare apps with, and couples want joint and individual views plus per-person roles.

## Method

1. **Collection.** A GitHub Actions workflow (`.github/workflows/scrape.yml`) runs `pipeline.find_ids` and `pipeline.scrape` on a GitHub runner. That's needed because this cloud session can't reach the app stores. It pulled the Apple customer-reviews feed from 7 English-language storefronts and Google Play (en, US) for the last 12 months. Store IDs were checked by hand (`config/apps.json`). Cleaning removed duplicates and reviews under 20 characters, leaving 7,396 reviews.
2. **Tagging.** 2,550 reviews were tagged by `pipeline.tag` with `claude-opus-5-5` in the `analyze.yml` workflow, at a cost of $6.09. The run stopped when the API account's credit ran out. Another 842 reviews come from a seeded sample that Claude tagged by reading each review in the working session. All tags use the frozen 15-theme codebook (`config/themes.json`). Where a review had both, the API tag is used.
3. **Reliability.** 448 reviews were tagged both ways, independently. The two agree on primary theme 80% of the time (Cohen's kappa 0.78), on sentiment 94% (kappa 0.89) and on review type 90% (kappa 0.87). Kappa is agreement after removing what chance alone would give; above 0.6 counts as substantial and above 0.8 as almost perfect.
4. **Analysis.** `python -m pipeline.analyze`. Pricing and "other" are excluded from the rankings. Every quote was checked word for word against its source review.

## Limits

- **Not every review is tagged.** 3,392 of the 7,396 are, and Goodbudget (86) and PocketGuard (154) have small samples, so small gaps between apps don't mean much. The cross-app pattern holds: sync is above 5% in all 8 apps.
- **Uneven samples.** Rocket Money makes up 36% of tagged reviews. Rates are calculated per app, so this doesn't skew comparisons between apps, but category-wide totals lean toward Rocket Money.
- **No synthesis briefs.** The per-theme briefs from `pipeline.synthesize` didn't run because the credit ran out. The briefs above were written by hand from the tagged data.
- **Free sources cap volume.** Apple's feed returns at most about 500 reviews per storefront.
- **Review bias.** App-store reviewers lean toward the very unhappy and the very happy.

## To finish the full run

Add API credit, then re-run the "Tag and analyze all reviews" workflow. It keeps the 2,550 reviews already tagged and pays only for the other 4,846. At the rate seen so far that's about $12 for tagging, plus roughly $4 for the reliability check and synthesis.
