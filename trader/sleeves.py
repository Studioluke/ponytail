"""Four $200 ETF sleeves: swing trades in shares plus call debit spreads, on paper.

Luke, 2026-10-24: swing trade and trade options on 4 ETFs, $200 each, scan the
market and each ETF's news before the open, trade every day, goal +5-8% a day.
Paper only. The goal is tracked as a stretch target next to the real numbers.

    python -m trader.sleeves scan     # premarket: trend, triggers, news, events
    python -m trader.sleeves trade    # ~15:45 ET: exits, entries, daily trade
    python -m trader.sleeves report   # writes trader/journal/sleeves/report.md

Fills are simulated against live Alpaca quotes and kept in a ledger. The
shared Alpaca paper account is flattened by the day trader at 15:45 and its
risk manager counts every position against the $300 limits, so real orders
there would be closed the same day and would block the day trader. Options
fills are deliberately pessimistic: buy at the ask, sell at the bid, on every
leg (Alpaca's free options feed is indicative, and spreads on these ETFs run
10-30% of the premium).

Setups (from trader/journal/notes/trading-playbook.md, signals on the underlying):
    STRETCH   above 200d, close < 10d avg - 2 ATR, IBS < 0.25; exit first close
              above the 5d avg, max 10 days
    RSI2      above 200d, RSI(2) < 5, IBS < 0.2; same exit
A signal buys shares (up to $150, stop 2.5 ETF ATR, max loss $50) and a call
debit spread or, if none fits, a single call (premium up to $100, -50% stop).
If nothing was bought by the run, one "learning trade" is taken (Luke: no day
without a trade): the flat sleeve whose underlying has the lowest RSI(2), at
half size for shares. Tue/Thu it is a debit spread, other days shares (stop 1.5 ATR, exit
on a close above the prior day's high, max 5 days).
"""
import json
import os
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from .config import DATA_URL

ET = ZoneInfo("America/New_York")
DIR = "trader/journal/sleeves"
LEDGER = f"{DIR}/ledger.json"
EVENTS = "trader/journal/research/events.csv"
START_CASH = 200.0
GOAL_LO, GOAL_HI = 0.05, 0.08
SHARES_MAX, MAX_LOSS = 150.0, 50.0
# Option premium cap. $50 buys nothing near the money on these ETFs once the
# bid-ask spread is paid, so options get up to $100 with a -50% stop; a gap can
# still lose the whole premium.
SPREAD_MAX = 100.0
# Skip options that would lose more than 30% of the premium if sold straight
# back (2026-10-27: a QLD 95/97C paid $99 and was worth $26 at the bid/ask).
MIN_BACK = 0.7
SLIP = 0.0005  # shares, each side
SLEEVES = {
    "QLD": {"under": "QQQ", "name": "2x Nasdaq 100",
            "holdings": ["NVDA", "MSFT", "AAPL", "AMZN", "GOOGL", "META", "AVGO", "TSLA"]},
    "SSO": {"under": "SPY", "name": "2x S&P 500",
            "holdings": ["NVDA", "MSFT", "AAPL", "AMZN", "META", "GOOGL", "AVGO", "BRK.B"]},
    "USD": {"under": "SMH", "name": "2x semiconductors",
            "holdings": ["NVDA", "AVGO", "AMD", "QCOM", "TXN", "MU", "INTC", "AMAT"]},
    "NVDL": {"under": "NVDA", "name": "2x Nvidia", "holdings": ["NVDA"]},
}


# indicators (lists of daily bars {'o','h','l','c'}, oldest first)

def sma(xs, n):
    return sum(xs[-n:]) / n if len(xs) >= n else None


def atr(bars, n=14):
    if len(bars) < n + 1:
        return None
    trs = [max(b["h"] - b["l"], abs(b["h"] - p["c"]), abs(b["l"] - p["c"])) for p, b in zip(bars[-n - 1:-1], bars[-n:])]
    return sum(trs) / n


def rsi(closes, n=2):
    if len(closes) < n + 1:
        return None
    up = dn = 0.0
    for a, b in zip(closes[-n - 1:-1], closes[-n:]):
        up += max(b - a, 0)
        dn += max(a - b, 0)
    return 100.0 if dn == 0 else 100 - 100 / (1 + up / dn)


def ibs(b):
    return (b["c"] - b["l"]) / (b["h"] - b["l"]) if b["h"] > b["l"] else 0.5


