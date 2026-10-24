# Trading playbook: what actually works (2026-10-24)

Luke asked for deep research on day and swing trading (candlesticks, wicks, chart patterns, indicators, volume) and a bot that wins 75% of the time. Every rule below was coded and backtested on our own Alpaca data, not taken from articles. Paper and simulation only; not financial advice.

## The answer in five lines

1. **A 75% win rate is reachable, but only with one kind of trade:** buy a sharp dip in a stock that is in an uptrend, sell into the first bounce, hold 3-5 days. Our best version (STRETCH) won **74% of 570 trades** on 36 stocks/ETFs since 2016, **72% after 2022**, and **77% on index ETFs alone**.
2. **High win rate is not the same as making money.** STRETCH makes about +1.2% per trade. With $200 a trade and a $1,000 account it would have turned $1,000 into about $1,960 over ten years (no year lost money, worst drawdown $89). Real edge, small dollars.
3. **Candlesticks alone are weak.** Hammers, engulfing candles, harami and doji add a little edge only in an uptrend after a pullback, and win 52-60%. The morning star lost money. The academic studies agree.
4. **Every popular day-trading pattern we tested is break-even or worse after costs** on 5-minute bars, 2024-2026, 16 liquid symbols, including the opening-range breakout our bot runs today (6,502 trades, 42% win, profit factor 0.99). Nothing intraday came close to 75%.
5. **Calls multiply the result and the risk.** On the same STRETCH signals, calls turned +1.2% per trade into +10-26% on paper under tight-spread assumptions, but win rate fell to 58-66%, single trades lost 95-100%, and at realistic retail spreads (8%) most of the edge disappeared.

Tripling $1,000 in two weeks is still not something any tested rule does. The honest path is: run STRETCH on paper, prove it live for a few weeks, then size it.

## What the research says (sources at the bottom)

- **Most day traders lose.** 97% of Brazilian futures day traders who kept at it 300+ days lost money (Chague et al.). In Taiwan, most heavy day traders lost after costs (Barber, Lee, Liu, Odean).
- **Candlesticks:** no reliable value on large US stocks (Marshall, Young and Rose 2006); some one-day patterns may help on Dow stocks since 1992 (Lu and Shiu 2016). Bulkowski's own stats: bullish engulfing reverses ~63% of the time, morning star 78% "reversal" but that is not the same as a profitable trade.
- **Chart patterns:** Lo, Mamaysky and Wang (2000) found patterns like head-and-shoulders and double bottoms carry some information, but "optimal for detecting anomalies need not be optimal for trading profits". Bulkowski: double bottoms fail to confirm 44% of the time in bull markets.
- **Short-term mean reversion** (Connors RSI(2), IBS) is the one family the public evidence and our own tests both support. Published win rates of 65-75% are typical, with no stop loss.
- **Opening-range breakout:** Zarattini, Barbon and Aziz (2024) report big returns for a 5-minute ORB, but only on "stocks in play" (unusual volume, news), long and short, scanning thousands of stocks. Our long-only version on 16 large caps is weak.
- **VWAP trend** (Zarattini and Aziz 2023) reports strong QQQ results long and short; independent replications are lower, and our long-only 5-minute version lost.
- **Math to remember:** break-even win rate = 1 / (1 + reward:risk). At 2:1 you only need 34%; at 0.5:1 you need 67%. A 75% strategy that risks $3 to make $1 loses money.

## Candle anatomy (the "whiskers")

- **Body**: open to close. Green when close > open.
- **Wicks / whiskers / shadows**: the thin lines above and below the body, the high and the low.
- **Long lower wick** (hammer): sellers pushed price down, buyers pushed it back. Means something only after a decline and in an uptrend.
- **Long upper wick** (shooting star): buyers failed at the highs.
- **IBS** (internal bar strength) = (close - low) / (high - low). Near 0 means the close is at the day's low; that, not the candle's name, is what our best setups use.

## The swing playbook (daily bars)

All rules are in `trader/patterns.py`. Results: 36 large-cap stocks and ETFs, 2016-01 to 2026-10, 0.05% cost each way, buy at the signal day's close.

