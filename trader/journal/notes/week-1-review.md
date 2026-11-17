## Week 1 review (Wed 2026-10-28)

Paper account, $300 of capital, 15-minute opening-range breakout with a VWAP filter, 2R target, flat by 15:45 ET. There were four sessions, Thu 10-22 to Tue 10-27. The 10-21 session was setup only.

### Results
| Day | Trades | Wins | P&L | Notes |
|---|---|---|---|---|
| Thu 10-22 | 1 | 1 | +$0.43 | AAPL, closed at the bell (+0.38R) |
| Fri 10-23 | 1 | 0 | -$0.74 | GOOGL stop (risk taken, gap). A sizing bug put all $300 in one trade |
| Mon 10-26 | 5 | 3 | +$1.15 | COST, IWM and QQQ hit 2R; AMZN stopped; TSLA flat at the bell |
| Tue 10-27 | 4 | 3 | +$6.08 | SOFI and UPS (in-play list) hit target; TSLA +1.27R at the bell; AVGO stopped |
| **Total** | **11** | **7 (64%)** | **+$6.91 (+2.3%)** | Profit factor 3.68, average +0.84R, max drawdown $1.84 (0.6%) |

By group:
- **Core** (SPY, QQQ, AAPL, MSFT, GOOGL): 3 trades, +$0.39.
- **Explore**: 6 trades, +$0.49.
- **In play** (research list, from 10-27): 2 trades, +$6.03.

**Risks taken knowingly** (learning mode overrode the gap rule or a research "skip"): 7 trades, 3 wins, +$4.62, average +0.36R. The trades with no override: 4 trades, all wins, average +1.67R. So far the rules we overrode were worth keeping. The 10-27 gap winners were earnings gaps (SOFI, UPS). The gap losers (GOOGL, AMZN, AVGO) had no fresh catalyst.

### Live vs backtest
- **Backtest, Jul to Oct:** 86 trades, 36% win rate, -0.6%. That is no edge. The deeper study in PR #8 found ORB is about breakeven after costs.
- **Live this week:** a 64% win rate and +2.3%. That is far better than the backtest, and the likeliest reason is luck plus a market that rose most days (QQQ +1.45% on 10-27).
- **The honest read:** 11 trades can't separate skill from noise. The backtest has 8 times the sample, and it says there is no edge yet.

### Rule breaks and incidents
1. **10-23 sizing bug.** One position used the whole $300, so 11 later signals sized to 0. Fixed by capping each position at a third of capital.
2. **10-27 small over-risk.** SOFI risked $1.53 and UPS $1.56 against the $1.50 cap. Both filled above the signal price. Fix: size with a slippage buffer. This tightens a rule, so no approval is needed, and I'll make it.
3. **10-27 crash on a target exit.** The close raced the stop cancel. SOFI was briefly without a stop and I closed it at target by hand. Fixed and tested.
4. **A scheduled task from another project ("Trader pass 9:33 ET")** keeps committing trader state mid-session. It placed no orders. Our state is protected by the merge=ours rule. It should still be paused.
5. **Every day had a trade**, as Luke asked. The 11:00 learning-trade fallback was never needed.

### Lessons
- **Capacity is the main limit now.** All 3 slots were full by about 10:00 on 10-26 and 10-27. On 10-27, 12 valid signals went untraded, including GOOGL, AMD and AMZN, which closed strong.
- **Earnings or news gaps look tradeable; plain gaps don't.** The gap rule could be split by catalyst. This needs more data.
- **The research brief earns its place.** Its in-play list produced the two best trades.

### Readiness verdict: stay on paper
- The risk manager's live-money gate needs 30+ closed trades, profit factor 1.2 or better, positive average R, drawdown under 6% and no breaches.
- This week passes profit factor, average R and drawdown, and fails trade count (11) and breaches (2 small ones).
- More important, the 4-month backtest shows no edge, and a 4-day sample can't overturn that.
- **Recommendation:** keep paper trading at least 2 more weeks to reach 30+ trades. Re-check on Wed 2026-11-11.

### Decision for Luke
More positions at once (lifting the 3-slot limit), so more signals get traded. Same $300 total and the same $1.50 risk per trade, but more trades open at the same moment.
- **Option A (recommended):** 5 slots of $60 each. This gets to 30 trades faster and tests more signals. If all 5 open trades hit their stops together, the loss is about $7.50 (2.5%), a little past the -2% ($6) daily breaker. The breaker only blocks new entries, not trades already open.
- **Option B:** keep 3 slots of $100. Slower to learn, less exposure at once.
