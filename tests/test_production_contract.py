#!/usr/bin/env python3
"""Fail-closed v1.0 checks for already privacy-filtered PUBLIC result files.

Never prints participant names, identifiers, source registries or row content.
Private preprocessing and opt-out decisions remain upstream prerequisites.
"""
from __future__ import annotations
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_pages import verify_release

DATA = ROOT / "docs" / "data"

class ProductionContract(unittest.TestCase):
    def test_manifest_and_totals(self):
        verify_release(DATA)
        boot = json.loads((DATA / "bootstrap.json").read_text(encoding="utf-8"))
        self.assertEqual(len(boot["editions"]), 14)
        self.assertEqual(sum(x["results"] for x in boot["editions"]), 945)
        self.assertEqual(sum(x["finishers"] for x in boot["editions"]), 651)
        # Public split rows include official finish results represented as
        # finish-station passages; they are not all original intermediate reads.
        self.assertEqual(sum(x["split_observations"] for x in boot["editions"]), 2482)

    def test_all_rows_and_passages(self):
        boot = json.loads((DATA / "bootstrap.json").read_text(encoding="utf-8"))
        overall = Counter()
        for ed in boot["editions"]:
            key = ed["race_key"]
            race = json.loads((DATA / "races" / (key + ".json")).read_text(encoding="utf-8"))
            self.assertFalse(race.get("demo_only"), key)
            self.assertFalse(race.get("release_state"), key)
            self.assertFalse(race["distance_verified"], key)
            self.assertEqual(race["route_status"], "none", key)
            ids = set()
            by_id = {}
            for row in race["results"]:
                self.assertNotIn(row["id"], ids, key)
                ids.add(row["id"])
                by_id[str(row["id"])] = row
                self.assertTrue(isinstance(row.get("name"), str) and row["name"].strip(), key)
                self.assertIsNone(row.get("source_uid"), key)
                self.assertIsNone(row.get("age"), key)
                self.assertNotIn("demo_only", row, key)
                self.assertIn(row["status"], ("FINISHED", "DNF", "DNS", "DSQ", "UNKNOWN"), key)
                if row["status"] == "FINISHED":
                    self.assertTrue(isinstance(row.get("finish_seconds"), (int,float))
                                    and row["finish_seconds"] > 0, key)
                else:
                    self.assertIsNone(row.get("finish_seconds"), key)
            station_ids = {str(s["uid"]) for s in race["stations"]}
            pairs = set()
            for split in race["splits"]:
                self.assertIn(str(split["result_id"]), by_id, key)
                self.assertIn(str(split["station_uid"]), station_ids, key)
                pair = (str(split["result_id"]), str(split["station_uid"]))
                self.assertNotIn(pair, pairs, key)
                pairs.add(pair)
                self.assertTrue(isinstance(split.get("elapsed_seconds"), (int,float))
                                and split["elapsed_seconds"] >= 0, key)
                self.assertNotIn("demo_only", split, key)
                runner = by_id[str(split["result_id"])]
                if runner["status"] == "FINISHED":
                    self.assertLessEqual(split["elapsed_seconds"], runner["finish_seconds"] + 5, key)
            overall["rows"] += len(race["results"])
            overall["finish"] += sum(r["status"] == "FINISHED" for r in race["results"])
            overall["splits"] += len(race["splits"])
        self.assertEqual(overall, Counter(rows=945, finish=651, splits=2482))

    def test_page_metadata_and_privacy_contract(self):
        html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<meta name="robots" content="noindex, nofollow">', html)
        self.assertIn("https://www.loppanalys.se/integritet/", html)
        self.assertIn("GAX100 Analys 1.0", html)
        self.assertIn("gax-production-copy", html)
        self.assertNotIn("design-demo med fiktiva deltagare", html)

if __name__ == "__main__":
    unittest.main(verbosity=1)
