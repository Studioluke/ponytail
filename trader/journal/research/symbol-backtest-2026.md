# ORB backtest by symbol, 2026 (research input)

Same rules as the live bot (15-min ORB above VWAP, stop at range midpoint, 2R target, flat 3:45, $300 capital, 0.5% risk), one symbol at a time. IEX 1-min bars, 1 cent slippage, no fees: optimistic. H1 = Jan-Jun, H2 = Jul to Oct 21. PF = profit factor (above 1 made money).

```
AAPL  H1 n= 59 win=39% pnl= +5.05 pf=1.12 | H2 n= 33 win=58% pnl=+19.42 pf=2.05
NFLX  H1 n= 43 win=35% pnl= -5.24 pf=0.86 | H2 n= 26 win=54% pnl=+15.44 pf=1.99
GOOGL H1 n= 48 win=46% pnl=+10.32 pf=1.35 | H2 n= 28 win=46% pnl= +5.12 pf=1.25
XOM   H1 n= 46 win=50% pnl=+21.74 pf=1.98 | H2 n= 25 win=32% pnl= -8.07 pf=0.61
MSFT  H1 n= 41 win=46% pnl= +8.85 pf=1.31 | H2 n= 29 win=52% pnl= +5.27 pf=1.28
SPY   H1 n= 85 win=38% pnl= +1.12 pf=1.04 | H2 n= 49 win=45% pnl= +4.72 pf=1.44
META  H1 n= 42 win=45% pnl= +8.42 pf=1.31 | H2 n= 22 win=45% pnl= -0.94 pf=0.94
IWM   H1 n= 59 win=41% pnl= +3.27 pf=1.10 | H2 n= 41 win=34% pnl= +1.55 pf=1.09
MU    H1 n= 15 win=33% pnl= -0.88 pf=0.93 | H2 n=  8 win=38% pnl= +1.53 pf=1.22
NVDA  H1 n= 38 win=37% pnl= +3.56 pf=1.11 | H2 n= 20 win=30% pnl= -0.66 pf=0.96
TSLA  H1 n= 30 win=37% pnl= -3.14 pf=0.89 | H2 n= 22 win=45% pnl= +2.34 pf=1.14
UNH   H1 n= 53 win=49% pnl= +7.72 pf=1.21 | H2 n= 31 win=32% pnl= -5.63 pf=0.78
DIA   H1 n= 65 win=45% pnl= +8.42 pf=1.35 | H2 n= 43 win=26% pnl= -8.10 pf=0.57
QQQ   H1 n= 60 win=42% pnl= +5.43 pf=1.19 | H2 n= 32 win=31% pnl= -4.47 pf=0.71
COST  H1 n= 63 win=38% pnl= -6.24 pf=0.87 | H2 n= 40 win=40% pnl= -0.88 pf=0.96
ORCL  H1 n= 25 win=24% pnl=-15.98 pf=0.38 | H2 n= 11 win=36% pnl= +3.34 pf=1.45
AMZN  H1 n= 46 win=46% pnl= +3.60 pf=1.10 | H2 n= 25 win=32% pnl= -8.51 pf=0.56
BAC   H1 n= 56 win=38% pnl=-15.42 pf=0.64 | H2 n= 38 win=42% pnl= -3.17 pf=0.86
AVGO  H1 n= 25 win=32% pnl= -6.62 pf=0.68 | H2 n=  9 win=44% pnl= -1.89 pf=0.74
JPM   H1 n= 55 win=38% pnl= -8.86 pf=0.79 | H2 n= 34 win=38% pnl= -9.50 pf=0.63
SMH   H1 n= 29 win=34% pnl=-14.28 pf=0.45 | H2 n= 14 win=36% pnl= -0.96 pf=0.92
PLTR  H1 n= 26 win=31% pnl=-10.66 pf=0.58 | H2 n= 21 win=38% pnl= -5.56 pf=0.69
CRM   H1 n= 31 win=32% pnl= -9.41 pf=0.60 | H2 n= 20 win=15% pnl=-11.82 pf=0.33
LLY   H1 n= 40 win=30% pnl=-20.93 pf=0.47 | H2 n= 23 win=22% pnl=-14.16 pf=0.39
AMD   H1 n= 22 win=36% pnl= -9.98 pf=0.53 | H2 n=  9 win=11% pnl= -9.34 pf=0.01
```

Read: AAPL, GOOGL, MSFT, SPY made money in both halves; NFLX strong in H2. AMD, SMH, CRM, LLY, PLTR, JPM lost in both halves. AMZN, QQQ, DIA flipped to losing in H2. Small samples (9-85 trades): treat as hints, not proof.
