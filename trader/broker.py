"""Thin REST client for Alpaca. Hard-wired to the paper endpoint."""
import os

import requests

from .config import DATA_URL, PAPER_URL


class LiveTradingRefused(RuntimeError):
    pass


class Broker:
    def __init__(self, key_id=None, secret=None, session=None):
        base = os.environ.get("APCA_API_BASE_URL", PAPER_URL).rstrip("/")
        if base != PAPER_URL:
            raise LiveTradingRefused(f"refusing non-paper endpoint {base}")
        self.base = PAPER_URL
        self.s = session or requests.Session()
        self.s.headers.update({
            "APCA-API-KEY-ID": key_id or os.environ["APCA_API_KEY_ID"],
            "APCA-API-SECRET-KEY": secret or os.environ["APCA_API_SECRET_KEY"],
        })

    def _req(self, method, url, **kw):
        r = self.s.request(method, url, timeout=15, **kw)
        if r.status_code >= 400:
            raise RuntimeError(f"{method} {url} -> {r.status_code}: {r.text[:200]}")
        return r.json() if r.content else None

    # trading API
    def account(self):
        return self._req("GET", f"{self.base}/v2/account")

    def clock(self):
        return self._req("GET", f"{self.base}/v2/clock")

    def positions(self):
        return self._req("GET", f"{self.base}/v2/positions")

    def open_orders(self):
        return self._req("GET", f"{self.base}/v2/orders", params={"status": "open"})

    def bracket_buy(self, symbol, qty, stop, target, client_id):
        return self._req("POST", f"{self.base}/v2/orders", json={
            "symbol": symbol, "qty": str(qty), "side": "buy", "type": "market",
            "time_in_force": "day", "order_class": "bracket",
            "client_order_id": client_id,
            "take_profit": {"limit_price": f"{target:.2f}"},
            "stop_loss": {"stop_price": f"{stop:.2f}"},
        })

    def buy_market(self, symbol, qty, client_id):
        return self._req("POST", f"{self.base}/v2/orders", json={
            "symbol": symbol, "qty": str(qty), "side": "buy", "type": "market",
            "time_in_force": "day", "client_order_id": client_id})

    def sell_stop(self, symbol, qty, stop):
        return self._req("POST", f"{self.base}/v2/orders", json={
            "symbol": symbol, "qty": str(qty), "side": "sell", "type": "stop",
            "stop_price": f"{stop:.2f}", "time_in_force": "day"})

    def order(self, order_id):
        return self._req("GET", f"{self.base}/v2/orders/{order_id}")

    def cancel(self, order_id):
        return self._req("DELETE", f"{self.base}/v2/orders/{order_id}")

    def close_position(self, symbol):
        return self._req("DELETE", f"{self.base}/v2/positions/{symbol}")

    def latest_price(self, symbol, feed="iex"):
        d = self._req("GET", f"{DATA_URL}/v2/stocks/{symbol}/trades/latest", params={"feed": feed})
        return float(d["trade"]["p"])

    def flatten(self):
        """Cancel all orders and close all positions."""
        return self._req("DELETE", f"{self.base}/v2/positions", params={"cancel_orders": "true"})

    def closed_orders(self, after_iso):
        return self._req("GET", f"{self.base}/v2/orders",
                         params={"status": "closed", "after": after_iso, "limit": 500, "nested": "true"})

    # market data API
    def bars(self, symbols, timeframe, start, end=None, feed="iex", adjustment="raw"):
        """Return {symbol: [bar, ...]} with every page fetched."""
        out, token = {}, None
        while True:
            params = {"symbols": ",".join(symbols), "timeframe": timeframe, "start": start,
                      "feed": feed, "limit": 10000, "adjustment": adjustment}
            if end:
                params["end"] = end
            if token:
                params["page_token"] = token
            d = self._req("GET", f"{DATA_URL}/v2/stocks/bars", params=params)
            for sym, bs in (d.get("bars") or {}).items():
                out.setdefault(sym, []).extend(bs)
            token = d.get("next_page_token")
            if not token:
                return out
