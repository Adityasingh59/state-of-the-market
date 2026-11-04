# State of Budgeting Apps: what 587 App Store reviews say users still lack

*Pilot study, 4 November 2026. Data: 587 US App Store reviews of Monarch Money (246) and Rocket Money (341), posted 20 July to 3 November 2026.*

## Summary

- **The pain both apps share is broken bank sync.** Even the app that handles it better, Rocket Money, gets sync complaints in 9.7% of its reviews; Monarch gets them in 15.4%. Reviews that mention sync average 2.3 stars. This is the clearest unmet need in the data: neither app has solved it.
- **Rocket Money's headline feature is its biggest source of complaints.** 40% of its reviews (136 of 341) are about finding or cancelling subscriptions, and 34% are complaints about it. The two most common requests are for cancellation that actually works (25 reviews) and detection of every subscription (19).
- **Paying to save money feels wrong to users.** 30% of Rocket Money reviews (102) are about its own price or billing, and 85 of those are negative. About 1 in 10 Rocket Money reviews (34) describe a charge the user didn't expect, after a trial, a cancellation or a deletion.
- **Support has been automated, and users notice.** Support and trust complaints appear in 18.2% of Rocket Money reviews and 9.3% of Monarch reviews. The recurring ask in both apps is to reach a human.
- **Monarch wins former Mint users and couples.** 20 reviewers say they came from Mint: 17 of them are positive and they average 4.5 stars. 23 Monarch reviews are from couples or families, and 18 of those are positive.

**Product bet:** a "sync you can trust" layer. That means alerts when a connection silently fails, repair of the missing history after reconnecting, and automatic removal of duplicate transactions. It's the one gap both leading apps share, and it sits underneath the duplicate, missing-data and wrong-budget complaints.

## The numbers

| | Monarch Money | Rocket Money |
|---|---|---|
| Reviews | 246 | 341 |
| Average rating | 3.65 | 2.36 |
| Positive / negative | 56% / 31% | 23% / 62% |
| Praise / bug / complaint / pricing (review type) | 55% / 17% / 12% / 7% | 22% / 16% / 37% / 21% |

**Pain rate by theme:** the share of an app's reviews that are negative or mixed about a theme, or report a bug, request or complaint there.

| Theme | Monarch | Rocket Money | Better of the two |
|---|---|---|---|
| Bills and subscription tracking | 1.6% | **33.7%** | Monarch |
| Pricing and subscription | 12.2% | **28.4%** | Monarch |
| Customer support and trust | 9.3% | **18.2%** | Monarch |
| Bank connection and sync | **15.4%** | 9.7% | Rocket Money (still 9.7%) |
| Ease of use and design | 5.7% | 10.0% | Monarch |
| Performance and stability | **6.5%** | 1.5% | Rocket Money |
| Budgeting method and flexibility | **5.7%** | 1.5% | Rocket Money |

Charts: `figures/pain_gap.png`, `figures/heatmap.png`. Full table: `pain_gap.csv`.

## Theme briefs

### 1. Bank sync: the unsolved floor

**What users say.** Accounts disconnect, reconnecting creates duplicates or loses weeks of data, and the app often gives no sign that anything is wrong.

- "essentially no UI for telling you that your accounts haven't been synced due to a problem, leading me to miss all spending on a few accounts for nearly a year" (Monarch, `monarch:a:14704658469`)
- "relinking them causes massive issues. Every single purchase and deposit gets duplicated" (Rocket Money, `rocketmoney:a:14669858797`)
- "transactions from that “reconnection” point on never came through" (Rocket Money, `rocketmoney:a:14742321124`)
- "if you have shared credit cards or replace cards, expect duplicate transactions that support won't fix" (Monarch, `monarch:a:14363103705`)

**Root cause.** Both apps depend on third-party data aggregators, and several reviewers blame Plaid by name. What users judge them on is what happens when a connection breaks: whether they're told, whether history is repaired, whether duplicates are cleaned up.

**Unmet need.** Visible connection health, gap backfill after a reconnect, and automatic de-duplication (for example when a card is replaced or shared).

### 2. Subscription cancellation: Rocket Money's promise gap

**What users say.** People install Rocket Money because of ads promising one-tap cancellation. They then find it misses subscriptions or can only cancel the easy ones.

