#!/usr/bin/env python3
"""Regenerate the tables in README.md from the normalized dataset.

Each generated section is delimited by begin/end markers so the scheduled
refresh keeps the published figures consistent with data/facilities.csv.
"""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "facilities.csv"
README_PATH = ROOT / "README.md"

CALIFORNIA_COUNTY_COUNT = 58
SAMPLE_SIZE = 5
SAMPLE_COLUMNS = [
    ("facility_name", "Facility"),
    ("city", "City"),
    ("county", "County"),
    ("setting_code", "Setting"),
    ("offers_detox", "Detox"),
    ("total_capacity", "Capacity"),
    ("license_expiration", "Expires"),
]


def read_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_int(value: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def table(headers: list[str], rows: list[list[str]], align_right: set[int]) -> str:
    separator = [
        "---:" if index in align_right else "---" for index in range(len(headers))
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def render_snapshot(rows: list[dict[str, str]]) -> str:
    counties = {row["county"] for row in rows if row["county"]}
    residential = sum(1 for row in rows if row["setting_code"] == "RES")
    beds = sum(as_int(row["total_capacity"]) for row in rows)

    figures = [
        ["Facilities", f"{len(rows):,}"],
        ["Counties covered", f"{len(counties)} of {CALIFORNIA_COUNTY_COUNT}"],
        ["Residential (licensed)", f"{residential:,}"],
        ["Outpatient and other (certified)", f"{len(rows) - residential:,}"],
        ["Offering detoxification", f"{sum(1 for r in rows if r['offers_detox'] == 'true'):,}"],
        ["Listed with an expired license", f"{sum(1 for r in rows if r['license_expired'] == 'true'):,}"],
        ["Total reported capacity", f"{beds:,} beds"],
    ]
    return table(["Measure", "Value"], figures, align_right={1})


def render_sample(rows: list[dict[str, str]]) -> str:
    step = max(len(rows) // SAMPLE_SIZE, 1)
    selected = [rows[index * step] for index in range(min(SAMPLE_SIZE, len(rows)))]

    headers = [label for _, label in SAMPLE_COLUMNS]
    body = [[(row[field] or "") for field, _ in SAMPLE_COLUMNS] for row in selected]
    return table(headers, body, align_right={5})


def render_counties(rows: list[dict[str, str]]) -> str:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["county"] or "(not reported)"].append(row)

    body = []
    totals = Counter()
    for county, county_rows in sorted(
        grouped.items(), key=lambda item: (-len(item[1]), item[0])
    ):
        residential = sum(1 for row in county_rows if row["setting_code"] == "RES")
        detox = sum(1 for row in county_rows if row["offers_detox"] == "true")
        beds = sum(as_int(row["total_capacity"]) for row in county_rows)

        totals["facilities"] += len(county_rows)
        totals["residential"] += residential
        totals["outpatient"] += len(county_rows) - residential
        totals["detox"] += detox
        totals["beds"] += beds

        body.append(
            [
                county.removesuffix(" County"),
                f"{len(county_rows):,}",
                f"{residential:,}",
                f"{len(county_rows) - residential:,}",
                f"{detox:,}",
                f"{beds:,}",
            ]
        )

    body.append(
        [
            "**Statewide**",
            f"**{totals['facilities']:,}**",
            f"**{totals['residential']:,}**",
            f"**{totals['outpatient']:,}**",
            f"**{totals['detox']:,}**",
            f"**{totals['beds']:,}**",
        ]
    )

    headers = ["County", "Facilities", "Residential", "Outpatient", "Detox", "Capacity"]
    return table(headers, body, align_right={1, 2, 3, 4, 5})


def replace_block(text: str, name: str, body: str) -> str:
    start = f"<!-- begin:{name} -->"
    end = f"<!-- end:{name} -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if not pattern.search(text):
        raise RuntimeError(f"Marker block '{name}' not found in README.md")
    return pattern.sub(lambda _: f"{start}\n{body}\n{end}", text)


def main() -> None:
    rows = read_rows()
    readme = README_PATH.read_text(encoding="utf-8")

    readme = replace_block(readme, "snapshot", render_snapshot(rows))
    readme = replace_block(readme, "sample", render_sample(rows))
    readme = replace_block(readme, "counties", render_counties(rows))

    README_PATH.write_text(readme, encoding="utf-8")
    print(f"rendered README.md from {len(rows)} records")


if __name__ == "__main__":
    main()
