## Risk review Monday 2026-11-09

**Kill switch:** off
**Account:** ACTIVE, equity $100,000.17, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $2.92 | -$6.00 |
| Losing trades today | 2 | 3 |
| Weekly loss | $2.92 | -$15.00 |
| Risk per trade | max $0.90 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.84 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| ABNB | 0.303 | 197.49 | 195.96 | 0.46 | -0.45 | -0.97 | stop |
| NVDA | 0.341 | 175.41 | 174.39 | 0.35 | -0.35 | -1.01 | stop |
| LRCX | 0.287 | 208.41 | 205.27 | 0.90 | 3.72 | +4.13 | eod |

**Risk actions:**
- 10:00 SPY risk_block: [noise] noise area 10:00: SPY 747.76 above upper band 744.07; vetoed: research says skip SPY: premarket gap +0.86% is past the 0.75% gap rule, so the bot will skip it
- 15:30 SPY risk_block: [lasthalf] last half hour: SPY prior close to 10:00 up; vetoed: research says skip SPY: premarket gap +0.86% is past the 0.75% gap rule, so the bot will skip it

### Since paper trading began
57 trades, P&L $0.44, win rate 33%, profit factor 1.02, average -0.01R, max drawdown $10.43 (3.48%), longest losing streak 14.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| control | 1 | $-0.21 | 0% | -0.92R |
| core | 15 | $-1.75 | 40% | +0.00R |
| explore | 28 | $-4.80 | 32% | +0.00R |
| in_play | 4 | $4.79 | 50% | +0.46R |
| lasthalf | 1 | $-0.21 | 0% | -0.69R |
| noise | 1 | $0.59 | 100% | +0.94R |
| sip_orb | 7 | $2.03 | 14% | -0.27R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 29 trades, P&L $-3.66, win rate 28%, average -0.20R. Other trades average +0.18R.

### Strategy experiment (since 2026-11-05)
| Strategy | Live | Shadow | Win rate | Profit factor | Avg R | P&L (live) | Verdict |
|---|---|---|---|---|---|---|---|
| sip_orb | 7 | 6 | 23% | 2.20 | +0.12R | $2.03 | testing (13/40) |
| noise | 1 | 1 | 50% | 1.88 | +0.21R | $0.59 | testing (2/40) |
| lasthalf | 1 | 3 | 25% | 0.13 | -0.39R | $-0.21 | testing (4/40) |
| control | 1 | 0 | 0% | 0.00 | -0.92R | $-0.21 | testing (1/40) |

Shadow trades are signals that got no slot, replayed on the day's bars. Promote at 40+ trades with PF above 1.2; retire at 40 trades with average R below 0.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 57 |
| Profit factor at least 1.2 | no | 1.02 |
| Positive average R | no | -0.01R |
| Max drawdown under 6% of capital | yes | 3.48% |
| No risk rule breaches | no | 2 |

**Verdict:** stay on paper

