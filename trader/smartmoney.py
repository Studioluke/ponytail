"""Follow the smart money: insider (SEC Form 4) and congressional (STOCK Act) buys.

    python -m trader.smartmoney import insider FILE...    # merge scraped openinsider.com screener pages
    python -m trader.smartmoney import congress FILE...   # merge scraped capitoltrades.com trade pages
    python -m trader.smartmoney backtest [--hold 20]      # replay every filter on daily bars -> report.md
    python -m trader.smartmoney leaders [--source insider|congress]   # best filers by track record
    python -m trader.smartmoney signals [YYYY-MM-DD]      # fresh disclosures that pass the backtested filters
    python -m trader.smartmoney track [YYYY-MM-DD]        # forward paper test of every signal -> paper.md

SEC, the House clerk and the Senate eFD site are blocked from the cloud
sandbox, so the raw pages are fetched by the agent (Firecrawl) and imported
here; see trader/journal/smartmoney/README.md.

Every number is measured from the day a trade became public, never the day it
was made: entry is the open of the first session after the disclosure (Form 4
filings land after the close; congressional reports can arrive 45 days late),
exit is the close `hold` sessions later. "Excess" is that return minus SPY's
over the same days. Filer track records are walk-forward: when a trade is
scored, only that filer's earlier trades whose exits had already happened
count, so a "top filer" signal never uses future results.
"""
import argparse
import csv
import json
import os
import re
import sys
import time
from bisect import bisect_right
from collections import defaultdict
from datetime import date, datetime, timedelta
from statistics import mean, median

DIR = os.environ.get("TRADER_SMARTMONEY", "trader/journal/smartmoney")
CACHE = os.environ.get("TRADER_BAR_CACHE", os.path.expanduser("~/.cache/trader-bars"))
INSIDER_FIELDS = ["filed", "traded", "symbol", "insider", "insider_id", "title", "price", "value", "own_change", "url"]
CONGRESS_FIELDS = ["published", "traded", "symbol", "politician", "politician_id", "party", "chamber", "owner",
                   "price", "value", "gap_days", "tx_id"]
# A filer needs this many closed trades before their record counts, and this
# win rate (beat SPY) and average excess to be a "top filer".
MIN_RECORD, TOP_WIN, TOP_EXCESS = 3, 0.6, 0.0


# ---------------------------------------------------------------- import

def _num(s):
    s = re.sub(r"[^\d.\-]", "", s or "")
    return float(s) if s not in ("", "-", ".") else None


def parse_openinsider(text):
    """Rows of an openinsider.com screener table (markdown) -> purchase dicts."""
    out = []
    for line in text.splitlines():
        if 'SEC Form 4")' not in line or not line.startswith("|"):
            continue
        c = [x.strip() for x in line.split(" | ")]
        if len(c) < 17 or not c[7].startswith("P"):
            continue
        filed = re.search(r"\[(\d{4}-\d\d-\d\d) ?([\d:]*)\]\((\S+)", c[1])
        sym = re.search(r"\[([A-Z][A-Z.]*)\]", c[3])
        who = re.search(r"\[([^\]]+)\]\(http://openinsider\.com/insider/[^/]+/(\d+)", c[5])
        if not (filed and sym and who):
            continue
        out.append({"filed": f"{filed.group(1)} {filed.group(2)}".strip(), "traded": c[2], "symbol": sym.group(1),
                    "insider": who.group(1), "insider_id": who.group(2), "title": c[6],
                    "price": _num(c[8]), "value": _num(c[12]), "own_change": c[11], "url": filed.group(3)})
    return out


def parse_capitoltrades(text):
    """Trade records embedded in a capitoltrades.com /trades page (raw HTML) -> buy dicts."""
    out = []
    text = text.replace('\\"', '"')
    for m in re.finditer(r'\{"_issuerId":.*?"value":(?:\d+|null)\}', text):
        try:
            d = json.loads(m.group(0))
        except ValueError:
            continue
        ticker = (d.get("issuer") or {}).get("issuerTicker") or ""
        if d.get("txType") != "buy" or not ticker.endswith(":US"):
            continue
        p = d["politician"]
        out.append({"published": d["pubDate"][:10], "traded": d["txDate"], "symbol": ticker[:-3].replace("/", "."),
                    "politician": f"{p.get('nickname') or p['firstName']} {p['lastName']}",
                    "politician_id": d["_politicianId"], "party": p.get("party"), "chamber": d.get("chamber"),
                    "owner": d.get("owner"), "price": d.get("price"), "value": d.get("value"),
                    "gap_days": d.get("reportingGap"), "tx_id": d["_txId"]})
    return out


