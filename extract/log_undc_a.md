# Extraction log — UN System Data Commons (batch A: mortality, fertility, life expectancy, population)

Date of extraction: 2026-10-25. Platform label: `UN_DataCommons`. MCP server: `UN_System_Data_Commons`.
Playbook read before any tool call: `skill://data-commons-researcher/SKILL.md`.

Countries (place DCIDs): country/NGA Nigeria, country/ETH Ethiopia, country/IND India, country/BGD Bangladesh, country/BRA Brazil.

Output files:
- `/home/claude/extract/metadata_undc_a.csv` — 16 rows (one per variable x facet; every variable had exactly one facet for these five countries).
- `/home/claude/extract/values_undc_a.csv` — 705 observation rows (80 get_observations calls, 16 variables x 5 countries).
- `/home/claude/extract/log_undc_a.md` — this file.

All values were written exactly as the JSON literal returned by the API (parsed as strings, never re-serialised as floats). A post-write check compared every CSV value against the saved raw responses: 705/705 identical, 0 duplicate (indicator, iso3, year) keys.

## Step A — get_variable_metadata (2 calls, both status SUCCESS)

| Call | Variables | Result |
|---|---|---|
| A1 | SH_DYN_MORT (u5mr), SH_DYN_NMRT (nmr), WHO MORT_NEONATAL_RATE (nmr_who), SH_DYN_IMRT (imr), SH_STA_MORT (mmr), UNICEF MNCH_MMR (mmr_unicef), UNDP GII_mmr (mmr_undp) | SUCCESS, 7 variables, 1 facet each, all 5 countries covered |
| A2 | UNICEF CME_SBR (sbr), WHO STILLBIRTH_RATE (sbr_who), UNICEF DM_FRATE_TOT (tfr), SP_DYN_ADKL (abr), UNICEF MNCH_ABR (abr_unicef), UNDP GII_abr (abr_undp), WHO LIFE_EXPECT (le0), UNDP HDI_le (le0_undp), UNICEF DM_POP (pop_u5) | SUCCESS, 9 variables, 1 facet each, all 5 countries covered |

Note: batch A2 carried 9 variable DCIDs rather than 7 (the brief said "two batches of 7" but listed 16 DCIDs); the API accepted it without issue.

Metadata observations:
- No variable returned a `description` field, and none returned `observation_properties` (so none is a multi-entity variable). Those CSV columns are therefore empty for all rows.
- Facet properties returned were only `observationPeriod` (P1Y for every facet) and `unit`; no measurementMethod, scalingFactor, import or release date was present. These, plus the variable `properties` block (populationType, statType, constraintProperties, undataAge/undataSex/undataEstBasis, measuredProperty) and the provenance properties, are in `extra_json`.
- Provenance `source` is "United Nations" for all four provenances (undata/p/SDG, undata/p/UNICEF, undata/p/WHO, undata/p/UNDP_HDRO), each with `isPartOf: United Nations Statistics Division`; the custodian is distinguishable only by the provenance id and `url` (unstats.un.org/sdgs/dataportal, data.unicef.org, who.int/data, hdr.undp.org).
- The three SDG CME variables (u5mr, nmr, imr) share the same facet id 2425806575015910660 (same SDG import). Facet-level `obsCount` and `dateRange` refer to the scope of the five requested countries (e.g. u5mr: 125 obs, 2000–2024 = 25 years x 5 countries).

Facet date ranges (metadata, all 5 countries): u5mr/nmr/imr 2000–2024; nmr_who 1952–2023 (292 obs); mmr/mmr_unicef 2000–2023; mmr_undp 1990–2023; sbr/sbr_who 2000–2023; tfr 2000–2025; abr/abr_unicef 2000–2023 (97 obs, i.e. gaps); abr_undp 1990–2023; le0 (WHO) 2000–2021; le0_undp 1990–2023; pop_u5 2000–2025.

## Step B — get_observations (80 calls)

Parameters for every call: `date="range"`, `date_range_start="2015"`, `date_range_end="2024"`. The API accepted `date="range"` on every call; no fallback to `date="all"` was needed. Every call returned HTTP-level success and a non-empty series.

Response shape: the server returned a tabular shape (`sourceMetadata`, `entityMetadata`, `data.columns` = [observationAbout, date, value], `data.rows`) rather than the `placeObservations/timeSeries` shape described in the playbook. No `alternativeSources` key was present in any response (noted in the `notes` column of every row), and no observation carried lower/upper bounds — the `lower`, `upper` and `alternative_sources` columns are empty throughout. `sourceMetadata.unit` was copied to `unit_note`.

