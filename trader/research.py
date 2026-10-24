"""Premarket research brief: the facts the trader and the risk manager read
before the open.

For each traded symbol it reports the premarket gap against the prior close,
trend (20/50-day averages), recent returns, daily volatility (ATR) and the
overnight headlines, then gives a verdict:

    skip     the bot's gap rule will skip it
    caution  an earnings or other headline catalyst, unusually high
             volatility, or a downtrend; tradable, but expect noise
    ok       nothing unusual

It also reads the market backdrop: SPY/QQQ regime, sector ETFs, rates,
dollar, gold, oil, volatility, and the day's large-cap movers.

    python -m trader.research [YYYY-MM-DD]   # writes trader/journal/research/<date>.md and .json

Information for the trader, never an order. The trading rules in config.py
still decide every trade.
"""
import csv
import json
import os
import re
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from .broker import Broker
from .config import DATA_URL, Config

ET = ZoneInfo("America/New_York")
SECTORS = {"XLK": "Tech", "SMH": "Semis", "XLC": "Comm services", "XLY": "Discretionary", "XLF": "Financials",
           "XLI": "Industrials", "XLE": "Energy", "XLV": "Health care", "XLP": "Staples", "XLU": "Utilities"}
MACRO = {"IWM": "Small caps", "DIA": "Dow", "TLT": "20y+ Treasuries", "UUP": "US dollar", "GLD": "Gold",
         "USO": "Crude oil", "VIXY": "VIX futures"}
EVENTS_PATH = "trader/journal/research/events.csv"
ETFS = {"SPY", "QQQ", "IWM", "DIA"}
EARNINGS = re.compile(r"\b(earnings|quarterly results|q[1-4] (results|revenue|eps)|eps|guidance|revenue (beat|miss)|"
                      r"to report)\b", re.I)
CATALYST = re.compile(r"\b(downgrades?|upgrades?|price target|antitrust|lawsuit|probe|sec|doj|ftc|fda|stock split|"
                      r"acquires?|acquisition|merger|buyback|recall|tariffs?|ban)\b", re.I)


def sma(closes, n):
    return sum(closes[-n:]) / n if len(closes) >= n else None


def atr_pct(bars, n=14):
    """Average true range over n days, as a fraction of the last close."""
    if len(bars) < n + 1:
        return None
    trs = [max(b["h"] - b["l"], abs(b["h"] - p["c"]), abs(b["l"] - p["c"])) for p, b in zip(bars[-n - 1:-1], bars[-n:])]
    return sum(trs) / n / bars[-1]["c"]


def profile(daily, price, fresh=True):
    """Trend and volatility facts from completed daily bars plus the latest price."""
    closes = [b["c"] for b in daily]
    if not closes:
        return {}
    prior = closes[-1]
    s20, s50 = sma(closes, 20), sma(closes, 50)
    atr = atr_pct(daily)
    # Today's ATR against the ATR of a month ago: above 1.3 means volatility is expanding.
    atr_then = atr_pct(daily[:-20]) if len(daily) > 35 else None
    return {
        "prior_close": prior,
        "price": price,
        # No trade yet today (IEX premarket is thin before ~8:00 ET) means no gap reading, not a 0% gap.
        "gap": price / prior - 1 if price and fresh else None,
        "ret_5d": prior / closes[-6] - 1 if len(closes) > 5 else None,
        "ret_20d": prior / closes[-21] - 1 if len(closes) > 20 else None,
        "sma20": s20, "sma50": s50,
        "trend": ("up" if s20 and s50 and prior > s20 > s50 else
                  "down" if s20 and s50 and prior < s20 < s50 else "mixed"),
        "atr_pct": atr,
        "vol_expanding": bool(atr and atr_then and atr / atr_then > 1.3),
    }


def tag_news(items, symbol):
    """Headlines that mention the symbol, with earnings and other catalysts flagged."""
    out = []
    for n in items:
        if symbol not in n.get("symbols", []):
            continue
        # Index ETFs get the whole market's headlines; flags only mean something for single stocks.
        single = symbol not in ETFS
        out.append({"time": n["created_at"], "headline": n["headline"], "source": n.get("source", ""),
                    "url": n.get("url", ""),
                    "earnings": single and bool(EARNINGS.search(n["headline"])),
                    "catalyst": single and bool(CATALYST.search(n["headline"]))})
    return out


