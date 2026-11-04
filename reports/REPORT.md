# State of Budgeting Apps: what users still can't get, from 8 apps' reviews

*4 November 2026. All 7,396 App Store and Google Play reviews for 8 budgeting apps from the last 12 months (5 Nov 2025 to 3 Nov 2026), every one tagged.*

## Summary

1. **Broken bank sync is the problem no app has solved.** It's complained about in more than 5% of reviews for every one of the 8 apps. The median is 16.4% of an app's reviews, ranging from 9.3% for Goodbudget, which is mostly manual entry, to 27.9% for PocketGuard. Sync comes up in 1,327 reviews (18%), and those average 2.4 stars against 3.5 for the rest. Among international users the share is 77%.
2. **Updates are breaking long-time users' routines.** 507 complaint reviews (6.9%) blame a recent update or redesign. They cluster in EveryDollar (18% of its reviews), Goodbudget (16%) and YNAB (15%). The most-repeated requests are "fewer taps" (39), "stable UI" (24) and "edit past months" (23).
3. **Users can't reach a human for support.** Support and trust complaints exceed 5% in 7 of 8 apps, peaking at 20.1% for PocketGuard. Requests for "human support" come from 6 apps, and requests to opt out of AI features from 5.
4. **App-specific gaps sit on top of that.** Rocket Money's subscription cancelling underdelivers: 26% of its reviews are about subscriptions, with 40 requests for cancellation that works and 31 for detecting every subscription. Goodbudget and EveryDollar have bugs and budget-math problems. YNAB's changes to its interface draw complaints in 30.5% of its reviews.

**Product bet: sync you can trust.** Warn users the moment a connection fails. Refill missing history after a reconnect. Remove duplicates automatically, which users ask for in 7 of the 8 apps. And say up front which banks, credit unions, payment apps and non-US institutions work. It's the one gap every app shares, and much of the duplicate, missing-data and wrong-balance trouble traces back to it.

*Pricing is left out on purpose. Price complaints appear for every paid app and don't point to a product gap. They are kept in the tags but excluded from the rankings and charts.*

## The data

| App | Reviews | App Store / Play | Avg rating | Share that are pain |
|---|---|---|---|---|
| Rocket Money | 3,000 | 326 / 2,674 | 3.42 | 46% |
| Monarch Money | 1,402 | 586 / 816 | 3.43 | 53% |
| YNAB | 1,003 | 620 / 383 | 3.29 | 56% |
| EveryDollar | 796 | 456 / 340 | 3.30 | 63% |
| Copilot Money (iOS only) | 495 | 495 / 0 | 3.52 | 54% |
| Simplifi by Quicken | 410 | 225 / 185 | 2.64 | 74% |
| PocketGuard | 204 | 96 / 108 | 3.03 | 64% |
| Goodbudget | 86 | 42 / 44 | 2.78 | 74% |
| **Total** | **7,396** | **2,846 / 4,550** | | **54%** |

**Pain rate by theme:** the share of an app's reviews that are negative or mixed about a theme, or report a bug, a missing feature or a complaint there.

| Theme | Copilot | EveryDollar | Goodbudget | Monarch | PocketGuard | Rocket | Simplifi | YNAB | Median |
|---|---|---|---|---|---|---|---|---|---|
| **Bank connection and sync** | 21.4% | 11.3% | 9.3% | 20.4% | **27.9%** | 11.3% | **26.3%** | 12.4% | **16.4%** |
| Ease of use and design | 10.9% | 15.1% | 15.1% | 5.6% | 7.8% | 4.6% | 12.2% | **30.5%** | 11.6% |
| Customer support and trust | 11.1% | 7.7% | 4.7% | 8.6% | **20.1%** | 13.2% | 16.3% | 7.4% | 9.9% |
| Performance and stability | 8.3% | 18.0% | **33.7%** | 5.5% | 9.8% | 5.6% | 14.9% | 5.9% | 9.1% |
| Budgeting method | 5.5% | 17.2% | **24.4%** | 4.0% | 3.4% | 1.2% | 5.6% | 7.9% | 5.6% |
| Categorization | 12.7% | 3.1% | 2.3% | 5.1% | 4.9% | 1.7% | **14.1%** | 2.8% | 4.0% |
| Bills and subscriptions | 2.4% | 1.6% | 1.2% | 2.1% | 1.5% | **11.9%** | 8.3% | 0.5% | 1.9% |

Charts: `figures/pain_gap.png`, `figures/heatmap.png`. Tables: `pain_gap.csv`, `theme_by_app.csv`.

## Theme briefs

### 1. Bank sync, the floor no one has fixed

The complaints repeat across apps: accounts silently disconnect, transactions arrive days late or not at all, reconnecting creates duplicates or wipes history, and some banks aren't supported at all.

The most common sync requests:
- automatic duplicate removal (22 reviews, 7 apps)
- faster sync (19)
- Cash App connection (16)
- connections that don't depend on Plaid (14)
- fewer re-authentications (12)
- multi-currency support (9, 4 apps)
- Canadian bank connections (9)
- credit union connections (8)

