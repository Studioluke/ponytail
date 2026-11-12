## Risk review Wednesday 2026-11-04

**Kill switch:** off
**Account:** ACTIVE, equity $99,998.04, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $-0.38 | -$6.00 |
| Losing trades today | 3 | 3 |
| Weekly loss | $-2.95 | -$15.00 |
| Risk per trade | max $1.43 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.80 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| AMD | 0.078 | 510.70 | 492.40 | 1.43 | -1.43 | -1.00 | stop |
| SPY | 0.077 | 767.99 | 765.23 | 0.21 | -0.21 | -0.99 | stop |
| QQQ | 0.085 | 698.47 | 692.70 | 0.49 | -0.49 | -1.00 | stop |
| DIA | 0.112 | 529.86 | 528.40 | 0.16 | 0.32 | +1.96 | target |
| NFLX | 0.916 | 65.28 | 64.63 | 0.60 | 1.26 | +2.12 | target |
| AAPL | 0.17 | 350.78 | 345.71 | 0.86 | 0.18 | +0.21 | eod |

**Risk actions:**
- 09:46 NFLX risk_taken: learning mode, trading anyway: gap +1.88% vs prior close 63.38 exceeds the 0.75% gap rule
- 09:47 SPY risk_taken: learning mode, trading anyway: gap +1.14% vs prior close 754.38 exceeds the 0.75% gap rule; research says skip SPY: premarket gap +0.91% is past the 0.75% gap rule, so the bot will skip it
- 09:47 AMD risk_taken: learning mode, trading anyway: research says skip AMD: Earnings (confirmed; call 5:00 ET) (2026-11-03, after the session): the opening range is unreliable
- 09:49 AAPL risk_taken: learning mode, trading anyway: gap +3.07% vs prior close 331.7 exceeds the 0.75% gap rule; research says skip AAPL: premarket gap +1.84% is past the 0.75% gap rule, so the bot will skip it
- 09:49 WMT risk_block: ORB break of 127.39 (range 125.92-127.39), VWAP 126.96; vetoed: 5 positions open, max 5
- 09:54 GOOGL risk_block: ORB break of 290.17 (range 283.73-290.17), VWAP 288.43; vetoed: 5 positions open, max 5
- 09:54 COST risk_block: ORB break of 1037.49 (range 1028.51-1037.49), VWAP 1033.78; vetoed: 5 positions open, max 5
- 09:56 MSFT risk_block: ORB break of 551.76 (range 542.66-551.76), VWAP 548.68; vetoed: 5 positions open, max 5
- 09:56 AMZN risk_block: ORB break of 269.97 (range 263.90-269.97), VWAP 268.17; vetoed: 5 positions open, max 5
- 10:16 BKNG risk_block: ORB break of 170.19 (range 160.69-170.19), VWAP 168.71; vetoed: 5 positions open, max 5
- 10:42 DIA risk_taken: learning mode, trading anyway: gap +2.08% vs prior close 517.02 exceeds the 0.75% gap rule; research says skip DIA: premarket gap +1.78% is past the 0.75% gap rule, so the bot will skip it
- 10:52  halted: 3 losing trades today

### Since paper trading began
47 trades, P&L $-1.76, win rate 36%, profit factor 0.89, average +0.04R, max drawdown $10.43 (3.48%), longest losing streak 14.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| core | 15 | $-1.75 | 40% | +0.00R |
| explore | 28 | $-4.80 | 32% | +0.00R |
| in_play | 4 | $4.79 | 50% | +0.46R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 29 trades, P&L $-3.66, win rate 28%, average -0.20R. Other trades average +0.42R.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 47 |
| Profit factor at least 1.2 | no | 0.89 |
| Positive average R | yes | +0.04R |
| Max drawdown under 6% of capital | yes | 3.48% |
| No risk rule breaches | no | 2 |

**Verdict:** stay on paper

