## Risk review Friday 2026-10-30

**Kill switch:** off
**Account:** ACTIVE, equity $100,001.03, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $-0.66 | -$6.00 |
| Losing trades today | 2 | 3 |
| Weekly loss | $1.48 | -$15.00 |
| Risk per trade | max $0.63 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.84 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| NFLX | 0.95 | 62.99 | 62.33 | 0.63 | -0.63 | -1.00 | stop |
| AAPL | 0.171 | 348.77 | 346.48 | 0.39 | -0.40 | -1.02 | stop |
| COST | 0.059 | 1013.88 | 1011.16 | 0.16 | 0.37 | +2.31 | target |

**Risk actions:**
- 10:39 NFLX risk_taken: learning mode, trading anyway: gap +1.08% vs prior close 62.08 exceeds the 0.75% gap rule
- 10:45 AAPL risk_taken: learning mode, trading anyway: research says skip AAPL: Earnings (estimated date) (2026-10-29, after the session): the opening range is unreliable; premarket gap -1.09% is past the 0.75% gap rule, so the bot will skip it
- 11:44 COST risk_taken: learning mode, trading anyway: gap +1.71% vs prior close 995.86 exceeds the 0.75% gap rule

### Since paper trading began
26 trades, P&L $1.17, win rate 31%, profit factor 1.13, average -0.10R, max drawdown $6.11 (2.04%), longest losing streak 14.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| core | 6 | $-0.98 | 33% | -0.20R |
| explore | 17 | $-3.35 | 24% | -0.25R |
| in_play | 3 | $5.50 | 67% | +0.94R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 18 trades, P&L $-0.32, win rate 22%, average -0.29R. Other trades average +0.33R.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | no | 26 |
| Profit factor at least 1.2 | no | 1.13 |
| Positive average R | no | -0.10R |
| Max drawdown under 6% of capital | yes | 2.04% |
| No risk rule breaches | no | 2 |

**Verdict:** stay on paper

