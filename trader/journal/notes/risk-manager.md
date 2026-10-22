# Risk Manager

Set up 2026-10-22 (thread "Risk manager agent", PR Studioluke/ponytail#3, stacked on #2).
Role (vault Descriptions.md): weigh every trade; if the risk manager and Luke don't agree, the trader cannot trade.

## What it enforces on every entry (code: trader/risk_manager.py)
- Kill switch: `trader/journal/KILL` file or `TRADER_KILL=1` blocks entries and flattens everything.
- Circuit breakers: -2% day ($6), 3 losing trades, -5% week ($15) on $300.
- Approved symbols only (SPY, QQQ, AAPL, MSFT, GOOGL), long only, stop < entry < target.
- Entry window 9:40-3:30 ET; flat by 3:45.
- Max 3 open positions, one per symbol.
- Dollar risk <= 0.5% of capital ($1.50); exposure <= $300.
- Stale data (bars > 3 min old) or price > 0.25% away from the signal, or already below the stop: no trade.
- Market research brief (trader/journal/research/DATE.json, PR #4) verdict "skip" vetoes that symbol for the day; "caution" is allowed and noted.
- Account must be ACTIVE and unblocked; PDT guard under $25k equity (matters for a real $300 account).
- Every pass: each open position must have a live stop order; re-placed if missing, position closed if that fails.
- Exits are never blocked.

## Commands
- `python -m trader.risk_manager kill "reason"` / `resume` / `status` / `review [date]`
- Review writes `trader/journal/notes/risk-review-DATE.md`.

## Live-money gate (for the 2026-10-28 review and after)
30+ closed paper trades, profit factor >= 1.2, positive average R, max drawdown < 6% of capital, zero rule breaches.
Passing only means Luke is asked. A 5-day sample will not pass the 30-trade bar; expect "stay on paper" on 10-28.

## Risk notes for the 10-28 decision
- At $300 one breakout uses almost all capital (sizing is cash-capped, not risk-capped). Real risk per trade is usually well under $1.50, so the daily stops rarely bind; concentration is the main exposure.
- Real money at $300 means the PDT rule: max 3 day trades per 5 days in a margin account, or settled-cash limits in a cash account. The paper account ($100k) hides this.
- Backtest edge is thin (PF ~1.0-1.2); treat any 1-week paper result as noise.

## Strategy-change policy
New symbols, parameters or rules must backtest on two separate periods with PF > 1 each before they trade. Limits are never loosened without Luke.
