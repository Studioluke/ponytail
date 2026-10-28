## Risk review Wednesday 2026-10-28

**Kill switch:** off
**Account:** ACTIVE, equity $100,005.00, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $-1.85 | -$6.00 |
| Losing trades today | 5 | 3 |
| Weekly loss | $5.38 | -$15.00 |
| Risk per trade | max $0.72 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $99.74 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| KLAC | 0.634 | 157.18 | 156.41 | 0.49 | -0.53 | -1.09 | stop |
| NFLX | 1.592 | 62.65 | 62.20 | 0.72 | -0.81 | -1.13 | stop |
| COST | 0.101 | 983.77 | 982.40 | 0.14 | -0.18 | -1.30 | stop |
| IWM | 0.355 | 280.89 | 280.41 | 0.17 | -0.17 | -1.00 | stop |
| DIA | 0.19 | 524.42 | 523.63 | 0.15 | -0.16 | -1.07 | stop |

**Risk actions:**
- 09:46 KLAC risk_taken: learning mode, trading anyway: gap +1.48% vs prior close 153.68 exceeds the 0.75% gap rule; research says skip KLAC: premarket gap +2.02% is past the 0.75% gap rule, so the bot will skip it
- 09:47 NFLX risk_taken: learning mode, trading anyway: gap -0.94% vs prior close 62.51 exceeds the 0.75% gap rule
- 10:08 COST risk_taken: learning mode, trading anyway: gap -0.91% vs prior close 992.08 exceeds the 0.75% gap rule
- 10:20  halted: 3 losing trades today

### Since paper trading began
16 trades, P&L $5.06, win rate 44%, profit factor 2.14, average +0.23R, max drawdown $1.85 (0.62%), longest losing streak 5.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| core | 3 | $0.39 | 67% | +0.60R |
| explore | 10 | $-0.83 | 30% | -0.10R |
| in_play | 3 | $5.50 | 67% | +0.94R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 10 trades, P&L $3.10, win rate 30%, average -0.10R. Other trades average +0.77R.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | no | 16 |
| Profit factor at least 1.2 | yes | 2.14 |
| Positive average R | yes | +0.23R |
| Max drawdown under 6% of capital | yes | 0.62% |
| No risk rule breaches | no | 2 |

**Verdict:** stay on paper

