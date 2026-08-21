# California Treatment Facility Licenses

A cleaned, weekly-updated dataset of every substance use disorder treatment
facility licensed or certified by the California Department of Health Care
Services (DHCS).

DHCS publishes this list as a live snapshot that is overwritten in place with
each update, so no public record exists of how licensure changes over time. This
repository normalizes the snapshot and commits it on a schedule, which turns the
commit history into a dated archive: which facilities appear, which lapse, and
how treatment capacity shifts by county.

## Current snapshot

| | |
| --- | --- |
| Facilities | 2,266 |
| Counties covered | 58 of 58 |
| Residential (licensed) | 1,063 |
| Outpatient and other (certified) | 1,203 |
| Offering detoxification | 1,041 |
| Listed with an expired license | 25 |

## Files

| Path | Description |
| --- | --- |
| `data/facilities.csv` | Normalized dataset, one row per license number |
| `data/facilities.json` | The same records as JSON |
| `data/metadata.json` | Retrieval timestamp, record counts, and a content checksum |
| `data/raw/dhcs_facilities.json` | Unmodified API response, retained for the archive |

Field definitions are in [`docs/data-dictionary.md`](docs/data-dictionary.md).

## What normalization does

The published files are not a copy of the upstream extract. The pipeline:

- converts `Lic_Expiration_Date` from `M/D/YYYY` strings to ISO dates, and
  derives whether each license has already expired
- splits `Program_Code` into a setting code and a detox flag
- splits `Target_Population` into its numeric code and label
- expands `Type_of_Application` into separate licensed and certified booleans
- normalizes yes/no columns to booleans and blank strings to nulls
- drops `OBJECTID` and the two empty unnamed columns, `F20` and `F21`
- discards coordinates that fall outside California's bounding box
- sorts by license number and writes deterministically, so a scheduled run only
  produces a diff when the underlying data actually changed

## Running locally

Requires Python 3.9 or newer. There are no third-party dependencies.

```bash
python3 scripts/fetch.py      # writes data/raw/dhcs_facilities.json
python3 scripts/normalize.py  # writes data/facilities.{csv,json} and metadata.json
```

## Updates

A scheduled workflow refreshes the data every Monday and commits any changes. It
can also be triggered manually from the Actions tab.

## Limitations

- DHCS does not publish definitions for the setting codes (`RES`, `NON`, `DSS`,
  `DPH`). They are preserved verbatim rather than expanded. See the data
  dictionary for the observed distribution.
- Records reflect what DHCS has published, including apparent staleness. Twenty
  five facilities in the current snapshot carry an expiration date in the past.
- `Additional_Facility_Locations` is free text and is not parsed into structured
  addresses.
- Refresh frequency is weekly, so the data can trail the upstream source by up
  to seven days. Query the
  [source layer](https://data.ca.gov/dataset/sud-recovery-treatment-facilities)
  directly if you need live values.

## Scope

This is licensing and certification data. A license indicates that a facility
has met DHCS requirements to operate; it is not a measure of treatment quality,
outcomes, or suitability, and nothing here ranks or endorses any provider.
Verify a facility's current status with DHCS before relying on it.

If you or someone you know needs help, SAMHSA's National Helpline is
1-800-662-4357, and the Suicide & Crisis Lifeline is 988.

## Source and license

Data is published by the California Department of Health Care Services on the
[California Open Data Portal](https://data.ca.gov/dataset/sud-recovery-treatment-facilities)
under CC-BY 4.0, and is redistributed here under those terms with attribution to
DHCS.

The code in this repository is available under the MIT License. See
[`LICENSE`](LICENSE).