| Setup | Rule | Trades | Win | Avg trade | Profit factor | 2016-21 / 2022-26 win |
|---|---|---|---|---|---|---|
| **STRETCH (core)** | Above 200-day avg; close more than 2 ATR under the 10-day avg; close in the bottom quarter of the day's range (IBS < 0.25). Sell on the first close above the 5-day avg, or after 10 days | 570 | **74%** | +1.18% | 2.68 | 75% / 72% |
| STRETCH, ETFs only | Same, on SPY, QQQ, IWM, DIA, XLF, XLE, XLK, SMH | 173 | **77%** | +0.99% | 2.98 | 82% / 72% |
| **RSI2 + IBS (core)** | Above 200-day avg; RSI(2) < 5; IBS < 0.2. Sell on the first close above the prior day's high, or after 10 days | 891 | 71% | +0.96% | 2.30 | 73% / 70% |
| 3 down days | Above 200-day avg; three lower closes in a row. Sell above the 5-day avg | 2,962 | 70% | +0.53% | 1.66 | 70% / 70% |
| Three white soldiers | Three strong green candles, each opening inside the last body. Hold 10 days | 92 | 66% | +1.24% | 1.83 | 73% / 63% |
| Volume breakout | Above 200-day avg; close at a 20-day high on 1.5x average volume; 2 ATR stop; sell on a close under the 10-day avg | 973 | 45% | +1.14% | 1.71 | 46% / 43% |
| Golden cross | 50-day avg crosses over the 200-day; sell 3% under the 50-day | 218 | 50% | +6.96% | 3.67 | 50% / 50% |

Dropped or weak (no edge over just being long in an uptrend, or failed after 2022): morning star (lost money), bullish engulfing after a pullback, RSI(14) crossing 30, plain 20-day and 52-week-high breakouts, pullback to the 20-day avg, inside-day breakouts, hammers and engulfing candles anywhere. Full table: `pattern-backtest-daily.md`.

**How to read the two kinds of setup.** Mean reversion (STRETCH, RSI2+IBS) wins often and makes a little each time. Trend and breakout (volume breakout, golden cross) win less than half the time but the winners are big. A sound book runs both; chasing only win rate means only the first kind.

**Stops.** The high-win setups have no stop in the test, which is why they win so often; the worst single trade was -24%. A 2.5 ATR stop on RSI2 kept it profitable (profit factor 1.32, still 69% wins). In the paper swing tracker the screener uses a 2.5 ATR stop and Luke's $50 max loss caps the damage.

## Best stocks to swing trade (screener)

`python -m trader.screener` scores ~100 liquid US stocks and ETFs by how the two core setups did on each one since 2016, and lists what fires today. As of the 10-23 close: nothing fires (the setups need a sharp dip), and the closest to a trigger are QQQ (0.8% away), SMH, SOXX, XLK, NVDA, AMZN, MSFT. Top names by history: QQQ, ADBE, NOW, SMH, MSFT, XLC, NVDA, PG, V, XLK, META, AMD, PANW, SOXX. Per-symbol samples are small (5-30 trades each), so use the score to choose where to look, not as a promise. Current list: `trader/journal/swing/screener.md`. `--plan` adds any firing setup to the paper swing tracker's plan.

## Day-trading results (5-minute bars, 2024-01 to 2026-10)

Long only, flat by 15:55, 0.02% cost each way. Rules in `trader/intraday_lab.py`.

| Rule | Trades | Win | Avg R | Profit factor | 2024 / 2025-26 PF |
|---|---|---|---|---|---|
| 5-min ORB, stocks in play (first bar 2x usual volume) | 307 | 38% | +0.04 | 1.22 | 1.59 / 1.05 |
| 5-min ORB, first bar green, stop its low | 5,211 | 33% | -0.02 | 1.10 | 1.07 / 1.11 |
| Gap-down fill in uptrend | 549 | 50% | +0.04 | 1.06 | 0.66 / 1.28 |
| Hammer tagging VWAP, 2R | 802 | 38% | -0.03 | 0.99 | 1.13 / 0.92 |
| **15-min ORB + VWAP, 2R (current bot)** | 6,502 | 42% | -0.04 | 0.99 | 1.00 / 0.98 |
| Bull flag after 1% morning pole, 2R | 482 | 43% | -0.04 | 0.86 | 0.91 / 0.84 |
| VWAP trend | 38,665 | 21% | -0.13 | 0.82 | 0.78 / 0.84 |
| 5-min RSI2 + IBS flush | 8,266 | 57% | -0.08 | 0.77 | 0.74 / 0.79 |

