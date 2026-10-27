# NVDA year-end view + AI cybersecurity picks (written 2026-10-24)

Estimate, not advice. Prices are Alpaca IEX closes for 2026-10-23. Ranges are for the 2026-12-31 close.

## Part 1: NVDA year-end 2026

### Where it stands
- Last close **$211.02**. 52-week range ~$165 to ~$239 (IEX closes; other feeds show a $243 high). Up ~16% over 12 months, down 6% in a month, ~12% off the high.
- Technicals: below the 20-day ($226) and 50-day ($222), above the 200-day ($203). RSI(14) ~22, deeply oversold. 60-day vol ~35%.
- The whole chip group is washed out: SOXX -15% in a month (RSI 14), QQQ RSI 24. Last week's drop came from Lam Research supply warnings and Jensen Huang's comments on neocloud funding (NVDA -4.4% on 10-22). Traders cite ~$207 as a demand zone.
- Street: consensus target ~$315-329 (49 of 62 Buy); Morgan Stanley $300. Even cautious models (24/7 Wall St.) sit at ~$264.

### Catalysts before year-end
- 2026-10-28 FOMC; 2026-11-03 AMD earnings (read-through).
- **2026-11-18 NVDA Q3 FY27 earnings** (after close). The Q4 guide, Rubin ramp, and China matter most.
- Security tie-in: Nvidia's Open Agent Safety Platform (OpenShell software + Sentry on BlueField-4 chips) gives it a new "AI security" angle, but it is small next to data-centre GPUs. It does not move NVDA by itself.

### Scenarios for 2026-12-31
| Case | Prob. | Range | What gets it there |
|---|---|---|---|
| Bear | ~25% | $165-195 | AI-capex fear spreads (neoclouds struggle to fund), soft Q4 guide, chip selloff continues; retest of the 52-week low area |
| Base | ~50% | $205-245 (mid ~$225) | Beat-and-raise on 11-18 as usual, oversold bounce back to the 50-day; stays under the high |
| Bull | ~25% | $250-285 | Strong Rubin/2027 data, capex worries fade, semis rip back; new all-time high |

Probability-weighted ~**$224** (about +6%). A pure volatility model (35% vol, ~47 trading days) gives a one-sigma band of about $180-243. NVDA usually moves ±6-8% on earnings.

## Part 2: Nvidia's cybersecurity partners (verified)

Nvidia's security push in 2026 is about **guarding AI agents**: OpenShell (a secure runtime that limits what agents can do, on the CPU) and Sentry (enforcement in the BlueField-4 network chip that quarantines a rogue agent in milliseconds). On 2026-10-21 Nvidia named the security vendors building on it: **1Password, Check Point, CrowdStrike, Cisco, F5, Fortinet, Microsoft, Okta, Palo Alto Networks, TrendAI, Zscaler**.

