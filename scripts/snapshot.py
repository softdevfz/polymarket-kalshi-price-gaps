#!/usr/bin/env python3
"""Daily snapshot of Polymarket vs Kalshi all-in price gaps from the public VoxOdds API.

Standard library only. Writes data/daily/YYYY-MM-DD.csv, data/latest.csv, upserts
data/summary.csv and refreshes the "Latest snapshot" block in README.md.
Exits 0 without writing anything when the API is unavailable or returns no rows,
so a bad day never commits an empty file.
"""
import csv, json, statistics, sys, time, urllib.request
from pathlib import Path

API = "https://voxodds.com/api/v1/executable-opportunities?amount_usd=100"
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ROW_FIELDS = [
    "snapshot_utc", "opportunity_id", "family", "side", "outcome", "polymarket_id", "kalshi_ticker",
    "budget_usd", "polymarket_all_in_price", "kalshi_all_in_price", "polymarket_fee_usd", "kalshi_fee_usd",
    "polymarket_shares", "kalshi_shares", "cheaper_venue", "advantage_pct", "reviewed_at", "voxodds_url",
]
SUMMARY_FIELDS = [
    "date", "snapshot_utc", "pairs_scanned", "matched_sides", "median_advantage_pct",
    "mean_advantage_pct", "polymarket_cheaper", "kalshi_cheaper", "ties",
    "gap_index_pct", "index_sides",
]


def is_long_shot(row):
    """All-in price below 2 cents or above 98 cents on either venue (excluded from the index)."""
    prices = (float(row["polymarket_all_in_price"]), float(row["kalshi_all_in_price"]))
    return any(p < 0.02 or p > 0.98 for p in prices)


def gap_index(rows):
    """VoxOdds Gap Index: median advantage over contract sides that are not long shots."""
    adv = [float(r["advantage_pct"]) for r in rows
           if r["advantage_pct"] not in ("", None) and not is_long_shot(r)]
    return (round(statistics.median(adv), 2) if adv else ""), len(adv)


