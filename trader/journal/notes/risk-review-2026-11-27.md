## Risk review Friday 2026-11-27

**Kill switch:** off
**Account:** ACTIVE, equity $100,005.12, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $-0.31 | -$6.00 |
| Losing trades today | 2 | 3 |
| Weekly loss | $3.22 | -$15.00 |
| Risk per trade | max $0.30 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.84 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| GILD | 0.34 | 176.01 | 175.29 | 0.24 | -0.26 | -1.06 | stop |
| SH | 0.875 | 34.18 | 33.84 | 0.30 | -0.05 | -0.17 | trail |

### Since paper trading began
110 trades, P&L $5.66, win rate 30%, profit factor 1.20, average +0.07R, max drawdown $10.43 (3.48%), longest losing streak 15.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| control | 6 | $-1.77 | 0% | -1.00R |
| core | 15 | $-1.75 | 40% | +0.00R |
| explore | 28 | $-4.80 | 32% | +0.00R |
| in_play | 4 | $4.79 | 50% | +0.46R |
| lasthalf | 12 | $-1.28 | 17% | -0.32R |
| noise | 13 | $1.56 | 31% | +0.20R |
| sip_orb | 32 | $8.91 | 31% | +0.42R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 29 trades, P&L $-3.66, win rate 28%, average -0.20R. Other trades average +0.17R.

### Strategy experiment (since 2026-11-05)
| Strategy | Live | Shadow | Win rate | Profit factor | Avg R | P&L (live) | Verdict |
|---|---|---|---|---|---|---|---|
| sip_orb | 32 | 28 | 30% | 2.27 | +0.50R | $8.91 | promote (more slots) |
| noise | 13 | 1 | 29% | 1.97 | +0.15R | $1.56 | testing (14/40) |
| lasthalf | 12 | 8 | 30% | 0.16 | -0.28R | $-1.28 | testing (20/40) |
| control | 6 | 8 | 21% | 0.19 | -0.67R | $-1.77 | testing (14/40) |
| sip_orb_wide | 0 | 42 | 48% | 2.26 | +0.58R | $0.00 | promote (more slots) |
| sip_orb_mkt | 0 | 2 | 0% | 0.00 | -1.00R | $0.00 | testing (2/40) |
| sip_orb_gapdn | 0 | 0 | | | | | no trades yet |
| noise_band | 0 | 2 | 50% | 21.76 | +1.16R | $0.00 | testing (2/40) |
| lasthalf_vwap | 0 | 0 | | | | | no trades yet |

**sip_orb live only:** 32 trades, win rate 31%, PF 2.13, avg +0.42R, $8.91.
**sip_orb worst day (live+shadow):** 2026-11-17, -5.70R over 5 trades.
**sip_orb since promotion (2026-11-19):** 20 trades, avg +0.56R, 20/40.

Shadow trades are signals that got no slot, replayed on the day's bars. Promote at 40+ trades with PF above 1.2; retire at 40 trades with average R below 0.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50
- 2026-11-17 NKE: lost -1.51R, stop did not hold

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 110 |
| Profit factor at least 1.2 | yes | 1.20 |
| Positive average R | yes | +0.07R |
| Max drawdown under 6% of capital | yes | 3.48% |
| No risk rule breaches | no | 3 |

**Same gate, 2026-11-05 onward:** At least 30 closed paper trades yes (63); Profit factor at least 1.2 yes (1.61); Positive average R yes (+0.10R); Max drawdown under 6% of capital yes (1.17%); No risk rule breaches no (1). Does not pass.

**Verdict:** stay on paper

