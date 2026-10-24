# Swing screener, close of 2026-10-23

Setups from trader/patterns.py, scored on each symbol's own history since 2016. Simulated/paper only; not advice.

## Firing on the latest close

None. The setups buy sharp dips in uptrends, so quiet or rising days fire nothing.

## Within 3% of the STRETCH trigger (watch list)

| Symbol | Close | Trigger (10d avg - 2 ATR) | Distance | Score |
|---|---|---|---|---|
| QQQ | 704.40 | 698.53 | 0.8% | 94.1 |
| SMH | 527.20 | 517.71 | 1.8% | 91.7 |
| SOXX | 478.20 | 469.40 | 1.9% | 89.5 |
| XLK | 183.23 | 179.85 | 1.9% | 90.2 |
| NVDA | 210.96 | 206.66 | 2.1% | 90.5 |
| AMZN | 248.00 | 242.11 | 2.4% | 80.6 |
| MSFT | 524.51 | 510.99 | 2.6% | 90.8 |
| JPM | 331.58 | 322.09 | 2.9% | 39.7 |

## Best swing candidates by history (top 25)

| Rank | Symbol | Score | STRETCH trades / win / PF | RSI2+IBS trades / win / PF | ATR % | Above 200d |
|---|---|---|---|---|---|---|
| 1 | QQQ | 94.1 | 27 / 93% / 58.34 | 32 / 84% / 3.77 | 1.7% | yes |
| 2 | ADBE | 93.6 | 17 / 82% / 8.01 | 22 / 91% / 23.80 | 3.4% | yes |
| 3 | NOW | 92.9 | 14 / 93% / 55.82 | 21 / 81% / 4.00 | 3.9% | yes |
| 4 | SQ | 92.1 | 5 / 100% / inf | 14 / 79% / 9.41 | 4.0% | yes |
| 5 | SMH | 91.7 | 29 / 79% / 11.37 | 31 / 87% / 4.61 | 3.5% | yes |
| 6 | MSFT | 90.8 | 14 / 86% / 7.14 | 24 / 79% / 13.48 | 2.1% | yes |
| 7 | XLC | 90.7 | 13 / 85% / 14.41 | 14 / 79% / 3.37 | 1.6% | no |
| 8 | NVDA | 90.5 | 18 / 78% / 5.41 | 19 / 84% / 9.16 | 2.8% | yes |
| 9 | PG | 90.3 | 11 / 73% / 2.66 | 25 / 84% / 10.26 | 2.0% | yes |
| 10 | V | 90.3 | 14 / 86% / 8.97 | 17 / 76% / 6.64 | 1.8% | yes |
| 11 | XLK | 90.2 | 25 / 84% / 9.79 | 31 / 77% / 2.41 | 2.3% | yes |
| 12 | META | 89.7 | 15 / 80% / 26.76 | 19 / 79% / 16.49 | 3.9% | yes |
| 13 | AMD | 89.5 | 11 / 73% / 2.50 | 27 / 81% / 8.49 | 5.7% | yes |
| 14 | PANW | 89.5 | 14 / 86% / 18.22 | 29 / 76% / 2.75 | 5.3% | yes |
| 15 | SOXX | 89.5 | 29 / 83% / 15.48 | 28 / 75% / 2.36 | 4.1% | yes |
| 16 | DIS | 88.9 | 6 / 83% / 6.00 | 18 / 78% / 4.57 | 1.7% | yes |
| 17 | MA | 88.9 | 11 / 100% / inf | 25 / 68% / 1.64 | 1.7% | yes |
| 18 | CRM | 88.7 | 11 / 73% / 3.15 | 20 / 80% / 6.06 | 3.5% | yes |
| 19 | HON | 88.2 | 13 / 77% / 11.81 | 21 / 76% / 3.20 | 2.5% | no |
| 20 | XBI | 87.5 | 7 / 86% / 231.72 | 25 / 72% / 1.79 | 3.1% | yes |
| 21 | UBER | 86.7 | 3 / 100% / inf | 12 / 67% / 1.42 | 2.7% | no |
| 22 | GOOGL | 86.6 | 17 / 65% / 4.85 | 24 / 79% / 9.04 | 2.6% | no |
| 23 | ABNB | 86.4 | 3 / 100% / inf | 8 / 62% / 2.12 | 2.6% | yes |
| 24 | CRWD | 83.7 | 7 / 86% / 3.05 | 14 / 64% / 5.67 | 5.3% | yes |
| 25 | KRE | 83.3 | 9 / 89% / 154.95 | 24 / 58% / 1.55 | 1.8% | yes |

Score = 50 x win rate + 10 x profit factor (capped at 5), pooled over both setups; 0 when the symbol fails the price, liquidity or volatility filter. The universe is today's large caps, so history flatters it (survivorship).
