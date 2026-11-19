## Risk review Thursday 2026-11-19

**Kill switch:** off
**Account:** ACTIVE, equity $100,001.07, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $0.13 | -$6.00 |
| Losing trades today | 1 | 3 |
| Weekly loss | $-0.84 | -$15.00 |
| Risk per trade | max $0.39 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.64 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| CRWD | 0.235 | 253.77 | 252.09 | 0.39 | -0.40 | -1.01 | stop |
| SH | 0.877 | 34.05 | 33.76 | 0.25 | 0.52 | +2.04 | eod |
| SPY | 0.083 | 716.52 | 712.98 | 0.29 | 0.00 | +0.00 | eod |

### Since paper trading began
89 trades, P&L $1.51, win rate 29%, profit factor 1.06, average -0.00R, max drawdown $10.43 (3.48%), longest losing streak 15.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| control | 6 | $-1.77 | 0% | -1.00R |
| core | 15 | $-1.75 | 40% | +0.00R |
| explore | 28 | $-4.80 | 32% | +0.00R |
| in_play | 4 | $4.79 | 50% | +0.46R |
| lasthalf | 8 | $-0.34 | 25% | -0.13R |
| noise | 8 | $0.43 | 25% | +0.15R |
| sip_orb | 20 | $4.95 | 25% | +0.19R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 29 trades, P&L $-3.66, win rate 28%, average -0.20R. Other trades average +0.09R.

### Strategy experiment (since 2026-11-05)
| Strategy | Live | Shadow | Win rate | Profit factor | Avg R | P&L (live) | Verdict |
|---|---|---|---|---|---|---|---|
| sip_orb | 20 | 23 | 26% | 2.20 | +0.37R | $4.95 | promote (more slots) |
| noise | 8 | 1 | 22% | 1.12 | +0.07R | $0.43 | testing (9/40) |
| lasthalf | 8 | 6 | 36% | 0.36 | -0.14R | $-0.34 | testing (14/40) |
| control | 6 | 3 | 0% | 0.00 | -1.00R | $-1.77 | testing (9/40) |
| sip_orb_wide | 0 | 25 | 28% | 1.27 | +0.05R | $0.00 | testing (25/40) |
| sip_orb_mkt | 0 | 2 | 0% | 0.00 | -1.00R | $0.00 | testing (2/40) |
| noise_band | 0 | 0 | | | | | no trades yet |

**sip_orb live only:** 20 trades, win rate 25%, PF 1.93, avg +0.19R, $4.95.
**sip_orb worst day (live+shadow):** 2026-11-17, -5.70R over 5 trades.
**sip_orb since promotion (2026-11-19):** 3 trades, avg -1.00R, 3/40.

Shadow trades are signals that got no slot, replayed on the day's bars. Promote at 40+ trades with PF above 1.2; retire at 40 trades with average R below 0.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50
- 2026-11-17 NKE: lost -1.51R, stop did not hold

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 89 |
| Profit factor at least 1.2 | no | 1.06 |
| Positive average R | no | -0.00R |
| Max drawdown under 6% of capital | yes | 3.48% |
| No risk rule breaches | no | 3 |

**Verdict:** stay on paper

