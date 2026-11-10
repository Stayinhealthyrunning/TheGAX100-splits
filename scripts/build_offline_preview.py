#!/usr/bin/env python3
"""Build a SINGLE-FILE, OFFLINE, SYNTHETIC GAX100 UX review.

Public source only. Does not open private repos, real participant files or
network connections. All 945 synthetic results have generated placeholder names.
"""
from __future__ import annotations
import argparse
import html
import json
from pathlib import Path
import re

def require(test, message):
    if not test:
        raise RuntimeError(message)

def generate_demo(edition: dict) -> dict:
    count = int(edition["results"])
    finishes = int(edition["finishers"])
    dnf = int(edition["dnf"])
    dns = int(edition["dns"])
    dsq = int(edition["dsq"])
    unknown = int(edition["unknown"])
    require(sum((finishes, dnf, dns, dsq, unknown)) == count,
            "Official aggregate status count changed")
    key = edition["race_key"]
    seq = ["FINISHED"] * finishes + ["DNF"] * dnf + ["DNS"] * dns
    seq += ["DSQ"] * dsq + ["UNKNOWN"] * unknown
    # Deliberately fictional names, teams and times – not traceable to participants.
    rows = []
    splits = []
    timing = [
        (1101, "DEMOKONTROLL A (fiktiv)", 36),
        (1102, "DEMOKONTROLL B (fiktiv)", 74),
        (1103, "DEMOKONTROLL C (fiktiv)", 120),
        (1199, "Mål (demotid)", 160.934)
    ]
    stations = [{"uid":sid,"name":name,"km":km,"sort":i,
                 "is_finish":i==3,"is_start":False,"is_analysis_boundary":True}
                for i,(sid,name,km) in enumerate(timing)]
    for i, status in enumerate(seq):
        id_ = f"demo-{key}-{i+1:03}"
        finish_seconds = round(19*3600 + i*450 + edition["year"]%9*390) if status=="FINISHED" else None
        sex = "F" if i % 3 == 0 else "M"
        row = {"id":id_,"source_uid":None,
               "name":f"Demolöpare {edition['edition_label']}-{i+1:03}",
               "bib":f"TEST{i+1:03}","sex":sex,"age":None,
               "class_name":"Kvinna" if sex=="F" else "Man",
               "club":"Fiktiv demoklubb", "status":status,
               "finish_seconds":finish_seconds,
               "place":i+1 if status=="FINISHED" else None}
        rows.append(row)
        if finish_seconds is not None:
            for idx,(uid,_,_) in enumerate(timing):
                fractions=(.24,.48,.76,1.0)
                t=round(finish_seconds*fractions[idx])
                splits.append({"result_id":id_,"station_uid":uid,
                              "elapsed_seconds":t,"place":i+1})
        elif status=="DNF" and i%2 == 0:
            for j in range(1 + (i % 3)):
                splits.append({"result_id":id_,"station_uid":timing[j][0],
                              "elapsed_seconds":round((19*3600+i*450)*(.24,.48,.76)[j]),
                              "place":None})
    return {"race_key":key,"family":"gax100","year":edition["year"],
            "name":edition["label"],"nominal_km":160.934,
            "date":"","source_url":"", "route_status":"none",
            "course_version":None,"distance_verified":False,
            "stations":stations,"results":rows,"splits":splits,
            "demo_only":True,"disclaimer":"ALL NAMES AND TIMES ARE FABRICATED FOR UI REVIEW"}

def prepare_payload(docs:Path) -> dict:
    bootstrap = json.loads((docs/"data/bootstrap.json").read_text(encoding="utf-8"))
    require(bootstrap["event"]=="GAX 100 miles","unexpected race identity")
    editions=bootstrap["editions"]
    require(len(editions)==14 and sum(e["results"] for e in editions)==945,
            "not the checked GAX catalogue")
    previews={"data/bootstrap.json":bootstrap,
              "data/coverage.json":json.loads((docs/"data/coverage.json").read_text(encoding="utf-8")),
              "data/route-inventory.json":[]}
    for ed in editions:
        p=f"data/races/{ed['race_key']}.json"
        locked=json.loads((docs/p).read_text(encoding="utf-8"))
        require(locked.get("release_state")=="PRIVATE_DATA_WITHHELD"
                and locked["results"]==[] and locked["splits"]==[],
                "a public source file unexpectedly contains participant data")
        previews[p]=generate_demo(ed)
    require(sum(len(v["results"]) for k,v in previews.items()
                if k.startswith("data/races/"))==945,"synthetic dataset count incorrect")
    require(all(r["name"].startswith("Demolöpare ")
                for k,v in previews.items() if k.startswith("data/races/")
                for r in v["results"]), "non synthetic identity detected")
    return previews

def build(docs:Path,out:Path):
    previews=prepare_payload(docs)
    page=(docs/"index.html").read_text(encoding="utf-8")
    required_scripts=["profile-analysis.js","multi-year-map.js",
                      "multi-year-comparison.js","gax-controls.js","app.js"]
    for name in required_scripts:
        require(f"assets/{name}" in page, f"missing GAX blueprint script {name}")
    inline_css=[]
    def style_repl(match):
        path=match.group(1).split("?",1)[0]
        if not path.startswith("assets/"):
            raise RuntimeError("External CSS is not permitted")
        css=(docs/path).read_text(encoding="utf-8").replace("</style","<\\/style")
        inline_css.append(path)
        return "<style data-inlined="+html.escape(path,quote=True)+">"+css+"</style>"
    page=re.sub(r'<link\s+rel="stylesheet"\s+href="([^"]+)"\s*/?>',
                style_repl,page)
    require(len(inline_css)==3,"expected exactly three inline styles")
    shim="""(function(){
      'use strict';
      const files=__PAYLOAD__;
      const nativeResponse=window.Response;
      window.fetch=(url)=>{
         const path=String(url).split('?')[0].replace(/^\\.\\//,'');
         if(Object.prototype.hasOwnProperty.call(files,path)){
           return Promise.resolve(new nativeResponse(JSON.stringify(files[path]), {
             status:200,headers:{'Content-Type':'application/json'}
           }));
         }
         return Promise.reject(new Error('Offline demo does not permit external data: '+path));
      };
      window.__GAX_OFFLINE_DEMO__=true;
    })();"""
    shim=shim.replace("__PAYLOAD__",json.dumps(previews,ensure_ascii=False,separators=(",",":")))
    require("</script" not in shim.lower(),"inline demo data contains unsafe script tags")
    loaded=[]
    def script_repl(match):
        path=match.group(1).split("?",1)[0]
        require(path.startswith("assets/"),"external JS not permitted")
        js=(docs/path).read_text(encoding="utf-8").replace("</script","<\\/script")
        loaded.append(Path(path).name)
        return f'<script data-inlined="{html.escape(path,quote=True)}">{js}</script>'
    page=re.sub(r'<script\s+src="([^"]+)"\s+defer\s*></script>',script_repl,page)
    require(loaded==required_scripts,"JS load order altered")
    banner="""<div class="gax-offline-demo" role="status">
    FÖRHANDSGRANSKNING · ALLA NAMN, TIDER OCH DEMOKONTROLLER ÄR FIKTIVA.
    Detta är Sätila-gränssnittet anpassat för GAX100. De verkliga uppgifterna ligger privat.
    Ingen webbsida eller persondatabas publiceras från denna fil.</div>"""
    demo_css="""<style>
       .gax-offline-demo{position:sticky;top:0;z-index:99999;
         background:#fdf3c9;color:#422f08;border-bottom:3px solid #bd8b30;
         text-align:center;padding:11px 18px;font:700 12px/1.5 system-ui,sans-serif}
       .gax-preview-note{display:none}
    </style>"""
    page=page.replace("<body>","<body>"+demo_css+banner,1)
    page=page.replace("</head>","<script>"+shim+"</script></head>",1)
    page=page.replace("<title>","<title>FÖRHANDSGRANSKNING · ",1)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(page,encoding="utf-8")
    text=out.read_text(encoding="utf-8")
    require(len(text)>250_000 and "__PAYLOAD__" not in text,"incomplete HTML preview")
    require('src="assets/' not in text and 'href="assets/' not in text,
            "non-standalone assets remain")
    require('FÖRHANDSGRANSKNING' in text and 'Demolöpare ' in text,
            "synthetic data review banner missing")
    print(f"OFFLINE_PREVIEW_PASS editions=14 synthetic_results=945 files=1 bytes={out.stat().st_size}")
    print("DATA_STATUS=100_PERCENT_FICTIONAL PARTICIPANT_PII=NONE")
    print("NO_PUBLIC_SITE_OR_RELEASE=true")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--docs",type=Path,default=Path("docs"))
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    build(args.docs,args.out)
