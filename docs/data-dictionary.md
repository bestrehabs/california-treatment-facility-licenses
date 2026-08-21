# Data dictionary

One row per DHCS license number. Fields are derived from the DHCS
`SUD_Recovery_Treatment_Facilities` layer; the "Source field" column gives the
upstream name so every value can be traced back to the publisher.

| Field | Type | Source field | Notes |
| --- | --- | --- | --- |
| `license_number` | string | `Application_Number` | Primary key. Unique across all records. |
| `facility_name` | string | `Facility_Name` | Published in uppercase by DHCS; left as-is. |
| `legal_entity` | string | `Legal_Entity_Name` | Operating entity, which often runs several facilities. |
| `address_line1` | string | `Facility_Address1` | |
| `address_line2` | string | `Facility_Address2` | Empty for 67% of records. |
| `additional_locations` | string | `Additional_Facility_Locations` | Free text. Empty for 86% of records. |
| `city` | string | `Facility_City` | |
| `state` | string | `Facility_State` | Always `CA`. |
| `zip` | string | `Facility_Zip` | Five digits, or `ZZZZZ-NNNN` where a plus-four is present. |
| `county` | string | `CountyName` | All 58 California counties appear. |
| `county_code` | string | `County_Code` | Two-digit, zero-padded. |
| `phone` | string | `Facility_Phone` | Published format `(NNN) NNN-NNNN`. |
| `setting_code` | string | `Program_Code` | See "Setting codes" below. |
| `offers_detox` | boolean | `Program_Code` | True when the source code carries the `-DETOX` suffix. |
| `is_licensed` | boolean | `Type_of_Application` | |
| `is_certified` | boolean | `Type_of_Application` | |
| `license_expiration` | date | `Lic_Expiration_Date` | Converted from `M/D/YYYY` to ISO `YYYY-MM-DD`. |
| `license_expired` | boolean | derived | Expiration earlier than the date the file was generated. |
| `treatment_capacity` | integer | `Treatment_Capacity` | Zero for most non-residential settings. |
| `total_capacity` | integer | `Total_Capacity` | |
| `target_population_code` | string | `Target_Population` | Numeric prefix, e.g. `1.1`. |
| `target_population` | string | `Target_Population` | Label, e.g. `CO-ED`. |
| `incidental_medical_services` | boolean | `Incident_Medical_Services` | DHCS refers to this as incidental medical services (IMS). |
| `adolescent_waiver` | boolean | `Adolescent_Waiver` | |
| `latitude` | float | `Latitude` | Six decimal places. Null when outside California's bounding box. |
| `longitude` | float | `Longitude` | Six decimal places. Null when outside California's bounding box. |

The source layer also contains `OBJECTID` and two unnamed columns, `F20` and
`F21`. `OBJECTID` is a row identifier that is not stable across refreshes, and
`F20` and `F21` are null for every record. All three are dropped.

## Setting codes

`Program_Code` combines a setting with an optional detox suffix. This split
separates the two, but **DHCS does not publish a definition of the setting
codes** in the dataset metadata, so the codes are preserved verbatim rather than
expanded into labels. Confirm their meaning with DHCS before relying on them.

What can be stated is the observed distribution and its relationship to
authorization type, which is consistent across every record:

| `setting_code` | Records | Authorization |
| --- | --- | --- |
| `NON` | 1,152 | Certified only |
| `RES` | 1,063 | Licensed (511 of these also certified) |
| `DSS` | 48 | Certified only |
| `DPH` | 3 | Certified only |

This pattern lines up with DHCS's published scope: the department
[licenses residential SUD facilities](https://www.dhcs.ca.gov/providers-partners/facility-licensing/)
and [certifies outpatient programs](https://www.dhcs.ca.gov/providers-partners/program-certification/),
while facilities licensed by the Department of Social Services or Department of
Public Health are exempt from DHCS residential licensure and may hold
certification only.

## Target population codes

| Code | Label |
| --- | --- |
| `1.1` | CO-ED |
| `1.2` | MEN ONLY |
| `1.3` | WOMEN ONLY |
| `1.4` | WOMEN/CHILDREN |
| `1.5` | YOUTH/ADOLESCENT |
| `1.7` | FAMILIES |
| `1.8` | DUAL DIAGNOSIS |
| `1.9` | CO-ED/CHILDREN |
| `1.10` | CO-ED/YOUTH |
| `1.11` | MEN/YOUTH |
| `1.12` | WOMEN/YOUTH |
| `1.13` | CO-ED/CHILD/DUAL |
| `1.14` | WOMEN/CHILD/DUAL |

Code `1.6` does not appear in the data. Eight records have no target population
value.

## Completeness

Measured against the most recent refresh:

| Field | Missing |
| --- | --- |
| `address_line1`, `city`, `state`, `zip` | 1 record |
| `county` | 2 records |
| `latitude`, `longitude` | 2 records |
| `phone` | 19 records |
| `target_population` | 8 records |

Every `license_expiration` value parsed successfully.