def fetch():
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(API, headers={
                "User-Agent": "polymarket-kalshi-price-gaps/1.0 (+https://github.com/softdevfz/polymarket-kalshi-price-gaps)",
                "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=240) as resp:
                return json.load(resp)
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(20 * (attempt + 1))
    print(f"API unavailable: {last}", file=sys.stderr)
    return None


def rows_from(payload):
    stamp = payload.get("generated_at", "")
    rows = []
    for o in payload.get("opportunities") or []:
        v = o.get("venues") or {}
        poly, kal = v.get("polymarket") or {}, v.get("kalshi") or {}
        if poly.get("effective_average_price") is None or kal.get("effective_average_price") is None:
            continue
        best = o.get("best_venue") or {}
        tie = poly["effective_average_price"] == kal["effective_average_price"]
        rows.append({
            "snapshot_utc": stamp, "opportunity_id": o.get("opportunity_id", ""), "family": o.get("family", ""),
            "side": o.get("side", ""), "outcome": o.get("normalized_outcome", ""),
            "polymarket_id": o.get("polymarket_id", ""), "kalshi_ticker": o.get("kalshi_ticker", ""),
            "budget_usd": o.get("all_in_budget_usd", ""),
            "polymarket_all_in_price": poly.get("effective_average_price"),
            "kalshi_all_in_price": kal.get("effective_average_price"),
            "polymarket_fee_usd": poly.get("estimated_fee_usd", ""), "kalshi_fee_usd": kal.get("estimated_fee_usd", ""),
            "polymarket_shares": poly.get("shares", ""), "kalshi_shares": kal.get("shares", ""),
            "cheaper_venue": "tie" if tie else best.get("platform", ""),
            "advantage_pct": best.get("effective_price_advantage_pct", ""),
            "reviewed_at": o.get("reviewed_at", ""), "voxodds_url": o.get("share_url", ""),
        })
    return rows


def summarize(payload, rows):
    adv = [float(r["advantage_pct"]) for r in rows if r["advantage_pct"] not in ("", None)]
    venues = [r["cheaper_venue"] for r in rows]
    return {
        "date": payload["generated_at"][:10], "snapshot_utc": payload["generated_at"],
        "pairs_scanned": payload.get("verified_pairs_scanned", ""), "matched_sides": len(rows),
        "median_advantage_pct": round(statistics.median(adv), 2) if adv else "",
        "mean_advantage_pct": round(statistics.fmean(adv), 2) if adv else "",
        "polymarket_cheaper": venues.count("polymarket"), "kalshi_cheaper": venues.count("kalshi"),
        "ties": venues.count("tie"),
        **dict(zip(("gap_index_pct", "index_sides"), gap_index(rows))),
    }


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def backfill(row):
    """Fill gap_index_pct for days recorded before the column existed, from that day's file."""
    daily = DATA / "daily" / f"{row['date']}.csv"
    if row.get("gap_index_pct") in (None, "") and daily.exists():
        with daily.open(newline="", encoding="utf-8") as fh:
            row["gap_index_pct"], row["index_sides"] = gap_index(list(csv.DictReader(fh)))
    return row


def upsert_summary(summary):
    path = DATA / "summary.csv"
    existing = []
    if path.exists():
        with path.open(newline="", encoding="utf-8") as fh:
            existing = [backfill(r) for r in csv.DictReader(fh) if r["date"] != summary["date"]]
    write_csv(path, SUMMARY_FIELDS, sorted(existing + [summary], key=lambda r: r["date"]))
    return len(existing) + 1


def refresh_readme(summary, rows, days):
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    start, end = "<!-- LATEST:START -->", "<!-- LATEST:END -->"
    if start not in text or end not in text:
        return
    liquid = [r for r in rows if min(float(r["polymarket_all_in_price"]), float(r["kalshi_all_in_price"])) >= 0.02]
    top = sorted(liquid, key=lambda r: float(r["advantage_pct"] or 0), reverse=True)[:5]
    lines = [
        start, "",
        f"Snapshot `{summary['snapshot_utc']}` · {days} day(s) of history in `data/summary.csv`.", "",
        "| Matched contract sides | VoxOdds Gap Index (median saving on the cheaper venue, long shots excluded) | Polymarket cheaper | Kalshi cheaper |",
        "|---:|---:|---:|---:|",
        f"| {summary['matched_sides']} | {summary['gap_index_pct']}% ({summary['index_sides']} sides) | {summary['polymarket_cheaper']} | {summary['kalshi_cheaper']} |",
        "", "Widest gaps in this snapshot, contracts priced at 2¢ or more ($100 all-in, fees included):", "",
        "| Outcome | Polymarket | Kalshi | Cheaper | Saving |", "|---|---:|---:|---|---:|",
    ]
    for r in top:
        lines.append(f"| {r['side']}: {r['outcome']} | {float(r['polymarket_all_in_price'])*100:.2f}¢ | "
                     f"{float(r['kalshi_all_in_price'])*100:.2f}¢ | {str(r['cheaper_venue']).title()} | "
                     f"{float(r['advantage_pct']):.1f}% |")
    lines += ["", "Live version: https://voxodds.com/polymarket-vs-kalshi", "", end]
    before, rest = text.split(start, 1)
    after = rest.split(end, 1)[1]
    readme.write_text(before + "\n".join(lines) + after, encoding="utf-8")


def main():
    payload = fetch()
    if not payload or not payload.get("ok") or not payload.get("generated_at"):
        print("No usable payload; nothing written.")
        return 0
    rows = rows_from(payload)
    if not rows:
        print("No matched rows; nothing written.")
        return 0
    summary = summarize(payload, rows)
    write_csv(DATA / "daily" / f"{summary['date']}.csv", ROW_FIELDS, rows)
    write_csv(DATA / "latest.csv", ROW_FIELDS, rows)
    days = upsert_summary(summary)
    refresh_readme(summary, rows, days)
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
