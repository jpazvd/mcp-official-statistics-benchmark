# Data360 extraction log (pairs_d360_1.csv)

Countries: NGA;IND;BRA | years 2000-2025 | limit 100

## STEP A - data calls

### CME_MR -> WB_WDI_SH_DYN_MORT (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=75 | has_more=False | error=none
- rows written: 75

### CME_SB -> WB_HNP_SH_DTH_STLB (WB_HNP)
- call: get_data offset=0 limit=100 2000-2025 | rows=72 | has_more=False | error=none
- rows written: 72
- note: 2022-2023 rows returned with OBS_VALUE literal null

### CME_SBR -> WB_HNP_SH_DYN_STLB (WB_HNP)
- call: get_data offset=0 limit=100 2000-2025 | rows=72 | has_more=False | error=none
- rows written: 72
- note: 2022-2023 rows returned with OBS_VALUE literal null

### CME_TM -> WB_WDI_SH_DTH_MORT (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=75 | has_more=False | error=none
- rows written: 75

### DM_DPR_CHD -> WB_WDI_SP_POP_DPND_YG (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=78 | has_more=False | error=none
- rows written: 78

### DM_DPR_OLD -> WB_WDI_SP_POP_DPND_OL (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=78 | has_more=False | error=none
- rows written: 78

### DM_DPR_TOT -> WB_WDI_SP_POP_DPND (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=78 | has_more=False | error=none
- rows written: 78

### DM_FRATE_TOT -> WB_WDI_SP_DYN_TFRT_IN (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=75 | has_more=False | error=none
- rows written: 75

### DM_LIFE_EXP -> WB_WDI_SP_DYN_LE00_IN (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=75 | has_more=False | error=none
- rows written: 75

### DM_POP -> WB_WDI_SP_POP_TOTL (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=78 | has_more=False | error=none
- rows written: 78

### DM_POP_GRT -> WB_WDI_SP_POP_GROW (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=78 | has_more=False | error=none
- rows written: 78

### DM_POP_URBN -> WB_WDI_SP_URB_TOTL_IN_ZS (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=78 | has_more=False | error=none
- rows written: 78
- note: rows carry URBANISATION=URB dimension

### DM_POP_U_GRT -> WB_WDI_SP_URB_GROW (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=78 | has_more=False | error=none
- rows written: 78
- note: rows carry URBANISATION=URB dimension

### ECD_CHLD_ADLT_SRC -> WB_EDSTATS_SE_PRM_LSKC_4 (WB_EDSTATS)
- call: get_data NGA;IND;BRA 2000-2025 limit=100 | rows=0 | has_more=False | error=none
- call: get_disaggregation required_country=NGA;IND;BRA | rows=REF_AREA count=10; NGA true, IND false, BRA false; UNIT_MEASURE=SHARE; TIME_PERIOD 1970-2024 | has_more=False | error=none
- call: get_data NGA 1970-2025 ref_area_filter=none | rows=0 | has_more=False | error=none
- call: get_data no country 1970-2025 ref_area_filter=none limit=20 | rows=0 | has_more=False | error=none
- rows written: 1 (no-data placeholder)
- note: get_disaggregation reports NGA covered (REF_AREA count=10; IND/BRA not) but get_data returned 0 rows for NGA;IND;BRA 2000-2025, for NGA alone 1970-2025 with ref_area_filter=none, and with no country filter at all

### ECD_CHLD_BKS_HM -> WB_EDSTATS_SE_PRM_LSKC_3 (WB_EDSTATS)
- call: get_data NGA;IND;BRA 2000-2025 limit=100 | rows=0 | has_more=False | error=none
- rows written: 1 (no-data placeholder)

### ECD_CHLD_EDU_PGM -> WB_EDSTATS_SE_PRM_LCBC_2 (WB_EDSTATS)
- call: get_data NGA;IND;BRA 2000-2025 limit=100 | rows=0 | has_more=False | error=none
- rows written: 1 (no-data placeholder)

