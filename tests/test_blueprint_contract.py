#!/usr/bin/env python3
"""Source-only, non-identifying public GAX100 blueprint safeguards."""
from __future__ import annotations
import json
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/"docs"
class BlueprintContract(unittest.TestCase):
    def test_sae_tila_blueprint_structure(self):
        html=(DOCS/"index.html").read_text(encoding="utf-8")
        expected=("runner-tools","map-duel-builder","overview","dynamics",
                  "segments","course","history","results","method",
                  "profile-dialog","compare-dialog","year-select")
        for item in expected:
            self.assertIn('id="'+item+'"',html)
        self.assertIn('data-family="gax100"',html)
        self.assertNotIn("Lygnern",html)
        self.assertNotIn("EQ Timing",html)
        self.assertEqual(len(re.findall(r'data-family="gax100"',html)),1)

    def test_osterlen_summer_design_and_nonfiction_sources(self):
        html=(DOCS/"index.html").read_text(encoding="utf-8")
        for anchor in ("landscape","stations-guide","gax-title","race-context"):
            self.assertIn('id="'+anchor+'"',html)
        self.assertEqual(html.count('class="gax-stage '),4)
        self.assertEqual(html.count('class="gax-station-point"'),5)
        self.assertIn("Brösarps backar",html)
        self.assertIn("Sandhammaren",html)
        self.assertIn("2027",html)
        css=(DOCS/"assets/gax.css").read_text(encoding="utf-8")
        self.assertIn(".gax-hero{",css)
        self.assertIn("min-height:0!important",css)
        self.assertIn(".gax-summer-scene",css)
        self.assertIn("@media(max-width:470px)",css)
        self.assertNotIn("url(https://",css)

    def test_duel_uses_built_in_geometry_without_file_input(self):
        html=(DOCS/"index.html").read_text(encoding="utf-8")
        js=(DOCS/"assets/app.js").read_text(encoding="utf-8")
        self.assertIn('id="open-map-duel"',html)
        self.assertNotIn('type="file"',html)
        self.assertNotIn("loadGaxLocalGPX",js)
        self.assertIn("gaxReplayRoute",js)
        self.assertFalse(any(DOCS.rglob("*.gpx")))

    def test_only_aggregate_public_data(self):
        data=DOCS/"data"
        boot=json.loads((data/"bootstrap.json").read_text(encoding="utf-8"))
        self.assertEqual(boot["event"],"GAX 100 miles")
        self.assertEqual(len(boot["editions"]),14)
        self.assertEqual([f["id"] for f in boot["families"]],["gax100"])
        self.assertEqual(sum(e["results"] for e in boot["editions"]),945)
        self.assertEqual(sum(e["finishers"] for e in boot["editions"]),651)
        self.assertEqual(sum(e["split_observations"] for e in boot["editions"]),1838)
        year23=next(e for e in boot["editions"] if e["year"]==2023)
        self.assertEqual((year23["results"],year23["finishers"]),(90,70))
        keys={e["race_key"] for e in boot["editions"]}
        self.assertEqual(len(keys),14)
        self.assertIn("2021-a-gax100",keys)
        self.assertIn("2021-b-gax100",keys)
        for key in keys:
            race=json.loads((data/"races"/(key+".json")).read_text(encoding="utf-8"))
            self.assertEqual(race["family"],"gax100")
            self.assertEqual(race["release_state"],"PRIVATE_DATA_WITHHELD")
            self.assertEqual(race["results"],[])
            self.assertEqual(race["splits"],[])
            self.assertEqual(race["stations"],[])
            self.assertFalse(race["distance_verified"])
            self.assertEqual(race["route_status"],"none")
        self.assertEqual(len(list((data/"races").glob("*.json"))),14)
        self.assertEqual(json.loads((data/"route-inventory.json").read_text(encoding="utf-8")),[])

    def test_no_raw_sources_or_copyrighted_sae_tila_assets(self):
        for path in DOCS.rglob("*"):
            if path.is_file():
                self.assertNotIn(path.suffix.lower(),{".sqlite",".db",".pdf",".fit",".gpx",".kmz",".mp3",".webp"})
                self.assertNotIn("satila",path.name.lower())
        js=(DOCS/"assets"/"app.js").read_text(encoding="utf-8")
        self.assertIn("editionKey",js)
        self.assertIn("PRIVATE_DATA_WITHHELD",js)
        self.assertIn("GaxCheckpointView?.render",js)
        self.assertIn("GaxCheckpointView?.renderComparison",js)
        self.assertIn("GaxCheckpointView?.renderProfile",js)
        self.assertIn("PRIVATE_DATA_WITHHELD", (DOCS/"data/races/2023-gax100.json").read_text(encoding="utf-8"))
        checkpoint=(DOCS/"assets/gax-controls.js").read_text(encoding="utf-8")
        self.assertIn("st.values.length>=5",checkpoint)
        self.assertIn("source-only",checkpoint)
        self.assertNotIn("Ramhulta",checkpoint)
        self.assertNotIn("satila-trail.mp3",js)

if __name__=="__main__":
    unittest.main(verbosity=2)
