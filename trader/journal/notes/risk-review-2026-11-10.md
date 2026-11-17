## Risk review Tuesday 2026-11-10

**Kill switch:** off
**Account:** ACTIVE, equity $99,998.74, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $-1.40 | -$6.00 |
| Losing trades today | 5 | 3 |
| Weekly loss | $1.52 | -$15.00 |
| Risk per trade | max $0.60 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.87 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| SPY | 0.079 | 749.72 | 746.87 | 0.23 | -0.23 | -1.02 | stop |
| CAT | 0.103 | 577.74 | 573.89 | 0.40 | -0.43 | -1.08 | stop |
| KLAC | 0.395 | 151.09 | 149.58 | 0.60 | -0.61 | -1.02 | stop |
| SH | 0.901 | 33.19 | 32.88 | 0.28 | -0.03 | -0.11 | trail |
| SH | 1.807 | 33.13 | 32.94 | 0.34 | -0.11 | -0.32 | eod |

### Since paper trading began
62 trades, P&L $-0.97, win rate 31%, profit factor 0.95, average -0.07R, max drawdown $10.43 (3.48%), longest losing streak 14.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| control | 2 | $-0.44 | 0% | -0.97R |
| core | 15 | $-1.75 | 40% | +0.00R |
| explore | 28 | $-4.80 | 32% | +0.00R |
| in_play | 4 | $4.79 | 50% | +0.46R |
| lasthalf | 2 | $-0.32 | 0% | -0.51R |
| noise | 2 | $0.56 | 50% | +0.42R |
| sip_orb | 9 | $0.99 | 11% | -0.45R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 29 trades, P&L $-3.66, win rate 28%, average -0.20R. Other trades average +0.04R.

### Strategy experiment (since 2026-11-05)
| Strategy | Live | Shadow | Win rate | Profit factor | Avg R | P&L (live) | Verdict |
|---|---|---|---|---|---|---|---|
| sip_orb | 9 | 6 | 20% | 1.62 | -0.03R | $0.99 | testing (15/40) |
| noise | 2 | 1 | 33% | 1.72 | +0.10R | $0.56 | testing (3/40) |
| lasthalf | 2 | 3 | 20% | 0.11 | -0.37R | $-0.32 | testing (5/40) |
| control | 2 | 1 | 0% | 0.00 | -0.98R | $-0.44 | testing (3/40) |

Shadow trades are signals that got no slot, replayed on the day's bars. Promote at 40+ trades with PF above 1.2; retire at 40 trades with average R below 0.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 62 |
| Profit factor at least 1.2 | no | 0.95 |
| Positive average R | no | -0.07R |
| Max drawdown under 6% of capital | yes | 3.48% |
| No risk rule breaches | no | 2 |

**Verdict:** stay on paper

