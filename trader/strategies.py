"""The strategy experiment that started 2026-11-05.

The strategy research thread (/mnt/project-files/day-trader/strategy-research.md,
2026-11-04) proposed this after 41 paper trades of the 15-minute ORB showed no
edge (PF 0.90). Luke, 2026-11-04: keep paper trading as long as it takes to
find a winning strategy. Four strategies run side by side, each with its own
slots. A signal that gets no slot is logged as a shadow trade
(trader/shadow.py replays it after the close), so every strategy builds a
sample quickly. Promote a strategy at 40+ trades with PF > 1.2. Retire it at
40 trades with average R < 0.

  sip_orb   Stocks-in-play 5-minute ORB (Zarattini, Barbon and Aziz 2024).
            At 9:35, rank the 100-stock watchlist by relative volume
            9:30-9:35 and keep the top 10 green first candles. Buy the first
            break of the 5-minute high, until 10:30. Stop = high - 0.1 x ATR14.
            No target: hold to 15:58. 2 slots.
  noise     SPY "noise area" momentum (Zarattini, Aziz and Barbon 2024).
            Checks only at :00 and :30. Above the upper band, buy SPY. Below
            the lower band, buy SH. Trail at the band or VWAP. If nothing has
            broken by 11:30, take a half-size trade in the direction of SPY
            vs its open. This replaces the 11:00 learning trade. 1 slot.
  lasthalf  Last-half-hour momentum (Gao, Han, Li and Zhou 2018). At 15:30,
            if SPY's return from the prior close to 10:00 is above 0, buy SPY;
            below 0, buy SH. Hard stop 0.5%, exit 15:58. 1 slot.
  control   The old 15-minute ORB on the 5 core symbols only, strict gap and
            research rules. Stop = max(range midpoint, 0.25 x ATR14), $0.75
            risk. Sell half at 2R, trail the rest at VWAP, exit 15:58. 1 slot.
"""
import re
from datetime import datetime, time
from zoneinfo import ZoneInfo

from .strategy import Signal, opening_range, vwap

ET = ZoneInfo("America/New_York")
EXPERIMENT_START = "2026-11-05"
SLOTS = {"sip_orb": 2, "noise": 1, "lasthalf": 1, "control": 1}
RISK_FRAC = {"sip_orb": 0.005, "noise": 0.005, "lasthalf": 0.005, "control": 0.0025}
PROMOTE = {"min_trades": 40, "profit_factor": 1.2}

SIP_SCAN_AT = time(9, 35)
SIP_LAST_ENTRY = time(10, 30)
SIP_TOP = 10
SIP_MIN_PRICE = 5.0
SIP_MIN_ATR = 0.50
SIP_STOP_ATR = 0.10
# Research "skip" verdicts still veto sip_orb for these, not for gaps or earnings.
SIP_BINARY = re.compile(r"halt|offering|FDA|PDUFA|delist|merger|acquisition", re.I)

NOISE_DAYS = 14
NOISE_FIRST = time(10, 0)
NOISE_LAST = time(15, 30)
NOISE_SKIP = (time(13, 30), time(15, 0))  # no new noise entries here; exits still run
NOISE_FALLBACK_AT = time(11, 30)
NOISE_HARD_STOP = 0.01
NOISE_FALLBACK_CAP = 0.5  # half of the $60 slot

LASTHALF_AT = time(15, 30)
LASTHALF_STOP = 0.005

CONTROL_STOP_ATR = 0.25
CONTROL_HALF_R = 2.0


def bar_time(b):
    return datetime.fromisoformat(b["t"].replace("Z", "+00:00")).astimezone(ET)


def atr(daily, n=14):
    """Average true range over the last n complete daily bars, oldest first."""
    if len(daily) < 2:
        return None
    trs = []
    for prev, b in zip(daily, daily[1:]):
        trs.append(max(b["h"] - b["l"], abs(b["h"] - prev["c"]), abs(b["l"] - prev["c"])))
    trs = trs[-n:]
    return sum(trs) / len(trs) if trs else None


# sip_orb