def _read_raw(path):
    with open(path) as f:
        raw = f.read()
    try:  # a saved Firecrawl result: {"markdown": ..., "rawHtml": ...}
        d = json.loads(raw)
        return "\n".join(str(d.get(k, "")) for k in ("markdown", "rawHtml"))
    except ValueError:
        return raw


def load(source, base=DIR):
    path = os.path.join(base, f"{source}.csv")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return list(csv.DictReader(f))


def merge(source, rows, base=DIR):
    fields, key = (INSIDER_FIELDS, "url") if source == "insider" else (CONGRESS_FIELDS, "tx_id")
    have = {r[key]: r for r in load(source, base)}
    before = len(have)
    for r in rows:
        have[str(r[key])] = {k: ("" if r.get(k) is None else r[k]) for k in fields}
    date_key = fields[0]
    os.makedirs(base, exist_ok=True)
    with open(os.path.join(base, f"{source}.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(sorted(have.values(), key=lambda r: (r[date_key], r[key]), reverse=True))
    return len(have) - before, len(have)


# ---------------------------------------------------------------- prices

def daily_bars(broker, symbols, start, end):
    """{symbol: [(date, open, close, volume)]} split/dividend adjusted, cached on disk per symbol."""
    os.makedirs(CACHE, exist_ok=True)
    out, need = {}, []
    for s in symbols:
        p = os.path.join(CACHE, f"{s}.json")
        if os.path.exists(p):
            with open(p) as f:
                d = json.load(f)
            if d["start"] <= start and d["end"] >= end and d.get("v") == 2:
                out[s] = [tuple(x) for x in d["bars"]]
                continue
        need.append(s)
    for i in range(0, len(need), 50):
        chunk = need[i:i + 50]
        got, feed = None, "sip"
        for attempt in range(8):
            try:
                got = _fetch(broker, chunk, start, end, feed)
                break
            except RuntimeError as e:
                if "429" in str(e):
                    time.sleep(min(2 ** attempt * 5, 60))  # data API allows 200 requests a minute
                elif "403" in str(e) and feed == "sip":
                    feed = "iex"  # free plans can't query the last 15 minutes of SIP
                else:
                    print(f"bars failed for {chunk[0]}..: {e}", file=sys.stderr)
                    break
        if got is None:
            continue  # leave uncached so the next run retries
        for s in chunk:
            bars = [(b["t"][:10], b["o"], b["c"], b["v"]) for b in got.get(s, [])]
            out[s] = bars
            with open(os.path.join(CACHE, f"{s}.json"), "w") as f:
                json.dump({"v": 2, "start": start, "end": end, "bars": bars}, f)
    return out


def _fetch(broker, symbols, start, end, feed):
    from .config import DATA_URL
    out, token = {}, None
    while True:
        params = {"symbols": ",".join(symbols), "timeframe": "1Day", "start": start, "end": end,
                  "feed": feed, "limit": 10000, "adjustment": "all"}
        if token:
            params["page_token"] = token
        d = broker._req("GET", f"{DATA_URL}/v2/stocks/bars", params=params)
        for s, bs in (d.get("bars") or {}).items():
            out.setdefault(s, []).extend(bs)
        token = d.get("next_page_token")
        if not token:
            return out


# ---------------------------------------------------------------- events

def events(source, base=DIR):
    """Normalised buys: who, symbol, public (date it became public), size, plus raw fields."""
    out = []
    for r in load(source, base):
        if source == "insider":
            public = r["filed"][:10]
            # Filed after the 16:00 close (or with no time): tradable next session either way.
            out.append({"who": r["insider"], "who_id": r["insider_id"], "symbol": r["symbol"], "public": public,
                        "traded": r["traded"], "value": float(r["value"] or 0), "role": role(r["title"]),
                        "title": r["title"]})
        else:
            out.append({"who": r["politician"], "who_id": r["politician_id"], "symbol": r["symbol"],
                        "public": r["published"], "traded": r["traded"], "value": float(r["value"] or 0),
                        "gap": int(r["gap_days"] or 0), "party": r["party"], "chamber": r["chamber"],
                        "owner": r["owner"]})
    return out


def role(title):
    t = (title or "").upper()
    if re.search(r"\bCEO\b|CHIEF EXEC|\bPRES\b|\bCFO\b|\bCOO\b|\bCOB\b|CHAIR", t):
        return "officer"
    if re.search(r"\bDIR\b|DIRECTOR", t):
        return "director"
    if "10%" in t:
        return "10% owner"
    return "other"


# Skip stocks we could not realistically trade: under $5, or under $5M a day
# traded over the 20 sessions before entry (spreads and gaps eat the edge).
MIN_PRICE, MIN_DOLLAR_VOLUME = 5.0, 5e6


def score(evts, bars, hold):
    """Attach entry/exit/return/excess to each event that has prices; drop the rest."""
    spy = bars.get("SPY") or []
    spy_ix = {b[0]: i for i, b in enumerate(spy)}
    out = []
    for e in evts:
        bs = bars.get(e["symbol"]) or []
        days = [b[0] for b in bs]
        i = bisect_right(days, e["public"])  # first session strictly after the disclosure date
        if i < 5 or i + hold - 1 >= len(bs):
            continue
        entry_d, entry = bs[i][0], bs[i][1]
        exit_d, exit_ = bs[i + hold - 1][0], bs[i + hold - 1][2]
        prior = bs[max(0, i - 20):i]
        if not entry or entry < MIN_PRICE or mean(b[2] * b[3] for b in prior) < MIN_DOLLAR_VOLUME:
            continue
        if entry_d not in spy_ix or exit_d not in spy_ix:
            continue
        s0, s1 = spy[spy_ix[entry_d]][1], spy[spy_ix[exit_d]][2]
        ret = exit_ / entry - 1
        out.append({**e, "entry_date": entry_d, "exit_date": exit_d, "ret": ret, "excess": ret - (s1 / s0 - 1)})
    return out


def add_cluster(scored, window=7):
    """Flag buys where 2+ different filers bought the same symbol within `window` days (as of disclosure)."""
    by_sym = defaultdict(list)
    for e in scored:
        by_sym[e["symbol"]].append(e)
    for es in by_sym.values():
        for e in es:
            d = date.fromisoformat(e["public"])
            others = {o["who_id"] for o in es if o["who_id"] != e["who_id"]
                      and timedelta(0) <= d - date.fromisoformat(o["public"]) <= timedelta(days=window)}
            e["cluster"] = len(others) + 1
    return scored


def add_record(scored):
    """Walk-forward filer record: stats over that filer's trades already exited before this entry."""
    by_who = defaultdict(list)
    for e in sorted(scored, key=lambda e: e["entry_date"]):
        past = [p for p in by_who[e["who_id"]] if p["exit_date"] < e["entry_date"]]
        if len(past) >= MIN_RECORD:
            e["rec_n"] = len(past)
            e["rec_win"] = sum(p["excess"] > 0 for p in past) / len(past)
            e["rec_excess"] = mean(p["excess"] for p in past)
        else:
            e["rec_n"], e["rec_win"], e["rec_excess"] = len(past), None, None
        by_who[e["who_id"]].append(e)
    return scored


def is_top(e):
    return e["rec_win"] is not None and e["rec_win"] >= TOP_WIN and e["rec_excess"] > TOP_EXCESS


FILTERS = {
    "insider": {
        "all $1M+ buys": lambda e: True,
        "officer (CEO/CFO/COO/Chair/Pres)": lambda e: e["role"] == "officer",
        "director": lambda e: e["role"] == "director",
        "10% owner": lambda e: e["role"] == "10% owner",
        "$5M+": lambda e: e["value"] >= 5e6,
        "cluster (2+ insiders in 7d)": lambda e: e["cluster"] >= 2,
        "officer + cluster": lambda e: e["role"] == "officer" and e["cluster"] >= 2,
        "top filer (walk-forward)": is_top,
    },
    "congress": {
        "all stock buys": lambda e: True,
        "$50K+": lambda e: e["value"] >= 50e3,
        "$250K+": lambda e: e["value"] >= 250e3,
        "reported within 10 days": lambda e: e["gap"] <= 10,
        "house": lambda e: e["chamber"] == "house",
        "senate": lambda e: e["chamber"] == "senate",
        "cluster (2+ members in 7d)": lambda e: e["cluster"] >= 2,
        "top filer (walk-forward)": is_top,
    },
}


def dedupe(scored):
    """One position per filer, symbol and entry day (a filer often reports one buy as several lots)."""
    seen, out = set(), []
    for e in scored:
        k = (e["who_id"], e["symbol"], e["entry_date"])
        if k not in seen:
            seen.add(k)
            out.append(e)
    return out


def stats(rows):
    if not rows:
        return None
    rets = [r["ret"] for r in rows]
    ex = [r["excess"] for r in rows]
    cut = len(ex) // 20  # 5% off each tail, so one moonshot can't carry a filter
    trimmed = sorted(ex)[cut:len(ex) - cut] or ex
    gains = sum(x for x in rets if x > 0)
    losses = -sum(x for x in rets if x < 0)
    return {"n": len(rows), "win": sum(x > 0 for x in rets) / len(rows), "beat_spy": sum(x > 0 for x in ex) / len(rows),
            "avg": mean(rets), "median": median(rets), "excess": mean(ex), "median_excess": median(ex), "trimmed_excess": mean(trimmed),
            "pf": gains / losses if losses else float("inf")}


def halves(rows):
    rows = sorted(rows, key=lambda r: r["entry_date"])
    mid = len(rows) // 2
    return rows[:mid], rows[mid:]


def passes(rows, min_n=30):
    """The bar a filter must clear before it can produce signals: same as the risk manager's
    strategy rule (two separate periods, both profitable), a positive edge over SPY in each,
    and a positive edge that survives trimming the 5% best and worst trades."""
    if len(rows) < min_n:
        return False
    a, b = (stats(h) for h in halves(rows))
    return all(s and s["pf"] > 1 and s["excess"] > 0 for s in (a, b)) and stats(rows)["trimmed_excess"] > 0


ALT_HOLDS = (5, 60)


def run_backtest(broker, hold=20, base=DIR):
    results = {}
    for source in ("insider", "congress"):
        evts = events(source, base)
        if not evts:
            continue
        syms = sorted({e["symbol"] for e in evts} | {"SPY"})
        start = min(e["public"] for e in evts)
        end = (date.today() - timedelta(days=1)).isoformat()  # SIP needs data 15+ min old
        bars = daily_bars(broker, syms, start, end)
        scored = add_record(add_cluster(dedupe(score(evts, bars, hold))))
        # Same filters at a shorter and a longer hold, to see whether the edge depends on the exit.
        alt = {h: add_record(add_cluster(dedupe(score(evts, bars, h)))) for h in ALT_HOLDS}
        res = {}
        for name, f in FILTERS[source].items():
            rows = [e for e in scored if f(e)]
            a, b = halves(rows)
            alt_stats = {str(h): stats([e for e in alt[h] if f(e)]) for h in ALT_HOLDS}
            # An edge that only exists at one exit day is likely luck, so it must also be
            # positive (on average) at the shorter and longer holds.
            robust = all(x and x["excess"] > 0 for x in alt_stats.values())
            res[name] = {"all": stats(rows), "first": stats(a), "second": stats(b),
                         "passes": passes(rows) and robust, "alt": alt_stats}
        results[source] = {"events": len(evts), "scored": len(scored), "hold": hold, "filters": res,
                           "leaders": leaders(scored),
                           # every filer's full-sample record, for scoring live signals
                           "records": leaders(scored, top=10 ** 6), "span": [min(e["entry_date"] for e in scored),
                                                                max(e["entry_date"] for e in scored)] if scored else None}
    return results


def leaders(scored, min_n=MIN_RECORD, top=15):
    by = defaultdict(list)
    for e in scored:
        by[(e["who_id"], e["who"])].append(e)
    rows = []
    for (wid, who), es in by.items():
        if len(es) < min_n:
            continue
        s = stats(es)
        rows.append({"who": who, "id": wid, **s, "symbols": sorted({e["symbol"] for e in es})[:6],
                     "dollars": sum(e["value"] for e in es)})
    rows.sort(key=lambda r: (r["beat_spy"], r["excess"]), reverse=True)
    return rows[:top]


def _pct(x):
    return "n/a" if x is None else f"{x * 100:+.1f}%"


def report(results):
    lines = ["# Smart-money backtest", "",
             f"Generated {datetime.now():%Y-%m-%d %H:%M}. Entry: open of the first session after the trade became public. "
             "Exit: close after the hold. Excess = return minus SPY over the same days. Win = return > 0. "
             "Only stocks at $5+ with $5M+ average daily dollar volume. A filter **passes** when it has 30+ trades, both halves (by date) have profit factor > 1 and positive excess, excess stays positive with the best and worst 5% of trades trimmed, and average excess is also positive at the 5- and 60-session holds.", ""]
    for source, r in results.items():
        lines += [f"## {source.title()} ({r['scored']} scored of {r['events']} disclosures, hold {r['hold']} sessions, "
                  f"entries {r['span'][0]} to {r['span'][1]})" if r["span"] else f"## {source.title()}", "",
                  "| Filter | Trades | Win | Beat SPY | Avg | Median | Avg excess | Trimmed excess | PF | 1st half excess | 2nd half excess | Passes |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for name, f in r["filters"].items():
            s = f["all"]
            if not s:
                lines.append(f"| {name} | 0 | | | | | | | | | | no |")
                continue
            lines.append(f"| {name} | {s['n']} | {s['win']:.0%} | {s['beat_spy']:.0%} | {_pct(s['avg'])} | {_pct(s['median'])} | "
                         f"{_pct(s['excess'])} | {_pct(s['trimmed_excess'])} | {s['pf']:.2f} | {_pct(f['first'] and f['first']['excess'])} | "
                         f"{_pct(f['second'] and f['second']['excess'])} | {'**yes**' if f['passes'] else 'no'} |")
        lines += ["", "Same filters held " + " and ".join(f"{h}" for h in ALT_HOLDS) + " sessions (avg excess, beat-SPY rate, trades):", "",
                  "| Filter | " + " | ".join(f"{h}d" for h in ALT_HOLDS) + " |", "|---" * (len(ALT_HOLDS) + 1) + "|"]
        for name, f in r["filters"].items():
            cells = [f"{_pct(x['excess'])}, {x['beat_spy']:.0%}, {x['n']}" if x else "n/a"
                     for x in (f["alt"].get(str(h)) for h in ALT_HOLDS)]
            lines.append(f"| {name} | " + " | ".join(cells) + " |")
        lines += ["", f"Top {source} filers by beat-SPY rate (3+ scored buys; in-sample, so a leaderboard, not a forecast):", "",
                  "| Filer | Buys | Win | Beat SPY | Avg excess | $ disclosed | Symbols |", "|---|---|---|---|---|---|---|"]
        for l in r["leaders"]:
            lines.append(f"| {l['who']} | {l['n']} | {l['win']:.0%} | {l['beat_spy']:.0%} | {_pct(l['excess'])} | "
                         f"${l['dollars'] / 1e6:,.1f}M | {', '.join(l['symbols'])} |")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- signals

def signals(day, base=DIR, lookback=3, results=None):
    """Disclosures from the last `lookback` days that match a filter which passed the backtest."""
    results = results or _load_results(base)
    out = []
    for source in ("insider", "congress"):
        passing = [n for n, f in ((results.get(source) or {}).get("filters") or {}).items() if f["passes"]]
        if not passing:
            continue
        evts = add_cluster(events(source, base))
        _record_from_results(evts, results.get(source, {}))
        lo = (date.fromisoformat(day) - timedelta(days=lookback)).isoformat()
        for e in evts:
            if not (lo <= e["public"] <= day):
                continue
            hits = [n for n in passing if n != FILTERS_ALL[source] and FILTERS[source][n](e)]
            # A filer whose own buys have mostly lagged SPY is not smart money, whatever the filter says.
            if hits and not (e["rec_win"] is not None and e["rec_win"] < 0.4):
                out.append({"source": source, "symbol": e["symbol"], "who": e["who"], "public": e["public"],
                            "value": e["value"], "filters": hits})
    by_sym = {}
    for s in out:
        by_sym.setdefault(s["symbol"], {"symbol": s["symbol"], "buys": []})["buys"].append(s)
    return sorted(by_sym.values(), key=lambda x: -sum(b["value"] for b in x["buys"]))


FILTERS_ALL = {"insider": "all $1M+ buys", "congress": "all stock buys"}


def _record_from_results(evts, res):
    rec = {l["id"]: l for l in res.get("records", [])}
    for e in evts:
        r = rec.get(e["who_id"])
        e["rec_n"], e["rec_win"], e["rec_excess"] = (r["n"], r["beat_spy"], r["excess"]) if r else (0, None, None)


def _load_results(base):
    p = os.path.join(base, "backtest.json")
    if not os.path.exists(p):
        return {}
    with open(p) as f:
        return json.load(f)


def liquid(broker, symbols, day):
    """Symbols that meet the backtest's price and dollar-volume floor over the last 20 sessions."""
    start = (date.fromisoformat(day) - timedelta(days=40)).isoformat()
    end = (date.fromisoformat(day) - timedelta(days=1)).isoformat()
    ok = set()
    for s, bs in daily_bars(broker, sorted(symbols), start, end).items():
        last = bs[-20:]
        if last and last[-1][2] >= MIN_PRICE and mean(b[2] * b[3] for b in last) >= MIN_DOLLAR_VOLUME:
            ok.add(s)
    return ok


def write_signals(day, base=DIR, broker=None):
    sig = signals(day, base)
    if sig and broker is not None:
        keep = liquid(broker, {x["symbol"] for x in sig}, day)
        sig = [x for x in sig if x["symbol"] in keep]
    with open(os.path.join(base, f"{day}.json"), "w") as f:
        json.dump({"date": day, "signals": sig}, f, indent=1)
    return sig


# ---------------------------------------------------------------- forward paper test

PAPER_FIELDS = ["signal_date", "symbol", "who", "source", "filters", "entry_date", "entry", "exit_date", "exit",
                "ret", "spy_ret", "excess", "status"]


def track(broker, today, base=DIR, hold=20):
    """Forward-test every signal file on paper: buy at the next open, sell at the close `hold`
    sessions later, compare with SPY. No orders are placed anywhere."""
    path = os.path.join(base, "paper.csv")
    rows = []
    if os.path.exists(path):
        with open(path) as f:
            rows = list(csv.DictReader(f))
    have = {(r["signal_date"], r["symbol"]) for r in rows}
    for name in sorted(os.listdir(base)):
        if not re.fullmatch(r"\d{4}-\d\d-\d\d\.json", name):
            continue
        with open(os.path.join(base, name)) as f:
            d = json.load(f)
        for x in d.get("signals", []):
            if (d["date"], x["symbol"]) not in have:
                b = x["buys"][0]
                rows.append({"signal_date": d["date"], "symbol": x["symbol"], "who": b["who"], "source": b["source"],
                             "filters": "; ".join(b["filters"]), "status": "pending"})
    live = [r for r in rows if r["status"] != "closed"]
    if live:
        start = min(r["signal_date"] for r in live)
        bars = daily_bars(broker, sorted({r["symbol"] for r in live} | {"SPY"}), start, today)
        spy = {b[0]: b for b in bars.get("SPY", [])}
        for r in live:
            bs = [b for b in bars.get(r["symbol"], []) if b[0] > r["signal_date"]]
            if not bs:
                continue
            r.update(entry_date=bs[0][0], entry=bs[0][1], status="open")
            if len(bs) >= hold and bs[0][0] in spy and bs[hold - 1][0] in spy:
                x = bs[hold - 1]
                ret = x[2] / bs[0][1] - 1
                spy_ret = spy[x[0]][2] / spy[bs[0][0]][1] - 1
                r.update(exit_date=x[0], exit=x[2], ret=round(ret, 4), spy_ret=round(spy_ret, 4),
                         excess=round(ret - spy_ret, 4), status="closed")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PAPER_FIELDS)
        w.writeheader()
        w.writerows(rows)
    closed = [r for r in rows if r["status"] == "closed"]
    lines = [f"# Smart-money forward paper test ({today})", "",
             f"Signals: {len(rows)}; open or pending: {len(rows) - len(closed)}; closed: {len(closed)}.", ""]
    if closed:
        ex = [float(r["excess"]) for r in closed]
        lines += [f"Closed: win {sum(float(r['ret']) > 0 for r in closed) / len(closed):.0%}, beat SPY "
                  f"{sum(x > 0 for x in ex) / len(ex):.0%}, avg excess {_pct(mean(ex))}.", ""]
    lines += ["| Signal | Symbol | Filer | Filters | Entry | Exit | Return | Excess | Status |", "|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: r["signal_date"], reverse=True):
        lines.append(f"| {r['signal_date']} | {r['symbol']} | {r['who']} | {r['filters']} | {r.get('entry_date') or ''} "
                     f"{r.get('entry') or ''} | {r.get('exit_date') or ''} {r.get('exit') or ''} | "
                     f"{_pct(float(r['ret'])) if r.get('ret') else ''} | {_pct(float(r['excess'])) if r.get('excess') else ''} | {r['status']} |")
    with open(os.path.join(base, "paper.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    return rows


# ---------------------------------------------------------------- CLI

def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m trader.smartmoney")
    sub = ap.add_subparsers(dest="cmd", required=True)
    im = sub.add_parser("import")
    im.add_argument("source", choices=["insider", "congress"])
    im.add_argument("files", nargs="+")
    bt = sub.add_parser("backtest")
    bt.add_argument("--hold", type=int, default=20)
    ld = sub.add_parser("leaders")
    ld.add_argument("--source", choices=["insider", "congress"], default="insider")
    sg = sub.add_parser("signals")
    sg.add_argument("day", nargs="?", default=date.today().isoformat())
    tr = sub.add_parser("track")
    tr.add_argument("day", nargs="?", default=date.today().isoformat())
    a = ap.parse_args(argv)

    if a.cmd == "import":
        parse = parse_openinsider if a.source == "insider" else parse_capitoltrades
        rows = [r for p in a.files for r in parse(_read_raw(p))]
        added, total = merge(a.source, rows)
        print(f"{a.source}: parsed {len(rows)}, {added} new, {total} total")
    elif a.cmd == "backtest":
        from .broker import Broker
        res = run_backtest(Broker(), a.hold)
        with open(os.path.join(DIR, "backtest.json"), "w") as f:
            json.dump(res, f, indent=1)
        md = report(res)
        with open(os.path.join(DIR, "report.md"), "w") as f:
            f.write(md + "\n")
        print(md)
    elif a.cmd == "leaders":
        res = _load_results(DIR).get(a.source) or {}
        for l in res.get("leaders", []):
            print(f"{l['who']:<40} n={l['n']:>3} win={l['win']:.0%} beatSPY={l['beat_spy']:.0%} excess={_pct(l['excess'])}")
    elif a.cmd == "signals":
        from .broker import Broker
        sig = write_signals(a.day, broker=Broker())
        for s in sig:
            print(s["symbol"], "; ".join(f"{b['who']} ${b['value']:,.0f} ({', '.join(b['filters'])})" for b in s["buys"]))
        if not sig:
            print("no fresh disclosures pass a backtested filter")
    elif a.cmd == "track":
        from .broker import Broker
        rows = track(Broker(), a.day)
        print(f"{len(rows)} paper signals; see {os.path.join(DIR, 'paper.md')}")


if __name__ == "__main__":
    main()
