# Smart-money backtest

Generated 2026-10-24 19:08. Entry: open of the first session after the trade became public. Exit: close after the hold. Excess = return minus SPY over the same days. Win = return > 0. Only stocks at $5+ with $5M+ average daily dollar volume. A filter **passes** when it has 30+ trades, both halves (by date) have profit factor > 1 and positive excess, excess stays positive with the best and worst 5% of trades trimmed, and average excess is also positive at the 5- and 60-session holds.

## Insider (529 scored of 2948 disclosures, hold 20 sessions, entries 2024-02-01 to 2026-09-28)

| Filter | Trades | Win | Beat SPY | Avg | Median | Avg excess | Trimmed excess | PF | 1st half excess | 2nd half excess | Passes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all $1M+ buys | 529 | 54% | 48% | +1.8% | +0.7% | +1.2% | +0.6% | 1.53 | +2.2% | +0.2% | no |
| officer (CEO/CFO/COO/Chair/Pres) | 179 | 56% | 47% | +0.9% | +0.7% | +0.4% | +0.3% | 1.28 | +1.0% | -0.3% | no |
| director | 208 | 56% | 52% | +3.9% | +1.4% | +3.0% | +1.9% | 2.22 | +4.2% | +1.7% | **yes** |
| 10% owner | 116 | 46% | 40% | -0.8% | -0.9% | -0.7% | -0.6% | 0.82 | -0.4% | -1.0% | no |
| $5M+ | 203 | 54% | 44% | +2.1% | +0.9% | +1.6% | +0.5% | 1.62 | +2.7% | +0.4% | **yes** |
| cluster (2+ insiders in 7d) | 101 | 57% | 47% | +0.9% | +0.7% | +0.5% | +0.1% | 1.24 | -0.4% | +1.4% | no |
| officer + cluster | 41 | 56% | 39% | -0.6% | +0.5% | -1.2% | -1.3% | 0.82 | -1.2% | -1.2% | no |
| top filer (walk-forward) | 17 | 59% | 47% | +2.0% | +1.5% | +3.0% | +3.0% | 1.62 | +2.3% | +3.6% | no |

Same filters held 5 and 60 sessions (avg excess, beat-SPY rate, trades):

| Filter | 5d | 60d |
|---|---|---|
| all $1M+ buys | +0.5%, 52%, 553 | -0.5%, 43%, 462 |
| officer (CEO/CFO/COO/Chair/Pres) | +0.7%, 57%, 183 | -1.1%, 42%, 158 |
| director | +0.4%, 49%, 211 | +0.5%, 43%, 191 |
| 10% owner | +0.2%, 52%, 133 | -0.9%, 44%, 89 |
| $5M+ | +0.4%, 50%, 223 | +0.9%, 48%, 165 |
| cluster (2+ insiders in 7d) | +0.6%, 53%, 101 | +0.8%, 58%, 93 |
| officer + cluster | +0.5%, 49%, 41 | -1.3%, 53%, 36 |
| top filer (walk-forward) | +0.8%, 60%, 40 | +27.9%, 50%, 4 |

Top insider filers by beat-SPY rate (3+ scored buys; in-sample, so a leaderboard, not a forecast):

| Filer | Buys | Win | Beat SPY | Avg excess | $ disclosed | Symbols |
|---|---|---|---|---|---|---|
| Casdin Capital, LLC | 5 | 100% | 100% | +18.9% | $39.9M | WGS |
| Fribourg Paul J | 7 | 100% | 86% | +11.2% | $45.6M | EL, IFF |
| Bbrc International Pte Ltd | 5 | 80% | 80% | +4.3% | $37.8M | VSCO |
| Fernandez Henry A | 7 | 71% | 71% | +2.4% | $30.1M | MSCI |
| Cohen Ryan | 3 | 100% | 67% | +10.0% | $57.5M | GME |
| Holding Frank B Jr | 3 | 67% | 67% | +4.7% | $12.3M | FCNCA |
| Leighton F Thomson | 3 | 67% | 67% | +0.2% | $8.6M | AKAM |
| Barakett Timothy R | 3 | 33% | 67% | -4.8% | $14.1M | KKR |
| Meister Keith A. | 5 | 60% | 60% | +14.4% | $82.6M | WGS |
| Jenisch Jan Philipp | 5 | 60% | 60% | -0.1% | $40.5M | AMRZ |
| Garden Edward P | 7 | 57% | 57% | +4.3% | $137.1M | FBIN, MIDD |
| Berkshire Hathaway Inc | 17 | 71% | 53% | -0.1% | $1,918.7M | LEN, OXY, SIRI, VRSN |
| Perez De La Mesa Manuel J | 4 | 50% | 50% | +1.5% | $5.8M | POOL |
| Greenoaks Capital Partners LLC | 6 | 83% | 50% | +1.0% | $151.9M | CPNG |
| Florance Andrew C | 4 | 50% | 50% | -1.4% | $8.6M | CSGP |

