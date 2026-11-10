#!/usr/bin/env python3
"""GAX100 complete UX acceptance – all 8 requested improvements.

Tests only the public synthetic offline HTML, never original participant names,
locally protected GPS coordinates or historical private result files.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright


def run(path: Path):
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={"width":1440,"height":900})
        page.on("pageerror",lambda e:errors.append(type(e).__name__))
        page.goto(path.resolve().as_uri(),wait_until="domcontentloaded")
        page.wait_for_function("() => document.querySelector('#source-indicator')?.textContent.includes('DESIGNDEMO')",timeout=30000)
        page.wait_for_selector("#sex-completion .completion-pair",timeout=20000)

        # 1. Four stages plus aid-station timeline live solely in a modal.
        guide=page.locator("#gax-guide-dialog")
        assert not guide.evaluate("(el)=>el.open"),"Guide must be closed at page start"
        assert page.locator("#landscape").is_hidden(),"Stages must not occupy main vertical flow"
        page.locator("[data-gax-open-guide]").first.click()
        assert guide.evaluate("(el)=>el.open"),"Open-stages control failed"
        assert page.locator("#landscape .gax-stage").count()==4
        assert page.locator("#stations-guide .gax-station-point").count()==5
        assert page.locator("#stations-guide").is_visible()
        page.locator(".gax-guide-close").click()
        assert not guide.evaluate("(el)=>el.open"),"Guide modal did not close"

        # 2. Every primary analysis section has a meaningful explain-method control.
        section_ids=["runner-tools","map-duel-builder","overview","dynamics",
                     "segments","course","history","results"]
        for sid in section_ids:
            locator=page.locator(f"#{sid} > .section-heading .gax-added-info")
            assert locator.count()==1, f"Missing section info for {sid}"
            assert locator.get_attribute("aria-label"), f"Info lacks accessible label in {sid}"
        assert page.locator("#race-context .gax-added-info").count()==1
        assert page.locator("#method > .gax-added-info").count()==1
        page.locator("#overview > .section-heading .gax-added-info").click()
        assert page.locator("#help-dialog").evaluate("(el)=>el.open"),"Section explanation dialog did not open"
        explanation=page.locator("#help-content").inner_text().lower()
        assert len(explanation)>100 and ("simulerade" in explanation or "fiktiva" in explanation)
        page.locator("#help-dialog [data-close='help-dialog']").click()

        # 3. No duplicate wide classes panel, only a summary under Start till mål.
        assert page.locator(".overview-groups-wide").count()==0
        group=page.locator("#gax-group-summary")
        page.wait_for_selector("#gax-group-summary #group-bars",timeout=20000)
        assert group.is_visible(),"Classes and sex are missing under Start till mål"
        assert page.locator("#extra-overview #sex-completion").count()==1
        assert page.locator("#group-bars").locator("div").count()>0
        assert page.locator("#history #group-table").count()==0
        assert group.locator("details.gax-group-details").count()==1
        group.locator("details.gax-group-details summary").click()
        assert group.locator("#group-table tbody tr").count()>0

        # 4. Strongest finishers: 2026 has 66 fabricated finishers,
        # so both sex cohorts can be ranked.
        page.locator('#standouts [data-standout-tab="finish"]').click()
        finish=page.locator("#standout-active-panel")
        assert finish.is_visible()
        body=finish.inner_text()
        assert "Ingen verifierad prestation" not in body, "Strongest-finisher ranking is still n=0"
        assert "n=0" not in body, "No comparable runners were detected"

        # 5. Shared segments/personal plan, prefilled by median.
        page.locator('[data-gax-mode="personal"]').click()
        assert page.locator("#gax-segment-analytics").is_hidden()
        assert page.locator("#gax-personal-plan-panel").is_visible()
        assert page.locator("#extra-segments").is_hidden()
        original=page.locator("#target-time").input_value()
        assert original.count(":")>=1, "Personal plan must start at edition's median finish"
        page.locator("#target-time").fill("25:30:00")
        page.locator("#calculate-plan").click()
        page.wait_for_function("() => document.querySelectorAll('#plan-table tbody tr').length >= 8",timeout=10000)
        assert "25:30" in page.locator("#plan-summary").inner_text(), "Personal goal time was not applied"
        page.locator('[data-gax-mode="analysis"]').click()
        assert page.locator("#gax-segment-analytics").is_visible()
        assert page.locator("#gax-personal-plan-panel").is_hidden()
        assert page.locator("#extra-segments").is_visible()

        # 6. Duplicated unsubstantiated organizer-distance card is removed.
        metrics=page.locator("#course-intelligence .course-intel-card").first.locator(".dimension-grid > article")
        assert metrics.count()==6,f"Expected six independent dimension cards; found {metrics.count()}"
        assert page.locator("#course-intelligence").get_by_text("Tävlingsdistans",exact=True).count()==1

        # 7. Per-year women/men chart must use the FICTIONAL source,
        # never claim exact age/gender evidence from historical results.
        page.wait_for_selector("#history-sex .sex-history-bars",timeout=18000)
        assert page.locator("#history-sex .sex-history-bars > div").count()==14
        assert "DESIGNDEMO" in page.locator("#history-sex").inner_text()
        assert "2021" in page.locator("#history-sex").inner_text()

        # 8. Historical route metadata and source links are visible, without
        # loading a third-party GPX or pretending a candidate is official.
        page.wait_for_selector("#course-provenance .gax-route-table tbody tr",timeout=18000)
        table=page.locator("#course-provenance .gax-route-table")
        assert table.locator("tbody tr").count()==14
        assert "2310208" in page.locator("#course-provenance").inner_html()
        assert "484861455" in page.locator("#course-provenance").inner_html()
        assert "kandidat" in page.locator("#course-provenance").inner_text().lower()
        page.select_option("#year-select","2022-gax100")
        page.wait_for_function("() => document.querySelector('#race-title')?.textContent.includes('2022')")
        assert page.locator('input[type="file"]').count()==0
        assert "2310208" in page.locator("#course-source a").get_attribute("href")
        assert page.locator("#open-map-duel").is_disabled()
        assert not errors,f"Unexpected GAX browser JS errors: {errors}"
        browser.close()
    print("GAX_UX_FULL_REVIEW_PASS: modal, information, compact classes, strongest finish, plan, distance, sex trends, GPX status")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--file",required=True,type=Path)
    run(parser.parse_args().file)