### ECD_CHLD_LMPSL -> WB_EDSTATS_UIS_ONTRACK_THREE_DOMAINS (WB_EDSTATS)
- call: get_data NGA;IND;BRA 2000-2025 limit=100 | rows=0 | has_more=False | error=none
- call: get_disaggregation required_country=NGA;IND;BRA | rows=REF_AREA count=85; NGA true, IND false, BRA false; UNIT_MEASURE=SHARE; TIME_PERIOD 1970-2024 | has_more=False | error=none
- call: get_data NGA 1970-2025 ref_area_filter=none | rows=0 | has_more=False | error=none
- call: get_data NGA default years ref_area_filter=none | rows=0 | has_more=False | error=none
- rows written: 1 (no-data placeholder)
- note: get_disaggregation reports NGA covered (REF_AREA count=85; IND/BRA not) but get_data returned 0 rows for NGA;IND;BRA 2000-2025, for NGA alone 1970-2025 with ref_area_filter=none, and for NGA with default year window

### ECON_GVT_EXP_PTEXP -> WB_WDI_SE_XPD_TOTL_GB_ZS (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=54 | has_more=False | error=none
- rows written: 54
- note: BRA 2000 returned OBS_VALUE 0 (verbatim)

### ECON_GVT_EXP_PTGDP -> WB_WDI_SE_XPD_TOTL_GD_ZS (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=53 | has_more=False | error=none
- rows written: 53

### ECON_GVT_REV_PTGDP -> IMF_WEO_GGR_NGDP (IMF_WEO)
- call: get_data offset=0 limit=100 2000-2025 | rows=77 | has_more=False | error=none
- rows written: 77
- note: rows carry COMP_BREAKDOWN_1=V_LST dimension; 2024-2025 values are IMF WEO estimates/projections per source

### ECON_ODA_INFLOW_PTGNI -> WB_WDI_DT_ODA_ODAT_GN_ZS (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=64 | has_more=False | error=none
- rows written: 64
- note: NGA has no rows for 2000-2007

### ECON_ODA_INFLOW_USD -> WB_WDI_DT_ODA_ODAT_CD (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=72 | has_more=False | error=none
- rows written: 72

### ECON_ODA_OUTFLOW_PTGNI -> WB_WDI_DC_ODA_TOTL_GN_ZS (WB_WDI)
- call: get_data NGA;IND;BRA 2000-2025 limit=100 | rows=0 | has_more=False | error=none
- rows written: 1 (no-data placeholder)
- note: indicator covers DAC donor countries; NGA/IND/BRA are not DAC donors

### ECON_ODA_OUTFLOW_USD -> WB_WDI_DC_ODA_TOTL_CD (WB_WDI)
- call: get_data NGA;IND;BRA 2000-2025 limit=100 | rows=0 | has_more=False | error=none
- rows written: 1 (no-data placeholder)
- note: indicator covers DAC donor countries; NGA/IND/BRA are not DAC donors

### ED_CR -> WB_EDSTATS_UIS_CR_1 (WB_EDSTATS)
- call: get_data NGA;IND;BRA 2000-2025 limit=100 | rows=0 | has_more=False | error=none
- call: get_disaggregation required_country=NGA;IND;BRA | rows=REF_AREA count=167; NGA/IND/BRA all true; SEX, URBANISATION, COMP_BREAKDOWN_1 (Q1-Q5) dims | has_more=False | error=none
- call: get_data NGA;IND;BRA 2000-2025 filters SEX=_T URBANISATION=_T ref_area_filter=none | rows=0 | has_more=False | error=none
- call: get_data BRA default years ref_area_filter=none | rows=0 | has_more=False | error=none
- call: get_data BRA 2000-2025 filters incl COMP_BREAKDOWN_1=_T | rows=0 | has_more=False | error=failed_validation: Invalid value '_T' for COMP_BREAKDOWN_1 (options Q1-Q5)
- call: get_data BRA 2000-2025 COMP_BREAKDOWN_1=WB_EDSTATS_Q1 | rows=0 | has_more=False | error=none
- rows written: 1 (no-data placeholder)
- note: get_disaggregation reports NGA, IND and BRA all covered (REF_AREA count=167; dims SEX F/M/_T, URBANISATION _T/RUR/URB, COMP_BREAKDOWN_1 wealth quintiles Q1-Q5) but every get_data call returned 0 rows (combined countries; SEX=_T+URBANISATION=_T; BRA alone default years; BRA with COMP_BREAKDOWN_1=WB_EDSTATS_Q1). WB_EDSTATS data endpoint appears empty via this MCP server

### ED_LR -> WB_WDI_SE_ADT_1524_LT_ZS (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=45 | has_more=False | error=none
- rows written: 45
- note: rows carry AGE=Y15T24 dimension

