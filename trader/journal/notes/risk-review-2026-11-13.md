## Risk review Friday 2026-11-13

**Kill switch:** off
**Account:** ACTIVE, equity $100,002.00, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $-0.22 | -$6.00 |
| Losing trades today | 2 | 3 |
| Weekly loss | $4.86 | -$15.00 |
| Risk per trade | max $0.45 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.86 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| SH | 1.803 | 33.10 | 32.85 | 0.45 | -0.11 | -0.24 | trail |
| SH | 1.815 | 32.98 | 32.80 | 0.33 | -0.11 | -0.34 | eod |

### Since paper trading began
70 trades, P&L $2.37, win rate 31%, profit factor 1.12, average +0.04R, max drawdown $10.43 (3.48%), longest losing streak 14.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| control | 3 | $-0.82 | 0% | -0.98R |
| core | 15 | $-1.75 | 40% | +0.00R |
| explore | 28 | $-4.80 | 32% | +0.00R |
| in_play | 4 | $4.79 | 50% | +0.46R |
| lasthalf | 4 | $-0.39 | 25% | -0.30R |
| noise | 4 | $0.34 | 25% | +0.05R |
| sip_orb | 12 | $5.00 | 25% | +0.43R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 29 trades, P&L $-3.66, win rate 28%, average -0.20R. Other trades average +0.21R.

### Strategy experiment (since 2026-11-05)
| Strategy | Live | Shadow | Win rate | Profit factor | Avg R | P&L (live) | Verdict |
|---|---|---|---|---|---|---|---|
| sip_orb | 12 | 13 | 28% | 2.49 | +0.53R | $5.00 | testing (25/40) |
| noise | 4 | 1 | 20% | 1.05 | -0.06R | $0.34 | testing (5/40) |
| lasthalf | 4 | 4 | 38% | 0.18 | -0.25R | $-0.39 | testing (8/40) |
| control | 3 | 3 | 0% | 0.00 | -0.99R | $-0.82 | testing (6/40) |
| sip_orb_wide | 0 | 7 | 29% | 1.53 | +0.17R | $0.00 | testing (7/40) |

Shadow trades are signals that got no slot, replayed on the day's bars. Promote at 40+ trades with PF above 1.2; retire at 40 trades with average R below 0.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 70 |
| Profit factor at least 1.2 | no | 1.12 |
| Positive average R | yes | +0.04R |
| Max drawdown under 6% of capital | yes | 3.48% |
| No risk rule breaches | no | 2 |

**Verdict:** stay on paper

