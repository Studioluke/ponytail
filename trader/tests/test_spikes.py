import unittest
from datetime import datetime

from trader import spikes
from trader.spikes import ET


def snap(price, vol, prev=None, o=None, high=None, vw=None):
    return {"latestTrade": {"p": price, "t": "2026-10-23T15:00:00Z"},
            "dailyBar": {"o": o or price, "h": high or price, "c": price, "v": vol, "vw": vw or price},
            "prevDailyBar": {"c": prev or price}}


HIST = [{"t": f"2026-10-{d:02d}T04:00:00Z", "v": 100_000} for d in range(1, 21)]


class Spikes(unittest.TestCase):
    def test_session_fraction_floor_and_cap(self):
        self.assertAlmostEqual(spikes.session_fraction(datetime(2026, 10, 23, 9, 35, tzinfo=ET)), 30 / 390)
        self.assertEqual(spikes.session_fraction(datetime(2026, 10, 23, 17, 0, tzinfo=ET)), 1)

    def test_day_move_with_volume_alerts(self):
        a = spikes.evaluate("XYZ", 25.0, snap(12.5, 400_000, prev=10), HIST, [], 0.5)
        self.assertEqual(a["kind"], ["day move"])
        self.assertEqual(a["rvol"], 8.0)

    def test_quiet_volume_or_penny_stock_skipped(self):
        self.assertIsNone(spikes.evaluate("XYZ", 25.0, snap(12.5, 100_000), HIST, [], 1))   # 1x volume
        self.assertIsNone(spikes.evaluate("XYZ", 80.0, snap(1.5, 9_000_000), HIST, [], 1))  # under $2

    def test_burst_in_last_15_minutes(self):
        mins = [{"t": "2026-10-23T14:40:00Z", "c": 10.0}, {"t": "2026-10-23T14:58:00Z", "c": 10.7}]
        a = spikes.evaluate("XYZ", 6.0, snap(10.7, 300_000), HIST, mins, 1)
        self.assertEqual(a["kind"], ["15-min burst"])
        self.assertEqual(a["burst_15m"], 7.0)

    def test_risk_note_flags_fade_and_dilution(self):
        a = spikes.evaluate("XYZ", 60.0, snap(8.0, 900_000, prev=5, high=10, vw=9), HIST, [], 1)
        notes = spikes.risk_note(a, [{"headline": "XYZ prices $20M registered direct offering"}],
                                 datetime(2026, 10, 23, 17, 0, tzinfo=ET))
        text = " ".join(notes)
        for s in ("off the high", "below VWAP", "50%+", "dilution"):
            self.assertIn(s, text)

    def test_new_listing_without_history_skipped(self):
        self.assertIsNone(spikes.evaluate("NEW", 1200.0, snap(180, 900_000, prev=14), HIST[:2], [], 1))

    def test_leveraged_etfs_are_not_companies(self):
        self.assertTrue(spikes.FUND.search("Tradr 2X Long BE Daily ETF"))
        self.assertFalse(spikes.FUND.search("GrafTech International Ltd."))


if __name__ == "__main__":
    unittest.main()
