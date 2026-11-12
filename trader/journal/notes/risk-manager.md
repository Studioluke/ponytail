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
- 2026-10-24: learning trade (trader thread, 76e8292): in learning mode, if nothing is entered by 11:00 ET, the bot takes one half-risk ($0.75) trade in the strongest trend, through check_entry. The daily review now breaks results out by group (core / explore / learning). Forced learning trades are kept out of the "risks taken knowingly" line.
- 2026-11-05, strategy experiment (trader thread with the strategy research thread; Luke 11-04: keep paper trading as long as it takes to find a winning strategy; paper changes are for the agents to decide). Four strategies now run side by side (trader/strategies.py): sip_orb (stocks-in-play 5-min ORB, 2 slots), noise (SPY noise-area momentum with an 11:30 half-size fallback, 1 slot), lasthalf (15:30 SPY/SH, 1 slot) and control (15-min ORB on the core five, 1 slot). Signals that get no slot become shadow trades (trader/journal/shadow.csv, replayed by `python -m trader.shadow DATE`), and the review shows a per-strategy scorecard. Promote at 40+ trades with PF > 1.2. Retire at 40 with avg R < 0.
  - Unchanged: the $1.50 per-trade cap, $300 exposure, $60 per position, 5 positions, the -2% day and -5% week breakers, the kill switch and the stop guard.
  - Tightened: learning mode's override path is gone. The gap rule and research "skip" are vetoes again for control, noise and lasthalf. The forced 11:00 learning trade is retired: its 24 trades went 21% win, -0.33R. Control risks $0.75 a trade, not $1.50.
  - Loosened, and noted here for Luke:
    - Flatten moved from 15:45 to 15:58.
    - The entry window is now 9:35-15:31, so sip_orb can enter from 9:35 and lasthalf at 15:30.
    - The 3-losing-trades halt now counts each strategy separately, so one strategy's losses don't stop the others. The dollar breakers still stop everything.
    - sip_orb may trade gap and earnings names. A research "skip" still vetoes it for halts, offerings, FDA, mergers and delistings.
    - SH (inverse SPY, a long position) and the 100-stock watchlist are on the approved list.
- 2026-11-11, Wednesday review (trader thread with the strategy research thread; live from 11-12):
  - Unchanged: every cap, breaker, kill switch and stop guard, sip_orb's live 0.1 x ATR stop, and slot counts.
  - Added (shadow only): sip_orb_wide. Every sip_orb signal also logs a shadow trade with the stop at the 5-min low, at most 0.25 x ATR below the high, at the same $ risk. Both are scored at 40 trades, and if wide leads on average R it takes the live slots. Reason: on 11-05/11-06, 7 of 7 stops hit within 1-2 minutes, and IEX's 5-min high is a median 9.4 bps off SIP.
  - Narrowed, and noted here for Luke: research "skip" verdicts tagged "gap" (the brief's new skip_tag field; an untagged skip without event words counts as a gap) no longer veto noise or lasthalf. The noise bands already include the overnight gap. Event skips (FOMC, CPI, NFP, earnings, halt) still veto them, and gap skips still veto control. On 11-09, gap skips vetoed both SPY strategies on a +2.4% day.
  - Separate SPY exposure: when another strategy already holds SPY or SH, noise and lasthalf use the S&P 500 twin VOO or SPDN, added to the approved list. Their stale-data check and trails still follow SPY. This adds no new caps; exposure, position and per-trade limits all still apply.
  - Reliability: network errors from 9:29 to 9:40 retry after 10 seconds, not at the next minute. The errors are listed in the day's flags as open_data_errors, so a sip_orb day built on gappy opening data can be flagged in the review.