| indicator_key | variable DCID | facet (sourceId) | provenance URL | NGA | ETH | IND | BGD | BRA |
|---|---|---|---|---|---|---|---|---|
| u5mr | undata/sdg/SH_DYN_MORT.AGE--Y0T4 | 2425806575015910660 | unstats.un.org/sdgs/dataportal | OK 10 (2015–2024) | OK 10 (2015–2024) | OK 10 (2015–2024) | OK 10 (2015–2024) | OK 10 (2015–2024) |
| nmr | undata/sdg/SH_DYN_NMRT.AGE--M0 | 2425806575015910660 | unstats.un.org/sdgs/dataportal | OK 10 (2015–2024) | OK 10 (2015–2024) | OK 10 (2015–2024) | OK 10 (2015–2024) | OK 10 (2015–2024) |
| nmr_who | undata/who/MORT_NEONATAL_RATE.AGE--D0T27__EST_BASIS--MODEL | 8513065162097383762 | who.int/data | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) |
| imr | undata/sdg/SH_DYN_IMRT.AGE--Y0 | 2425806575015910660 | unstats.un.org/sdgs/dataportal | OK 10 (2015–2024) | OK 10 (2015–2024) | OK 10 (2015–2024) | OK 10 (2015–2024) | OK 10 (2015–2024) |
| mmr | undata/sdg/SH_STA_MORT.SEX--F | 5746826742182915890 | unstats.un.org/sdgs/dataportal | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) |
| mmr_unicef | undata/unicef/MNCH_MMR.SEX--F | 10718169538713698758 | data.unicef.org | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) |
| mmr_undp | undata/undphdro/GII_mmr.SEX--F | 7922698253759988974 | hdr.undp.org | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) |
| sbr | undata/unicef/CME_SBR | 17074264088979274996 | data.unicef.org | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) |
| sbr_who | undata/who/STILLBIRTH_RATE | 402228947309153478 | who.int/data | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) |
| tfr | undata/unicef/DM_FRATE_TOT | 1896065916138908710 | data.unicef.org | OK 10 (2015–2024) | OK 10 (2015–2024) | OK 10 (2015–2024) | OK 10 (2015–2024) | OK 10 (2015–2024) |
| abr | undata/sdg/SP_DYN_ADKL.AGE--Y15T19__SEX--F | 10542619612277702061 | unstats.un.org/sdgs/dataportal | OK 5 (2015–2020; no 2018) | OK 2 (2016–2017) | OK 6 (2015–2020) | OK 9 (2015–2023) | OK 8 (2015–2022) |
| abr_unicef | undata/unicef/MNCH_ABR.AGE--Y15T19 | 11769139301642030360 | data.unicef.org | OK 5 (2015–2020; no 2018) | OK 2 (2016–2017) | OK 6 (2015–2020) | OK 9 (2015–2023) | OK 8 (2015–2022) |
| abr_undp | undata/undphdro/GII_abr.AGE--Y15T19__SEX--F | 8414898729775726004 | hdr.undp.org | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) |
| le0 | undata/who/LIFE_EXPECT.AGE--Y0 | 7248648420381455101 | who.int/data | OK 7 (2015–2021) | OK 7 (2015–2021) | OK 7 (2015–2021) | OK 7 (2015–2021) | OK 7 (2015–2021) |
| le0_undp | undata/undphdro/HDI_le | 11910738306687386597 | hdr.undp.org | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) | OK 9 (2015–2023) |
| pop_u5 | undata/unicef/DM_POP.AGE--Y0T4 | 9589496361978137601 | data.unicef.org | OK 10 (2015–2024) | OK 10 (2015–2024) | OK 10 (2015–2024) | OK 10 (2015–2024) | OK 10 (2015–2024) |

Rows per indicator: u5mr 50, nmr 50, nmr_who 45, imr 50, mmr 45, mmr_unicef 45, mmr_undp 45, sbr 45, sbr_who 45, tfr 50, abr 30, abr_unicef 30, abr_undp 45, le0 35, le0_undp 45, pop_u5 50 = 705.

Latest year available (within the 2015–2024 window) per indicator: u5mr 2024; nmr 2024; nmr_who 2023; imr 2024; mmr 2023; mmr_unicef 2023; mmr_undp 2023; sbr 2023; sbr_who 2023; tfr 2024; abr 2023 (BGD only; BRA 2022, NGA/IND 2020, ETH 2017); abr_unicef same as abr; abr_undp 2023; le0 (WHO) 2021; le0_undp 2023; pop_u5 2024 (metadata facet range extends to 2025 for tfr and pop_u5, outside the requested window).

The primary source (facet id and provenance URL) was identical across all five countries for every variable — no country-level source switching observed.

## Anomalies and notes for the reviewer

