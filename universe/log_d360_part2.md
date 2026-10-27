# Data360 matching log — part 2 (124 codes)

Tools: data360_search_indicators (queries list, required_country=NGA;IND;BRA, limit=5, by_query), data360_get_metadata (fetch_disaggregation=false, select_fields=[source_organisation,definition,time_period_range,latest_data]).

## Tool behaviour notes
- `data360_search_indicators`: long natural-language phrases (>7-8 words) frequently return "No indicators found"; short 2-4 word phrases work far better. Queries were re-run with shorter phrasing where the first attempt failed. `database` filter accepts semicolon lists but unknown IDs (ILO_SDG, ILO_ILOSTAT) abort the whole call.
- `data360_get_metadata` with `select_fields=["source_organisation","definition","time_period_range","latest_data"]` returns only `database_name` (those field names do not exist). Working field names: `authoring_entity`, `sources`, `definition_long`, `time_periods`. `latest_data` is taken from the search result instead. All "same"/"related" candidates had metadata fetched with the working field names.
- covers_NGA/IND/BRA taken from the search result `covers_country` object.

## Calls made
Search calls (each 8 queries unless noted, required_country=NGA;IND;BRA, limit=5, by_query): 21 calls (one with database filter "WB_HCP; WB_HNP; UNICEF_DW", one with "WHO_GHO", two aborted on bad database IDs and re-run, one with limit=8).
Metadata calls: 86 indicators (10 initial calls wasted on wrong select_fields names, then re-run).

