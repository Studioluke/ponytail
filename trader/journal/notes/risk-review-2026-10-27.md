## Risk review Tuesday 2026-10-27

**Kill switch:** off
**Account:** ACTIVE, equity $100,006.86, day trades (5d) n/a, PDT flag n/a

### Limits
| Rule | Used | Limit |
|---|---|---|
| Daily loss | $6.08 | -$6.00 |
| Losing trades today | 1 | 3 |
| Weekly loss | $7.23 | -$15.00 |
| Risk per trade | max $1.56 today | $1.50 |
| Open positions | 0 now | 3 |
| Position size | max $100.05 today | $100.00 (33% of capital) |

### Trades today
| Symbol | Qty | Entry | Stop | Risk $ | P&L | R | Exit |
|---|---|---|---|---|---|---|---|
| AVGO | 0.289 | 345.11 | 341.33 | 1.09 | -1.12 | -1.03 | stop |
| SOFI | 6.122 | 16.17 | 15.92 | 1.53 | 3.12 | +2.04 | target |
| UPS | 0.974 | 102.72 | 101.12 | 1.56 | 2.91 | +1.87 | target |
| TSLA | 0.247 | 403.28 | 399.56 | 0.92 | 1.17 | +1.27 | eod |

**Risk actions:**
- 09:46 TSLA risk_taken: learning mode, trading anyway: gap +1.55% vs prior close 391.69 exceeds the 0.75% gap rule; research says skip TSLA: premarket gap +0.88% is past the 0.75% gap rule, so the bot will skip it
- 09:46 AVGO risk_taken: learning mode, trading anyway: gap +3.07% vs prior close 329.275 exceeds the 0.75% gap rule; research says skip AVGO: premarket gap +2.70% is past the 0.75% gap rule, so the bot will skip it
- 09:47 SOFI risk_taken: learning mode, trading anyway: gap +10.51% vs prior close 14.46 exceeds the 0.75% gap rule; research says skip SOFI: premarket gap +9.68% is past the 0.75% gap rule, so the bot will skip it
- 10:03 UPS risk_taken: learning mode, trading anyway: gap +1.11% vs prior close 100.23 exceeds the 0.75% gap rule; research says skip UPS: premarket gap -2.24% is past the 0.75% gap rule, so the bot will skip it
- 10:11 KO risk_block: ORB break of 92.80 (range 91.00-92.80), VWAP 92.37; vetoed: 3 positions open, max 3
- 10:31 AAPL risk_block: ORB break of 345.09 (range 342.82-345.09), VWAP 343.82; vetoed: 3 positions open, max 3
- 10:34 IWM risk_block: ORB break of 278.11 (range 277.58-278.11), VWAP 277.60; vetoed: 3 positions open, max 3
- 10:42 AMZN risk_block: ORB break of 251.27 (range 249.77-251.27), VWAP 249.96; vetoed: 3 positions open, max 3
- 10:44 GOOGL risk_block: ORB break of 319.95 (range 316.96-319.95), VWAP 318.66; vetoed: 3 positions open, max 3
- 11:03 META risk_block: ORB break of 628.00 (range 623.30-628.00), VWAP 624.38; vetoed: 3 positions open, max 3
- 11:04 MSFT risk_block: ORB break of 533.68 (range 530.12-533.68), VWAP 531.12; vetoed: 3 positions open, max 3
- 11:15 AMD risk_block: ORB break of 554.89 (range 539.03-554.89), VWAP 549.75; vetoed: 3 positions open, max 3
- 11:42 DIA risk_block: ORB break of 523.90 (range 522.23-523.90), VWAP 522.91; vetoed: 3 positions open, max 3
- 11:46 NVDA risk_block: ORB break of 218.49 (range 217.43-218.49), VWAP 217.20; vetoed: 3 positions open, max 3

### Since paper trading began
11 trades, P&L $6.91, win rate 64%, profit factor 3.68, average +0.84R, max drawdown $1.84 (0.61%), longest losing streak 3.

| Group | Trades | P&L | Win rate | Avg R |
|---|---|---|---|---|
| core | 3 | $0.39 | 67% | +0.60R |
| explore | 6 | $0.49 | 50% | +0.59R |
| in_play | 2 | $6.03 | 100% | +1.95R |

Learning trades are the forced 11:00 ET trade at half risk on days with no entry.

**Risks taken knowingly (learning mode):** 7 trades, P&L $4.62, win rate 43%, average +0.36R. Other trades average +1.67R.

**Breaches:**
- 2026-10-27 SOFI: entered with $1.53 risk, cap $1.50
- 2026-10-27 UPS: entered with $1.56 risk, cap $1.50

### Live-money gate
| Check | Pass | Value |
|---|---|---|
| At least 30 closed paper trades | no | 11 |
| Profit factor at least 1.2 | yes | 3.68 |
| Positive average R | yes | +0.84R |
| Max drawdown under 6% of capital | yes | 0.61% |
| No risk rule breaches | no | 2 |

**Verdict:** stay on paper

