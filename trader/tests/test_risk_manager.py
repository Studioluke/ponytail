import os
import tempfile
import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from trader import risk_manager as rm
from trader import run
from trader.config import Config
from trader.risk import Book
from trader.strategy import Signal

ET = ZoneInfo("America/New_York")
NOW = datetime(2026, 10, 22, 10, 30, tzinfo=ET)
ACCOUNT = {"status": "ACTIVE", "equity": "100000", "cash": "100000", "daytrade_count": 0}


class Tmp(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        d = self.dir.name
        self.cfg = Config(capital=300, symbols=("SPY", "QQQ"), state_path=f"{d}/state.json",
                          journal_path=f"{d}/trades.csv", kill_path=f"{d}/KILL", notes_dir=f"{d}/notes")
        self.book = Book()
        self.book.roll("2026-10-22", "2026-W43")
        os.environ.pop("TRADER_KILL", None)

    def tearDown(self):
        self.dir.cleanup()


class Veto(Tmp):
    sig = Signal("SPY", 600.0, 599.0, 602.0, "test")

    def check(self, qty=0.4, sig=None, now=NOW, account=ACCOUNT, positions=(), bar_age=1, last=600.0):
        return rm.check_entry(self.cfg, self.book, sig or self.sig, qty, now, account, list(positions),
                              now - timedelta(minutes=bar_age), last)

    def test_clean_entry_approved(self):
        d = self.check()
        self.assertTrue(d.ok, d.reasons)

    def test_kill_switch_file_and_env(self):
        rm.kill(self.cfg, "test")
        self.assertIn("kill switch", str(self.check()))
        rm.resume(self.cfg)
        self.assertTrue(self.check().ok)
        os.environ["TRADER_KILL"] = "1"
        self.assertFalse(self.check().ok)
        del os.environ["TRADER_KILL"]

    def test_circuit_breaker(self):
        self.book.record(-6.01)  # 2% of $300
        self.assertIn("circuit breaker", str(self.check()))

    def test_risk_over_cap(self):
        # $1.50 cap; 2 shares x $1 = $2
        self.assertIn("per-trade cap", str(self.check(qty=2)))

    def test_exposure_over_capital(self):
        d = self.check(positions=[{"symbol": "QQQ", "cost_basis": "250"}])
        self.assertIn("exposure", str(d))

    def test_max_positions(self):
        cfg = Config(capital=300, symbols=("SPY", "QQQ"), max_open_positions=1, kill_path=self.cfg.kill_path)
        d = rm.check_entry(cfg, self.book, self.sig, 0.01, NOW, ACCOUNT, [{"symbol": "QQQ", "cost_basis": "1"}])
        self.assertIn("max 1", str(d))

    def test_unlisted_symbol_and_bad_bracket(self):
        d = self.check(sig=Signal("TSLA", 600, 601, 602, "x"))
        self.assertIn("approved list", str(d))
        self.assertIn("bad bracket", str(d))

    def test_entry_window(self):
        self.assertIn("entry window", str(self.check(now=NOW.replace(hour=15, minute=35))))

    def test_stale_data_and_slippage(self):
        self.assertIn("stale data", str(self.check(bar_age=5)))
        self.assertIn("price moved", str(self.check(last=603)))
        self.assertIn("below stop", str(self.check(last=598.9)))

    def test_account_flags_and_pdt(self):
        self.assertIn("account status", str(self.check(account={**ACCOUNT, "status": "SUSPENDED"})))
        self.assertIn("PDT", str(self.check(account={**ACCOUNT, "equity": "300", "daytrade_count": 3})))
        self.assertTrue(self.check(account={**ACCOUNT, "daytrade_count": 3}).ok)  # $100k paper is exempt


class FakeBroker:
    def __init__(self, stop_status="new", stop_fails=False):
        self.stop_status, self.stop_fails = stop_status, stop_fails
        self.calls = []

    def order(self, oid):
        return {"status": self.stop_status}

    def sell_stop(self, sym, qty, stop):
        self.calls.append(("sell_stop", sym))
        if self.stop_fails:
            raise RuntimeError("rejected")
        return {"id": "new-stop"}

    def close_position(self, sym):
        self.calls.append(("close", sym))

    def positions(self):
        return [{"symbol": "SPY", "cost_basis": "240"}]

    def open_orders(self):
        return []

    def flatten(self):
        self.calls.append(("flatten",))

    def closed_orders(self, since):
        return []


class Guard(Tmp):
    def setUp(self):
        super().setUp()
        self.book.open["SPY"] = {"qty": 0.4, "entry": 600, "stop": 599, "target": 602, "stop_order_id": "s1"}

    def run_protect(self, broker):
        return rm.protect(broker, self.cfg, self.book, run.journal, lambda m: None, NOW)

    def test_live_stop_left_alone(self):
        b = FakeBroker("accepted")
        self.assertEqual(self.run_protect(b), [])
        self.assertEqual(b.calls, [])

    def test_cancelled_stop_replaced(self):
        b = FakeBroker("canceled")
        self.assertEqual(self.run_protect(b), ["SPY"])
        self.assertEqual(self.book.open["SPY"]["stop_order_id"], "new-stop")
        self.assertNotIn(("close", "SPY"), b.calls)

    def test_unprotectable_position_closed(self):
        b = FakeBroker("rejected", stop_fails=True)
        self.run_protect(b)
        self.assertIn(("close", "SPY"), b.calls)
        self.assertEqual(self.book.open["SPY"]["exit_reason"], "risk")

    def test_kill_switch_flattens_in_loop(self):
        rm.kill(self.cfg, "test")
        b = FakeBroker()
        run.step(b, self.cfg, self.book, NOW)
        self.assertIn(("flatten",), b.calls)


class Review(Tmp):
    def write(self, rows):
        for r in rows:
            run.journal(self.cfg, r)

    def test_review_pairs_trades_and_flags_breaches(self):
        t = "2026-10-22T10:00:00-04:00"
        self.write([
            {"time": t, "symbol": "SPY", "event": "buy", "qty": 0.4, "price": "600.00", "stop": 599, "target": 602},
            {"time": t, "symbol": "SPY", "event": "exit_stop", "qty": 0.4, "price": "599.00", "pnl": "-0.40"},
            {"time": t, "symbol": "QQQ", "event": "buy", "qty": 1, "price": "500.00", "stop": 498, "target": 504},
            {"time": t, "symbol": "QQQ", "event": "exit_target", "qty": 1, "price": "504.00", "pnl": "4.00"},
            {"time": t, "symbol": "SPY", "event": "risk_block", "note": "vetoed: stale data"},
        ])
        trades = rm.closed_trades(rm._rows(self.cfg))
        self.assertEqual([round(x["r"], 2) for x in trades], [-1.0, 2.0])
        text = rm.review(self.cfg, NOW.date(), book=self.book)
        self.assertIn("2 trades", text)
        self.assertIn("vetoed: stale data", text)
        self.assertIn("$2.00 risk", text)  # QQQ entered over the $1.50 cap
        self.assertIn("stay on paper", text)
        self.assertTrue(os.path.exists(rm.write_review(self.cfg, NOW.date(), text)))

    def test_gate_passes_good_record(self):
        trades = [{"pnl": 3.0, "r": 2.0}, {"pnl": -1.5, "r": -1.0}] * 15
        s = rm.stats(trades, 300)
        self.assertAlmostEqual(s["profit_factor"], 2.0)
        self.assertTrue(rm.gate(s, 0)[1])
        self.assertFalse(rm.gate(s, 1)[1])


if __name__ == "__main__":
    unittest.main()
