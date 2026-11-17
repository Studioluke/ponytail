## Risk review Monday 2026-11-16

**Kill switch:** off
**Account:** ACTIVE, equity $100,001.35, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $-0.64 | -$6.00 |
| Losing trades today | 3 | 3 |
| Weekly loss | $-0.64 | -$15.00 |
| Risk per trade | max $0.65 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.89 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| COIN | 0.491 | 121.75 | 120.66 | 0.54 | -0.55 | -1.03 | stop |
| SH | 1.798 | 33.31 | 32.95 | 0.65 | -0.07 | -0.11 | trail |
| SH | 1.781 | 33.59 | 33.43 | 0.28 | -0.02 | -0.07 | eod |

### Since paper trading began
73 trades, P&L $1.73, win rate 30%, profit factor 1.08, average +0.03R, max drawdown $10.43 (3.48%), longest losing streak 14.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| control | 3 | $-0.82 | 0% | -0.98R |
| core | 15 | $-1.75 | 40% | +0.00R |
| explore | 28 | $-4.80 | 32% | +0.00R |
| in_play | 4 | $4.79 | 50% | +0.46R |
| lasthalf | 5 | $-0.41 | 20% | -0.26R |
| noise | 5 | $0.27 | 20% | +0.02R |
| sip_orb | 13 | $4.45 | 23% | +0.32R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 29 trades, P&L $-3.66, win rate 28%, average -0.20R. Other trades average +0.17R.

### Strategy experiment (since 2026-11-05)
| Strategy | Live | Shadow | Win rate | Profit factor | Avg R | P&L (live) | Verdict |
|---|---|---|---|---|---|---|---|
| sip_orb | 13 | 14 | 26% | 2.13 | +0.42R | $4.45 | testing (27/40) |
| noise | 5 | 1 | 17% | 0.93 | -0.07R | $0.27 | testing (6/40) |
| lasthalf | 5 | 4 | 33% | 0.18 | -0.23R | $-0.41 | testing (9/40) |
| control | 3 | 3 | 0% | 0.00 | -0.99R | $-0.82 | testing (6/40) |
| sip_orb_wide | 0 | 9 | 22% | 0.97 | -0.09R | $0.00 | testing (9/40) |

Shadow trades are signals that got no slot, replayed on the day's bars. Promote at 40+ trades with PF above 1.2; retire at 40 trades with average R below 0.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 73 |
| Profit factor at least 1.2 | no | 1.08 |
| Positive average R | yes | +0.03R |
| Max drawdown under 6% of capital | yes | 3.48% |
| No risk rule breaches | no | 2 |

**Verdict:** stay on paper