def load_events(path, day):
    """Rows from the events calendar that matter for `day`: anything today, plus
    yesterday's after-close reports, which move today's open."""
    if not os.path.exists(path):
        return []
    prev = (day - timedelta(days=3 if day.weekday() == 0 else 1)).isoformat()
    with open(path) as f:
        return [r for r in csv.DictReader(f)
                if r["date"] == day.isoformat() or (r["date"] == prev and r["timing"] == "after")]


def verdict(p, news, max_gap, events=()):
    """skip / caution / ok, with the reasons."""
    why, level = [], "ok"
    for e in events:
        if e["symbol"] != "ALL":
            why.append(f"{e['event']} ({e['date']}, {e['timing']} the session): the opening range is unreliable")
            level = "skip"
    gap = p.get("gap")
    if gap is None and level != "skip":
        why.append("no premarket trade yet, gap unknown")
    elif gap is not None and abs(gap) > max_gap:
        why.append(f"premarket gap {gap:+.2%} is past the {max_gap:.2%} gap rule, so the bot will skip it")
        level = "skip"
    if level != "skip":
        if any(n["earnings"] for n in news):
            why.append("earnings headline overnight; check whether it reports today")
            level = "caution"
        elif any(n["catalyst"] for n in news):
            why.append("headline catalyst overnight")
            level = "caution"
        if p.get("vol_expanding"):
            why.append(f"volatility expanding (ATR {p['atr_pct']:.2%} of price)")
            level = "caution"
        if p.get("trend") == "down":
            why.append("below its 20- and 50-day averages; long breakouts fight the trend")
            level = "caution"
    return level, why or ["nothing unusual"]


def regime(spy, qqq, vixy):
    """One-line read of the market backdrop for a long-only breakout bot."""
    notes = []
    for name, p in (("SPY", spy), ("QQQ", qqq)):
        if p:
            notes.append(f"{name} trend {p['trend']}, gap {_pct(p.get('gap'))}, 5d {_pct(p.get('ret_5d'))}")
    risk_off = any(p and p.get("gap") is not None and p["gap"] < -0.0075 for p in (spy, qqq))
    if vixy and vixy.get("ret_5d") is not None and vixy["ret_5d"] > 0.10:
        notes.append(f"VIX futures up {vixy['ret_5d']:.1%} in 5 days")
        risk_off = True
    trend_up = all(p and p["trend"] == "up" for p in (spy, qqq))
    label = "risk-off open" if risk_off else "trend up" if trend_up else "mixed / range"
    return label, notes


def _pct(x):
    return "n/a" if x is None else f"{x:+.2%}"


def _utc_iso(day, hour_et):
    t = datetime(day.year, day.month, day.day, hour_et, tzinfo=ET).astimezone(ZoneInfo("UTC"))
    return t.strftime("%Y-%m-%dT%H:%M:%S")


def gather(broker, cfg, day):
    syms = list(dict.fromkeys(list(cfg.symbols) + ["SPY", "QQQ"] + list(SECTORS) + list(MACRO)))
    start = (day - timedelta(days=100)).isoformat()
    daily = broker.bars(syms, "1Day", start, end=(day - timedelta(days=1)).isoformat(), feed=cfg.data_feed)
    snaps = broker._req("GET", f"{DATA_URL}/v2/stocks/snapshots",
                        params={"symbols": ",".join(syms), "feed": cfg.data_feed})
    prof = {}
    for s in syms:
        bars = [b for b in daily.get(s, []) if b["t"][:10] < day.isoformat()]
        snap = snaps.get(s) or {}
        trade = snap.get("latestTrade") or {}
        price = trade.get("p")
        p = profile(bars, price, fresh=trade.get("t", "") >= _utc_iso(day, 4))
        if p:
            p["price_time"] = trade.get("t", "")
            prof[s] = p
    since = datetime(day.year, day.month, day.day, tzinfo=ET) - timedelta(hours=18)
    news = broker._req("GET", f"{DATA_URL}/v1beta1/news",
                       params={"symbols": ",".join(cfg.symbols), "start": since.isoformat(), "limit": 50,
                               "sort": "desc"}).get("news", [])
    market_news = broker._req("GET", f"{DATA_URL}/v1beta1/news",
                              params={"start": since.isoformat(), "limit": 15, "sort": "desc"}).get("news", [])
    movers = broker._req("GET", f"{DATA_URL}/v1beta1/screener/stocks/movers", params={"top": 50})
    return prof, news, market_news, movers


