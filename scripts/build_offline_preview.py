#!/usr/bin/env python3
"""Deterministic, OFFLINE and entirely fictional GAX100 design-review database.

Counts per edition are the real, published aggregates. Every individual name,
sex assignment, club, finish time, checkpoint time and DNF passage is invented.
The station model depicts the organiser's current/2027 information, not
verified historical splits in each edition. NO private repo or participant
database is read, consulted, fetched, imported or copied by this script.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import html
import json
import math
from pathlib import Path
import random
import re
import statistics

FEMALE_FIRST = (
    "Agnes", "Alva", "Amelie", "Annika", "Beatrice", "Carolina", "Cecilia", "Disa",
    "Elina", "Ellen", "Elsa", "Emelie", "Erika", "Felicia", "Filippa", "Hanna",
    "Helena", "Ida", "Ingrid", "Isabella", "Josefin", "Julia", "Karin", "Klara",
    "Lina", "Linnea", "Liselott", "Louise", "Lovisa", "Madeleine", "Maria",
    "Märta", "Nadja", "Nina", "Petra", "Rebecca", "Sandra", "Sanna", "Selma",
    "Tilda", "Tove", "Vera", "Wilma", "Ylva"
)
MALE_FIRST = (
    "Albin", "Alex", "Anton", "Arvid", "Benjamin", "Björn", "Carl", "Daniel",
    "David", "Edvin", "Elias", "Emil", "Fabian", "Filip", "Fredrik", "Gustav",
    "Hampus", "Henrik", "Isak", "Jakob", "Jens", "Joel", "Jonatan", "Karl",
    "Kristoffer", "Lars", "Ludvig", "Magnus", "Malte", "Marcus", "Mattias",
    "Mikael", "Nils", "Olof", "Oskar", "Patrik", "Rasmus", "Robin", "Sebastian",
    "Simon", "Tobias", "Valter", "Viktor", "William"
)
SURNAMES = (
    "Ahlström", "Almgren", "Berg", "Berglund", "Björklund", "Blomqvist",
    "Bodin", "Borg", "Dahl", "Dahlberg", "Edlund", "Ek", "Ekholm", "Eklund",
    "Englund", "Falk", "Fors", "Forsberg", "Gran", "Granberg", "Hagberg",
    "Hall", "Hallberg", "Hedberg", "Hellström", "Holm", "Hult", "Jönsson",
    "Karlberg", "Kjellberg", "Lager", "Lind", "Lindberg", "Lindgren", "Lund",
    "Lundberg", "Lundqvist", "Malm", "Malmberg", "Marklund", "Mårtensson",
    "Nord", "Nordberg", "Nordlund", "Nyberg", "Nyström", "Olsson", "Palm",
    "Palmgren", "Rosen", "Rosén", "Sandberg", "Sandell", "Sjöberg", "Sjögren",
    "Skoglund", "Sund", "Sundberg", "Sundström", "Söderberg", "Viklund",
    "Wall", "Wallberg", "Wester", "Wiklund", "Åkerman", "Öberg", "Östlund"
)
# Every club below is invented; no implication of real club membership.
DEMO_CLUBS = (
    "", "", "", "", "Sydkustens Löpglädje", "Solhedens Trailvänner",
    "Sommarstigens IF", "Strandängens Ultralöpare", "Havsvindens Löparklubb",
    "Kornfältets Running", "Österlenska Långlöparna",
    "Bokskogens Stiglöpare", "Skymningslöpning IF", "Kustbackarnas LK"
)
# Reference grid for SIMULATED passages. 2027 organiser guidance:
# https://gax100.se/information/ ; NOT proof of historical annual timing.
# 2027 cutoffs are given at 43/80/163 while aid stations are at 44/79,
# so never conflate these distinct categories.
TIMING = (
    (3001, "Snogeholm", 30.0, 5*3600),
    (3002, "Floen", 35.0, int(5.5*3600)),
    (3003, "Magleberg", 44.0, 6.5*3600),
    (3004, "Verkaån", 65.0, None),
    (3005, "Brösarps backar", 71.0, 12*3600),
    (3006, "Brösarp väg", 75.0, int(12.5*3600)),
    (3007, "Haväng", 79.0, 14*3600),
    (3008, "Skillinge", 118.0, None),
    (3009, "Sandhammaren", 131.0, 27*3600),
    (3010, "Mål · Ystad", 161.9, 32*3600),
)
# Per-km fatigue weighting: coast and the last 80 km get slower;
# noise makes late splits varied and occasional overtakes possible.
LEG_WEIGHTS = (0.79, .82, .86, .97, 1.10, 1.05, 1.10, 1.29, 1.44, 1.53)
MODEL_SCHEMA = "gax100-fictional-osterlen-demo-v2"


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def seeded(key):
    return random.Random(int.from_bytes(
        hashlib.sha256(("GAX100-Osterlen-synthetic-v2:" + key).encode("utf-8")).digest()[:8],
        "big"))


def synthetic_name(sex, rng, used_names):
    given = FEMALE_FIRST if sex == "F" else MALE_FIRST
    for _ in range(5000):
        name = rng.choice(given) + " " + rng.choice(SURNAMES)
        if name not in used_names:
            used_names.add(name)
            return name
    raise RuntimeError("Fictional Swedish-name pool exhausted")


def sex_for_status(edition, rng, status):
    """Approximate female representation. 2026 has published F totals 14/5/3."""
    if int(edition["year"]) == 2026 and status in ("FINISHED", "DNF", "DNS"):
        wanted = {"FINISHED":14, "DNF":5, "DNS":3}[status]
        count = int({"FINISHED":"finishers", "DNF":"dnf", "DNS":"dns"}[status] in edition and
                    edition[{"FINISHED":"finishers", "DNF":"dnf", "DNS":"dns"}[status]])
        if count >= wanted:
            values = ["F"] * wanted + ["M"] * (count - wanted)
            rng.shuffle(values)
            return values
    count = int(edition.get({"FINISHED":"finishers", "DNF":"dnf", "DNS":"dns",
                              "DSQ":"dsq", "UNKNOWN":"unknown"}[status], 0))
    p = .18 + .035 * ((int(edition["year"]) + (edition["edition_label"].endswith("B"))) % 4) / 3
    values = ["F"] * min(count, round(count*p)) + ["M"] * (count - min(count, round(count*p)))
    rng.shuffle(values)
    return values


def finish_time(rng, sex, year):
    # Calibrated to broad ranges in 2026 public results, but never copied
    # from any real participant. All returned seconds are synthetic.
    earliest = (22.1 if sex == "F" else 16.15) + ((year % 7)-3)*.11
    tail = 31.70
    quant = rng.betavariate(2.2, 1.27)
    value = earliest + (tail - earliest)*quant + rng.uniform(-.30,.30)
    return round(max(earliest + .1, min(tail, value))*3600)


def checkpoints_for_finish(rng, finish_seconds):
    edges = [0.] + [row[2] for row in TIMING]
    # A symmetric profile is disturbed by smooth individual leg variation.
    parts = []
    for i, weight in enumerate(LEG_WEIGHTS):
        diff = edges[i+1] - edges[i]
        parts.append(diff * weight * rng.uniform(.91, 1.09))
    total = sum(parts)
    cumulative = 0
    times = []
    for part in parts:
        cumulative += part
        times.append(round(finish_seconds * (cumulative / total)))
    times[-1] = finish_seconds
    require(all(times[i] > times[i-1] for i in range(1, len(times))),
            "Non-monotonic simulated control times")
    # Finalists must be inside time limits of the current reference model.
    for idx, (_, _, _, cutoff) in enumerate(TIMING):
        if cutoff is not None and times[idx] > cutoff:
            return None
    return times


def passages(rng, finish_seconds):
    for _ in range(400):
        times = checkpoints_for_finish(rng, finish_seconds)
        if times is not None:
            return times
    raise RuntimeError("Cannot fit a synthetic finisher within 2027 reference cutoffs")


def generate_demo(edition, used_names=None):
    rng = seeded(edition["race_key"])
    used_names = set() if used_names is None else used_names
    count = int(edition["results"])
    status_keys = ("FINISHED", "DNF", "DNS", "DSQ", "UNKNOWN")
    status_counts = dict(zip(status_keys, [int(edition[k])
                          for k in ("finishers", "dnf", "dns", "dsq", "unknown")]))
    require(sum(status_counts.values()) == count, "Official status totals changed")
    source_rows = []
    for status in status_keys:
        for sex in sex_for_status(edition, rng, status):
            source_rows.append((status, sex))
    require(len(source_rows) == count, "Synthetic sex distribution mismatch")
    rng.shuffle(source_rows)
    key = edition["race_key"]
    stations = [
        {"uid":uid, "name":name, "km":km, "sort":i,
         "is_finish":i == len(TIMING)-1, "is_start":False,
         "is_analysis_boundary":True,
         "demo_only":True, "cutoff_reference_seconds":cutoff}
        for i, (uid, name, km, cutoff) in enumerate(TIMING)
    ]
    rows, splits = [], []
    for i, (status, sex) in enumerate(source_rows):
        rid = f"fiction-{key}-{i+1:03}"
        record = {
            "id":rid, "source_uid":None,
            "name":synthetic_name(sex, rng, used_names),
            "bib":f"F-{100+i}", "sex":sex, "age":None,
            "class_name":"Kvinnor" if sex=="F" else "Män",
            "club":rng.choice(DEMO_CLUBS), "nationality":"SWE",
            "status":status, "finish_seconds":None, "place":None,
            "demo_only":True
        }
        if status=="FINISHED":
            record["finish_seconds"] = finish_time(rng,sex,int(edition["year"]))
        rows.append(record)
    finishers=sorted([r for r in rows if r["status"]=="FINISHED"],
                     key=lambda r:(r["finish_seconds"],r["id"]))
    for rank, r in enumerate(finishers,1):
        r["place"]=rank
        for idx,elapsed in enumerate(passages(rng,r["finish_seconds"])):
            splits.append({"result_id":r["id"],"station_uid":TIMING[idx][0],
                           "elapsed_seconds":elapsed,"place":None,"demo_only":True})
    # DNF runners have no invented finish time. Their last timed checkpoint
    # varies, more frequently in the second half of the ultradistance.
    for r in rows:
        if r["status"]!="DNF":
            continue
        terminal=rng.choices([1,2,3,5,6,7,8],weights=[2,5,5,10,17,19,26],k=1)[0]
        hypothetical=round(rng.uniform(22,34)*3600)
        for idx,elapsed in enumerate(passages(rng,min(hypothetical,31.4*3600))):
            if idx > terminal:
                break
            splits.append({"result_id":r["id"],"station_uid":TIMING[idx][0],
                           "elapsed_seconds":elapsed,"place":None,"demo_only":True})
    # Place at station computed among all recorded passage times, not copied
    # from final ranks; natural overtakes appear in segment analysis.
    grouped={}
    for sp in splits:
        grouped.setdefault(sp["station_uid"],[]).append(sp)
    for items in grouped.values():
        items.sort(key=lambda sp:(sp["elapsed_seconds"],sp["result_id"]))
        for pos,sp in enumerate(items,1):
            sp["place"]=pos
    rows.sort(key=lambda r:(r["place"] is None,r["place"] or 1e9,r["name"]))
    require(len(rows)==count and sum(r["status"]=="FINISHED" for r in rows)==status_counts["FINISHED"],
            "Synthetic row-count or finisher-count regression")
    ids={r["id"] for r in rows}
    require(len(ids)==len(rows) and all(s["result_id"] in ids for s in splits),
            "Orphan or duplicate synthetic runner")
    require(all(r["name"] not in ("", "Demolöpare") for r in rows), "Invalid fictional name")
    return {
        "race_key":key,"family":"gax100","year":edition["year"],
        "name":edition["label"],"nominal_km":161.9,
        "date":"","source_url":edition.get("source_url",""),
        "route_status":"none","course_version":None,"distance_verified":False,
        "stations":stations,"results":rows,"splits":splits,
        "demo_only":True,"model_schema":MODEL_SCHEMA,
        "reference_course":"Arrangörens stationer och reptider för 2027, ej historiska passager",
        "disclaimer":"ALL NAMES AND TIMES ARE FABRICATED FOR UI REVIEW"
    }


def prepare_payload(docs:Path):
    bootstrap=json.loads((docs/"data/bootstrap.json").read_text(encoding="utf-8"))
    require(bootstrap["event"]=="GAX 100 miles","Unexpected GAX race identity")
    editions=bootstrap["editions"]
    require(len(editions)==14 and sum(int(e["results"]) for e in editions)==945,
            "Unexpected official GAX edition catalogue")
    require(sum(int(e["finishers"]) for e in editions)==651,"Source finisher totals changed")
    used=set()
    demo_boot=json.loads(json.dumps(bootstrap))
    demo_coverage=[]
    files={"data/route-inventory.json":[],
           "data/route-candidates.json":json.loads((docs/"data/route-candidates.json").read_text(encoding="utf-8"))}
    for i,ed in enumerate(editions):
        filename=f"data/races/{ed['race_key']}.json"
        locked=json.loads((docs/filename).read_text(encoding="utf-8"))
        require(locked.get("release_state")=="PRIVATE_DATA_WITHHELD" and
                locked.get("results")==[] and locked.get("splits")==[] and
                locked.get("stations")==[], "Real participant data discovered in public files")
        race=generate_demo(ed,used)
        files[filename]=race
        simulated_splits=len(race["splits"])
        endings=[r["finish_seconds"] for r in race["results"] if r["status"]=="FINISHED"]
        target=demo_boot["editions"][i]
        target["original_source_split_observations"]=ed["split_observations"]
        target["split_observations"]=simulated_splits
        target["timing_stations"]=len(TIMING)
        target["median_seconds"]=round(statistics.median(endings),2) if endings else None
        target["sex_known"]=len(race["results"])
        target["sex_f"]=sum(row["sex"]=="F" for row in race["results"])
        target["sex_m"]=sum(row["sex"]=="M" for row in race["results"])
        target["sex_source"]="fictional_design_demo"
        target["sex_evidence_note"]="Simulerat kön per demolöpare; 2026 kalibrerat på offentlig köns-/statussumma"
        target["demo_only"]=True
        target["source_age_verified"]=False
        demo_coverage.append(dict(target))
    demo_boot["demo_only"]=True
    demo_boot["demo_disclaimer"]="All participant details and split times are fictional."
    demo_boot["historical_split_warning"]="2027 reference station model, not archived real splits."
    files["data/bootstrap.json"]=demo_boot
    files["data/coverage.json"]=demo_coverage
    require(len(used)==945, "Fictional Swedish identities not unique across years")
    require(sum(len(v["results"]) for k,v in files.items() if k.startswith("data/races/"))==945,
            "Demo result count mismatch")
    require(sum(len(v["splits"]) for k,v in files.items() if k.startswith("data/races/"))>6500,
            "Demo must contain realistic segment samples")
    for key,race in files.items():
        if not key.startswith("data/races/"):
            continue
        require(all(row["demo_only"] and row["source_uid"] is None and
                    row["bib"].startswith("F-") for row in race["results"]),
                "A non-synthetic runner was found")
        require(all(sp.get("demo_only") for sp in race["splits"]),
                "A non-synthetic split was found")
    return files


def build(docs:Path,out:Path):
    files=prepare_payload(docs)
    page=(docs/"index.html").read_text(encoding="utf-8")
    required_scripts=["profile-analysis.js","multi-year-map.js",
                      "multi-year-comparison.js","gax-controls.js","app.js","gax-ux.js"]
    for name in required_scripts:
        require(f"assets/{name}" in page, f"Missing GAX app script {name}")
    inline_css=[]
    def style_repl(match):
        path=match.group(1).split("?",1)[0]
        require(path.startswith("assets/") and ".." not in path,"External CSS forbidden")
        css=(docs/path).read_text(encoding="utf-8").replace("</style","<\\/style")
        inline_css.append(path)
        return '<style data-inlined="'+html.escape(path,quote=True)+'">'+css+'</style>'
    page=re.sub(r'<link\s+rel="stylesheet"\s+href="([^"]+)"\s*/?>',style_repl,page)
    require(len(inline_css)==3,"Expected exactly three inline styles")
    shim="""(function(){
      'use strict';
      const files=__PAYLOAD__;
      const ResponseCtor=window.Response;
      window.fetch=(url)=>{
        const path=String(url).split('?')[0].replace(/^\\.\\//,'');
        if(Object.prototype.hasOwnProperty.call(files,path)){
          return Promise.resolve(new ResponseCtor(JSON.stringify(files[path]),{
             status:200,headers:{'Content-Type':'application/json'}
          }));
        }
        return Promise.reject(new Error('Offline GAX demo does not allow external data: '+path));
      };
      window.__GAX_OFFLINE_DEMO__=true;
      document.documentElement.classList.add('gax-is-demo');
    })();"""
    shim=shim.replace("__PAYLOAD__",json.dumps(files,ensure_ascii=False,separators=(",",":")))
    require("</script" not in shim.lower(),"Unsafe HTML in demo JSON")
    loaded=[]
    def script_repl(match):
        path=match.group(1).split("?",1)[0]
        require(path.startswith("assets/") and ".." not in path,"External JS forbidden")
        script=(docs/path).read_text(encoding="utf-8").replace("</script","<\\/script")
        loaded.append(Path(path).name)
        return f'<script data-inlined="{html.escape(path,quote=True)}">{script}</script>'
    page=re.sub(r'<script\s+src="([^"]+)"\s+defer\s*></script>',script_repl,page)
    require(loaded==required_scripts,"JS loading sequence altered")
    banner="""<div class="gax-offline-demo" role="status">
     <strong>DESIGNDEMO</strong> Alla löparnamn, kön, klubbar, sluttider och mellantider är fiktiva.
     Årens resultatantal är hämtade från officiella sammanställningar.
     Kontrollerna modelleras efter arrangörens 2027-information – inte historiska mätningar.
     </div>"""
    page=page.replace("<body>","<body>"+banner,1)
    page=page.replace("</head>","<script>"+shim+"</script></head>",1)
    page=page.replace("<title>","<title>Design-demo · ",1)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(page,encoding="utf-8")
    result=out.read_text(encoding="utf-8")
    require(len(result)>250_000 and "__PAYLOAD__" not in result,"Incomplete review HTML")
    require('src="assets/' not in result and 'href="assets/' not in result,
            "Non-standalone assets remain")
    require("DESIGNDEMO" in result and "ALL NAMES AND TIMES ARE FABRICATED" in result and
            "fiction-2023-gax100-" in result,"Synthetic source disclaimer missing")
    print(f"OFFLINE_PREVIEW_PASS editions=14 fictional_results=945 files=1 bytes={out.stat().st_size}")
    print("DATA_STATUS=100_PERCENT_SYNTHETIC_NAME_SEX_CLUB_TIME_AND_SPLITS")
    print("NO_REAL_PARTICIPANT_DATA_NO_PUBLIC_RESULTS=true")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--docs",type=Path,default=Path("docs"))
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    build(args.docs,args.out)
