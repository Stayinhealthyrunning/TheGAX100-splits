#!/usr/bin/env python3
"""Live Chromium smoke tests for the privacy-filtered v1.0 Pages output.

Serves the exact staged static site from localhost. Only aggregate test
outcomes are printed; names and profiles never enter CI logs or artifacts.
"""
from __future__ import annotations
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def check(site: Path):
    assert (site / "index.html").is_file(), "Production build is missing"
    handler = partial(QuietHandler, directory=str(site.resolve()))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    errors = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width":390,"height":844})
            page.on("pageerror", lambda error: errors.append(type(error).__name__))
            page.goto(f"http://127.0.0.1:{server.server_port}/", wait_until="domcontentloaded")
            page.wait_for_function("() => document.querySelector('#source-indicator')?.textContent.includes('Officiella GAX100-källor')",timeout=30000)
            assert page.locator("html.gax-production").count()==1
            assert page.locator("#year-select option").count()==14
            assert page.locator(".gax-preview-note").is_hidden()
            assert page.locator(".gax-production-copy").first.is_visible()
            assert "DESIGNDEMO" not in page.locator("#source-indicator").inner_text()
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 2"), "Mobile overflow"
            # Select the official 2023 table where multiple source checkpoints exist.
            page.select_option("#year-select","2023-gax100")
            page.wait_for_function("() => document.querySelector('#scope-status')?.textContent.includes('90')",timeout=20000)
            assert "Officiella GAX100-källor" in page.locator("#source-indicator").inner_text()
            assert page.locator("#results-table tbody tr").count()>1
            page.locator("#results-table [data-open]").first.click()
            assert page.locator("#profile-dialog").evaluate("(el) => el.open")
            assert page.locator("#gax-runner-checkpoints tbody tr").count() >= 2
            assert "Officiella" in page.locator("#gax-runner-checkpoints h3").inner_text()
            page.locator("#profile-dialog [data-close='profile-dialog']").first.click()
            page.set_viewport_size({"width":1440,"height":900})
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 2"), "Desktop overflow"
            # Real participant names are used transiently for input only, never logged.
            names = page.evaluate("""async () => (await (await fetch('data/races/2023-gax100.json')).json()).results.filter(r=>r.status==='FINISHED').slice(0,2).map(r=>r.name)""")
            assert len(names)==2 and names[0]!=names[1]
            for name in names:
                page.locator("#map-duel-search").fill(name)
                page.locator("[data-map-duel-id]").first.click()
            assert page.locator("#open-compare").is_enabled()
            page.locator("#open-compare").click()
            assert page.locator("#compare-dialog").evaluate("(el) => el.open")
            assert page.locator("#gax-direct-controls tbody tr").count()>=2
            assert "officiella" in page.locator("#gax-direct-controls h3").inner_text().lower()
            page.locator("#compare-dialog [data-close='compare-dialog']").first.click()
            # Finish-only source years must remain finish-only, not invent checkpoints.
            for key, total in [("2025-gax100",119),("2026-gax100",110)]:
                page.select_option("#year-select",key)
                page.wait_for_function("(n) => document.querySelector('#scope-status')?.textContent.includes(String(n))",arg=total,timeout=20000)
                assert "Officiella GAX100-källor" in page.locator("#source-indicator").inner_text()
                result = page.evaluate("(key) => fetch('data/races/'+key+'.json').then(r=>r.json()).then(j=>j.stations.length)",key)
                assert result==1, "A finish-only year acquired fictitious checkpoints"
            assert not errors, f"Browser JavaScript error types: {errors}"
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
    print("GAX100_V1_PRODUCTION_BROWSER_PASS: 14 editions, real-source display, profiles, comparisons, mobile/desktop, finish-only safeguards")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--site",required=True,type=Path)
    check(parser.parse_args().site)
