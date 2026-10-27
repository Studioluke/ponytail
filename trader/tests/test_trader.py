import os
import unittest
from datetime import datetime, timedelta, timezone

from trader import research, strategy
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

    def test_fractional(self):
        # $300 * 0.5% = $1.50 risk, $1.50 stop -> 1 share, but cash allows 0.387
        self.assertEqual(size(300, 0.005, 775, 773.5, 300, fractional=True), 0.387)
        self.assertEqual(size(300, 0.005, 775, 774, 300, fractional=True), 0.387)
        self.assertEqual(size(300, 0.005, 775, 760, 300, fractional=True), 0.1)

    def test_fractional_minimum(self):
        self.assertEqual(size(300, 0.005, 775, 774, 0.5, fractional=True), 0)

    def test_bad_stop(self):
        self.assertEqual(size(1000, 0.005, 50, 51, 1000), 0)


class Breakers(unittest.TestCase):
    def test_limits(self):
        cfg = Config(capital=1000)
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
        trades = simulate({"SPY": bars}, Config(symbols=("SPY",), capital=1000, fractional=False), slippage=0)
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0]["how"], "target")
        self.assertEqual(trades[0]["qty"], 3)  # $5 / $1.50 risk
        self.assertAlmostEqual(trades[0]["pnl"], 9.0)

    def test_stop_hit(self):
        bars = day_bars(after=[(102.1, 100.2, 100.4)])
        trades = simulate({"SPY": bars}, Config(symbols=("SPY",), capital=1000, fractional=False), slippage=0)
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


class Research(unittest.TestCase):
    def daily(self, closes):
        return [{"t": f"2026-09-{i + 1:02d}", "o": c, "h": c * 1.01, "l": c * 0.99, "c": c}
                for i, c in enumerate(closes)]

    def test_trend_and_gap(self):
        p = research.profile(self.daily([100 + i for i in range(60)]), 160.8)
        self.assertEqual(p["trend"], "up")
        self.assertAlmostEqual(p["gap"], 160.8 / 159 - 1)

    def test_stale_price_has_no_gap(self):
        p = research.profile(self.daily([100] * 60), 100, fresh=False)
        self.assertIsNone(p["gap"])
        level, why = research.verdict(p, [], 0.0075)
        self.assertEqual(level, "ok")
        self.assertIn("gap unknown", why[0])

    def test_big_gap_is_skip(self):
        p = research.profile(self.daily([100] * 60), 98.5)
        self.assertEqual(research.verdict(p, [], 0.0075)[0], "skip")

    def test_downtrend_is_caution(self):
        p = research.profile(self.daily([160 - i for i in range(60)]), 101)
        self.assertEqual(research.verdict(p, [], 0.0075)[0], "caution")

    def test_news_flags_skip_index_etfs(self):
        items = [{"symbols": ["MSFT", "SPY"], "created_at": "2026-10-22T08:00:00Z",
                  "headline": "Microsoft beats on Q3 earnings, raises guidance"}]
        self.assertTrue(research.tag_news(items, "MSFT")[0]["earnings"])
        self.assertFalse(research.tag_news(items, "SPY")[0]["earnings"])
        # "steps" must not match "eps"
        items[0]["headline"] = "Microsoft steps up AI spending"
        self.assertFalse(research.tag_news(items, "MSFT")[0]["earnings"])

    def test_earnings_event_is_skip(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write("date,symbol,event,timing,source\n2026-10-28,MSFT,Earnings,after,x\n2026-10-29,ALL,GDP,pre,x\n")
        from datetime import date
        self.assertEqual(research.load_events(f.name, date(2026, 10, 28))[0]["symbol"], "MSFT")
        ev = research.load_events(f.name, date(2026, 10, 29))
        self.assertEqual(sorted(e["symbol"] for e in ev), ["ALL", "MSFT"])  # after-close report carries over
        p = research.profile(self.daily([100] * 60), 100)
        self.assertEqual(research.verdict(p, [], 0.0075, [ev[0] if ev[0]["symbol"] == "MSFT" else ev[1]])[0], "skip")
        os.unlink(f.name)


class Watchlist(unittest.TestCase):
    def test_universe_puts_traded_first_without_duplicates(self):
        from dataclasses import replace
        cfg = replace(Config(), symbols=("SPY", "AAPL"), watchlist=("AAPL", "XOM", "SPY", "KO"))
        self.assertEqual(research.universe(cfg), ["SPY", "AAPL", "XOM", "KO"])

    def test_default_watchlist_is_100_and_covers_traded(self):
        cfg = Config()
        self.assertEqual(len(set(cfg.watchlist)), 100)
        self.assertTrue(set(cfg.symbols) <= set(cfg.watchlist) or os.environ.get("TRADER_SYMBOLS"))

    def test_in_play_scores_gap_in_atrs(self):
        self.assertEqual(research.in_play({"gap": -0.04, "atr_pct": 0.02}, []), 2.0)
        self.assertEqual(research.in_play({"gap": None, "atr_pct": 0.02}, []), 0)
        news = [{"earnings": True, "catalyst": False}]
        self.assertEqual(research.in_play({"gap": 0.01, "atr_pct": 0.02, "vol_expanding": True}, news), 1.25)
