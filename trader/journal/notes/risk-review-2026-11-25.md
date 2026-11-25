## Risk review Wednesday 2026-11-25

**Kill switch:** off
**Account:** ACTIVE, equity $100,005.44, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $-0.41 | -$6.00 |
| Losing trades today | 5 | 3 |
| Weekly loss | $3.53 | -$15.00 |
| Risk per trade | max $1.10 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.94 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| C | 0.539 | 110.90 | 110.43 | 0.25 | -0.26 | -1.03 | stop |
| DELL | 0.214 | 278.75 | 273.60 | 1.10 | -1.10 | -1.00 | stop |
| SH | 1.689 | 35.44 | 35.08 | 0.61 | -0.05 | -0.08 | trail |
| CVX | 0.285 | 209.87 | 209.24 | 0.18 | -0.18 | -1.00 | stop |
| BAC | 1.259 | 47.55 | 47.33 | 0.28 | 1.42 | +5.13 | eod |
| SH | 1.73 | 34.65 | 34.41 | 0.42 | -0.24 | -0.58 | eod |

### Since paper trading began
108 trades, P&L $5.97, win rate 31%, profit factor 1.22, average +0.09R, max drawdown $10.43 (3.48%), longest losing streak 15.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| control | 6 | $-1.77 | 0% | -1.00R |
| core | 15 | $-1.75 | 40% | +0.00R |
| explore | 28 | $-4.80 | 32% | +0.00R |
| in_play | 4 | $4.79 | 50% | +0.46R |
| lasthalf | 12 | $-1.28 | 17% | -0.32R |
| noise | 12 | $1.61 | 33% | +0.23R |
| sip_orb | 31 | $9.17 | 32% | +0.46R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 29 trades, P&L $-3.66, win rate 28%, average -0.20R. Other trades average +0.19R.

### Strategy experiment (since 2026-11-05)
| Strategy | Live | Shadow | Win rate | Profit factor | Avg R | P&L (live) | Verdict |
|---|---|---|---|---|---|---|---|
| sip_orb | 31 | 28 | 31% | 2.32 | +0.53R | $9.17 | promote (more slots) |
| noise | 12 | 1 | 31% | 2.05 | +0.18R | $1.61 | testing (13/40) |
| lasthalf | 12 | 8 | 30% | 0.16 | -0.28R | $-1.28 | testing (20/40) |
| control | 6 | 8 | 21% | 0.19 | -0.67R | $-1.77 | testing (14/40) |
| sip_orb_wide | 0 | 41 | 46% | 2.22 | +0.56R | $0.00 | promote (more slots) |
| sip_orb_mkt | 0 | 2 | 0% | 0.00 | -1.00R | $0.00 | testing (2/40) |
| sip_orb_gapdn | 0 | 0 | | | | | no trades yet |
| noise_band | 0 | 2 | 50% | 21.76 | +1.16R | $0.00 | testing (2/40) |
| lasthalf_vwap | 0 | 0 | | | | | no trades yet |

**sip_orb live only:** 31 trades, win rate 32%, PF 2.20, avg +0.46R, $9.17.
**sip_orb worst day (live+shadow):** 2026-11-17, -5.70R over 5 trades.
**sip_orb since promotion (2026-11-19):** 19 trades, avg +0.65R, 19/40.

Shadow trades are signals that got no slot, replayed on the day's bars. Promote at 40+ trades with PF above 1.2; retire at 40 trades with average R below 0.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50
- 2026-11-17 NKE: lost -1.51R, stop did not hold

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 108 |
| Profit factor at least 1.2 | yes | 1.22 |
| Positive average R | yes | +0.09R |
| Max drawdown under 6% of capital | yes | 3.48% |
| No risk rule breaches | no | 3 |

**Same gate, 2026-11-05 onward:** At least 30 closed paper trades yes (61); Profit factor at least 1.2 yes (1.66); Positive average R yes (+0.12R); Max drawdown under 6% of capital yes (1.17%); No risk rule breaches no (1). Does not pass.

**Verdict:** stay on paper

