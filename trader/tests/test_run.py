import csv
import dataclasses
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from trader import risk_manager, run, strategies, strategy
from trader.config import Config
from trader.risk import Book

ET = ZoneInfo("America/New_York")
OPEN = datetime(2026, 10, 26, 13, 30, tzinfo=timezone.utc)  # 9:30 ET


def bars(prices, start=OPEN, vol=1000):
    return [{"t": (start + timedelta(minutes=i)).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "o": p, "h": p + 0.05, "l": p - 0.05, "c": p, "v": vol} for i, p in enumerate(prices)]


def daily(close, rng=2.0, n=20):
    """n prior daily bars ending 2026-10-23, each with range `rng` (so ATR = rng)."""
    out = []
    for i in range(n):
        d = datetime(2026, 10, 23) - timedelta(days=n - 1 - i)
        out.append({"t": d.strftime("%Y-%m-%dT04:00:00Z"), "o": close, "h": close + rng / 2,
                    "l": close - rng / 2, "c": close, "v": 1_000_000})
    return out


class FakeBroker:
    def __init__(self, data, days=None, five=None, hist5=None, hist_min=None):
        self.data, self.orders, self.n = data, [], 0
        self.days = days or {s: daily(b[0]["o"]) for s, b in data.items()}
        self.five, self.hist5, self.hist_min = five or {}, hist5 or {}, hist_min or {}
        self.held, self.prices, self.last_symbol = [], {}, next(iter(data))

    def positions(self):
        return self.held

    def open_orders(self):
        return []

    def closed_orders(self, since):
        return []

    def account(self):
        return {"status": "ACTIVE", "cash": "100000", "equity": "100000", "daytrade_count": 0}

    def bars(self, symbols, timeframe, start, end=None, feed="iex"):
        today = start[:10] == "2026-10-26"
        if timeframe == "1Day":
            return {s: self.days[s] for s in symbols if s in self.days}
        if timeframe == "5Min":
            src = self.five if today else self.hist5
            return {s: [src[s]] for s in symbols if s in src}
        if not today:
            return {s: self.hist_min[s] for s in symbols if s in self.hist_min}
        return {s: self.data[s] for s in symbols if s in self.data}

    def latest_price(self, symbol, feed="iex"):
        if symbol in self.prices:
            return self.prices[symbol]
        return self.data[symbol][-1]["c"]

    def buy_market(self, symbol, qty, client_id):
        self.n += 1
        self.orders.append(("buy", symbol, qty, client_id))
        self.last_symbol = symbol
        return {"id": f"o{self.n}"}

    def order(self, oid):
        return {"status": "filled", "filled_avg_price": str(self.latest_price(self.last_symbol))}

    def sell_stop(self, symbol, qty, stop):
        self.n += 1
        self.orders.append(("stop", symbol, qty, stop))
        return {"id": f"o{self.n}"}

    def sell_market(self, symbol, qty):
        self.orders.append(("sell", symbol, qty))

    def cancel(self, oid):
        self.orders.append(("cancel", oid))

    def close_position(self, symbol):
        self.orders.append(("close", symbol))


class Base(unittest.TestCase):
    def setUp(self):
        run._DAY.clear()
        d = tempfile.mkdtemp()
        self.cfg = Config(symbols=("AAA", "BBB"), core_symbols=("AAA", "BBB"), watchlist=("AAA", "BBB", "CCC"),
                          state_path=f"{d}/s.json", journal_path=f"{d}/j.csv", kill_path=f"{d}/KILL",
                          research_dir=f"{d}/r", learning_mode=True)
        os.environ.pop("TRADER_KILL", None)
        self.book = Book()
        self.book.roll("2026-10-26", "2026-W44")
        self.book.sip_watch = []  # most tests are not about the 9:35 scan

    def at(self, h, m, s=30):
        return datetime(2026, 10, 26, h, m, s, tzinfo=ET)

    def journal(self):
        with open(self.cfg.journal_path) as f:
            return list(csv.DictReader(f))

    def shadows(self):
        path = run.shadow_path(self.cfg)
        if not os.path.exists(path):
            return []
        with open(path) as f:
            return list(csv.DictReader(f))

    def buys(self, broker):
        return [o for o in broker.orders if o[0] == "buy"]


