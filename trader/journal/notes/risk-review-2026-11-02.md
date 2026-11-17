## Risk review Monday 2026-11-02

**Kill switch:** off
**Account:** ACTIVE, equity $99,999.19, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $-1.83 | -$6.00 |
| Losing trades today | 5 | 3 |
| Weekly loss | $-1.83 | -$15.00 |
| Risk per trade | max $1.00 today | $1.50 |
| Open positions | 0 now | 5 |
| Position size | max $59.84 today | $60.00 (20% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| SPY | 0.078 | 760.09 | 759.37 | 0.06 | 0.12 | +2.14 | target |
| DIA | 0.114 | 522.03 | 521.28 | 0.09 | 0.17 | +1.99 | target |
| GOOGL | 0.208 | 286.67 | 284.36 | 0.48 | -0.48 | -1.00 | stop |
| MSFT | 0.113 | 528.80 | 524.52 | 0.48 | -0.49 | -1.01 | stop |
| COST | 0.058 | 1026.03 | 1020.27 | 0.33 | 0.72 | +2.16 | target |
| TSLA | 0.145 | 410.32 | 406.88 | 0.50 | -0.50 | -1.00 | stop |
| NFLX | 0.952 | 62.86 | 62.46 | 0.38 | -0.38 | -1.00 | stop |
| AMZN | 0.238 | 250.56 | 246.35 | 1.00 | -1.00 | -1.00 | stop |

**Risk actions:**
- 09:46 DIA risk_taken: learning mode, trading anyway: gap +0.75% vs prior close 517 exceeds the 0.75% gap rule; research says skip DIA: premarket gap +0.77% is past the 0.75% gap rule, so the bot will skip it
- 09:49 GOOGL risk_taken: learning mode, trading anyway: gap +0.89% vs prior close 279.9 exceeds the 0.75% gap rule
- 09:49 AMZN risk_taken: learning mode, trading anyway: gap +1.14% vs prior close 240.345 exceeds the 0.75% gap rule; research says skip AMZN: premarket gap +0.79% is past the 0.75% gap rule, so the bot will skip it
- 09:56 IWM risk_block: ORB break of 282.01 (range 280.57-282.01), VWAP 281.53; vetoed: 5 positions open, max 5
- 10:00 AVGO risk_block: ORB break of 328.38 (range 324.43-328.38), VWAP 326.50; vetoed: 5 positions open, max 5
- 10:04 META risk_block: ORB break of 619.03 (range 610.09-619.03), VWAP 615.06; vetoed: 5 positions open, max 5
- 10:13 QQQ risk_block: ORB break of 695.87 (range 693.36-695.87), VWAP 694.93; vetoed: 5 positions open, max 5
- 10:22 NVDA risk_block: ORB break of 209.00 (range 206.77-209.00), VWAP 208.16; vetoed: 5 positions open, max 5
- 10:25 PLTR risk_block: ORB break of 186.71 (range 181.68-186.71), VWAP 184.76; vetoed: 5 positions open, max 5
- 10:29 TSLA risk_taken: learning mode, trading anyway: gap +1.21% vs prior close 399.8 exceeds the 0.75% gap rule; research says skip TSLA: premarket gap +1.53% is past the 0.75% gap rule, so the bot will skip it
- 14:01  halted: 3 losing trades today

### Since paper trading began
34 trades, P&L $-0.67, win rate 32%, profit factor 0.94, average -0.04R, max drawdown $7.58 (2.53%), longest losing streak 14.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| core | 9 | $-1.83 | 33% | -0.12R |
| explore | 22 | $-4.34 | 27% | -0.14R |
| in_play | 3 | $5.50 | 67% | +0.94R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 22 trades, P&L $-2.13, win rate 23%, average -0.28R. Other trades average +0.41R.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | yes | 34 |
| Profit factor at least 1.2 | no | 0.94 |
| Positive average R | no | -0.04R |
| Max drawdown under 6% of capital | yes | 2.53% |
| No risk rule breaches | no | 2 |

**Verdict:** stay on paper

