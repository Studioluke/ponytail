## Risk review Wednesday 2026-11-11

**Kill switch:** off
**Account:** ACTIVE, equity $99,999.68, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $0.96 | -$6.00 |
| Losing trades today | 0 | 3 |
| Weekly loss | $2.48 | -$15.00 |
| Risk per trade | max $0.64 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.73 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| DELL | 0.162 | 368.69 | 364.71 | 0.64 | 0.96 | +1.49 | eod |

**Risk actions:**
- 11:30 SPY risk_block: [noise] noise area 11:30: fallback: no band break by 11:30, SPY above its open 756.72; vetoed: research says skip SPY: premarket gap +0.94% is past the 0.75% gap rule, so the bot will skip it
- 15:30 SPY risk_block: [lasthalf] last half hour: SPY prior close to 10:00 up; vetoed: research says skip SPY: premarket gap +0.94% is past the 0.75% gap rule, so the bot will skip it

### Since paper trading began
63 trades, P&L $-0.01, win rate 32%, profit factor 1.00, average -0.04R, max drawdown $10.43 (3.48%), longest losing streak 14.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| control | 2 | $-0.44 | 0% | -0.97R |
| core | 15 | $-1.75 | 40% | +0.00R |
| explore | 28 | $-4.80 | 32% | +0.00R |
| in_play | 4 | $4.79 | 50% | +0.46R |
| lasthalf | 2 | $-0.32 | 0% | -0.51R |
| noise | 2 | $0.56 | 50% | +0.42R |
| sip_orb | 10 | $1.95 | 20% | -0.25R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 29 trades, P&L $-3.66, win rate 28%, average -0.20R. Other trades average +0.09R.

### Strategy experiment (since 2026-11-05)
| Strategy | Live | Shadow | Win rate | Profit factor | Avg R | P&L (live) | Verdict |
|---|---|---|---|---|---|---|---|
| sip_orb | 10 | 8 | 28% | 2.00 | +0.31R | $1.95 | testing (18/40) |
| noise | 2 | 1 | 33% | 1.72 | +0.10R | $0.56 | testing (3/40) |
| lasthalf | 2 | 4 | 33% | 0.15 | -0.30R | $-0.32 | testing (6/40) |
| control | 2 | 1 | 0% | 0.00 | -0.98R | $-0.44 | testing (3/40) |

Shadow trades are signals that got no slot, replayed on the day's bars. Promote at 40+ trades with PF above 1.2; retire at 40 trades with average R below 0.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 63 |
| Profit factor at least 1.2 | no | 1.00 |
| Positive average R | no | -0.04R |
| Max drawdown under 6% of capital | yes | 3.48% |
| No risk rule breaches | no | 2 |

**Verdict:** stay on paper