### ED_MAT -> WB_HCP_MINPROF_M_ENDPRIM (WB_HCP)
- call: get_data offset=0 limit=100 2000-2025 | rows=3 | has_more=False | error=none
- rows written: 3
- note: no NGA rows

### ED_READ -> WB_HCP_MINPROF_R_ENDPRIM (WB_HCP)
- call: get_data offset=0 limit=100 2000-2025 | rows=3 | has_more=False | error=none
- rows written: 3
- note: no NGA rows

### ED_ROFST_ADM -> WB_WDI_SE_PRM_UNER_ZS (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=42 | has_more=False | error=none
- rows written: 42

### FD_STUNTING -> UNICEF_DW_FD_STUNTING (UNICEF_DW)
- call: get_data NGA;IND;BRA 2000-2025 limit=100 | rows=0 | has_more=False | error=none
- call: get_disaggregation required_country=NGA;IND;BRA | rows=REF_AREA count=40; NGA/IND/BRA all false | has_more=False | error=none
- rows written: 1 (no-data placeholder)
- note: get_disaggregation confirms NGA, IND, BRA not covered (REF_AREA count=40, all three false); dims AGE M24T59/M36T59; TIME_PERIOD 2017-2023

### FD_UNDERWEIGHT -> UNICEF_DW_FD_UNDERWEIGHT (UNICEF_DW)
- call: get_data NGA;IND;BRA 2000-2025 limit=100 | rows=0 | has_more=False | error=none
- call: get_disaggregation required_country=NGA;IND;BRA | rows=REF_AREA count=41; NGA/IND/BRA all false | has_more=False | error=none
- rows written: 1 (no-data placeholder)
- note: get_disaggregation confirms NGA, IND, BRA not covered (REF_AREA count=41, all three false); dims AGE M24T59/M36T59; TIME_PERIOD 2017-2023

### GN_ED_ATTN -> UNICEF_DW_GN_ED_ATTN (UNICEF_DW)
- call: get_data offset=0 limit=100 2000-2025 | rows=32 | has_more=False | error=none
- call: get_disaggregation required_country=NGA;IND;BRA | rows=REF_AREA count=179; NGA/IND/BRA all true; SEX F/M | has_more=False | error=none
- rows written: 32
- note: rows carry SEX dimension (F/M only; no _T total in codelist); indicator_description='Series Footnote: nan - Source Link: nan - Time Coverage: nan'

### GN_FB_BNK_ACCSS -> WB_WDI_FX_OWN_TOTL_ZS (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=15 | has_more=False | error=none
- rows written: 15

### GN_LF_PTCPN -> WB_WDI_SL_TLF_CACT_ZS (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=78 | has_more=False | error=none
- rows written: 78

### GN_TIMEUSE -> WB_GS_SG_TIM_UWRK (WB_GS)
- call: get_data offset=0 limit=100 2000-2025 | rows=6 | has_more=False | error=none
- rows written: 6
- note: rows carry SEX dimension (F/M); BRA only, no NGA/IND rows

### GN_UNMPLY -> WB_WDI_SL_UEM_TOTL_ZS (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=78 | has_more=False | error=none
- rows written: 78

### HVA_EPI_INF_ANN -> WB_WDI_SH_HIV_INCD_YG (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=26 | has_more=False | error=none
- rows written: 26
- note: only NGA full series plus IND 2024; no BRA rows

### HVA_EPI_LHIV -> WB_HNP_SH_HIV (WB_HNP)
- call: get_data offset=0 limit=100 2000-2025 | rows=72 | has_more=False | error=none
- rows written: 72
- note: WB_HNP_SH_HIV is all-ages population living with HIV, not the UNICEF 0-14 child series; OBS_VALUE literal null for all NGA rows, all IND rows except 2022, and BRA 2023

### HVA_PREV_KNOW -> WB_HCP_HVA_PREV_KNOW (WB_HCP)
- call: get_data offset=0 limit=100 2000-2025 | rows=4 | has_more=False | error=none
- rows written: 4
- note: rows carry AGE=Y15T24 dimension; no BRA rows

### IM_BCG -> WB_HCP_VACBCG (WB_HCP)
- call: get_data offset=0 limit=100 2000-2025 | rows=45 | has_more=False | error=none
- rows written: 45
- note: series starts 2010 in this database

