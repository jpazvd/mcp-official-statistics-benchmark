"""
UN DC UNICEF variables vs the UNICEF SDMX MCP (sdmx.data.unicef.org) — code crosswalk, value fidelity, vintage/revisions.
Also Data360 vs UNICEF MCP for the 117 UN DC–Data360 pairs.
Inputs : ../universe/values_unicef_undc_*.csv (UN DC, verbatim), ../unicefmcp/series_all.csv + ../unicefmcp/supplement/series_supplement.csv
         (UNICEF MCP, verbatim), ../universe/values_unicef_d360_*.csv, ../unicefmcp/codelist_unicef_indicator.csv
Outputs: ../unicefmcp/out/undc_vs_mcp_paired.csv, undc_vs_mcp_by_variable.csv, undc_vs_mcp_vintage.csv, undc_vs_mcp_summary.csv,
         d360_vs_mcp_paired.csv, d360_vs_mcp_by_indicator.csv
Run    : python3 -I unicef_mcp_compare.py
"""
import json, glob
import numpy as np, pandas as pd
from pathlib import Path
import sys; sys.path.insert(0, str(Path(__file__).resolve().parent))   # allow -I runs

ROOT = Path(__file__).resolve().parent.parent
U, M = ROOT / "universe", ROOT / "unicefmcp"
OUT = M / "out"; OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------- UN DC values (all 247 codes)
undc = pd.concat([pd.read_csv(f, dtype=str, keep_default_na=False) for f in sorted(glob.glob(str(U / "values_unicef_undc_*.csv")))], ignore_index=True)
undc = undc[(undc.year != "") & (undc.value != "")].copy()
undc["code"] = undc.undc_dcid_queried.str.replace("undata/unicef/", "", regex=False).str.split(".").str[0]
undc["variant"] = undc.undc_dcid_queried.str.split(".", n=1).str[1].fillna("")
from undc_dw_crosswalk import parse_dims
undc["dims"] = undc.variant.map(parse_dims)
undc["yr"] = undc.year.str[:4]
undc["v"] = pd.to_numeric(undc.value, errors="coerce")

# ---------------------------------------------------------------- UNICEF MCP series (totals extraction + targeted breakdown supplement)
mcp = pd.concat([pd.read_csv(M / "series_all.csv", dtype=str, keep_default_na=False),
                 pd.read_csv(M / "supplement" / "series_supplement.csv", dtype=str, keep_default_na=False)], ignore_index=True)
mcp = mcp[~mcp.flowRef.str.contains("SUBNAT|CME_SUBNATIONAL|MG_FLOW")].drop_duplicates(["flowRef", "indicator", "iso3", "dims_json", "time_period"]).copy()
mcp["flow"] = mcp.flowRef.str.split("/").str[1]
mcp["x"] = mcp.extra_attrs_json.map(lambda s: json.loads(s) if s else {})
def dims_of(r):
    d = json.loads(r.dims_json) if r.dims_json else {}
    if r.flow == "GLOBAL_DATAFLOW" and "AGE" in r.x: d["AGE"] = r.x["AGE"]   # GLOBAL_DATAFLOW carries AGE as an attribute
    return d
mcp["d"] = [dims_of(r) for r in mcp.itertuples(index=False)]
mcp["yr"] = mcp.time_period.str[:4]
mcp["v"] = pd.to_numeric(mcp.value, errors="coerce")
mcp["mult"] = pd.to_numeric(mcp.x.map(lambda x: x.get("UNIT_MULTIPLIER", "")), errors="coerce").fillna(0).astype(int)
mcp["v_scaled"] = mcp.v * (10.0 ** mcp.mult)
mcp_codes = set(mcp.indicator)
cl = pd.read_csv(M / "codelist_unicef_indicator.csv", dtype=str, keep_default_na=False).set_index("id")

from undc_dw_crosswalk import map_code as _map_code, RENAMED
KNOWN = mcp_codes | set(cl.index)
def map_code(code, dims): return _map_code(code, dims, KNOWN)

# ---------------------------------------------------------------- join
idx = {}
for r in mcp.itertuples(index=False):
    idx.setdefault((r.indicator, r.iso3, r.yr), []).append(r)
