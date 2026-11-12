## Risk review Monday 2026-10-26

**Kill switch:** off
**Account:** ACTIVE, equity $100,000.82, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $1.15 | -$6.00 |
| Losing trades today | 2 | 3 |
| Weekly loss | $1.15 | -$15.00 |
| Risk per trade | max $1.36 today | $1.50 |
| Open positions | 0 now | 3 |
| Position size | max $99.99 today | $100.00 (33% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| COST | 0.099 | 1007.32 | 1004.11 | 0.32 | 0.66 | +2.08 | target |
| IWM | 0.36 | 277.01 | 276.38 | 0.23 | 0.50 | +2.20 | target |
| QQQ | 0.14 | 710.07 | 707.59 | 0.35 | 0.70 | +2.02 | target |
| AMZN | 0.399 | 250.61 | 248.85 | 0.70 | -0.71 | -1.01 | stop |
| TSLA | 0.253 | 394.17 | 388.78 | 1.36 | -0.01 | -0.01 | eod |

**Risk actions:**
- 09:52 TSLA risk_taken: learning mode, trading anyway: gap +3.15% vs prior close 372.15 exceeds the 0.75% gap rule; research says skip TSLA: premarket gap +2.45% is past the 0.75% gap rule, so the bot will skip it
- 10:19 AMZN risk_taken: learning mode, trading anyway: research says skip AMZN: premarket gap +0.91% is past the 0.75% gap rule, so the bot will skip it

### Since paper trading began
7 trades, P&L $0.83, win rate 57%, profit factor 1.57, average +0.72R, max drawdown $0.74 (0.25%), longest losing streak 2.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| core | 3 | $0.39 | 67% | +0.60R |
| explore | 4 | $0.44 | 50% | +0.82R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 3 trades, P&L $-1.46, win rate 0%, average -0.54R. Other trades average +1.67R.

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | no | 7 |
| Profit factor at least 1.2 | yes | 1.57 |
| Positive average R | yes | +0.72R |
| Max drawdown under 6% of capital | yes | 0.25% |
| No risk rule breaches | yes | 0 |

**Verdict:** stay on paper