class Control(Base):
    def test_orb_break_enters_with_wider_stop_and_half_at_2r(self):
        # 15-minute range 99.95-100.05, then a fresh close above it at 9:50.
        broker = FakeBroker({"AAA": bars([100] * 20 + [100.4]), "BBB": bars([100] * 21)})
        run.step(broker, self.cfg, self.book, self.at(9, 51))
        self.assertEqual([(o[1], o[3].split("-")[0]) for o in self.buys(broker)], [("AAA", "control")])
        t = self.book.open["AAA"]
        # ATR 2.0 -> stop at least 0.50 below; midpoint was only 0.40 below.
        self.assertAlmostEqual(t["stop"], 99.9, places=2)
        self.assertIsNone(t["target"])
        self.assertAlmostEqual(t["half_at"], 101.4, places=2)
        self.assertEqual(t["strategy"], "control")
        # $0.75 risk cap for the control group.
        self.assertLessEqual(t["qty"] * (t["entry"] - t["stop"]), 0.75 + 1e-6)
        self.assertIn("[control]", self.journal()[-1]["note"])

    def test_gap_is_a_veto_now_even_in_learning_mode(self):
        b = bars([102] * 20 + [102.4])
        broker = FakeBroker({"AAA": b, "BBB": bars([100] * 21)}, days={"AAA": daily(100), "BBB": daily(100)})
        run.step(broker, self.cfg, self.book, self.at(9, 51))
        self.assertEqual(self.buys(broker), [])
        self.assertEqual(self.journal()[-1]["event"], "skip")

    def test_research_skip_is_a_veto(self):
        os.makedirs(self.cfg.research_dir, exist_ok=True)
        with open(f"{self.cfg.research_dir}/2026-10-26.json", "w") as f:
            json.dump({"watchlist": [{"symbol": "AAA", "verdict": "skip", "why": "earnings"}]}, f)
        broker = FakeBroker({"AAA": bars([100] * 20 + [100.4]), "BBB": bars([100] * 21)})
        run.step(broker, self.cfg, self.book, self.at(9, 51))
        self.assertEqual(self.buys(broker), [])
        self.assertEqual(self.journal()[-1]["event"], "risk_block")

    def test_second_control_signal_becomes_a_shadow_trade(self):
        broker = FakeBroker({"AAA": bars([100] * 20 + [100.4]), "BBB": bars([100] * 20 + [100.4])})
        run.step(broker, self.cfg, self.book, self.at(9, 51))
        self.assertEqual(len(self.buys(broker)), 1)
        sh = self.shadows()
        self.assertEqual([(r["strategy"], r["symbol"]) for r in sh], [("control", "BBB")])
        self.assertIn("slots full", sh[0]["why"])
        self.assertGreater(float(sh[0]["qty"]), 0)

    def test_three_control_losses_halt_control_only(self):
        self.book.strat_losses = {"control": 3}
        broker = FakeBroker({"AAA": bars([100] * 20 + [100.4]), "BBB": bars([100] * 21)})
        run.step(broker, self.cfg, self.book, self.at(9, 51))
        self.assertEqual(self.buys(broker), [])
        self.assertEqual(self.shadows()[0]["symbol"], "AAA")  # still sampled
        self.assertIsNone(self.book.halted(self.cfg, "noise"))
        self.assertIn("losing control", self.book.halted(self.cfg, "control"))


