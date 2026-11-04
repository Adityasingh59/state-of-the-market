# State of Budgeting Apps: what users still can't get, from 8 apps' reviews

*4 November 2026. 7,396 App Store and Google Play reviews scraped for 8 budgeting apps (5 Nov 2025 to 3 Nov 2026). 1,290 of them were tagged, sampled across all 8 apps.*

## Summary

1. **Broken bank sync is the problem no app has solved.** It's the only theme complained about in more than 5% of reviews for every one of the 8 apps. The median is 15.5% of an app's reviews, ranging from 8.1% for Goodbudget, which is mostly manual entry, to 32.5% for Simplifi. Reviews that mention sync average 2.5 stars, against 3.3 for the rest.
2. **Updates are breaking long-time users' routines.** 104 complaint reviews (8% of all tagged) blame a recent update or redesign. Examples are extra taps in YNAB, EveryDollar locking past months, and envelope totals breaking in Goodbudget. Long-time users are among the unhappiest: 64% of their reviews are complaints.
3. **Users can't reach a human for support.** Support and trust complaints exceed 5% in 7 of 8 apps. Users mostly ask for a real person, not a chatbot, when money or data is at stake.
4. **App-specific gaps sit on top of that.** Rocket Money's subscription cancelling underdelivers (29.5% of its reviews). EveryDollar and Goodbudget have budgeting-logic problems (21% and 26%). YNAB's changes to its interface draw complaints in 30% of its reviews.

**Product bet: sync you can trust.** Warn users the moment a connection fails. Refill missing history after a reconnect. Remove duplicates automatically. And be honest about which banks work before people pay. It's the one gap every app shares, and much of the duplicate, missing-data and wrong-balance trouble traces back to it.

*Pricing is left out on purpose. Price complaints appear for every paid app and don't point to a product gap. They are kept in the tags but excluded from the rankings and charts.*

## The data

| App | Reviews scraped | Tagged | Avg rating (tagged) | Share of tagged that are pain |
|---|---|---|---|---|
| Monarch Money | 1,402 | 306 | 3.61 | 48% |
| Rocket Money | 3,000 | 298 | 2.60 | 71% |
| Copilot Money (iOS only) | 495 | 120 | 3.73 | 53% |
| YNAB | 1,003 | 120 | 3.29 | 59% |
| EveryDollar | 796 | 120 | 3.14 | 62% |
| Simplifi by Quicken | 410 | 120 | 2.47 | 76% |
| PocketGuard | 204 | 120 | 2.98 | 63% |
| Goodbudget | 86 | 86 | 2.78 | 76% |
| **Total** | **7,396** | **1,290** | | **62%** |

**Pain rate by theme:** the share of an app's tagged reviews that are negative or mixed about a theme, or report a bug, a missing feature or a complaint there.

| Theme | Copilot | EveryDollar | Goodbudget | Monarch | PocketGuard | Rocket | Simplifi | YNAB | Median |
|---|---|---|---|---|---|---|---|---|---|
| **Bank connection and sync** | 19.2% | 12.5% | 8.1% | 17.6% | 26.7% | 9.4% | **32.5%** | 13.3% | **15.5%** |
| Customer support and trust | 12.5% | 5.8% | 3.5% | 8.8% | **18.3%** | 15.1% | 15.8% | 6.7% | 10.7% |
| Ease of use and design | 9.2% | 9.2% | 10.5% | 4.9% | 6.7% | 9.7% | 8.3% | **30.0%** | 9.2% |
| Performance and stability | 11.7% | 7.5% | **34.9%** | 6.5% | 6.7% | 2.3% | 8.3% | 7.5% | 7.5% |
| Budgeting method | 5.0% | 20.8% | **25.6%** | 5.2% | 5.8% | 1.3% | 7.5% | 12.5% | 6.7% |
| Platform and devices | 5.0% | 10.8% | 14.0% | 4.6% | 1.7% | 3.0% | 9.2% | 5.0% | 5.0% |
| Bills and subscriptions | 1.7% | 3.3% | 1.2% | 1.6% | 1.7% | **29.5%** | 10.8% | 0.0% | 1.7% |

Charts: `figures/pain_gap.png`, `figures/heatmap.png`. Tables: `pain_gap.csv`, `theme_by_app.csv`.

## Theme briefs

### 1. Bank sync, the floor no one has fixed

