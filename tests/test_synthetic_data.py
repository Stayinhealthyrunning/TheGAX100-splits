#!/usr/bin/env python3
"""Full GAX synthetic dataset contract. No original participant records used."""
from __future__ import annotations
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from build_offline_preview import TIMING, prepare_payload, generate_demo, MODEL_SCHEMA


class FictionalRaceDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files=prepare_payload(ROOT/"docs")
        cls.boot=cls.files["data/bootstrap.json"]
        cls.races=[cls.files[f"data/races/{e['race_key']}.json"]
                   for e in cls.boot["editions"]]

    def test_full_14_editions_and_year_2023_source_counts(self):
        self.assertEqual(len(self.races),14)
        self.assertEqual(sum(len(r["results"]) for r in self.races),945)
        self.assertEqual(sum(sum(x["status"]=="FINISHED" for x in r["results"])
                             for r in self.races),651)
        self.assertEqual(len({r["race_key"] for r in self.races}),14)
        row23=next(r for r in self.races if r["year"]==2023)
        self.assertEqual((len(row23["results"]),
                          sum(x["status"]=="FINISHED" for x in row23["results"])),(90,70))

    def test_realistic_identity_names_sexes_and_fiction_labels(self):
        rows=[row for race in self.races for row in race["results"]]
        self.assertEqual(len({r["name"] for r in rows}),945)
        self.assertEqual({r["sex"] for r in rows},{"M","F"})
        self.assertTrue(all(r["name"].count(" ")>=1 for r in rows))
        self.assertTrue(all(r["id"].startswith("fiction-") and
                            r["bib"].startswith("F-") and
                            r["source_uid"] is None and r["demo_only"]
                            for r in rows))
        self.assertTrue(any(r["club"] for r in rows))
        self.assertTrue(any(not r["club"] for r in rows))

    def test_2026_published_sex_outcome_aggregate_is_preserved(self):
        race=next(r for r in self.races if r["year"]==2026)
        bysex=Counter((x["sex"],x["status"]) for x in race["results"])
        self.assertEqual([bysex["F",s] for s in ("FINISHED","DNF","DNS")],
                         [14,5,3])
        self.assertEqual([bysex["M",s] for s in ("FINISHED","DNF","DNS")],
                         [52,28,8])
        self.assertEqual(len(race["results"]),110)

    def test_checkpoints_and_reptid_reference(self):
        expected=[(uid,name,km) for uid,name,km,_ in TIMING]
        for race in self.races:
            self.assertEqual([(s["uid"],s["name"],s["km"]) for s in race["stations"]],
                             expected)
            self.assertFalse(race["distance_verified"])
            self.assertEqual(race["model_schema"],MODEL_SCHEMA)
            self.assertTrue(race["demo_only"])
            self.assertTrue(all(s["demo_only"] for s in race["stations"]))

    def test_all_times_monotonic_finalists_within_model_cutoffs(self):
        for race in self.races:
            byrunner=defaultdict(list)
            for sp in race["splits"]:
                byrunner[sp["result_id"]].append(sp)
                self.assertTrue(sp["demo_only"])
            for row in race["results"]:
                sequence=byrunner[row["id"]]
                sequence.sort(key=lambda sp:sp["station_uid"])
                seconds=[s["elapsed_seconds"] for s in sequence]
                self.assertEqual(seconds,sorted(seconds))
                self.assertEqual(len(set(seconds)),len(seconds))
                if row["status"]=="FINISHED":
                    self.assertEqual(len(sequence),len(TIMING))
                    self.assertEqual(seconds[-1],row["finish_seconds"])
                    self.assertLess(row["finish_seconds"],32*3600)
                    self.assertGreater(row["finish_seconds"],16*3600)
                    for sp,(_,_,_,limit) in zip(sequence,TIMING):
                        if limit:
                            self.assertLessEqual(sp["elapsed_seconds"],limit)
                elif row["status"]=="DNS":
                    self.assertEqual(sequence,[])
                    self.assertIsNone(row["finish_seconds"])
                elif row["status"]=="DNF":
                    self.assertGreater(len(sequence),0)
                    self.assertLess(len(sequence),len(TIMING))
                    self.assertIsNone(row["finish_seconds"])
                else:
                    self.assertIsNone(row["finish_seconds"])

    def test_ranks_are_monotonic_and_source_sums_unchanged(self):
        original=json.loads((ROOT/"docs/data/bootstrap.json").read_text(encoding="utf-8"))
        self.assertEqual(sum(e["split_observations"] for e in original["editions"]),1838)
        self.assertGreater(sum(e["split_observations"] for e in self.boot["editions"]),6500)
        for race in self.races:
            finishers=sorted((r for r in race["results"] if r["status"]=="FINISHED"),
                             key=lambda r:r["place"])
            self.assertEqual([r["place"] for r in finishers],list(range(1,len(finishers)+1)))
            self.assertEqual([r["finish_seconds"] for r in finishers],
                             sorted(r["finish_seconds"] for r in finishers))

    def test_reproducible_demo_build(self):
        other=prepare_payload(ROOT/"docs")
        for ed in self.boot["editions"]:
            key=f"data/races/{ed['race_key']}.json"
            self.assertEqual(self.files[key],other[key])


if __name__=="__main__":
    unittest.main(verbosity=2)
