"""Settings and risk limits. Every number here can be overridden by env var."""
import os
from dataclasses import dataclass, field
from datetime import time

PAPER_URL = "https://paper-api.alpaca.markets"
DATA_URL = "https://data.alpaca.markets"


def _f(name, default):
    return float(os.environ.get(name, default))


@dataclass(frozen=True)
class Config:
    # SPY/QQQ plus the large caps whose breakouts were profitable in both
    # Jan-Jun and Jul-Oct 2026 backtests (see the vault journal, 2026-10-21).
    symbols: tuple = field(default_factory=lambda: tuple(
        os.environ.get("TRADER_SYMBOLS", "SPY,QQQ,AAPL,MSFT,GOOGL").split(",")))
    # Capital the bot sizes against. Luke set $300 on 2026-10-21; the paper
    # account itself holds more, and everything above this is ignored.
    capital: float = field(default_factory=lambda: _f("TRADER_CAPITAL", 300))
    # $300 can't buy a whole SPY share, so trade fractional shares.
    fractional: bool = True
    risk_per_trade: float = field(default_factory=lambda: _f("TRADER_RISK_PER_TRADE", 0.005))
    max_daily_loss: float = field(default_factory=lambda: _f("TRADER_MAX_DAILY_LOSS", 0.02))
    max_daily_losses: int = field(default_factory=lambda: int(_f("TRADER_MAX_DAILY_LOSSES", 3)))
    max_weekly_loss: float = field(default_factory=lambda: _f("TRADER_MAX_WEEKLY_LOSS", 0.05))
    # Risk manager limits (trader/risk_manager.py).
    max_open_positions: int = field(default_factory=lambda: int(_f("TRADER_MAX_POSITIONS", 3)))
    # Largest single position as a share of capital. 1.0 keeps the sizing the
    # backtests used; lower it to spread $300 over more than one breakout.
    max_position_frac: float = field(default_factory=lambda: _f("TRADER_MAX_POSITION_FRAC", 1.0))
    # Refuse to enter on bars older than this, or if the last trade has run
    # this far from the signal price.
    max_data_age_minutes: int = field(default_factory=lambda: int(_f("TRADER_MAX_DATA_AGE", 3)))
    max_slippage: float = field(default_factory=lambda: _f("TRADER_MAX_SLIPPAGE", 0.0025))
    # The kill switch is this file (committed with the journal) or TRADER_KILL=1.
    kill_path: str = field(default_factory=lambda: os.environ.get("TRADER_KILL_FILE", "trader/journal/KILL"))
    notes_dir: str = field(default_factory=lambda: os.environ.get("TRADER_NOTES", "trader/journal/notes"))
    # Times are US/Eastern.
    session_start: time = time(9, 40)
    last_entry: time = time(15, 30)
    flatten_at: time = time(15, 45)
    opening_range_minutes: int = 15
    reward_risk: float = 2.0
    # Vault rule: skip a symbol that opens more than 0.75% away from the prior close.
    max_gap: float = 0.0075
    data_feed: str = field(default_factory=lambda: os.environ.get("TRADER_FEED", "iex"))
    state_path: str = field(default_factory=lambda: os.environ.get("TRADER_STATE", "trader/journal/state.json"))
    journal_path: str = field(default_factory=lambda: os.environ.get("TRADER_JOURNAL", "trader/journal/trades.csv"))
