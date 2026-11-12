## Risk review Thursday 2026-11-05

**Kill switch:** off
**Account:** ACTIVE, equity $99,998.24, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $0.22 | -$6.00 |
| Losing trades today | 1 | 3 |
| Weekly loss | $-2.73 | -$15.00 |
| Risk per trade | max $0.63 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.88 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| QCOM | 0.38 | 157.31 | 156.47 | 0.32 | -0.37 | -1.16 | stop |
| SH | 1.789 | 33.47 | 33.12 | 0.63 | 0.59 | +0.94 | eod |

**Risk actions:**
- 10:00 SH risk_block: [noise] noise area 10:00: SPY 754.19 below lower band 764.38; vetoed: stale data: last bar 14:55, now 10:00

### Since paper trading began
49 trades, P&L $-1.54, win rate 37%, profit factor 0.90, average +0.03R, max drawdown $10.43 (3.48%), longest losing streak 14.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| core | 15 | $-1.75 | 40% | +0.00R |
| explore | 28 | $-4.80 | 32% | +0.00R |
| in_play | 4 | $4.79 | 50% | +0.46R |
| noise | 1 | $0.59 | 100% | +0.94R |
| sip_orb | 1 | $-0.37 | 0% | -1.16R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 29 trades, P&L $-3.66, win rate 28%, average -0.20R. Other trades average +0.37R.

### Strategy experiment (since 2026-11-05)
| Strategy | Live | Shadow | Win rate | Profit factor | Avg R | P&L (live) | Verdict |
|---|---|---|---|---|---|---|---|
| sip_orb | 1 | 3 | 0% | 0.00 | -1.04R | $-0.37 | testing (4/40) |
| noise | 1 | 0 | 100% | inf | +0.94R | $0.59 | testing (1/40) |
| lasthalf | 0 | 1 | 100% | inf | +0.23R | $0.00 | testing (1/40) |
| control | 0 | 0 | | | | | no trades yet |

Shadow trades are signals that got no slot, replayed on the day's bars. Promote at 40+ trades with PF above 1.2; retire at 40 trades with average R below 0.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 49 |
| Profit factor at least 1.2 | no | 0.90 |
| Positive average R | yes | +0.03R |
| Max drawdown under 6% of capital | yes | 3.48% |
| No risk rule breaches | no | 2 |

**Verdict:** stay on paper

