#!/usr/bin/env python3
"""Normalize the raw DHCS extract into the published CSV and JSON files.

Output ordering and formatting are deterministic so that scheduled runs produce
diffs only when the underlying licensing data actually changes.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "dhcs_facilities.json"
CSV_PATH = ROOT / "data" / "facilities.csv"
JSON_PATH = ROOT / "data" / "facilities.json"
METADATA_PATH = ROOT / "data" / "metadata.json"

DATASET_URL = "https://data.ca.gov/dataset/sud-recovery-treatment-facilities"
DATASET_LICENSE = "CC-BY 4.0, California Open Data Portal"

DETOX_SUFFIX = "-DETOX"
LATITUDE_RANGE = (32.0, 42.5)
LONGITUDE_RANGE = (-125.0, -113.5)

FIELDS = [
    "license_number",
    "facility_name",
    "legal_entity",
    "address_line1",
    "address_line2",
    "additional_locations",
    "city",
    "state",
    "zip",
    "county",
    "county_code",
    "phone",
    "setting_code",
    "offers_detox",
    "is_licensed",
    "is_certified",
    "license_expiration",
    "license_expired",
    "treatment_capacity",
    "total_capacity",
    "target_population_code",
    "target_population",
    "incidental_medical_services",
    "adolescent_waiver",
    "latitude",
    "longitude",
]


def clean(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def parse_yes_no(value: object) -> bool | None:
    text = clean(value)
    if text is None:
        return None
    return {"yes": True, "no": False}.get(text.lower())


def parse_expiration(value: object) -> str | None:
    text = clean(value)
    if text is None:
        return None
    try:
        return datetime.strptime(text, "%m/%d/%Y").date().isoformat()
    except ValueError:
        return None


def split_program_code(value: object) -> tuple[str | None, bool | None]:
    text = clean(value)
    if text is None:
        return None, None
    if text.upper().endswith(DETOX_SUFFIX):
        return text[: -len(DETOX_SUFFIX)], True
    return text, False


def split_target_population(value: object) -> tuple[str | None, str | None]:
    text = clean(value)
    if text is None:
        return None, None
    if "---" in text:
        code, _, label = text.partition("---")
        return clean(code), clean(label)
    return None, text


def parse_authorization(value: object) -> tuple[bool, bool]:
    text = (clean(value) or "").lower()
    return "licensed" in text, "certified" in text


def parse_capacity(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def parse_city(value: object) -> str | None:
    text = clean(value)
    if text is None:
        return None
    return clean(text.rstrip(","))


def parse_zip(value: object) -> str | None:
    text = clean(value)
    if text is None:
        return None
    digits = "".join(character for character in text if character.isdigit())
    if len(digits) >= 9:
        return f"{digits[:5]}-{digits[5:9]}"
    return digits[:5] if len(digits) >= 5 else None


def parse_coordinate(value: object, bounds: tuple[float, float]) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    low, high = bounds
    if not low <= number <= high:
        return None
    return round(number, 6)


def normalize(record: dict, today: date) -> dict:
    setting_code, offers_detox = split_program_code(record.get("Program_Code"))
    population_code, population = split_target_population(record.get("Target_Population"))
    is_licensed, is_certified = parse_authorization(record.get("Type_of_Application"))
    expiration = parse_expiration(record.get("Lic_Expiration_Date"))

    return {
        "license_number": clean(record.get("Application_Number")),
        "facility_name": clean(record.get("Facility_Name")),
        "legal_entity": clean(record.get("Legal_Entity_Name")),
        "address_line1": clean(record.get("Facility_Address1")),
        "address_line2": clean(record.get("Facility_Address2")),
        "additional_locations": clean(record.get("Additional_Facility_Locations")),
        "city": parse_city(record.get("Facility_City")),
        "state": clean(record.get("Facility_State")),
        "zip": parse_zip(record.get("Facility_Zip")),
        "county": clean(record.get("CountyName")),
        "county_code": clean(record.get("County_Code")),
        "phone": clean(record.get("Facility_Phone")),
        "setting_code": setting_code,
        "offers_detox": offers_detox,
        "is_licensed": is_licensed,
        "is_certified": is_certified,
        "license_expiration": expiration,
        "license_expired": None if expiration is None else expiration < today.isoformat(),
        "treatment_capacity": parse_capacity(record.get("Treatment_Capacity")),
        "total_capacity": parse_capacity(record.get("Total_Capacity")),
        "target_population_code": population_code,
        "target_population": population,
        "incidental_medical_services": parse_yes_no(record.get("Incident_Medical_Services")),
        "adolescent_waiver": parse_yes_no(record.get("Adolescent_Waiver")),
        "latitude": parse_coordinate(record.get("Latitude"), LATITUDE_RANGE),
        "longitude": parse_coordinate(record.get("Longitude"), LONGITUDE_RANGE),
    }


def deduplicate(rows: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    duplicates = 0
    for row in rows:
        key = row["license_number"]
        if key in seen:
            duplicates += 1
            continue
        seen[key] = row
    if duplicates:
        print(f"collapsed {duplicates} duplicate license numbers", file=sys.stderr)
    return sorted(seen.values(), key=lambda row: row["license_number"])


def csv_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def write_csv(rows: list[dict]) -> None:
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(row[field]) for field in FIELDS})


def write_json(rows: list[dict]) -> None:
    JSON_PATH.write_text(
        json.dumps(rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_metadata(rows: list[dict], retrieved_at: str | None) -> None:
    counties = Counter(row["county"] for row in rows if row["county"])
    metadata = {
        "dataset_url": DATASET_URL,
        "license": DATASET_LICENSE,
        "publisher": "California Department of Health Care Services",
        "retrieved_at": retrieved_at,
        "normalized_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "record_count": len(rows),
        "county_count": len(counties),
        "expired_count": sum(1 for row in rows if row["license_expired"]),
        "detox_count": sum(1 for row in rows if row["offers_detox"]),
        "content_sha256": hashlib.sha256(CSV_PATH.read_bytes()).hexdigest(),
    }
    METADATA_PATH.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    raw = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    today = datetime.now(timezone.utc).date()

    rows = [normalize(record, today) for record in raw["records"]]
    skipped = [row for row in rows if not row["license_number"]]
    if skipped:
        print(f"skipped {len(skipped)} records without a license number", file=sys.stderr)

    rows = deduplicate([row for row in rows if row["license_number"]])

    write_csv(rows)
    write_json(rows)
    write_metadata(rows, raw.get("retrieved_at"))

    print(f"wrote {len(rows)} records", file=sys.stderr)


if __name__ == "__main__":
    main()
