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

<!-- begin:snapshot -->
| Measure | Value |
| --- | ---: |
| Facilities | 2,266 |
| Counties covered | 58 of 58 |
| Residential (licensed) | 1,063 |
| Outpatient and other (certified) | 1,203 |
| Offering detoxification | 1,041 |
| Listed with an expired license | 25 |
| Total reported capacity | 21,342 beds |
<!-- end:snapshot -->

## Files

| Path | Description |
| --- | --- |
| `data/facilities.csv` | Normalized dataset, one row per license number |
| `data/facilities.json` | The same records as JSON |
| `data/metadata.json` | Retrieval timestamp, record counts, and a content checksum |
| `data/raw/dhcs_facilities.json` | Unmodified API response, retained for the archive |

Field definitions are in [`docs/data-dictionary.md`](docs/data-dictionary.md).

A few rows, abridged to seven of the twenty-six columns:

<!-- begin:sample -->
| Facility | City | County | Setting | Detox | Capacity | Expires |
| --- | --- | --- | --- | --- | ---: | --- |
| CHRYSALIS | OAKLAND | Alameda County | RES | false | 20 | 2027-10-31 |
| HEALTHRIGHT 360 | LOS ANGELES | Los Angeles County | RES | false | 200 | 2026-09-30 |
| RESEDA RECOVERY CENTER INC | RESEDA | Los Angeles County | RES | true | 6 | 2027-04-30 |
| CHRISTOPHER CARE CHOOSING LIFE | MISSION VIEJO | Orange County | RES | true | 6 | 2027-12-31 |
| SOLUTIONS FOR RECOVERY | SAN DIEGO | San Diego County | NON | true | 0 | 2027-11-30 |
<!-- end:sample -->

## What normalization does

The published files are not a copy of the upstream extract. The pipeline:

- converts `Lic_Expiration_Date` from `M/D/YYYY` strings to ISO dates, and
  derives whether each license has already expired
- splits `Program_Code` into a setting code and a detox flag
- splits `Target_Population` into its numeric code and label
- expands `Type_of_Application` into separate licensed and certified booleans
- normalizes yes/no columns to booleans and blank strings to nulls
- strips trailing commas from city names, while leaving meaningful trailing
  periods in values like `INC.` and `AVE.` intact
- drops `OBJECTID` and the two empty unnamed columns, `F20` and `F21`
- discards coordinates that fall outside California's bounding box
- sorts by license number and writes deterministically, so a scheduled run only
  produces a diff when the underlying data actually changed

## Facilities by county

Counts of licensed and certified facilities, with reported capacity. Capacity is
concentrated in residential settings; most outpatient programs report zero beds.

<!-- begin:counties -->
| County | Facilities | Residential | Outpatient | Detox | Capacity |
| --- | ---: | ---: | ---: | ---: | ---: |
| Los Angeles | 826 | 455 | 371 | 479 | 7,758 |
| Orange | 298 | 163 | 135 | 166 | 2,044 |
| San Diego | 179 | 67 | 112 | 79 | 1,871 |
| Riverside | 127 | 65 | 62 | 60 | 1,224 |
| Sacramento | 65 | 27 | 38 | 23 | 712 |
| Ventura | 59 | 28 | 31 | 32 | 447 |
| San Bernardino | 58 | 19 | 39 | 20 | 781 |
| Fresno | 46 | 16 | 30 | 17 | 747 |
| Alameda | 42 | 15 | 27 | 3 | 401 |
| Contra Costa | 38 | 16 | 22 | 10 | 334 |
| Kern | 37 | 11 | 26 | 7 | 333 |
| Sonoma | 35 | 12 | 23 | 14 | 305 |
| San Francisco | 34 | 12 | 22 | 6 | 691 |
| Placer | 32 | 16 | 16 | 16 | 142 |
| Santa Barbara | 30 | 11 | 19 | 8 | 223 |
| Marin | 29 | 14 | 15 | 14 | 308 |
| Santa Clara | 29 | 8 | 21 | 8 | 239 |
| San Mateo | 22 | 11 | 11 | 2 | 186 |
| San Joaquin | 19 | 7 | 12 | 7 | 228 |
| Santa Cruz | 19 | 8 | 11 | 4 | 242 |
| Tulare | 19 | 8 | 11 | 3 | 194 |
| Monterey | 18 | 6 | 12 | 6 | 159 |
| Stanislaus | 18 | 5 | 13 | 4 | 162 |
| Butte | 13 | 4 | 9 | 1 | 116 |
| El Dorado | 13 | 6 | 7 | 3 | 127 |
| San Luis Obispo | 13 | 4 | 9 | 7 | 66 |
| Shasta | 13 | 4 | 9 | 2 | 126 |
| Solano | 12 | 5 | 7 | 2 | 98 |
| Sutter | 10 | 4 | 6 | 3 | 44 |
| Kings | 8 | 3 | 5 | 3 | 60 |
| Mendocino | 8 | 1 | 7 | 1 | 64 |
| Yolo | 7 | 2 | 5 | 3 | 100 |
| Humboldt | 6 | 3 | 3 | 2 | 140 |
| Lake | 6 | 2 | 4 | 0 | 75 |
| Merced | 6 | 2 | 4 | 0 | 81 |
| Napa | 6 | 2 | 4 | 2 | 106 |
| Nevada | 6 | 2 | 4 | 2 | 87 |
| Yuba | 6 | 4 | 2 | 4 | 53 |
| Madera | 5 | 1 | 4 | 1 | 10 |
| San Benito | 5 | 3 | 2 | 3 | 37 |
| Tuolumne | 5 | 3 | 2 | 3 | 46 |
| Calaveras | 4 | 3 | 1 | 2 | 112 |
| Imperial | 4 | 0 | 4 | 4 | 0 |
| Siskiyou | 4 | 0 | 4 | 0 | 0 |
| Tehama | 4 | 2 | 2 | 1 | 39 |
| Glenn | 3 | 0 | 3 | 1 | 0 |
| Mariposa | 3 | 1 | 2 | 1 | 12 |
| (not reported) | 2 | 1 | 1 | 1 | 6 |
| Amador | 2 | 1 | 1 | 1 | 6 |
| Inyo | 2 | 0 | 2 | 0 | 0 |
| Sierra | 2 | 0 | 2 | 0 | 0 |
| Trinity | 2 | 0 | 2 | 0 | 0 |
| Alpine | 1 | 0 | 1 | 0 | 0 |
| Colusa | 1 | 0 | 1 | 0 | 0 |
| Del Norte | 1 | 0 | 1 | 0 | 0 |
| Lassen | 1 | 0 | 1 | 0 | 0 |
| Modoc | 1 | 0 | 1 | 0 | 0 |
| Mono | 1 | 0 | 1 | 0 | 0 |
| Plumas | 1 | 0 | 1 | 0 | 0 |
| **Statewide** | **2,266** | **1,063** | **1,203** | **1,041** | **21,342** |
<!-- end:counties -->

## Running locally

Requires Python 3.9 or newer. There are no third-party dependencies.

```bash
python3 scripts/fetch.py          # writes data/raw/dhcs_facilities.json
python3 scripts/normalize.py      # writes data/facilities.{csv,json} and metadata.json
python3 scripts/render_readme.py  # regenerates the tables in this file
```

The tables above are generated. Edit `scripts/render_readme.py` rather than the
regions between the `begin:` and `end:` markers, which are overwritten on every
run.

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
