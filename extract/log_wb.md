# World Bank Data360 extraction log

Run date: 2026-10-25. Countries: NGA, ETH, IND, BGD, BRA. Observation window requested: 2015-2024 (limit=100 per page; all calls returned has_more=false, total_count=null, so a single page sufficed unless noted).
Note on get_data responses: every call with country_code set returned the advisory `failed_validation: ref_area_filter=member_economies_only applies only when REF_AREA is unpinned ... filter was not applied` -- harmless, data returned normally.
Note on metadata: Data360 returns `date_last_update`/`date_released` as null for all indicators; the `version_statement.version_date` was used as `last_updated` in metadata_wb.csv.

## Indicator ID discovery
- lbw: `data360_search_indicators(query="low-birthweight babies", required_country="NGA;IND", limit=5)` -> 0 results ("No indicators found"). Fallback `query="birth weight", database="wdi; hnp"` -> found WB_HNP_SH_STA_BRTW_ZS (HNP, 1960-2023, covers NGA and IND) and WB_WDI_SH_STA_BRTW_ZS (WDI, 2000-2020, covers IND but NOT NGA). Both named "Low-birthweight babies (% of births)", code SH.STA.BRTW.ZS. Headline `lbw` = HNP version (wider coverage); WDI version recorded as `lbw_wdi`.
- pop_u5: `data360_search_indicators(query="population ages 0-4", database="hnp; wdi", required_country="NGA;IND", limit=6)` returned only 0-14 totals and 0-4 SHARES by sex (WB_WDI_SP_POP_0004_FE_5Y, WB_WDI_SP_POP_0004_MA_5Y). Further searches in HNP found WB_HNP_SP_POP_5Y "Population, age group" (dimensions SEX, AGE) -- `data360_get_disaggregation` on it timed out twice; a test get_data call (NGA;IND, 2023) returned only SEX=F and SEX=M rows for AGE=Y0T4 (no both-sexes total), and the search flagged covers_country NGA/IND = false for the HNP population series. No both-sexes 0-4 total count exists in WDI/HNP via this server -> pop_u5 SKIPPED (logged; sex-specific counts not extracted since the task asked for a total).

## Metadata calls (STEP A) -- all succeeded, 32 rows written to metadata_wb.csv
All 32 `data360_get_metadata` calls succeeded (fetch_disaggregation=false except for the two UNICEF_DW indicators, where disaggregation options were fetched: REF_AREA, SEX [F, M, _T], AGE [Y0T4], UNIT_MEASURE [PT], COMP_BREAKDOWN_1 [UNICEF_DW_CLUSTER_1/2/3], TIME_PERIOD 1983-2022, REGION). The first call (u5mr) was made without select_fields to enumerate available fields; subsequent calls used select_fields for the ~25 useful fields. Fields present in the full payload but not requested later: csv_link, json_link, api_link, api_explorer_link, links, api_documentation, ref_country (217 economies), geographic_units (48 aggregates), confidentiality_status, related_indicators, aliases, languages, definition_references, methodology_references.

