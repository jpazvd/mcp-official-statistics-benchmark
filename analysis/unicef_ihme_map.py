"""Map the 247 UNICEF indicator codes (UN DC) to IHME GBD 2023 constructs served by the IHME MCP tools.
Rule-based with explicit overrides; output ../universe/out/unicef_ihme_mapping.csv and summary by dataflow."""
import pandas as pd
from pathlib import Path
U = Path(__file__).resolve().parent.parent / "universe"
codes = pd.read_csv(U / "undc_unicef_codes.csv", dtype=str).fillna("")

SAME = {  # same statistical construct (independent GBD model) -> comparable with caveats
 "CME_MR": "get_mortality_probability / get_child_mortality_trend (5q0, neonatal, <1 year, 1-4, 5-9, 10-14, 15-19, 20-24, 5-14, 10-19, 10-24 bands; no 1-59-month band)",
 "CME_TM": "get_cause_burden(measure=deaths, all causes, by age band) — death counts",
 "CME_SB": "get_fertility(measure=stillbirth_count, wk_cutoff=28)", "CME_SBR": "get_fertility(measure=stillbirth_rate, wk_cutoff=28)",
 "DM_POP": "get_population", "DM_BRTS": "get_population(measure=live_births)", "DM_POP_PROP": "get_population(age_group=...) — shares derivable, not published",
 "DM_FRATE_TOT": "get_fertility(measure=tfr)", "DM_LIFE_EXP": "get_life_expectancy", "DM_NET_MG_RATE": "get_population(measure=migration) — count not rate, sparse",
 "MNCH_ABR": "get_fertility(measure=asfr, 15-19)", "MNCH_MMR": "get_mmr (GBD definition incl. late and HIV-aggravated deaths)",
 "MNCH_MATERNAL_DEATHS": "get_cause_burden(Maternal disorders, deaths) — count", "MNCH_LIFE_EXPECTANCY": "get_life_expectancy (female)",
 "MNCH_ANC1": "get_covariate(ANC1 coverage)", "MNCH_ANC4": "get_covariate(ANC4 coverage)", "MNCH_SAB": "get_covariate(Skilled Birth Attendance)",
 "MNCH_INSTDEL": "get_covariate(In-Facility Delivery)", "MNCH_INSTDEL_TND": "get_covariate(In-Facility Delivery)", "MNCH_PNCMOM": "get_covariate(Postnatal Care Visit)",
 "MNCH_DEMAND_FP": "get_covariate(Demand for contraception satisfied with modern methods)", "MNCH_UHC": "get_covariate(Universal health coverage index)",
 "IM_VACC": "get_covariate: DTP3, MCV1, Polio3, Hib3, PCV3, RotaC, HepB3, RCV1 (not DTP1, IPV1-3, MenA)", "IM_MCV2": "get_covariate(MCV2)", "IM_BCG": "get_covariate(BCG lagged five-year coverage)",
 "NT_ANE": "get_impairment(Anemia, females 15-49) — GBD impairment model vs WHO model",
 "HVA_EPI_DTH_ANN": "get_cause_burden(HIV/AIDS, deaths, by age band) — GBD model vs UNAIDS", "HVA_EPI_DTH_RT": "get_cause_burden(HIV/AIDS, deaths rate)",
 "HVA_EPI_INF_ANN": "get_cause_burden(HIV/AIDS, incidence count)", "HVA_EPI_INF_RT": "get_cause_burden(HIV/AIDS, incidence per 100,000 total pop; UNAIDS per 1,000 uninfected)",
 "HVA_EPI_LHIV": "get_cause_burden(HIV/AIDS, prevalence count, 0-14)",
 "NT_DANT_BMI_G25_MOD": "get_risk_exposure(High body-mass index, adults) — series 52-54 overweight/obese", "NT_DANT_BMI_G30_MOD_ADJ": "get_risk_exposure(High body-mass index) obese series",
}
RELATED = {  # GBD publishes a different construct of the same phenomenon
 "NT_ANT_HAZ_NE2": "get_risk_exposure(Child stunting) 3 severity categories x age bands; no 0-59-month <-2 SD aggregate", "NT_ANT_HAZ_NE2_MOD": "as NT_ANT_HAZ_NE2", "NT_ANT_HAZ_NE2_MOD_NUMTH": "exposure x population, not published",
 "NT_ANT_WHZ_NE2": "get_risk_exposure(Child wasting) categories", "NT_ANT_WHZ_NE3": "get_risk_exposure(Child wasting) < -3 SD category", "NT_ANT_WAZ_NE2": "get_risk_exposure(Child underweight) categories",
 "NT_ANT_WHZ_PO2": "get_risk_exposure(High body-mass index) child bands — IOTF-type cut-offs, not WHZ > +2 SD", "NT_ANT_WHZ_PO2_MOD": "as NT_ANT_WHZ_PO2", "NT_ANT_WHZ_PO2_MOD_NUMTH": "not published",
 "NT_BW_LBW": "get_risk_exposure(Low birth weight and short gestation) joint 58-category distribution", "NT_BW_WEI": "as NT_BW_LBW",
 "NT_BF_EXBF": "get_risk_exposure(Suboptimal breastfeeding) non-exclusive categories 1-5 months", "NT_BF_CBF": "get_risk_exposure(Suboptimal breastfeeding) discontinued breastfeeding 6-23 months",
 "NT_BF_EIBF": "none for early initiation; suboptimal breastfeeding covers exclusivity only", "NT_BF_MIXMF": "non-exclusive partial category", "NT_BF_EBF": "discontinued breastfeeding (ever breastfed differs)",
 "NT_SANT_5_19_BAZ_NE2_MOD": "no thinness exposure; High BMI child bands only", "NT_SANT_5_19_BAZ_PO1_MOD": "get_risk_exposure(High body-mass index) 5-19 bands", "NT_SANT_5_19_BAZ_PO2_MOD": "get_risk_exposure(High body-mass index) obese 5-19 bands",
 "NT_VAS_S1": "get_risk_exposure(Vitamin A deficiency) — deficiency prevalence, not supplementation coverage", "NT_VAS_S2": "as NT_VAS_S1", "NT_VAS_TWODOSE": "as NT_VAS_S1",
 "WS_PPL_W_DW": "get_risk_exposure(Unsafe water source) 11 source x treatment categories", "WS_PPL_W_DWSR": "as WS_PPL_W_DW", "WS_PPL_W_SW": "unsafe water: surface water category",
 "WS_PPL_S": "get_risk_exposure(Unsafe sanitation) 2 categories", "WS_PPL_SF": "as WS_PPL_S", "WS_PPL_S_OD": "unsafe sanitation: no facility category", "WS_PPL_HF_HANDWASH": "get_risk_exposure(No access to handwashing facility) — complement",
 "PT_F_PS-SX_V_PTNR_12MNTH": "get_risk_exposure(Intimate partner violence) — lifetime, all ages", "PT_CM_IPV_12M": "as PT_F_PS-SX_V_PTNR_12MNTH", "PT_SXV_AGE18": "get_risk_exposure(Sexual violence against children)", "PT_ST_BUL_30_DYS": "get_risk_exposure(Bullying victimization)",
 "MNCH_ADO_TOBACCO": "get_risk_exposure(Smoking / Chewing tobacco) prevalence by age band 10-14, 15-19", "MNCH_ADO_INSUFF_PHYS": "get_risk_exposure(Low physical activity) — adults 25+ only",
 "CME_PND": "derivable from neonatal and under-5 deaths; not published", "DM_DPR_CHD": "derivable from population by age; not published", "DM_DPR_OLD": "as DM_DPR_CHD", "DM_DPR_TOT": "as DM_DPR_CHD",
 "DM_BRTS_SURVIVING_1": "derivable from live births and <1 mortality; not published", "DM_POP_GRT": "derivable from population series", "MNCH_UHC_RMNCH": "UHC index only (no RMNCH sub-index)",
 "ECON_GVT_EXP_PTGDP": "none (LDI per capita is the only economic covariate)", "GN_ED_ATTN": "get_covariate(Education years per capita) — mean years, not attainment share",
}
rows = []
for _, r in codes.iterrows():
    c = r.indicator_code
    if c in SAME: cls, how = "same construct (independent GBD estimate)", SAME[c]
    elif c in RELATED: cls, how = "related construct", RELATED[c]
    else: cls, how = "none", ""
    rows.append(dict(indicator_code=c, dataflow=r.dataflow, undc_name=r.undc_name, ihme_class=cls, ihme_construct=how))
m = pd.DataFrame(rows)
m.to_csv(U / "out" / "unicef_ihme_mapping.csv", index=False)
s = m.groupby("dataflow").ihme_class.value_counts().unstack(fill_value=0)
s["n_codes"] = s.sum(axis=1); s.loc["TOTAL"] = s.sum()
s.to_csv(U / "out" / "ihme_mapping_summary.csv")
print(s.to_string())