def facts(bars):
    """Signal inputs from bars whose last entry is today (provisional at the run)."""
    closes = [b["c"] for b in bars]
    b, a = bars[-1], atr(bars)
    f = {"close": b["c"], "sma200": sma(closes, 200), "sma10": sma(closes, 10), "sma5": sma(closes, 5),
         "atr": a, "rsi2": rsi(closes), "ibs": ibs(b)}
    up = f["sma200"] is not None and b["c"] > f["sma200"]
    f["stretch"] = bool(up and a and b["c"] < f["sma10"] - 2 * a and f["ibs"] < 0.25)
    f["rsi2_sig"] = bool(up and f["rsi2"] is not None and f["rsi2"] < 5 and f["ibs"] < 0.2)
    f["above200"] = up
    return f


# options

def pick_spread(chain, price, budget):
    """A call debit spread that fits the budget, else a single call.
    chain: [{'symbol','strike','bid','ask'}] for one expiry. Long leg from the
    money to 8% out, nearest first, short leg as wide as the budget allows,
    never paying over 65% of the width. Buys at the ask, sells at the bid.
    If no spread fits, the nearest call up to 12% out whose ask fits.
    Returns None when nothing fits."""
    calls = sorted((c for c in chain if c["ask"] > 0), key=lambda c: c["strike"])
    for lg in (c for c in calls if price * 0.99 <= c["strike"] <= price * 1.08):
        best = None
        for sh in calls:
            if sh["strike"] <= lg["strike"] or sh["bid"] < 0.05:
                continue
            debit = (lg["ask"] - sh["bid"]) * 100
            width = (sh["strike"] - lg["strike"]) * 100
            back = (lg["bid"] - sh["ask"]) * 100  # what selling it straight back would bring
            if 0 < debit <= budget and debit <= 0.65 * width and back >= MIN_BACK * debit:
                best = {"long": lg["symbol"], "short": sh["symbol"], "k1": lg["strike"], "k2": sh["strike"],
                        "debit": round(debit, 2), "width": width}
        if best:
            return best
    for c in calls:
        if price * 0.99 <= c["strike"] <= price * 1.12 and c["ask"] * 100 <= budget and c["bid"] >= MIN_BACK * c["ask"]:
            return {"long": c["symbol"], "short": None, "k1": c["strike"], "k2": None,
                    "debit": round(c["ask"] * 100, 2), "width": None}
    return None


def label(p):
    return f"{p['k1']:g}C" if p["short"] is None else f"{p['k1']:g}/{p['k2']:g}C"


def spread_value(quotes, pos, mid=False):
    """What closing now would bring: sell the long at its bid, buy back the short at
    its ask. mid=True gives the mid-quote value, which the exit rules watch, so the
    bid-ask haircut alone can't trigger the stop."""
    lq = quotes.get(pos["long"])
    sq = quotes.get(pos["short"]) if pos["short"] else {"bid": 0.0, "ask": 0.0}
    if not lq or not sq:
        return None
    if mid:
        return max((lq["bid"] + lq["ask"]) / 2 - (sq["bid"] + sq["ask"]) / 2, 0.0) * 100 * pos["qty"]
    return max(lq["bid"] - sq["ask"], 0.0) * 100 * pos["qty"]


# ledger

def new_ledger(start):
    return {"start": start, "sleeves": {s: {"cash": START_CASH, "shares": None, "spread": None} for s in SLEEVES},
            "trades": [], "equity": {}}


def load(path=LEDGER):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def save(led, path=LEDGER):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(led, f, indent=1)


def log(led, day, sleeve, action, what, qty, price, why, kind, pnl=None):
    led["trades"].append({"date": day, "sleeve": sleeve, "action": action, "what": what, "qty": round(qty, 4),
                          "price": round(price, 4), "pnl": None if pnl is None else round(pnl, 2),
                          "why": why, "kind": kind})


def trading_days_between(a, b):
    d0, d1 = date.fromisoformat(a), date.fromisoformat(b)
    return sum(1 for i in range(1, (d1 - d0).days + 1) if (d0 + timedelta(days=i)).weekday() < 5)


