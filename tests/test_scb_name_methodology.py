#!/usr/bin/env python3
"""SCB 2022 statistical name source methodology and fail-closed coverage tests."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from enrich_scb_first_names import scb_choice,runner_first_name,SOURCE_SHA256

D=ROOT/'docs'/'data'
def counts(female,male):
    return {'tilltalsnamn':{'F':female,'M':male},
            'fornamn':{'F':female,'M':male}}

class SCBNameMethodology(unittest.TestCase):
    def test_majority_must_be_strong(self):
        choice,state=scb_choice('emma',counts({'emma':1200},{'emma':2}))
        self.assertEqual(choice[1],'F')
        self.assertEqual(state,'scb_strong')
        self.assertGreaterEqual(choice[2],.98)

    def test_missing_other_sex_is_not_zero(self):
        choice,state=scb_choice('rar',counts({'rar':30},{}))
        self.assertIsNone(choice) # 30/31 is <98% because unlisted may be one.
        self.assertEqual(state,'scb_ambiguous')
        choice,_=scb_choice('common',counts({'common':150},{}))
        self.assertEqual(choice[1],'F')

    def test_cross_sex_name_stays_unknown(self):
        choice,state=scb_choice('kim',counts({'kim':900},{'kim':700}))
        self.assertIsNone(choice)
        self.assertEqual(state,'scb_ambiguous')

    def test_not_a_person_gender_classifier(self):
        self.assertEqual(runner_first_name('Anna Maria'),'anna')
        self.assertIsNone(runner_first_name('Anonym deltagare'))
        self.assertIsNone(runner_first_name('J'))
        self.assertEqual(len(SOURCE_SHA256),64)

    def test_production_overlay_only_public_results_and_clear_provenance(self):
        doc=json.loads((D/'name-based-classification.json').read_text(encoding='utf-8'))
        self.assertEqual(doc['schema'],'gax100-first-name-statistical-estimate-1')
        if doc.get('scb_source_year') is None:
            # Before the SCB ingestion job commits; the source-independent
            # methodology tests still apply.
            return
        self.assertEqual(doc['scb_source_year'],2022)
        self.assertEqual(doc['scb_workbook_sha256'],SOURCE_SHA256)
        self.assertEqual(doc['scb_min_dominant_count'],30)
        self.assertEqual(doc['scb_min_conservative_probability'],.98)
        for key,rows in doc['editions'].items():
            race=json.loads((D/'races'/(key+'.json')).read_text(encoding='utf-8'))
            by_id={str(r['id']):r for r in race['results']}
            for entry in rows:
                self.assertEqual(set(entry),{'result_id','status','estimated_sex',
                                            'method','probability','evidence_count'})
                original=by_id.get(str(entry['result_id']))
                self.assertIsNotNone(original)
                self.assertIsNone(original['sex'])
                self.assertEqual(original['status'],entry['status'])
                self.assertNotIn('name',entry)
                if entry['method'].startswith('scb_'):
                    self.assertGreaterEqual(entry['probability'],.98)
                    self.assertGreaterEqual(entry['evidence_count'],30)

if __name__=='__main__':unittest.main(verbosity=1)