## Phrasing used per code (first phrase -> alternative if needed)
- MNCH_LIFE_EXPECTANCY: "life expectancy at birth female"
- MNCH_LTR_MATERNAL_DEATH: "lifetime risk of maternal death"
- MNCH_MATERNAL_DEATHS: "number of maternal deaths"
- MNCH_MLRACT: "febrile children receiving artemisinin combination therapy ACT antimalarial" (none) -> "malaria treatment children under 5 antimalarial drugs" (none) -> "malaria diagnostic testing children" surfaced WB_HCP_MNCH_MLRACT
- MNCH_MLRCARE: "children with fever treatment sought health facility" (none) -> "fever children under 5 care seeking"
- MNCH_MLRDIAG: "children with fever malaria blood test finger heel stick" (none) -> "malaria diagnostic testing children"
- MNCH_MMR: "maternal mortality ratio per 100000 live births" (none) -> "maternal mortality ratio"
- MNCH_PNCMOM: "postnatal care mothers within 2 days of birth"
- MNCH_PNCNB: "postnatal care newborns within 2 days"
- MNCH_PNEUCARE: "acute respiratory infection children care seeking" (none) -> found via "fever children under 5 care seeking" (WB_HCP_U5_PNEU_CS, WB_WDI_SH_STA_ARIC_ZS)
- MNCH_SAB: "births attended by skilled health staff" (none!) -> "skilled birth attendance"
- MNCH_UHC: "UHC service coverage index"
- MNCH_UHC_RMNCH: "UHC sub-index reproductive maternal newborn child health"
- NT_ANE: "anemia prevalence women of reproductive age"
- NT_ANT_HAZ_NE2: "stunting prevalence children under 5"; NT_ANT_HAZ_NE2_MOD: "stunting modeled estimate"; NT_ANT_HAZ_NE2_MOD_NUMTH: "number of stunted children under 5" / "stunted children count" (no count series)
- NT_ANT_WAZ_NE2: "underweight prevalence children under 5"
- NT_ANT_WHZ_NE2: "wasting prevalence children under 5"; NT_ANT_WHZ_NE3: "severe wasting children under 5"
- NT_ANT_WHZ_PO2: "overweight prevalence children under 5"; _MOD: same + "overweight children count"; _MOD_NUMTH: "number of overweight children under 5" (no count series)
- NT_BF_CBF: "continued breastfeeding 12-23 months" / "continued breastfeeding" (none)
- NT_BF_EBF: "ever breastfed children" (EdStats de-facto series only, related)
- NT_BF_EIBF: "early initiation of breastfeeding within one hour" / "early initiation of breastfeeding" (none)
- NT_BF_EXBF: "exclusive breastfeeding under 6 months" (none) -> "exclusive breastfeeding"
- NT_BF_EXBF_2D: "exclusively breastfed first two days after birth" / "breastfeeding first days after birth" (none)
- NT_BF_MIXMF: "mixed milk feeding infants under 6 months" / "mixed milk feeding" (none)
- NT_BW_LBW: "low birthweight babies" (none) -> "low birthweight" (none) -> "birth weight" (HNP/HCP filter) and "children weighed at birth" surfaced WDI/HNP/HCP LBW series
- NT_BW_WEI: "children weighed at birth" / "infant weighed at birth" (none)
- NT_CF_ASF: "egg or flesh foods consumption children 6-23 months" / "egg flesh foods children" (none)
- NT_CF_FG_0_T_2, NT_CF_FG_3_T_4: "child food poverty" / "severe food poverty children" / "food poverty" (none relevant)
- NT_CF_ISSSF_FL: "introduction of solid semi-solid soft foods 6-8 months" / "solid semi-solid soft foods infants" (none)
- NT_CF_MAD: "minimum acceptable diet children 6-23 months" (none) -> "minimum acceptable diet" -> HNP IYCF all-3 series (same), EdStats MDD+MMF (related)
- NT_CF_MDD: "minimum dietary diversity children 6-23 months" (none) -> "minimum dietary diversity" / "dietary diversity" (only composite)
- NT_CF_MMF: "minimum meal frequency children 6-23 months" (none) -> "minimum meal frequency" (WB_HCP_MEALFREQ, UNICEF-sourced but 2023 only)
- NT_CF_ZEROFV: "zero vegetable fruit consumption" (none)
- NT_DANT_BMI_G25_MOD: "overweight adults BMI 25 or more"; G30_MOD_ADJ: "obesity adults BMI 30 or more age-standardized"; L18_MOD: "underweight adults BMI below 18.5" / "underweight adults" / WHO_GHO-filtered (none)
- NT_IOD_ANY_TH / TS: "iodized salt" (HCP/HNP/UNICEF_DW filter)
- NT_SANT_5_19_*: "thinness children adolescents 5-19 years BMI", "overweight children adolescents 5-19 years", "obesity children adolescents 5-19 years" + short variants + WHO_GHO filter (none; only under-5 BAZ series)
- NT_VAS_S1/S2/TWODOSE: "vitamin A supplementation"
- PT_ADLS_LBR_HC: "adolescents household chores" / "child labour household chores" (none)
- PT_ADLT_PS_NEC: "adults attitude physical punishment necessary raise children" / "physical punishment attitudes" (none)
- PT_CHLD_1-14_PS-PSY-V_CGVR_TND, PT_CHLD_PS_PSY_V_CGVR: "violent discipline children caregivers" (none relevant)
- PT_CHLD_DN: "children in detention rate" (none)
- PT_CHLD_LBR_ECON: "child labour economic activities ages 5-17" (none) -> "child labour" (WB_HCP_CHILD_LABOR); PT_CHLD_LBR_ECON_HC: "children engaged in child labour including household chores" (none)
- PT_CHLD_REG: "birth registration children under 5"
- PT_CHLD_RES_CARE: "children in residential care" (none)
- PT_CM_BANK: "women with account at financial institution ages 20-24" (none) -> "account ownership female" (Findex, related)
- PT_CM_BIRTHS18: "women who gave birth before age 18"; PT_CM_BIRTHS20: "adolescent fertility first birth before age 20"
- PT_CM_DEC_FAMILY: "women decision making visits to family"
- PT_CM_EMPLOY_12M: "women employed past 12 months" / "women employed in last 12 months" (none)
- PT_CM_IPV_12M: "intimate partner violence past 12 months" (none) -> "intimate partner violence"
- PT_CM_W_BTNG, PT_W_BTNG: "women who believe husband is justified in beating wife" (none) -> "wife beating justified"; male: "men who think wife beating is justified", "attitudes wife beating men" (women-only series)
- PT_FGM_ELIM: "attitudes towards female genital mutilation should end" (none) -> "attitudes female genital mutilation"
- PT_F_15-19_FGM_TND, PT_F_FGM: "female genital mutilation prevalence"
- PT_F_MRD_U15(_TND), PT_F_MRD_U18_TND, PT_MRD_U18: "child marriage before age 15", "child marriage before age 18", "women married by age 15 or 18"; male: "men married before age 18", "men who were first married by age 18" (none)
- PT_F_PS-SX_V_PTNR_12MNTH: "intimate partner violence"
- PT_F_TMRD15: "number of girls married before 15" (no count series)
- PT_MRD: "adolescents currently married or in union ages 15-19" / "currently married adolescents" (none)
- PT_NMRD: "adolescents never married" (none)
- PT_ST_BUL_30_DYS: "students bullied past 30 days" / "bullying students" (UIS 12-month series only, related)
- PT_SXV_AGE18: "sexual violence in childhood before age 18"; male: "men experienced sexual violence by age 18" (none)
- PV_ADOLESCENT: "adolescent poverty rate" (none)
- PV_CHLD_DEPRV_* / PV_CHLD_DPRV_* / SPP_CHLD_POV_PROF: "children multidimensional deprivation", "child deprivation", "child poverty", "poverty headcount children" (none)
- PV_CHLD_INCM_PL: "children living in households below national poverty line" (none) -> "child poverty national poverty line" (population series, related)
- PV_LEVEL: categorical; no match. PV_VMIR, SPP_VMI: "vast majority income" (none)
- SPP_CHLD_SOC_PROT: "social protection coverage children", "children covered by social protection benefits ILO", "social assistance coverage" (population ASPIRE series only, related)
- SPP_DIST_SOC_PROT_BNFT: "social protection benefits distribution poorest quintile" (none) -> "benefit incidence poorest quintile all social protection" (none) -> "benefits incidence" (WDI PER_ALLSP_BEN_Q1_TOT, ASPIRE SPL_BEF_GRP_PRG)
- SPP_GDPPC: "GDP per capita current US dollars"; SPP_GINI: "Gini index"; SPP_HSLD_INCOME_SHARE: "income share held by lowest 20 percent", "...highest 20 percent", "income share lowest 40 percent"; SPP_PALMA: "Palma ratio" (OECD IDD only)
- SPP_MOTHERS_CASH_BNF: "mothers with newborns receiving maternity cash benefit" / "maternity benefits coverage mothers" / "maternity benefit" (WBL legal entitlements only; none)
- WS_HCF_*: long phrasings all failed -> "WASH health care facilities" (HCP basic water/sanitation/hygiene); "health care waste management", "health care facilities waste management" (none); "health care facilities cleaning" (none)
- WS_PPL_HF_HANDWASH: "population with basic handwashing facilities with soap and water" (none) -> "handwashing facilities"
- WS_PPL_M_NPART: "adolescent girls not participating ... menstrual period" / "menstrual hygiene" (none)
- WS_PPL_S: "population using at least basic sanitation services" (none) -> "basic sanitation services", "safely managed sanitation", "basic sanitation population"
- WS_PPL_SF: "improved sanitation facilities", "sewer connection" (CLEAR latrine series only), "improved latrines"
- WS_PPL_S_OD: "open defecation"
- WS_PPL_W_DW: "basic drinking water services", "safely managed drinking water", "limited drinking water services", "people using basic drinking water"
- WS_PPL_W_DWSR: "improved water source" (CLEAR non-piped/unimproved/FFC series)
- WS_PPL_W_SW: "surface water drinking"
- WS_SCH_H / H-F: "schools basic hygiene services", "schools handwashing facilities"; WS_SCH_S / S-I: "schools basic sanitation services", "schools improved sanitation"; WS_SCH_W-I / W_DW: "schools drinking water"
- WT_ADLS_10-17_LBR_ECON: "child labour thresholds"; LBR_HC: "child labour household chores"; TIME_ECON: "hours spent in economic activity children"; TIME_HC: "hours household chores children" / "time use children"
- WT_ADLS_ED_NEET: "youth not in education employment or training" (none) -> "NEET youth"; "NEET ages 15-19" (none)
- WT_ADLS_LAB_FRC_UNEMP: "youth unemployment rate ages 15-24" (none) -> "youth unemployment"

