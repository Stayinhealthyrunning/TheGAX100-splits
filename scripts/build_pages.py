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
        # Static photograph-style visual is an original generated asset whose exact
        # bytes are release-pinned. No third-party runtime dependency or remote hotlink.
        hero = docs / "assets" / "hero-ales-stenar-trail-runners.webp"
        check(hero.exists() and hashlib.sha256(hero.read_bytes()).hexdigest() ==
              "1df7031ed35634b7170a584d8bdc4c5e77958dceddfc451a830eecd3d9c73070",
              "GAX100 v1.2 hero is missing or differs from approved original")
        for pattern in ("*.js", "*.css", "*.webp"):
            for asset in (docs / "assets").glob(pattern):
                target = output / "assets" / asset.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(asset, target)
        # Replay music is a separate, non-personal config asset. Its referenced
        # binary is served only if present in this GitHub repo. Never fetch from
        # third-party storage at runtime or silently substitute a different song.
        audio_config = data / "replay-audio.json"
        if audio_config.exists():
            config = load(audio_config)
            src = config.get("src", "")
            check(src == "assets/audio/audioera-acoustic-guitar-happy-637709.mp3" and
                  config.get("schema") == "loppanalys-replay-audio-1",
                  "Invalid GAX100 replay sound config")
            (output / "data").mkdir(parents=True, exist_ok=True)
            shutil.copyfile(audio_config, output / "data" / "replay-audio.json")
            sound = docs / src
            if sound.exists():
                check(sound.stat().st_size > 10000 and
                      hashlib.sha256(sound.read_bytes()).hexdigest() ==
                      "ed089921eb56654ab4c97025c5ceebd057e6c739a9d3f15328033dc909d09e49",
                      "Replay soundtrack differs from the user-supplied original")
                dest = output / src
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(sound, dest)
            else:
                print("Audio asset not yet present in GitHub; replay remains available without music")
        # Verified race-class overlay cannot import a new person, guess
        # attributes from a name, or alter the 16 immutable release bundles.
        source_classes=load(data/"official-result-classification.json")
        check(source_classes.get("schema")=="gax100-confirmed-race-classification-1",
              "Official classification overlay schema is invalid")
        for edition_key,entries in source_classes.get("editions",{}).items():
            check(edition_key in {e["race_key"] for e in load(data/"bootstrap.json")["editions"]},
                  "Unknown edition in classification overlay")
            public_race=load(data/"races"/(edition_key+".json"))
            allowed={str(row["id"]):row for row in public_race["results"] if row["status"]=="FINISHED"}
            seen=set()
            for item in entries:
                identifier=str(item.get("result_id"))
                check(identifier not in seen,"Duplicate public result classification ID")
                seen.add(identifier)
                check(set(item).issubset({"result_id","sex","finish_seconds","overall_rank","sex_class_rank"}),
                      "Unapproved attribute in public classification")
                row=allowed.get(identifier)
                check(row is not None and row["finish_seconds"]==item.get("finish_seconds")
                      and item.get("sex") in {"F","M"},
                      "Classification does not match privacy-released finisher and timing")
                check(row.get("sex") in (None,item["sex"]),"Official classification source disagrees")
            if edition_key=="2024-gax100":
                check(len(entries)==54 and sum(e["sex"]=="F" for e in entries)==18
                      and sum(e["sex"]=="M" for e in entries)==36,
                      "2024 podium source coverage must be complete (18 F, 36 M)")
        # Statistical first-name estimates are never official sex assignments.
        # Ship a separate clearly documented overlay, keyed only to already
        # privacy-released result IDs and never to full names or DUV identifiers.
        estimates=load(data/"name-based-classification.json")
        check(estimates.get("schema")=="gax100-first-name-statistical-estimate-1",
              "Missing estimate-only source schema")
        entries_by_year=estimates.get("editions",{})
        expected_keys={e["race_key"] for e in load(data/"bootstrap.json")["editions"]}
        check(set(entries_by_year)==expected_keys,
              "Every edition must have an estimate table, even if empty")
        for edition_key,entries in entries_by_year.items():
            original=load(data/"races"/(edition_key+".json"))
            allowed={str(row["id"]):row for row in original["results"]}
            confirmed={str(x["result_id"]) for x in source_classes.get("editions",{}).get(edition_key,[])}
            seen=set()
            for estimate in entries:
                check(set(estimate)=={"result_id","status","estimated_sex","method","probability","evidence_count"},
                      "Unapproved field in estimated class data")
                token=str(estimate["result_id"])
                check(token not in seen and token not in confirmed,
                      "Estimate duplicates or overrides verified class")
                seen.add(token)
                row=allowed.get(token)
                check(row is not None and row["status"]==estimate["status"] and
                      row.get("sex") not in ("F","M") and estimate["estimated_sex"] in ("F","M"),
                      "Estimate does not match a currently unclassified published result")
                method=estimate["method"]
                if method=="genderize_first_name_SE":
                    check(isinstance(estimate["probability"],(int,float)) and
                          estimate["probability"]>=0.99 and
                          isinstance(estimate["evidence_count"],int) and
                          estimate["evidence_count"]>=50,"Weak statistical name evidence")
                elif method=="verified_cohort_first_name_consensus":
                    check(estimate["probability"] is None and
                          isinstance(estimate["evidence_count"],int) and
                          estimate["evidence_count"]>=4,"Weak source-cohort name evidence")
                elif method in {"scb_tilltalsnamn_population_2022","scb_fornamn_population_2022"}:
                    check(isinstance(estimate["probability"],(int,float)) and
                          0.98<=estimate["probability"]<=1.0 and
                          isinstance(estimate["evidence_count"],int) and
                          estimate["evidence_count"]>=30,
                          "Weak SCB 2022 sex-separated name prevalence evidence")
                else:check(False,"Unknown name-estimate method")
        files |= {"course-display.json", "route-candidates.json", "route-inventory.json", "historical-checkpoint-km.json", "official-result-classification.json", "name-based-classification.json"}
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
