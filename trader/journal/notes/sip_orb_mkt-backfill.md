# sip_orb_mkt backfill (11-05 to 2026-11-17)

Filter: SPY's last 1-min close at entry >= its 9:30 open and not below the lower noise band. In-sample: the filter was designed by looking at these trades, so this flatters it. Only forward trades count toward its 40.

| Set | All | Filter passes | Filter blocks |
|---|---|---|---|
| live | 17 trades, avg -0.03R, PF 0.96, wins 3 | 10 trades, avg +0.48R, PF 1.59, wins 2 | 7 trades, avg -0.76R, PF 0.22, wins 1 |
| shadow:sip_orb | 15 trades, avg +0.41R, PF 1.57, wins 4 | 9 trades, avg +1.35R, PF 3.61, wins 4 | 6 trades, avg -1.00R, PF 0.00, wins 0 |
| shadow:sip_orb_wide | 14 trades, avg -0.42R, PF 0.49, wins 2 | 8 trades, avg +0.02R, PF 1.04, wins 2 | 6 trades, avg -1.00R, PF 0.00, wins 0 |
| sip_orb live+shadow | 32 trades, avg +0.17R, PF 1.22, wins 7 | 19 trades, avg +0.89R, PF 2.33, wins 6 | 13 trades, avg -0.87R, PF 0.12, wins 1 |

| Kind | Day | Symbol | Entry | R | Filter |
|---|---|---|---|---|---|
| shadow:sip_orb | 2026-11-05 | HD | 09:35 | -1.00 | block |
| shadow:sip_orb | 2026-11-05 | ARM | 09:35 | -1.00 | block |
| shadow:sip_orb | 2026-11-05 | ANET | 09:35 | -1.00 | block |
| live | 2026-11-05 | QCOM | 09:46 | -1.16 | block |
| live | 2026-11-06 | COP | 09:36 | -1.11 | pass |
| live | 2026-11-06 | WMT | 09:48 | -1.04 | pass |
| live | 2026-11-06 | MCD | 09:49 | -0.76 | pass |
| live | 2026-11-09 | ABNB | 09:36 | -0.97 | pass |
| live | 2026-11-09 | LRCX | 09:36 | +4.13 | pass |
| shadow:sip_orb | 2026-11-09 | TGT | 09:36 | +3.94 | pass |
| shadow:sip_orb | 2026-11-09 | AVGO | 09:36 | +3.59 | pass |
| shadow:sip_orb | 2026-11-09 | AMZN | 09:37 | -1.00 | pass |
| live | 2026-11-09 | NVDA | 09:41 | -1.01 | pass |
| live | 2026-11-10 | CAT | 09:37 | -1.08 | pass |
| live | 2026-11-10 | KLAC | 09:47 | -1.02 | block |
| shadow:sip_orb | 2026-11-11 | COST | 09:35 | -1.00 | block |
| shadow:sip_orb | 2026-11-11 | V | 09:39 | +5.59 | pass |
| live | 2026-11-11 | DELL | 10:07 | +1.49 | block |
| live | 2026-11-12 | AVGO | 09:36 | -1.03 | pass |
| live | 2026-11-12 | NVDA | 09:36 | +8.77 | pass |
| shadow:sip_orb_wide | 2026-11-12 | NVDA | 09:36 | +3.62 | pass |
| shadow:sip_orb_wide | 2026-11-12 | AVGO | 09:36 | -1.00 | pass |
| shadow:sip_orb_wide | 2026-11-12 | DELL | 09:36 | +1.91 | pass |
| shadow:sip_orb | 2026-11-12 | DELL | 09:36 | +3.65 | pass |
| shadow:sip_orb_wide | 2026-11-12 | HOOD | 09:36 | -0.35 | pass |
| shadow:sip_orb | 2026-11-12 | HOOD | 09:36 | -0.65 | pass |
| shadow:sip_orb_wide | 2026-11-12 | AMAT | 09:36 | -1.00 | pass |
| shadow:sip_orb | 2026-11-12 | AMAT | 09:36 | -1.00 | pass |
| shadow:sip_orb_wide | 2026-11-12 | SMCI | 09:37 | -1.00 | pass |
| shadow:sip_orb | 2026-11-12 | SMCI | 09:37 | -1.00 | pass |
| shadow:sip_orb | 2026-11-12 | GOOGL | 09:59 | -1.00 | pass |
| shadow:sip_orb_wide | 2026-11-12 | GOOGL | 09:59 | -1.00 | pass |
| shadow:sip_orb | 2026-11-16 | MSTR | 09:37 | -1.00 | block |
| shadow:sip_orb_wide | 2026-11-16 | MSTR | 09:37 | -1.00 | block |
| live | 2026-11-16 | COIN | 09:51 | -1.03 | block |
| shadow:sip_orb_wide | 2026-11-16 | COIN | 09:51 | -1.00 | block |
| live | 2026-11-17 | NKE | 09:36 | -1.51 | block |
| live | 2026-11-17 | LOW | 09:36 | -1.08 | block |
| shadow:sip_orb_wide | 2026-11-17 | LOW | 09:36 | -1.00 | block |
| shadow:sip_orb_wide | 2026-11-17 | NKE | 09:36 | -1.00 | block |
| live | 2026-11-17 | HD | 09:49 | -1.08 | pass |
| shadow:sip_orb_wide | 2026-11-17 | HD | 09:49 | -1.00 | pass |
| live | 2026-11-17 | DIS | 09:52 | -1.03 | block |
| shadow:sip_orb_wide | 2026-11-17 | DIS | 09:52 | -1.00 | block |
| shadow:sip_orb | 2026-11-17 | SCHW | 09:53 | -1.00 | block |
| shadow:sip_orb_wide | 2026-11-17 | SCHW | 09:53 | -1.00 | block |