# dimensions that are not population breakdowns (never required to be _T)
IGNORE = {"VACCINE", "SERVICE_TYPE", "DATA_SOURCE", "HCF_TYPE", "SCH_TYPE", "INDICATOR_UIS", "SKILL_TYPE", "SDG_INDICATOR", "UNIT_MEASURE", "SERIES_NAME",
          "SERIES_YEAR", "CAUSE_OF_DEATH", "AGE_GROUP", "ECD_DOMAIN", "PROJ_SCENARIO", "FGM_PRACTITIONER", "FGM_TYPE", "AGE_FGM", "MTH_FGM_STATUS",
          "AGE_AT_BIRTH", "NUMBER_CHLD", "WASH_SERVICE", "ADMIN_LEVEL", "REF_AREA_PARENT", "TIME_PERIOD_METHOD", "EDUCATION_LEVEL", "POV_THRESHOLD"}
SEX_IN_CODE = ("PT_CM_", "PT_F_", "PT_M_", "MNCH_", "HVA_PMTCT", "NT_ANE", "WS_PPL_M", "GN_ANEMIA")
def ok(d, req, allow_age_any=False, relax_age=False):
    """required codes must be carried by the row (a dimension absent from the flow counts as satisfied — e.g. SEX for an IMMUNISATION row);
    with relax_age the row may carry AGE=_T where UN DC labels an implicit age (NT_VAS 6–59 months vs DW total); every other breakdown must be a total"""
    for k, v in req.items():
        if k not in d: continue
        if k == "AGE" and relax_age and d[k] in ("_T", ""): continue
        if d[k] != v: return False
    for k, v in d.items():
        if k in req or k in IGNORE: continue
        if k == "AGE" and allow_age_any: continue
        if v not in ("_T", ""): return False
    return True
def pick(rows, ucode, req):
    """match order: thematic row carrying every required code with totals elsewhere; thematic AGE=_T (implicit age); GLOBAL_DATAFLOW copy; thematic single inherent age"""
    them = [r for r in rows if r.flow != "GLOBAL_DATAFLOW"]
    glob_ = [r for r in rows if r.flow == "GLOBAL_DATAFLOW"]
    req = dict(req)
    if "SEX" in req and ucode.startswith(SEX_IN_CODE): req.pop("SEX")
    c = [r for r in them if ok(r.d, req)]
    if c: return c, "thematic:" + ("+".join(f"{k}={v}" for k, v in req.items()) or "totals")
    c = [r for r in them if ok(r.d, dict(req, AGE=req.get("AGE", "_T")), relax_age=True)]
    if c: return c, "thematic:AGE=_T" + (" (UN DC age label implicit)" if "AGE" in req else "")
    gr = {k: v for k, v in req.items() if k in ("SEX", "AGE")}
    g = [r for r in glob_ if ok(r.d, gr)] or [r for r in glob_ if ok(r.d, gr, relax_age=True)]
    if g: return g, "GLOBAL_DATAFLOW"
    c = [r for r in them if ok(r.d, {k: v for k, v in req.items() if k != "AGE"}, allow_age_any=True)]
    if c and len({x.d.get("AGE") for x in c}) == 1: return c, "thematic:single-age=" + str(c[0].d.get("AGE"))
    return [], ""

out = []
for r in undc.itertuples(index=False):
    ucode, req = map_code(r.code, r.dims)
    if r.dims.get("AGE") and "AGE" not in req: req = dict(req, AGE=r.dims["AGE"])   # UN DC age label tried first, relaxed to _T if the flow has no such age
    rows = idx.get((ucode, r.iso3, r.yr), [])
    cand, how = pick(rows, ucode, req) if rows else ([], "")
    mv = cand[0] if cand else None
    out.append(dict(undc_code=r.code, undc_dcid=r.undc_dcid_queried, unicef_code=ucode, required=json.dumps(req, separators=(",", ":")), iso3=r.iso3, year=r.yr,
                    undc_value=r.value, undc_v=r.v, mcp_value=mv.value if mv else "", mcp_v=mv.v if mv else np.nan, mcp_v_scaled=mv.v_scaled if mv else np.nan,
                    mcp_unit_multiplier=mv.mult if mv else np.nan, mcp_flow=mv.flow if mv else "", mcp_dims=json.dumps(mv.d, separators=(",", ":")) if mv else "",
                    mcp_lower=mv.lower_bound if mv else "", mcp_upper=mv.upper_bound if mv else "", mcp_source=mv.data_source if mv else "",
                    mcp_unit=mv.unit_measure if mv else "", mcp_obs_status=mv.obs_status if mv else "", match_how=how, n_candidates=len(cand),
                    unicef_code_in_mcp=ucode in mcp_codes, unicef_code_in_codelist=ucode in cl.index))