def step(led, day, mk):
    """One daily run. mk[sleeve] = {'etf': facts-ish dict with price, low, open,
    prev_high, atr; 'under': facts(...); 'quotes': {occ: {bid, ask}};
    'chain': [...] or None; 'expiry': 'YYYY-MM-DD'}. Mutates and returns led."""
    entries = 0
    for s, sl in led["sleeves"].items():
        m = mk.get(s)
        if not m:
            continue
        e, u = m["etf"], m["under"]
        pos = sl["shares"]
        if pos:
            held = trading_days_between(pos["date"], day)
            px = why = None
            if held > 0 and e["low"] <= pos["stop"]:
                px, why = min(e["open"], pos["stop"]), "stop"
            elif pos["kind"] == "signal" and u["close"] > u["sma5"]:
                px, why = e["price"], "target: underlying closed above 5d avg"
            elif pos["kind"] == "learning" and held > 0 and e["price"] > e["prev_high"]:
                px, why = e["price"], "target: above prior day's high"
            elif held >= (10 if pos["kind"] == "signal" else 5):
                px, why = e["price"], "time"
            if px is not None:
                px *= 1 - SLIP
                pnl = pos["qty"] * (px - pos["entry"])
                sl["cash"] += pos["qty"] * px
                log(led, day, s, "sell", s, pos["qty"], px, why, pos["kind"], pnl)
                sl["shares"] = None
        sp = sl["spread"]
        if sp:
            val = spread_value(m["quotes"], sp)
            held = trading_days_between(sp["date"], day)
            dte = (date.fromisoformat(sp["expiry"]) - date.fromisoformat(day)).days
            why = None
            if val is None:
                pass  # no quote today: hold and mark at cost
            elif spread_value(m["quotes"], sp, mid=True) >= 1.5 * sp["debit"]:
                why = "take profit +50%"
            elif spread_value(m["quotes"], sp, mid=True) <= 0.5 * sp["debit"]:
                why = "stop -50%"
            elif dte <= 7:
                why = "7 days to expiry"
            elif sp["kind"] == "signal" and u["close"] > u["sma5"]:
                why = "target: underlying closed above 5d avg"
            elif held >= (10 if sp["kind"] == "signal" else 5):
                why = "time"
            if why:
                sl["cash"] += val
                log(led, day, s, "close spread", f"{label(sp)} {sp['expiry']}", sp["qty"],
                    val / 100 / sp["qty"], why, sp["kind"], val - sp["debit"])
                sl["spread"] = None

    def buy_shares(s, budget, stop_atr, risk, kind, why):
        sl, e = led["sleeves"][s], mk[s]["etf"]
        px = e["price"] * (1 + SLIP)
        stop = px - stop_atr * e["atr"]
        qty = min(budget / px, risk / (px - stop), sl["cash"] / px)
        if qty * px < 10:
            return False
        sl["cash"] -= qty * px
        sl["shares"] = {"qty": qty, "entry": px, "date": day, "stop": round(stop, 2), "kind": kind}
        log(led, day, s, "buy", s, qty, px, why, kind)
        return True

    def buy_spread(s, budget, kind, why):
        sl, m = led["sleeves"][s], mk[s]
        if not m.get("chain"):
            return False
        pick = pick_spread(m["chain"], m["etf"]["price"], min(budget, sl["cash"]))
        if not pick:
            return False
        sl["cash"] -= pick["debit"]
        sl["spread"] = {**pick, "qty": 1, "date": day, "expiry": m["expiry"], "kind": kind}
        log(led, day, s, "open spread", f"{label(pick)} {m['expiry']}", 1, pick["debit"] / 100,
            why, kind)
        return True

    for s, sl in led["sleeves"].items():
        if s not in mk:
            continue
        u = mk[s]["under"]
        if not (u["stretch"] or u["rsi2_sig"]):
            continue
        why = f"{'STRETCH' if u['stretch'] else 'RSI2+IBS'} on {SLEEVES[s]['under']}"
        if not sl["shares"] and buy_shares(s, SHARES_MAX, 2.5, MAX_LOSS, "signal", why):
            entries += 1
        if not sl["spread"] and buy_spread(s, SPREAD_MAX, "signal", why):
            entries += 1

    if entries == 0:
        wd = date.fromisoformat(day).weekday()
        first = "spread" if wd in (1, 3) else "shares"
        ranked = sorted((s for s in led["sleeves"] if s in mk and mk[s]["under"]["rsi2"] is not None),
                        key=lambda s: mk[s]["under"]["rsi2"])
        flat = [s for s in ranked if not led["sleeves"][s]["shares"] and not led["sleeves"][s]["spread"]]
        for s in flat + [s for s in ranked if s not in flat]:
            sl, why = led["sleeves"][s], f"learning trade: lowest RSI(2) {mk[s]['under']['rsi2']:.0f} on {SLEEVES[s]['under']}"
            order = [first, "shares" if first == "spread" else "spread"]
            done = False
            for inst in order:
                if inst == "shares" and not sl["shares"]:
                    done = buy_shares(s, SHARES_MAX / 2, 1.5, MAX_LOSS / 2, "learning", why)
                elif inst == "spread" and not sl["spread"]:
                    done = buy_spread(s, SPREAD_MAX, "learning", why)
                if done:
                    break
            if done:
                entries += 1
                break

    eq = {}
    for s, sl in led["sleeves"].items():
        m = mk.get(s, {})
        v = sl["cash"]
        if sl["shares"]:
            v += sl["shares"]["qty"] * m.get("etf", {}).get("price", sl["shares"]["entry"])
        if sl["spread"]:
            val = spread_value(m.get("quotes", {}), sl["spread"])
            v += sl["spread"]["debit"] if val is None else val
        eq[s] = round(v, 2)
    led["equity"][day] = eq
    led["last_entries"] = entries
    return led