| key | database | indicator id | time_period_range (metadata) | version_date |
|---|---|---|---|---|
| u5mr | WB_WDI | WB_WDI_SH_DYN_MORT | 1960-2024 | 2026-07-01 |
| nmr | WB_WDI | WB_WDI_SH_DYN_NMRT | 1960-2024 | 2026-07-01 |
| imr | WB_WDI | WB_WDI_SP_DYN_IMRT_IN | 1960-2024 | 2026-07-01 |
| mmr | WB_WDI | WB_WDI_SH_STA_MMRT | 1985-2023 | 2026-07-01 |
| mmr_national | WB_WDI | WB_WDI_SH_STA_MMRT_NE | 1985-2023 | 2025-06-05 |
| sbr | WB_HNP | WB_HNP_SH_DYN_STLB | 1960-2023 | 2024-09-23 |
| tfr | WB_WDI | WB_WDI_SP_DYN_TFRT_IN | 1960-2024 | 2026-07-01 |
| abr | WB_WDI | WB_WDI_SP_ADO_TFRT | 1960-2024 | 2026-07-01 |
| le0 | WB_WDI | WB_WDI_SP_DYN_LE00_IN | 1960-2024 | 2026-07-01 |
| dtp3 | WB_WDI | WB_WDI_SH_IMM_IDPT | 1980-2024 | 2026-07-01 |
| mcv1 | WB_WDI | WB_WDI_SH_IMM_MEAS | 1980-2024 | 2026-07-01 |
| mcv2 | WB_HNP | WB_HNP_SH_IMM_MEA2 | 1960-2023 | 2024-09-23 |
| sba | WB_WDI | WB_WDI_SH_STA_BRTC_ZS | 1980-2022 | 2026-07-01 |
| anc1 | WB_WDI | WB_WDI_SH_STA_ANVC_ZS | 1984-2021 | 2026-07-01 |
| anc4 | WB_HNP | WB_HNP_SH_STA_ANV4_ZS | 1960-2023 | 2024-09-23 |
| fp_mod | WB_HCP | WB_HCP_MNCH_DEMAND_FP | 1990-2024 | 2026-10-14 (version 2) |
| cpr_mod | WB_WDI | WB_WDI_SP_DYN_CONM_ZS | 1961-2024 | 2026-07-01 |
| cpr_mod_allwomen | WB_HNP | WB_HNP_SP_DYN_CONM_AL_ZS | 1960-2023 | 2024-09-23 |
| anem_w | WB_WDI | WB_WDI_SH_ANM_ALLW_ZS | 2000-2023 | 2026-07-01 |
| stunt | WB_WDI | WB_WDI_SH_STA_STNT_ME_ZS | 2000-2024 | 2026-07-01 |
| stunt_survey | WB_WDI | WB_WDI_SH_STA_STNT_ZS | 1983-2024 | 2026-04-08 |
| stunt_unicefdw | UNICEF_DW | UNICEF_DW_NT_ANT_HAZ_NE2 | 1983-2022 | 2024-10-02 |
| wast | WB_WDI | WB_WDI_SH_STA_WAST_ZS | 1983-2024 | 2026-04-08 |
| wast_unicefdw | UNICEF_DW | UNICEF_DW_NT_ANT_WHZ_NE2 | 1983-2022 | 2024-10-02 |
| ovwt | WB_WDI | WB_WDI_SH_STA_OWGH_ME_ZS | 2000-2024 | 2026-07-01 |
| ovwt_survey | WB_WDI | WB_WDI_SH_STA_OWGH_ZS | 1983-2024 | 2026-04-08 |
| ebf | WB_WDI | WB_WDI_SH_STA_BFED_ZS | 1986-2020 | 2026-07-01 |
| ipv | WB_WDI | WB_WDI_SG_VAW_1549_ZS | 2000-2017 | 2020-02-28 |
| chmar | WB_WDI | WB_WDI_SP_M18_2024_FE_ZS | 1985-2023 | 2026-07-01 |
| breg | WB_WDI | WB_WDI_SP_REG_BRTH_ZS | 2000-2022 | 2026-07-01 |
| lbw | WB_HNP | WB_HNP_SH_STA_BRTW_ZS | 1960-2023 | 2024-09-23 |
| lbw_wdi | WB_WDI | WB_WDI_SH_STA_BRTW_ZS | 2000-2020 | 2026-07-01 |

Metadata anomalies:
- `WB_WDI_SH_STA_MMRT_NE`, `WB_WDI_SH_STA_ANVC_ZS`, `WB_WDI_SP_DYN_CONM_ZS`, `WB_WDI_SP_REG_BRTH_ZS`: measurement_unit is null in metadata (unit written as empty; get_data records carry UNIT_MEASURE codes instead).
- `WB_HNP_SH_DYN_STLB` (stillbirth rate): name says "per 1,000 total births" but measurement_unit says "Per 1,000 live births" and get_data UNIT_MEASURE_NAME is "Per 1,000 live births" -- internal inconsistency in the HNP metadata; definition confirms the denominator is total births.
- `WB_WDI_SG_VAW_1549_ZS` (ipv): unit field says "ages 15 years and older" while the name/definition say ages 15-49; version_date 2020-02-28 (stale series, metadata time range ends 2017).
- `WB_HCP_MNCH_DEMAND_FP` (fp_mod): definition_long says "married women"; name says "women aged 15-49"; sources_note = "Youth" (HCP theme tag, not a real source note); methodology/limitation null; source listed as WDI series SH.FPL.SATM.ZS.
- `WB_WDI_SP_DYN_LE00_IN` alternate identifier is mislabelled "Male Life Expectancy at Birth (years)" though the series is total.
- `WB_WDI_SP_DYN_TFRT_IN` authoring_entity URI includes an unrelated Eurostat earnings URL (earn_ses_monthly).
- HNP-licensed series (sbr, mcv2, anc4, cpr_mod_allwomen, lbw) carry the CC BY 4.0 licence with the World Bank's mandatory arbitration addendum; UNICEF_DW series are CC BY-NC 3.0 IGO (non-commercial), WDI series plain CC BY-4.0.
- WDI `stunt_survey`, `wast`, `ovwt_survey` metadata time range runs to 2024 but only survey years are populated; `wast` limitation note says only latest estimates are provided, yet multiple years were returned.

