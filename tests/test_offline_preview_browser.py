#!/usr/bin/env python3
"""Interactive offline acceptance: synthetic GAX UX, without real participants."""
from __future__ import annotations
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

def main(file:Path):
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={"width":390,"height":844})
        page.on("pageerror",lambda exc:errors.append(type(exc).__name__))
        page.goto(file.resolve().as_uri(),wait_until="domcontentloaded")
        page.wait_for_selector("#year-select option",state="attached",timeout=25000)
        assert page.locator("#year-select option").count()==14, "14 editions missing"
        assert page.locator(".gax-offline-demo").count()==1, "fictional data banner missing"
        assert page.locator("#results-table tbody tr").count()>0,"synthetic results missing"
        assert "Demolöpare" in page.locator("#results-table tbody").inner_text(),"demo results not displayed"
        assert "Demokontroll" in page.locator("#gax-controls-panel").inner_text().title(),"demo control panel empty"
        page.select_option("#year-select","2021-a-gax100")
        page.wait_for_function("() => document.querySelector('#race-title')?.textContent.includes('2021-A')")
        page.select_option("#year-select","2021-b-gax100")
        page.wait_for_function("() => document.querySelector('#race-title')?.textContent.includes('2021-B')")
        page.select_option("#year-select","2023-gax100")
        page.wait_for_function("() => document.querySelector('#scope-status')?.textContent.includes('90')")
        assert "Demolöpare" in page.locator("#results-table tbody").inner_text()
        page.locator("#results-table [data-open]").first.click()
        assert page.locator("#profile-dialog").evaluate("(el) => el.open")
        assert page.locator("#gax-runner-checkpoints tbody tr").count()>=1
        page.locator("#profile-dialog [data-close='profile-dialog']").first.click()
        page.set_viewport_size({"width":1440,"height":900})
        page.locator("#map-duel-search").fill("Demolöpare 2023-001")
        page.locator("[data-map-duel-id]").first.click()
        page.locator("#map-duel-search").fill("Demolöpare 2023-002")
        page.locator("[data-map-duel-id]").first.click()
        assert page.locator("#open-compare").is_enabled()
        page.locator("#open-compare").click()
        assert page.locator("#compare-dialog").evaluate("(el)=>el.open")
        assert page.locator("#gax-direct-controls tbody tr").count()>=1
        assert not errors, "browser JS errors"
        browser.close()
    print("OFFLINE_PREVIEW_BROWSER_PASS mobile390 desktop1440 14editions two_runners profile_controls")
    print("ONLY_FICTIONAL_NAMES_AND_SPLITS=true")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--file",type=Path,required=True)
    args=parser.parse_args()
    main(args.file)
