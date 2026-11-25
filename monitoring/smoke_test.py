"""Read-only smoke test of the public SoundGraph user journey."""
import re
import time
from urllib.parse import urlsplit

from playwright.sync_api import Error, sync_playwright, expect

URL = "https://soundgraph.streamlit.app/"
TIMEOUT = 120_000
STARTUP_TIMEOUT = 90


def app_scope(page):
    """Find the app in the document or a Streamlit-hosted iframe."""
    deadline = time.monotonic() + STARTUP_TIMEOUT
    requested_wake = False
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.get_by_test_id("stSelectbox").first.is_visible() and frame.get_by_text("Artista da música de referência", exact=True).is_visible():
                    return frame
                wake = frame.get_by_role("button", name=re.compile(r"get this app back up|wake (?:up|the app)|start (?:the |this )?app", re.I))
                if not requested_wake and wake.first.is_visible():
                    print("INFO: requesting normal public wake-up", flush=True)
                    wake.first.click(timeout=5000)
                    requested_wake = True
                    deadline = time.monotonic() + STARTUP_TIMEOUT
            except Error:
                # A frame can detach or reload during startup.
                continue
        page.wait_for_timeout(1000)
    raise RuntimeError("App selector not visible within startup timeout")


def diagnostics(page, signals):
    # Keep logs public-safe: no HTML dumps, cookies, URL query strings or secrets.
    print("DIAGNOSTICS: browser state", flush=True)
    print(f"WebSocket events: {signals['websocket']}; page errors: {signals['page_error']}; failed requests: {signals['failed_request']}", flush=True)
    markers = {
        "SoundGraph": re.compile(r"SoundGraph", re.I),
        "Neo4j connected": re.compile(r"Neo4j conectado", re.I),
        "login": re.compile(r"sign in|log in|continue with google", re.I),
        "sleep": re.compile(r"sleep|asleep|wake|back up", re.I),
        "connection error": re.compile(r"Não foi possível consultar o Neo4j|connection error|websocket", re.I),
        "app error": re.compile(r"Traceback|application error|app has encountered an error", re.I),
    }
    for index, frame in enumerate(page.frames):
        try:
            host = urlsplit(frame.url).hostname or "(local frame)"
            body = frame.locator("body").inner_text(timeout=2000)
            matched = [name for name, pattern in markers.items() if pattern.search(body)]
            print(f"Frame {index}: host={host}; body_chars={len(body)}; markers={matched}", flush=True)
        except Error:
            print(f"Frame {index}: unavailable", flush=True)


def choose(page, label, search, option):
    widget = page.get_by_test_id("stSelectbox").filter(
        has=page.get_by_text(label, exact=True)
    )
    box = widget.get_by_role("combobox")
    expect(box).to_be_visible(timeout=TIMEOUT)
    box.click()
    box.fill(search)
    result = page.get_by_role("option", name=option)
    expect(result).to_be_visible(timeout=30_000)
    result.click()


def main():
    start = time.monotonic()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            page.set_default_timeout(30_000)
            signals = {"websocket": 0, "page_error": 0, "failed_request": 0}
            for event, key in [("websocket", "websocket"), ("pageerror", "page_error"), ("requestfailed", "failed_request")]:
                page.on(event, lambda _, key=key: signals.__setitem__(key, signals[key] + 1))
            response = page.goto(URL, wait_until="domcontentloaded", timeout=60_000)
            if response is None or response.status >= 400:
                raise RuntimeError(f"Public app unavailable: HTTP {response.status if response else 'unknown'}")
            print(f"PASS: public URL responded HTTP {response.status}")

            scope = app_scope(page)
            expect(scope.get_by_text(re.compile("Neo4j conectado"))).to_be_visible(timeout=TIMEOUT)
            print("PASS: app initialized and Neo4j catalog loaded")

            choose(scope, "Artista da música de referência", "Frank Zappa",
                   re.compile(r"^Frank Zappa\s*·\s*\d+\s+faixas?$"))
            choose(scope, "Música de referência", "Willie the Pimp",
                   re.compile(r"^Willie the Pimp\s*·\s*1969$"))
            # Default hybrid method, 70% tags, 10 results.
            expect(scope.get_by_role("heading", name=re.compile(r"^Recomendações"))).to_be_visible(timeout=TIMEOUT)
            expect(scope.get_by_text("Zig Zag Wanderer", exact=True).first).to_be_visible(timeout=TIMEOUT)
            expect(scope.get_by_text("62,71%", exact=True).first).to_be_visible(timeout=TIMEOUT)
            expect(scope.get_by_role("heading", name=re.compile(r"^Graph Explorer"))).to_be_visible(timeout=TIMEOUT)
            print("PASS: hybrid recommendation Zig Zag Wanderer / 62.71% and Graph Explorer")
            print(f"PASS: smoke test completed in {time.monotonic()-start:.1f}s")
        except Exception:
            if "page" in locals() and "signals" in locals():
                diagnostics(page, signals)
            raise
        finally:
            browser.close()


if __name__ == "__main__":
    main()
