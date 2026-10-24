import unittest

from trader.swing import simulate

PLAN = [{"symbol": "X", "active_from": "2026-10-26", "exit_by": "2026-10-30",
         "entry_low": 95.0, "entry_high": 100.0, "stop": 90.0, "target": 110.0}]


def bar(d, o, h, l, c):
    return {"t": f"2026-10-{d}T04:00:00Z", "o": o, "h": h, "l": l, "c": c}


class SwingTest(unittest.TestCase):
    def test_entry_then_target(self):
        res = simulate(PLAN, {"X": [bar(26, 104, 105, 99, 102), bar(27, 103, 111, 102, 108)]})
        t = res["trades"][0]
        self.assertEqual((t["entry"], t["exit"], t["why"]), (100.0, 110.0, "target"))
        self.assertAlmostEqual(t["qty"], 2.0)  # $200 position / $100
        self.assertAlmostEqual(res["equity"], 1020.0)

    def test_loss_capped_at_max_loss(self):
        wide = [{**PLAN[0], "stop": 50.0}]
        res = simulate(wide, {"X": [bar(26, 100, 101, 40, 45)]})
        self.assertAlmostEqual(res["trades"][0]["pnl"], -50.0)

    def test_same_day_stop_and_target_counts_as_stop(self):
        res = simulate(PLAN, {"X": [bar(26, 98, 112, 89, 100)]})
        self.assertEqual(res["trades"][0]["why"], "stop")
        self.assertAlmostEqual(res["equity"], 1000 - 200 / 98 * 8)  # in at the 98 open, out at 90

    def test_never_enters_above_zone_and_time_exit(self):
        self.assertEqual(simulate(PLAN, {"X": [bar(26, 104, 106, 101, 105)]})["trades"], [])
        res = simulate(PLAN, {"X": [bar(29, 99, 101, 97, 100), bar(30, 100, 104, 99, 103)]})
        self.assertEqual(res["trades"][0]["why"], "time")


    def test_reenters_after_exit(self):
        res = simulate(PLAN, {"X": [bar(26, 99, 111, 98, 110), bar(27, 99, 100, 97, 98)]})
        self.assertEqual(res["trades"][0]["why"], "target")
        self.assertIn("X", res["open"])


if __name__ == "__main__":
    unittest.main()
