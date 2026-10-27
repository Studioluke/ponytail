import dataclasses
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from trader import risk_manager, run, strategy
from trader.config import Config
from trader.risk import Book

ET = ZoneInfo("America/New_York")


def bars(prices, start=datetime(2026, 10, 26, 13, 30, tzinfo=timezone.utc)):
    return [{"t": (start + timedelta(minutes=i)).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "o": p, "h": p + 0.05, "l": p - 0.05, "c": p, "v": 1000} for i, p in enumerate(prices)]


class FakeBroker:
    def __init__(self, data):
        self.data, self.orders, self.n = data, [], 0

    def positions(self):
        return []

    def open_orders(self):
        return []

    def closed_orders(self, since):
        return []

    def account(self):
        return {"status": "ACTIVE", "cash": "100000", "equity": "100000", "daytrade_count": 0}

    def bars(self, symbols, timeframe, start, end=None, feed="iex"):
        if timeframe == "1Day":
            return {s: [{"t": "2026-10-23T04:00:00Z", "c": self.data[s][0]["o"]}] for s in symbols}
        return {s: self.data[s] for s in symbols if s in self.data}

    def latest_price(self, symbol, feed="iex"):
        return self.data[symbol][-1]["c"]

    def buy_market(self, symbol, qty, client_id):
        self.n += 1
        self.orders.append(("buy", symbol, qty, client_id))
        self.last_symbol = symbol
        return {"id": f"o{self.n}"}

    def order(self, oid):
        return {"status": "filled", "filled_avg_price": str(self.data[self.last_symbol][-1]["c"])}

    def sell_stop(self, symbol, qty, stop):
        self.n += 1
        self.orders.append(("stop", symbol, qty, stop))
        return {"id": f"o{self.n}"}


class LearningTrade(unittest.TestCase):
    def setUp(self):
        d = tempfile.mkdtemp()
        self.cfg = Config(symbols=("AAA", "BBB"), state_path=f"{d}/s.json", journal_path=f"{d}/j.csv",
                          kill_path=f"{d}/KILL", research_dir=f"{d}/r", learning_mode=True)
        os.environ.pop("TRADER_KILL", None)

    def test_strongest_trend_picks_furthest_above_vwap(self):
        up = bars([100] * 15 + [100 + i * 0.05 for i in range(1, 60)])
        flat = bars([100] * 15 + [100.01] * 59)
        sig = strategy.strongest_trend({"AAA": flat, "BBB": up}, 15, 2.0)
        self.assertEqual(sig.symbol, "BBB")
        self.assertLess(sig.stop, sig.entry)
        self.assertLess(sig.entry, sig.target)

    def test_no_trade_by_11_takes_one_learning_trade(self):
        # 90 minutes of a slow climb that never makes a fresh ORB break at the
        # current bar, so only the fallback can enter.
        climb = bars([100] * 15 + [100.2 + i * 0.01 for i in range(75)] + [101.0] * 16)
        broker = FakeBroker({"AAA": climb, "BBB": bars([100] * 106)})
        book = Book()
        book.roll("2026-10-26", "2026-W44")
        book.traded_today = ["AAA", "BBB"]  # their ORB signals already came and went
        now = datetime(2026, 10, 26, 11, 1, 30, tzinfo=ET)
        run.step(broker, self.cfg, book, now)
        buys = [o for o in broker.orders if o[0] == "buy"]
        self.assertEqual(len(buys), 1)
        self.assertEqual(buys[0][1], "AAA")
        self.assertTrue(buys[0][3].startswith("learn-"))
        self.assertTrue(book.learning_tried)
        self.assertIn("AAA", book.open)
        # Half risk: at most $0.75 at the stop.
        t = book.open["AAA"]
        self.assertGreater(t["entry"], t["stop"])
        self.assertLessEqual(t["qty"] * (t["entry"] - t["stop"]), 0.75 + 1e-6)
        run.step(broker, self.cfg, book, now + timedelta(minutes=1))
        self.assertEqual(len([o for o in broker.orders if o[0] == "buy"]), 1)  # only once a day

    def test_orb_break_still_enters(self):
        # 15-minute range at 100, then a fresh close above it at 9:50.
        b = bars([100] * 20 + [100.4])
        broker = FakeBroker({"AAA": b, "BBB": bars([100] * 21)})
        book = Book()
        book.roll("2026-10-26", "2026-W44")
        run.step(broker, self.cfg, book, datetime(2026, 10, 26, 9, 51, 30, tzinfo=ET))
        buys = [o for o in broker.orders if o[0] == "buy"]
        self.assertEqual([(o[1], o[3][:4]) for o in buys], [("AAA", "orb-")])
        self.assertEqual(book.entries, 1)
        self.assertTrue(any(o[0] == "stop" and o[1] == "AAA" for o in broker.orders))

    def test_no_learning_trade_before_11(self):
        broker = FakeBroker({"AAA": bars([100] * 15 + [100.5] * 60), "BBB": bars([100] * 75)})
        book = Book()
        book.roll("2026-10-26", "2026-W44")
        book.traded_today = ["AAA", "BBB"]
        run.step(broker, self.cfg, book, datetime(2026, 10, 26, 10, 45, 30, tzinfo=ET))
        self.assertEqual(broker.orders, [])


