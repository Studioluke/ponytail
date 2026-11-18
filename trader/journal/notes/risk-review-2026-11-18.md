## Risk review Wednesday 2026-11-18

**Kill switch:** off
**Account:** ACTIVE, equity $100,000.97, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $1.56 | -$6.00 |
| Losing trades today | 3 | 3 |
| Weekly loss | $-0.97 | -$15.00 |
| Risk per trade | max $0.55 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.84 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| AAPL | 0.119 | 355.98 | 353.72 | 0.27 | -0.27 | -1.00 | stop |
| SH | 0.877 | 34.09 | 33.74 | 0.31 | -0.20 | -0.65 | trail |
| QQQ | 0.056 | 662.49 | 657.60 | 0.27 | -0.28 | -1.02 | stop |
| LOW | 0.275 | 217.05 | 215.81 | 0.34 | 1.34 | +3.93 | eod |
| NKE | 1.672 | 35.79 | 35.46 | 0.55 | 0.82 | +1.49 | eod |
| SPY | 0.082 | 729.72 | 726.09 | 0.30 | 0.14 | +0.47 | eod |

**Risk actions:**
- 13:37 MSFT risk_block: [control] ORB break of 508.39 (range 502.10-508.39), VWAP 504.20, stop 4.65 below (ATR 18.60); vetoed: FOMC day: no new entries 13:30-15:00 ET

### Since paper trading began
86 trades, P&L $1.39, win rate 29%, profit factor 1.06, average -0.01R, max drawdown $10.43 (3.48%), longest losing streak 15.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| control | 6 | $-1.77 | 0% | -1.00R |
| core | 15 | $-1.75 | 40% | +0.00R |
| explore | 28 | $-4.80 | 32% | +0.00R |
| in_play | 4 | $4.79 | 50% | +0.46R |
| lasthalf | 7 | $-0.34 | 29% | -0.15R |
| noise | 7 | $-0.09 | 14% | -0.12R |
| sip_orb | 19 | $5.35 | 26% | +0.26R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 29 trades, P&L $-3.66, win rate 28%, average -0.20R. Other trades average +0.08R.

### Strategy experiment (since 2026-11-05)
| Strategy | Live | Shadow | Win rate | Profit factor | Avg R | P&L (live) | Verdict |
|---|---|---|---|---|---|---|---|
| sip_orb | 19 | 21 | 28% | 2.41 | +0.47R | $5.35 | promote (more slots) |
| noise | 7 | 1 | 12% | 0.59 | -0.17R | $-0.09 | testing (8/40) |
| lasthalf | 7 | 5 | 42% | 0.40 | -0.14R | $-0.34 | testing (12/40) |
| control | 6 | 3 | 0% | 0.00 | -1.00R | $-1.77 | testing (9/40) |
| sip_orb_wide | 0 | 22 | 32% | 1.55 | +0.20R | $0.00 | testing (22/40) |
| sip_orb_mkt | 0 | 0 | | | | | no trades yet |
| noise_band | 0 | 0 | | | | | no trades yet |

**sip_orb live only:** 19 trades, win rate 26%, PF 2.08, avg +0.26R, $5.35.
**sip_orb worst day (live+shadow):** 2026-11-17, -5.70R over 5 trades.

Shadow trades are signals that got no slot, replayed on the day's bars. Promote at 40+ trades with PF above 1.2; retire at 40 trades with average R below 0.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50
- 2026-11-17 NKE: lost -1.51R, stop did not hold

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 86 |
| Profit factor at least 1.2 | no | 1.06 |
| Positive average R | no | -0.01R |
| Max drawdown under 6% of capital | yes | 3.48% |
| No risk rule breaches | no | 3 |

**Verdict:** stay on paper