Takeaway: on liquid large caps, intraday patterns are mostly noise after costs. The only hint of edge is the 5-minute ORB on stocks with unusual opening volume, which matches the published research but needs a wider scan (hundreds of names with news) to get enough trades. Recommendation: keep the day bot on paper for learning, but put the real effort into the swing setups.

## Options (calls)

`python -m trader.options_lab` replays every STRETCH trade as a call, priced with Black-Scholes (no long real options history here; Alpaca's starts in 2024).

| Instrument, $200 a trade | Win | Avg return | Profit factor | Worst | Avg $ per trade |
|---|---|---|---|---|---|
| Shares | 74% | +1.2% | 2.68 | -24% | +$2.37 |
| Call, 35 days, 0.70 delta | 66% / 51% | +9.6% / -2.7% | 2.05 / 0.77 | -95% | +$19 / -$5 |
| Call, 35 days, at the money | 66% / 54% | +15.7% / +1.8% | 2.39 / 1.14 | -99% | +$31 / +$4 |
| Call, weekly, at the money | 58% / 52% | +26.3% / +4.3% | 1.88 / 1.13 | -100% | +$53 / +$9 |

First figure: 3% spread, implied vol 1.15x realised (liquid names, good fills). Second: 8% spread, 1.3x (closer to what retail pays; Bryzgalova et al. found an average 12.6% spread on retail options). Calls only make sense on the most liquid names with tight spreads, small size, and with the understanding that each one can go to zero. Next step: paper-trade STRETCH signals as 30-45 day calls on Alpaca paper alongside the shares to measure real fills.

## Caveats

- **Survivorship:** the universe is today's big winners (NVDA, AVGO, PANW...). Results on stocks that later collapsed would be worse.
- **Many rules tried:** about 35 daily and 8 intraday variants. STRETCH and RSI2+IBS were chosen from published research before testing and held in both periods, but expect live results a bit below the backtest.
- **Fills:** daily setups assume buying at the close (a market-on-close order a few minutes before 4pm). Intraday assumes no partial fills.
- **Bull market:** 2016-2026 was mostly up. Buy-the-dip setups suffer in a long bear market; the 200-day filter keeps them out of the worst of it.

## Next steps

1. Run `python -m trader.screener --plan` after each close so firing STRETCH / RSI2+IBS setups enter the paper swing tracker automatically.
2. Paper-trade the same signals as calls on Alpaca paper to measure real option fills.
3. Day bot: test the 5-minute ORB on a stocks-in-play scan (unusual volume + news) before changing the live paper strategy.

## Sources

- Chague, De-Losso, Giovannetti, "Day Trading for a Living?" (SSRN 3423101): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101
- Barber, Lee, Liu, Odean, Taiwan day traders: https://faculty.haas.berkeley.edu/odean/papers/day%20traders/Day%20Trading%20Skill%20110523.pdf
- Marshall, Young, Rose, "Market Timing with Candlestick Technical Analysis": https://mro.massey.ac.nz/handle/10179/1604
- Lu and Shiu (2016) and other candlestick studies: https://journals.sagepub.com/doi/10.1177/2158244017736799
- Lo, Mamaysky, Wang, "Foundations of Technical Analysis" (2000): https://www.nber.org/papers/w7613
- Bulkowski candlestick and chart pattern statistics: https://thepatternsite.com/MorningStar.html , https://thepatternsite.com/Confirmation.html
- Zarattini, Barbon, Aziz, 5-minute ORB on stocks in play: https://www.cxoadvisory.com/individual-investing/intraday-trading-of-overactive-stocks-via-opening-range-breakout/
- Zarattini and Aziz, VWAP trend: https://concretumgroup.com/volume-weighted-average-price-vwap-the-holy-grail-for-day-trading-systems/
- Connors RSI(2) on the S&P 500: https://backtrex.com/en/backtests/connors-rsi-2-sp-500
- IBS mean reversion: https://wealth-lab.com/blog/build-a-profitable-mean-reversion-strategy-using-the-ibs-indicator
- Bryzgalova, Pavlova, Sikorskaya, "Retail Trading in Options" (JF 2023): https://lbsresearch.london.edu/id/eprint/2827
- Break-even win rate and expectancy: https://nexusfi.com/articles/trading/Expectancy