# market data

def _broker():
    from .broker import Broker
    return Broker()


def daily(br, symbols, day, days=420):
    start = (date.fromisoformat(day) - timedelta(days=days)).isoformat()
    # The free plan refuses SIP data from the last 15 minutes.
    end = min(datetime.fromisoformat(day).replace(tzinfo=ET), datetime.now(ET) - timedelta(minutes=16))
    out = br.bars(symbols, "1Day", start, end=end.isoformat(), feed="sip")
    return {s: [b for b in bs if b["t"][:10] < day] for s, bs in out.items()}


def snapshots(br, symbols):
    return br._req("GET", f"{DATA_URL}/v2/stocks/snapshots", params={"symbols": ",".join(symbols), "feed": "iex"})


def option_chain(br, etf, day):
    """Calls on the ETF for the nearest expiry 21-50 days out, with indicative quotes."""
    d = date.fromisoformat(day)
    cs = br._req("GET", f"{br.base}/v2/options/contracts", params={
        "underlying_symbols": etf, "type": "call", "limit": 500,
        "expiration_date_gte": (d + timedelta(days=21)).isoformat(),
        "expiration_date_lte": (d + timedelta(days=50)).isoformat()}).get("option_contracts", [])
    if not cs:
        return None, None
    exp = min(c["expiration_date"] for c in cs)
    cs = [c for c in cs if c["expiration_date"] == exp]
    return exp, [{"symbol": c["symbol"], "strike": float(c["strike_price"])} for c in cs]


def option_quotes(br, symbols):
    out = {}
    for i in range(0, len(symbols), 100):
        d = br._req("GET", f"{DATA_URL}/v1beta1/options/snapshots",
                    params={"symbols": ",".join(symbols[i:i + 100]), "feed": "indicative"})
        for k, v in (d.get("snapshots") or {}).items():
            q = v.get("latestQuote") or {}
            out[k] = {"bid": float(q.get("bp") or 0), "ask": float(q.get("ap") or 0)}
    return out


def market(br, day):
    unders = [v["under"] for v in SLEEVES.values()]
    hist = daily(br, list(SLEEVES) + unders, day)
    snaps = snapshots(br, list(SLEEVES) + unders)
    mk = {}
    for etf, cfg in SLEEVES.items():
        u = cfg["under"]
        sn, su = snaps.get(etf) or {}, snaps.get(u) or {}
        if not sn.get("latestTrade") or not su.get("latestTrade") or not hist.get(etf) or not hist.get(u):
            continue
        db, dbu = sn.get("dailyBar") or {}, su.get("dailyBar") or {}
        p, pu = float(sn["latestTrade"]["p"]), float(su["latestTrade"]["p"])
        today_u = {"o": dbu.get("o", pu), "h": max(dbu.get("h", pu), pu), "l": min(dbu.get("l", pu), pu), "c": pu}
        ebars = hist[etf]
        exp, chain = option_chain(br, etf, day)
        held = []
        led = load()
        if led and led["sleeves"][etf]["spread"]:
            sp = led["sleeves"][etf]["spread"]
            held = [x for x in (sp["long"], sp["short"]) if x]
        q = option_quotes(br, [c["symbol"] for c in chain or []] + held)
        if chain:
            chain = [{**c, **q[c["symbol"]]} for c in chain if c["symbol"] in q]
        mk[etf] = {"etf": {"price": p, "open": db.get("o", p), "low": min(db.get("l", p), p),
                           "prev_high": ebars[-1]["h"], "atr": atr(ebars)},
                   "under": facts(hist[u] + [today_u]), "quotes": q, "chain": chain, "expiry": exp}
    return mk


