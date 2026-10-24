"""Position sizing and the circuit breakers from Luke's vault rules."""
import json
import math
import os
from dataclasses import asdict, dataclass, field


def size(capital, risk_frac, entry, stop, cash_available, fractional=False):
    """Shares so a stop-out loses at most risk_frac of capital and the
    position never costs more than the cash we're allowed to use. Fractional
    sizes round down to 0.001 share and must be worth at least $1."""
    per_share = entry - stop
    if per_share <= 0 or entry <= 0:
        return 0
    qty = min(capital * risk_frac / per_share, min(capital, cash_available) / entry)
    if not fractional:
        return max(0, math.floor(qty))
    qty = math.floor(qty * 1000) / 1000
    return qty if qty * entry >= 1 else 0


@dataclass
class Book:
    day: str = ""
    week: str = ""
    day_pnl: float = 0.0
    week_pnl: float = 0.0
    day_losses: int = 0
    traded_today: list = field(default_factory=list)
    seen_orders: list = field(default_factory=list)
    # symbol -> {qty, entry, stop, target, stop_order_id, exit_reason}
    open: dict = field(default_factory=dict)

    def roll(self, day, week):
        if week != self.week:
            self.week, self.week_pnl = week, 0.0
        if day != self.day:
            self.day, self.day_pnl, self.day_losses, self.traded_today, self.open = day, 0.0, 0, [], {}

    def record(self, pnl):
        self.day_pnl += pnl
        self.week_pnl += pnl
        if pnl < 0:
            self.day_losses += 1

    def halted(self, cfg):
        """Return the reason trading is stopped, or None."""
        if self.day_pnl <= -cfg.max_daily_loss * cfg.capital:
            return f"daily loss limit hit ({self.day_pnl:.2f})"
        if self.day_losses >= cfg.max_daily_losses:
            return f"{self.day_losses} losing trades today"
        if self.week_pnl <= -cfg.max_weekly_loss * cfg.capital:
            return f"weekly loss limit hit ({self.week_pnl:.2f})"
        return None

    @classmethod
    def load(cls, path):
        if os.path.exists(path):
            with open(path) as f:
                return cls(**json.load(f))
        return cls()

    def save(self, path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=1)
