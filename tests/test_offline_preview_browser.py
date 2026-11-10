#!/usr/bin/env python3
"""Acceptance: compact Österlen design and 945 real-looking FICTIONAL participants."""
from __future__ import annotations
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

def main(file: Path):
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=1)
        page.on("pageerror",lambda exc:errors.append(str(exc)[:320]))
        page.goto(file.resolve().as_uri(),wait_until="domcontentloaded")
        page.wait_for_selector("#year-select option",state="attached",timeout=25000)
        assert page.locator("#year-select option").count()==14,"All 14 editions must load"
        assert page.locator(".gax-offline-demo").count()==1,"Fictional-data warning missing"
        assert page.locator(".gax-stage").count()==4,"Four authentic course chapters missing"
        assert page.locator(".gax-station-point").count()==5,"2027 aid stations missing"
        assert "Österlen" in page.locator(".gax-hero").inner_text()
        assert "DESIGNDEMO" in page.locator(".gax-offline-demo").inner_text()
        page.wait_for_function("() => document.querySelector('#results-table tbody')?.querySelectorAll('tr').length > 1")
        mobile_hero=page.locator(".gax-hero").evaluate("(el)=>el.getBoundingClientRect().height")
        assert mobile_hero<500,f"Mobile hero still fills entire screen: {mobile_hero}"
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth+2"),"Mobile horizontal overflow"
        dataset=page.evaluate("""async () => (await (await fetch('data/races/2026-gax100.json')).json())""")
        assert len(dataset["results"])==110 and len([r for r in dataset["results"] if r["status"]=="FINISHED"])==66
        assert sum(r["sex"]=="F" and r["status"]=="FINISHED" for r in dataset["results"])==14
        assert all(r["demo_only"] and r["name"].count(" ")>=1 for r in dataset["results"])
        assert all(r["source_uid"] is None for r in dataset["results"])
        assert len(dataset["stations"])==10
        assert len(dataset["splits"])>700
        assert "Simulerad" in page.locator("#source-indicator").inner_text() or "DESIGNDEMO" in page.locator("#source-indicator").inner_text()
        page.select_option("#year-select","2021-a-gax100")
        page.wait_for_function("() => document.querySelector('#race-title')?.textContent.includes('2021-A')")
        page.select_option("#year-select","2021-b-gax100")
        page.wait_for_function("() => document.querySelector('#race-title')?.textContent.includes('2021-B')")
        page.select_option("#year-select","2023-gax100")
        page.wait_for_function("() => document.querySelector('#scope-status')?.textContent.includes('90')")
        assert page.locator("#results-table tbody tr").count()>0
        row=page.locator("#results-table [data-open]").first
        row.click()
        assert page.locator("#profile-dialog").evaluate("(el)=>el.open")
        assert page.locator("#gax-runner-checkpoints tbody tr").count()>=8
        assert "Simulerade" in page.locator("#gax-runner-checkpoints h3").inner_text()
        page.locator("#profile-dialog [data-close='profile-dialog']").first.click()
        page.set_viewport_size({"width":1440,"height":900})
        desktop_hero=page.locator(".gax-hero").evaluate("(el)=>el.getBoundingClientRect().height")
        assert desktop_hero<430,f"Desktop top section still excessive: {desktop_hero}"
        race_context_y=page.locator("#race-context").evaluate("(el)=>el.getBoundingClientRect().top + window.scrollY")
        assert race_context_y<520,f"Race selector appears too far below fold: {race_context_y}"
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth+2"),"Desktop horizontal overflow"
        names=page.evaluate("""async () => (await (await fetch('data/races/2023-gax100.json')).json()).results.filter(r=>r.status==='FINISHED').slice(0,2).map(r=>r.name)""")
        assert len(names)==2 and names[0]!=names[1]
        for name in names:
            page.locator("#map-duel-search").fill(name)
            page.locator("[data-map-duel-id]").first.click()
        assert page.locator("#open-compare").is_enabled()
        page.locator("#open-compare").click()
        assert page.locator("#compare-dialog").evaluate("(el)=>el.open")
        assert page.locator("#gax-direct-controls tbody tr").count()>=8
        assert "simulerade" in page.locator("#gax-direct-controls h3").inner_text().lower()
        assert not errors,f"Browser JS errors: {errors}"
        browser.close()
    print(f"OSTERLEN_BROWSER_PASS mobile_hero={mobile_hero:.0f}px desktop_hero={desktop_hero:.0f}px 14editions 10checkpoints 945fictional")
    print("No real names, source IDs or private files were used.")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--file",type=Path,required=True)
    main(parser.parse_args().file)