# commands

def is_open(br, day):
    cal = br._req("GET", f"{br.base}/v2/calendar", params={"start": day, "end": day})
    return bool(cal) and cal[0]["date"] == day


def cmd_trade(day=None):
    br = _broker()
    day = day or datetime.now(ET).date().isoformat()
    if not is_open(br, day):
        print(f"MARKET CLOSED {day}")
        return
    led = load() or new_ledger(day)
    mk = market(br, day)
    before = len(led["trades"])
    step(led, day, mk)
    save(led)
    for t in led["trades"][before:]:
        pnl = "" if t["pnl"] is None else f" P&L {t['pnl']:+.2f}"
        print(f"{t['sleeve']} {t['action']} {t['what']} x{t['qty']} @ {t['price']}{pnl} ({t['why']})")
    if len(led["trades"]) == before:
        print("NO TRADES (no cash free or no quotes)")
    cmd_report(day)


def trigger_prices(bars):
    """Underlying close that would fire STRETCH tomorrow, holding today's bar out.
    Approximate: the 10d avg and ATR move a little with the new close."""
    closes = [b["c"] for b in bars]
    a, m10 = atr(bars), sma(closes[-9:] + [closes[-1]], 10)
    return None if a is None or m10 is None else m10 - 2 * a


def cmd_scan(day=None):
    br = _broker()
    day = day or datetime.now(ET).date().isoformat()
    if not is_open(br, day):
        print(f"MARKET CLOSED {day}")
        return
    unders = [v["under"] for v in SLEEVES.values()]
    hist = daily(br, list(SLEEVES) + unders, day)
    snaps = snapshots(br, list(SLEEVES) + unders)
    since = min(datetime.fromisoformat(day).replace(tzinfo=ET), datetime.now(ET)) - timedelta(hours=18)
    syms = sorted({x for v in SLEEVES.values() for x in [v["under"], *v["holdings"]]} | set(SLEEVES))
    news = br._req("GET", f"{DATA_URL}/v1beta1/news", params={
        "symbols": ",".join(syms), "start": since.isoformat(), "limit": 50, "sort": "desc"}).get("news", [])
    import csv
    events = []
    if os.path.exists(EVENTS):
        horizon = (date.fromisoformat(day) + timedelta(days=4)).isoformat()
        with open(EVENTS) as f:
            events = [r for r in csv.DictReader(f) if day <= r["date"] <= horizon]
    out = {"date": day, "sleeves": []}
    L = [f"# ETF sleeves premarket scan {day}", "",
         "Paper only. Premarket prices are from the IEX feed and thin before 9:30.", "",
         "| ETF | Underlying | Last close | vs 200d | RSI(2) | STRETCH fires at | Premarket | Setup |",
         "|---|---|---|---|---|---|---|---|"]
    for etf, cfg in SLEEVES.items():
        u = cfg["under"]
        bars = hist.get(u) or []
        if len(bars) < 201:
            continue
        f = facts(bars)
        trig = trigger_prices(bars)
        pre = ((snaps.get(u) or {}).get("latestTrade") or {}).get("p")
        gap = None if pre is None else pre / f["close"] - 1
        setup = ("STRETCH would fire now" if f["stretch"] else "RSI2 would fire now" if f["rsi2_sig"]
                 else "below 200d: setups off, learning trades only" if not f["above200"]
                 else f"needs {trig / f['close'] - 1:+.1%} to trigger")
        rel = {etf, u, *cfg["holdings"]}
        heads = [n for n in news if rel & set(n.get("symbols", []))][:5]
        ev = [r for r in events if r["symbol"] in rel or r["symbol"] == "ALL"]
        out["sleeves"].append({"etf": etf, "under": u, "close": f["close"], "sma200": f["sma200"], "rsi2": f["rsi2"],
                               "trigger": trig, "premarket": pre, "setup": setup,
                               "news": [n["headline"] for n in heads], "events": ev})
        L.append(f"| {etf} | {u} | {f['close']:.2f} | {f['close'] / f['sma200'] - 1:+.1%} | {f['rsi2']:.0f} | "
                 f"{trig:.2f} | {'n/a' if gap is None else f'{gap:+.1%}'} | {setup} |")
    for s in out["sleeves"]:
        L += ["", f"## {s['etf']} ({SLEEVES[s['etf']]['name']})"]
        L += [f"- Event: {r['date']} {r['symbol']} {r['event']} ({r['timing']})" for r in s["events"]]
        L += [f"- {h}" for h in s["news"]] or ["- No headlines in the last 18 hours."]
    # Same order as step(): flat sleeves first, then by RSI(2).
    led = load()
    busy = {s for s, sl in (led or {}).get("sleeves", {}).items() if sl["shares"] or sl["spread"]}
    ranked = sorted(out["sleeves"], key=lambda s: (s["etf"] in busy, s["rsi2"]))
    if ranked:
        L += ["", f"If nothing triggers by 15:41 ET, today's learning trade goes to {ranked[0]['etf']} "
                  f"(RSI(2) {ranked[0]['rsi2']:.0f}, lowest among flat sleeves), as "
                  f"{'a call debit spread' if date.fromisoformat(day).weekday() in (1, 3) else 'shares'}."]
    os.makedirs(DIR, exist_ok=True)
    with open(f"{DIR}/scan-{day}.json", "w") as fh:
        json.dump(out, fh, indent=1, default=str)
    with open(f"{DIR}/scan-{day}.md", "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L))


def report_text(led, day):
    days = sorted(led["equity"])
    n = len(days)
    L = [f"# ETF sleeves ({day})", "",
         "Paper only, simulated fills on live Alpaca quotes (options at the ask/bid). Four $200 sleeves. "
         "Goal +5-8% a day is a stretch target; it is tracked, not expected.", "",
         "| Sleeve | Equity | Today | Since start | Goal at 5%/day | Goal at 8%/day | Holding |",
         "|---|---|---|---|---|---|---|"]
    tot = prev_tot = 0.0
    for s in SLEEVES:
        sl = led["sleeves"][s]
        eq = led["equity"][days[-1]][s] if days else START_CASH
        pv = led["equity"][days[-2]][s] if n > 1 else START_CASH
        tot, prev_tot = tot + eq, prev_tot + pv
        hold = []
        if sl["shares"]:
            hold.append(f"{sl['shares']['qty']:.2f} sh @ {sl['shares']['entry']:.2f} (stop {sl['shares']['stop']})")
        if sl["spread"]:
            hold.append(f"{label(sl['spread'])} {sl['spread']['expiry']} "
                        f"(paid ${sl['spread']['debit']:.0f})")
        L.append(f"| {s} | ${eq:.2f} | {eq / pv - 1:+.1%} | {eq / START_CASH - 1:+.1%} | "
                 f"${START_CASH * (1 + GOAL_LO) ** n:.2f} | ${START_CASH * (1 + GOAL_HI) ** n:.2f} | "
                 f"{'; '.join(hold) or 'cash'} |")
    start = START_CASH * len(SLEEVES)
    L.append(f"| **All** | **${tot:.2f}** | {tot / prev_tot - 1:+.1%} | {tot / start - 1:+.1%} | "
             f"${start * (1 + GOAL_LO) ** n:.2f} | ${start * (1 + GOAL_HI) ** n:.2f} | |")
    closed = [t for t in led["trades"] if t["pnl"] is not None]
    wins = sum(t["pnl"] > 0 for t in closed)
    L += ["", f"Trading days: {n}. Closed trades: {len(closed)}, {wins} won, "
              f"P&L ${sum(t['pnl'] for t in closed):+.2f}.", "",
          "## Trades", "| Date | Sleeve | Action | What | Qty | Price | P&L | Why |", "|---|---|---|---|---|---|---|---|"]
    L += [f"| {t['date']} | {t['sleeve']} | {t['action']} | {t['what']} | {t['qty']:g} | {t['price']:.2f} | "
          f"{'' if t['pnl'] is None else f'{t['pnl']:+.2f}'} | {t['why']} |" for t in reversed(led["trades"][-40:])] \
        or ["| none | | | | | | | |"]
    return "\n".join(L) + "\n"


def cmd_report(day=None):
    day = day or datetime.now(ET).date().isoformat()
    led = load() or new_ledger(day)
    text = report_text(led, day)
    os.makedirs(DIR, exist_ok=True)
    with open(f"{DIR}/report.md", "w") as f:
        f.write(text)
    print(text)


def main(argv):
    cmd = argv[0] if argv else "report"
    day = argv[1] if len(argv) > 1 else None
    {"scan": cmd_scan, "trade": cmd_trade, "report": cmd_report}[cmd](day)


if __name__ == "__main__":
    main(sys.argv[1:])