def build(day, cfg=None, broker=None, events_path=EVENTS_PATH):
    cfg = cfg or Config()
    broker = broker or Broker()
    prof, news, market_news, movers = gather(broker, cfg, day)
    events = load_events(events_path, day)
    label, notes = regime(prof.get("SPY"), prof.get("QQQ"), prof.get("VIXY"))
    watch = []
    for s in cfg.symbols:
        p = prof.get(s, {})
        hs = tag_news(news, s)
        level, why = verdict(p, hs, cfg.max_gap, [e for e in events if e["symbol"] == s])
        # Keep every flagged headline so each verdict shows its evidence, then fill to five.
        shown = [n for n in hs if n["earnings"] or n["catalyst"]]
        shown += [n for n in hs if n not in shown][:max(0, 5 - len(shown))]
        watch.append({"symbol": s, "verdict": level, "why": why, **p, "news": shown})
    # Large, liquid names only: the movers list is mostly penny stocks.
    big = {k: [m for m in movers.get(k, []) if m["price"] >= 20][:5] for k in ("gainers", "losers")}
    data = {"date": day.isoformat(), "generated": datetime.now(ET).isoformat(timespec="minutes"),
            "regime": label, "regime_notes": notes, "events": events, "watchlist": watch,
            "sectors": {s: prof.get(s) for s in SECTORS}, "macro": {s: prof.get(s) for s in MACRO},
            "market_news": [{"time": n["created_at"], "headline": n["headline"], "symbols": n.get("symbols", [])}
                            for n in market_news],
            "movers": big}
    return data


def markdown(d):
    L = [f"## Research brief {d['date']}", "",
         f"Generated {d['generated']} ET from Alpaca market data and news (IEX feed: premarket prices are thin "
         "and can be minutes old). Information for the trader, not an order.", "",
         f"**Regime:** {d['regime']}. " + "; ".join(d["regime_notes"]), "",
         "**Scheduled events:** " + ("; ".join(f"{e['symbol']}: {e['event']} ({e['date']}, {e['timing']})"
                                              for e in d["events"]) or "none on the calendar"), "",
         "### Watchlist", "",
         "| Symbol | Verdict | Last | Gap | 5d | 20d | Trend | ATR | Why |", "|---|---|---|---|---|---|---|---|---|"]
    for w in d["watchlist"]:
        L.append(f"| {w['symbol']} | **{w['verdict']}** | {w.get('price') or 'n/a'} | {_pct(w.get('gap'))} | "
                 f"{_pct(w.get('ret_5d'))} | {_pct(w.get('ret_20d'))} | {w.get('trend', 'n/a')} | "
                 f"{_pct(w.get('atr_pct')).lstrip('+')} | {'; '.join(w['why'])} |")
    L += ["", "### Sectors and macro (gap vs prior close, 5-day, trend)", "",
          "| ETF | What | Gap | 5d | 20d | Trend |", "|---|---|---|---|---|---|"]
    for group, names in ((d["sectors"], SECTORS), (d["macro"], MACRO)):
        rows = sorted(((s, p) for s, p in group.items() if p), key=lambda x: -(x[1].get("ret_5d") or 0))
        for s, p in rows:
            L.append(f"| {s} | {names[s]} | {_pct(p.get('gap'))} | {_pct(p.get('ret_5d'))} | "
                     f"{_pct(p.get('ret_20d'))} | {p['trend']} |")
    L += ["", "### Watchlist headlines (last 18 hours)", ""]
    any_news = False
    for w in d["watchlist"]:
        for n in w["news"]:
            any_news = True
            flag = " [earnings]" if n["earnings"] else " [catalyst]" if n["catalyst"] else ""
            L.append(f"- {w['symbol']}{flag}: [{n['headline']}]({n['url']}) ({n['source']}, {n['time'][11:16]} UTC)")
    if not any_news:
        L.append("- none")
    L += ["", "### Market headlines", ""]
    L += [f"- {n['headline']} ({', '.join(n['symbols'][:4]) or 'market'})" for n in d["market_news"][:10]] or ["- none"]
    L += ["", "### Large-cap movers (price $20 and up, info only, not in the bot's universe)", ""]
    for k in ("gainers", "losers"):
        L.append(f"- {k.title()}: " + (", ".join(f"{m['symbol']} {m['percent_change']:+.1f}%" for m in d["movers"][k])
                                       or "none"))
    return "\n".join(L) + "\n"


def write(day, out_dir="trader/journal/research"):
    d = build(day)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"{day}.json"), "w") as f:
        json.dump(d, f, indent=1)
    md = markdown(d)
    with open(os.path.join(out_dir, f"{day}.md"), "w") as f:
        f.write(md)
    return md


if __name__ == "__main__":
    print(write(date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.now(ET).date()))
