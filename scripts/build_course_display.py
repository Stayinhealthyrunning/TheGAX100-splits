#!/usr/bin/env python3
"""Build display-only route geometry from the project's GPX originals."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET

SOURCES = (
    (2026, "Garmin · arrangörens bana", "COURSE_484861455.gpx",
     "https://connect.garmin.com/app/course/484861455",
     "46c298b5f20a7a9c8762c17d4a91f4d7ed87e4b60d1561b372c8b447581dbb94", None),
    (2022, "Plotaroute · historisk kandidat", "Gax 100 Miles-2022-M6.gpx",
     "https://www.plotaroute.com/route/2310208",
     "5f1c8c181efdf9e3379ed47c231acb60c4ca9f3e73791b9caf9e0c450262a9ed", .25),
    (2021, "Plotaroute · kandidat med oklar A/B-koppling", "Gax 2021 100 Miles_final.gpx",
     "https://www.plotaroute.com/route/1589517",
     "7c7b9a0ad63239611c3955f76841eb8b265c043b03abbb6db49dc9caa520b272", .25),
    (None, "AllTrails · årtal obekräftat", "The_Gax_100_miles.gpx",
     None, "9073f562cde894cffe2327680ff4208d7435013527cad9078d6a0872243c1380", .25),
)


def distance(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, (*a[:2], *b[:2]))
    h = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 12742.0176 * math.asin(min(1, math.sqrt(h)))


def simplify(run, tolerance=10):
    """Keep turns within tolerance metres, and keep each segment's endpoints."""
    if len(run) <= 2:
        return run
    xy = [(lon * 64000, lat * 111200) for _, lat, lon, _ in run]
    keep, todo = {0, len(run)-1}, [(0, len(run)-1)]
    while todo:
        start, end = todo.pop()
        ax, ay = xy[start]
        dx, dy = xy[end][0]-ax, xy[end][1]-ay
        length_sq = dx*dx+dy*dy
        worst, split = tolerance*tolerance, None
        for i in range(start+1, end):
            x, y = xy[i][0]-ax, xy[i][1]-ay
            fraction = max(0, min(1, (x*dx+y*dy)/length_sq)) if length_sq else 0
            error = (x-fraction*dx)**2+(y-fraction*dy)**2
            if error > worst:
                worst, split = error, i
        if split is not None:
            keep.add(split)
            todo.extend(((start, split), (split, end)))
    return [run[i] for i in sorted(keep)]


def convert(path, year, label, url, checksum, gap_km):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != checksum:
        raise ValueError(f"Unexpected GPX content in {path.name}")
    root = ET.fromstring(raw)
    runs, total, max_leg = [], 0, 0
    for segment in root.findall(".//{*}trkseg"):
        run, previous = [], None
        for pt in segment.findall("{*}trkpt"):
            lat, lon = float(pt.attrib["lat"]), float(pt.attrib["lon"])
            elevation = float(pt.findtext("{*}ele", "nan"))
            if not (55.1 <= lat <= 56.2 and 13.2 <= lon <= 14.8 and -50 <= elevation <= 850):
                raise ValueError(f"Point out of bounds in {path.name}")
            current = lat, lon
            if previous is not None:
                leg = distance(previous, current)
                max_leg = max(max_leg, leg)
                if gap_km is not None and leg > gap_km:
                    runs.append(run)
                    run = []
                else:
                    total += leg
            run.append([round(total, 4), round(lat, 5), round(lon, 5), round(elevation, 1)])
            previous = current
        if run:
            runs.append(run)
    if not (130 <= total <= 185) or not runs:
        raise ValueError(f"Unexpected route length in {path.name}: {total}")
    # Preserve the organizer's original vertex sequence, including sparse sections.
    if year != 2026:
        runs = [simplify(run) for run in runs]
    return {"year": year, "label": label, "source_url": url, "source_sha256": checksum,
            "max_source_leg_km": round(max_leg, 3), "runs": runs}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    routes = []
    for year, label, name, url, checksum, gap in SOURCES:
        path = next((folder/name for folder in args.source if (folder/name).is_file()), None)
        if path is None:
            parser.error(f"Missing GPX: {name}")
        routes.append(convert(path, year, label, url, checksum, gap))
    args.out.write_text(json.dumps(routes, ensure_ascii=False, separators=(",", ":"))+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
