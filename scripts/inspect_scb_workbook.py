#!/usr/bin/env python3
"""Inspect only public SCB aggregate spreadsheet structure, no runner records."""
import re
import sys
import zipfile
from xml.etree import ElementTree as ET
from pathlib import Path

N='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG='http://schemas.openxmlformats.org/package/2006/relationships'

def read_workbook(path):
    with zipfile.ZipFile(path) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            with z.open('xl/sharedStrings.xml') as stream:
                for event,elem in ET.iterparse(stream,events=('end',)):
                    if elem.tag=='{%s}si'%N:
                        strings.append(''.join(e.text or '' for e in elem.iter('{%s}t'%N)))
                        elem.clear()
        book=ET.fromstring(z.read('xl/workbook.xml'))
        relroot=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rels={x.get('Id'):x.get('Target') for x in relroot.findall('{%s}Relationship'%PKG)}
        for sheet in book.findall('.//{%s}sheet'%N):
            target=rels.get(sheet.get('{%s}id'%R),'')
            path='xl/'+target.lstrip('/') if not target.startswith('xl/') else target
            path=path.replace('xl/xl/','xl/')
            if path not in z.namelist():
                print('SCB-SHEET-UNAVAILABLE:',sheet.get('name'),target)
                continue
            first_rows=[]
            with z.open(path) as stream:
                for event,elem in ET.iterparse(stream,events=('end',)):
                    if elem.tag=='{%s}row'%N:
                        cells=[]
                        for c in elem.findall('{%s}c'%N):
                            v=c.find('{%s}v'%N)
                            val=v.text if v is not None else ''
                            if c.get('t')=='s' and val:
                                try: val=strings[int(val)]
                                except (IndexError,ValueError):val='<unknown shared string>'
                            if c.get('t')=='inlineStr':
                                val=''.join(x.text or '' for x in c.iter('{%s}t'%N))
                            if len(cells)<12:cells.append((c.get('r'),str(val)[:75]))
                        first_rows.append(cells)
                        elem.clear()
                        if len(first_rows)>=7:break
            print('SCB-SHEET:',sheet.get('name'),'filename:',path)
            for row in first_rows:print('SCB-ROW:',row)
        print('SCB-SHARED-STRINGS:',len(strings))
if __name__=='__main__':read_workbook(Path(sys.argv[1]))
