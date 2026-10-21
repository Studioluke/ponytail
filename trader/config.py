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
    symbols: tuple = ("SPY", "QQQ")
    # Capital the bot sizes against. Until Luke sets it, we act as if the
    # account held $1,000, even though the paper account itself holds more.
    capital: float = field(default_factory=lambda: _f("TRADER_CAPITAL", 1000))
    risk_per_trade: float = field(default_factory=lambda: _f("TRADER_RISK_PER_TRADE", 0.005))
    max_daily_loss: float = field(default_factory=lambda: _f("TRADER_MAX_DAILY_LOSS", 0.02))
    max_daily_losses: int = field(default_factory=lambda: int(_f("TRADER_MAX_DAILY_LOSSES", 3)))
    max_weekly_loss: float = field(default_factory=lambda: _f("TRADER_MAX_WEEKLY_LOSS", 0.05))
    # Times are US/Eastern.
    session_start: time = time(9, 40)
    last_entry: time = time(15, 30)
    flatten_at: time = time(15, 45)
    opening_range_minutes: int = 15
    reward_risk: float = 2.0
    data_feed: str = field(default_factory=lambda: os.environ.get("TRADER_FEED", "iex"))
    state_path: str = field(default_factory=lambda: os.environ.get("TRADER_STATE", "trader/data/state.json"))
    journal_path: str = field(default_factory=lambda: os.environ.get("TRADER_JOURNAL", "trader/data/journal.csv"))