1. **Variable naming / concept check.** All 16 DCIDs resolved to the expected concept. Two labels deserve a flag:
   - `undata/who/LIFE_EXPECT.AGE--Y0` is named "Life expectancy [Age=Under 1 year old]" — the age constraint denotes age 0, i.e. life expectancy at birth, not a mortality measure.
   - `undata/sdg/SH_DYN_MORT.AGE--Y0T4` is named generically "Mortality rate [Age=Under 5 years old]" (the SDG 3.2.1 U5MR); the unit confirms per 1,000 live births.
2. **Unit label inconsistency for nmr_who.** `undata/who/MORT_NEONATAL_RATE...` carries unit `undata/UNIT_MEASURE-RATIO_COUNT_DEATHS_PER_100000_COUNT_BIRTHS` (per 100,000) but the values (e.g. Nigeria 2023 = 33.699321977; Brazil 2023 = 7.609497202) are of the same magnitude as the SDG NMR per 1,000 live births (Nigeria 2023 = 39.23941847; Brazil 2023 = 7.595652). The unit metadata is almost certainly mislabelled; values were kept exactly as returned. Similarly, `mmr_undp` uses `RATE_MORTALITY_PER_100000_COUNT` while mmr uses `RATIO_COUNT_PER_100000_COUNT_LIVEBIRTHS` — same magnitude, different unit codes.
3. **nmr vs nmr_who diverge for Nigeria.** SDG NMR rises 2015→2023 (37.99→39.24) while WHO model-based NMR falls (37.14→33.70); for ETH/IND/BGD/BRA the two series are near-identical. Likely different UN IGME revision rounds behind the two imports.
4. **mmr_unicef is a 2-decimal rounding of mmr (SDG)** for every country-year (e.g. NGA 2023: 992.82921 vs 992.83); same underlying MMEIG estimates. `mmr_undp` (HDRO) differs and is flat from 2020 onward for all five countries (e.g. NGA 2020–2023 all 1047.235352; IND 102.653912; BGD 123.0282527; BRA 72.14753684; ETH 266.6895641) — HDRO carries the last available MMEIG value forward, so 2021–2023 are not independent observations.
5. **sbr_who is sbr (UNICEF) at lower precision** (same values to 9 decimals vs 13 decimals, e.g. IND 2023 11.8088 vs 11.8088000000281).
6. **abr (SDG) and abr_unicef are the same survey-based series** (SDG at 6 decimals, UNICEF at 1 decimal) with identical gaps: NGA missing 2018 and ending 2020; ETH only 2016–2017; IND ending 2020; BRA ending 2022; BGD through 2023. BGD 2018–2020 are round integers (75, 74, 74). `abr_undp` (HDRO) is a continuous modelled series 2015–2023 for all five countries and differs materially (e.g. NGA 2020: 74.629028 SDG vs 89.081 HDRO; IND 2020: 11.3 vs 14.423).
7. **le0 (WHO) vs le0_undp (HDRO) disagree sharply for Nigeria**: WHO 2021 = 63.3974984 vs HDRO 2021 = 53.455 (HDRO 2015 = 51.939 vs WHO 61.73359862). For ETH/IND/BGD/BRA the two are within ~1–3 years. WHO series ends 2021; HDRO continues to 2023. Note also WHO LE for India drops to 67.30780612 in 2021 (COVID-19 year) and HDRO shows the same dip (67.282).
8. **Ethiopia u5mr/imr spikes in 2021–2022** (u5mr 51.52→70.35→68.06→51.49; imr 39.41→49.86→48.32→38.67) while nmr declines smoothly. Returned as-is; plausibly conflict-related excess mortality in the IGME 2024 round.
9. **Brazil mmr 2021 = 127.99026 (COVID-19 year peak)**, back to 66.91036 in 2023; India mmr 2021 = 154.79778 vs 100.5309 in 2020 and 89.64525 in 2022; Bangladesh mmr 2021 = 193.89067 vs 151.84625 in 2020. All returned as-is.
10. **Nigeria u5mr/imr/nmr essentially flat or rising 2015–2024** (u5mr 117.82→115.65; nmr 37.99→39.05; imr 68.00→69.77). Returned as-is.
11. **tfr unit** is `undata/UNIT_MEASURE-COUNT` (births per woman implied); `pop_u5` is `COUNT_PERSONS` with integer values.
12. **Working-directory collision.** A parallel extraction job (batch B, writing `*_undc_b.csv`) overwrote two helper scripts in the shared scratchpad root during this run. No `_a` output file was touched; this job's helpers were moved into a private subfolder (`scratchpad/undc_a/`) and all saved raw responses (`obs_<key>.json`) are kept there for audit.
13. **No errors, no empty responses, no retries** across all 82 tool calls (2 metadata + 80 observations).