j = pd.DataFrame(out)
def rel(a, b):
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100 * (a - b) / ((a + b) / 2)
    r = np.where((a == 0) & (b == 0), 0.0, r)
    return np.where(((a + b) == 0) & ~((a == 0) & (b == 0)), 200.0, r)
j["rel_diff_pct"] = rel(j.undc_v.values, j.mcp_v.values)
j["rel_diff_scaled_pct"] = rel(j.undc_v.values, j.mcp_v_scaled.values)
j["string_equal"] = (j.undc_value.str.strip() == j.mcp_value.str.strip()) & (j.mcp_value != "")
j.to_csv(OUT / "undc_vs_mcp_paired.csv", index=False)

# ---------------------------------------------------------------- per-variable summary, vintage and revision metrics
mcp_latest = mcp.groupby(["indicator", "iso3"]).yr.max().rename("mcp_latest").reset_index()
def summ(g):
    m = g[g.mcp_value != ""]
    ad, ads = m.rel_diff_pct.abs(), m.rel_diff_scaled_pct.abs()
    latest = g.year.max(); ml = m[m.year == latest]
    hist = m[m.year < latest]
    return pd.Series(dict(undc_obs=len(g), matched_obs=len(m), undc_years=f"{g.year.min()}-{g.year.max()}", undc_latest=latest,
                          share_exact_string=m.string_equal.mean() if len(m) else np.nan,
                          share_within_0_01pct=(ad <= 0.01).mean() if len(m) else np.nan, share_within_1pct=(ad <= 1).mean() if len(m) else np.nan,
                          share_within_0_01pct_scaled=(ads <= 0.01).mean() if len(m) else np.nan,
                          max_abs_rel_pct=ad.max() if len(m) else np.nan, median_abs_rel_pct=ad.median() if len(m) else np.nan,
                          latest_year_matched=len(ml) > 0, latest_year_within_1pct=(ml.rel_diff_pct.abs() <= 1).all() if len(ml) else np.nan,
                          n_hist_years_revised_gt1pct=int((hist.rel_diff_pct.abs() > 1).sum()), n_hist_years_matched=len(hist),
                          mcp_unit_multiplier=";".join(sorted({str(int(x)) for x in m.mcp_unit_multiplier.dropna()})),
                          match_how=";".join(sorted(set(m.match_how))) if len(m) else "", countries=",".join(sorted(set(g.iso3)))))
s = j.groupby(["undc_code", "undc_dcid", "unicef_code", "unicef_code_in_mcp", "unicef_code_in_codelist"]).apply(summ).reset_index()
undc_latest = j.groupby(["undc_dcid", "unicef_code", "iso3"]).year.max().rename("undc_latest").reset_index()
vint = undc_latest.merge(mcp_latest, left_on=["unicef_code", "iso3"], right_on=["indicator", "iso3"], how="left").drop(columns=["indicator"])
vint["lag_years"] = pd.to_numeric(vint.mcp_latest, errors="coerce") - pd.to_numeric(vint.undc_latest, errors="coerce")
vint.to_csv(OUT / "undc_vs_mcp_vintage.csv", index=False)
s = s.merge(vint.groupby("undc_dcid").lag_years.max().rename("max_lag_years").reset_index(), on="undc_dcid", how="left")

