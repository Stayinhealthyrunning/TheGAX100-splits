#!/usr/bin/env python3
"""Public-only Legends Tracking source reconnaissance; no participant data collected.

Checks live page and checkpoint view availability on organizer-linked 2024/2026
sites. Intentionally never prints or stores runner identities, device positions,
request query parameters, times, individual checkpoints, or raw HTML.
"""
from __future__ import annotations
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

TRACKERS = {
    "2024": "https://gax100.legendstracking.com/",
    "2026": "https://gax100-2026.legendstracking.com/",
}
CHECKPOINTS = ("magleberg", "haväng", "sandhammaren", "verkaån", "skillinge")
NAVLABELS = ("participantlist", "leaderboard", "checkpoint view", "statistics")
def inspect(page, year, url):
    response_categories=set()
    def track(response):
        parsed=urlsplit(response.url)
        # Only inspect host and endpoint category, never individual URL paths,
        # query strings or records potentially containing participant identifiers.
        if "legendstracking.com" not in (parsed.hostname or ""): return
        path=(parsed.path or "").lower()
        if any(x in path for x in ("/api/", "graphql", "/json")):
            response_categories.add("possible_data_service")
        if any(x in path for x in (".js", ".css")):
            response_categories.add("static_application")
    page.on("response",track)
    try:
        response=page.goto(url,wait_until="domcontentloaded",timeout=25000)
        page.wait_for_timeout(3500)
        body=page.locator("body").inner_text(timeout=8000).lower()
        found=sorted(cp for cp in CHECKPOINTS if cp in body)
        controls=[name for name in NAVLABELS if name in body]
        clicked=False
        try:
            checkpoint=page.get_by_text("Checkpoint View",exact=True).first
            if checkpoint.count() and checkpoint.is_visible():
                checkpoint.click(timeout=4500)
                page.wait_for_timeout(1500)
                clicked=True
        except Exception:
            pass
        body=page.locator("body").inner_text(timeout=8000).lower()
        found=sorted(set(found)|{cp for cp in CHECKPOINTS if cp in body})
        # Gate: this only tells us whether the public UI seems populated.
        # It NEVER proves an official individual passertime or position.
        print(f"Legends {year}: http={response.status if response else 'none'}; app_sections={len(controls)}; "
              f"checkpoint_view_clicked={clicked}; known_station_labels={','.join(found) or 'none'}; "
              f"network_categories={','.join(sorted(response_categories)) or 'none'}")
        if not found:
            print(f"Legends {year}: NO externally verified checkpoint metadata suitable for public import")
    except Exception as error:
        print(f"Legends {year}: source currently inaccessible ({type(error).__name__}); no data imported")

def main():
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True)
        try:
            page=browser.new_page(viewport={"width":1440,"height":900})
            for year,url in TRACKERS.items(): inspect(page,year,url)
        finally:
            browser.close()

if __name__=="__main__":
    main()