250 of the 1,290 tagged reviews (19%) are about bank connections. The complaints repeat across apps: accounts silently disconnect, transactions arrive days late or not at all, reconnecting creates duplicates or wipes history, and some banks just aren't supported. 19 of the sync complaints say the app blamed Plaid, a third party or a "known issue".

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
- support non-US banks and multiple currencies, which international users ask for in 18 reviews

### 2. Updates that break what worked

Every app has some reviews like this, but they cluster in YNAB (25 of 120 tagged), EveryDollar (17) and Goodbudget (15 of 86).

- "More scrolling and more taps for what used to take one tap" (YNAB, `ynab:a:14158438732`)
- "locked out their customers from their OWN budgets with their latest update" (EveryDollar, `everydollar:g:762973c6-7716-44ad-9f0b-f0239202fa9b`)
- "But since it's last upgrade nothing works" (Goodbudget, `goodbudget:g:27a0cf11-aa5d-4792-b32c-9764d74a8c51`)
- "Why release an update when 2/3 of the tools aren’t even completed?" (PocketGuard, `pocketguard:a:14453021311`)

**The unmet need:** stability for loyal users. That means testing before release, a way to keep the old layout, and no locking of data the user still wants to edit. EveryDollar's past-month lock alone produced 8 requests to "edit past months".

### 3. Support that can't escalate

- "a Chatbot is not enough to help me" (Simplifi, `simplifi:a:14667818169`)

When a bank link or the budget's numbers break, users want a ticket that a person actually picks up. Requests for "human support" come from 6 of the 8 apps.

### 4. App-specific gaps

- **Rocket Money:** subscription detection and cancellation miss many subscriptions (29.5%). The top requests are "working subscription cancellation" (19) and "detect all subscriptions" (12).
- **EveryDollar and Goodbudget:** problems with budget logic and envelope math. Examples: savings that don't reduce what's left to spend, totals that don't add up, recurring items that can't be scheduled.
- **YNAB:** churn in the interface (30% ease-of-use complaints). Users ask for the progress bars back and fewer taps.
- **Copilot:** iOS only, and users ask for Android. It also has gaps tracking income categories and investment contributions.

### Who's happiest

- **Copilot** has the highest average rating (3.73) and **Monarch** has the lowest share of complaints (48%).
- **Former Mint users** (42 tagged reviews) still choose an app by comparing it with Mint. **Couples** (56) value shared budgets but ask for joint and individual views and per-person roles.

## Method

1. **Collection.** A GitHub Actions workflow (`.github/workflows/scrape.yml`) runs `pipeline.find_ids` and `pipeline.scrape` on a GitHub runner. That's needed because this cloud session can't reach the app stores. It pulled the Apple customer-reviews feed from 7 English-language storefronts and Google Play (en, US) for the last 12 months. Store IDs were checked by hand (`config/apps.json`) after the first run picked wrong Google Play packages. Cleaning removed duplicates and reviews under 20 characters, leaving 7,396 reviews.
2. **Sample.** No Anthropic API key was available, so the full tagging run (`pipeline.tag`) couldn't run. Claude tagged a seeded random sample by reading each review in the working session: up to 120 reviews for each of six apps, all 86 for Goodbudget, and 60 Google Play reviews each for Monarch and Rocket Money. These were added to 484 App Store reviews tagged earlier for those two apps. Tags follow the frozen 15-theme codebook (`config/themes.json`) and the `pipeline.tag` schema.
3. **Analysis.** `python -m pipeline.analyze`. Pricing and "other" are excluded from the rankings. Every quote was checked word for word against its source review.

## Limits

- **This is a sample.** Most apps have about 120 tagged reviews, so a rate like 15% carries a margin of roughly ±6 points. The pattern holds, since sync shows up in all 8 apps, but small gaps between apps don't mean much.
- **Unequal samples.** Monarch and Rocket Money have more tagged reviews (306 and 298), mostly from the App Store. The other apps mix both stores.
- **One tagger, no reliability check.** The second-model check (`pipeline.reliability`) needs an API key.
- **Free sources cap volume.** Apple's feed returns at most about 500 reviews per storefront, and PocketGuard and Goodbudget had few reviews in the 12-month window.
- **Review bias.** App-store reviewers lean toward the very unhappy and the very happy.

## Full-scale run

Add `ANTHROPIC_API_KEY` as a secret in the GitHub repo, then run tagging, reliability and synthesis on all 7,396 reviews. That replaces the sample with full counts and adds an agreement rate you can quote.
