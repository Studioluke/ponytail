## Risk review Tuesday 2026-11-03

**Kill switch:** off
**Account:** ACTIVE, equity $99,998.43, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $-0.73 | -$6.00 |
| Losing trades today | 4 | 3 |
| Weekly loss | $-2.57 | -$15.00 |
| Risk per trade | max $1.31 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.75 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| IWM | 0.213 | 280.45 | 279.82 | 0.13 | -0.13 | -0.97 | stop |
| QQQ | 0.087 | 686.81 | 684.99 | 0.16 | -0.16 | -1.01 | stop |
| INTC | 0.956 | 62.45 | 61.70 | 0.72 | -0.71 | -0.99 | stop |
| META | 0.097 | 615.23 | 612.52 | 0.26 | 0.46 | +1.75 | target |
| MSFT | 0.116 | 512.79 | 510.24 | 0.30 | 0.59 | +1.99 | target |
| SPY | 0.079 | 754.54 | 753.41 | 0.09 | 0.17 | +1.90 | target |
| AMD | 0.111 | 496.82 | 485.05 | 1.31 | -0.94 | -0.72 | eod |

**Risk actions:**
- 09:46 AMD risk_taken: learning mode, trading anyway: gap +2.85% vs prior close 466.745 exceeds the 0.75% gap rule; research says skip AMD: Earnings (confirmed; call 5:00 ET) (2026-11-03, after the session): the opening range is unreliable
- 09:50 INTC risk_taken: learning mode, trading anyway: gap +2.30% vs prior close 59.955 exceeds the 0.75% gap rule; research says skip INTC: premarket gap +3.58% is past the 0.75% gap rule, so the bot will skip it
- 10:23  halted: 3 losing trades today

### Since paper trading began
41 trades, P&L $-1.39, win rate 34%, profit factor 0.90, average +0.01R, max drawdown $8.58 (2.86%), longest losing streak 14.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| core | 12 | $-1.23 | 42% | +0.15R |
| explore | 25 | $-4.95 | 28% | -0.12R |
| in_play | 4 | $4.79 | 50% | +0.46R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 24 trades, P&L $-3.78, win rate 21%, average -0.33R. Other trades average +0.50R.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 41 |
| Profit factor at least 1.2 | no | 0.90 |
| Positive average R | yes | +0.01R |
| Max drawdown under 6% of capital | yes | 2.86% |
| No risk rule breaches | no | 2 |

**Verdict:** stay on paper

