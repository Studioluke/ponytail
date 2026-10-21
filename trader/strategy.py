"""Opening-range breakout, long only, with a VWAP filter.

The first `opening_range_minutes` of the session set a high and low. After
that, the first 1-minute bar that closes above the range high, while also
above VWAP, is a buy signal. The stop sits at the range midpoint and the
target at `reward_risk` times the risk. One trade per symbol per day.
"""
from dataclasses import dataclass


@dataclass
class Signal:
    symbol: str
    entry: float
    stop: float
    target: float
    reason: str


def opening_range(bars, minutes):
    first = bars[:minutes]
    if len(first) < minutes:
        return None
    return max(b["h"] for b in first), min(b["l"] for b in first)


def vwap(bars):
    pv = sum((b["h"] + b["l"] + b["c"]) / 3 * b["v"] for b in bars)
    vol = sum(b["v"] for b in bars)
    return pv / vol if vol else None


def check(symbol, bars, minutes, reward_risk):
    """bars: today's regular-session 1-min bars, oldest first, up to now."""
    rng = opening_range(bars, minutes)
    if rng is None or len(bars) <= minutes:
        return None
    hi, lo = rng
    # Only act on a fresh break: the latest bar closes above the range and
    # no earlier post-range bar did.
    post = bars[minutes:]
    last = post[-1]
    if last["c"] <= hi or any(b["c"] > hi for b in post[:-1]):
        return None
    vw = vwap(bars)
    if vw is None or last["c"] <= vw:
        return None
    entry = last["c"]
    stop = (hi + lo) / 2
    risk = entry - stop
    if risk <= 0:
        return None
    return Signal(symbol, entry, round(stop, 2), round(entry + reward_risk * risk, 2),
                  f"ORB break of {hi:.2f} (range {lo:.2f}-{hi:.2f}), VWAP {vw:.2f}")
