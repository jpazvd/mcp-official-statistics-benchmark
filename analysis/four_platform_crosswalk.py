"""
Round-1 crosswalk concepts (child/women/family indicators common to UN DC, Data360, IHME) extended with the UNICEF SDMX warehouse (via MCP)
for the three countries covered by the warehouse extraction (NGA, IND, BRA).
Inputs : harmonized_long.csv (UN DC / Data360 / IHME, harmonised units), ../unicefmcp/series_all.csv (+ supplement)
Outputs: ../unicefmcp/out/crosswalk_four_platforms_long.csv, crosswalk_dw_agreement.csv, crosswalk_dw_latest.csv
Run    : python3 -I four_platform_crosswalk.py
"""
import json
import numpy as np, pandas as pd
from pathlib import Path
A = Path(__file__).resolve().parent; M = A.parent / "unicefmcp"; OUT = M / "out"
h = pd.read_csv(A / "harmonized_long.csv", dtype=str, keep_default_na=False)
h = h[h.variant.isin(["headline", ""]) | (h.variant == "headline")] if "variant" in h.columns else h
h["v"] = pd.to_numeric(h.value, errors="coerce"); h["yr"] = h.year.str[:4]
h = h[h.iso3.isin(["NGA", "IND", "BRA"])]
DW = {  # concept -> (warehouse code, flow, required dims)
 "u5mr": ("CME_MRY0T4", "CME", {}), "nmr": ("CME_MRM0", "CME", {}), "imr": ("CME_MRY0", "CME", {}), "sbr": ("CME_SBR", "CME", {}),
 "mmr": ("MNCH_MMR", "MNCH", {}), "abr": ("MNCH_ABR", "MNCH", {"AGE": "Y15T19"}), "tfr": ("DM_FRATE_TOT", "DM", {}), "le0": ("DM_LIFE_EXP", "DM", {}),
 "dtp3": ("IM_DTP3", "IMMUNISATION", {}), "mcv1": ("IM_MCV1", "IMMUNISATION", {}), "mcv2": ("IM_MCV2", "IMMUNISATION", {"AGE": "Y02"}),
 "sba": ("MNCH_SAB", "MNCH", {"AGE": "Y15T49"}), "anc1": ("MNCH_ANC1", "MNCH", {"AGE": "Y15T49"}), "anc4": ("MNCH_ANC4", "MNCH", {"AGE": "Y15T49"}), "fp_mod": ("MNCH_DEMAND_FP", "MNCH", {"AGE": "Y15T49"}),
 "anem_w": ("NT_ANE_WOM_15_49_MOD", "NUTRITION", {}), "stunt": ("NT_ANT_HAZ_NE2_MOD", "NUTRITION", {}), "wast": ("NT_ANT_WHZ_NE2", "NUTRITION", {}),
 "ovwt": ("NT_ANT_WHZ_PO2_MOD", "NUTRITION", {}), "lbw": ("NT_BW_LBW", "NUTRITION", {}), "ebf": ("NT_BF_EXBF", "NUTRITION", {}),
 "ipv": ("PT_F_PS-SX_V_PTNR_12MNTH", "PT", {"AGE": "Y15T49"}), "pop_u5": ("DM_POP_U5", "DM", {}), "chmar": ("PT_F_20-24_MRD_U18", "PT_CM", {"AGE": "Y20T24"}),
 "breg": ("PT_CHLD_Y0T4_REG", "PT", {"AGE": "Y0T4"}), "chlab": ("PT_CHLD_5-17_LBR_ECON", "PT", {"AGE": "Y5T17"}), "fgm": ("PT_F_15-49_FGM", "PT_FGM", {"AGE": "Y15T49"}),
}
s = pd.concat([pd.read_csv(M / "series_all.csv", dtype=str, keep_default_na=False), pd.read_csv(M / "supplement" / "series_supplement.csv", dtype=str, keep_default_na=False)])
s["flow"] = s.flowRef.str.split("/").str[1]; s["d"] = s.dims_json.map(lambda t: json.loads(t) if t else {}); s["yr"] = s.time_period.str[:4]
s["x"] = s.extra_attrs_json.map(lambda t: json.loads(t) if t else {}); s["mult"] = pd.to_numeric(s.x.map(lambda x: x.get("UNIT_MULTIPLIER", "0")), errors="coerce").fillna(0)
IGN = {"DATA_SOURCE", "VACCINE", "UNIT_MEASURE"}
rows = []
for k, (code, flow, req) in DW.items():
    d = s[(s.indicator == code) & (s.flow == flow)]
    for r in d.itertuples(index=False):
        dd = r.d
        if any(dd.get(a) != b for a, b in req.items()): continue
        if any(v not in ("_T", "") for a, v in dd.items() if a not in req and a not in IGN and a != "AGE"): continue
        if "AGE" not in req and dd.get("AGE", "_T") not in ("_T", "") and len({x.get("AGE") for x in d.d}) > 1: continue
        val = pd.to_numeric(r.value, errors="coerce") * (10.0 ** r.mult)
        rows.append(dict(platform="UNICEF_SDMX_warehouse", indicator_key=k, platform_indicator_id=f"{flow}/{code}", iso3=r.iso3, year=r.yr, v=val,
                         lower=r.lower_bound, upper=r.upper_bound, obs_status=r.obs_status, data_source=r.data_source))
dw = pd.DataFrame(rows).drop_duplicates(["indicator_key", "iso3", "year"])
dw["source"] = dw.data_source
allp = pd.concat([h[["platform", "indicator_key", "platform_indicator_id", "iso3", "yr", "v"]].rename(columns={"yr": "year"}), dw[["platform", "indicator_key", "platform_indicator_id", "iso3", "year", "v"]]], ignore_index=True)
allp.to_csv(OUT / "crosswalk_four_platforms_long.csv", index=False)
def rel(a, b):
    with np.errstate(divide="ignore", invalid="ignore"): r = 100 * (a - b) / ((a + b) / 2)
    return np.where((a == 0) & (b == 0), 0.0, r)
out = []
for plat in ["UN_DataCommons", "WorldBank_Data360", "IHME_GBD2023"]:
    o = h[h.platform == plat][["indicator_key", "iso3", "yr", "v"]].rename(columns={"yr": "year", "v": "other"})
    j = dw.merge(o, on=["indicator_key", "iso3", "year"], how="inner"); j["rel"] = rel(j.v.values, j.other.values)
    for k, g in j.groupby("indicator_key"):
        ad = g.rel.abs()
        out.append(dict(indicator_key=k, vs=plat, n_pairs=len(g), share_within_1pct=(ad <= 1).mean(), share_within_5pct=(ad <= 5).mean(), median_abs_rel_pct=ad.median(), max_abs_rel_pct=ad.max(),
                        years=f"{g.year.min()}-{g.year.max()}"))
ag = pd.DataFrame(out)
ag["verdict"] = np.where(ag.share_within_1pct == 1, "identical (within 1%)", np.where(ag.share_within_5pct >= 0.9, "rounding / minor", "different series or vintage"))
ag.to_csv(OUT / "crosswalk_dw_agreement.csv", index=False)
lat = allp.groupby(["indicator_key", "platform"]).year.max().unstack()
lat.to_csv(OUT / "crosswalk_dw_latest.csv")
print(ag.pivot(index="indicator_key", columns="vs", values="verdict").to_string())
print(ag.groupby("vs").verdict.value_counts().unstack(fill_value=0).to_string())
print(lat.to_string())
print("DW concepts with data:", dw.indicator_key.nunique(), "obs:", len(dw), "| with bounds:", (dw.lower != "").mean().round(2))