# documented reasons for residual differences (from inspection of DATA_SOURCE labels, footnotes and codelists)
REASON = {
 "IM_VACC": "WUENIC release lag: DW serves the 2026 release (to 2025), UN DC the 2025 release", "IM_BCG": "WUENIC release lag", "IM_HEPBB": "WUENIC release lag",
 "IM_HPV": "WUENIC release lag", "IM_MCV2": "WUENIC release lag",
 "HVA_EPI_DTH_ANN": "UNAIDS release lag: DW 'UNAIDS 2026 estimates' vs UN DC 2025 estimates", "HVA_EPI_INF_ANN": "UNAIDS release lag", "HVA_EPI_LHIV": "UNAIDS release lag",
 "HVA_PED_LOST_AIDS": "UNAIDS release lag",
 "WS_HCF_W": "JMP release lag (2026 round)", "WS_SCH_H": "JMP release lag (2026 round)", "WS_SCH_H-F": "JMP release lag (2026 round)", "WS_SCH_S": "JMP release lag (2026 round)",
 "WS_SCH_S-I": "JMP release lag (2026 round)", "WS_SCH_W-I": "JMP release lag (2026 round)", "WS_SCH_W_DW": "JMP release lag (2026 round)",
 "GN_LF_PTCPN": "ILO modelled-estimate revision (DW 'ILO API' current vintage)", "GN_UNMPLY": "ILO modelled-estimate revision", "GN_ED_ATTN": "World Bank/UIS series revision (DW 'WB API')",
 "GN_SG_LGL_GENEQEMP": "UN Women/World Bank legal-framework series revision", "GN_IT_MOB_OWN": "different source series: UN DC annual series (ITU-type), DW 2017 Findex by sex",
 "PV_CHLD_DEPRV_M": "MODA update: DW copy is a later estimate (6-year newer latest year)", "PV_CHLD_DEPRV_S": "MODA update", "PV_CHLD_DPRV_AVG_HS": "MODA update", "PV_CHLD_DPRV_AVG_S_HS": "MODA update",
 "MG_INTERNAL_DISP_PERS": "IDMC GIDD 2026 release vs earlier release", "MG_NEW_INTERNAL_DISP": "IDMC GIDD 2026 release vs earlier release",
 "MG_RFGS_CNTRY_ASYLM": "UNHCR Global Trends 2026 release vs earlier release", "MG_RFGS_CNTRY_ORIGIN": "UNHCR release lag", "MG_INTNL_MG_CNTRY_DEST": "UN DESA International Migrant Stock 2024 vs 2020",
 "MG_RFGS_CNTRY_ASYLM_PER1000": "UN DC series is an integer '1' for every year (ingestion/rounding error); DW holds decimals", "MG_RFGS_CNTRY_ASYLM_PER_USD_GNI": "UN DC series is an integer '1' for every year (ingestion/rounding error); DW holds decimals",
 "PV_LEVEL": "categorical value: UN DC recodes the DW string category ('Low') as a 0/1 variable per category",
 "DM_POP_URBN": "WUP 2025 revision (DW) vs earlier WUP (UN DC)", "DM_POP_U_GRT": "WUP 2025 revision", "DM_POP_DOU": "WUP 2025 revision", "DM_BU_PC_DOU": "WUP 2025 revision", "DM_POP_DOU_GRT": "WUP 2025 revision",
}
def verdict(r):
    if r.matched_obs == 0:
        if r.unicef_code == "?": return "no counterpart: code not in the DW codelist"
        if not r.unicef_code_in_mcp: return "no counterpart: code in codelist, no DW data for these countries"
        return "no counterpart: code has DW data but no row for these years/breakdowns"
    if r.share_within_0_01pct == 1: return "identical"
    if r.share_within_0_01pct_scaled == 1 and r.mcp_unit_multiplier not in ("", "0"): return "identical after unit multiplier"
    if r.share_within_1pct == 1: return "identical to rounding"
    return "differs"
s["verdict"] = s.apply(verdict, axis=1)
s["reason"] = np.where(s.verdict == "differs", s.undc_code.map(REASON).fillna("see paired file"), "")
s.loc[(s.verdict == "differs") & (s.undc_code.str.startswith("PV_CHLD_DEPRV")), "reason"] = "MODA update"
s["categorical_equivalent"] = s.undc_code.eq("PV_LEVEL")
LABEL_NOTES = {"FD_ANAR": "UN DC label error: the FD_ANAR variable (functional-difficulty flow code) holds the all-children adjusted net attendance rate ED_ANAR_L1",
               "MNCH_BIRTH18": "UN DC age label Y15T49; the DW series is women aged 20-24 (Y20T24)", "PT_MRD_U18": "UN DC PT_MRD_U18.SEX--F is the count of child brides (DW PT_F_TMRD18), not a proportion",
               "PT_CM_IPV_12M": "DW itself carries identical values for PT_CM_IPV_12M and PT_CM_EMPLOY_12M (Nigeria DHS 2023-24, all marriage-status categories) — upstream issue, faithfully copied",
               "IM_VACC": "VACCINE--PCV3 variant: the DW retired IM_PCV3 and now serves IM_PCVC (PCV, last dose); UN DC keeps the old code",
               "CME_PND": "UN DC unit label Percent for 0-1 fractions", "PV_CHLD_DPRV_AVG_HS": "UN DC unit label Percent for an average number of deprivations"}