- "it only found 3 outta like 10" (`rocketmoney:a:14722443451`)
- "all it does is cancel the ones that are already easy to cancel" (`rocketmoney:a:14649051969`)

**Unmet need.** Detection that covers every subscription, including other email accounts and app-store billing, and honest messaging about what can't be cancelled. 44 Rocket Money reviews (13%) ask for exactly one of these two things.

### 3. Pricing and billing trust

**What users say.** Paying a subscription to cut subscriptions reads as ironic, and charges after a trial or cancellation read as deceptive.

- "Subscription to cancel subscriptions" (`rocketmoney:a:14690844208`)
- "They warn you about every subscription under the sun… except their own" (`rocketmoney:a:14585435352`)
- "Moving it behind an exclusive Premium+ paywall" (bill negotiation, `rocketmoney:a:14690686612`)

Monarch gets milder price complaints (12.2%), mostly that the free trial is short, the fee is high, and cancellation happens outside the app.

**Unmet need.** Users want three things: renewal reminders for the app's own fee, cancellation inside the app, and the price shown before account linking.

### 4. Support: AI first, human never

- "if the user persists long enough they can get to a Zendesk ticket" (Monarch, `monarch:a:14355273654`)
- "A phone line is need. Enough AI support and overworked chat representatives" (Rocket Money, `rocketmoney:a:14695106467`)

**Unmet need.** Users want a reachable human when money or data is at stake. In Rocket Money's reviews, trust is also hurt by aggressive advertising (47 reviews mention ads) and suspicion of data sharing (12 reviews).

### 5. Monarch-specific: update regressions and flexibility

Monarch's complaints lean toward product changes: the current month was removed from cash flow and reports, and later updates brought lag and crashes (6.5%). There are also requests for more budgeting flexibility.

- "The current month is not showing anymore and that’s the most helpful thing" (`monarch:a:14355848741`)
- "you can’t budget by paycheck and can only budget by month" (`monarch:a:14331154897`)

Other requests each come up once or twice: budgeting by paycheck, goal contributions that vary for variable income, percentage-based goals, an Apple Watch app, support for the iPhone Duo, and API/MCP access to the user's own data.

### Where Monarch is winning

- **Former Mint users:** "Ever since Mint was shutdown, I’ve been having the hardest time finding a budgeting app that fits my needs" (`monarch:a:14361874879`). They are Monarch's happiest segment, averaging 4.5 stars.
- **Couples and families:** shared household budgets are praised far more often than criticised. The one recurring gap is a partner invite or membership that doesn't work.

## Method

1. **Data.** Two Apify exports of the actor "The Better App Store Reviews Scraper", one for Monarch and one for Rocket Money (US storefront, sorted by most recent). Imported with `python -m pipeline.apify import`, which removed 13 duplicate or very short reviews (600 down to 587).
2. **Tagging.** Each review was tagged against the frozen 15-theme codebook in `config/themes.json` with a primary theme, all themes mentioned, sentiment, type, stated user segment and unmet need. The Claude API wasn't available in this environment, so Claude tagged every review by reading it directly in the working session. The tags use the same schema as `pipeline/tag.py`.
3. **Analysis.** `python -m pipeline.analyze` (pain rates, pain gap, heatmap). Every quote above was checked word for word against its source review.

## Limits

- **Two apps, not a category.** "Better of the two" is not "best in the category". Findings about Rocket Money's subscription feature are specific to Rocket Money.
- **US App Store only, about 3.5 months.** Monarch covers 20 Jul to 3 Nov and Rocket Money covers 16 Sep to 3 Nov, so the windows differ and trends over time aren't comparable. Google Play isn't included.
- **One tagger, no reliability check yet.** The planned second-model re-tag of a 20% sample (`python -m pipeline.reliability`) hasn't been run, so there is no agreement rate to quote yet.
- **Review bias.** App-store reviewers lean toward the very unhappy and the very happy. Treat percentages as the strength of a signal, not as rates across the whole user base.

## To reach the full study

Export the other six apps from Apify (YNAB, Copilot, EveryDollar, PocketGuard, Simplifi, Goodbudget), ideally across several countries, and get Google Play reviews with `pipeline.scrape`. Then run `pipeline.tag`, `pipeline.reliability`, `pipeline.synthesize` and `pipeline.analyze` with an API key. The same report then becomes a real category-wide "pain gap".