### IM_HEPBB -> WB_HCP_VACHEPBB (WB_HCP)
- call: get_data offset=0 limit=100 2000-2025 | rows=45 | has_more=False | error=none
- rows written: 45
- note: series starts 2010 in this database

### IM_HPV -> WB_HCP_HPV_VAC (WB_HCP)
- call: get_data offset=0 limit=100 2000-2025 | rows=13 | has_more=False | error=none
- rows written: 13
- note: no IND rows; NGA only 2023-2024

### IM_MCV2 -> WB_HCP_VACMCV2 (WB_HCP)
- call: get_data offset=0 limit=100 2000-2025 | rows=35 | has_more=False | error=none
- rows written: 35
- note: series starts 2010; NGA rows only from 2019

### IM_PAB -> WB_WDI_SH_VAC_TTNS_ZS (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=75 | has_more=False | error=none
- rows written: 75

### IM_VACC -> WB_HCP_VACDTP3 (WB_HCP)
- call: get_data offset=0 limit=100 2000-2025 | rows=45 | has_more=False | error=none
- rows written: 45
- note: series starts 2010 in this database

### MG_INTERNAL_DISP_PERS -> WB_WDI_SM_POP_IDPC (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=35 | has_more=False | error=none
- rows written: 35
- note: BRA rows only 2021-2025; NGA from 2013; IND from 2009

### MG_INTNL_MG_CNTRY_DEST -> WB_WDI_SM_POP_TOTL (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=18 | has_more=False | error=none
- rows written: 18
- note: quinquennial points 2000-2020 plus 2024

### MG_NEW_INTERNAL_DISP -> WB_WDI_VC_IDP_NWCV (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=33 | has_more=False | error=none
- rows written: 33
- note: BRA rows only 2021-2023

### MG_RFGS_CNTRY_ASYLM -> WB_WDI_SM_POP_RHCR_EA (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=78 | has_more=False | error=none
- rows written: 78

### MG_RFGS_CNTRY_ORIGIN -> WB_WDI_SM_POP_RHCR_EO (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=78 | has_more=False | error=none
- rows written: 78

### MNCH_ABR -> WB_WDI_SP_ADO_TFRT (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=75 | has_more=False | error=none
- rows written: 75

### MNCH_ANC1 -> WB_WDI_SH_STA_ANVC_ZS (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=19 | has_more=False | error=none
- rows written: 19

### MNCH_ANC4 -> WB_HCP_ANTENATAL_CARE_4 (WB_HCP)
- call: get_data offset=0 limit=100 2000-2025 | rows=22 | has_more=False | error=none
- rows written: 22
- note: rows carry AGE=Y15T49 dimension

### MNCH_BIRTH18 -> WB_HCP_BIRTHS_18 (WB_HCP)
- call: get_data offset=0 limit=100 2000-2025 | rows=8 | has_more=False | error=none
- rows written: 8
- note: rows carry AGE=Y20T24 dimension (standard 20-24 cohort, not the Y15T49 variant listed in pairs file); no BRA rows

### MNCH_DIARCARE -> WB_HCP_DIARRHOEA (WB_HCP)
- call: get_data offset=0 limit=100 2000-2025 | rows=9 | has_more=False | error=none
- rows written: 9
- note: rows carry AGE=Y0T4 dimension; no BRA rows; NGA 2011 value 3.7 is an outlier vs adjacent years (verbatim)

### MNCH_DIARRHOEAT_TR -> WB_WDI_SH_STA_ORTH (WB_WDI)
- call: get_data offset=0 limit=100 2000-2025 | rows=10 | has_more=False | error=none
- rows written: 10
- note: no BRA rows

### MNCH_INSTDEL -> WB_HCP_INSBIRTHS (WB_HCP)
- call: get_data offset=0 limit=100 2000-2025 | rows=31 | has_more=False | error=none
- rows written: 31
- note: no NGA rows; same d360 series also mapped to MNCH_INSTDEL_TND

### MNCH_INSTDEL_TND -> WB_HCP_INSBIRTHS (WB_HCP)
- call: reused result of get_data for WB_HCP_INSBIRTHS (same series as MNCH_INSTDEL) | rows=31 | has_more=False | error=none
- rows written: 31
- note: same d360 series as MNCH_INSTDEL (one call reused, rows duplicated under this code); no NGA rows

