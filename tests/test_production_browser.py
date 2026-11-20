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
            assert page.locator("#gax-title").inner_text().strip().lower() == "gax100 splits"
            page.wait_for_function("() => {const x=document.querySelector('.gax-hero-image');return x?.complete && x.naturalWidth >= 1100;}",timeout=16000)
            assert page.locator(".gax-hero-image").get_attribute("src")=="assets/hero-ales-stenar-trail-runners.webp"
            assert "GAX100 Analys 1.2" in page.title()
            assert page.locator(".gax-station-point.gax-station-terminal").count() == 2
            assert page.locator(".gax-cutoffs tbody tr").count() >= 9
            config = page.evaluate("() => fetch('data/replay-audio.json').then(r => r.json())")
            assert config["src"].startswith("assets/audio/")
            assert "AudioERA" in config["credit"]
            sound=page.request.head(f"http://127.0.0.1:{server.server_port}/"+config["src"])
            assert sound.status==200, "Original soundtrack must be deployed with the release"
            assert "audio/" in sound.headers.get("content-type","")
            provenance=page.request.get(f"http://127.0.0.1:{server.server_port}/data/historical-checkpoint-km.json")
            assert provenance.status==200
            assert len(provenance.json()["editions"])==14
            assert page.locator("#year-select option").count()==14
            assert page.locator(".gax-preview-note").is_hidden()
            assert page.locator(".gax-production-copy").first.is_visible()
            assert "DESIGNDEMO" not in page.locator("#source-indicator").inner_text()
            assert page.locator(".gax-demo-copy").first.is_hidden()
            page.locator("#method > .gax-added-info").click()
            help_text = page.locator("#help-content").inner_text().lower()
            assert "officiella tävlingsresultat" in help_text
            assert "påhittade" not in help_text, "The release must not present real runners as fictional"
            page.locator("#help-dialog [data-close='help-dialog']").click()
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 2"), "Mobile overflow"
            # Select the official 2023 table where multiple source checkpoints exist.
            page.select_option("#year-select","2023-gax100")
            page.wait_for_function("() => document.querySelector('#scope-status')?.textContent.includes('90')",timeout=20000)
            assert "Officiella GAX100-källor" in page.locator("#source-indicator").inner_text()
            assert page.locator("#results-table tbody tr").count()>1
            page.wait_for_function("() => document.querySelector('#gax-controls-content')?.textContent.includes('44 km (årsresultat)')",timeout=12000)
            page.locator("#results-table [data-open]").first.click()
            assert page.locator("#profile-dialog").evaluate("(el) => el.open")
            assert page.locator("#gax-runner-checkpoints tbody tr").count() >= 2
            assert "Officiella" in page.locator("#gax-runner-checkpoints h3").inner_text()
            if page.locator("#profile-dialog [data-replay-music]").count():
                page.wait_for_function("() => !document.querySelector('#profile-dialog [data-replay-music]').disabled",timeout=18000)
                assert "AudioERA" in page.locator("#profile-dialog .replay-music-credit").inner_text()
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
            # Older GAX code preserved TIME even if historical km was unknown.
            # This was accidentally regressed by requiring finite(st.km) for
            # profile passage rows. Validate actual 2024/2021 source timing.
            for key, total in [("2021-a-gax100",38),("2024-gax100",87)]:
                page.select_option("#year-select",key)
                page.wait_for_function("(n) => document.querySelector('#scope-status')?.textContent.includes(String(n))",arg=total,timeout=20000)
                page.locator("#results-table [data-open]").first.click()
                assert page.locator("#profile-dialog").evaluate("(el) => el.open")
                source_table=page.locator(".profile-source-passages")
                assert source_table.count()==1 and source_table.evaluate("(el) => el.open")
                assert source_table.locator("tbody tr").count()==5, "Historical source TIME controls must not be filtered for null km"
                assert source_table.locator("td").filter(has_text="Haväng").count()>=1
                assert "referens" in source_table.inner_text().lower() or "källkonflikt" in source_table.inner_text().lower()
                assert page.locator(".profile-split-table tbody tr").count()>=3, "Source-time segments should survive absent km"
                assert "3/4" in page.locator(".profile2-facts").inner_text() or "4/4" in page.locator(".profile2-facts").inner_text()
                page.locator("#profile-dialog [data-close='profile-dialog']").first.click()
            # 2019: year source has class-conflicting km and must not collapse it.
            page.select_option("#year-select","2019-gax100")
            page.wait_for_function("() => document.querySelector('#gax-controls-content')?.textContent.includes('källkonflikt')",timeout=20000)
            assert "43–44 km" in page.locator("#gax-controls-content").inner_text()
            # 2024: current organizer reference may be shown but not claimed for 2024.
            page.select_option("#year-select","2024-gax100")
            page.wait_for_function("() => document.querySelector('#gax-controls-content')?.textContent.includes('referens, ej årsverifierat')",timeout=20000)
            # Finish-only source years must remain finish-only, not invent checkpoints.
            for key, total in [("2025-gax100",119),("2026-gax100",110)]:
                page.select_option("#year-select",key)
                page.wait_for_function("(n) => document.querySelector('#scope-status')?.textContent.includes(String(n))",arg=total,timeout=20000)
                assert "Officiella GAX100-källor" in page.locator("#source-indicator").inner_text()
                result = page.evaluate("(key) => fetch('data/races/'+key+'.json').then(r=>r.json()).then(j=>j.stations.length)",key)
                assert result==1, "A finish-only year acquired fictitious checkpoints"
                assert page.locator("#gax-controls-content .gax-start-control").count()==1
                page.wait_for_function("() => document.querySelector('#extra-dynamics')?.hidden === true",timeout=15000)
                assert page.locator("#extra-dynamics").is_hidden()
                assert page.locator("#extra-segments").is_hidden()
                assert page.locator("#standouts").locator("xpath=ancestor::article[1]").is_hidden()
                assert page.locator("#extra-overview #age-chart").locator("xpath=ancestor::article[1]").is_hidden()
                # Open a real, source-FINISHED profile and verify nominal pace.
                page.locator("#results-table [data-open]").first.click()
                assert page.locator("#profile-dialog").evaluate("(el) => el.open")
                facts=page.locator(".profile2-facts").inner_text()
                assert "Snittfart" in facts
                assert "nominell 100 miles" in facts
                assert "min/km" in facts or "/km" in facts
                assert page.locator("#gax-runner-checkpoints .gax-start-control").count()==1
                assert page.locator("#gax-runner-checkpoints tbody tr").count()==2
                assert "bara officiell målpassage" in page.locator("#gax-runner-checkpoints").inner_text()
                page.locator("#profile-dialog [data-close='profile-dialog']").first.click()
            assert not errors, f"Browser JavaScript error types: {errors}"
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
    print("GAX100_V1_2_BROWSER_PASS: original imagery and audio, 14 source years, km provenance conflicts, responsive data hiding, real profiles/comparisons")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--site",required=True,type=Path)
    check(parser.parse_args().site)
