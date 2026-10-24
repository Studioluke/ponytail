import unittest

from trader import intraday_lab as I
from trader import options_lab as O
from trader import patterns as P
from trader import screener as S


def b(o, h, l, c, v=1000, t="2020-01-01"):
    return {"t": f"{t}T05:00:00Z", "o": o, "h": h, "l": l, "c": c, "v": v}


def series(closes):
    return [b(c, c * 1.01, c * 0.99, c, t=f"2020-{1 + k // 28:02d}-{1 + k % 28:02d}") for k, c in enumerate(closes)]


class CandleTest(unittest.TestCase):
    def test_hammer_has_long_lower_whisker(self):
        self.assertTrue(P.is_hammer(b(100, 100.5, 96, 100.3)))
        self.assertFalse(P.is_hammer(b(100, 104, 99.5, 100.3)))  # long upper wick: shooting star

    def test_bull_engulfing(self):
        self.assertTrue(P.is_bull_engulfing(b(101, 101.5, 99.5, 100), b(99.8, 102, 99.5, 101.5)))
        self.assertFalse(P.is_bull_engulfing(b(100, 101.5, 99.5, 101), b(99.8, 102, 99.5, 101.5)))

    def test_ibs(self):
        self.assertAlmostEqual(P.ibs(b(100, 110, 100, 101)), 0.1)


class IndicatorTest(unittest.TestCase):
    def test_sma(self):
        self.assertEqual(P.sma([1, 2, 3, 4], 2), [None, 1.5, 2.5, 3.5])

    def test_rsi_extremes(self):
        self.assertEqual(P.rsi([1, 2, 3, 4, 5], 2)[-1], 100.0)
        self.assertLess(P.rsi([5, 4, 3, 2, 1], 2)[-1], 1)


class EngineTest(unittest.TestCase):
    def test_dip_in_uptrend_is_bought_and_sold_on_recovery(self):
        closes = [100 + 0.2 * k for k in range(230)] + [140, 150]
        bars = series(closes)
        entry, exit_fn, hold, stop = P.RULES["RSI2<10 above 200d, exit >5d avg"]
        trades = P.run_rule(bars, entry, exit_fn, hold, stop)
        self.assertTrue(trades)
        self.assertGreater(trades[-1]["ret"], 0)
        self.assertEqual(trades[-1]["how"], "rule")

    def test_stats(self):
        s = P.stats([{"ret": 0.02, "days": 1}, {"ret": -0.01, "days": 1}])
        self.assertEqual((s["n"], s["win"]), (2, 0.5))
        self.assertAlmostEqual(s["pf"], 2.0)


class OptionsTest(unittest.TestCase):
    def test_call_price_and_strike(self):
        self.assertAlmostEqual(O.bs_call(100, 100, 0, 0.3), 0)
        k = O.strike_for_delta(100, 35 / 365, 0.3, 0.7)
        self.assertLess(k, 100)  # a 0.70 delta call is in the money
        self.assertGreater(O.bs_call(100, k, 35 / 365, 0.3), 100 - k)


class IntradayTest(unittest.TestCase):
    def test_walk_stop_before_target_on_same_bar(self):
        from datetime import time
        day = [{"o": 100, "h": 100, "l": 100, "c": 100, "et": time(9, 30)},
               {"o": 100, "h": 103, "l": 98, "c": 100, "et": time(9, 35)}]
        self.assertEqual(I.walk(day, 0, 100, 99, 102), (99, "stop"))


class ScreenerTest(unittest.TestCase):
    def test_plan_row_for_firing_setup(self):
        bars = series([100 + 0.2 * k for k in range(240)])
        row = {"sym": "X", "fit": True, "score": 90, "bars": bars,
               "t": {"fires": [S.STRETCH], "close": 147.8, "date": "2020-09-30"}}
        out = S.plan_rows([row], existing=[])
        self.assertEqual(out[0]["symbol"], "X")
        self.assertLess(out[0]["stop"], out[0]["entry_low"])
        self.assertEqual(S.plan_rows([row], existing=[{"symbol": "X"}]), [])


if __name__ == "__main__":
    unittest.main()