### MNCH_IPTP -> WB_HNP_SH_MLR_IPTP_ZS (WB_HNP)
- call: get_data offset=0 limit=100 2000-2025 | rows=72 | has_more=False | error=none
- rows written: 72
- note: OBS_VALUE literal null for all BRA and IND rows and most NGA rows; only NGA 2003, 2007, 2008, 2010, 2011, 2013, 2015, 2017, 2018 carry values


## STEP B - metadata calls

- metadata CME_MR -> WB_WDI_SH_DYN_MORT (WB_WDI): ok; version_date=2026-07-01; time_periods=1960-2024; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata CME_SB -> WB_HNP_SH_DTH_STLB (WB_HNP): ok; version_date=2024-09-23; time_periods=1960-2023; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata CME_SBR -> WB_HNP_SH_DYN_STLB (WB_HNP): ok; version_date=2024-09-23; time_periods=1960-2023; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata CME_TM -> WB_WDI_SH_DTH_MORT (WB_WDI): ok; version_date=2026-07-01; time_periods=1960-2024; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata DM_DPR_CHD -> WB_WDI_SP_POP_DPND_YG (WB_WDI): ok; version_date=2026-07-01; time_periods=1960-2025; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata DM_DPR_OLD -> WB_WDI_SP_POP_DPND_OL (WB_WDI): ok; version_date=2026-07-01; time_periods=1960-2025; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata DM_DPR_TOT -> WB_WDI_SP_POP_DPND (WB_WDI): ok; version_date=2026-07-01; time_periods=1960-2025; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- (corrected: CME_SB, CME_SBR, CME_TM metadata rows re-written with verbatim server text)
- metadata CME_SB -> WB_HNP_SH_DTH_STLB (WB_HNP): ok; version_date=2024-09-23; time_periods=1960-2023; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata CME_SBR -> WB_HNP_SH_DYN_STLB (WB_HNP): ok; version_date=2024-09-23; time_periods=1960-2023; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata CME_TM -> WB_WDI_SH_DTH_MORT (WB_WDI): ok; version_date=2026-07-01; time_periods=1960-2024; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- anomaly note (observer, not server): WB_WDI_SH_DTH_MORT alternate_identifiers carries label "Mortality rate age 20-24", which does not match the series name "Number of under-five deaths"
- metadata DM_FRATE_TOT -> WB_WDI_SP_DYN_TFRT_IN (WB_WDI): ok; version_date=2026-07-01; time_periods=1960-2024; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata DM_LIFE_EXP -> WB_WDI_SP_DYN_LE00_IN (WB_WDI): ok; version_date=2026-07-01; time_periods=1960-2024; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata DM_POP -> WB_WDI_SP_POP_TOTL (WB_WDI): ok; version_date=2026-07-01; time_periods=1960-2025; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata DM_POP_GRT -> WB_WDI_SP_POP_GROW (WB_WDI): ok; version_date=2026-07-01; time_periods=1961-2025; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata DM_POP_URBN -> WB_WDI_SP_URB_TOTL_IN_ZS (WB_WDI): ok; version_date=2026-07-01; time_periods=1960-2025; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata DM_POP_U_GRT -> WB_WDI_SP_URB_GROW (WB_WDI): ok; version_date=2026-07-01; time_periods=1961-2025; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- note: DM_POP_U_GRT methodology text had runs of blank lines in the server response (collapsed to single spaces in the saved copy); the alternate_identifier URI lists for DM_FRATE_TOT and DM_POP were shortened to the first URI (WPP). All other fields verbatim.
- anomaly note (observer): WB_WDI_SP_DYN_LE00_IN alternate_identifiers carries label "Male Life Expectancy at Birth (years)" for the total series.
- metadata ECD_CHLD_ADLT_SRC -> WB_EDSTATS_SE_PRM_LSKC_4 (WB_EDSTATS): ok; version_date=2024-10-03; time_periods=2019-2023; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata ECD_CHLD_BKS_HM -> WB_EDSTATS_SE_PRM_LSKC_3 (WB_EDSTATS): ok; version_date=2024-10-03; time_periods=2021-2023; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata ECD_CHLD_EDU_PGM -> WB_EDSTATS_SE_PRM_LCBC_2 (WB_EDSTATS): ok; version_date=2024-10-03; time_periods=2019-2023; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata ECD_CHLD_LMPSL -> WB_EDSTATS_UIS_ONTRACK_THREE_DOMAINS (WB_EDSTATS): ok; version_date=2024-10-03; time_periods=2010-2019; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata ECON_GVT_EXP_PTEXP -> WB_WDI_SE_XPD_TOTL_GB_ZS (WB_WDI): ok; version_date=2026-07-01; time_periods=1980-2025; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata ECON_GVT_EXP_PTGDP -> WB_WDI_SE_XPD_TOTL_GD_ZS (WB_WDI): ok; version_date=2026-07-01; time_periods=1970-2025; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata ECON_GVT_REV_PTGDP -> IMF_WEO_GGR_NGDP (IMF_WEO): ok; version_date=2026-10-13; time_periods=1980-2031; license=License Specified Externally (https://www.imf.org/external/terms.htm)
- note: for ECON_GVT_EXP_PTEXP/PTGDP the server methodology/statistical_concept text contained long runs of \r\n; collapsed to single spaces in the saved copy, wording otherwise verbatim. ECD_* WB_EDSTATS metadata time_periods are 2019-2023 / 2021-2023 / 2019-2023 / 2010-2019 although get_data returned no rows.
- metadata ECON_ODA_INFLOW_PTGNI -> WB_WDI_DT_ODA_ODAT_GN_ZS (WB_WDI): ok; version_date=2026-07-01; time_periods=1960-2023; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata ECON_ODA_INFLOW_USD -> WB_WDI_DT_ODA_ODAT_CD (WB_WDI): ok; version_date=2026-07-01; time_periods=1960-2023; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata ECON_ODA_OUTFLOW_PTGNI -> WB_WDI_DC_ODA_TOTL_GN_ZS (WB_WDI): ok; version_date=2025-06-05; time_periods=1960-2017; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata ECON_ODA_OUTFLOW_USD -> WB_WDI_DC_ODA_TOTL_CD (WB_WDI): ok; version_date=2025-06-05; time_periods=1960-2024; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata ED_CR -> WB_EDSTATS_UIS_CR_1 (WB_EDSTATS): ok; version_date=2024-10-03; time_periods=1996-2019; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata ED_LR -> WB_WDI_SE_ADT_1524_LT_ZS (WB_WDI): ok; version_date=2026-04-08; time_periods=1970-2024; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- note: ED_CR (WB_EDSTATS_UIS_CR_1) metadata time_periods 1996-2019 although get_data returned no rows for NGA/IND/BRA; ECON_ODA_INFLOW_PTGNI methodology had a duplicated paragraph in the server text (kept once in saved copy).
- metadata ED_MAT -> WB_HCP_MINPROF_M_ENDPRIM (WB_HCP): ok; version_date=2026-10-14; time_periods=1995-2019; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata ED_READ -> WB_HCP_MINPROF_R_ENDPRIM (WB_HCP): ok; version_date=2026-10-14; time_periods=2001-2019; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata ED_ROFST_ADM -> WB_WDI_SE_PRM_UNER_ZS (WB_WDI): ok; version_date=2026-04-08; time_periods=1970-2024; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata FD_STUNTING -> UNICEF_DW_FD_STUNTING (UNICEF_DW): ok; version_date=2024-10-02; time_periods=2017-2023; license=CC BY-NC 3.0 IGO (https://creativecommons.org/licenses/by-nc/3.0/igo/)
- metadata FD_UNDERWEIGHT -> UNICEF_DW_FD_UNDERWEIGHT (UNICEF_DW): ok; version_date=2024-10-02; time_periods=2017-2023; license=CC BY-NC 3.0 IGO (https://creativecommons.org/licenses/by-nc/3.0/igo/)
- metadata GN_ED_ATTN -> UNICEF_DW_GN_ED_ATTN (UNICEF_DW): ok; version_date=2024-10-02; time_periods=1970-2021; license=CC BY-NC 3.0 IGO (https://creativecommons.org/licenses/by-nc/3.0/igo/)
- anomaly note (observer): UNICEF_DW_GN_ED_ATTN definition says "at least upper secondary (ISCED 3)" but the methodology text says "attained or completed primary education"; UNICEF_DW topics for GN_ED_ATTN are "Planet / Agriculture and Food / Healthy Sustainable Diets" (as served). ED_ROFST_ADM methodology \r\n runs collapsed to single spaces.
- metadata GN_FB_BNK_ACCSS -> WB_WDI_FX_OWN_TOTL_ZS (WB_WDI): ok; version_date=2026-07-01; time_periods=2011-2024; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata GN_LF_PTCPN -> WB_WDI_SL_TLF_CACT_ZS (WB_WDI): ok; version_date=2026-07-01; time_periods=1990-2025; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata GN_TIMEUSE -> WB_GS_SG_TIM_UWRK (WB_GS): ok; version_date=2025-11-04; time_periods=1960-2023; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata GN_UNMPLY -> WB_WDI_SL_UEM_TOTL_ZS (WB_WDI): ok; version_date=2026-07-01; time_periods=1991-2025; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata HVA_EPI_INF_ANN -> WB_WDI_SH_HIV_INCD_YG (WB_WDI): ok; version_date=2025-06-05; time_periods=1990-2024; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata HVA_EPI_LHIV -> WB_HNP_SH_HIV (WB_HNP): ok; version_date=2024-09-23; time_periods=1960-2023; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata HVA_PREV_KNOW -> WB_HCP_HVA_PREV_KNOW (WB_HCP): ok; version_date=2026-10-14; time_periods=2010-2023; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- anomaly note (observer): WB_HNP_SH_HIV definition_long says "percentage of people who are infected with HIV" while measurement_unit is Count and name is "Population living with HIV". Multi-paragraph methodology texts (GN_LF_PTCPN, GN_UNMPLY, HVA_EPI_LHIV) had \r\n runs collapsed to single spaces.
- metadata IM_BCG -> WB_HCP_VACBCG (WB_HCP): ok; version_date=2026-10-14; time_periods=2010-2024; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata IM_HEPBB -> WB_HCP_VACHEPBB (WB_HCP): ok; version_date=2026-10-14; time_periods=2010-2024; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata IM_HPV -> WB_HCP_HPV_VAC (WB_HCP): ok; version_date=2026-10-14; time_periods=2010-2024; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata IM_MCV2 -> WB_HCP_VACMCV2 (WB_HCP): ok; version_date=2026-10-14; time_periods=2010-2024; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata IM_PAB -> WB_WDI_SH_VAC_TTNS_ZS (WB_WDI): ok; version_date=2026-07-01; time_periods=1980-2024; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata IM_VACC -> WB_HCP_VACDTP3 (WB_HCP): ok; version_date=2026-10-14; time_periods=2010-2024; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata MG_INTERNAL_DISP_PERS -> WB_WDI_SM_POP_IDPC (WB_WDI): ok; version_date=2026-07-01; time_periods=2009-2024; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata MG_INTNL_MG_CNTRY_DEST -> WB_WDI_SM_POP_TOTL (WB_WDI): ok; version_date=2026-07-01; time_periods=1990-2024; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata MG_NEW_INTERNAL_DISP -> WB_WDI_VC_IDP_NWCV (WB_WDI): ok; version_date=2026-07-01; time_periods=2009-2023; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata MG_RFGS_CNTRY_ASYLM -> WB_WDI_SM_POP_RHCR_EA (WB_WDI): ok; version_date=2026-07-01; time_periods=1960-2024; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata MG_RFGS_CNTRY_ORIGIN -> WB_WDI_SM_POP_RHCR_EO (WB_WDI): ok; version_date=2026-07-01; time_periods=1960-2024; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- note: MG_* methodology texts had \r\n paragraph breaks collapsed to single spaces in saved copies; MG_INTNL_MG_CNTRY_DEST and MG_NEW_INTERNAL_DISP kept their \n breaks.
- metadata MNCH_ABR -> WB_WDI_SP_ADO_TFRT (WB_WDI): ok; version_date=2026-07-01; time_periods=1960-2024; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata MNCH_ANC1 -> WB_WDI_SH_STA_ANVC_ZS (WB_WDI): ok; version_date=2026-07-01; time_periods=1984-2021; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata MNCH_ANC4 -> WB_HCP_ANTENATAL_CARE_4 (WB_HCP): ok; version_date=2026-10-14; time_periods=2010-2024; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata MNCH_BIRTH18 -> WB_HCP_BIRTHS_18 (WB_HCP): ok; version_date=2026-10-14; time_periods=2010-2024; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata MNCH_DIARCARE -> WB_HCP_DIARRHOEA (WB_HCP): ok; version_date=2026-10-14; time_periods=2010-2024; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata MNCH_DIARRHOEAT_TR -> WB_WDI_SH_STA_ORTH (WB_WDI): ok; version_date=2026-07-01; time_periods=1985-2021; license=CC BY-4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata MNCH_INSTDEL -> WB_HCP_INSBIRTHS (WB_HCP): ok; version_date=2026-10-14; time_periods=1990-2023; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata MNCH_INSTDEL_TND -> WB_HCP_INSBIRTHS (WB_HCP): ok; version_date=2026-10-14; time_periods=1990-2023; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- metadata MNCH_IPTP -> WB_HNP_SH_MLR_IPTP_ZS (WB_HNP): ok; version_date=2024-09-23; time_periods=1960-2023; license=CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
- note: MNCH_INSTDEL and MNCH_INSTDEL_TND share one metadata call (WB_HCP_INSBIRTHS); the row is duplicated under both UNICEF codes.

## Summary

- Indicators in pairs_d360_1.csv: 59; all 59 present in both output files (59 metadata rows, 2,500 values rows = 2,491 observations + 9 no-data placeholders).
- No pagination was needed: every get_data call returned has_more=false (max 78 rows per call, below limit=100).
- Server always returned failed_validation "ref_area_filter=member_economies_only applies only when REF_AREA is unpinned... filter was not applied" when country_code is set; harmless, logged once here rather than per call.
- No data (placeholder rows): ECD_CHLD_ADLT_SRC, ECD_CHLD_BKS_HM, ECD_CHLD_EDU_PGM, ECD_CHLD_LMPSL, ED_CR (all WB_EDSTATS: get_data returned 0 rows under every filter tried, even where get_disaggregation reports NGA/IND/BRA covered - the WB_EDSTATS data endpoint appears empty via this MCP server); FD_STUNTING, FD_UNDERWEIGHT (UNICEF_DW: NGA/IND/BRA confirmed not covered); ECON_ODA_OUTFLOW_PTGNI, ECON_ODA_OUTFLOW_USD (donor-side series, no rows for these recipients).
- Literal "null" OBS_VALUE rows kept verbatim: CME_SB (6), CME_SBR (6), HVA_EPI_LHIV (48), MNCH_IPTP (63).
- Dimension fields recorded in `dimensions` (compact JSON): URBANISATION (DM_POP_URBN, DM_POP_U_GRT), COMP_BREAKDOWN_1=V_LST (ECON_GVT_REV_PTGDP), AGE (ED_LR Y15T24, HVA_PREV_KNOW Y15T24, MNCH_ANC4 Y15T49, MNCH_BIRTH18 Y20T24, MNCH_DIARCARE Y0T4), SEX F/M (GN_ED_ATTN, GN_TIMEUSE). No obs_status field is returned by this server; column left empty.
- Mapping caveats (data as served, flagged in notes): HVA_EPI_LHIV -> WB_HNP_SH_HIV is all-ages population living with HIV, not the UNICEF 0-14 series; MNCH_BIRTH18 rows carry AGE=Y20T24 (standard cohort) not the Y15T49 variant listed in the pairs file; MNCH_INSTDEL and MNCH_INSTDEL_TND both map to WB_HCP_INSBIRTHS (one call, rows and metadata duplicated under both codes).
- Value anomalies kept verbatim: ECON_GVT_EXP_PTEXP BRA 2000 = 0; MNCH_DIARCARE NGA 2011 = 3.7 (adjacent years 27-65).
- Metadata: version_or_last_update_date taken from version_statement.version_date (date_last_update was null for every indicator). Multi-paragraph server texts containing \r\n runs were collapsed to single spaces where noted above; wording otherwise verbatim. Observer-flagged label inconsistencies in server metadata: WB_WDI_SH_DTH_MORT alternate id labelled "Mortality rate age 20-24"; WB_WDI_SP_DYN_LE00_IN alternate id labelled "Male Life Expectancy at Birth"; WB_HNP_SH_HIV definition says "percentage" while unit is Count; UNICEF_DW_GN_ED_ATTN definition (ISCED 3) vs methodology (primary).
