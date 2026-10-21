# Day trader (Alpaca paper)

A small, rule-based day trader for Luke's **Alpaca paper account**. It is
hard-wired to `https://paper-api.alpaca.markets` and refuses to start against
any other trading endpoint. It is unrelated to the rest of this repo.

## Rules (from the vault, adjustable by env var)

| Rule | Default | Env var |
|---|---|---|
| Symbols | SPY, QQQ, AAPL, MSFT, GOOGL (long only, cash) | `TRADER_SYMBOLS` |
| Capital it sizes against | $300 (fractional shares) | `TRADER_CAPITAL` |
| Risk per trade | 0.5% | `TRADER_RISK_PER_TRADE` |
| Daily stop | -2% or 3 losing trades | `TRADER_MAX_DAILY_LOSS`, `TRADER_MAX_DAILY_LOSSES` |
| Weekly stop | -5% | `TRADER_MAX_WEEKLY_LOSS` |
| Entries | 9:40 to 3:30 ET | |
| Flat by | 3:45 ET | |
| Skip a symbol that gaps more than | 0.75% from prior close | |

## Strategy

Opening-range breakout: the first 15 minutes set a range. The first 1-minute
close above the range high, while above VWAP, buys at market and places a
resting stop order; the bot sells at the target itself, since Alpaca does not
allow bracket orders on fractional shares. The
stop is the range midpoint and the target is 2x the risk. One trade per symbol
per day. This is a starting point to measure, not a proven edge.

## Use

Needs `APCA_API_KEY_ID` and `APCA_API_SECRET_KEY` (paper keys) and `requests`.

```
python -m trader.run check        # account, clock, latest prices
python -m trader.run loop         # trade today's session, flat by 3:45
python -m trader.backtest 2026-07-01 2026-10-20
python -m trader.notes 2026-10-22  # the day's journal note in Markdown
python -m unittest discover -s trader/tests -t .
```

State (`state.json`) and the trade journal (`trades.csv`) live in `trader/journal/` and are committed after each session, so they survive between cloud sessions. Daily notes also go to Luke's Obsidian vault.
