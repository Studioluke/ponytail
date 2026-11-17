import unittest
from datetime import datetime

from trader import gappers
from trader.gappers import ET

OPEN = datetime(2026, 10, 29, 9, 30, tzinfo=ET)


def bar(minute, o, h, l, c, v=10_000):
    t = datetime(2026, 10, 29, 13, 30 + minute).strftime("%Y-%m-%dT%H:%M:00Z")  # UTC = ET + 4h
    return {"t": t, "o": o, "h": h, "l": l, "c": c, "v": v}


class Gappers(unittest.TestCase):
    def test_breakout_above_opening_range(self):
        mins = [bar(i, 117, 120, 115, 118) for i in range(5)] + [bar(6, 119, 123, 119, 122)]
        a = gappers.evaluate("GK", 100, mins, OPEN, 5)
        self.assertEqual((a["gap"], a["orh"], a["stop"], a["breaking"]), (17.0, 120, 115, True))

    def test_inside_range_is_watch_and_small_gap_skipped(self):
        mins = [bar(i, 117, 120, 115, 118) for i in range(6)]
        self.assertFalse(gappers.evaluate("GK", 100, mins, OPEN, 5)["breaking"])
        self.assertIsNone(gappers.evaluate("GK", 113, mins, OPEN, 5))  # +3.5% gap

    def test_earnings_tag(self):
        self.assertTrue(gappers.EARNINGS.search("Crocs Reports Third Quarter 2026 Financial Results"))
        self.assertFalse(gappers.EARNINGS.search("US Economy Grew 3.4% in the Third Quarter"))


if __name__ == "__main__":
    unittest.main()
