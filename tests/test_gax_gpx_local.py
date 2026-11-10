#!/usr/bin/env python3
"""Browser acceptance for built-in GAX routes, map zoom and replay."""
from __future__ import annotations
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright


def check_zoom(map_view):
    svg=map_view.locator("svg").first
    original=float(svg.get_attribute("viewBox").split()[2])
    map_view.locator('[data-gax-map-zoom="in"]').press("Enter")
    assert float(svg.get_attribute("viewBox").split()[2])<original
    map_view.locator('[data-gax-map-zoom="out"]').press("Enter")
    assert abs(float(svg.get_attribute("viewBox").split()[2])-original)<.01
    map_view.locator('[data-gax-map-zoom="in"]').press("Enter")
    map_view.locator('[data-gax-map-zoom="fit"]').press("Enter")
    assert abs(float(svg.get_attribute("viewBox").split()[2])-original)<.01


def check(file:Path):
    errors, writes=[],[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={"width":1280,"height":900})
        page.on("pageerror",lambda e:errors.append(type(e).__name__))
        page.on("request",lambda req:writes.append(req.method)
                if req.method not in ("GET","HEAD") else None)
        page.route("https://tile.openstreetmap.org/**",lambda route:route.abort())
        page.goto(file.resolve().as_uri(),wait_until="domcontentloaded")
        page.wait_for_selector("#year-select option",state="attached",timeout=20000)
        page.wait_for_function("()=>document.querySelector('#source-indicator')?.textContent.includes('DESIGNDEMO')")
        assert page.locator("#year-select").input_value()=="2026-gax100"
        course_map=page.locator("#course-map")
        course_map.locator("svg").wait_for(state="visible")
        assert "GPX 2026" in page.locator("#course-source").inner_text()
        assert page.locator('input[type="file"]').count()==0
        check_zoom(course_map)
        assert course_map.locator(".osm-tile-layer image").first.get_attribute("href").startswith("https://tile.openstreetmap.org/")
        assert course_map.locator(".osm-tile-layer image").first.evaluate("(el)=>getComputedStyle(el).opacity")=="0.94"
        editions=page.locator("#year-select option").evaluate_all(
            "(options)=>options.map(o=>[o.value,o.textContent.split(' · ')[0]])"
        )
        assert len(editions)==14
        for key,label in editions:
            if key=="2026-gax100":
                continue
            year=int(label[:4])
            source=2026 if year>=2025 else 2022 if year>=2022 else 2021
            page.select_option("#year-select",key)
            page.wait_for_function(
                """([source,label,isReference])=>{
                  const note=document.querySelector('#course-source').textContent;
                  return note.includes('GPX '+source) && (isReference
                    ?note.includes('Vald upplaga · '+label+'.'):note.startsWith('Visad bana · GPX '+source));
                }""",
                arg=[source,label,source!=year or year==2021],
            )
            note=page.locator("#course-source").inner_text()
            if source!=year or year==2021:
                assert "Vald upplaga · "+label+"." in note
                assert "referens" in note
            assert course_map.locator(".route-gold").is_visible()
            assert course_map.locator(".route-gold").get_attribute("d").count("M")==(
                59 if source==2021 else 1
            )
        page.locator("#gax-course-layers summary").click()
        layers=page.locator("#gax-course-layer-map .gax-course-layer")
        layers.first.wait_for(state="visible")
        assert layers.count()==4
        check_zoom(page.locator("#gax-course-layer-map"))
        page.locator("#gax-course-layer-choices input").first.uncheck()
        assert layers.count()==3
        page.locator("#gax-course-layers summary").click()
        page.select_option("#year-select","2026-gax100")
        page.wait_for_function("()=>document.querySelector('#course-source').textContent.includes('GPX 2026')")
        def names_for(key):
            return page.evaluate(
                """async (key)=> (await (await fetch('data/races/'+key+'.json')).json())
                  .results.filter(r=>r.status==='FINISHED').slice(0,2).map(r=>r.name)""",
                key,
            )

        def move(slider):
            maxv=float(slider.get_attribute("max"))
            slider.evaluate(
                "(el,val)=>{el.value=String(val);el.dispatchEvent(new Event('input',{bubbles:true}));}",
                maxv*.63,
            )

        names=names_for("2026-gax100")
        page.locator("#results-table [data-open]").first.click()
        personal=page.locator("#profile-mini-map")
        assert "GPX 2026" in page.locator("#profile-replay-stage").inner_text()
        before=personal.locator("[data-route-cursor]").get_attribute("cx")
        move(page.locator("#profile-replay-range"))
        assert personal.locator("[data-route-cursor]").get_attribute("cx")!=before
        check_zoom(personal)
        page.locator("#profile-dialog [data-close='profile-dialog']").first.click()

        for name in names:
            page.locator("#map-duel-search").fill(name)
            page.locator("[data-map-duel-id]").first.click()
        assert page.locator("#open-map-duel").is_enabled()
        page.locator("#open-map-duel").click()
        assert "GPX 2026" in page.locator("#map-duel-content").inner_text()
        assert "fiktiva" in page.locator("#map-duel-content").inner_text().lower()
        duel=page.locator("#map-duel-map")
        assert duel.locator("[data-runner-marker]").count()==2
        before=duel.locator("[data-runner-marker]").first.get_attribute("cx")
        move(page.locator("#map-duel-clock"))
        assert duel.locator("[data-runner-marker]").first.get_attribute("cx")!=before
        assert page.locator("#map-duel-leaderboard tbody tr").count()==2
        check_zoom(duel)
        page.locator("#map-duel-dialog [data-close='map-duel-dialog']").first.click()

        page.select_option("#multi-year-year","2021-b-gax100")
        page.locator("#multi-year-search").fill(names_for("2021-b-gax100")[0])
        page.locator("[data-multi-year-add]").first.click()
        page.locator("#open-multi-year-comparison").click()
        cross=page.locator("#multi-year-map-root")
        cross.locator("[data-map-path]").first.wait_for(state="visible")
        assert "GPX 2021" in cross.inner_text() and "GPX 2026" in cross.inner_text()
        assert cross.locator("[data-map-path]").count()==3
        assert cross.locator("[data-map-path] path").last.get_attribute("d").count("M")==59
        move(cross.locator("[data-map-range]"))
        assert cross.locator("[data-map-marker][transform]").count()==3
        cross.locator('[data-map-zoom="1"]').press("Enter")
        assert not writes, "Original GPX should never upload or send POST/PUT"
        assert not errors,f"Browser errors: {errors}"
        browser.close()
    print("GAX_MAP_REPLAY_PASS: all editions, zoom, overlays, individual replay and same-/cross-year Kartduell")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--file",required=True,type=Path)
    check(parser.parse_args().file)
