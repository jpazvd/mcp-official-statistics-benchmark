# MCP cost measurement — call count and response size

Date: 2026-10-27. Questions: (Q1) under-five mortality rate, Nigeria, all available years; (Q2) DTP3 immunization coverage, Nigeria, all years.
Scope: calls and sizes only; no analysis of the data. Raw responses in `raw/` (file names prefixed A–D by platform and step). Per-call detail in `calls.csv`; `chars` = `wc -c` of the saved raw file.

## Summary

| Platform | Q1 calls | Q1 chars | Q1 obs | Q2 calls | Q2 chars | Q2 obs | Errors |
|---|---|---|---|---|---|---|---|
| A. UN System Data Commons | 3 (incl. mandatory resource read) | 20,459 (8,462 excl. resource) | 25 (2000–2024) | 2 | 21,949 | 25 (2000–2024) | none |
| B. World Bank Data360 | 2 | 15,201 | 61 (1964–2024) | 3 (1 error + retry) | 10,190 | 41 (1984–2024) | search "DTP3 immunization" → 0 hits |
| C. IHME GBD | 1 | 15,253 | 34 (1990–2023) | 1 | 16,532 | 44 (1980–2023) | none |
| D. UNICEF SDMX MCP (Yves) | 5 as prescribed (1 error + retry; step 4 redundant) | 13,665 | 25 (2000–2024) | 2 | 7,350 | 26 (2000–2025) | 5-segment key rejected (flow has 4 dims) |

Minimal paths on D once the dimension rule is known: Q1 = find_indicator_candidates + list_dimensions + query_data = 3 calls / 10,942 chars; or find_indicator_candidates + get_time_series = 2 calls / 8,811 chars (get_time_series builds the key itself).

Setup not counted above: one ToolSearch to load the 10 tool schemas (result not persisted; roughly 17k chars of schema text, the two IHME tool descriptions being the largest at ~2.5k each) plus a second ToolSearch to load `ReadMcpResourceTool`, which was also deferred.

## Per-platform notes (what a first-time agent needs to know)

