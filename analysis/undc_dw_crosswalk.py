"""UN DC (undata/unicef/<CODE>.<DIM>--<code>__...) -> UNICEF SDMX warehouse code + required dimension codes. Shared by the comparison and universe scripts."""
def parse_dims(v):
    d = {}
    for part in v.split('__') if v else []:
        if '--' in part:
            k, val = part.split('--', 1); d[k] = val
    return d

# ---------------------------------------------------------------- crosswalk: UN DC code + variant dims -> (UNICEF code, required DW dimension codes)
WASH_SUFFIX = {"ALB": "ALB", "B": "B", "L": "L", "N": "N", "SM": "SM", "I": "I", "UI": "UI", "LAT": "LAT", "SEP": "SEP", "SEW": "SEW", "SEW_WWT": "SEW",
               "ONSITE_DIS": "DIS", "ONSITE_FST": "FST", "I_NP": "NP", "I_P": "P", "I_PRE": "PRE", "I_QUA": "QUA", "I_AVA": "AVA"}
RENAMED = {"IM_PCV3": "IM_PCVC"}   # code retired/renamed in the warehouse (PCV last dose) — UN DC still carries the old code
NOTES = {}
def map_code(code, dims, known_codes):
    """returns (unicef_code, req) — req: DW dimension -> code that the matched row must carry (besides totals elsewhere)"""
    age, sex = dims.get("AGE", ""), dims.get("SEX", "")
    req = {}
    if age: req["AGE"] = age
    if sex: req["SEX"] = sex
    if code in ("CME_MR", "CME_TM"):
        return code + age, {}
    if code == "CME_ARR":
        return {"Y0T4": "CME_ARR_U5MR", "Y10T19": "CME_ARR_10T19"}.get(age, "?"), {}
    if code == "DM_POP":
        return {"": "DM_POP_TOT", "Y0T4": "DM_POP_U5", "Y0T17": "DM_POP_U18", "Y10T19": "DM_POP_ADLCNT", "Y15T24": "DM_POP_15TO24"}.get(age, "?"), {}
    if code == "DM_POP_PROP":
        return {"Y0T17": "DM_POP_CHILD_PROP", "Y10T19": "DM_POP_ADLCNT_PROP"}.get(age, "?"), {}
    if code.startswith("DM_") and "URBANIZATION" in dims:
        return code, {"RESIDENCE": {"U": "U", "DOU_R": "R", "DOU_U": "U", "DOU_CITY": "CITY", "DOU_TSUB": "TSUB"}.get(dims["URBANIZATION"], dims["URBANIZATION"])}
    ecd = {"ECD_CHLD_ADLT_SRC": "ECD_CHLD_24-59M_ADLT_SRC", "ECD_CHLD_BKS_HM": "ECD_CHLD_U5_BKS-HM", "ECD_CHLD_EDU_PGM": "ECD_CHLD_36-59M_EDU-PGM",
           "ECD_CHLD_LFT_ALN": "ECD_CHLD_U5_LFT-ALN", "ECD_CHLD_PLYTH_HM": "ECD_CHLD_U5_PLYTH-HM", "ED_LR": "ED_15-24_LR", "NT_ANE": "NT_ANE_WOM_15_49_MOD",
           "PT_ADLS_LBR_HC": "PT_ADLS_10-14_LBR_HC", "PT_CHLD_LBR_ECON": "PT_CHLD_5-17_LBR_ECON", "PT_CHLD_LBR_ECON_HC": "PT_CHLD_5-17_LBR_ECON-HC",
           "PT_CHLD_PS_PSY_V_CGVR": "PT_CHLD_1-14_PS-PSY-V_CGVR", "PT_CHLD_REG": "PT_CHLD_Y0T4_REG", "PT_CHLD_RES_CARE": "PT_CHLD_RES-CARE",
           "PT_F_MRD_U15_TND": "PT_F_20-24_MRD_U15_TND", "PT_F_MRD_U18_TND": "PT_F_20-24_MRD_U18_TND", "PT_ST_BUL_30_DYS": "PT_ST_13-15_BUL_30-DYS",
           "PV_CHLD_DPRV_AVG_HS": "PV_CHLD_DPRV-AVG-HS", "PV_CHLD_DPRV_AVG_S_HS": "PV_CHLD_DPRV-AVG-S-HS", "PV_CHLD_DPRV_AVG_POV_HS": "PV_CHLD_DPRV-AVG-POV-HS",
           "PV_CHLD_DPRV_AVG_POV_S_HS": "PV_CHLD_DPRV-AVG-POV-S-HS", "PV_CHLD_INCM_PL": "PV_CHLD_INCM-PL", "WS_PPL_M_NPART": "WS_PPL_M-NPART_AGE_15_19",
           "WT_ADLS_ED_NEET": "WT_ADLS_15-19_ED_NEET", "WT_ADLS_LAB_FRC_UNEMP": "WT_ADLS_15-19_LAB_FRC_UNEMP", "WS_PPL_W_SW": "WS_PPL_W-SW", "WS_PPL_S_OD": "WS_PPL_S-OD"}
    if code in ecd:
        return ecd[code], {}
    if code in ("ECON_GVT_EXP_PTEXP", "ECON_GVT_EXP_PTGDP"):
        gf = dims.get("GOVERNMENT_FUNCTION", ""); suf = code[-5:]
        return {"COFOG99_09": f"ECON_GVT_EDU_EXP_{suf}", "COFOG99_07": f"ECON_GVT_HLTH_EXP_{suf}", "COFOG99_10": f"ECON_SOC_PRO_EXP_{suf}", "": code}.get(gf, "?"), {}
    if code in ("ED_CR", "ED_ROFST", "ED_ROFST_ADM", "ED_MAT", "ED_READ"):
        lvl = dims.get("EDUCATION_LEVEL", ""); L = {"ISCED11_02": "L02", "ISCED11_1": "L1", "ISCED11_2": "L2", "ISCED11_3": "L3", "GRAD23": "G23"}.get(lvl, "?")
        base = {"ED_CR": "ED_CR_", "ED_ROFST": "ED_ROFST_", "ED_ROFST_ADM": "ED_ROFST_", "ED_MAT": "ED_MAT_", "ED_READ": "ED_READ_"}[code]
        return base + L + ("_ADM" if code == "ED_ROFST_ADM" else ""), {}
    if code == "FD_ANAR" and "DISABILITY_STATUS" not in dims:   # UN DC's FD_ANAR rows hold the all-children ANAR series (ED_ANAR_L*) — label error in UN DC
        return "ED_ANAR_" + dims.get("SCHOOL_AGE", "?"), {"EDUCATION_LEVEL": dims.get("EDUCATION_LEVEL", "")}
    if code == "FD_ANAR":
        return code, {"EDUCATION_LEVEL": dims.get("EDUCATION_LEVEL", ""), "AGE": {"L1": "PRY_SCHOOL_AGE", "L2": "LSRY_SCHOOL_AGE", "L3": "USRY_SCHOOL_AGE"}.get(dims.get("SCHOOL_AGE", ""), "?")}
    if code == "FD_OOS":   # UN DC puts the school-age level in AGE ("L1")
        return code, {"EDUCATION_LEVEL": dims.get("EDUCATION_LEVEL", ""), "DISABILITY_STATUS": dims.get("DISABILITY_STATUS", "PD"),
                      "AGE": {"L1": "PRY_SCHOOL_AGE", "L2": "LSRY_SCHOOL_AGE", "L3": "USRY_SCHOOL_AGE"}.get(age, age)}
    if code == "IM_MCV2":
        return code, {"AGE": "Y02"} if age == "Y2" else req
    if code == "FD_FUNC_DIFFICULTY":
        return code, {"AGE": age, "DISABILITY_STATUS": dims.get("DISABILITY_STATUS", "PD")}
    if code == "GN_ED_ATTN":        # UN DC age 25+ is the DW's only age (_T)
        return code, {"SEX": sex} if sex else {}
    if code in ("GN_LF_PTCPN", "GN_UNMPLY", "GN_TIMEUSE"):
        return code, {k: v for k, v in (("AGE", age), ("SEX", sex)) if v}
    if code == "IM_VACC":
        vac = "IM_" + dims.get("VACCINE", "?")
        return RENAMED.get(vac, vac), {}
    if code.startswith("MG_"):
        sp = dims.get("STATISTICAL_POPULATION", "")
        return code, {"STAT_POP": sp or "_T", "AGE": age or "_T"}
    if code == "MNCH_DIARRHOEAT_TR":
        return {"ORS": "MNCH_ORS", "ORSZINC": "MNCH_ORSZINC", "ORT": "MNCH_ORTCF", "ZINC": "MNCH_ZINC"}.get(dims.get("DIARRHOEA_TREATMENT", ""), "?"), {}
    if code == "NT_BF_CBF":
        return {"": "NT_BF_CBF_12_23", "M12T23": "NT_BF_CBF_12_23", "M12T15": "NT_BF_CBF_12_15", "M20T23": "NT_BF_CBF_20_23"}.get(age, "?"), {}
    if code.startswith("PT_CM_"):   # DW codes these women-only indicators SEX=_T
        return code, {"AGE": age, "CH_MARRIAGE_STATUS": dims.get("MARITAL_STATUS", "_T")}
    if code == "PT_FGM_ELIM":
        return ("PT_F_15-49_FGM_ELIM" if sex == "F" else "PT_M_15-49_FGM_ELIM") if age == "Y15T49" else "?", {}
    if code == "PT_F_FGM":
        return {"Y15T49": "PT_F_15-49_FGM", "Y0T14": "PT_F_0-14_FGM"}.get(age, "?"), {}
    if code == "PT_F_MRD_U15":
        return {"Y20T24": "PT_F_20-24_MRD_U15", "Y45T49": "PT_F_45-49_MRD_U15"}.get(age, "?"), {}
    if code == "PT_MRD":
        return ("PT_F_15-19_MRD" if sex == "F" else "PT_M_15-19_MRD") if age == "Y15T19" else "?", {}
    if code == "PT_MRD_U18":
        if age == "" and sex == "F": return "PT_F_TMRD18", {}
        return ({"Y20T24": "PT_F_20-24_MRD_U18", "Y45T49": "PT_F_45-49_MRD_U18"}.get(age, "?") if sex == "F" else "?"), {}
    if code == "PT_SXV_AGE18":
        return ("PT_F_18-29_SX-V_AGE-18" if sex == "F" and age == "Y18T29" else "?"), {}
    if code == "PT_W_BTNG":
        return ({"F": "PT_F_15-49_W-BTNG", "M": "PT_M_15-49_W-BTNG"}.get(sex, "?") if age == "Y15T49" else "?"), {}
    if code == "PV_ADOLESCENT":
        return code, {"SEX": sex} if sex else {}
    if code in ("PV_CHLD_DEPRV_M", "PV_CHLD_DEPRV_S"):
        n = dims.get("NUMBER_OF_DEPRIVATIONS", ""); s = "S-" if code.endswith("_S") else ""
        return (f"PV_CHLD_DPRV-{s}{n}-HS" if n else "?"), {}
    if code.startswith("SPP_"):
        r = {}
        if "WEALTH_QUANTILE" in dims: r["WEALTH_QUINTILE"] = dims["WEALTH_QUANTILE"]
        if "POVERTY_THRESHOLD" in dims: r["POV_THRESHOLD"] = {"D_1": "S1", "D_2": "S2", "D_3": "S3", "D_4": "S4_MORE"}.get(dims["POVERTY_THRESHOLD"], dims["POVERTY_THRESHOLD"])
        return code, r
    if code.startswith("WS_") and "WASH_SERVICE" in dims:
        ws = dims["WASH_SERVICE"]; pref, _, suf = ws.partition("_")
        stem = {"WS_HCF_H": "WS_HCF_H", "WS_HCF_S": "WS_HCF_S", "WS_HCF_W": "WS_HCF_W", "WS_HCF_WM": "WS_HCF_WM", "WS_HCF_C": "WS_HCF_C",
                "WS_PPL_HF_HANDWASH": "WS_PPL_H", "WS_PPL_S": "WS_PPL_S", "WS_PPL_SF": "WS_PPL_S", "WS_PPL_W_DW": "WS_PPL_W", "WS_PPL_W_DWSR": "WS_PPL_W",
                "WS_SCH_H": "WS_SCH_H", "WS_SCH_S": "WS_SCH_S", "WS_SCH_W_DW": "WS_SCH_W"}.get(code)
        if stem: return f"{stem}-{WASH_SUFFIX.get(suf, suf)}", {}
    if code in known_codes:
        return code, req
    return "?", {}

