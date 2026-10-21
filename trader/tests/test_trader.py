import os
import unittest
from datetime import datetime, timedelta, timezone

from trader import strategy
from trader.backtest import simulate
from trader.broker import Broker, LiveTradingRefused
from trader.config import Config
from trader.risk import Book, size


def bar(t, o, h, l, c, v=1000):
    return {"t": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "o": o, "h": h, "l": l, "c": c, "v": v}


def day_bars(breakout_at=20, after=None):
    """Synthetic session: flat 100-101 range, breakout to 102, then `after` bars."""
    start = datetime(2026, 10, 20, 13, 30, tzinfo=timezone.utc)  # 09:30 ET
    out = []
    for i in range(breakout_at):
        out.append(bar(start + timedelta(minutes=i), 100.5, 101, 100, 100.5))
    out.append(bar(start + timedelta(minutes=breakout_at), 100.8, 102, 100.8, 102, 5000))
    prev = 102
    for i, (h, l, c) in enumerate(after or [], start=breakout_at + 1):
        out.append(bar(start + timedelta(minutes=i), prev, h, l, c))
        prev = c
    return out


class Sizing(unittest.TestCase):
    def test_risk_caps_size(self):
        # $1,000 * 0.5% = $5 risk, $1/share stop -> 5 shares
        self.assertEqual(size(1000, 0.005, 50, 49, 10_000), 5)

    def test_cash_caps_size(self):
        self.assertEqual(size(1000, 0.005, 600, 599.5, 10_000), 1)

    def test_bad_stop(self):
        self.assertEqual(size(1000, 0.005, 50, 51, 1000), 0)


class Breakers(unittest.TestCase):
    def test_limits(self):
        cfg = Config()
        b = Book()
        b.roll("2026-10-20", "2026-W43")
        self.assertIsNone(b.halted(cfg))
        b.record(-20.01)
        self.assertIn("daily", b.halted(cfg))
        b.roll("2026-10-21", "2026-W43")
        self.assertIsNone(b.halted(cfg))
        for _ in range(3):
            b.record(-1)
        self.assertIn("losing", b.halted(cfg))
        for d in ("22", "23"):  # week now -23.01, then -19 a day
            b.roll(f"2026-10-{d}", "2026-W43")
            b.record(-19)
        self.assertIn("weekly", b.halted(cfg))
        b.roll("2026-10-27", "2026-W44")
        self.assertIsNone(b.halted(cfg))


class Strategy(unittest.TestCase):
    def test_breakout_signal(self):
        sig = strategy.check("SPY", day_bars(), 15, 2.0)
        self.assertIsNotNone(sig)
        self.assertEqual(sig.entry, 102)
        self.assertEqual(sig.stop, 100.5)
        self.assertEqual(sig.target, 105)

    def test_no_signal_inside_range(self):
        self.assertIsNone(strategy.check("SPY", day_bars()[:-1], 15, 2.0))

    def test_only_first_break(self):
        bars = day_bars(after=[(102.5, 101.8, 102.2)])
        self.assertIsNone(strategy.check("SPY", bars, 15, 2.0))


class Backtest(unittest.TestCase):
    def test_target_hit(self):
        bars = day_bars(after=[(103, 101.9, 102.8), (105.5, 102.8, 105.2)])
        trades = simulate({"SPY": bars}, Config(symbols=("SPY",)), slippage=0)
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0]["how"], "target")
        self.assertEqual(trades[0]["qty"], 3)  # $5 / $1.50 risk
        self.assertAlmostEqual(trades[0]["pnl"], 9.0)

    def test_stop_hit(self):
        bars = day_bars(after=[(102.1, 100.2, 100.4)])
        trades = simulate({"SPY": bars}, Config(symbols=("SPY",)), slippage=0)
        self.assertEqual(trades[0]["how"], "stop")
        self.assertAlmostEqual(trades[0]["pnl"], -4.5)


class PaperOnly(unittest.TestCase):
    def test_refuses_live_endpoint(self):
        os.environ["APCA_API_BASE_URL"] = "https://api.alpaca.markets"
        try:
            with self.assertRaises(LiveTradingRefused):
                Broker("k", "s")
        finally:
            del os.environ["APCA_API_BASE_URL"]


if __name__ == "__main__":
    unittest.main()
