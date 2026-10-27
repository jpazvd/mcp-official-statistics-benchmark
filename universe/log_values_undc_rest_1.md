# Log: UN System Data Commons extraction — pairs_undc_rest_1.csv (52 variables x NGA/IND/BRA)

Date: 2026-10-27. Tool: UN_System_Data_Commons get_observations(variable_dcid, place_dcid, date="all").
Output: /home/claude/universe/values_unicef_undc_rest_1.csv

## Call log

| # | undc_dcid | place | status | n obs | year span | note |
|---|-----------|-------|--------|-------|-----------|------|
| 1 | undata/unicef/CME_ARR.AGE--Y0T4 | NGA | ok | 1 | 2023 | tabular data.rows shape; only one obs returned with date=all |
| 1 | undata/unicef/CME_ARR.AGE--Y0T4 | IND | ok | 1 | 2023 | |
| 1 | undata/unicef/CME_ARR.AGE--Y0T4 | BRA | ok | 1 | 2023 | |
| 2 | undata/unicef/CME_ARR.AGE--Y10T19 | NGA | ok | 1 | 2021 | |
| 2 | undata/unicef/CME_ARR.AGE--Y10T19 | IND | ok | 1 | 2021 | |
| 2 | undata/unicef/CME_ARR.AGE--Y10T19 | BRA | ok | 1 | 2021 | |
| 3 | undata/unicef/CME_ARR_SBR | NGA | ok | 1 | 2023 | |
| 3 | undata/unicef/CME_ARR_SBR | IND | ok | 1 | 2023 | value returned as integer literal 4 |
| 3 | undata/unicef/CME_ARR_SBR | BRA | ok | 1 | 2023 | |
| 4 | undata/unicef/CME_MR.AGE--Y0 | NGA | ok | 25 | 2000-2024 | unit given as DCID string undata/UNIT_MEASURE-RATIO_COUNT_DEATHS_PER_1000_COUNT_LIVEBIRTHS |
| 4 | undata/unicef/CME_MR.AGE--Y0 | IND | ok | 25 | 2000-2024 | |
| 4 | undata/unicef/CME_MR.AGE--Y0 | BRA | ok | 25 | 2000-2024 | 2016 value (14.579) breaks the monotone decline (2015=13.72, 2017=13.27) - as returned |
| 5 | undata/unicef/CME_MR.AGE--Y1T4 | NGA | ok | 25 | 2000-2024 | unit DCID ...DEATHS_PER_1000_COUNT_POP_Y1 |
| 5 | undata/unicef/CME_MR.AGE--Y1T4 | IND | ok | 25 | 2000-2024 | |
| 5 | undata/unicef/CME_MR.AGE--Y1T4 | BRA | ok | 25 | 2000-2024 | |
| 6 | undata/unicef/CME_MR.AGE--Y5T14 | NGA | ok | 25 | 2000-2024 | |
| 6 | undata/unicef/CME_MR.AGE--Y5T14 | IND | ok | 25 | 2000-2024 | |
| 6 | undata/unicef/CME_MR.AGE--Y5T14 | BRA | ok | 25 | 2000-2024 | |
| 7 | undata/unicef/CME_MR.AGE--Y10T19 | NGA | ok | 25 | 2000-2024 | |
| 7 | undata/unicef/CME_MR.AGE--Y10T19 | IND | ok | 25 | 2000-2024 | |
| 7 | undata/unicef/CME_MR.AGE--Y10T19 | BRA | ok | 25 | 2000-2024 | |
| 8 | undata/unicef/CME_PND | NGA | ok | 25 | 2000-2024 | ANOMALY: unit=Percent but values are fractions 0.27-0.34 |
| 8 | undata/unicef/CME_PND | IND | ok | 25 | 2000-2024 | same unit/scale mismatch |
| 8 | undata/unicef/CME_PND | BRA | ok | 25 | 2000-2024 | same unit/scale mismatch |
| 9 | undata/unicef/CME_TM.AGE--Y0 | NGA | ok | 25 | 2000-2024 | integer counts |
| 9 | undata/unicef/CME_TM.AGE--Y0 | IND | ok | 25 | 2000-2024 | |
| 9 | undata/unicef/CME_TM.AGE--Y0 | BRA | ok | 25 | 2000-2024 | 2016 bump (42432) consistent with CME_MR Y0 2016 |
| 10 | undata/unicef/CME_TM.AGE--Y5T14 | NGA | ok | 25 | 2000-2024 | |
| 10 | undata/unicef/CME_TM.AGE--Y5T14 | IND | ok | 25 | 2000-2024 | |
| 10 | undata/unicef/CME_TM.AGE--Y5T14 | BRA | ok | 25 | 2000-2024 | |
| 11 | undata/unicef/DM_BRTS | NGA | ok | 26 | 2000-2025 | includes 2025 (projection) |
| 11 | undata/unicef/DM_BRTS | IND | ok | 26 | 2000-2025 | |
| 11 | undata/unicef/DM_BRTS | BRA | ok | 26 | 2000-2025 | |
| 12 | undata/unicef/DM_BRTS_SURVIVING_1 | NGA | ok | 26 | 2000-2025 | |
| 12 | undata/unicef/DM_BRTS_SURVIVING_1 | IND | ok | 26 | 2000-2025 | |
| 12 | undata/unicef/DM_BRTS_SURVIVING_1 | BRA | ok | 26 | 2000-2025 | |
| 13 | undata/unicef/DM_BU_PC_DOU.URBANIZATION--DOU_R | NGA | ok | 26 | 2000-2025 | unit given as generic undata/UNIT_MEASURE-COUNT (likely m2 per capita; not stated) |
| 13 | undata/unicef/DM_BU_PC_DOU.URBANIZATION--DOU_R | IND | ok | 26 | 2000-2025 | |
| 13 | undata/unicef/DM_BU_PC_DOU.URBANIZATION--DOU_R | BRA | ok | 26 | 2000-2025 | |
| 14 | undata/unicef/DM_NET_MG_RATE | NGA | ok | 26 | 2000-2025 | unit given as generic UNIT_MEASURE-COUNT although name says per 1,000 population |
| 14 | undata/unicef/DM_NET_MG_RATE | IND | ok | 26 | 2000-2025 | |
| 14 | undata/unicef/DM_NET_MG_RATE | BRA | ok | 26 | 2000-2025 | |
| 15 | undata/unicef/DM_POP_DOU.URBANIZATION--DOU_R | NGA | ok | 26 | 2000-2025 | NB: rural share 18-23% is DEGURBA (GHSL) definition, far below WUP rural share |
| 15 | undata/unicef/DM_POP_DOU.URBANIZATION--DOU_R | IND | ok | 26 | 2000-2025 | |
| 15 | undata/unicef/DM_POP_DOU.URBANIZATION--DOU_R | BRA | ok | 26 | 2000-2025 | |
| 16 | undata/unicef/DM_POP_DOU_GRT.URBANIZATION--DOU_R | NGA | ok | 26 | 2000-2025 | |
| 16 | undata/unicef/DM_POP_DOU_GRT.URBANIZATION--DOU_R | IND | ok | 26 | 2000-2025 | |
| 16 | undata/unicef/DM_POP_DOU_GRT.URBANIZATION--DOU_R | BRA | ok | 26 | 2000-2025 | |
| 17 | undata/unicef/DM_POP_PROP.AGE--Y0T17 | NGA | ok | 26 | 2000-2025 | |
| 17 | undata/unicef/DM_POP_PROP.AGE--Y0T17 | IND | ok | 26 | 2000-2025 | |
| 17 | undata/unicef/DM_POP_PROP.AGE--Y0T17 | BRA | ok | 26 | 2000-2025 | |
| 18 | undata/unicef/DM_POP_PROP.AGE--Y10T19 | NGA | ok | 26 | 2000-2025 | |
| 18 | undata/unicef/DM_POP_PROP.AGE--Y10T19 | IND | ok | 26 | 2000-2025 | |
| 18 | undata/unicef/DM_POP_PROP.AGE--Y10T19 | BRA | ok | 26 | 2000-2025 | |
| 19 | undata/unicef/ECD_CHLD_LFT_ALN.AGE--Y0T4 | NGA | ok | 1 | 2021 | |
| 19 | undata/unicef/ECD_CHLD_LFT_ALN.AGE--Y0T4 | IND | no data | 0 | - | empty data{} returned |
| 19 | undata/unicef/ECD_CHLD_LFT_ALN.AGE--Y0T4 | BRA | no data | 0 | - | empty data{} returned |
| 20 | undata/unicef/ECD_CHLD_LMPSL_PRXY.AGE--M36T47 | NGA | no data | 0 | - | variable exists (name resolved) but empty data{} |
| 20 | undata/unicef/ECD_CHLD_LMPSL_PRXY.AGE--M36T47 | IND | no data | 0 | - | |
| 20 | undata/unicef/ECD_CHLD_LMPSL_PRXY.AGE--M36T47 | BRA | no data | 0 | - | |
| 21 | undata/unicef/ECD_CHLD_PLYTH_HM.AGE--Y0T4 | NGA | ok | 1 | 2021 | |
| 21 | undata/unicef/ECD_CHLD_PLYTH_HM.AGE--Y0T4 | IND | no data | 0 | - | |
| 21 | undata/unicef/ECD_CHLD_PLYTH_HM.AGE--Y0T4 | BRA | no data | 0 | - | |
| 22 | undata/unicef/ED_ROFST.EDUCATION_LEVEL--ISCED11_1__SCHOOL_AGE--L1 | NGA | ok | 1 | 2018 | only one obs with date=all (survey-based) |
| 22 | undata/unicef/ED_ROFST.EDUCATION_LEVEL--ISCED11_1__SCHOOL_AGE--L1 | IND | ok | 1 | 2016 | value 5.9000001 (float artefact) kept verbatim |
| 22 | undata/unicef/ED_ROFST.EDUCATION_LEVEL--ISCED11_1__SCHOOL_AGE--L1 | BRA | ok | 1 | 2019 | value 0.4908559 |
| 23 | undata/unicef/FD_ANAR.EDUCATION_LEVEL--ISCED11_1__SCHOOL_AGE--L1 | NGA | ok | 1 | 2018 | value 66.699997 (float32 artefact) kept verbatim |
| 23 | undata/unicef/FD_ANAR.EDUCATION_LEVEL--ISCED11_1__SCHOOL_AGE--L1 | IND | ok | 1 | 2016 | value 95.199997 (float32 artefact) |
| 23 | undata/unicef/FD_ANAR.EDUCATION_LEVEL--ISCED11_1__SCHOOL_AGE--L1 | BRA | ok | 1 | 2019 | |
| 24 | undata/unicef/FD_EARLY_CH_EDU.AGE--Y3T4__DISABILITY_STATUS--PD | NGA | ok | 1 | 2021 | |
| 24 | undata/unicef/FD_EARLY_CH_EDU.AGE--Y3T4__DISABILITY_STATUS--PD | IND | no data | 0 | - | |
| 24 | undata/unicef/FD_EARLY_CH_EDU.AGE--Y3T4__DISABILITY_STATUS--PD | BRA | no data | 0 | - | |
| 25 | undata/unicef/FD_EARLY_STIM.AGE--Y2T4__DISABILITY_STATUS--PD | NGA | ok | 1 | 2021 | integer literal 38 |
| 25 | undata/unicef/FD_EARLY_STIM.AGE--Y2T4__DISABILITY_STATUS--PD | IND | no data | 0 | - | |
| 25 | undata/unicef/FD_EARLY_STIM.AGE--Y2T4__DISABILITY_STATUS--PD | BRA | no data | 0 | - | |
| 26 | undata/unicef/FD_FOUNDATIONAL_LEARNING.AGE--Y7T14__DISABILITY_STATUS--PD | NGA | ok | 1 | 2021 | |
| 26 | undata/unicef/FD_FOUNDATIONAL_LEARNING.AGE--Y7T14__DISABILITY_STATUS--PD | IND | no data | 0 | - | |
| 26 | undata/unicef/FD_FOUNDATIONAL_LEARNING.AGE--Y7T14__DISABILITY_STATUS--PD | BRA | no data | 0 | - | |
| 27 | undata/unicef/FD_FUNC_DIFFICULTY.AGE--Y2T4__DISABILITY_STATUS--PD | NGA | ok | 1 | 2021 | |
| 27 | undata/unicef/FD_FUNC_DIFFICULTY.AGE--Y2T4__DISABILITY_STATUS--PD | IND | no data | 0 | - | |
| 27 | undata/unicef/FD_FUNC_DIFFICULTY.AGE--Y2T4__DISABILITY_STATUS--PD | BRA | no data | 0 | - | |
| 28 | undata/unicef/FD_NEVER_ATTENDED.AGE--Y10T17__DISABILITY_STATUS--PD | NGA | ok | 1 | 2021 | integer literal 24 |
| 28 | undata/unicef/FD_NEVER_ATTENDED.AGE--Y10T17__DISABILITY_STATUS--PD | IND | no data | 0 | - | |
| 28 | undata/unicef/FD_NEVER_ATTENDED.AGE--Y10T17__DISABILITY_STATUS--PD | BRA | no data | 0 | - | |
| 29 | undata/unicef/FD_OOS.AGE--L1__DISABILITY_STATUS--PD__EDUCATION_LEVEL--ISCED11_1 | NGA | ok | 1 | 2021 | |
| 29 | undata/unicef/FD_OOS.AGE--L1__DISABILITY_STATUS--PD__EDUCATION_LEVEL--ISCED11_1 | IND | no data | 0 | - | |
| 29 | undata/unicef/FD_OOS.AGE--L1__DISABILITY_STATUS--PD__EDUCATION_LEVEL--ISCED11_1 | BRA | no data | 0 | - | |
| 30 | undata/unicef/FD_SANITATION_FACILITIES.AGE--Y2T17__DISABILITY_STATUS--PD | NGA | ok | 1 | 2021 | |
| 30 | undata/unicef/FD_SANITATION_FACILITIES.AGE--Y2T17__DISABILITY_STATUS--PD | IND | no data | 0 | - | |
| 30 | undata/unicef/FD_SANITATION_FACILITIES.AGE--Y2T17__DISABILITY_STATUS--PD | BRA | no data | 0 | - | |
| 31 | undata/unicef/FD_SEVER_PHY_PUNISH.AGE--Y2T14__DISABILITY_STATUS--PD | NGA | ok | 1 | 2021 | |
| 31 | undata/unicef/FD_SEVER_PHY_PUNISH.AGE--Y2T14__DISABILITY_STATUS--PD | IND | no data | 0 | - | |
| 31 | undata/unicef/FD_SEVER_PHY_PUNISH.AGE--Y2T14__DISABILITY_STATUS--PD | BRA | no data | 0 | - | |
| 32 | undata/unicef/FD_SOCIAL_TRANSFERS.AGE--Y2T17__DISABILITY_STATUS--PD | NGA | ok | 1 | 2021 | |
| 32 | undata/unicef/FD_SOCIAL_TRANSFERS.AGE--Y2T17__DISABILITY_STATUS--PD | IND | no data | 0 | - | |
| 32 | undata/unicef/FD_SOCIAL_TRANSFERS.AGE--Y2T17__DISABILITY_STATUS--PD | BRA | no data | 0 | - | |
| 33 | undata/unicef/GN_IDX | NGA | ok | 1 | 2023 | SIGI index score labelled unit=Percent |
| 33 | undata/unicef/GN_IDX | IND | ok | 1 | 2023 | integer literal 43 |
| 33 | undata/unicef/GN_IDX | BRA | ok | 1 | 2023 | |
| 34 | undata/unicef/GN_IT_MOB_OWN | NGA | ok | 1 | 2017 | integer literal 41 |
| 34 | undata/unicef/GN_IT_MOB_OWN | IND | no data | 0 | - | |
| 34 | undata/unicef/GN_IT_MOB_OWN | BRA | ok | 9 | 2014-2022 | integer values |
| 35 | undata/unicef/GN_MTNTY_LV_BNFTS.VALUE_CATEGORY--VAL_08 | NGA | ok | 1 | 2024 | binary variable (unit CATEGORY_BINARY_TF); value 0 = No for NGA 2024; no 2022 obs for NGA |
| 35 | undata/unicef/GN_MTNTY_LV_BNFTS.VALUE_CATEGORY--VAL_08 | IND | ok | 2 | 2022-2024 | values 1 |
| 35 | undata/unicef/GN_MTNTY_LV_BNFTS.VALUE_CATEGORY--VAL_08 | BRA | ok | 2 | 2022-2024 | values 1 |
| 36 | undata/unicef/GN_PTNTY_LV_BNFTS.VALUE_CATEGORY--VAL_08 | NGA | ok | 2 | 2022-2024 | binary; values 0 |
| 36 | undata/unicef/GN_PTNTY_LV_BNFTS.VALUE_CATEGORY--VAL_08 | IND | ok | 2 | 2022-2024 | binary; values 0 |
| 36 | undata/unicef/GN_PTNTY_LV_BNFTS.VALUE_CATEGORY--VAL_08 | BRA | ok | 2 | 2022-2024 | binary; values 1 |
| 37 | undata/unicef/GN_SG_LGL_GENEQEMP | NGA | ok | 3 | 2018-2022 | biennial; integer values |
| 37 | undata/unicef/GN_SG_LGL_GENEQEMP | IND | ok | 3 | 2018-2022 | |
| 37 | undata/unicef/GN_SG_LGL_GENEQEMP | BRA | ok | 3 | 2018-2022 | |
| 38 | undata/unicef/HVA_EPI_DTH_ANN.AGE--Y0T4 | NGA | no data | 0 | - | variable resolves (name returned) but empty data{} for all three countries |
| 38 | undata/unicef/HVA_EPI_DTH_ANN.AGE--Y0T4 | IND | no data | 0 | - | |
| 38 | undata/unicef/HVA_EPI_DTH_ANN.AGE--Y0T4 | BRA | no data | 0 | - | |
| 39 | undata/unicef/HVA_EPI_DTH_ANN.AGE--Y0T14 | NGA | no data | 0 | - | empty data{} |
| 39 | undata/unicef/HVA_EPI_DTH_ANN.AGE--Y0T14 | IND | no data | 0 | - | |
| 39 | undata/unicef/HVA_EPI_DTH_ANN.AGE--Y0T14 | BRA | no data | 0 | - | |
| 40 | undata/unicef/HVA_EPI_DTH_ANN.AGE--Y15T24 | NGA | ok | 15 | 2010-2024 | rounded UNAIDS-style estimates |
| 40 | undata/unicef/HVA_EPI_DTH_ANN.AGE--Y15T24 | IND | ok | 1 | 2024 | ANOMALY: only 2024 returned with date=all (NGA has 2010-2024) |
| 40 | undata/unicef/HVA_EPI_DTH_ANN.AGE--Y15T24 | BRA | no data | 0 | - | |
| 41 | undata/unicef/HVA_EPI_DTH_RT.AGE--Y0T14 | NGA | no data | 0 | - | empty data{} |
| 41 | undata/unicef/HVA_EPI_DTH_RT.AGE--Y0T14 | IND | no data | 0 | - | |
| 41 | undata/unicef/HVA_EPI_DTH_RT.AGE--Y0T14 | BRA | no data | 0 | - | |
| 42 | undata/unicef/HVA_EPI_INF_ANN.AGE--Y0T14 | NGA | no data | 0 | - | empty data{} |
| 42 | undata/unicef/HVA_EPI_INF_ANN.AGE--Y0T14 | IND | no data | 0 | - | |
| 42 | undata/unicef/HVA_EPI_INF_ANN.AGE--Y0T14 | BRA | no data | 0 | - | |
| 43 | undata/unicef/HVA_EPI_INF_ANN.AGE--Y0T19 | NGA | no data | 0 | - | empty data{} |
| 43 | undata/unicef/HVA_EPI_INF_ANN.AGE--Y0T19 | IND | no data | 0 | - | |
| 43 | undata/unicef/HVA_EPI_INF_ANN.AGE--Y0T19 | BRA | no data | 0 | - | |
| 44 | undata/unicef/HVA_EPI_INF_RT.AGE--Y0T14 | NGA | no data | 0 | - | empty data{} |
| 44 | undata/unicef/HVA_EPI_INF_RT.AGE--Y0T14 | IND | no data | 0 | - | |
| 44 | undata/unicef/HVA_EPI_INF_RT.AGE--Y0T14 | BRA | no data | 0 | - | |
| 45 | undata/unicef/HVA_EPI_LHIV.AGE--Y0T19 | NGA | no data | 0 | - | empty data{} |
| 45 | undata/unicef/HVA_EPI_LHIV.AGE--Y0T19 | IND | no data | 0 | - | |
| 45 | undata/unicef/HVA_EPI_LHIV.AGE--Y0T19 | BRA | no data | 0 | - | |
| 46 | undata/unicef/HVA_EPI_LHIV.AGE--Y15T24 | NGA | ok | 15 | 2010-2024 | rounded estimates |
| 46 | undata/unicef/HVA_EPI_LHIV.AGE--Y15T24 | IND | ok | 1 | 2024 | ANOMALY: only 2024 returned with date=all |
| 46 | undata/unicef/HVA_EPI_LHIV.AGE--Y15T24 | BRA | no data | 0 | - | |
| 47 | undata/unicef/HVA_PED_ART_CVG.AGE--Y0T14 | NGA | no data | 0 | - | empty data{} |
| 47 | undata/unicef/HVA_PED_ART_CVG.AGE--Y0T14 | IND | no data | 0 | - | |
| 47 | undata/unicef/HVA_PED_ART_CVG.AGE--Y0T14 | BRA | no data | 0 | - | |
| 48 | undata/unicef/HVA_PED_ART_NUM.AGE--Y0T14 | NGA | no data | 0 | - | empty data{} |
| 48 | undata/unicef/HVA_PED_ART_NUM.AGE--Y0T14 | IND | no data | 0 | - | |
| 48 | undata/unicef/HVA_PED_ART_NUM.AGE--Y0T14 | BRA | no data | 0 | - | |
| 49 | undata/unicef/HVA_PED_EID_CVG.AGE--Y0 | NGA | no data | 0 | - | empty data{} (NGA usually has EID coverage; absent here) |
| 49 | undata/unicef/HVA_PED_EID_CVG.AGE--Y0 | IND | ok | 1 | 2024 | integer literal 67 |
| 49 | undata/unicef/HVA_PED_EID_CVG.AGE--Y0 | BRA | no data | 0 | - | |
| 50 | undata/unicef/HVA_PED_EID_NUM.AGE--Y0 | NGA | no data | 0 | - | empty data{} |
| 50 | undata/unicef/HVA_PED_EID_NUM.AGE--Y0 | IND | ok | 1 | 2024 | |
| 50 | undata/unicef/HVA_PED_EID_NUM.AGE--Y0 | BRA | no data | 0 | - | |
| 51 | undata/unicef/HVA_PED_LOST.AGE--Y0T17 | NGA | ok | 15 | 2010-2024 | rounded estimates |
| 51 | undata/unicef/HVA_PED_LOST.AGE--Y0T17 | IND | no data | 0 | - | |
| 51 | undata/unicef/HVA_PED_LOST.AGE--Y0T17 | BRA | no data | 0 | - | |
| 52 | undata/unicef/HVA_PED_LOST_AIDS.AGE--Y0T17 | NGA | ok | 15 | 2010-2024 | rounded estimates |
| 52 | undata/unicef/HVA_PED_LOST_AIDS.AGE--Y0T17 | IND | no data | 0 | - | |
| 52 | undata/unicef/HVA_PED_LOST_AIDS.AGE--Y0T17 | BRA | no data | 0 | - | |