class InPlay(unittest.TestCase):
    setUp = LearningTrade.setUp

    def write_brief(self, in_play):
        os.makedirs(self.cfg.research_dir, exist_ok=True)
        with open(f"{self.cfg.research_dir}/2026-10-26.json", "w") as f:
            json.dump({"watchlist": [], "in_play": in_play}, f)

    def test_in_play_symbol_is_traded_and_tagged(self):
        self.write_brief(["CCC", "AAA"])
        b = bars([100] * 20 + [100.4])
        broker = FakeBroker({"AAA": bars([100] * 21), "BBB": bars([100] * 21), "CCC": b})
        book = Book()
        book.roll("2026-10-26", "2026-W44")
        run.step(broker, self.cfg, book, datetime(2026, 10, 26, 9, 51, 30, tzinfo=ET))
        self.assertEqual([o[1] for o in broker.orders if o[0] == "buy"], ["CCC"])
        with open(self.cfg.journal_path) as f:
            self.assertIn("[in_play]", f.read())

    def test_in_play_off_or_missing_brief_keeps_the_base_list(self):
        self.assertEqual(risk_manager.day_config(self.cfg, "2026-10-26").symbols, ("AAA", "BBB"))
        self.write_brief(["CCC"])
        off = dataclasses.replace(self.cfg, trade_in_play=False)
        self.assertEqual(risk_manager.day_config(off, "2026-10-26").symbols, ("AAA", "BBB"))
        self.assertEqual(risk_manager.day_config(self.cfg, "2026-10-26").symbols, ("AAA", "BBB", "CCC"))


class TargetExit(unittest.TestCase):
    def test_close_waits_for_the_stop_cancel_and_survives_a_failed_close(self):
        class B:
            def __init__(self):
                self.polls, self.closed, self.fail = 0, False, True

            def latest_price(self, sym, feed):
                return 11.0

            def cancel(self, oid):
                pass

            def order(self, oid):
                self.polls += 1
                return {"status": "pending_cancel" if self.polls < 2 else "canceled"}

            def close_position(self, sym):
                if self.fail:
                    raise RuntimeError("403 insufficient qty available")
                self.closed = True

        b, book = B(), Book()
        book.open["X"] = {"qty": 1, "entry": 10, "stop": 9.5, "target": 10.9, "stop_order_id": "s1"}
        run._time.sleep, sleep = (lambda s: None), run._time.sleep
        try:
            run.manage(b, Config(), book)  # close fails: no crash, exit not marked
            self.assertNotIn("exit_reason", book.open["X"])
            b.fail = False
            run.manage(b, Config(), book)
        finally:
            run._time.sleep = sleep
        self.assertTrue(b.closed)
        self.assertEqual(book.open["X"]["exit_reason"], "target")


if __name__ == "__main__":
    unittest.main()
