#!/usr/bin/env python3
"""One-off structural audit of SCB's public aggregate name tables, never GAX runner data."""
import io,zipfile,xml.etree.ElementTree as ET
from urllib.request import Request,urlopen

SOURCES={
"scb_2022":"https://www.scb.se/contentassets/9fe7dbb460994c72b835163dbc491ef9/namn-med-minst-tva-barare-31-december-2022.xlsx",
"isof_2023":"https://www.isof.se/download/18.7ada16dc193deb67224b81f9/1736421163157/Tilltalsnamn%20hela%20befolkningen%202023.xlsx",
}
NS={"s":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
def inspect(name,url):
    req=Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; open-data-source-audit/1.0)","Accept":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"})
    with urlopen(req,timeout=35) as resp:
        raw=resp.read(40_000_000)
    print("SOURCE",name,"bytes",len(raw),"xlsx",raw.startswith(b"PK"))
    if not raw.startswith(b"PK"):return
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        shared=[]
        if "xl/sharedStrings.xml" in z.namelist():
            root=ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared=["".join(node.itertext()) for node in root.findall("s:si",NS)]
        workbook=ET.fromstring(z.read("xl/workbook.xml"))
        sheets=workbook.findall(".//s:sheet",NS)
        print("WORKSHEETS",[(el.get("name"),el.get("sheetId")) for el in sheets])
        for sheet in z.namelist():
            if not sheet.startswith("xl/worksheets/sheet") or not sheet.endswith(".xml"):continue
            rows=[]
            with z.open(sheet) as fp:
                for event,row in ET.iterparse(fp,events=("end",)):
                    if row.tag!="{"+NS["s"]+"}row":continue
                    cells=[]
                    for c in row.findall("s:c",NS)[:11]:
                        v=c.find("s:v",NS)
                        ins=c.find("s:is",NS)
                        value=v.text if v is not None else "".join(ins.itertext()) if ins is not None else ""
                        if c.get("t")=="s" and value and value.isdigit() and int(value)<len(shared):value=shared[int(value)]
                        cells.append((c.get("r"),str(value)[:65]))
                    if any(v for _,v in cells):rows.append(cells)
                    row.clear()
                    if len(rows)>=11:break
            print("SHEET",sheet,"sample_first_11_rows",rows)
for name,url in SOURCES.items():
    try:inspect(name,url)
    except Exception as e:print("SOURCE_UNAVAILABLE",name,type(e).__name__,str(e)[:160])