### A. UN System Data Commons
- The server instructions require reading `skill://data-commons-researcher/SKILL.md` before any tool call: 11,997 chars, paid once per session. The playbook also says to call `get_variable_metadata` between search and retrieval (not done here, so the "minimal" sequence is one call shorter than the playbook prescribes).
- `search_indicators` for U5MR did **not** return a `undata/unicef/*` DCID. The top-10 `variables` list was entirely WHO wealth-decile disaggregations (`undata/who/MORT_U5_RATE.WEALTH_QUANTILE--*`); the total U5MR (`undata/sdg/SH_DYN_MORT.AGE--Y0T4`) appeared only inside `topics[].memberVariables`. An agent that reads only the `variables` array would pick a decile series.
- Search payloads are large relative to the data: 7,085 chars (U5MR) and 20,749 chars (DTP3) of candidate lists versus 1,377 / 1,200 chars for the actual 25-year series. The DTP3 search returned 58 DCID name mappings, mostly WHO zero-dose and wealth-decile variants. Search is 84–95% of the per-question cost.
- `get_observations(date="all")` returned 25 annual points, point estimates only: no bounds, no obs status, no footnotes, no vintage. Source is a provenance URL + numeric sourceId (no source name string). Unit is a Data Commons code (`undata/UNIT_MEASURE-RATIO_COUNT_PER_1000_COUNT_LIVEBIRTHS`). Values are full precision (matches UN IGME).
- The UNICEF DTP3 DCID was returned for Q2 and carries `provenanceUrl: https://data.unicef.org/`, unit `Percent`. Values correspond to the WUENIC 2024 revision (differ from platform D's 2025 revision in several years); no vintage field says so.
- Observations are compact: ~50 chars each.

### B. World Bank Data360
- `data360_search_indicators` with `query="DTP3 immunization"` returned 0 results (error text: `No indicators found for: 'DTP3 immunization'`). Retry with the WDI spelling `"DPT immunization"` returned 48 hits with `WB_WDI_SH_IMM_IDPT` first and `WB_HCP_VACDTP3` third. The server's vocabulary is WDI naming, not WHO/UNICEF naming.
- `data360_get_data` defaults to the **last 5 years** and 50 records; "all years" requires explicit `start_year`/`end_year` (from `time_period_range` in the search hit) and `limit=100`. The U5MR series is 61 rows, so a default call would have needed pagination.
- Every `get_data` response carries a `failed_validation` warning that `ref_area_filter=member_economies_only` is ignored when `country_code` is set — noise on every call.
- Data rows are verbose: ~210 chars per observation (REF_AREA, REF_AREA_NAME, UNIT_MEASURE, UNIT_MEASURE_NAME, UNIT_MULT, claim_id repeated on each row). `definition_short` is `null` in the data response; the search response gives a definition truncated at 100 characters. The original source (UN IGME, WUENIC) is never named — only the database (WDI/HCP). No bounds, status flags, footnotes or vintage.
- Values are rounded to 1 decimal (U5MR) / integers (DTP3). U5MR series extends back to 1964; DTP3 to 1984.

### C. IHME GBD
- One call per question; no discovery step needed because the tools are indicator-specific (`get_child_mortality_trend`) or accept aliases (`get_covariate("DTP3 coverage")` resolved directly to covariate 2431; the planned second attempt with "DTP3 coverage (proportion)" was not needed).
- `language` is a required parameter on every IHME tool (passed `"en"`). `end_year` is capped at 2023 (GBD 2023 round); the U5MR default range is 1990–2023; covariates run from 1980.
- The result is JSON serialised inside a `"result"` string (double-encoded), so it needs a second parse.
- Richest metadata of the four: 95% uncertainty intervals on every value (male/female/combined for U5MR), a citation, a definition for the covariate, unit (for the covariate only; U5MR unit lives in the tool description, not the response), and a `covariate_framing` note that GBD covariates are modelled estimates, not WHO/UNICEF official statistics.
- That richness is expensive: ~450 chars per U5MR row (9 values) and ~290 chars per covariate row (covariate name, location, unit repeated on every row), plus ~2.5k chars of fixed reporting/rounding/interval/presentation guardrail text appended to every response regardless of size. Per question this is the most characters of any platform except UN DC's DTP3 search.
- Rows are rounded to GBD publication precision; `fmt='csv'` gives full precision (not tested here). IHME U5MR is a different estimate series from UN IGME (not comparable — not analysed).

### D. UNICEF SDMX MCP (Yves)
- `find_indicator_candidates` is the right entry point: it returns the indicator code, a definition, the unit, and a `recommendedFlowRef` in one call (6,220 chars for 10 U5MR candidates; 2,823 chars for 4 DTP3 candidates).
- `query_data` requires the key to have exactly as many segments as the flow has dimensions. The prescribed 5-segment key `NGA.CME_MRY0T4._T._T._T` was rejected: `Key has too many segments (5). Expected 4 for dimensions: REF_AREA, INDICATOR, SEX, WEALTH_QUINTILE`. The error message itself gives the dimension order, so an agent can recover without `list_dimensions`. `list_dimensions` is cheap (932 chars) but only needed if the agent wants the order before the first attempt.
- For IMMUNISATION/1.0 the short key `NGA.IM_DTP3.` (3 segments) was accepted and auto-padded to `NGA.IM_DTP3..` (4 dims: REF_AREA.INDICATOR.VACCINE.AGE). So too few segments pad; too many fail. This asymmetry is worth documenting.
- `query_data` returns the raw SDMX CSV plus a provenance block (resolved flow, key, dimensionOrder, reproducible `queryURL`, scope policy). CME rows carry `DATA_SOURCE=UN_IGME`, `LOWER_BOUND`/`UPPER_BOUND`, `OBS_STATUS=A`, full precision, ~100 chars per observation including bounds. IMMUNISATION rows carry `DATA_SOURCE="WHO/UNICEF estimates of national immunization coverage, 2025 revision"` (the only platform that states the vintage), `OBS_STATUS=E`, no bounds, and footnote columns (`SERIES_FOOTNOTE`, `OBS_FOOTNOTE`, `SOURCE_LINK`, `COUNTRY_NOTES`) present but empty for these series.
- `get_time_series` has no `key` argument; it takes `location`, `subject`, `filters`, `time`. It accepted the equivalent request without error and built the 4-segment key itself, so it does not need `list_dimensions`. Its compact output (2,591 chars, ~70 chars per observation) drops bounds, status and data source unless `verbose=true`.
- `query_data` enforces a bounded time window (`allowUnboundedTime=false` by default); 2000–2025 was accepted. True "all years" would need `allowUnboundedTime=true` or a wide window; CME data before 2000 was not requested here, so the 25-observation count is a window artefact, not the flow's full extent.
- D returned the 2025 WUENIC revision for DTP3 (2000–2025, 26 points); A and B returned the 2024 revision (2000/1984–2024). Several year values differ between revisions. Not analysed; noted because only D exposes the vintage.

## Metadata coverage at the data-retrieval step (from calls.csv)

| | Definition | Source | Unit | Bounds | Obs status | Footnotes | Vintage |
|---|---|---|---|---|---|---|---|
| A UN DC get_observations | name only | URL + id | code | no | no | no | no |
| B D360 get_data | null (truncated in search) | database only | yes | no | no | no | no |
| C IHME trend / covariate | no / yes | citation | no / yes | yes | no | fixed guardrail text | GBD round only |
| D Yves query_data | code only (in find step) | DATA_SOURCE + queryURL | code | yes (CME) / no (IMM) | yes | columns present, empty | yes (IMM only) |
| D Yves get_time_series | name only | flow/key/URL | label | no | no | no | no |

## Deviations from the prescribed sequence
- B step 3 errored and was retried once with `"DPT immunization"` (recorded as 3 and 3b).
- C step 2 succeeded on the first covariate name; no second attempt made.
- D step 3 errored and was retried once with the 4-segment key (recorded as 3 and 3b). D step 4 used `location`/`subject`/`filters` because `get_time_series` has no `key` parameter.
- Two ToolSearch calls were needed instead of one (`ReadMcpResourceTool` was deferred separately).
- Raw results were written with the Write tool from the inline tool output; the harness only persists results above roughly 75k chars to `tool-results/`, and none of these calls crossed that threshold. JSON validity and observation counts of every saved file were verified programmatically (all parse; counts in `calls.csv` match).
