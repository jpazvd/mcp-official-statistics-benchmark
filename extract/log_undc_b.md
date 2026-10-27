# UN System Data Commons extraction log (batch B)

Date: 2026-10-25. Platform: UN System Data Commons MCP server (`UN_System_Data_Commons`).
Countries: country/NGA, country/ETH, country/IND, country/BGD, country/BRA.
Outputs: `/home/claude/extract/metadata_undc_b.csv` (32 facet rows, 24 variables), `/home/claude/extract/values_undc_b.csv` (645 observation rows).
All values written exactly as returned by the API (JSON numeric repr; no rounding).

## Setup calls
| Call | Status |
|---|---|
| ToolSearch (4 schemas) | OK |
| ReadMcpResourceTool `skill://data-commons-researcher/SKILL.md` | OK |
| `search_indicators(query="measles first dose MCV1 coverage children 1 year", include_topics=false, places=[Nigeria, India])` | OK, 10 variables, ALL WHO subgroup variables (sex, urban/rural, wealth decile, mother's age, education) — no national variable in this result |
| `search_indicators(query="IM_MCV1", include_topics=false, places=[Nigeria])` | OK, 10 variables; includes NATIONAL `undata/who/IMM_COV_SH.AGE--Y1__VACCINE--MCV1` ("Immunization coverage [Age=1 year old, Vaccine=Measles first dose]", WHO). Used as `mcv1`. No undata/unicef/IM_MCV1 or undata/sdg MCV1 variable was returned by either search. |
| `get_variable_metadata` batch 1 (8 vars) | OK |
| `get_variable_metadata` batch 2 (8 vars) | OK |
| `get_variable_metadata` batch 3 (8 vars) | OK |

Note: the `get_observations` response format differs from the playbook (`data.columns/rows` + `entityMetadata` instead of `placeObservations/timeSeries`); the parser handled both. `date="range"` with `date_range_start="2015"`, `date_range_end="2024"` was accepted on every call — no `date="all"` fallback was needed. No call errored. The observation tool never returned lower/upper bounds for any variable.

## Observation calls (date=range 2015–2024)
Status OK for every call. "n" = observations returned; "—" = empty response (no rows in range).

| indicator_key | variable DCID | NGA | ETH | IND | BGD | BRA | primary facet(s) |
|---|---|---|---|---|---|---|---|
| dtp3 | undata/sdg/SH_ACS_DTP3 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | 3722936608695937273 (SDG) |
| mcv1 | undata/who/IMM_COV_SH.AGE--Y1__VACCINE--MCV1 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | 15881878718417744244 (WHO) |
| mcv2 | undata/sdg/SH_ACS_MCV2 | n=6, 2019–2024 | n=6, 2019–2024 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | 3722936608695937273 (SDG) |
| mcv2_who | undata/who/IMM_COV_MCV2_SH | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | 15881878718417744244 (WHO) |
| mcv2_unicef | undata/unicef/IM_MCV2.AGE--Y2__VACCINE--MCV2 | n=6, 2019–2024 | n=6, 2019–2024 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | 15005650441306304968 (UNICEF) |
| sba | undata/sdg/SH_STA_BRTC | n=4, 2017–2024 | n=2, 2016–2019 | n=2, 2016–2021 | n=6, 2016–2023 | n=10, 2015–2024 | 3722936608695937273 (SDG) |
| anc1 | undata/who/ANC_COVERAGE...V_GE1 | n=3, 2017–2021 | n=2, 2016–2019 (alt listed) | n=2, 2016–2021 (alt listed) | n=3, 2018–2022 (alt listed) | n=1, 2015 | 15881878718417744244 (WHO, P1Y) |
| anc4 | undata/who/ANC_COVERAGE...V_GE4 | n=1, 2024 (facet 8991758111213825275, P4Y; 3 alts) | n=2, 2016–2019 (facet 17474927233864888815, P6Y; 1 alt) | n=1, 2021 (facet 3562761713907965015, P5Y; 3 alts) | n=2, 2022–2023 (facet 15881878718417744244, P1Y; 5 alts) | n=9, 2015–2023 (facet 15881878718417744244, P1Y; 2 alts) | DIFFERS BY COUNTRY (see anomalies) |
| fp_mod | undata/sdg/SH_FPL_MTMM.AGE--Y15T49__SEX--F | n=4, 2016–2021 | n=7, 2015–2021 | n=2, 2015–2019 | n=3, 2017–2022 | — (empty) | 3722936608695937273 (SDG) |
| fp_mod_unicef | undata/unicef/MNCH_DEMAND_FP.AGE--Y15T49 | n=4, 2016–2021 | n=7, 2015–2021 | n=2, 2015–2019 | n=3, 2017–2022 | — (empty) | 15005650441306304968 (UNICEF) |
| fp_mod_who | undata/who/FP_UNPD_UHC.SEX--F | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | 15881878718417744244 (WHO) |
| anem_w | undata/sdg/SH_STA_ANEM.AGE--Y15T49__SEX--F | n=9, 2015–2023 | n=9, 2015–2023 | n=9, 2015–2023 | n=9, 2015–2023 | n=9, 2015–2023 | 3722936608695937273 (SDG) |
| anem_w_who | undata/who/ANE_PREV_SH.AGE--Y15T49__SEX--F | n=9, 2015–2023 | n=9, 2015–2023 | n=9, 2015–2023 | n=9, 2015–2023 | n=9, 2015–2023 | 15881878718417744244 (WHO) |
| stunt | undata/sdg/SH_STA_STNT.AGE--Y0T4 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | 5810115657342770571 (SDG) |
| wast | undata/sdg/SH_STA_WAST.AGE--Y0T4 | n=5, 2015–2021 | n=2, 2016–2019 | n=3, 2015–2020 | n=4, 2015–2022 | n=1, 2019 | 5810115657342770571 (SDG) |
| ovwt | undata/sdg/SN_STA_OVWGT.AGE--Y0T4 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | n=10, 2015–2024 | 5810115657342770571 (SDG) |
| lbw | undata/who/LBW_PREV | — (no data, no sourceMetadata) | — (no data) | n=6, 2015–2020 | n=6, 2015–2020 | n=6, 2015–2020 | 15881878718417744244 (WHO) |
| lbw_unicef | undata/unicef/NT_BW_LBW | — (no data) | — (no data) | n=6, 2015–2020 | n=6, 2015–2020 | n=6, 2015–2020 | 15005650441306304968 (UNICEF) |
| ebf | undata/unicef/NT_BF_EXBF | n=3, 2016–2024 (alt facet 676179467171518898 P1M listed) | n=2, 2016–2019 | n=3, 2015–2020 | n=3, 2018–2022 | n=1, 2019 | 15005650441306304968 (UNICEF) |
| ebf_who | undata/who/BFEED_EXCL_6M_SH | n=2, 2016–2018 | n=2, 2016–2019 | n=2, 2015–2017 | n=2, 2018–2019 | — (empty) | 15881878718417744244 (WHO) |
| ipv | undata/sdg/VC_VAW_MARR.AGE--Y15T49__SEX--F | n=1, 2023 | n=1, 2023 | n=1, 2023 | n=1, 2023 | n=1, 2023 | 3722936608695937273 (SDG) |
| ipv_unicef | undata/unicef/PT_F_PS-SX_V_PTNR_12MNTH.AGE--Y15T49__SEX--F | n=1, 2024 | n=1, 2016 | n=1, 2016 | n=1, 2015 | — (no data) | 15005650441306304968 (UNICEF) |
| chmar | undata/unicef/PT_MRD_U18.SEX--F | n=1, 2023 | n=1, 2023 | n=1, 2023 | n=1, 2023 | n=1, 2023 | 1896065916138908710 (UNICEF) |
| breg | undata/sdg/SG_REG_BRTH.AGE--Y0T4 | n=1, 2024 | n=1, 2016 | n=1, 2021 | — (empty in range) | n=1, 2015 | 3722936608695937273 (SDG) |

### Diagnostic calls (date="latest", NOT written to values CSV)
| Variable / place | Result |
|---|---|
| fp_mod (SDG) / BRA | latest = 2006, value 89.3 (explains empty 2015–2024 range) |
| fp_mod_unicef / BRA | latest = 2006, value 89.3 |
| ebf_who / BRA | latest = 2007, value 38.6 |
| breg (SDG) / BGD | latest = 2025, value 59.1 — outside the requested 2015–2024 window (a 2025 observation exists; not extracted) |

## Anomalies and caveats

1. **chmar (undata/unicef/PT_MRD_U18.SEX--F) resolves to a COUNT, not a proportion.** The variable name says "Proportion of persons married or in union before age 18 [Sex=Female]" but the facet unit is `undata/UNIT_MEASURE-COUNT` and the values are absolute numbers (NGA 23700000; ETH 19900000; IND 222400000; BGD 43400000; BRA 21900000; all dated 2023). These look like the number of women/girls married before 18 (stock), not a prevalence rate. Do not use as child-marriage prevalence without re-checking; a prevalence variable was not in the brief's DCID list.
2. **mcv2_who vs mcv2 (SDG) / mcv2_unicef:** WHO `IMM_COV_MCV2_SH` reports `0` for NGA and ETH in 2015–2018, whereas the SDG and UNICEF series simply have no observation before 2019 (MCV2 introduced into these national schedules in 2019). The WHO zeros are placeholders for "not in schedule", not measured coverage. Where both exist, SDG, WHO and UNICEF MCV2 values are identical (all WUENIC-based).
3. **anc4 primary facet differs between countries.** Seven WHO facets exist, distinguished only by `observationPeriod` (P1Y, P2Y, P3Y, P4Y, P5Y, P6Y, P7Y — i.e. survey recall/reference periods). The API chose P4Y (8991758111213825275) for NGA, P6Y (17474927233864888815) for ETH, P5Y (3562761713907965015) for IND and P1Y (15881878718417744244) for BGD and BRA. The non-primary facets are listed under `alternative_sources` in the values CSV; observations from alternative facets were NOT retrieved (would require `source_override`). anc1 has a P2Y alternative facet (6873154236026966246) for ETH, IND, BGD, also not retrieved.
4. **anc4 BRA values carry 8 decimals** (e.g. 90.96573386) and are annual 2015–2023, unlike the survey-point values for the other countries (modelled/administrative series). anc1 BRA has only one point (2015).
5. **Duplicate/near-duplicate concepts across sources:** anem_w (SDG) and anem_w_who are identical for all 45 points. fp_mod (SDG) and fp_mod_unicef are identical (survey points), whereas fp_mod_who (UNPD/UHC) is a modelled annual series (2015–2024) with different values (e.g. NGA 2021: 41.9 survey vs 41.8 modelled). lbw (WHO) is rounded to 1 decimal whereas lbw_unicef gives 4 decimals of the same estimate (IND 2015: 28.7 vs 28.6616). ebf (UNICEF) has 4 decimals vs ebf_who 2 decimals; ebf_who stops at 2019 and has an extra NGA 2018 point (25.17) that is absent from the UNICEF series, while the UNICEF series has NGA 2021 (34.3633) and 2024 (28.7778), IND 2020 (63.6885) and BGD 2022 (53.2855) that WHO lacks.
6. **Different reference years for the IPV pair:** ipv (SDG, VC_VAW_MARR) returns a single 2023 point for all 5 countries (WHO/UN modelled estimates), whereas ipv_unicef returns survey-year points (NGA 2024 = 9.2; ETH 2016 = 19.8; IND 2016 = 22.0; BGD 2015 = 28.8; BRA none). NGA 2023 SDG (19.6) vs NGA 2024 UNICEF survey (9.2) differ substantially — different sources/methods.
7. **lbw / lbw_unicef have no data for NGA and ETH** (metadata entity coverage lists only IND, BGD, BRA; empty responses had no `sourceMetadata` block). Coverage ends in 2020 for all three.
8. **Survey-year gaps:** sba, anc1, anc4, fp_mod, wast, ebf, breg, ipv_unicef are survey-based with 1–6 points per country in the window. breg BGD has nothing in 2015–2024 (latest is 2025). fp_mod BRA and ebf_who BRA have nothing after 2006/2007.
9. **Unit codes:** stunt/wast/ovwt facets report unit `undata/UNIT_MEASURE-PT_POP_M0T59` (percentage of population aged 0–59 months) rather than "Percent"; written verbatim to `unit`/`unit_note`.
10. **Entity typeOf:** India is typed `["Country","Place"]` while the others are `["Country"]` — cosmetic, but noted.
11. **sba NGA** values are 2017: 43, 2018: 43.3, 2022: 50.7, 2024: 45.7 (the 2022 point is higher than 2024; both as returned).
12. **mcv1 selection:** used the national WHO series `undata/who/IMM_COV_SH.AGE--Y1__VACCINE--MCV1`; no UNICEF (IM_MCV1) or SDG national MCV1 variable surfaced in either search. Values are identical in pattern to WUENIC.
13. Metadata `description` field was absent from all 24 variable responses (left empty). `observation_properties` was also absent from every variable (no multi-entity variables).

## Totals
- Metadata rows: 32 (24 variables; anc1 has 2 facets, anc4 has 7, ebf has 2, all others 1).
- Value rows: 645. Per indicator: dtp3 50, mcv1 50, mcv2 42, mcv2_who 50, mcv2_unicef 42, sba 24, anc1 11, anc4 15, fp_mod 16, fp_mod_unicef 16, fp_mod_who 50, anem_w 45, anem_w_who 45, stunt 50, wast 15, ovwt 50, lbw 18, lbw_unicef 18, ebf 12, ebf_who 8, ipv 5, ipv_unicef 4, chmar 5, breg 4.
- get_observations calls: 120 range calls (all OK) + 4 diagnostic latest calls.
