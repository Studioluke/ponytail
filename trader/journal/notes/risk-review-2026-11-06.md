## Risk review Friday 2026-11-06

**Kill switch:** off
**Account:** ACTIVE, equity $99,997.26, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $-0.94 | -$6.00 |
| Losing trades today | 5 | 3 |
| Weekly loss | $-3.67 | -$15.00 |
| Risk per trade | max $0.30 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.88 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| COP | 0.442 | 135.47 | 134.88 | 0.26 | -0.29 | -1.11 | stop |
| WMT | 0.479 | 124.75 | 124.41 | 0.16 | -0.17 | -1.04 | stop |
| MCD | 0.22 | 271.44 | 271.08 | 0.08 | -0.06 | -0.76 | stop |
| SPY | 0.08 | 739.63 | 736.79 | 0.23 | -0.21 | -0.92 | stop |
| SPY | 0.081 | 737.94 | 734.19 | 0.30 | -0.21 | -0.69 | eod |

### Since paper trading began
54 trades, P&L $-2.48, win rate 33%, profit factor 0.85, average -0.05R, max drawdown $10.43 (3.48%), longest losing streak 14.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| control | 1 | $-0.21 | 0% | -0.92R |
| core | 15 | $-1.75 | 40% | +0.00R |
| explore | 28 | $-4.80 | 32% | +0.00R |
| in_play | 4 | $4.79 | 50% | +0.46R |
| lasthalf | 1 | $-0.21 | 0% | -0.69R |
| noise | 1 | $0.59 | 100% | +0.94R |
| sip_orb | 4 | $-0.89 | 0% | -1.02R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 29 trades, P&L $-3.66, win rate 28%, average -0.20R. Other trades average +0.11R.

### Strategy experiment (since 2026-11-05)
| Strategy | Live | Shadow | Win rate | Profit factor | Avg R | P&L (live) | Verdict |
|---|---|---|---|---|---|---|---|
| sip_orb | 4 | 3 | 0% | 0.00 | -1.01R | $-0.89 | testing (7/40) |
| noise | 1 | 1 | 50% | 1.88 | +0.21R | $0.59 | testing (2/40) |
| lasthalf | 1 | 2 | 33% | 0.19 | -0.33R | $-0.21 | testing (3/40) |
| control | 1 | 0 | 0% | 0.00 | -0.92R | $-0.21 | testing (1/40) |

Shadow trades are signals that got no slot, replayed on the day's bars. Promote at 40+ trades with PF above 1.2; retire at 40 trades with average R below 0.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 54 |
| Profit factor at least 1.2 | no | 0.85 |
| Positive average R | no | -0.05R |
| Max drawdown under 6% of capital | yes | 3.48% |
| No risk rule breaches | no | 2 |

**Verdict:** stay on paper

