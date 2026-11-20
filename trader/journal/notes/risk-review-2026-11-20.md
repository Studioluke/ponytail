## Risk review Friday 2026-11-20

**Kill switch:** off
**Account:** ACTIVE, equity $100,001.96, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $0.91 | -$6.00 |
| Losing trades today | 2 | 3 |
| Weekly loss | $0.07 | -$15.00 |
| Risk per trade | max $0.63 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.86 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| NFLX | 1.014 | 58.97 | 58.78 | 0.19 | -0.20 | -1.04 | stop |
| SPY | 0.086 | 692.64 | 688.97 | 0.32 | -0.32 | -1.01 | stop |
| COP | 0.44 | 135.86 | 135.34 | 0.23 | 0.03 | +0.13 | eod |
| SH | 1.699 | 35.23 | 34.86 | 0.63 | 1.41 | +2.24 | eod |

### Since paper trading began
93 trades, P&L $2.43, win rate 30%, profit factor 1.10, average +0.00R, max drawdown $10.43 (3.48%), longest losing streak 15.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| control | 6 | $-1.77 | 0% | -1.00R |
| core | 15 | $-1.75 | 40% | +0.00R |
| explore | 28 | $-4.80 | 32% | +0.00R |
| in_play | 4 | $4.79 | 50% | +0.46R |
| lasthalf | 9 | $-0.66 | 22% | -0.23R |
| noise | 9 | $1.84 | 33% | +0.38R |
| sip_orb | 22 | $4.78 | 27% | +0.13R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 29 trades, P&L $-3.66, win rate 28%, average -0.20R. Other trades average +0.09R.

### Strategy experiment (since 2026-11-05)
| Strategy | Live | Shadow | Win rate | Profit factor | Avg R | P&L (live) | Verdict |
|---|---|---|---|---|---|---|---|
| sip_orb | 22 | 24 | 26% | 2.13 | +0.30R | $4.78 | promote (more slots) |
| noise | 9 | 1 | 30% | 2.54 | +0.29R | $1.84 | testing (10/40) |
| lasthalf | 9 | 7 | 31% | 0.22 | -0.25R | $-0.66 | testing (16/40) |
| control | 6 | 5 | 0% | 0.00 | -1.00R | $-1.77 | testing (11/40) |
| sip_orb_wide | 0 | 28 | 29% | 1.17 | -0.02R | $0.00 | testing (28/40) |
| sip_orb_mkt | 0 | 2 | 0% | 0.00 | -1.00R | $0.00 | testing (2/40) |
| noise_band | 0 | 1 | 100% | inf | +2.44R | $0.00 | testing (1/40) |

**sip_orb live only:** 22 trades, win rate 27%, PF 1.86, avg +0.13R, $4.78.
**sip_orb worst day (live+shadow):** 2026-11-17, -5.70R over 5 trades.
**sip_orb since promotion (2026-11-19):** 6 trades, avg -0.82R, 6/40.

Shadow trades are signals that got no slot, replayed on the day's bars. Promote at 40+ trades with PF above 1.2; retire at 40 trades with average R below 0.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50
- 2026-11-17 NKE: lost -1.51R, stop did not hold

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 93 |
| Profit factor at least 1.2 | no | 1.10 |
| Positive average R | yes | +0.00R |
| Max drawdown under 6% of capital | yes | 3.48% |
| No risk rule breaches | no | 3 |

**Verdict:** stay on paper

