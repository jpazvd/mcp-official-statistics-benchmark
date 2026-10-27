# Data360 matching log — part 1 (123 UNICEF codes)

Method: data360_search_indicators with `queries` lists (8 phrases per call), required_country="NGA;IND;BRA", limit=5, result_layout="by_query"; then data360_get_metadata (fetch_disaggregation=false, select_fields=[source_organisation, definition, time_period_range, latest_data]) for every "same"/"related" candidate. Known UNICEF_DW mirrors (FD_STUNTING, FD_UNDERWEIGHT, GN_ED_ATTN in this part) recorded directly as UNICEF_DW_<code> and also searched for other-database counterparts.

## Search calls and phrasing

### Tool notes
- `data360_search_indicators`: 28 calls total (26 with `queries` lists of 2-8 phrases, required_country="NGA;IND;BRA", limit=5, by_query; 1 call without country filter for donor-side ODA; 2 calls with `database` filter "wdi" / "wdi; UNICEF_DW" to force-surface WDI/UNICEF_DW series that the semantic ranker buried). Search is semantic and returns empty for many exact phrasings (e.g. "population ages 0-14", "DTP3 immunization") while a looser phrase ("population share young ages", "polio immunization") surfaces them; alternative phrasings were tried as instructed (one or two per code).
- `data360_get_metadata`: 97 calls. The requested `select_fields` names (source_organisation, definition, time_period_range, latest_data) are NOT recognised (the tool returns only database_name). Real field names are `sources` (list of {name, organization, publisher, note, uri}), `authoring_entity`, `definition_long`, `time_periods`; `fetch_disaggregation=true` also returns dimension values and per-country REF_AREA coverage. All Step-B calls used `select_fields=["sources","authoring_entity","definition_long","time_periods"]`.
- d360_source column concatenates the `sources[].organization` / `name` text (plus authoring_entity when it names the custodian). unicef_sourced="yes" only when that text names UNICEF / UN Children's Fund / IGME / JME / WUENIC (WHO+UNICEF immunization) / State of the World's Children / Childinfo / UNICEF Data Warehouse / WHO-UNICEF JMP.

