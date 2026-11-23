## Risk review Monday 2026-11-23

**Kill switch:** off
**Account:** ACTIVE, equity $100,001.25, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $-0.70 | -$6.00 |
| Losing trades today | 3 | 3 |
| Weekly loss | $-0.70 | -$15.00 |
| Risk per trade | max $0.36 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.84 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| IBM | 0.259 | 230.69 | 230.07 | 0.16 | -0.18 | -1.12 | stop |
| UNH | 0.181 | 330.63 | 328.62 | 0.36 | -0.37 | -1.02 | stop |
| SH | 0.875 | 34.19 | 33.83 | 0.31 | 0.01 | +0.03 | trail |
| SPY | 0.082 | 724.41 | 720.86 | 0.29 | -0.16 | -0.55 | eod |

### Since paper trading began
97 trades, P&L $1.73, win rate 30%, profit factor 1.07, average -0.02R, max drawdown $10.43 (3.48%), longest losing streak 15.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| control | 6 | $-1.77 | 0% | -1.00R |
| core | 15 | $-1.75 | 40% | +0.00R |
| explore | 28 | $-4.80 | 32% | +0.00R |
| in_play | 4 | $4.79 | 50% | +0.46R |
| lasthalf | 10 | $-0.82 | 20% | -0.26R |
| noise | 10 | $1.85 | 40% | +0.35R |
| sip_orb | 24 | $4.23 | 25% | +0.03R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 29 trades, P&L $-3.66, win rate 28%, average -0.20R. Other trades average +0.05R.

### Strategy experiment (since 2026-11-05)
| Strategy | Live | Shadow | Win rate | Profit factor | Avg R | P&L (live) | Verdict |
|---|---|---|---|---|---|---|---|
| sip_orb | 24 | 24 | 25% | 2.03 | +0.24R | $4.23 | promote (more slots) |
| noise | 10 | 1 | 36% | 2.55 | +0.27R | $1.85 | testing (11/40) |
| lasthalf | 10 | 8 | 33% | 0.21 | -0.24R | $-0.82 | testing (18/40) |
| control | 6 | 5 | 0% | 0.00 | -1.00R | $-1.77 | testing (11/40) |
| sip_orb_wide | 0 | 30 | 33% | 1.32 | +0.08R | $0.00 | testing (30/40) |
| sip_orb_mkt | 0 | 2 | 0% | 0.00 | -1.00R | $0.00 | testing (2/40) |
| noise_band | 0 | 1 | 100% | inf | +2.44R | $0.00 | testing (1/40) |

**sip_orb live only:** 24 trades, win rate 25%, PF 1.69, avg +0.03R, $4.23.
**sip_orb worst day (live+shadow):** 2026-11-17, -5.70R over 5 trades.
**sip_orb since promotion (2026-11-19):** 8 trades, avg -0.88R, 8/40.

Shadow trades are signals that got no slot, replayed on the day's bars. Promote at 40+ trades with PF above 1.2; retire at 40 trades with average R below 0.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50
- 2026-11-17 NKE: lost -1.51R, stop did not hold

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 97 |
| Profit factor at least 1.2 | no | 1.07 |
| Positive average R | no | -0.02R |
| Max drawdown under 6% of capital | yes | 3.48% |
| No risk rule breaches | no | 3 |

**Verdict:** stay on paper

