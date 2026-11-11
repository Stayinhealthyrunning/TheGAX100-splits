#!/usr/bin/env python3
"""Stage the demo or a verified, privacy-filtered GAX100 public release."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

from build_offline_preview import build

STATUSES = ("FINISHED", "DNF", "DNS", "DSQ", "UNKNOWN")
EDITION_KEYS = {f"{year}-gax100" for year in range(2014, 2027) if year != 2021} | {
    "2021-a-gax100", "2021-b-gax100",
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check(condition, message):
    if not condition:
        raise ValueError(message)


def verify_release(data):
    manifest = load(data / "release-manifest.json")
    check(manifest["schema"] == "gax100-public-release-1", "Unknown release manifest")
    boot = load(data / "bootstrap.json")
    coverage = load(data / "coverage.json")
    editions = {ed["race_key"]: ed for ed in boot["editions"]}
    counts = {ed["race_key"]: ed for ed in coverage}
    check(set(editions) == set(counts) == EDITION_KEYS and
          len(boot["editions"]) == len(coverage) == 14, "Incomplete edition catalog")
    expected = {"bootstrap.json", "coverage.json"} | {
        f"races/{key}.json" for key in EDITION_KEYS
    }
    check(set(manifest["sha256"]) == expected, "Unexpected release files")
    for name, digest in manifest["sha256"].items():
        check(hashlib.sha256((data / name).read_bytes()).hexdigest() == digest,
              "Release file checksum mismatch")
    for key, ed in editions.items():
        race = load(data / "races" / (key + ".json"))
        rows, splits = race["results"], race["splits"]
        check(race["race_key"] == key and not race.get("demo_only") and
              not race.get("release_state"), "Invalid production race")
        ids = {row["id"] for row in rows}
        stations = {station["uid"] for station in race["stations"]}
        check(len(ids) == len(rows) and all(
            row.get("source_uid") is None and row.get("age") is None and
            not row.get("demo_only") and row["status"] in STATUSES and
            isinstance(row["name"], str) and row["name"].strip() for row in rows
        ), "Invalid public result rows")
        check(all(split["result_id"] in ids and split["station_uid"] in stations
                  and not split.get("demo_only") for split in splits), "Invalid public splits")
        for summary in (ed, counts[key]):
            check(summary["results"] == len(rows) and summary["split_observations"] == len(splits)
                  and summary["finishers"] == sum(row["status"] == "FINISHED" for row in rows),
                  "Published totals disagree with release rows")
    return expected


def stage(docs, output):
    data = docs / "data"
    output.mkdir(parents=True, exist_ok=False)
    manifest = data / "release-manifest.json"
    if not manifest.exists():
        build(docs, output / "index.html")
    else:
        files = verify_release(data)
        page = (docs / "index.html").read_text(encoding="utf-8")
        check('<meta name="robots" content="noindex, nofollow">' in page, "Missing indexing policy")
        (output / "index.html").write_text(page.replace("<html ", '<html class="gax-production" ', 1),
                                           encoding="utf-8")
        for pattern in ("*.js", "*.css"):
            for asset in (docs / "assets").glob(pattern):
                target = output / "assets" / asset.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(asset, target)
        files |= {"course-display.json", "route-candidates.json", "route-inventory.json"}
        for name in files:
            target = output / "data" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(data / name, target)
        print("GAX100 public release checks passed for 14 editions")
    (output / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (output / ".nojekyll").touch()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs", type=Path, default=Path("docs"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    stage(args.docs, args.out)
