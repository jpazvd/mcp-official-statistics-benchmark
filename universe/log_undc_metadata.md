# Log: UN System Data Commons variable metadata pull (UNICEF indicators)

Date: 2026-10-26
Tool: `UN_System_Data_Commons` MCP server, `get_variable_metadata`
Playbook read first: `skill://data-commons-researcher/SKILL.md`
Input: `/home/claude/universe/rep_dcids.json` (247 DCIDs, all unique, all prefixed `undata/unicef/`)
Entities on every call: `country/NGA, country/IND, country/BRA, country/BGD, country/ETH`
Output: `/home/claude/universe/undc_unicef_metadata.csv`

## Calls made

| # | Batch size | DCIDs | Result |
|---|-----------|-------|--------|
| 0 | 20 | rep_dcids[0:20] | FAILED, HTTP 400: `{"code":3,"message":"variable_dcids cannot exceed 10"}` |
| 1-24 | 10 | rep_dcids[0:240] in order | SUCCESS |
| 25 | 7 | rep_dcids[240:247] | SUCCESS |

- Total calls: 26 (1 failed + 25 successful). The planned 20-per-call plan (13 calls) was not possible: the server enforces a hard limit of 10 `variable_dcids` per call, so the fallback of 10 per call was used from the start (25 calls instead of 13). No further retries were needed; every 10-DCID call returned `status: SUCCESS`.
- Every response contained exactly the requested DCIDs under `variables` (no extra, no missing) and a single provenance entry.
- Each response was saved verbatim to the scratchpad (`resp_01.json` to `resp_25.json`) and parsed with a Python/csv script into the CSV; no values were typed by hand.

## Output summary

- Rows written: 260 (one row per variable x facet; 244 facet rows + 16 rows for variables returned with no facets).
- Variables requested: 247. Found (metadata returned with a `name`): 247. Not found: 0. No `(not found)` rows were needed.
- Variables with empty `description`: 247 of 247. The server returned no `description` field for any UNICEF variable; the only text is `name` and the variable `properties` (populationType, statType, measuredProperty, constraintProperties and the `undata*` constraint values), which are stored in `extra_json`.
- Variables with more than one facet: 13 (all nutrition, `NT_*`): NT_ANT_HAZ_NE2, NT_ANT_WAZ_NE2, NT_ANT_WHZ_NE2, NT_ANT_WHZ_NE3, NT_ANT_WHZ_PO2, NT_BF_CBF, NT_BF_EBF, NT_BF_EXBF, NT_BF_MIXMF, NT_CF_ISSSF_FL.AGE--M6T8, NT_CF_MMF, NT_IOD_ANY_TH, NT_IOD_ANY_TS. In each case the second facet is `676179467171518898` with `observationPeriod = P1M` and month-level date ranges (e.g. `2005-06` to `2019-03`), covering only a subset of the five countries (NGA/BGD, sometimes IND).
- Variables returned with a name but zero facets for the five entities (16): ECD_CHLD_LMPSL_PRXY.AGE--M36T47, ECON_ODA_OUTFLOW_PTGNI, ECON_ODA_OUTFLOW_USD, HVA_PREV_CNDM_REG.AGE--Y15T19, HVA_PREV_KNOW.AGE--Y15T19, HVA_PREV_STIGMA.AGE--Y15T19, HVA_PREV_TEST_RES.AGE--Y15T19, HVA_PREV_TEST_RES_12.AGE--Y15T19, IM_VACC.AGE--Y2__VACCINE--RCV1, IM_YFV.AGE--Y2__VACCINE--YFV, MG_UNRWA_RFGS_CNTRY_ASYLM, MNCH_CSEC_TND, MNCH_INSTDEL_TND, MNCH_ITNPREG.AGE--Y15T19, PT_CHLD_RES_CARE.AGE--Y0T16, WS_HCF_C.WASH_SERVICE--CS_B__WASH_SERVICE_TYPE--CLEAN. These rows have `variable_name` filled and all facet columns empty (the variable exists in the graph but has no observations for NGA/IND/BRA/BGD/ETH).

## Provenance and facets

- Provenance is identical for all 244 facet rows: `provenance_id = undata/p/UNICEF`, `source = "United Nations"`, `url = https://data.unicef.org/`, plus `domain = www.un.org` and `isPartOf = "United Nations Statistics Division"` (the last two are kept in `extra_json.provenance`). No provenance other than data.unicef.org appeared.
- Facet properties returned: only `unit` and `observationPeriod`. No facet carried `measurementMethod`, so that column is empty throughout.
- 22 distinct facet ids; `15005650441306304968` (unit Percent, P1Y) accounts for 178 of 244 facet rows.
- `observation_period`: P1Y on 231 rows, P1M on 13 rows.
- `obs_count` ranges from 1 to 130 (130 = 5 countries x 26 years, 2000-2025).
- Entity coverage: 121 facet rows cover all 5 countries, 46 cover 4, 16 cover 3, 43 cover 2, 18 cover 1.

## Oddities worth knowing (all written exactly as returned)

- Units are codes, not labels, except `Percent`. Several look wrong at source: `MNCH_LIFE_EXPECTANCY.SEX--F` unit `UNIT_MEASURE-COUNT`; `PT_MRD_U18.SEX--F` ("Proportion of persons married...") unit `UNIT_MEASURE-COUNT`; `GN_IDX` (SIGI index), `PV_CHLD_DPRV_AVG_*` (average number of deprivations) and `PV_VMIR`-type ratios partly labelled `Percent`. One unit code is truncated: `undata/UNIT_MEASURE-RATIO_COUNT_PER_1000_COUNT_` (MG_RFGS_CNTRY_ASYLM_PER1000).
- Names carry typos from the source: "Assitance" (ECON_ODA_*), "coninued breastfeeding" (NT_BF_CBF), "sever wasting" (NT_ANT_WHZ_NE3), "populationthat" (GN_ED_ATTN), "anitretrovirals" (HVA_PMTCT_ARV_NUM), "ITPp" (MNCH_IPTP), "children under left alone" (ECD_CHLD_LFT_ALN).
- `MNCH_CSEC` is named "...cesarean section (trends)" while `MNCH_CSEC_TND` is named "...cesarean section" (the "(trends)" suffix appears on the non-TND code).
- Several HVA_PREV_* names say "(aged 15-24 years)" or "(aged 15-49 years)" while the DCID constraint is Age = 15 to 19.
- `constraintProperties` is a string when there is one constraint and a list when there are several; preserved as returned inside `extra_json.variable.properties`.