class StocksInPlay(Base):
    def setUp(self):
        super().setUp()
        self.book.sip_watch = None

    def broker(self, first, after):
        five = {"CCC": {"t": "2026-10-26T13:30:00Z", "o": 50.0, "h": first, "l": 49.8, "c": 50.9, "v": 5000},
                "AAA": {"t": "2026-10-26T13:30:00Z", "o": 100.0, "h": 100.1, "l": 99.9, "c": 100.0, "v": 1000}}
        hist5 = {"CCC": {"t": "x", "v": 1000}, "AAA": {"t": "x", "v": 1000}}
        b = FakeBroker({"AAA": bars([100] * 7), "BBB": bars([100] * 7), "CCC": bars([50.5] * 6 + [after]),
                        "SPY": bars([500] * 7)},
                       days={"AAA": daily(100), "BBB": daily(100), "CCC": daily(50, rng=3.0), "SPY": daily(500)},
                       five=five, hist5=hist5)
        return b

    def test_scan_ranks_by_rvol_and_buys_the_first_break(self):
        broker = self.broker(51.0, 51.2)
        run.step(broker, self.cfg, self.book, self.at(9, 37))
        self.assertEqual([c["symbol"] for c in self.book.sip_watch], ["CCC", "AAA"])
        self.assertEqual(self.book.sip_watch[0]["rvol"], 5.0)
        self.assertEqual([o[1] for o in self.buys(broker)], ["CCC"])
        t = self.book.open["CCC"]
        self.assertEqual(t["strategy"], "sip_orb")
        self.assertAlmostEqual(t["stop"], 51.0 - 0.1 * 3.0, places=2)
        self.assertIsNone(t["target"])
        self.assertEqual(self.journal()[0]["event"], "sip_scan")

    def test_red_first_candle_is_not_traded(self):
        broker = self.broker(51.0, 51.2)
        broker.five["CCC"]["c"] = 49.9  # closed below its open
        run.step(broker, self.cfg, self.book, self.at(9, 37))
        self.assertEqual(self.buys(broker), [])

    def test_earnings_skip_does_not_block_sip_but_an_offering_does(self):
        os.makedirs(self.cfg.research_dir, exist_ok=True)
        for why, n in (("Earnings after the close", 1), ("secondary offering priced", 0)):
            run._DAY.clear()
            self.book = Book()
            self.book.roll("2026-10-26", "2026-W44")
            with open(f"{self.cfg.research_dir}/2026-10-26.json", "w") as f:
                json.dump({"watchlist": [{"symbol": "CCC", "verdict": "skip", "why": why}]}, f)
            broker = self.broker(51.0, 51.2)
            run.step(broker, self.cfg, self.book, self.at(9, 37))
            self.assertEqual(len(self.buys(broker)), n, why)


def spy_day(prices, start):
    return bars(prices, start=start)


class Noise(Base):
    def broker(self, spy_prices, prior=500.0):
        # 14 prior sessions where SPY moves 0.1% from its open every minute: sigma 0.001.
        hist = []
        for k in range(14):
            d = datetime(2026, 10, 6, 13, 30, tzinfo=timezone.utc) + timedelta(days=k)
            hist += bars([500.5] * 390, start=d)
            hist[-390]["o"] = 500.0
        days = {"SPY": [{"t": (datetime(2026, 10, 6) + timedelta(days=k)).strftime("%Y-%m-%dT04:00:00Z"),
                         "o": prior, "h": prior + 1, "l": prior - 1, "c": prior} for k in range(14)],
                "SH": daily(40), "AAA": daily(100), "BBB": daily(100), "IWM": daily(200)}
        n = len(spy_prices)
        data = {"SPY": bars(spy_prices), "SH": bars([40] * n), "AAA": bars([100] * n), "BBB": bars([100] * n),
                "IWM": bars([200] * n)}
        return FakeBroker(data, days=days, hist_min={"SPY": hist})

    def test_break_above_upper_band_buys_spy_on_the_grid(self):
        broker = self.broker([500] * 29 + [501.0])  # 9:59 bar closes 0.2% up; band is 0.1%
        run.step(broker, self.cfg, self.book, self.at(10, 0, 5))
        self.assertEqual([o[1] for o in self.buys(broker)], ["SPY"])
        t = self.book.open["SPY"]
        self.assertEqual((t["strategy"], t["trail"], t["dir"]), ("noise", "band", 1))
        self.assertAlmostEqual(t["stop"], round(501.0 * 0.99, 2))
        # Only once per grid point and once a day.
        run.step(broker, self.cfg, self.book, self.at(10, 1, 5))
        self.assertEqual(len(self.buys(broker)), 1)

    def test_break_below_lower_band_buys_sh(self):
        broker = self.broker([500] * 29 + [499.0])
        run.step(broker, self.cfg, self.book, self.at(10, 0, 5))
        self.assertEqual([o[1] for o in self.buys(broker)], ["SH"])
        self.assertEqual(self.book.open["SH"]["dir"], -1)

    def test_no_entry_between_grid_points(self):
        broker = self.broker([500] * 34 + [501.0])
        run.step(broker, self.cfg, self.book, self.at(10, 5, 5))
        self.assertEqual(self.buys(broker), [])

    def test_fallback_at_1130_is_half_size(self):
        broker = self.broker([500] * 119 + [500.2])  # inside the band, above the open
        run.step(broker, self.cfg, self.book, self.at(11, 0, 5))
        self.assertEqual(self.buys(broker), [])
        broker = self.broker([500] * 119 + [500.2])
        run.step(broker, self.cfg, self.book, self.at(11, 30, 5))
        self.assertEqual([o[1] for o in self.buys(broker)], ["SPY"])
        t = self.book.open["SPY"]
        self.assertEqual(t["trail"], "vwap_grid")
        self.assertLessEqual(t["qty"] * t["entry"], self.cfg.capital * self.cfg.max_position_frac / 2 + 0.01)
        self.assertIn("fallback", self.journal()[-1]["note"])

    def test_lasthalf_buys_spy_and_shadows_iwm(self):
        prices = [500] * 29 + [501.0] + [500.5] * 330
        broker = self.broker(prices, prior=500.0)
        self.book.flags["noise_done"] = True
        run.step(broker, self.cfg, self.book, self.at(15, 30, 5))
        self.assertEqual([o[1] for o in self.buys(broker)], ["SPY"])
        t = self.book.open["SPY"]
        self.assertEqual(t["strategy"], "lasthalf")
        self.assertAlmostEqual(t["stop"], round(500.5 * 0.995, 2))
        self.assertEqual([(r["strategy"], r["symbol"]) for r in self.shadows()], [("lasthalf", "IWM")])