### Phrasing used per code (first phrase that produced the recorded candidate; "none" codes list all phrases tried)
- CME_ARR: "annual rate of reduction under-five mortality"; "annual rate of reduction mortality" -> none
- CME_ARR_SBR: covered by the same ARR phrases -> none
- CME_MR: "under-5 mortality rate", "neonatal mortality rate", "infant mortality rate", "probability of dying among children ages 5-9 years" (surfaced 5-9/10-14/15-19), "probability of dying youth" (surfaced 20-24, HNP SH_DYN)
- CME_PND: "neonatal deaths share of under-five deaths" -> none
- CME_SB, CME_SBR: "stillbirth rate"
- CME_TM: "number of under-5 deaths", "number of neonatal deaths", "mortality adolescents number of deaths" (surfaced 10-14/15-19 counts, HNP SH_DTH)
- DM_BRTS: "number of births", "live births total" -> none; "crude birth rate" recorded as related
- DM_BRTS_SURVIVING_1: "births surviving to age 1" -> none
- DM_BU_PC_DOU: "built-up area per capita", "built-up area" -> none
- DM_DPR_CHD / DM_DPR_OLD / DM_DPR_TOT: "child dependency ratio", "old age dependency ratio"
- DM_FRATE_TOT: "total fertility rate"; DM_LIFE_EXP: "life expectancy at birth"; DM_NET_MG_RATE: "net migration rate"
- DM_POP: "population total", "population under 15 percent of total", "young population share" (HNP SP_POP_5Y)
- DM_POP_DOU / DM_POP_DOU_GRT: "share of population by degree of urbanisation", "urban population growth annual" (national-definition series only)
- DM_POP_GRT: "population growth rate"; DM_POP_PROP: "population share young ages" (database=wdi) after 6 failed "population ages 0-14 ..." phrasings
- DM_POP_URBN / DM_POP_U_GRT: "urban population percent", "rural population share", "urban population growth annual"
- ECD_CHLD_ADLT_SRC: "early stimulation" (after "early stimulation responsive care adult engaged activities" and "early childhood development index four domains")
- ECD_CHLD_BKS_HM: "children with three or more books at home"; ECD_CHLD_EDU_PGM: "ECD programme attendance" (after "attendance early childhood education programme", "early childhood education attendance", "children attending early childhood education 36-59 months" all empty)
- ECD_CHLD_LFT_ALN: "children left with inadequate supervision", "inadequate supervision" -> none
- ECD_CHLD_LMPSL / _PRXY: "children developmentally on track"; ECD_CHLD_PLYTH_HM: "children who play with two or more types of playthings", "playthings" -> none
- ECON_GVT_EXP_PTEXP: "government expenditure on education" (database=wdi) for SE.XPD.TOTL.GB.ZS after 7 empty phrasings; "health spending share of government expenditure"; "social protection expenditure" (IMF GFS COFOG)
- ECON_GVT_EXP_PTGDP: "government expenditure on education percent of GDP", "expenditure on health percent of GDP"
- ECON_GVT_REV_PTGDP: "government revenue percent of GDP", "revenue excluding grants percent of GDP"
- ECON_ODA_INFLOW_*: "net ODA received percent of GNI", "net ODA provided by donor" (surfaced DT.ODA.ODAT.CD); ECON_ODA_OUTFLOW_*: "net ODA provided percent of GNI", "net ODA provided total current US dollars" (no country filter)
- ED_CR: "completion rate lower secondary both sexes" (UIS CR_1/2/3); ED_LR: "literacy rate youth"; ED_MAT/ED_READ: "minimum proficiency level mathematics/reading", "minimum proficiency mathematics/reading lower secondary", "below minimum reading proficiency"
- ED_ROFST / ED_ROFST_ADM / FD_OOS: "out of school primary percent", "secondary out of school percent", "out of school youth upper secondary"
- FD_ANAR: "net attendance rate primary", "total net attendance rate" ("adjusted net attendance rate" surfaced only the age-minus-one series)
- FD_EARLY_CH_EDU / FD_EARLY_STIM: reuse of ECD series; FD_FOUNDATIONAL_LEARNING: "learning poverty", "foundational reading skills children", "foundational numeracy skills children"
- FD_FUNC_DIFFICULTY: "children with disabilities functional difficulty", "disability prevalence children" -> none; FD_NEVER_ATTENDED: "children who never attended school" -> none
- FD_SANITATION_FACILITIES: "basic sanitation services"; FD_SEVER_PHY_PUNISH: "physical punishment children violent discipline" -> none; FD_SOCIAL_TRANSFERS: "social transfers household coverage"
- FD_STUNTING / FD_UNDERWEIGHT: known UNICEF_DW mirrors + "stunting prevalence children under 5", "underweight prevalence children under 5"
- GN_ED_ATTN: known UNICEF_DW mirror + "educational attainment upper secondary"; GN_FB_BNK_ACCSS: "account ownership financial institution"; GN_IDX: "social institutions and gender index", "SIGI gender discrimination social institutions", "SIGI", "women business and the law" (related only)
- GN_IT_MOB_OWN: "mobile phone ownership"; GN_LF_PTCPN: "labor force participation rate ages 15+"; GN_MTNTY_LV_BNFTS: "maternity leave paid"; GN_PTNTY_LV_BNFTS: "paternity leave"; GN_SG_LGL_GENEQEMP: "legal frameworks gender equality employment"; GN_TIMEUSE: "unpaid care work time use"; GN_UNMPLY: "unemployment rate", "unemployment ILO estimate"
- HVA_EPI_DTH_ANN: "HIV AIDS deaths children"; HVA_EPI_DTH_RT: no rate series -> none; HVA_EPI_INF_ANN: "children newly infected with HIV"; HVA_EPI_INF_RT: "HIV incidence"; HVA_EPI_LHIV: "children living with HIV" (HNP SH_HIV with AGE Y0T14)
- HVA_PED_ART_CVG: "antiretroviral therapy coverage children" (all-ages only); HVA_PED_ART_NUM, HVA_PED_EID_*: "early infant diagnosis HIV virological test" -> none; HVA_PED_LOST: "children orphaned" -> none (all-cause); HVA_PED_LOST_AIDS: same phrase -> SH_HIV_ORPH
- HVA_PMTCT_*: "antiretroviral therapy coverage for PMTCT pregnant women living with HIV", "PMTCT", "prevention of mother-to-child transmission antiretroviral", "mother-to-child HIV transmission", "pregnant women tested for HIV antenatal" -> none
- HVA_PREV_CNDM_MULT / _REG: "condom use"; HVA_PREV_KNOW: "young people with comprehensive correct knowledge of HIV"; HVA_PREV_KNOW_TEST / TEST_RES / TEST_RES_12: "HIV testing young people", "women who have ever been tested for HIV" -> none; HVA_PREV_STIGMA: "discriminatory attitudes HIV stigma" -> none
- IM_BCG: "BCG immunization"; IM_HEPBB: "hepatitis B birth dose vaccination"; IM_HPV: "HPV vaccine coverage girls"; IM_MCV2: "measles second dose immunization"; IM_PAB: "tetanus protection at birth" (after "newborns protected at birth against tetanus" empty); IM_VACC: "Hib3 immunization", "polio immunization", "measles first dose immunization", "pneumococcal conjugate vaccine third dose", "rotavirus vaccine last dose" ("DTP3 immunization", "DTP1 immunization first dose" returned empty but DTP series surfaced via other queries); IM_YFV: "yellow fever vaccine", "yellow fever" -> none
- MG_INTERNAL_DISP_PERS / MG_NEW_INTERNAL_DISP: "internally displaced persons", "displaced conflict total"; MG_INTNL_MG_CNTRY_DEST: "international migrant stock"; MG_RFGS_CNTRY_ASYLM / _ORIGIN: "refugee population"; MG_RFGS_*PER1000 / PER_USD_GNI: "refugees per 1000 population" -> none; MG_UNRWA_RFGS_CNTRY_ASYLM: none (WDI excludes UNRWA)
- MNCH_ABR: "adolescent birth rate"; MNCH_ADO_ALCOHOL: "alcohol use adolescents" -> none; MNCH_ADO_INSUFF_PHYS: "insufficient physical activity adolescents", "physical activity", "insufficiently physically active adolescents 11-17" -> none; MNCH_ADO_TOBACCO: "tobacco use adolescents" (adult series only; "tobacco use youth 13-15 years", "smoking prevalence youth 13-15" empty)
- MNCH_ANC1: "prenatal care one visit"; MNCH_ANC4: "antenatal care at least four visits"; MNCH_BIRTH18: "women who gave birth before age 18"; MNCH_CSEC / _TND: "cesarean section delivery", "caesarean", "births by caesarean section percent", "births delivered by caesarean section" -> none
- MNCH_DEMAND_FP: "family planning modern methods"; MNCH_DIARCARE / MNCH_DIARRHOEAT_TR: "diarrhea treatment"; MNCH_INFDEC: "women decision making reproductive health"; MNCH_INSTDEL / _TND: "cesarean section delivery" (surfaced WB_HCP_INSBIRTHS), "institutional births" empty
- MNCH_IPTP: "malaria prevention pregnant women"; MNCH_ITN: "bed nets children under 5"; MNCH_ITN2 / MNCH_ITNOWN: "insecticide treated nets households", "households with at least one insecticide-treated net", "indoor residual spraying", "percentage of households owning ITN" -> none; MNCH_ITNPREG: "pregnant women sleeping under bed nets"

