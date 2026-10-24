# Smart money: insider and congressional buys

Code: `trader/smartmoney.py`. Data and results live here.

| File | What |
|---|---|
| `insider.csv` | SEC Form 4 open-market purchases of $1M+ (from openinsider.com), Jan 2024 on |
| `congress.csv` | Congressional stock buys, STOCK Act reports (from capitoltrades.com), Dec 2025 on |
| `report.md`, `backtest.json` | Backtest of every filter, plus the filer leaderboards |
| `<date>.json` | Fresh disclosures that pass a backtested filter (read by the research brief) |
| `paper.csv`, `paper.md` | Forward paper test of those signals: next open in, 20 sessions out, vs SPY. No orders |

## Refreshing the data

sec.gov, the House clerk and the Senate eFD site are blocked from the cloud
sandbox, so an agent fetches the pages with Firecrawl (`formats: ["markdown",
"rawHtml"]`, which saves the result to a file) and imports them:

- Insider, last 3 days, $1M+ purchases:
  `http://openinsider.com/screener?fd=3&xp=1&vl=1000&sortcol=0&cnt=500&page=1`
- Congress, newest stock buys (96 per page; page 1-2 covers a few days):
  `https://www.capitoltrades.com/trades?pageSize=96&txType=buy&assetType=stock&page=1`

```
python -m trader.smartmoney import insider  <saved firecrawl result>...
python -m trader.smartmoney import congress <saved firecrawl result>...
python -m trader.smartmoney signals          # writes <today>.json
python -m trader.smartmoney track            # updates paper.csv / paper.md
python -m trader.smartmoney backtest         # rerun after adding history (slow first time: fetches bars)
```

## What a signal is

A disclosure from the last 3 days that matches a filter which passed the
backtest (`report.md`), in a stock at $5+ trading $5M+ a day, from a filer
whose own record is not mostly losing to SPY. Signals are information for the
research brief and the forward paper test. They never place orders and never
change the day trader's verdicts or limits.
