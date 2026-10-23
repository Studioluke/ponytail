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

## Learning mode (Luke, 2026-10-22)
Luke: mistakes are fine on paper; trade through risk, note it, and learn. With `learning_mode` on (default; `TRADER_LEARNING=0` turns it off), the gap rule and research "skip" verdicts become `risk_taken` warnings instead of vetoes. All other vetoes still hold: breakers, caps, stale data, slippage, kill switch, stop guard. The daily review reports risk-taken trades separately (P&L, win rate, average R vs the other trades), not as breaches, so we can see whether those warnings were worth heeding.

## Change log
- 2026-10-23, sizing fix (trader thread, 9f612d0): a 9:46 GOOGL entry used the whole $300, so ten later breakouts sized to 0 and were lost for the day. The default `max_position_frac` went from 100% to 1/3 of capital (about $100 a position), which matches the 3-position cap. This only tightens risk. The daily review now shows the position-size limit. Lesson: with $300, concentration rather than stop distance was the binding risk.
- 2026-10-23: a session committed `trader/journal/state.json` while the loop ran and wiped an open position from state. Rule: only the trader loop writes state.json. Other threads never commit it.
