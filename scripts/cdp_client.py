# -*- coding: utf-8 -*-
"""Минимальный CDP-клиент (Chrome DevTools Protocol) поверх websocket-client.
Используем его, чтобы выполнять запросы ВНУТРИ браузера (fetch с куками сессии)."""
import json
import time
import urllib.request
import websocket  # websocket-client

CDP_HTTP = "http://localhost:9222"


def list_tabs():
    with urllib.request.urlopen(CDP_HTTP + "/json/list", timeout=8) as r:
        return json.load(r)


def find_page_tab(url_substr=""):
    """Возвращает вкладку типа 'page' (опц. с подстрокой в URL)."""
    tabs = [t for t in list_tabs() if t.get("type") == "page"]
    if url_substr:
        tabs = [t for t in tabs if url_substr in t.get("url", "")] or tabs
    return tabs[0] if tabs else None


class CDP:
    def __init__(self, tab):
        self.ws = websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=120)
        self._id = 0
        self.tab = tab

    def send(self, method, params=None, timeout=120):
        self._id += 1
        mid = self._id
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        deadline = time.time() + timeout
        while time.time() < deadline:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"CDP error in {method}: {msg['error']}")
                return msg.get("result", {})
        raise TimeoutError(f"CDP timeout: {method}")

    def evaluate(self, expression, await_promise=False, timeout=120):
        res = self.send("Runtime.evaluate", {
            "expression": expression,
            "awaitPromise": await_promise,
            "returnByValue": True,
            "timeout": timeout * 1000,
        }, timeout=timeout + 10)
        if res.get("exceptionDetails"):
            raise RuntimeError("JS exception: " + json.dumps(res["exceptionDetails"])[:500])
        return res.get("result", {}).get("value")

    def navigate(self, url):
        self.send("Page.enable")
        return self.send("Page.navigate", {"url": url})

    def get_cookies(self):
        return self.send("Network.getAllCookies").get("cookies", [])

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass
