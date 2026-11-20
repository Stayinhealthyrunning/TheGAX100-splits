#!/usr/bin/env python3
"""Extend GAX100 estimated FIRST-NAME frequencies from official SCB 2022 tables.

Source: SCB's final, public full-population XLSX containing first names and
preferred first names with >=2 bearers, separately for registered women/men.
This is statistical name prevalence, NOT verification of a runner's sex,
gender identity, or official race class.

No full runner names, times, or IDs are transmitted to SCB. Its XLSX is
downloaded as a public aggregate by the separate Actions job, stays ephemeral,
and is never committed. The output contains ONLY existing publicly released
result IDs and a strictly flagged name-statistical estimate.
"""
from __future__ import annotations
import collections
import hashlib
import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'docs'/'data'
SRC='https://www.scb.se/contentassets/9fe7dbb460994c72b835163dbc491ef9/namn-med-minst-tva-barare-31-december-2022.xlsx'
N='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG='http://schemas.openxmlformats.org/package/2006/relationships'
P_MIN=.98
N_MIN=30
SOURCE_SHA256='b099822f53baf393fc0dba8b2c8665b7475c3b2001b6efbbe1d96525709792e4'
SCB_METHOD={'tilltalsnamn':'scb_tilltalsnamn_population_2022','fornamn':'scb_fornamn_population_2022'}

def normalize(name: str):
    return unicodedata.normalize('NFKC',str(name or '').strip().casefold()).replace('‐','-').replace('‑','-').replace('–','-')

def runner_first_name(name):
    name=str(name or '').strip()
    if not name or name.casefold().startswith(('anonym','unknown','okänd','anonymous')):
        return None
    token=normalize(name.split()[0].strip('.'))
    return token if len(token)>=2 and any(c.isalpha() for c in token) else None

def worksheet_rows(stream,strings):
    for _,row in ET.iterparse(stream,events=('end',)):
        if row.tag!='{%s}row'%N:continue
        n=int(row.get('r') or 0)
        if n<6:
            row.clear()
            continue
        a=b=None
        for c in row.findall('{%s}c'%N):
            addr=c.get('r','')
            col=re.match(r'[A-Z]+',addr)
            if not col or col.group(0) not in ('A','B'):continue
            v=c.find('{%s}v'%N)
            val=v.text if v is not None else None
            if c.get('t')=='s' and val is not None:
                try:val=strings[int(val)]
                except (ValueError,IndexError):val=None
            elif c.get('t')=='inlineStr':
                val=''.join(t.text or '' for t in c.iter('{%s}t'%N))
            if col.group(0)=='A':a=val
            else:b=val
        if isinstance(a,str) and b is not None:
            try:count=int(float(str(b).replace(' ','').replace('\xa0','')))
            except (TypeError,ValueError):count=0
            if count>=2:
                yield normalize(a),count
        row.clear()

def scb_name_counts(path):
    counts={kind:{'F':{},'M':{}} for kind in SCB_METHOD}
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        if not all(k in names for k in ('xl/workbook.xml','xl/_rels/workbook.xml.rels','xl/sharedStrings.xml')):
            raise ValueError('Official SCB workbook expected XML sections are absent')
        strings=[]
        with z.open('xl/sharedStrings.xml') as stream:
            for _,elem in ET.iterparse(stream,events=('end',)):
                if elem.tag=='{%s}si'%N:
                    strings.append(''.join(x.text or '' for x in elem.iter('{%s}t'%N)))
                    elem.clear()
        book=ET.fromstring(z.read('xl/workbook.xml'))
        relations=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rels={e.get('Id'):e.get('Target') for e in relations.findall('{%s}Relationship'%PKG)}
        found=set()
        for sh in book.findall('.//{%s}sheet'%N):
            title=normalize(sh.get('name',''))
            if title.startswith('tilltalsnamn'):kind='tilltalsnamn'
            elif title.startswith('förnamn'):kind='fornamn'
            else:continue # Ignore surnames entirely.
            sex='F' if 'kvinnor' in title else 'M' if 'män' in title else None
            if not sex:continue
            if (kind,sex) in found:raise ValueError('Duplicate SCB first-name sheet')
            found.add((kind,sex))
            target=rels.get(sh.get('{%s}id'%R))
            if not target:raise ValueError('SCB first-name sheet without relationship')
            target=('xl/'+target.lstrip('/')) if not target.startswith('xl/') else target
            target=target.replace('xl/xl/','xl/')
            if target not in names:raise ValueError('SCB sheet target missing')
            with z.open(target) as stream:
                for name,count in worksheet_rows(stream,strings):
                    if name in counts[kind][sex]:
                        raise ValueError('Duplicate SCB aggregate name')
                    counts[kind][sex][name]=count
    if found!={(kind,sex) for kind in SCB_METHOD for sex in ('F','M')}:
        raise ValueError('Both sexes and both first-name types must exist')
    if any(len(counts[k][sx])<10000 for k in counts for sx in ('F','M')):
        raise ValueError('Suspiciously short SCB name population table')
    return counts

def scb_choice(first,counts):
    # A missing entry means fewer than TWO registered bearers, NOT zero.
    # Use minority=1 as a conservative upper bound; never treat absence as zero.
    choices=[]
    examined=0
    for kind in ('tilltalsnamn','fornamn'):
        f=counts[kind]['F'].get(first)
        m=counts[kind]['M'].get(first)
        if f is None and m is None:continue
        examined+=1
        ff=f if f is not None else 1
        mm=m if m is not None else 1
        sex='F' if ff>mm else 'M' if mm>ff else None
        dom=max(ff,mm)
        probability=dom/(ff+mm)
        if sex and dom>=N_MIN and probability>=P_MIN:
            choices.append((kind,sex,round(probability,6),dom))
    if choices:
        # A contradictory signal in the other table invalidates an estimate.
        if len({x[1] for x in choices})>1:return None,'scb_conflicting_tables'
        return choices[0],'scb_strong'
    return None,'scb_ambiguous' if examined else 'scb_unlisted'

def main(path):
    source=Path(path)
    if not source.exists() or source.stat().st_size<10000:
        raise ValueError('Expected full official SCB spreadsheet not available')
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if digest!=SOURCE_SHA256:
        raise ValueError('SCB workbook changed from vetted 2022 dataset: manual review required')
    counts=scb_name_counts(source)
    official=json.loads((DATA/'official-result-classification.json').read_text(encoding='utf-8'))
    previous=json.loads((DATA/'name-based-classification.json').read_text(encoding='utf-8'))
    bootstrap=json.loads((DATA/'bootstrap.json').read_text(encoding='utf-8'))
    manual=json.loads((DATA/'manual-result-classification.json').read_text(encoding='utf-8'))
    if manual.get('schema')!='gax100-manual-analytical-group-1':
        raise ValueError('Missing manual analytical group provenance')
    if official.get('schema')!='gax100-confirmed-race-classification-1' or previous.get('schema')!='gax100-first-name-statistical-estimate-1':
        raise ValueError('Expected existing privacy/source schemas')
    # Cross-check SCB's majority with EXPLICIT classes for the same given
    # name already present in the public GAX cohort. Never label an individual
    # when their given name demonstrably occurs across classes locally.
    official_first=collections.defaultdict(set)
    race_by_year={}
    for edition in bootstrap['editions']:
        key=edition['race_key']
        race=json.loads((DATA/'races'/(key+'.json')).read_text(encoding='utf-8'))
        race_by_year[key]=race
        confirmed={str(x['result_id']):x['sex'] for x in official.get('editions',{}).get(key,[])}
        for row in race['results']:
            sex=row.get('sex') if row.get('sex') in ('F','M') else confirmed.get(str(row['id']))
            firstname=runner_first_name(row.get('name'))
            if firstname and sex in ('F','M'):official_first[firstname].add(sex)
    by_year={}
    tally=collections.Counter()
    for ed in bootstrap['editions']:
        key=ed['race_key']
        race=race_by_year[key]
        released={str(r['id']):r for r in race['results']}
        confirmed={str(x['result_id']):x['sex'] for x in official.get('editions',{}).get(key,[])}
        existing={str(x['result_id']):x for x in previous.get('editions',{}).get(key,[])}
        owner_groups={str(x['result_id']) for x in manual.get('editions',{}).get(key,[])}
        entries=[]
        for result_id,row in released.items():
            if row.get('sex') in ('F','M') or result_id in confirmed or result_id in owner_groups:
                continue
            first=runner_first_name(row.get('name'))
            if not first:continue
            choice,status=scb_choice(first,counts)
            old=existing.get(result_id)
            if choice:
                kind,sex,prob,n=choice
                known_sexes=official_first.get(first,set())
                if any(known!=sex for known in known_sexes):
                    tally['scb_conflicts_with_official_gax_class_held_unknown']+=1
                    continue
                if old and old['estimated_sex']!=sex:
                    tally['existing_conflict_held_unknown']+=1
                    continue
                entries.append(dict(result_id=row['id'],status=row['status'],estimated_sex=sex,
                        method=SCB_METHOD[kind],probability=prob,evidence_count=n))
                tally[SCB_METHOD[kind]]+=1
            elif old and status=='scb_unlisted':
                # Name absent from SCB 2022; retain older documented estimate.
                entries.append(old)
                tally['prior_evidence_retained']+=1
            elif old:
                tally['existing_ambiguous_reclassified_unknown']+=1
            else:tally[status]+=1
        # Fail-closed: do not produce estimates for unlisted/unreleased IDs.
        seen=set()
        for item in entries:
            token=str(item['result_id'])
            if token in seen or token not in released or token in confirmed or released[token].get('sex') in ('F','M') or released[token]['status']!=item['status']:
                raise ValueError('SCB overlay violates official or privacy release IDs')
            seen.add(token)
        by_year[key]=entries
    result=dict(previous)
    result['editions']=by_year
    result['method']='Official SCB name population statistics, conservative missing-category counts; anonymous name-level frequency only. NOT an individual sex, gender, or official race class.'
    result['source_url']=SRC
    result['scb_source_year']=2022
    result['scb_workbook_sha256']=digest
    result['scb_min_dominant_count']=N_MIN
    result['scb_min_conservative_probability']=P_MIN
    result['disclaimer_sv']='UPPSKATTAT från förnamnets förekomst hos SCB:s folkbokförda kvinnor och män 2022, INTE verifierad uppgift om löparen eller officiell tävlingsklass. Namn med svag eller motstridig fördelning lämnas okända.'
    (DATA/'name-based-classification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('SCB full-population workbook SHA256:',digest)
    print('SCB name counts: preferred women/men',len(counts['tilltalsnamn']['F']),len(counts['tilltalsnamn']['M']))
    print('SCB name counts: given women/men',len(counts['fornamn']['F']),len(counts['fornamn']['M']))
    print('SCB aggregate-only classification count:',dict(tally))
    print('Final estimated public result rows:',sum(map(len,by_year.values())))
    print('Years covered:',len(by_year))
    # Do not print full names, individual IDs, results or timing records.
    return 0

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: enrich_scb_first_names.py /path/to/offline-scb.xlsx')
    raise SystemExit(main(sys.argv[1]))
