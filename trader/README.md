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

## Risk manager

`trader/risk_manager.py` has a veto over every entry; the trader cannot buy
anything it rejects. Exits are never blocked. Every signal must pass all of:

- kill switch off (`trader/journal/KILL` absent and `TRADER_KILL` unset)
- daily and weekly circuit breakers above
- symbol on the approved list, long only, stop < entry < target
- inside the 9:40-3:30 ET entry window
- at most 3 open positions (`TRADER_MAX_POSITIONS`), one per symbol
- dollar risk at or under 0.5% of capital, total exposure at or under capital,
  one position at or under `TRADER_MAX_POSITION_FRAC` of capital (default 100%)
- bars no older than 3 minutes, last trade within 0.25% of the signal price and above the stop
- no "skip" verdict for the symbol in today's research brief (`trader/journal/research/DATE.json`)
- account ACTIVE and not blocked; under $25k equity, no 4th day trade in 5 days (PDT)

Each pass it also checks that every open position still has a live stop
order, re-places a missing one, and closes the position if that fails.
Vetoes and guard actions are journaled as `risk_block` and `risk_guard`.

```
python -m trader.risk_manager kill "reason"   # stop trading and flatten now
python -m trader.risk_manager resume          # clear the kill switch
python -m trader.risk_manager status          # limits used, account flags
python -m trader.risk_manager review [date]   # daily review -> trader/journal/notes/
```

The daily review shows limits used, each trade's dollar risk and R, every
veto, running stats (win rate, profit factor, average R, max drawdown), any
rule breaches, and the live-money gate: 30+ paper trades, profit factor
1.2+, positive average R, max drawdown under 6%, and no breaches. Passing
the gate only means Luke is asked; it never turns on live trading.

Strategy changes (new symbols, parameters, or rules) go through the risk
manager before they trade: backtest on two separate periods, both with a
profit factor above 1, and no loosening of the limits above without Luke's
say-so.

## Strategy

Opening-range breakout: the first 15 minutes set a range. The first 1-minute
close above the range high, while above VWAP, buys at market and places a
resting stop order; the bot sells at the target itself, since Alpaca does not
allow bracket orders on fractional shares. The
stop is the range midpoint and the target is 2x the risk. One trade per symbol
per day. This is a starting point to measure, not a proven edge.

## Research brief

`python -m trader.research` writes `journal/research/<date>.md` and `.json`
before the open: each symbol's premarket gap, trend, ATR and overnight
headlines with a **skip / caution / ok** verdict, sector and macro ETFs, a
regime read, and scheduled events from `journal/research/events.csv` (earnings
days are marked skip). It runs at 9:10 ET on weekdays and is copied to the
vault's Research-Briefs note. It informs the trader and the risk manager; it
does not place or block orders.

## Use

Needs `APCA_API_KEY_ID` and `APCA_API_SECRET_KEY` (paper keys) and `requests`.

```
python -m trader.run check        # account, clock, latest prices
python -m trader.run loop         # trade today's session, flat by 3:45
python -m trader.backtest 2026-07-01 2026-10-20
python -m trader.notes 2026-10-22  # the day's journal note in Markdown
python -m trader.research          # today's premarket research brief
python -m unittest discover -s trader/tests -t .
```

State (`state.json`) and the trade journal (`trades.csv`) live in `trader/journal/` and are committed after each session, so they survive between cloud sessions. Daily notes also go to Luke's Obsidian vault.

## Pattern lab, screener, options study

Research and backtests behind the trading playbook
(`trader/journal/notes/trading-playbook.md`):

```
python -m trader.patterns          # 26 daily candlestick / chart / indicator rules, 2016-now
python -m trader.intraday_lab      # 8 day-trading rules on 5-minute bars, 2024-now
python -m trader.options_lab       # the swing setups replayed as modelled calls
python -m trader.screener [--plan] # best swing candidates, today's firing setups
```

All read-only; none of them places orders. `--plan` appends firing setups to
the paper swing tracker's plan (`trader/journal/swing/plan.csv`).