s["label_note"] = s.undc_code.map(LABEL_NOTES).fillna("")
s.to_csv(OUT / "undc_vs_mcp_by_variable.csv", index=False)
print(s.verdict.value_counts().to_string())
print("\nlag distribution (max over countries, matched variables):")
print(s[s.matched_obs > 0].max_lag_years.value_counts(dropna=False).sort_index().to_string())
print("\ndiffers:")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70); pd.set_option("display.max_rows", 300)
print(s[s.verdict == "differs"][["undc_dcid", "unicef_code", "matched_obs", "share_within_1pct", "max_abs_rel_pct", "latest_year_within_1pct", "n_hist_years_revised_gt1pct", "match_how", "reason"]].to_string(index=False))
print("\nno counterpart:")
print(s[s.verdict.str.startswith("no")][["undc_dcid", "unicef_code", "undc_obs", "undc_years", "verdict"]].to_string(index=False))
# headline summary
tot = len(s); matched = s[s.matched_obs > 0]
summary = pd.DataFrame([dict(metric="UN DC variables with ≥1 observation (3 countries)", value=tot),
                        dict(metric="variables matched to a DW row", value=len(matched)),
                        dict(metric="identical (all obs within 0.01%)", value=(s.verdict == "identical").sum()),
                        dict(metric="identical after unit multiplier", value=(s.verdict == "identical after unit multiplier").sum()),
                        dict(metric="identical to rounding (≤1%)", value=(s.verdict == "identical to rounding").sum()),
                        dict(metric="differs", value=(s.verdict == "differs").sum()),
                        dict(metric="no counterpart row", value=s.verdict.str.startswith("no").sum()),
                        dict(metric="paired observations", value=int(s.matched_obs.sum())),
                        dict(metric="paired observations within 0.01% (raw or unit-scaled)", value=int(((j.mcp_value != "") & ((j.rel_diff_pct.abs() <= 0.01) | (j.rel_diff_scaled_pct.abs() <= 0.01))).sum())),
                        dict(metric="paired observations with exact string equality", value=int(j.string_equal.sum())),
                        dict(metric="matched variables where DW latest year is newer than UN DC", value=int((matched.max_lag_years > 0).sum())),
                        dict(metric="matched variables with ≥1 historical year revised by >1%", value=int((matched.n_hist_years_revised_gt1pct > 0).sum())),
                        dict(metric="matched variables with latest common year within 1%", value=int(matched.latest_year_within_1pct.fillna(False).astype(bool).sum()))])
summary.to_csv(OUT / "undc_vs_mcp_summary.csv", index=False)
print("\n" + summary.to_string(index=False))

# ---------------------------------------------------------------- Data360 vs UNICEF MCP (117 pairs) through the UN DC join
d = pd.concat([pd.read_csv(f, dtype=str, keep_default_na=False) for f in sorted(glob.glob(str(U / "values_unicef_d360_*.csv")))], ignore_index=True)
d = d[(d.year != "") & (d.value != "") & (d.value != "null")].copy()
d["yr"] = d.year.str[:4]; d["v"] = pd.to_numeric(d.value, errors="coerce")
def is_total(dims):
    try: jd = json.loads(dims) if dims else {}
    except Exception: return True
    return all(v in ("_T", "T", "URB") or k in ("COMP_BREAKDOWN_1", "AGE") for k, v in jd.items()) or jd.get("SEX") == "F"
d = d[d.dimensions.map(is_total)].drop_duplicates(["indicator_code", "iso3", "yr"])
jm = j[j.mcp_value != ""].drop_duplicates(["undc_code", "iso3", "year"])
dm = d.merge(jm[["undc_code", "unicef_code", "iso3", "year", "mcp_value", "mcp_v", "mcp_v_scaled"]], left_on=["indicator_code", "iso3", "yr"], right_on=["undc_code", "iso3", "year"], how="inner")
dm["rel_diff_pct"] = rel(dm.v.values, dm.mcp_v.values); dm["rel_diff_scaled_pct"] = rel(dm.v.values, dm.mcp_v_scaled.values)
dm.to_csv(OUT / "d360_vs_mcp_paired.csv", index=False)
ds = dm.groupby(["indicator_code", "d360_idno"]).apply(lambda g: pd.Series(dict(n=len(g), share_within_1pct=(np.minimum(g.rel_diff_pct.abs(), g.rel_diff_scaled_pct.abs()) <= 1).mean(),
                                                                              median_abs_rel_pct=g.rel_diff_pct.abs().median(), max_abs_rel_pct=g.rel_diff_pct.abs().max()))).reset_index()
ds.to_csv(OUT / "d360_vs_mcp_by_indicator.csv", index=False)
print("\nData360 vs UNICEF MCP: indicators", len(ds), "| all within 1%:", (ds.share_within_1pct == 1).sum(), "| >=90% within 1%:", (ds.share_within_1pct >= 0.9).sum(), "| pairs", len(dm))