def stocks_in_play(first_5m, hist_5m_vol, daily):
    """Rank the watchlist at 9:35.

    first_5m: {sym: 9:30-9:35 bar}. hist_5m_vol: {sym: [9:30-9:35 volume on each
    of the last 14 days]}. daily: {sym: prior daily bars}. Returns up to
    SIP_TOP dicts {symbol, hi, lo, atr, rvol, green}, best first. Only green
    candles are tradable, because we are long only."""
    ranked = []
    for sym, b in first_5m.items():
        hist = [v for v in hist_5m_vol.get(sym, []) if v]
        a = atr(daily.get(sym, []))
        if len(hist) < 5 or not a or b["c"] < SIP_MIN_PRICE or a < SIP_MIN_ATR:
            continue
        rvol = b["v"] / (sum(hist) / len(hist))
        if rvol < 1.0:
            continue
        ranked.append({"symbol": sym, "hi": b["h"], "lo": b["l"], "atr": round(a, 4), "rvol": round(rvol, 2),
                       "green": b["c"] > b["o"]})
    ranked.sort(key=lambda x: -x["rvol"])
    return ranked[:SIP_TOP]


def sip_signal(c, bars, last_price):
    """c: a stocks_in_play entry. bars: today's 1-min bars. Signal on the first
    post-9:35 bar whose high breaks the 5-minute high (a buy stop there), with
    the market price as entry and the stop 0.1 x ATR below the trigger."""
    post = [b for b in bars if bar_time(b).time() >= SIP_SCAN_AT]
    if not c["green"] or not post or post[-1]["h"] <= c["hi"] or any(b["h"] > c["hi"] for b in post[:-1]):
        return None
    stop = round(c["hi"] - SIP_STOP_ATR * c["atr"], 2)
    if last_price <= stop:
        return None
    return Signal(c["symbol"], last_price, stop, None,
                  f"5-min ORB break of {c['hi']:.2f} (range {c['lo']:.2f}-{c['hi']:.2f}), RVOL {c['rvol']:.1f}, "
                  f"ATR {c['atr']:.2f}", strategy="sip_orb")


# noise area

def minute_index(b):
    t = bar_time(b)
    return (t.hour - 9) * 60 + t.minute - 30


def noise_sigma(days):
    """days: [[1-min bars of one session], ...] for the last NOISE_DAYS days.
    Returns {minute index: average |close / open - 1|}."""
    acc = {}
    for bars in days:
        if not bars:
            continue
        o = bars[0]["o"]
        for b in bars:
            acc.setdefault(minute_index(b), []).append(abs(b["c"] / o - 1))
    return {i: sum(v) / len(v) for i, v in acc.items() if v}


def noise_bands(spy_bars, prior_close, sigma):
    """(upper, lower) for the last bar in spy_bars, or None."""
    if not spy_bars or prior_close is None:
        return None
    s = sigma.get(minute_index(spy_bars[-1]))
    if s is None:
        return None
    o = spy_bars[0]["o"]
    return max(o, prior_close) * (1 + s), min(o, prior_close) * (1 - s)


def on_noise_grid(now):
    """The :00/:30 check key for `now` ("10:30"), or None between checks. The
    loop polls once a minute a few seconds past the minute, so allow :01/:31."""
    t = now.time()
    if t < NOISE_FIRST or t > time(15, 31) or now.minute % 30 > 1:
        return None
    return f"{now.hour:02d}:{now.minute - now.minute % 30:02d}"


def noise_direction(spy_bars, prior_close, sigma):
    """+1 above the upper band, -1 below the lower band, else 0."""
    bands = noise_bands(spy_bars, prior_close, sigma)
    if not bands:
        return 0
    c = spy_bars[-1]["c"]
    return 1 if c > bands[0] else -1 if c < bands[1] else 0


# last half hour

def lasthalf_direction(spy_bars, prior_close):
    """Sign of SPY's return from the prior close to 10:00 (close of the 9:59 bar)."""
    early = [b for b in spy_bars if bar_time(b).time() < time(10, 0)]
    if not early or not prior_close:
        return 0
    r = early[-1]["c"] / prior_close - 1
    return 1 if r > 0 else -1 if r < 0 else 0


# control

def control_signal(sym, bars, minutes, a):
    """The old 15-min ORB, with the stop widened to at least 0.25 x ATR14, half
    off at 2R and no fixed target."""
    sig = strategy_check(sym, bars, minutes)
    if not sig:
        return None
    dist = max(sig.entry - sig.stop, CONTROL_STOP_ATR * a if a else 0)
    stop = round(sig.entry - dist, 2)
    return Signal(sym, sig.entry, stop, None, sig.reason + f", stop {dist:.2f} below (ATR {a or 0:.2f})",
                  strategy="control", half_at=round(sig.entry + CONTROL_HALF_R * dist, 2))