## Observation calls (STEP B) -- 32 get_data calls, all status OK, single page each (has_more=false), 1000 rows written to values_wb.csv
Per-country coverage: B=BGD, R=BRA, E=ETH, I=IND, N=NGA. "null" rows are records where the API returned OBS_VALUE as the literal string "null" (kept verbatim in the value column; they are NOT counted as observations below).

| key | rows written | non-null | years (non-null) | latest non-null year | notes |
|---|---|---|---|---|---|
| u5mr | 50 | 50 | 2015-2024 | 2024 | all 5 countries x 10 years |
| nmr | 50 | 50 | 2015-2024 | 2024 | complete |
| imr | 50 | 50 | 2015-2024 | 2024 | complete |
| mmr | 45 | 45 | 2015-2023 | 2023 | complete to 2023 (series ends 2023) |
| mmr_national | 15 | 15 | 2015-2022 | 2022 | sparse: BRA 8 yrs (2015-22), BGD 5 (2015-20), IND 2015 only, NGA 2018 only, ETH none. Values differ sharply from modelled mmr (e.g. NGA 2018: 512 national vs 1118 modelled; IND 2015: 130 vs 129; BGD 2020: 163 vs 152). BGD 2015 value 195.862 has 3 decimals while others are integers/1dp |
| sbr | 45 | 35 | 2015-2021 | 2021 | 2022 and 2023 rows returned as "null" for all 5 countries |
| tfr | 50 | 50 | 2015-2024 | 2024 | complete |
| abr | 50 | 50 | 2015-2024 | 2024 | complete |
| le0 | 50 | 50 | 2015-2024 | 2024 | complete; note sharp 2021 dips (IND 67.282, BGD 71.103) consistent with WPP COVID revisions |
| dtp3 | 50 | 50 | 2015-2024 | 2024 | complete |
| mcv1 | 50 | 50 | 2015-2024 | 2024 | complete |
| mcv2 | 45 | 32 | 2015-2022 | 2022 | 2023 "null" for all; ETH and NGA "null" 2015-2018 (NGA MCV2 introduced 2019: value 9) |
| sba | 17 | 17 | 2015-2022 | 2022 | survey years only: NGA 2017/18/22, IND 2016/21, BRA 2015-20 annual, BGD 2016-19, ETH 2016/19 |
| anc1 | 10 | 10 | 2015-2021 | 2021 | survey years only; BRA only 2015 |
| anc4 | 45 | 13 | 2015-2021 | 2021 | 32 "null" rows; non-null: BRA 2015-19 annual, BGD 2018/19, ETH 2016/19, IND 2016/21, NGA 2017/18 |
| fp_mod | 7 | 7 | 2016-2024 | 2024 | HCP series; NGA 2018/2024, BGD 2018/22, IND 2016/21, ETH 2016; BRA none. HCP is a re-publication of WDI SH.FPL.SATM.ZS |
| cpr_mod | 17 | 17 | 2015-2022 | 2022 | BRA none; ETH annual 2015-21 (mix of 1dp and 6dp values, e.g. 34.618115 vs 35.6, suggesting mixed sources: PMA/DHS); NGA 2016-18, 2021; BGD 2016/18/19/22; IND 2016/21 |
| cpr_mod_allwomen | 45 | 11 | 2015-2021 | 2021 | HNP all-women version: 34 "null" rows; non-null BRA 2019 only (79.5), ETH 2015-19, IND 2016/21, NGA 2016-18. Differs from married-women cpr_mod by construction (e.g. IND 2021: 42.7 all women vs 56.4 married) |
| anem_w | 45 | 45 | 2015-2023 | 2023 | complete to 2023 |
| stunt | 50 | 50 | 2015-2024 | 2024 | JME modelled, complete |
| stunt_survey | 15 | 15 | 2015-2022 | 2022 | WDI survey-based; BGD 2015/18/19/22, NGA 2015/16/18/20/21, IND 2015/17/20, ETH 2016/19, BRA 2019 |
| stunt_unicefdw | 15 | 15 | 2015-2020 | 2020 | filter SEX=_T applied (log: disaggregation_filters={"SEX":"_T"}); rows also carry AGE=Y0T4 and COMP_BREAKDOWN_1 (UNICEF_DW_CLUSTER_1 or _2). Two surveys in same year for BGD 2019 (26.2 cluster_1 / 28 cluster_2) and NGA 2018 (33.1 / 36.8) -- both kept. Values match WDI survey series where years overlap except: BGD 2015 (32.7 DW vs 35 WDI), BGD 2019 (WDI shows 28 = cluster_2), NGA 2018 (WDI 36.8 = cluster_2), IND 2017 (34.7 DW vs 36.1 WDI), BRA 2019 (7.2 DW vs 8 WDI). Series footnote: JME Expanded Databases May 2023, coverage 1989-2020 (older vintage than WDI 2026) |
| wast | 15 | 15 | 2015-2022 | 2022 | survey-based; same survey years as stunt_survey |
| wast_unicefdw | 15 | 15 | 2015-2020 | 2020 | SEX=_T; duplicates in BGD 2019 (9.5/9.8) and NGA 2018 (6.8/6.8); differs from WDI for IND 2017 (17.3 vs 16.9), BRA 2019 (3.1 vs 3.4), BGD 2015 (15.6 vs 10) |
| ovwt | 50 | 50 | 2015-2024 | 2024 | JME modelled, complete |
| ovwt_survey | 15 | 15 | 2015-2022 | 2022 | survey-based |
| ebf | 8 | 8 | 2016-2019 | 2019 | BRA none; BGD 2018/19, ETH 2016/19, IND 2016/18, NGA 2017/18; values with 5 decimals (e.g. 62.60072) |
| ipv | 3 | 3 | 2015-2016 | 2016 | only BGD 2015, ETH 2016, IND 2016; BRA and NGA none (series stale, ends 2017 globally) |
| chmar | 7 | 7 | 2016-2024 | 2024 | BRA none; rows carry AGE=Y20T24 dimension; NGA 2024 (33.4), BGD 2022 (50.7), IND 2021 (22.3) |
| breg | 8 | 8 | 2015-2021 | 2021 | BRA 2015 only (96.4); ETH 2016 = 2.7; BGD 2018 (25.2) vs 2019 (56) jump (different surveys/definitions) |
| lbw | 45 | 18 | 2015-2020 | 2020 | HNP: 27 "null" rows (2021-2023 all countries; ETH and NGA all years). Non-null values identical to WDI series |
| lbw_wdi | 18 | 18 | 2015-2020 | 2020 | WDI: only BGD, BRA, IND returned (ETH, NGA absent, as the search flagged for NGA); values 6dp modelled estimates identical to HNP |

