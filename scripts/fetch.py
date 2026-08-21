#!/usr/bin/env python3
"""Download the DHCS SUD Recovery Treatment Facilities layer to data/raw/.

The layer is a live snapshot that DHCS overwrites in place, so each run is
archived verbatim to preserve state that the upstream source does not retain.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

LAYER_URL = (
    "https://services7.arcgis.com/7MUwsS9z05YumJRZ/arcgis/rest/services"
    "/SUD_Recovery_Treatment_Facilities/FeatureServer/0"
)
PAGE_SIZE = 1000
REQUEST_TIMEOUT = 60
MAX_ATTEMPTS = 4

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "dhcs_facilities.json"


def request_json(params: dict[str, str]) -> dict:
    url = f"{LAYER_URL}/query?{urllib.parse.urlencode(params)}"
    last_error: Exception | None = None

    for attempt in range(MAX_ATTEMPTS):
        try:
            with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            last_error = error
        else:
            if "error" in payload:
                raise RuntimeError(f"ArcGIS returned an error: {payload['error']}")
            return payload
        time.sleep(2**attempt)

    raise RuntimeError(f"Request failed after {MAX_ATTEMPTS} attempts: {last_error}")


def expected_count() -> int:
    payload = request_json({"where": "1=1", "returnCountOnly": "true", "f": "json"})
    return int(payload["count"])


def fetch_records() -> list[dict]:
    expected = expected_count()
    records: list[dict] = []

    while len(records) < expected:
        payload = request_json(
            {
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "false",
                "orderByFields": "OBJECTID",
                "resultOffset": str(len(records)),
                "resultRecordCount": str(PAGE_SIZE),
                "f": "json",
            }
        )
        batch = payload.get("features", [])
        if not batch:
            break
        records.extend(feature["attributes"] for feature in batch)
        print(f"fetched {len(records)}/{expected}", file=sys.stderr)

    if len(records) != expected:
        raise RuntimeError(f"Expected {expected} records but received {len(records)}")

    return records


def main() -> None:
    records = fetch_records()

    document = {
        "source_layer": LAYER_URL,
        "retrieved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "record_count": len(records),
        "records": records,
    }

    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    RAW_PATH.write_text(
        json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {RAW_PATH.relative_to(ROOT)}", file=sys.stderr)


if __name__ == "__main__":
    main()