## Summary

- Calls: 156 (52 variables x 3 countries), all returned HTTP-level success; 93 returned observations, 63 returned empty `data{}` (written as one row with year="" value="" notes="no observations").
- CSV rows written: 1335 data lines (1272 observation rows + 63 no-observation rows) + header.
- All responses came in the tabular shape (`data.columns`/`data.rows`), none in `placeObservations`. No `alternativeSources` field was present in any response (column left empty).
- Verified: every (dcid, country) pair present exactly once per date; no duplicate (dcid, iso3, year); all values numeric literals as returned; 7 random spot checks against the raw responses match.

### Variables with no data in any of the three countries (10)
ECD_CHLD_LMPSL_PRXY.AGE--M36T47; HVA_EPI_DTH_ANN.AGE--Y0T4; HVA_EPI_DTH_ANN.AGE--Y0T14; HVA_EPI_DTH_RT.AGE--Y0T14; HVA_EPI_INF_ANN.AGE--Y0T14; HVA_EPI_INF_ANN.AGE--Y0T19; HVA_EPI_INF_RT.AGE--Y0T14; HVA_EPI_LHIV.AGE--Y0T19; HVA_PED_ART_CVG.AGE--Y0T14; HVA_PED_ART_NUM.AGE--Y0T14.
(All resolve to a named StatisticalVariable, so the DCIDs exist; the country-level series are simply not loaded, which is suspicious for the HIV paediatric block, where NGA at least should have UNAIDS estimates.)

