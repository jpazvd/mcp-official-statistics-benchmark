"""
Data360 against the UNICEF SDMX warehouse, joined directly (not only through UN DC's observation years):
for each UN DC code with a Data360 same-concept counterpart, the warehouse series is the one the UN DC join selected
(code, flow, dimension codes), taken in full for 2000-2025; Data360 totals are joined on country and year.
Inputs : ../unicefmcp/out/undc_vs_mcp_paired.csv, ../unicefmcp/series_all.csv + supplement, ../universe/values_unicef_d360_*.csv, extraction_pairs.csv
Outputs: ../unicefmcp/out/d360_vs_dw_paired.csv, d360_vs_dw_by_indicator.csv, d360_vs_dw_summary.csv
Run    : python3 -I d360_vs_dw.py
"""
import json, glob
import numpy as np, pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
U, M = ROOT / "universe", ROOT / "unicefmcp"; OUT = M / "out"
p = pd.read_csv(OUT / "undc_vs_mcp_paired.csv", dtype=str, keep_default_na=False)
def strip_src(s_):
    d = json.loads(s_) if s_ else {}; d.pop("DATA_SOURCE", None); return json.dumps(d, separators=(",", ":"))
sel = p[p.mcp_value != ""].groupby(["undc_code", "iso3"]).agg(unicef_code=("unicef_code", "first"), mcp_flow=("mcp_flow", "first"), mcp_dims=("mcp_dims", "first")).reset_index()
sel["mcp_dims"] = sel.mcp_dims.map(strip_src)
mcp = pd.concat([pd.read_csv(M / "series_all.csv", dtype=str, keep_default_na=False), pd.read_csv(M / "supplement" / "series_supplement.csv", dtype=str, keep_default_na=False)])
mcp = mcp[~mcp.flowRef.str.contains("SUBNAT|CME_SUBNATIONAL|MG_FLOW")].drop_duplicates(["flowRef", "indicator", "iso3", "dims_json", "time_period"]).copy()
mcp["flow"] = mcp.flowRef.str.split("/").str[1]; mcp["yr"] = mcp.time_period.str[:4]
mcp["x"] = mcp.extra_attrs_json.map(lambda s: json.loads(s) if s else {})
def dims_key(r):
    d = json.loads(r.dims_json) if r.dims_json else {}
    if r.flow == "GLOBAL_DATAFLOW" and "AGE" in r.x: d["AGE"] = r.x["AGE"]
    d.pop("DATA_SOURCE", None)   # MNCH and HIV_AIDS carry the survey as a dimension: the series is the union over sources
    return json.dumps(d, separators=(",", ":"))

mcp["dkey"] = [dims_key(r) for r in mcp.itertuples(index=False)]
mcp["mult"] = pd.to_numeric(mcp.x.map(lambda x: x.get("UNIT_MULTIPLIER", "")), errors="coerce").fillna(0).astype(int)
mcp["v"] = pd.to_numeric(mcp.value, errors="coerce") * (10.0 ** mcp.mult)
w = sel.merge(mcp[["indicator", "flow", "dkey", "iso3", "yr", "v", "value", "data_source"]], left_on=["unicef_code", "mcp_flow", "mcp_dims", "iso3"], right_on=["indicator", "flow", "dkey", "iso3"], how="inner")
w = w.drop_duplicates(["undc_code", "iso3", "yr"])
d = pd.concat([pd.read_csv(f, dtype=str, keep_default_na=False) for f in sorted(glob.glob(str(U / "values_unicef_d360_*.csv")))], ignore_index=True)
d = d[(d.year != "") & (d.value != "") & (d.value != "null")].copy()
d["yr"] = d.year.str[:4]; d["dv"] = pd.to_numeric(d.value, errors="coerce")
def is_total(dims):
    try: jd = json.loads(dims) if dims else {}
    except Exception: return True
    return all(v in ("_T", "T", "URB") or k in ("COMP_BREAKDOWN_1", "AGE") for k, v in jd.items()) or jd.get("SEX") == "F"
