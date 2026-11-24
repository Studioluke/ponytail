## Risk review Tuesday 2026-11-24

**Kill switch:** off
**Account:** ACTIVE, equity $100,005.86, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $4.64 | -$6.00 |
| Losing trades today | 2 | 3 |
| Weekly loss | $3.94 | -$15.00 |
| Risk per trade | max $0.72 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.90 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| SH | 0.864 | 34.66 | 34.28 | 0.33 | -0.19 | -0.58 | trail |
| GILD | 0.344 | 173.80 | 172.75 | 0.36 | 1.57 | +4.35 | eod |
| VRTX | 0.108 | 552.28 | 549.43 | 0.31 | 1.21 | +3.93 | eod |
| MRNA | 0.273 | 219.43 | 216.80 | 0.72 | 2.28 | +3.18 | eod |
| SH | 1.73 | 34.59 | 34.41 | 0.31 | -0.22 | -0.71 | eod |

### Since paper trading began
102 trades, P&L $6.38, win rate 31%, profit factor 1.25, average +0.08R, max drawdown $10.43 (3.48%), longest losing streak 15.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| control | 6 | $-1.77 | 0% | -1.00R |
| core | 15 | $-1.75 | 40% | +0.00R |
| explore | 28 | $-4.80 | 32% | +0.00R |
| in_play | 4 | $4.79 | 50% | +0.46R |
| lasthalf | 11 | $-1.04 | 18% | -0.30R |
| noise | 11 | $1.66 | 36% | +0.26R |
| sip_orb | 27 | $9.29 | 33% | +0.45R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 29 trades, P&L $-3.66, win rate 28%, average -0.20R. Other trades average +0.18R.

### Strategy experiment (since 2026-11-05)
| Strategy | Live | Shadow | Win rate | Profit factor | Avg R | P&L (live) | Verdict |
|---|---|---|---|---|---|---|---|
| sip_orb | 27 | 26 | 30% | 2.42 | +0.47R | $9.29 | promote (more slots) |
| noise | 11 | 1 | 33% | 2.14 | +0.20R | $1.66 | testing (12/40) |
| lasthalf | 11 | 8 | 32% | 0.19 | -0.27R | $-1.04 | testing (19/40) |
| control | 6 | 7 | 15% | 0.08 | -0.80R | $-1.77 | testing (13/40) |
| sip_orb_wide | 0 | 35 | 40% | 1.73 | +0.31R | $0.00 | testing (35/40) |
| sip_orb_mkt | 0 | 2 | 0% | 0.00 | -1.00R | $0.00 | testing (2/40) |
| noise_band | 0 | 1 | 100% | inf | +2.44R | $0.00 | testing (1/40) |

**sip_orb live only:** 27 trades, win rate 33%, PF 2.53, avg +0.45R, $9.29.
**sip_orb worst day (live+shadow):** 2026-11-17, -5.70R over 5 trades.
**sip_orb since promotion (2026-11-19):** 13 trades, avg +0.47R, 13/40.

Shadow trades are signals that got no slot, replayed on the day's bars. Promote at 40+ trades with PF above 1.2; retire at 40 trades with average R below 0.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50
- 2026-11-17 NKE: lost -1.51R, stop did not hold

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 102 |
| Profit factor at least 1.2 | yes | 1.25 |
| Positive average R | yes | +0.08R |
| Max drawdown under 6% of capital | yes | 3.48% |
| No risk rule breaches | no | 3 |

**Verdict:** stay on paper

