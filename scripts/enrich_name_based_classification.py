#!/usr/bin/env python3
"""Name-statistical estimate for already public GAX100 result rows.

CAUTION: A first name's common association with M/F is NOT a participant's
identity and NEVER a verified race class. The optional overlay is always
labeled UPPSKATTAT, can be removed, and cannot override organizer/DUV data.

Only unique FIRST NAMES (no family names, runner IDs, or timing records) are
sent to the public Genderize API. The script logs only aggregate counts.
It never modifies the 14 privacy-released race bundles.
"""
from __future__ import annotations
import collections
import json
import re
import sys
import time
import unicodedata
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"docs"/"data"
CLASSIFICATION=DATA/"official-result-classification.json"
OUTPUT=DATA/"name-based-classification.json"
ENDPOINT="https://api.genderize.io"
MIN_API_PROBABILITY=0.99
MIN_API_COUNT=50
MIN_LOCAL_UNANIMOUS_PEOPLE=4
BATCH=10

def first_name(name):
    name=str(name or "").strip()
    if not name or name.casefold().startswith(("anonym","unknown","okänd","anonymous")):
        return None
    token=re.split(r"[\s\-]+",name)[0].strip().strip(".")
    if not token or not any(c.isalpha() for c in token):return None
    token=unicodedata.normalize("NFKC",token).casefold()
    return token if len(token)>=2 else None

def norm_full(name):
    return "".join(c for c in unicodedata.normalize("NFKD",str(name or "").casefold())
                   if c.isalnum() and not unicodedata.combining(c))

def api_gender(first_names):
    """Return only aggregate name statistics; never log URL or names."""
    out={}
    for i in range(0,len(first_names),BATCH):
        batch=first_names[i:i+BATCH]
        params=[("country_id","SE")]+[("name[]",n) for n in batch]
        url=ENDPOINT+"?"+urlencode(params)
        try:
            req=Request(url,headers={"User-Agent":"GAX100-research/1.0"})
            with urlopen(req,timeout=22) as response:
                payload=json.loads(response.read(300000).decode("utf-8"))
            if not isinstance(payload,list) or len(payload)!=len(batch):
                raise ValueError("Unexpected API response shape")
            for item in payload:
                name=str(item.get("name") or "").casefold()
                if name not in batch:raise ValueError("API echoed an unrequested name")
                gender=item.get("gender")
                probability=item.get("probability")
                count=item.get("count")
                if gender in ("male","female") and isinstance(probability,(float,int)) and isinstance(count,int):
                    out[name]={"sex":"M" if gender=="male" else "F",
                               "probability":round(float(probability),4),"count":count}
        except Exception as e:
            print("Aggregate name statistics unavailable ("+type(e).__name__+
                  "); retaining only locally corroborated first-name estimates")
            break
        time.sleep(0.25)
    print("Name-statistics unique first-names queried:",len(out))
    return out

def main():
    from_api=True
    if "--no-api" in sys.argv:from_api=False
    official=json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
    boot=json.loads((DATA/"bootstrap.json").read_text(encoding="utf-8"))
    existing=json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else {}
    if official.get("schema")!="gax100-confirmed-race-classification-1":
        raise ValueError("Official-source classification contract missing")
    training=collections.defaultdict(lambda:{"F":set(),"M":set()})
    unknown=[]
    all_races={}
    for ed in boot["editions"]:
        key=ed["race_key"]
        race=json.loads((DATA/"races"/(key+".json")).read_text(encoding="utf-8"))
        all_races[key]=race
        official_by_id={str(row["result_id"]):row["sex"]
                        for row in official.get("editions",{}).get(key,[])}
        for r in race["results"]:
            given=r.get("sex") if r.get("sex") in ("F","M") else official_by_id.get(str(r["id"]))
            firstname=first_name(r.get("name"))
            if not firstname:continue
            if given in ("F","M"):
                training[firstname][given].add(norm_full(r.get("name")))
            else:
                unknown.append((key,r,firstname))
    needs=sorted({first for _,_,first in unknown})
    api=api_gender(needs) if from_api else {}
    by_year={ed["race_key"]:[] for ed in boot["editions"]}
    counts=collections.Counter()
    for key,r,first in unknown:
        local=training.get(first,{"F":set(),"M":set()})
        n_f,n_m=len(local["F"]),len(local["M"])
        data=api.get(first)
        source=None;sex=None;probability=None;count=None
        if data and data["probability"]>=MIN_API_PROBABILITY and data["count"]>=MIN_API_COUNT:
            if (n_f and data["sex"]=="M") or (n_m and data["sex"]=="F"):
                counts["source_conflict"]+=1
                continue
            source="genderize_first_name_SE"
            sex=data["sex"];probability=data["probability"];count=data["count"]
        elif max(n_f,n_m)>=MIN_LOCAL_UNANIMOUS_PEOPLE and not(min(n_f,n_m)>0):
            source="verified_cohort_first_name_consensus"
            sex="F" if n_f else "M";probability=None;count=max(n_f,n_m)
        else:
            counts["unresolved"]+=1
            continue
        by_year[key].append({
            "result_id":r["id"],"status":r["status"],
            "estimated_sex":sex,"method":source,
            "probability":probability,"evidence_count":count
        })
        counts[source]+=1
    # Every estimate is for a *published*, otherwise class-unknown row.
    for key,values in by_year.items():
        race=all_races[key]
        lookup={str(r["id"]):r for r in race["results"]}
        explicit={str(v["result_id"]) for v in official.get("editions",{}).get(key,[])}
        seen=set()
        for v in values:
            keyid=str(v["result_id"])
            if keyid in seen or keyid in explicit:raise ValueError("Official classification override")
            seen.add(keyid)
            original=lookup.get(keyid)
            if not original or original["status"]!=v["status"] or original.get("sex") in ("F","M"):
                raise ValueError("Estimate references wrong or classified row")
            if v["method"]=="genderize_first_name_SE" and not(
                  v["probability"]>=MIN_API_PROBABILITY and v["evidence_count"]>=MIN_API_COUNT):
                raise ValueError("Low-confidence name estimate")
            if v["method"]=="verified_cohort_first_name_consensus" and v["evidence_count"]<MIN_LOCAL_UNANIMOUS_PEOPLE:
                raise ValueError("Low-support cohort name estimate")
    doc={
      "schema":"gax100-first-name-statistical-estimate-1",
      "method":"First-name frequency, not actual sex/gender identity or official race class.",
      "disclaimer_sv":"UPPSKATTAT från namnets statistiska förekomst, inte verifierad uppgift om personen eller officiell tävlingsklass. Tvetydiga namn lämnas utan uppskattning.",
      "min_probability":MIN_API_PROBABILITY,"min_count":MIN_API_COUNT,
      "source_url":"https://genderize.io/documentation/api/reference",
      "country_id":"SE",
      "editions":by_year
    }
    OUTPUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Unverified public-result records:",len(unknown))
    print("Estimate-only rows:",sum(map(len,by_year.values())))
    print("By evidence type:",dict(counts))
    print("All 14 editions preserved:",len(by_year))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
