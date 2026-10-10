# Polymarket vs Kalshi price gaps (daily open dataset)

What does the **same** prediction-market contract cost on Polymarket and on Kalshi once fees are included? This repository answers that once a day and keeps the history.

Every morning a GitHub Action calls the public [VoxOdds](https://voxodds.com) API. It records the all-in price of a $100 order on both venues for every contract pair whose resolution rules have been reviewed as equivalent. Nothing is estimated from headline odds. The prices come from walking each venue's live order book, with estimated taker fees included.

[![VoxOdds Gap Index, live](https://voxodds.com/og/polymarket-vs-kalshi.png)](https://voxodds.com/polymarket-vs-kalshi)

<!-- LATEST:START -->

Snapshot `2026-10-10T11:11:16.993659+00:00` · 14 day(s) of history in `data/summary.csv`.

| Matched contract sides | VoxOdds Gap Index (median saving on the cheaper venue, long shots excluded) | Polymarket cheaper | Kalshi cheaper |
|---:|---:|---:|---:|
| 38 | 5.71% (23 sides) | 23 | 15 |

Widest gaps in this snapshot, contracts priced at 2¢ or more ($100 all-in, fees included):

| Outcome | Polymarket | Kalshi | Cheaper | Saving |
|---|---:|---:|---|---:|
| Yes: Andy Beshear wins and accepts the 2028 Democratic presidential nomination | 2.85¢ | 5.79¢ | Polymarket | 50.8% |
| Yes: Mark Kelly wins and accepts the 2028 Democratic presidential nomination | 2.60¢ | 4.41¢ | Polymarket | 41.0% |
| Yes: Ron DeSantis wins and accepts the 2028 Republican presidential nomination | 2.79¢ | 4.39¢ | Polymarket | 36.4% |
| Yes: Kamala Harris wins and accepts the 2028 Democratic presidential nomination | 6.64¢ | 8.53¢ | Polymarket | 22.2% |
| Yes: Alexandria Ocasio-Cortez wins and accepts the 2028 Democratic presidential nomination | 18.49¢ | 14.84¢ | Kalshi | 19.7% |

Live version: https://voxodds.com/polymarket-vs-kalshi

<!-- LATEST:END -->

## Files

| File | What it contains |
|---|---|
| `data/daily/YYYY-MM-DD.csv` | One row per matched contract side (Yes and No are separate rows) for that day's snapshot |
| `data/latest.csv` | Copy of the most recent daily file |
| `data/summary.csv` | One row per day: matched sides, the VoxOdds Gap Index (`gap_index_pct`, long shots excluded, and `index_sides`), the median and mean saving over all sides, how often each venue was cheaper |

### Columns in the daily files

| Column | Meaning |
|---|---|
| `snapshot_utc` | When VoxOdds computed the quotes |
| `opportunity_id` | Stable VoxOdds id for the pair and side |
| `family` | Market family, for example `republican_nominee_2028` |
| `side`, `outcome` | The outcome being bought |
| `polymarket_id`, `kalshi_ticker` | Venue identifiers of the two paired markets |
| `budget_usd` | All-in budget used for the quote (100) |
| `polymarket_all_in_price`, `kalshi_all_in_price` | Effective average price per contract including estimated taker fees (0 to 1) |
| `polymarket_fee_usd`, `kalshi_fee_usd` | Estimated fees for the order |
| `polymarket_shares`, `kalshi_shares` | Contracts the budget buys on each venue |
| `cheaper_venue` | `polymarket`, `kalshi` or `tie` |
| `advantage_pct` | How much lower the cheaper venue's effective price is, in percent |
| `reviewed_at` | When the pair's equivalence was last reviewed |
| `voxodds_url` | Live quote page for the pair |

## The VoxOdds Gap Index

The VoxOdds Gap Index is the median fee-inclusive saving on the cheaper venue across contracts matched on Polymarket and Kalshi, for a $100 all-in order, **excluding long shots** (an all-in price below 2¢ or above 98¢ on either venue). It is the `gap_index_pct` column of `data/summary.csv`, one value per day; `index_sides` is how many contract sides it covers.

Why long shots are excluded (from 3 October 2026): on a contract priced at a fraction of a cent, a 0.1¢ difference reads as a 50%+ saving. With those sides included, the median sat between a cluster of near-zero gaps and a cluster of very large ones, so one or two rows entering or leaving the snapshot could move it from about 4% to about 11%. `gap_index_pct` is backfilled from the daily files for every day in the dataset. The previous definition, which included every side, remains available as `median_advantage_pct`.

## Method and caveats

- **Pairing is fail-closed.** Only pairs pinned to reviewed question and rule fingerprints are included. If a venue changes its rules, the pair drops out until it is reviewed again.
- **Fees are estimates.** Polymarket taker fees are modeled as shares × live fee rate × price × (1 - price). Kalshi fees are modeled as 0.07 × contracts × price × (1 - price), with zero-fee series handled explicitly. The venue's own order preview is authoritative.
- **Snapshots, not averages.** Each file is one moment in time. Order books move, and a quote can change before execution.
- **Long shots.** Contracts priced under 2 cents can show very large percentage gaps on small absolute amounts.
- Check venue eligibility and your jurisdiction before trading. Market-implied odds, not financial advice.

## Live sources

- Live comparison page: https://voxodds.com/polymarket-vs-kalshi
- JSON API: https://voxodds.com/api/v1/executable-opportunities?amount_usd=100
- MCP server for AI agents (no key needed): https://voxodds.com/mcp · registry name `com.voxodds/voxodds`

## License and citation

The data is published under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) and the code under the MIT license. Please cite as:

> VoxOdds, "Polymarket vs Kalshi price gaps (daily open dataset)", https://github.com/softdevfz/polymarket-kalshi-price-gaps

Questions or corrections: open an issue.
