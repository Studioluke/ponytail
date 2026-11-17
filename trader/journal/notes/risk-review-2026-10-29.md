## Risk review Thursday 2026-10-29

**Kill switch:** off
**Account:** ACTIVE, equity $100,001.71, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $-3.25 | -$6.00 |
| Losing trades today | 7 | 3 |
| Weekly loss | $2.13 | -$15.00 |
| Risk per trade | max $0.89 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.72 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| DIA | 0.114 | 522.77 | 522.25 | 0.06 | -0.06 | -1.01 | stop |
| QQQ | 0.083 | 716.27 | 714.25 | 0.17 | -0.17 | -1.01 | stop |
| GOOGL | 0.207 | 288.11 | 284.24 | 0.80 | -0.80 | -1.00 | stop |
| AMD | 0.104 | 573.61 | 566.88 | 0.70 | -0.70 | -1.00 | stop |
| AMZN | 0.24 | 248.52 | 244.81 | 0.89 | -0.89 | -1.00 | stop |
| TSLA | 0.147 | 406.28 | 403.47 | 0.41 | -0.41 | -0.99 | stop |
| AVGO | 0.173 | 344.51 | 342.42 | 0.36 | -0.20 | -0.55 | eod |

**Risk actions:**
- 10:03 QQQ risk_taken: learning mode, trading anyway: gap -1.24% vs prior close 725.59 exceeds the 0.75% gap rule; research says skip QQQ: premarket gap -1.30% is past the 0.75% gap rule, so the bot will skip it
- 11:11 AMD risk_taken: learning mode, trading anyway: gap -2.77% vs prior close 578.435 exceeds the 0.75% gap rule
- 11:11 AVGO risk_taken: learning mode, trading anyway: gap -2.70% vs prior close 351.9 exceeds the 0.75% gap rule
- 11:31 AMZN risk_taken: learning mode, trading anyway: gap -3.15% vs prior close 254.69 exceeds the 0.75% gap rule; research says skip AMZN: Earnings (confirmed; call 5:00 ET) (2026-10-29, after the session): the opening range is unreliable; premarket gap -2.04% is past the 0.75% gap rule, so the bot will skip it
- 11:42 GOOGL risk_taken: learning mode, trading anyway: gap -11.83% vs prior close 325.37 exceeds the 0.75% gap rule; research says skip GOOGL: Earnings (2026-10-28, after the session): the opening range is unreliable
- 13:02  halted: 3 losing trades today

### Since paper trading began
23 trades, P&L $1.83, win rate 30%, profit factor 1.24, average -0.13R, max drawdown $5.08 (1.69%), longest losing streak 12.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| core | 5 | $-0.58 | 40% | -0.04R |
| explore | 15 | $-3.09 | 20% | -0.37R |
| in_play | 3 | $5.50 | 67% | +0.94R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 15 trades, P&L $0.34, win rate 20%, average -0.37R. Other trades average +0.33R.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | no | 23 |
| Profit factor at least 1.2 | yes | 1.24 |
| Positive average R | no | -0.13R |
| Max drawdown under 6% of capital | yes | 1.69% |
| No risk rule breaches | no | 2 |

**Verdict:** stay on paper

