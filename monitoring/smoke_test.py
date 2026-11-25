"""Read-only smoke test of the public SoundGraph user journey."""
import re
import time

from playwright.sync_api import sync_playwright, expect

URL = "https://soundgraph.streamlit.app/"
TIMEOUT = 120_000


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
            response = page.goto(URL, wait_until="domcontentloaded", timeout=60_000)
            if response is None or response.status >= 400:
                raise RuntimeError(f"Public app unavailable: HTTP {response.status if response else 'unknown'}")
            print(f"PASS: public URL responded HTTP {response.status}")

            # Normal public recovery flow, if Streamlit presents its sleep screen.
            heading = page.get_by_role("heading", name="SoundGraph", exact=True)
            wake = page.get_by_role("button", name=re.compile("get this app back up", re.I))
            expect(heading.or_(wake).first).to_be_visible(timeout=TIMEOUT)
            if wake.is_visible():
                print("INFO: Streamlit is asleep; requesting normal public wake-up")
                wake.click()
            expect(heading).to_be_visible(timeout=TIMEOUT)
            expect(page.get_by_text(re.compile("Neo4j conectado"))).to_be_visible(timeout=TIMEOUT)
            print("PASS: app initialized and Neo4j catalog loaded")

            choose(page, "Artista da música de referência", "Frank Zappa",
                   re.compile(r"^Frank Zappa\s*·\s*\d+\s+faixas?$"))
            choose(page, "Música de referência", "Willie the Pimp",
                   re.compile(r"^Willie the Pimp\s*·\s*1969$"))
            # Default hybrid method, 70% tags, 10 results.
            expect(page.get_by_role("heading", name="Recomendações", exact=True)).to_be_visible(timeout=TIMEOUT)
            expect(page.get_by_text("Zig Zag Wanderer", exact=True).first).to_be_visible(timeout=TIMEOUT)
            expect(page.get_by_text("62,71%", exact=True).first).to_be_visible(timeout=TIMEOUT)
            expect(page.get_by_role("heading", name="Graph Explorer", exact=True)).to_be_visible(timeout=TIMEOUT)
            print("PASS: hybrid recommendation Zig Zag Wanderer / 62.71% and Graph Explorer")
            print(f"PASS: smoke test completed in {time.monotonic()-start:.1f}s")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
