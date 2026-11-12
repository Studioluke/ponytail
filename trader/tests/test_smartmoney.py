import json
import os
import tempfile
import unittest

from trader import research, smartmoney as sm

OI_ROW = ('| M | [2026-05-29 17:23:07](http://www.sec.gov/Archives/edgar/data/1/0001/form4.xml "SEC Form 4") | '
          '2026-05-28 | **[ABC](http://openinsider.com/ABC)** | [Abc Corp](http://openinsider.com/ABC) | '
          '[Doe Jane](http://openinsider.com/insider/Doe-Jane/42 "x") | CEO, Dir | P - Purchase | $10.50 | +100,000 | '
          '500,000 | +25% | +$1,050,000 |  |  |  |  |')
CT_HTML = ('{\\"_issuerId\\":1,\\"_politicianId\\":\\"X1\\",\\"_txId\\":9,\\"chamber\\":\\"senate\\",'
           '\\"issuer\\":{\\"issuerName\\":\\"Berkshire\\",\\"issuerTicker\\":\\"BRK/B:US\\"},\\"owner\\":\\"self\\",'
           '\\"politician\\":{\\"firstName\\":\\"Ann\\",\\"lastName\\":\\"Lee\\",\\"nickname\\":null,\\"party\\":\\"democrat\\"},'
           '\\"price\\":500,\\"pubDate\\":\\"2026-10-01T13:00:00Z\\",\\"reportingGap\\":20,\\"txDate\\":\\"2026-09-11\\",'
           '\\"txType\\":\\"buy\\",\\"txTypeExtended\\":null,\\"value\\":8000}')


def bars(days, start=100.0, step=1.0, vol=1e6):
    """Daily bars on consecutive dates 2026-01-01.., open == close, price rising by `step`."""
    return [(f"2026-01-{d:02d}", start + step * i, start + step * i, vol) for i, d in enumerate(days)]


class Parsing(unittest.TestCase):
    def test_openinsider_row(self):
        r = sm.parse_openinsider(OI_ROW)[0]
        self.assertEqual((r["symbol"], r["insider"], r["insider_id"], r["value"]), ("ABC", "Doe Jane", "42", 1050000))
        self.assertEqual(r["filed"], "2026-05-29 17:23:07")
        self.assertEqual(sm.role(r["title"]), "officer")

    def test_capitoltrades_record(self):
        r = sm.parse_capitoltrades(CT_HTML)[0]
        self.assertEqual((r["symbol"], r["politician"], r["published"], r["chamber"]), ("BRK.B", "Ann Lee", "2026-10-01", "senate"))

    def test_merge_dedupes(self):
        with tempfile.TemporaryDirectory() as d:
            rows = sm.parse_openinsider(OI_ROW)
            self.assertEqual(sm.merge("insider", rows, d), (1, 1))
            self.assertEqual(sm.merge("insider", rows, d), (0, 1))

    def test_merge_mixes_new_and_stored_rows(self):
        with tempfile.TemporaryDirectory() as d:
            sm.merge("congress", sm.parse_capitoltrades(CT_HTML), d)
            other = CT_HTML.replace('_txId\\":9', '_txId\\":10')
            self.assertEqual(sm.merge("congress", sm.parse_capitoltrades(other), d), (1, 2))


class Scoring(unittest.TestCase):
    def setUp(self):
        days = list(range(1, 31))
        self.bars = {"SPY": bars(days, 100, 0), "ABC": bars(days, 100, 1)}
        self.evt = {"who": "Doe", "who_id": "1", "symbol": "ABC", "public": "2026-01-10", "value": 1e6}

    def test_entry_is_next_session_open(self):
        e = sm.score([self.evt], self.bars, hold=5)[0]
        self.assertEqual((e["entry_date"], e["exit_date"]), ("2026-01-11", "2026-01-15"))
        self.assertAlmostEqual(e["ret"], 114 / 110 - 1)
        self.assertAlmostEqual(e["excess"], e["ret"])  # SPY flat

    def test_illiquid_or_cheap_skipped(self):
        thin = {**self.bars, "ABC": bars(range(1, 31), 100, 1, vol=10)}
        self.assertEqual(sm.score([self.evt], thin, 5), [])
        cheap = {**self.bars, "ABC": bars(range(1, 31), 2, 0, vol=1e9)}
        self.assertEqual(sm.score([self.evt], cheap, 5), [])

    def test_record_is_walk_forward(self):
        mk = lambda i, ex: {"who_id": "1", "entry_date": f"2026-02-{i:02d}", "exit_date": f"2026-02-{i + 2:02d}", "excess": ex}
        rows = sm.add_record([mk(1, .1), mk(2, .1), mk(3, .1), mk(4, -.1), mk(10, .1)])
        # The 4th trade enters before the 3rd exits, so only 2 trades count: no record yet.
        self.assertIsNone(rows[3]["rec_win"])
        self.assertEqual(rows[4]["rec_n"], 4)
        self.assertAlmostEqual(rows[4]["rec_win"], 0.75)

    def test_passes_needs_both_halves(self):
        good = [{"entry_date": f"2026-{m:02d}-01", "ret": .02, "excess": .01} for m in range(1, 13)] * 3
        self.assertTrue(sm.passes(good))
        bad = [dict(r, ret=-.02, excess=-.01) if r["entry_date"] >= "2026-07" else r for r in good]
        self.assertFalse(sm.passes(bad))
        self.assertFalse(sm.passes(good[:10]))


class Brief(unittest.TestCase):
    def test_research_reads_latest_signals(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "2026-10-22.json"), "w") as f:
                json.dump({"signals": [{"symbol": "ABC", "buys": []}]}, f)
            from datetime import date
            self.assertEqual(research.load_smart_money(date(2026, 10, 24), d)[0]["symbol"], "ABC")
            self.assertEqual(research.load_smart_money(date(2026, 10, 30), d), [])


if __name__ == "__main__":
    unittest.main()