## Skipped / not extracted
- pop_u5: no both-sexes 0-4 total found (see discovery notes). Candidates seen: WB_WDI_SP_POP_0004_FE_5Y / _MA_5Y (shares by sex), WB_HNP_SP_POP_5Y (counts by SEX x AGE, but no SEX=_T total; `data360_get_disaggregation` timed out twice and search reported covers_country=false for NGA/IND). Not written to values_wb.csv.

## Cross-database differences worth noting
- WDI vs HNP versions of the same concept carry different vintages: WDI series are version 2026-07-01 (latest year 2024) while HNP series are version 2024-09-23 (latest year 2023) and return literal "null" placeholders for empty cells rather than omitting rows. HNP mcv2, anc4, cpr_mod_allwomen and lbw therefore contain many "null" rows.
- lbw: HNP and WDI values agree exactly where both exist; HNP adds ETH/NGA rows but all "null".
- JME modelled (stunt/ovwt ME series) vs survey-based (stunt_survey, wast, ovwt_survey) vs UNICEF_DW: the modelled series is annual and complete; survey series only in survey years; UNICEF_DW is an older JME vintage (May 2023) with cluster-level duplicates in some years and slightly different point estimates for a few surveys.
- Maternal mortality: modelled (MMEIG) vs national estimates diverge substantially (see mmr_national row).
