"""Backfill the sip_orb_mkt filter over sip_orb trades since 11-05 (live + shadow, and the wide shadows).

    python -m trader.backfill_mkt > trader/journal/notes/sip_orb_mkt-backfill.md
"""
import csv, sys
from datetime import datetime
from . import run, strategies, shadow, risk_manager
from .broker import Broker
from .config import Config
ET = run.ET
cfg, b = Config(), Broker()
live = [t for t in risk_manager.closed_trades(risk_manager._rows(cfg)) if t["day"] >= "2026-11-05" and t["group"] == "sip_orb"]
rows = [r for r in shadow.load(cfg) if r["strategy"] in ("sip_orb", "sip_orb_wide") and r.get("exit_time")]
# entry times for live trades from trades.csv
buys = {}
for r in csv.DictReader(open(cfg.journal_path)):
    if r["event"] == "buy" and "[sip_orb]" in r["note"] and r["time"] >= "2026-11-05":
        buys.setdefault((r["time"][:10], r["symbol"]), r["time"])
items = [("live", t["day"], t["symbol"], buys.get((t["day"], t["symbol"])), t["r"]) for t in live]
items += [("shadow:" + r["strategy"], r["time"][:10], r["symbol"], r["time"], float(r["r"])) for r in rows]
cache = {}
out = []
for kind, day, sym, ts, r in items:
    if not ts:
        continue
    if day not in cache:
        close_ = datetime.fromisoformat(day).replace(hour=16, tzinfo=ET)
        run._DAY.clear()
        ctx = run.day_data(b, cfg, close_)
        sb = b.bars(["SPY"], "1Min", close_.replace(hour=9, minute=30).isoformat(), end=close_.isoformat(), feed=cfg.data_feed)["SPY"]
        cache[day] = (ctx, sb)
    ctx, sb = cache[day]
    t = datetime.fromisoformat(ts).astimezone(ET)
    upto = [x for x in sb if strategies.bar_time(x) < t.replace(second=0, microsecond=0)]
    bands = strategies.noise_bands(upto, run.prior_close(ctx, "SPY"), ctx["sigma"]) if upto else None
    ok = strategies.spy_ok_for_longs(upto, bands)
    out.append((kind, day, sym, ts[11:16], r, ok))
def stats(xs):
    if not xs: return "0 trades"
    w = sum(x for x in xs if x > 0); l = -sum(x for x in xs if x < 0)
    return f"{len(xs)} trades, avg {sum(xs)/len(xs):+.2f}R, PF {w/l if l else float('inf'):.2f}, wins {sum(1 for x in xs if x>0)}"
lines = ["# sip_orb_mkt backfill (11-05 to %s)" % max(o[1] for o in out), "",
         "Filter: SPY's last 1-min close at entry >= its 9:30 open and not below the lower noise band. "
         "In-sample: the filter was designed by looking at these trades, so this flatters it. Only forward trades count toward its 40.", "",
         "| Set | All | Filter passes | Filter blocks |", "|---|---|---|---|"]
for k in ("live", "shadow:sip_orb", "shadow:sip_orb_wide"):
    xs = [o for o in out if o[0] == k]
    lines.append(f"| {k} | {stats([o[4] for o in xs])} | {stats([o[4] for o in xs if o[5]])} | {stats([o[4] for o in xs if not o[5]])} |")
allsip = [o for o in out if o[0] in ("live", "shadow:sip_orb")]
lines.append(f"| sip_orb live+shadow | {stats([o[4] for o in allsip])} | {stats([o[4] for o in allsip if o[5]])} | {stats([o[4] for o in allsip if not o[5]])} |")
lines += ["", "| Kind | Day | Symbol | Entry | R | Filter |", "|---|---|---|---|---|---|"]
lines += [f"| {o[0]} | {o[1]} | {o[2]} | {o[3]} | {o[4]:+.2f} | {'pass' if o[5] else 'block'} |" for o in sorted(out, key=lambda o: (o[1], o[3]))]
print("\n".join(lines))
