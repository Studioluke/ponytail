## Risk review Thursday 2026-11-12

**Kill switch:** off
**Account:** ACTIVE, equity $100,002.24, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $2.60 | -$6.00 |
| Losing trades today | 3 | 3 |
| Weekly loss | $5.07 | -$15.00 |
| Risk per trade | max $0.39 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.84 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| AVGO | 0.165 | 362.42 | 360.07 | 0.39 | -0.40 | -1.03 | stop |
| AAPL | 0.166 | 359.09 | 356.82 | 0.38 | -0.38 | -1.01 | stop |
| SPY | 0.039 | 761.89 | 754.32 | 0.30 | -0.11 | -0.37 | trail |
| NVDA | 0.382 | 156.43 | 155.40 | 0.39 | 3.45 | +8.77 | eod |
| SH | 1.826 | 32.77 | 32.61 | 0.29 | 0.04 | +0.14 | eod |

### Since paper trading began
68 trades, P&L $2.59, win rate 32%, profit factor 1.13, average +0.05R, max drawdown $10.43 (3.48%), longest losing streak 14.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| control | 3 | $-0.82 | 0% | -0.98R |
| core | 15 | $-1.75 | 40% | +0.00R |
| explore | 28 | $-4.80 | 32% | +0.00R |
| in_play | 4 | $4.79 | 50% | +0.46R |
| lasthalf | 3 | $-0.28 | 33% | -0.29R |
| noise | 3 | $0.45 | 33% | +0.15R |
| sip_orb | 12 | $5.00 | 25% | +0.43R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 29 trades, P&L $-3.66, win rate 28%, average -0.20R. Other trades average +0.24R.

### Strategy experiment (since 2026-11-05)
| Strategy | Live | Shadow | Win rate | Profit factor | Avg R | P&L (live) | Verdict |
|---|---|---|---|---|---|---|---|
| sip_orb | 12 | 13 | 28% | 2.49 | +0.53R | $5.00 | testing (25/40) |
| noise | 3 | 1 | 25% | 1.30 | -0.02R | $0.45 | testing (4/40) |
| lasthalf | 3 | 4 | 43% | 0.22 | -0.23R | $-0.28 | testing (7/40) |
| control | 3 | 3 | 0% | 0.00 | -0.99R | $-0.82 | testing (6/40) |
| sip_orb_wide | 0 | 7 | 29% | 1.53 | +0.17R | $0.00 | testing (7/40) |

Shadow trades are signals that got no slot, replayed on the day's bars. Promote at 40+ trades with PF above 1.2; retire at 40 trades with average R below 0.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 68 |
| Profit factor at least 1.2 | no | 1.13 |
| Positive average R | yes | +0.05R |
| Max drawdown under 6% of capital | yes | 3.48% |
| No risk rule breaches | no | 2 |

**Verdict:** stay on paper

