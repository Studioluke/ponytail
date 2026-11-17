## Risk review Tuesday 2026-11-17

**Kill switch:** off
**Account:** ACTIVE, equity $99,999.44, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $-1.89 | -$6.00 |
| Losing trades today | 7 | 3 |
| Weekly loss | $-2.53 | -$15.00 |
| Risk per trade | max $0.53 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.87 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| NKE | 1.475 | 40.59 | 40.37 | 0.32 | -0.49 | -1.51 | stop |
| LOW | 0.267 | 223.96 | 223.06 | 0.24 | -0.26 | -1.08 | stop |
| HD | 0.174 | 342.82 | 341.49 | 0.23 | -0.25 | -1.08 | stop |
| AAPL | 0.169 | 353.88 | 351.52 | 0.40 | -0.40 | -1.00 | stop |
| DIS | 0.495 | 120.95 | 120.44 | 0.25 | -0.26 | -1.03 | stop |
| SH | 1.76 | 33.95 | 33.65 | 0.53 | -0.16 | -0.30 | trail |
| SH | 1.759 | 34.01 | 33.84 | 0.30 | -0.07 | -0.23 | eod |

### Since paper trading began
80 trades, P&L $-0.16, win rate 28%, profit factor 0.99, average -0.05R, max drawdown $10.43 (3.48%), longest losing streak 14.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| control | 4 | $-1.22 | 0% | -0.99R |
| core | 15 | $-1.75 | 40% | +0.00R |
| explore | 28 | $-4.80 | 32% | +0.00R |
| in_play | 4 | $4.79 | 50% | +0.46R |
| lasthalf | 6 | $-0.48 | 17% | -0.25R |
| noise | 6 | $0.11 | 17% | -0.03R |
| sip_orb | 17 | $3.19 | 18% | -0.03R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 29 trades, P&L $-3.66, win rate 28%, average -0.20R. Other trades average +0.03R.

### Strategy experiment (since 2026-11-05)
| Strategy | Live | Shadow | Win rate | Profit factor | Avg R | P&L (live) | Verdict |
|---|---|---|---|---|---|---|---|
| sip_orb | 17 | 15 | 22% | 1.78 | +0.17R | $3.19 | testing (32/40) |
| noise | 6 | 1 | 14% | 0.74 | -0.10R | $0.11 | testing (7/40) |
| lasthalf | 6 | 4 | 30% | 0.16 | -0.23R | $-0.48 | testing (10/40) |
| control | 4 | 3 | 0% | 0.00 | -0.99R | $-1.22 | testing (7/40) |
| sip_orb_wide | 0 | 14 | 14% | 0.72 | -0.42R | $0.00 | testing (14/40) |

Shadow trades are signals that got no slot, replayed on the day's bars. Promote at 40+ trades with PF above 1.2; retire at 40 trades with average R below 0.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50
- 2026-11-17 NKE: lost -1.51R, stop did not hold

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 80 |
| Profit factor at least 1.2 | no | 0.99 |
| Positive average R | no | -0.05R |
| Max drawdown under 6% of capital | yes | 3.48% |
| No risk rule breaches | no | 3 |

**Verdict:** stay on paper

