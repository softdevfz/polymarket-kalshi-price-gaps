# Polymarket vs Kalshi price gaps (daily open dataset)

What does the **same** prediction-market contract cost on Polymarket and on Kalshi once fees are included? This repository answers that once a day and keeps the history.

Every morning a GitHub Action calls the public [VoxOdds](https://voxodds.com) API. It records the all-in price of a $100 order on both venues for every contract pair whose resolution rules have been reviewed as equivalent. Nothing is estimated from headline odds. The prices come from walking each venue's live order book, with estimated taker fees included.

[![VoxOdds Gap Index, live](https://voxodds.com/og/polymarket-vs-kalshi.png)](https://voxodds.com/polymarket-vs-kalshi)

<!-- LATEST:START -->

Snapshot `2026-09-30T11:10:42.837261+00:00` · 4 day(s) of history in `data/summary.csv`.

| Matched contract sides | VoxOdds Gap Index (median saving on the cheaper venue) | Polymarket cheaper | Kalshi cheaper |
|---:|---:|---:|---:|
| 35 | 12.52% | 23 | 12 |

Widest gaps in this snapshot, contracts priced at 2¢ or more ($100 all-in, fees included):

| Outcome | Polymarket | Kalshi | Cheaper | Saving |
|---|---:|---:|---|---:|
| Yes: Andy Beshear wins and accepts the 2028 Democratic presidential nomination | 3.50¢ | 6.82¢ | Polymarket | 48.6% |
| Yes: Ron DeSantis wins and accepts the 2028 Republican presidential nomination | 2.91¢ | 4.69¢ | Polymarket | 38.0% |
| Yes: Mark Kelly wins and accepts the 2028 Democratic presidential nomination | 2.91¢ | 4.59¢ | Polymarket | 36.6% |
| Yes: Josh Shapiro wins and accepts the 2028 Democratic presidential nomination | 6.42¢ | 5.01¢ | Kalshi | 21.9% |
| Yes: Alexandria Ocasio-Cortez wins and accepts the 2028 Democratic presidential nomination | 19.21¢ | 15.89¢ | Kalshi | 17.2% |

Live version: https://voxodds.com/polymarket-vs-kalshi

<!-- LATEST:END -->

## Files

| File | What it contains |
|---|---|
| `data/daily/YYYY-MM-DD.csv` | One row per matched contract side (Yes and No are separate rows) for that day's snapshot |
| `data/latest.csv` | Copy of the most recent daily file |
| `data/summary.csv` | One row per day: matched sides, the VoxOdds Gap Index (`median_advantage_pct`), mean saving, how often each venue was cheaper |

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

The VoxOdds Gap Index is the median fee-inclusive saving on the cheaper venue across all contracts matched on Polymarket and Kalshi, for a $100 all-in order. It is the `median_advantage_pct` column of `data/summary.csv`, one value per day.

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