d = d[d.dimensions.map(is_total)].drop_duplicates(["indicator_code", "iso3", "yr"])
j = d.merge(w[["undc_code", "unicef_code", "mcp_flow", "iso3", "yr", "v", "value", "data_source"]].rename(columns={"value": "dw_value", "data_source": "dw_source"}), left_on=["indicator_code", "iso3", "yr"], right_on=["undc_code", "iso3", "yr"], how="inner")
with np.errstate(divide="ignore", invalid="ignore"): j["rel"] = 100 * (j.dv - j.v) / ((j.dv + j.v) / 2)
j["rel"] = np.where((j.dv == 0) & (j.v == 0), 0.0, j.rel)
j.to_csv(OUT / "d360_vs_dw_paired.csv", index=False)
# latest years
proj = sel[sel.mcp_flow == "DM"].merge(mcp[mcp.flow == "DM_PROJECTIONS"][["indicator", "dkey", "iso3", "yr"]], left_on=["unicef_code", "mcp_dims", "iso3"], right_on=["indicator", "dkey", "iso3"], how="inner")
dw_latest = pd.concat([w[["undc_code", "yr"]], proj[["undc_code", "yr"]]]).groupby("undc_code").yr.max().rename("dw_latest"); d_latest = d.groupby("indicator_code").yr.max().rename("d360_latest")
def summ(g):
    ad = g.rel.abs(); latest = g.yr.max(); hist = g[g.yr < latest]
    return pd.Series(dict(n_pairs=len(g), share_within_1pct=(ad <= 1).mean(), share_within_5pct=(ad <= 5).mean(), median_abs_rel_pct=ad.median(), max_abs_rel_pct=ad.max(),
                          years=f"{g.yr.min()}-{g.yr.max()}", n_hist_revised_gt1pct=int((hist.rel.abs() > 1).sum()), dw_source=";".join(sorted(set(g.dw_source)))[:120]))
s = j.groupby(["indicator_code", "unicef_code", "d360_idno", "d360_database_id"]).apply(summ).reset_index()
s = s.merge(dw_latest, left_on="indicator_code", right_index=True, how="left").merge(d_latest, left_on="indicator_code", right_index=True, how="left")
s["lag_years"] = pd.to_numeric(s.dw_latest) - pd.to_numeric(s.d360_latest)
def verdict(r):
    if r.share_within_1pct == 1: return "identical (within 1%)"
    if r.share_within_5pct >= 0.9: return "rounding / minor"
    return "different series or vintage"
s["verdict"] = s.apply(verdict, axis=1)
pairs = pd.read_csv(U / "extraction_pairs.csv", dtype=str).fillna("")
no = pairs[~pairs.indicator_code.isin(s.indicator_code)][["indicator_code", "d360_idno", "d360_database_id", "unicef_sourced"]].copy()
no["verdict"] = np.where(no.indicator_code.isin(d.indicator_code), np.where(no.indicator_code.isin(w.undc_code), "no overlapping years", "no warehouse row for these countries"), "no Data360 data (3 countries)")
s = pd.concat([s, no], ignore_index=True)
s = s.merge(pairs[["indicator_code", "unicef_sourced", "undc_name"]].drop_duplicates("indicator_code"), on="indicator_code", how="left", suffixes=("", "_p"))
s["unicef_sourced"] = s.unicef_sourced.fillna(s.get("unicef_sourced_p"))
s.to_csv(OUT / "d360_vs_dw_by_indicator.csv", index=False)
print(s.verdict.value_counts().to_string()); print(s.groupby(["d360_database_id", "verdict"]).size().unstack(fill_value=0).to_string())
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200); pd.set_option("display.max_colwidth", 60)
print(s[s.verdict == "different series or vintage"][["indicator_code", "d360_idno", "n_pairs", "share_within_1pct", "median_abs_rel_pct", "years", "n_hist_revised_gt1pct", "dw_latest", "d360_latest", "dw_source"]].to_string(index=False))
print("lag distribution:"); print(s[s.n_pairs.notna()].lag_years.value_counts(dropna=False).sort_index().to_string())
summary = pd.DataFrame([dict(metric="Data360 same-concept pairs", value=len(pairs)), dict(metric="pairs with overlapping years in the warehouse", value=int(s.n_pairs.notna().sum())),
                        dict(metric="identical (within 1%)", value=int((s.verdict == "identical (within 1%)").sum())), dict(metric="rounding / minor", value=int((s.verdict == "rounding / minor").sum())),
                        dict(metric="different series or vintage", value=int((s.verdict == "different series or vintage").sum())), dict(metric="paired observations", value=len(j)),
                        dict(metric="paired observations within 1%", value=int((j.rel.abs() <= 1).sum())),
                        dict(metric="pairs where the warehouse has a newer latest year", value=int((s.lag_years > 0).sum())), dict(metric="pairs where Data360 has a newer latest year", value=int((s.lag_years < 0).sum()))])
summary.to_csv(OUT / "d360_vs_dw_summary.csv", index=False); print(summary.to_string(index=False))