## Congress (2892 scored of 4681 disclosures, hold 20 sessions, entries 2025-12-17 to 2026-09-24)

| Filter | Trades | Win | Beat SPY | Avg | Median | Avg excess | Trimmed excess | PF | 1st half excess | 2nd half excess | Passes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all stock buys | 2892 | 53% | 47% | +1.3% | +0.6% | -0.1% | -0.4% | 1.38 | -0.9% | +0.8% | no |
| $50K+ | 66 | 42% | 44% | -0.2% | -1.0% | -0.6% | -0.8% | 0.95 | -2.7% | +1.5% | no |
| $250K+ | 7 | 43% | 43% | +6.4% | -1.4% | +6.3% | +6.3% | 2.79 | -4.8% | +14.7% | no |
| reported within 10 days | 366 | 45% | 47% | -0.6% | -0.7% | -0.9% | -1.1% | 0.86 | -2.1% | +0.2% | no |
| house | 2440 | 51% | 47% | +0.9% | +0.3% | -0.2% | -0.6% | 1.25 | -1.4% | +0.9% | no |
| senate | 452 | 61% | 49% | +3.6% | +2.7% | +0.7% | +0.4% | 2.47 | +0.4% | +1.0% | no |
| cluster (2+ members in 7d) | 445 | 52% | 48% | +1.7% | +0.4% | +0.3% | -0.3% | 1.46 | -0.6% | +1.1% | no |
| top filer (walk-forward) | 65 | 46% | 35% | +2.5% | -0.8% | -0.8% | -1.5% | 1.92 | -3.3% | +1.6% | no |

Same filters held 5 and 60 sessions (avg excess, beat-SPY rate, trades):

| Filter | 5d | 60d |
|---|---|---|
| all stock buys | +0.5%, 53%, 3110 | -0.8%, 42%, 2514 |
| $50K+ | +0.2%, 54%, 69 | +2.3%, 56%, 61 |
| $250K+ | +0.5%, 43%, 7 | +2.8%, 80%, 5 |
| reported within 10 days | -0.2%, 49%, 374 | -1.8%, 36%, 350 |
| house | +0.2%, 51%, 2656 | -0.6%, 43%, 2078 |
| senate | +2.5%, 66%, 454 | -1.5%, 40%, 436 |
| cluster (2+ members in 7d) | +0.3%, 53%, 468 | +0.9%, 46%, 394 |
| top filer (walk-forward) | +0.4%, 51%, 276 | +4.8%, 58%, 45 |

Top congress filers by beat-SPY rate (3+ scored buys; in-sample, so a leaderboard, not a forecast):

| Filer | Buys | Win | Beat SPY | Avg excess | $ disclosed | Symbols |
|---|---|---|---|---|---|---|
| Gary Peters | 6 | 83% | 83% | +8.5% | $0.1M | KHC, PEP, SJM, SWK, T, VZ |
| John Fetterman | 5 | 80% | 80% | +10.4% | $0.0M | AMZN, ERIE, GOOGL, MSFT, MU |
| Tracey Mann | 5 | 80% | 80% | +5.9% | $0.0M | AAPL, GOOGL, META, MSFT, NVDA |
| Rick Larsen | 9 | 89% | 78% | +4.3% | $0.1M | APH, CARR, CASY, DRI, MCK, META |
| Katie Britt | 12 | 67% | 67% | +0.9% | $0.1M | AAPL, AMZN, EOG, GOOGL, JPM, MSFT |
| Jonathan Jackson | 14 | 43% | 64% | -0.1% | $0.6M | AMZN, BK, BP, C, GEV, HLT |
| Tim Walberg | 12 | 58% | 58% | +0.7% | $0.3M | AAPL, AMZN, BA, BAC, CAT, CVX |
| Nancy Pelosi | 7 | 57% | 57% | +6.4% | $3.6M | AMZN, BE, GOOGL, INTC, NVDA, TEM |
| Michael Rulli | 11 | 55% | 55% | +1.9% | $0.1M | AAPL, GOOGL, KLAC, KO, LLY, META |
| David Taylor | 68 | 49% | 53% | +0.7% | $0.6M | AAPL, AEP, AMGN, AMZN, AVGO, CRM |
| Julia Letlow | 111 | 50% | 52% | +0.9% | $0.9M | AA, AAPL, ABBV, ABT, ACI, ACN |
| Markwayne Mullin | 52 | 46% | 52% | -0.7% | $2.6M | AAPL, ADBE, AMAT, AMKR, AMZN, APG |
| Jared Moskowitz | 27 | 56% | 52% | +2.5% | $0.2M | AMAT, ASML, ATO, AVGO, AXP, CB |
| Scott Franklin | 4 | 50% | 50% | +4.6% | $0.0M | ACN, MCD, NVO, PEP |
| Rick Allen | 10 | 50% | 50% | +1.4% | $0.1M | AMD, AVGO, AXP, FERG, KMI, SPGI |