### Ambiguities and judgement calls
1. HCP (WB_HCP_*) series frequently copy UNICEF indicators verbatim ("Name in source: ..." equals the UNICEF name) and cite data.unicef.org as source - recorded as same + unicef_sourced=yes (IM_BCG, IM_HEPBB, IM_HPV, IM_MCV2, IM_VACC antigens, MNCH_ANC4, MNCH_BIRTH18, MNCH_DIARCARE, MNCH_ITNPREG, HVA_PREV_KNOW).
2. EdStats "(De Facto)" series (WB_EDSTATS_SE_PRM_*) carry MICS-identical wording (early stimulation, 3+ books, ECE attendance, institutional delivery) but list only "World Bank Education Statistics" as source and cover only NGA among the three test countries; recorded as same with unicef_sourced=no because the metadata does not name UNICEF.
3. UNICEF_DW mirrors: FD_STUNTING / FD_UNDERWEIGHT exist in Data360 (AGE M24T59/M36T59) but cover ~40 countries, not NGA/IND/BRA; GN_ED_ATTN covers 179 incl. all three. The Data360 UNICEF_DW database also exposes the NT_ANT_* / NT_IOD_* codes listed as known mirrors (seen in search results) but those codes are outside part 1.
4. Mortality: CME_MR/CME_TM wealth-quintile and sex-by-age variants are not in Data360 except U5MR by sex; HNP dimensioned series (WB_HNP_SH_DYN, WB_HNP_SH_DTH, WB_HNP_SP_POP_5Y) report no NGA/IND/BRA coverage in the search tool.
5. ED_ROFST (survey-based, with wealth/urban dims) vs ED_ROFST_ADM (administrative): the UIS out-of-school series in Data360 are enrolment-based, so recorded as same for ED_ROFST_ADM and related for ED_ROFST.
6. FD_ANAR: Data360 has UIS total net attendance rates (NART), not adjusted NAR (ANAR); recorded as related.
7. Degree-of-urbanisation (DEGURBA) series (DM_*_DOU) have no Data360 counterpart; national-definition urban/rural series recorded as related.
8. GN_MTNTY/PTNTY_LV_BNFTS: UNICEF VALUE_CATEGORY codes VAL_08/VAL_09 could not be resolved from the input; WBL binary and length-in-days series recorded as related.
9. MNCH_BIRTH18 input lists AGE Y15T49 while the standard indicator uses women 20-24; the HCP copy (20-24) is recorded as same with a note.
10. MNCH_INFDEC input lists only the 15-19 band; WDI SG.DMK.SRCR.FN.ZS is 15-49, so recorded as related.
11. HVA_EPI_LHIV: WB_HNP_SH_HIV definition text says "percentage" but the unit is COUNT with AGE values _T / Y0T14 / Y_GE15; recorded as same for the Y0T14 variant.
12. ECON_GVT_EXP: health share uses WHO GHED domestic government health expenditure (excludes external funding), not strictly COFOG-07; recorded as same with a note. No single series for the combined COFOG 7+9+10 variant.