def strategy_check(sym, bars, minutes):
    from .strategy import check
    return check(sym, bars, minutes, 2.0)


# exits, shared by the live loop and the shadow replay

def exit_action(t, px, close, vw, spy=None, grid=False):
    """What to do with open trade t now. px: last price of the symbol; close and
    vw: its last complete 1-min close and today's VWAP; spy: {"close", "vwap",
    "upper", "lower"} for SPY-referenced trails; grid: a :00/:30 check.
    Returns None, ("half", reason) or ("close", reason)."""
    if t.get("target") and px >= t["target"]:
        return ("close", "target")
    if t.get("half_at") and not t.get("half_done") and px >= t["half_at"]:
        return ("half", "half at 2R")
    trail = t.get("trail")
    if trail == "vwap" and t.get("half_done") and close is not None and vw and close < vw:
        return ("close", "trail")
    if grid and spy and trail in ("band", "vwap_grid"):
        d = t.get("dir", 1)
        if trail == "band" and spy.get("upper") is not None:
            level = max(spy["upper"], spy["vwap"]) if d > 0 else min(spy["lower"], spy["vwap"])
        else:
            level = spy["vwap"]
        if (d > 0 and spy["close"] < level) or (d < 0 and spy["close"] > level):
            return ("close", "trail")
    return None


def simulate(t, bars, spy_bars=None, prior_close=None, sigma=None, flatten=time(15, 58)):
    """Replay open trade t (entered at t["time"], an ET iso string) over the
    day's 1-min bars. Returns {exit_time, exit_price, how, pnl, r}, with pnl in
    dollars for t["qty"] and r against the original stop."""
    start = datetime.fromisoformat(t["time"])
    qty, entry, stop0 = t["qty"], t["entry"], t["stop"]
    stop, half_qty, realized, last, seen = stop0, 0.0, 0.0, None, set()
    t = dict(t)
    spy_by_time = {b["t"]: i for i, b in enumerate(spy_bars or [])}
    for i, b in enumerate(bars):
        bt = bar_time(b)
        if bt < start.replace(second=0, microsecond=0):
            continue
        last = b
        if bt.time() >= flatten:
            return _done(t, bt, b["o"], "eod", qty, half_qty, realized, entry, stop0)
        if b["l"] <= stop:
            return _done(t, bt, stop, "stop", qty, half_qty, realized, entry, stop0)
        vw = vwap(bars[:i + 1])
        spy = None
        j = spy_by_time.get(b["t"])
        if spy_bars and j is not None:
            sb = spy_bars[:j + 1]
            bands = noise_bands(sb, prior_close, sigma or {})
            spy = {"close": sb[-1]["c"], "vwap": vwap(sb),
                   "upper": bands[0] if bands else None, "lower": bands[1] if bands else None}
        key = on_noise_grid(bt.replace(second=0) + _one_min())
        grid = key is not None and key not in seen
        if grid:
            seen.add(key)
        act = exit_action(t, b["h"] if t.get("half_at") or t.get("target") else b["c"], b["c"], vw, spy, grid)
        if act and act[0] == "half":
            half_qty = round(qty / 2, 3)
            realized += half_qty * (t["half_at"] - entry)
            t["half_done"] = True
            stop = max(stop, entry)
        elif act:
            px = t["target"] if act[1] == "target" else b["c"]
            return _done(t, bt, px, act[1], qty, half_qty, realized, entry, stop0)
    if last is None:
        return None
    return _done(t, bar_time(last), last["c"], "eod", qty, half_qty, realized, entry, stop0)


def _one_min():
    from datetime import timedelta
    return timedelta(minutes=1)


def _done(t, bt, px, how, qty, half_qty, realized, entry, stop0):
    pnl = realized + (qty - half_qty) * (px - entry)
    risk = qty * (entry - stop0)
    return {"exit_time": bt.isoformat(), "exit_price": round(px, 4), "how": how, "pnl": round(pnl, 4),
            "r": round(pnl / risk, 3) if risk > 0 else 0.0}
