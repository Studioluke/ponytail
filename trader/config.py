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
    # Capital the bot sizes against. Luke set $300 on 2026-10-21; the paper
    # account itself holds more, and everything above this is ignored.
    capital: float = field(default_factory=lambda: _f("TRADER_CAPITAL", 300))
    # $300 can't buy a whole SPY share, so trade fractional shares.
    fractional: bool = True
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
    # Vault rule: skip a symbol that opens more than 0.75% away from the prior close.
    max_gap: float = 0.0075
    data_feed: str = field(default_factory=lambda: os.environ.get("TRADER_FEED", "iex"))
    state_path: str = field(default_factory=lambda: os.environ.get("TRADER_STATE", "trader/journal/state.json"))
    journal_path: str = field(default_factory=lambda: os.environ.get("TRADER_JOURNAL", "trader/journal/trades.csv"))