### Partial coverage (18)
- NGA only: ECD_CHLD_LFT_ALN, ECD_CHLD_PLYTH_HM, all nine FD_* disability variables, HVA_PED_LOST, HVA_PED_LOST_AIDS (single 2021 MICS point for ECD/FD; 2010-2024 for HVA_PED_LOST*).
- NGA+IND only: HVA_EPI_DTH_ANN.AGE--Y15T24, HVA_EPI_LHIV.AGE--Y15T24 (IND has only 2024 while NGA has 2010-2024).
- IND only: HVA_PED_EID_CVG.AGE--Y0, HVA_PED_EID_NUM.AGE--Y0 (2024 only).
- NGA+BRA only: GN_IT_MOB_OWN (NGA 2017; BRA 2014-2022).

### Anomalies
1. CME_PND (neonatal share of under-five deaths): unit labelled "Percent" but all values are fractions in 0-1 (e.g. NGA 2024 = 0.344763672231078). Flagged in `notes`.
2. Float32 artefacts kept verbatim: ED_ROFST IND 2016 = 5.9000001; FD_ANAR NGA 2018 = 66.699997, IND 2016 = 95.199997.
3. CME_MR.AGE--Y0 and CME_TM.AGE--Y0 for BRA show a 2016 bump (IMR 14.579 vs 13.72 in 2015 and 13.27 in 2017; deaths 42432) that breaks the monotone trend; returned as-is.
4. `date="all"` returned a single observation for several variables (CME_ARR*, CME_ARR_SBR, ED_ROFST, FD_ANAR, ECD/FD survey indicators, GN_IDX, HIV IND 2024 points) although some clearly have longer histories elsewhere (e.g. IND HIV 15-24 only 2024 while NGA has 2010-2024).
5. Unit strings are heterogeneous: plain "Percent" vs DCID-style strings such as undata/UNIT_MEASURE-RATIO_COUNT_DEATHS_PER_1000_COUNT_LIVEBIRTHS, undata/UNIT_MEASURE-COUNT (generic, used even for DM_NET_MG_RATE "per 1,000" and DM_BU_PC_DOU built-up area per capita), undata/UNIT_MEASURE-CATEGORY_BINARY_TF (GN_*_LV_BNFTS, values 0/1).
6. DM_POP_DOU rural share (DEGURBA definition) is 16-23% for all three countries, much lower than the WUP "rural" share; definitional, not an error.
7. Numerous integer-literal values (e.g. CME_ARR_SBR IND = 4, GN_IDX IND = 43, FD_EARLY_STIM NGA = 38) are stored exactly as returned (no ".0").
8. Provenance URL is the generic https://data.unicef.org/ for every facet; facet ids differ by dataset (15005650441306304968 for most Percent series; 15394015532395128522 / 16059553784243044970 / 14452878761585262522 / 15697043862166702755 for the four CME_MR age groups; 1907673203465659357 CME_TM; 9589496361978137601 DM_BRTS*; 1896065916138908710 COUNT-type series; 8712313410891279707 binary GN leave benefits).