class Exits(unittest.TestCase):
    def test_half_then_vwap_trail(self):
        t = {"entry": 100, "stop": 99, "target": None, "half_at": 102, "trail": "vwap"}
        self.assertEqual(strategies.exit_action(t, 101.9, 101.9, 100.5), None)
        self.assertEqual(strategies.exit_action(t, 102.0, 102.0, 100.5)[0], "half")
        t["half_done"] = True
        self.assertIsNone(strategies.exit_action(t, 101, 101, 100.5))
        self.assertEqual(strategies.exit_action(t, 100.4, 100.4, 100.5), ("close", "trail"))

    def test_band_trail_only_on_the_grid(self):
        t = {"trail": "band", "dir": 1}
        spy = {"close": 500.2, "vwap": 500.3, "upper": 500.5, "lower": 499.5}
        self.assertIsNone(strategies.exit_action(t, 1, 1, 1, spy, grid=False))
        self.assertEqual(strategies.exit_action(t, 1, 1, 1, spy, grid=True), ("close", "trail"))
        sh = {"trail": "band", "dir": -1}
        spy_down = dict(spy, close=499.3)  # still below min(lower, VWAP): hold
        self.assertIsNone(strategies.exit_action(sh, 1, 1, 1, spy_down, grid=True))
        spy_up = dict(spy, close=499.6)
        self.assertEqual(strategies.exit_action(sh, 1, 1, 1, spy_up, grid=True), ("close", "trail"))

    def test_manage_sells_half_and_moves_stop_to_breakeven(self):
        broker = FakeBroker({"AAA": bars([102.1])})
        book = Book()
        book.open["AAA"] = {"qty": 0.5, "entry": 100, "stop": 99, "stop0": 99, "target": None, "half_at": 102,
                            "trail": "vwap", "stop_order_id": "s1", "strategy": "control"}
        cfg = Config(journal_path=tempfile.mkdtemp() + "/j.csv")
        run._time.sleep, sleep = (lambda s: None), run._time.sleep
        try:
            run.manage(broker, cfg, book, datetime(2026, 10, 26, 11, 0, tzinfo=ET), {"AAA": bars([102.1])})
        finally:
            run._time.sleep = sleep
        t = book.open["AAA"]
        self.assertIn(("sell", "AAA", 0.25), broker.orders)
        self.assertEqual((t["qty"], t["qty0"], t["stop"], t["half_done"]), (0.25, 0.5, 100, True))
        self.assertEqual(broker.orders[-1], ("stop", "AAA", 0.25, 100))


class Simulate(unittest.TestCase):
    def test_stop_eod_and_half(self):
        b = bars([100] * 30 + [99.0] + [100] * 10)
        t = {"time": "2026-10-26T09:45:00-04:00", "qty": 1.0, "entry": 100.0, "stop": 99.5, "target": None}
        self.assertEqual(strategies.simulate(t, b)["how"], "stop")
        b2 = bars([100] * 20 + [100.2] * 380)  # never stops; out at 15:58
        res = strategies.simulate(t, b2)
        self.assertEqual(res["how"], "eod")
        self.assertAlmostEqual(res["pnl"], 0.2, places=4)
        b3 = bars([100] * 20 + [101.0] + [101.2] * 5 + [100.1])  # 2R hit, then below VWAP (~100.29)
        t3 = dict(t, half_at=101.0, trail="vwap")
        res = strategies.simulate(t3, b3)
        self.assertEqual(res["how"], "trail")
        self.assertAlmostEqual(res["pnl"], 0.5 * 1.0 + 0.5 * 0.1, places=3)


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