Depth of each tie (deepest first):
- **CrowdStrike**: deepest. 10-20/21 "software to silicon" deal: Falcon AIDR on OpenShell, planned Sentry enforcement on BlueField-4, and its SafeMind agent runs on Nvidia Nemotron models.
- **Palo Alto Networks**: Prisma AIRS (AI gateway + AI runtime security) and agent-identity security on Nvidia's reference design. Now also owns CyberArk (CYBR data stops in Feb 2026).
- **Zscaler, Fortinet, Check Point, Okta, Cisco**: named OpenShell integrators. Zscaler already has ~$70M ARR from "security for AI" and an IBM/Red Hat pact.
- Not on the list: Cloudflare, SentinelOne (both still AI-security players, just not named Nvidia partners).
- Morpheus (Nvidia's older AI threat-detection framework) did not show up in 2026 news; the action has moved to OpenShell/Sentry.

### Why the theme has legs
AI agents with access to company systems need identity, guardrails and runtime monitoring, which is new spend on top of normal security budgets. Sector momentum is real: Morgan Stanley and Evercore surveys (Oct) flag stronger security spending; CIBR/HACK/BUG ETFs are at or near highs (CIBR +38% over 12 months vs QQQ +16%). The risk is that a lot of this is priced in: several names are up 70-140% in a year.

## Part 3: Snapshot (Alpaca, 10-23 close)
| Ticker | Price | 1m | 12m | Off high | vs 50-day | RSI | Vol | Next earnings |
|---|---|---|---|---|---|---|---|---|
| NVDA | 211.02 | -6% | +16% | -12% | below ($222) | 22 | 35% | 11-18 |
| CRWD | 257.55 | -1% | +97% | -8% | above ($235) | 44 | 71% | ~early Dec (est.) |
| PANW | 380.61 | -2% | +77% | -9% | above ($370) | 43 | 62% | ~11-18 (est.) |
| FTNT | 179.98 | +1% | +112% | -8% | above ($171) | 46 | 46% | **10-28** after close (confirmed) |
| ZS | 255.31 | +19% | -20% | -24% | well above ($197) | 74 | 66% | ~late Nov (est.) |
| CHKP | 159.09 | +17% | -18% | -22% | well above ($135) | 87 | 36% | **11-02** pre-market (confirmed) |
| OKTA | 213.01 | +3% | +141% | -8% | above ($185) | 47 | 77% | ~early Dec (est.) |
| CSCO | 106.49 | 0% | +54% | -18% | below ($110) | 39 | 34% | ~mid Nov (est.) |
| NET | 325.80 | -9% | +50% | -10% | above ($319) | 39 | 63% | ~early Nov (est.) |
| S | 24.00 | 0% | +38% | -9% | above ($22.6) | 43 | 64% | ~12-04 (est.) |
| CIBR (ETF) | 106.15 | +3% | +38% | -4% | above ($100) | 50 | 35% | n/a |

## Part 4: Rankings

### To invest (hold 6-18 months)
1. **CrowdStrike (CRWD)**: the closest Nvidia partner, platform leader, fastest-growing big name. Pricey and very volatile (71% vol), so buy in pieces, not all at once.
2. **Palo Alto (PANW)**: the "one platform" consolidator, with AI runtime security plus identity (CyberArk). Steadier than CRWD.
3. **Nvidia (NVDA)**: the picks-and-shovels; the security work rides on its chips. Cheapest entry in months after the selloff, but the most macro and capex risk.
4. **Fortinet (FTNT)**: profitable, cheaper on earnings, hardware plus AI. A good balance name; 10-28 earnings first.
5. **Zscaler (ZS)**: clearest "security for AI" revenue line, but it just ran +19% in a month; wait for a pullback.
- Simple option: **CIBR** ETF gets the whole theme in one ticket with half the volatility.
- Avoid for now: CSCO (below its 50-day, slow grower), CHKP (stretched, slower grower).

### To swing trade (days to weeks; paper first)
Rule of thumb: buy uptrends on pullbacks near the 20/50-day, not names at RSI 75+, and never hold through earnings unless that is the plan.
1. **PANW**: in an uptrend, pulled back to the 20/50-day. Entry ~$370-382, stop ~$355 (under the 50-day), target ~$415-420 (prior high). ~2.2:1. Exit before ~11-18 earnings.
2. **CRWD**: same set-up. Entry ~$245-258, stop ~$232, target ~$278. ~1.7-2:1. Fresh Nvidia news on 10-21 is support.
3. **NVDA**: oversold bounce. Entry ~$205-212 (the cited demand zone), stop ~$197, target ~$222-226 (50/20-day). ~1.5-2:1. Only with a market that stops falling (watch SOXX); exit before 11-18 unless trading the earnings.
4. **FTNT**: earnings play. Either wait for 10-28 and buy a gap-up that holds the first hour, or buy a dip to ~$171-174 (50-day) after the report with a stop ~$164.
5. **OKTA**: identity for AI agents; uptrend, RSI 47. Entry on a dip to ~$200-205, stop ~$190, target ~$230.
- Do not chase: **CHKP** (RSI 87, earnings 11-02) and **ZS** (RSI 74). QLYS, TENB, RBRK are also at fresh highs.

## Risks
- AI-capex scare: if hyperscalers or neoclouds cut spending, NVDA drops and AI-security names fall with it as "AI trades".
- Valuation: CRWD, ZS, NET, OKTA trade at very high multiples; one soft guide can mean -15-25% in a day (e.g. S and CRWD fell 7-8% on 8-28).
- Partnerships are integrations, not big contracts. Nvidia names 11 vendors, so being a partner is not a moat on its own.
- Sentry has no confirmed ship date yet.
- Macro: FOMC 10-28; semis are in a sharp selloff right now.
- Swing trades here are multi-day, which is outside the paper bot's intraday flat-by-close rules. Treat them as a separate manual/paper sleeve.

## For the day trader
Earnings dates added to `trader/journal/research/events.csv` (FTNT 10-28, CHKP 11-02, NVDA 11-18, plus estimates), so the research agent marks those days "skip" if any of these get onto the watchlist.

Sources: Alpaca market data; [NVIDIA OpenShell reference architecture, 10-21](https://www.manilatimes.net/2026/10/21/tmt-newswire/globenewswire/nvidia-launches-openshell-reference-architecture-for-safe-ai-agents/2450556/amp); [CrowdStrike + NVIDIA press release](https://www.crowdstrike.com/en-us/press-releases/crowdstrike-nvidia-expand-ai-agent-security-software-silicon/); [NVIDIA blog on CrowdStrike](https://blogs.nvidia.com/blog/nvidia-crowdstrike-fal-con-2026/); [Palo Alto blog](https://www.paloaltonetworks.com/blog/2026/09/securing-ai-agents-at-scale-with-nvidia/); [CNBC on the Open Agent Safety Platform](https://www.cnbc.com/2026/09/28/nvidia-releases.html); [StorageReview on Sentry/BlueField-4](https://www.storagereview.com/news/nvidia-open-agent-safety-platform-openshell-sentry-bluefield-4); [TradingKey NVDA 10-23](https://www.tradingkey.com/analysis/stocks/us-stocks/262235232-nvidia-stock-forecast-huang-neocloud-funding-chip-selloff-206-support-october-23-2026-tradingkey); [24/7 Wall St. NVDA 10-20](https://247wallst.com/investing/2026/10/20/nvidia-keeps-falling-and-wall-street-wont-move-its-target-is-it-time-to-buy/); [StockAnalysis NVDA](https://stockanalysis.com/stocks/nvda/); [24/7 Wall St. Zscaler 10-09](https://247wallst.com/investing/2026/10/09/zscaler-jumps-6-on-reaffirmed-revenue-outlook-and-ibm-security-pact-palo-alto-and-crowdstrike-gain-4/); [Investing.com on Check Point](https://www.investing.com/news/stock-market-news/why-is-check-point-software-stock-rallying-today-93CH-4970130); [Fortinet Q3 date](https://capital.com/en-gb/news/fortinet-to-announce-third-quarter-2026-financial-results); [Cybersecurity earnings calendar](https://www.smartcalendars.ai/en/feeds/cybersecurity-earnings-calendar).
