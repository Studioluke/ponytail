import unittest

from trader import sleeves as S


def bar(c, h=None, l=None, o=None):
    return {"o": o or c, "h": h or c + 1, "l": l or c - 1, "c": c}


def under(close=100, sma5=101, rsi2=20, stretch=False, rsi2_sig=False):
    return {"close": close, "sma5": sma5, "rsi2": rsi2, "stretch": stretch, "rsi2_sig": rsi2_sig}


def etf(price=50, low=49, open_=50, prev_high=52, atr=2):
    return {"price": price, "low": low, "open": open_, "prev_high": prev_high, "atr": atr}


CHAIN = [{"symbol": f"X{k}", "strike": k, "bid": b, "ask": a}
         for k, b, a in [(50, 2.0, 2.2), (51, 1.5, 1.6), (52, 1.1, 1.2), (53, 0.7, 0.8), (55, 0.3, 0.4)]]


def mk(**over):
    base = {s: {"etf": etf(), "under": under(rsi2=30 + i), "quotes": {}, "chain": None, "expiry": "2026-11-20"}
            for i, s in enumerate(S.SLEEVES)}
    for s, v in over.items():
        base[s].update(v)
    return base


class Indicators(unittest.TestCase):
    def test_rsi_all_down_is_zero(self):
        self.assertEqual(S.rsi([10, 9, 8]), 0)

    def test_stretch_fires_on_deep_dip_above_200d(self):
        bars = [bar(100 + i * 0.05, h=100.5 + i * 0.05, l=99.5 + i * 0.05) for i in range(220)]
        bars.append(bar(107, h=109, l=106.9))
        f = S.facts(bars)
        self.assertTrue(f["above200"])
        self.assertTrue(f["stretch"])

    def test_no_signal_below_200d(self):
        bars = [bar(200 - i * 0.3) for i in range(220)]
        f = S.facts(bars)
        self.assertFalse(f["stretch"] or f["rsi2_sig"])


class Options(unittest.TestCase):
    def test_spread_buys_ask_sells_bid_within_budget(self):
        p = S.pick_spread(CHAIN, 50, 100)
        # 50/52 costs $110, over budget, so the long moves up a strike
        self.assertEqual((p["k1"], p["k2"]), (51, 53))
        self.assertAlmostEqual(p["debit"], (1.6 - 0.7) * 100)

    def test_single_call_when_no_spread_fits(self):
        p = S.pick_spread(CHAIN, 50, 45)
        self.assertIsNone(p["short"])
        self.assertLessEqual(p["debit"], 45)

    def test_value_closes_at_worse_side(self):
        pos = {"long": "X50", "short": "X52", "qty": 1}
        q = {c["symbol"]: c for c in CHAIN}
        self.assertAlmostEqual(S.spread_value(q, pos), (2.0 - 1.2) * 100)


class Step(unittest.TestCase):
    def test_learning_trade_when_nothing_fires(self):
        led = S.new_ledger("2026-10-26")
        S.step(led, "2026-10-26", mk())  # Monday: shares
        buys = [t for t in led["trades"] if t["action"] == "buy"]
        self.assertEqual(len(buys), 1)
        self.assertEqual(buys[0]["sleeve"], "QLD")  # lowest RSI(2)
        self.assertEqual(buys[0]["kind"], "learning")
        self.assertLessEqual(buys[0]["qty"] * buys[0]["price"], S.SHARES_MAX / 2 + 0.01)

    def test_tuesday_learning_trade_is_options(self):
        led = S.new_ledger("2026-10-27")
        S.step(led, "2026-10-27", mk(QLD={"chain": CHAIN}))
        self.assertEqual(led["trades"][0]["action"], "open spread")
        self.assertLess(led["sleeves"]["QLD"]["cash"], 200)

    def test_signal_buys_shares_and_spread_with_loss_caps(self):
        led = S.new_ledger("2026-10-26")
        S.step(led, "2026-10-26", mk(SSO={"under": under(stretch=True), "chain": CHAIN}))
        pos = led["sleeves"]["SSO"]["shares"]
        self.assertEqual(pos["kind"], "signal")
        self.assertLessEqual(pos["qty"] * (pos["entry"] - pos["stop"]), S.MAX_LOSS + 0.01)
        self.assertIsNotNone(led["sleeves"]["SSO"]["spread"])
        self.assertEqual(sum(t["kind"] == "learning" for t in led["trades"]), 0)

    def test_stop_and_target_exits(self):
        led = S.new_ledger("2026-10-26")
        S.step(led, "2026-10-26", mk())
        stop = led["sleeves"]["QLD"]["shares"]["stop"]
        S.step(led, "2026-10-27", mk(QLD={"etf": etf(low=stop - 1, open_=50)}))
        sells = [t for t in led["trades"] if t["action"] == "sell"]
        self.assertEqual(sells[0]["why"], "stop")
        self.assertLess(sells[0]["pnl"], 0)

    def test_learning_exit_above_prior_high(self):
        led = S.new_ledger("2026-10-26")
        S.step(led, "2026-10-26", mk())
        S.step(led, "2026-10-27", mk(QLD={"etf": etf(price=53, low=50, prev_high=52)}))
        sells = [t for t in led["trades"] if t["action"] == "sell"]
        self.assertTrue(sells and sells[0]["pnl"] > 0)

    def test_report_tracks_goal(self):
        led = S.new_ledger("2026-10-26")
        S.step(led, "2026-10-26", mk())
        text = S.report_text(led, "2026-10-26")
        self.assertIn("$210.00", text)  # 200 x 1.05 after one day
        self.assertIn("$216.00", text)


if __name__ == "__main__":
    unittest.main()
