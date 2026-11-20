#!/usr/bin/env python3
"""Enrich already PUBLIC GAX100 results from explicit DUV/organizer race classes.

This is NOT a name-to-gender classifier. A participant is linked ONLY if:
  1. the person already exists in privacy-filtered public race JSON,
  2. DUV explicitly records M/F in the SAME event,
  3. both normalized full name and official finish time match uniquely.
We never pull DUV birth years, nationalities, profile IDs, or source-only names.
Logs are aggregate only; no names or source page content.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
RACES=ROOT/"docs"/"data"/"races"
OUTPUT=ROOT/"docs"/"data"/"official-result-classification.json"
DUV={
  "2014-gax100":23300,
  "2015-gax100":23772,
  "2016-gax100":39559,
  "2017-gax100":42393,
  "2018-gax100":49072,
  "2019-gax100":58792,
  "2020-gax100":65149,
  "2021-a-gax100":73171,
  "2021-b-gax100":73170,
  "2022-gax100":79309,
  "2023-gax100":96096,
  "2024-gax100":104698,
}
def norm(value):
    value=unicodedata.normalize("NFKD", str(value or ""))
    return "".join(c for c in value.lower() if c.isalnum() and not unicodedata.combining(c))
def seconds(value):
    match=re.search(r"(?<!\d)(\d{1,2}):(\d{2}):(\d{2})(?!\d)", str(value or ""))
    return sum(int(x)*(60**p) for x,p in zip(match.groups(),(2,1,0))) if match else None
def row_source_name(cells):
    for cell in cells:
        text=cell.get_text(" ",strip=True)
        if "," in text and re.search(r"[A-Za-zÅÄÖåäö],\s*[A-Za-zÅÄÖåäö]",text):
            lhs,rhs=text.split(",",1)
            if re.search(r"[A-Za-zÅÄÖåäö]",lhs) and re.search(r"[A-Za-zÅÄÖåäö]",rhs):
                return rhs.strip()+" "+lhs.strip()
    return None
def parse_public_duv(data):
    soup=BeautifulSoup(data,"html.parser")
    found=[]
    for tr in soup.find_all("tr"):
        cells=tr.find_all(["td","th"],recursive=False)
        if len(cells)<6: continue
        value=[c.get_text(" ",strip=True) for c in cells]
        sexes=[v for v in value if v in ("F","M")]
        times=[seconds(v) for v in value]
        times=[x for x in times if x is not None]
        name=row_source_name(cells)
        if len(sexes)!=1 or not times or not name:continue
        # Only an explicit positive finishing time from the public event table.
        sec=times[0]
        if sec<=0:continue
        first=value[0] if value else ""
        try:rank=int(first.strip())
        except (ValueError,TypeError):rank=None
        found.append((name,sexes[0],sec,rank))
    # De-duplicate any nested table or duplicated HTML markup row.
    result={}
    for name,sex,sec,rank in found:
        key=(norm(name),sec)
        if key in result and result[key]!=(sex,rank):
            raise ValueError("Conflicting DUV source classifications")
        result[key]=(sex,rank)
    return [(name,sex,sec,rank) for name,sex,sec,rank in found if result.get((norm(name),sec))==(sex,rank)]
def duv_page(event_id):
    url=f"https://statistik.d-u-v.org/getresultevent.php?event={event_id}"
    request=Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; GAX100-results-quality/1.0; public source verification)"})
    with urlopen(request,timeout=25) as response:
        data=response.read(1_500_001)
    if len(data)>=1_500_001 or len(data)<1000:raise ValueError("Invalid source size")
    return data
def find_unique_match(race, source_name, source_seconds):
    rows=[row for row in race["results"] if row["status"]=="FINISHED"
          and row.get("finish_seconds")==source_seconds and norm(row.get("name"))==norm(source_name)]
    return rows[0] if len(rows)==1 else None
def enrich_year(key, event_id):
    race=json.loads((RACES/(key+".json")).read_text(encoding="utf-8"))
    source=parse_public_duv(duv_page(event_id))
    seen=set()
    entries=[]
    for source_name,sex,sec,rank in source:
        row=find_unique_match(race,source_name,sec)
        if not row:continue
        if row["id"] in seen:raise ValueError("Duplicate public result match")
        seen.add(row["id"])
        if row.get("sex") in ("M","F") and row["sex"]!=sex:
            raise ValueError("Source sex discrepancy; review before publication")
        entries.append(dict(result_id=row["id"],sex=sex,finish_seconds=sec,overall_rank=rank))
    return entries,len(source),len([r for r in race["results"] if r["status"]=="FINISHED"])
def main():
    old=json.loads(OUTPUT.read_text(encoding="utf-8"))
    merged=old["editions"].copy()
    source_index=old.get("source_by_edition",{}).copy()
    good=0
    for key,event_id in DUV.items():
        try:
            rows,source_count,release_count=enrich_year(key,event_id)
            # Fail closed for very partial or blocked sources, keep older known-good.
            if len(rows)<min(3,release_count):
                print(f"{key}: no reliable matched results; previous data preserved")
                continue
            if key=="2024-gax100":
                female=sum(r["sex"]=="F" for r in rows)
                male=sum(r["sex"]=="M" for r in rows)
                if len(rows)!=54 or female!=18 or male!=36:
                    raise ValueError("2024 expected 54 (18F/36M) source match not met")
            merged[key]=rows
            source_index[key]={"source_url":f"https://statistik.d-u-v.org/getresultevent.php?event={event_id}",
                 "source_label":"DUV official event classification, sourced from organizer",
                 "matched_to_public_results":len(rows),"source_finishers":source_count,
                 "public_finishers":release_count}
            good+=1
            print(f"{key}: explicit_source_matched={len(rows)}/{release_count}; source_rows={source_count}")
        except Exception as error:
            print(f"{key}: unavailable or review needed ({type(error).__name__}); previous data preserved")
    if not good:
        print("No additional sources available; existing verified 2024 overlay retained")
        return 0
    # Verify that the final output includes only IDs from released race bundles.
    for key,rows in merged.items():
        race=json.loads((RACES/(key+".json")).read_text(encoding="utf-8"))
        allowed={r["id"]:r for r in race["results"] if r["status"]=="FINISHED"}
        seen=set()
        for item in rows:
            if item["result_id"] in seen:raise ValueError("Duplicate source result ID")
            seen.add(item["result_id"])
            record=allowed.get(item["result_id"])
            if record is None or record["finish_seconds"]!=item["finish_seconds"] or item["sex"] not in ("M","F"):
                raise ValueError("Unreleased or invalid classification row")
    payload={
     "schema":"gax100-confirmed-race-classification-1",
     "policy":"Only explicit official race sex-classification, matched by published full name AND finish time. No name-based gender guessing. Overlay references only privacy-released result IDs; original SHA-256 race release files unchanged.",
     "source":old["source"],
     "source_by_edition":source_index,
     "editions":merged
    }
    OUTPUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Verified classifications updated for {good} source years; total source-confirmed participant labels={sum(len(r) for r in merged.values())}")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
