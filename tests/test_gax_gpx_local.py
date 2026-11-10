#!/usr/bin/env python3
"""2026-GPX Kartduell browser acceptance; fabricated GPX exists only in test RAM.

The 2026 organizer's actual course and original participants are NEVER fetched
or committed. The test models a 152 km synthetic test polyline in Skåne so
it can exercise GPX import, local-only behavior and full moving-marker UI.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

WAYPOINTS=[
    (55.426,13.820),(55.680,13.700),(55.720,14.100),(55.740,14.250),
    (55.680,14.340),(55.580,14.330),(55.380,14.280),(55.390,13.700),
    (55.426,13.820)
]

def synthetic_gpx():
    pts=[]
    for a,b in zip(WAYPOINTS,WAYPOINTS[1:]):
        for i in range(120):
            f=i/120
            pts.append((a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f))
    pts.append(WAYPOINTS[-1])
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<gpx version="1.1" creator="SYNTHETIC_TEST_ONLY" '
            'xmlns="http://www.topografix.com/GPX/1/1"><trk><name>TEST – EJ VERKLIG RUTT</name><trkseg>'
            +''.join(f'<trkpt lat="{lat:.8f}" lon="{lon:.8f}"><ele>{5+i%65}</ele></trkpt>'
                     for i,(lat,lon) in enumerate(pts))
            +'</trkseg></trk></gpx>')

def check(file:Path):
    errors, writes=[],[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={"width":1280,"height":900})
        page.on("pageerror",lambda e:errors.append(type(e).__name__))
        page.on("request",lambda req:writes.append(req.method)
                if req.method not in ("GET","HEAD") else None)
        page.goto(file.resolve().as_uri(),wait_until="domcontentloaded")
        page.wait_for_selector("#year-select option",state="attached",timeout=20000)
        page.wait_for_function("()=>document.querySelector('#source-indicator')?.textContent.includes('DESIGNDEMO')")
        assert page.locator("#year-select").input_value()=="2026-gax100"
        assert not page.locator("#gax-local-gpx-card").is_hidden()
        assert page.locator("#open-map-duel").is_disabled()
        assert page.locator(".gax-gpx-official-link").get_attribute("href")=="https://connect.garmin.com/app/course/484861455"
        page.locator("#gax-gpx-upload").set_input_files({
            "name":"TEST-gax100-2026.gpx",
            "mimeType":"application/gpx+xml",
            "buffer":synthetic_gpx().encode("utf-8")
        })
        page.wait_for_function("()=>document.querySelector('#gax-gpx-status')?.textContent.includes('inläst')")
        assert "km" in page.locator("#gax-gpx-status").inner_text()
        assert page.locator("#course-map svg").count()>0, "Imported GPX must draw a real local route map"
        names=page.evaluate("""async()=> (await (await fetch('data/races/2026-gax100.json')).json()).results.filter(r=>r.status==='FINISHED').slice(0,2).map(r=>r.name)""")
        assert len(names)==2 and names[0]!=names[1]
        for name in names:
            page.locator("#map-duel-search").fill(name)
            page.locator("[data-map-duel-id]").first.click()
        assert page.locator("#open-map-duel").is_enabled()
        page.locator("#open-map-duel").click()
        assert page.locator("#map-duel-dialog").evaluate("(el)=>el.open")
        assert "fiktiva" in page.locator("#map-duel-content").inner_text().lower()
        assert page.locator("#map-duel-map svg").count()>0, "Cartographic duel did not draw"
        assert page.locator("#map-duel-leaderboard tbody tr").count()==2
        dial=page.locator("#map-duel-clock")
        maxv=float(dial.get_attribute("max"))
        assert maxv>70_000
        dial.evaluate("(el,val)=>{el.value=String(val);el.dispatchEvent(new Event('input',{bubbles:true}));}",round(maxv*.63))
        assert "Tävlingsklocka" in page.locator("#map-duel-readout").inner_text()
        page.locator("#map-duel-dialog [data-close='map-duel-dialog']").first.click()
        page.select_option("#year-select","2023-gax100")
        # Race title changes before the async data and route controls finish;
        # check the actual source-link state, not just the year heading.
        page.wait_for_function("""() => document.querySelector('#race-title')?.textContent.includes('2023')
          && document.querySelector('#gax-gpx-source-link')?.getAttribute('href')?.includes('2332034')
          && document.querySelector('#gax-gpx-status')?.textContent.includes('2023')""",timeout=15000)
        assert page.locator("#gax-local-gpx-card").is_visible(), "2023 has a source-linked external route candidate"
        assert "2332034" in page.locator("#gax-gpx-source-link").get_attribute("href"), "2023 candidate source missing"
        assert page.locator("#open-map-duel").is_disabled(), "No historical GPX should leak from 2026 demo"
        page.select_option("#year-select","2026-gax100")
        page.wait_for_function("""() => document.querySelector('#race-title')?.textContent.includes('2026')
          && document.querySelector('#gax-gpx-status')?.textContent.includes('inläst')
          && document.querySelector('#gax-gpx-source-link')?.getAttribute('href')?.includes('484861455')""",timeout=15000)
        assert page.locator("#gax-local-gpx-card").is_visible(), "2026 local route should restore from RAM"
        page.reload(wait_until="domcontentloaded")
        page.wait_for_function("()=>document.querySelector('#source-indicator')?.textContent.includes('DESIGNDEMO')")
        assert "Ingen GPX inläst" in page.locator("#gax-gpx-status").inner_text(), "Local GPX must not persist"
        assert page.locator("#open-map-duel").is_disabled()
        assert not writes, "Original GPX should never upload or send POST/PUT"
        assert not errors,f"Browser errors: {errors}"
        browser.close()
    print("GAX_LOCAL_GPX_KARTDUELL_PASS: private-in-browser import, scoped to each selected edition, two moving runners, no upload, no persistence")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--file",required=True,type=Path)
    check(parser.parse_args().file)