class InPlay(Base):
    def test_in_play_off_or_missing_brief_keeps_the_base_list(self):
        self.assertEqual(risk_manager.day_config(self.cfg, "2026-10-26").symbols, ("AAA", "BBB"))
        os.makedirs(self.cfg.research_dir, exist_ok=True)
        with open(f"{self.cfg.research_dir}/2026-10-26.json", "w") as f:
            json.dump({"watchlist": [], "in_play": ["CCC"]}, f)
        off = dataclasses.replace(self.cfg, trade_in_play=False)
        self.assertEqual(risk_manager.day_config(off, "2026-10-26").symbols, ("AAA", "BBB"))
        self.assertEqual(risk_manager.day_config(self.cfg, "2026-10-26").symbols, ("AAA", "BBB", "CCC"))


class Fomc(Base):
    def brief(self):
        os.makedirs(self.cfg.research_dir, exist_ok=True)
        with open(f"{self.cfg.research_dir}/2026-10-26.json", "w") as f:
            json.dump({"watchlist": [], "events": [{"date": "2026-10-26", "symbol": "ALL",
                                                    "event": "FOMC decision 2:00 ET", "timing": "during"}]}, f)

    def test_fomc_day_halves_risk(self):
        self.brief()
        broker = FakeBroker({"AAA": bars([100] * 20 + [100.4]), "BBB": bars([100] * 21)},
                            days={"AAA": daily(100, rng=0.1), "BBB": daily(100)})
        run.step(broker, self.cfg, self.book, self.at(9, 51))
        t = self.book.open["AAA"]
        self.assertLessEqual(t["qty"] * (t["entry"] - t["stop"]), 0.375 + 1e-6)

    def test_fomc_blackout_vetoes_entries(self):
        sig = strategy.Signal("AAA", 100.0, 99.0, 102.0, "test")
        acct = {"status": "ACTIVE", "cash": "100000", "equity": "100000", "daytrade_count": 0}
        at = datetime(2026, 10, 26, 14, 10, tzinfo=ET)
        d = risk_manager.check_entry(self.cfg, self.book, sig, 0.5, at, acct, [], fomc=True)
        self.assertTrue(any("FOMC" in r for r in d.reasons))
        d = risk_manager.check_entry(self.cfg, self.book, sig, 0.5, at, acct, [], fomc=False)
        self.assertFalse(any("FOMC" in r for r in d.reasons))


class ShadowReplay(Base):
    def test_replay_fills_results_and_review_counts_them(self):
        from trader import shadow
        broker = FakeBroker({"AAA": bars([100] * 20 + [100.4]), "BBB": bars([100] * 20 + [100.4])})
        run.step(broker, self.cfg, self.book, self.at(9, 51))
        self.assertEqual(len(self.shadows()), 1)
        # Replay: BBB runs past 2R (101.4), half comes off, then the rest stops at breakeven.
        broker.data["BBB"] = bars([100] * 20 + [100.4] * 5 + [101.5] * 5 + [100.2] * 5)
        broker.data["SPY"] = bars([500] * 35)
        run._DAY.clear()
        self.assertEqual(shadow.replay(broker, self.cfg, datetime(2026, 10, 26).date()), 1)
        r = self.shadows()[0]
        self.assertEqual(r["how"], "stop")
        self.assertAlmostEqual(float(r["r"]), 1.0, places=2)  # half at +2R, half at 0R
        res = shadow.results(self.cfg)
        self.assertEqual(res[0]["group"], "control")
        lines = risk_manager.experiment_lines(self.cfg, [], start="2026-10-01")
        self.assertTrue(any(line.startswith("| control | 0 | 1 |") for line in lines), lines)


class SipLateBreak(unittest.TestCase):
    def test_break_during_the_scan_still_counts_within_the_chase_limit(self):
        c = {"symbol": "CCC", "hi": 51.0, "lo": 49.8, "atr": 3.0, "rvol": 5.0, "green": True}
        b = bars([50.5] * 5 + [51.2, 51.3, 51.25])  # broke at 9:35, still above
        sig = strategies.sip_signal(c, b, 51.3)
        self.assertIsNotNone(sig)
        self.assertAlmostEqual(sig.stop, 50.7)
        self.assertIsNone(strategies.sip_signal(c, b, 51.7))  # ran past 0.2 x ATR
        self.assertIsNone(strategies.sip_signal(c, b, 50.9))  # back under the high


if __name__ == "__main__":
    unittest.main()