## Ambiguities / judgement calls
- Known UNICEF_DW mirrors in this part (NT_ANT_HAZ_NE2, NT_ANT_WHZ_NE2, NT_IOD_ANY_TH, NT_IOD_ANY_TS) recorded directly; UNICEF_DW_NT_ANT_WAZ_NE2 (underweight) and WHZ_NE3/PO2 did NOT surface in search and were not in the known list, so not recorded.
- WB_HNP_SN_ITK_SALT_ZS "Consumption of iodized salt (% of households)": definition wording matches NT_IOD_ANY_TH almost verbatim; recorded as "same" for TH and "related" for TS (denominator ambiguity).
- WB_HCP_OVERWEIGHT is titled "Survey Estimates" but its source is the WDI modeled series SH.STA.OWGH.ME.ZS; recorded under NT_ANT_WHZ_PO2_MOD with a note.
- WB_HCP_FAO_STUNTING is actually low birthweight (ID misleading); recorded under NT_BW_LBW.
- WB_HNP_SH_STA_IYCF_ZS (all 3 IYCF practices, DHS) recorded as "same" for NT_CF_MAD; DHS vs UNICEF 2021 IYCF definitions may differ in detail.
- MNCH_PNEUCARE: WB_HCP_U5_PNEU_CS has the UNICEF indicator name in source but cites WHO GHO; unicef_sourced="no" per the rule.
- PT_MRD_U18 UNDC unit is listed as COUNT but the indicator is a proportion; matched to the female 20-24 percentage series.
- PT_CM_* series (women 20-24 by child-marriage status) have no Data360 counterpart with marital-status split; recorded best population-level counterparts as "related".
- UNICEF trend-analysis series (PT_F_MRD_U15_TND, _U18_TND, PT_F_15-19_FGM_TND) matched to survey-point WDI series as "related".
- SPP_DIST_SOC_PROT_BNFT: ASPIRE SPL_BEF_GRP_PRG metadata has an empty sources list; UNICEF SPP series presumably derived from ASPIRE but not confirmed.
- WS_SCH_S HCP definition text appears copy-pasted from the HCF sanitation definition (staff toilet, accessible toilet), not the JMP schools definition; recorded as "same" on the basis of the name in source.
- CLEAR Water (WB_CLEAR) series re-publish JMP ladders with WHO and UNICEF listed as source organisations; treated as UNICEF-sourced (JMP).
- Count-type UNICEF series (NUMTH, TMRD15) have no Data360 counterpart; Data360 holds prevalence only.
- 5-19 year-old BMI (NCD-RisC/WHO) series not found in Data360 despite WHO_GHO-filtered search.