- "The team unfortunately never advises customers that they are having issues" (PocketGuard, `pocketguard:a:14485863334`)
- "No notice in the app that it happened" (Copilot, `copilot:a:14709853188`)
- "very often you need to reconnect your accounts and then the double transactions appear" (Copilot, `copilot:a:13811964764`)
- "every 1-2 months, I get like 50-100 DUPLICATE TRANSACTIONS that I then have to manually delete, 1 by 1" (EveryDollar, `everydollar:a:14085323678`)
- "all my historical data was removed" (Simplifi, `simplifi:a:13663923632`)
- "oh this is a known issue from months ago with absolutely no update what so ever" (Simplifi, `simplifi:g:27234668-e3e1-40c9-8214-768870f1ab48`)
- "I hate that I now spend at least an hour every week to manually enter transactions" (YNAB, `ynab:g:fc0b217d-83dc-429c-994a-6820249c7626`)
- "stop spending time on that AI nonsense nobody asked for. Fix your core issues first - missing transactions, breaking connections" (Monarch, `monarch:g:1e3fe6af-6b47-4095-b649-f0d9a1f138b7`)

**Why it matters:** "its value depends entirely on being able to sync with your financial institution" (PocketGuard, `pocketguard:a:14553856626`). When sync breaks, every budget, report and alert built on it is wrong.

### 2. Updates that break what worked

- "More scrolling and more taps for what used to take one tap" (YNAB, `ynab:a:14158438732`)
- "locked out their customers from their OWN budgets with their latest update" (EveryDollar, `everydollar:g:762973c6-7716-44ad-9f0b-f0239202fa9b`)
- "But since it's last upgrade nothing works" (Goodbudget, `goodbudget:g:27a0cf11-aa5d-4792-b32c-9764d74a8c51`)
- "Why release an update when 2/3 of the tools aren’t even completed?" (PocketGuard, `pocketguard:a:14453021311`)

Long-time users (384 reviews) are among the unhappiest: 60% of their reviews are complaints.

**The unmet need:** stability for loyal users. That means testing before release, a way to keep the old layout, and no locking of data the user still wants to edit.

### 3. Support that can't escalate

- "a Chatbot is not enough to help me" (Simplifi, `simplifi:a:14667818169`)

When a bank link or the budget's numbers break, users want a ticket that a person actually picks up. A smaller but growing thread asks for a way to turn off AI features (12 reviews, 5 apps).

### 4. App-specific gaps

- **Rocket Money:** subscription detection and cancellation miss many subscriptions.
- **Goodbudget and EveryDollar:** envelope totals and budget math break after updates, and EveryDollar's locked past months draw repeated complaints.
- **YNAB:** churn in the interface (30.5% ease-of-use complaints). Users ask for the progress bars back and fewer taps.
- **Copilot and Simplifi:** auto-categorization complaints (12.7% and 14.1%). Copilot is iOS only.

### Who's happiest

- **Former Mint users** (165 reviews) average 4.1 stars. More than half of them are on Monarch.
- **Couples and families** (257 reviews) are the most satisfied segment, with only 26% complaints. Their asks are joint and individual views and per-person roles.
- **Copilot** has the highest average rating (3.52) and **Rocket Money** has the lowest share of complaints (46%), helped by many short positive Google Play reviews.

## Method

1. **Collection.** A GitHub Actions workflow (`.github/workflows/scrape.yml`) runs `pipeline.find_ids` and `pipeline.scrape` on a GitHub runner. That's needed because this cloud session can't reach the app stores. It pulled the Apple customer-reviews feed from 7 English-language storefronts and Google Play (en, US) for the last 12 months. Store IDs were checked by hand (`config/apps.json`). Cleaning removed duplicates and reviews under 20 characters, leaving 7,396 reviews.
2. **Tagging.** Every review is tagged against the frozen 15-theme codebook (`config/themes.json`). 2,550 were tagged by `pipeline.tag` with `claude-opus-5-5` in the `analyze.yml` workflow, at a cost of $6.09, before the API account's credit ran out. The other 4,846 were tagged by Claude reading each review in the working session, using the same schema. Where a review had both, the API tag is used.
3. **Reliability.** 448 reviews were tagged both ways, independently. The two agree on primary theme 80% of the time (Cohen's kappa 0.78), on sentiment 94% (kappa 0.89) and on review type 90% (kappa 0.87). Kappa is agreement after removing what chance alone would give; above 0.6 counts as substantial and above 0.8 as almost perfect.
4. **Analysis.** `python -m pipeline.analyze`. Pricing and "other" are excluded from the rankings. Every quote was checked word for word against its source review.

## Limits

- **Two taggers.** The two methods agree closely (see Reliability above), but they aren't identical.
- **Uneven volume.** Rocket Money is 41% of all reviews, and Goodbudget (86) and PocketGuard (204) are small. Rates are calculated per app, so this doesn't skew comparisons between apps, but small gaps for the small apps don't mean much.
- **Free sources cap volume.** Apple's feed returns at most about 500 reviews per storefront, and Google Play reviews are en-US only.
- **No synthesis briefs.** The per-theme briefs from `pipeline.synthesize` didn't run because the credit ran out. The briefs above were written by hand from the tagged data.
- **Review bias.** App-store reviewers lean toward the very unhappy and the very happy. Treat rates as the strength of a signal, not as rates across the whole user base.
