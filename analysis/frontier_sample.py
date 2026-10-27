"""
Cost-frontier benchmark, step 1: the pre-registered sample and the exact call specification for each server.
Frame  : UN DC UNICEF codes whose series map to a warehouse series with data for Nigeria (universe_dw_vs_undc_by_code.csv,
         undc_vs_mcp_paired.csv). Strata: UN DC's 17 UNICEF sector groups x breakdown richness (the sector's codes ranked by number of UN DC
         variables and split into a lower and an upper half). One code drawn per stratum, seed 20261027.
Series : the code's representative UN DC variable when it is matched for Nigeria, else its matched variable with most
         Nigerian observations; the warehouse series is the matched one (flow, indicator, pinned dimensions; DATA_SOURCE
         and any dimension that varies across matched rows are left open).
Country: Nigeria for every series; Brazil and Somalia for 12 series drawn from the 34 (same seed).
Query  : q1 = the warehouse codelist name of the series (the custodian's name); q2 = the UN DC variable name without
         its bracketed breakdown, used only if the target is absent from the q1 result.
Output : ../unicefmcp/frontier/sample.csv, spec_warehouse.csv, spec_undc.csv, spec_d360.csv
Run    : python3 -I frontier_sample.py
"""
import json, re
import numpy as np, pandas as pd
from pathlib import Path
H = Path(__file__).resolve().parent.parent
M = H / "unicefmcp"; OUT = M / "frontier"; OUT.mkdir(exist_ok=True)
SEED = 20261027
rng = np.random.RandomState(SEED)
codes = pd.read_csv(H / "universe/undc_unicef_codes.csv", dtype=str, keep_default_na=False)
reps = pd.read_csv(H / "universe/undc_unicef_representatives.csv", dtype=str, keep_default_na=False)
uni = pd.read_csv(M / "out/universe_dw_vs_undc_by_code.csv", dtype=str, keep_default_na=False)
pair = pd.read_csv(M / "out/undc_vs_mcp_paired.csv", dtype=str, keep_default_na=False)
cl = pd.read_csv(M / "codelist_unicef_indicator.csv", dtype=str, keep_default_na=False).drop_duplicates("id").set_index("id")
flows = pd.read_csv(M / "flows_all.csv", dtype=str, keep_default_na=False).set_index("id")
d360 = pd.read_csv(M / "out/d360_vs_dw_by_indicator.csv", dtype=str, keep_default_na=False)

frame = codes.merge(uni[["indicator_code", "dw_status"]], on="indicator_code")
frame = frame[frame.dw_status.isin(["verbatim code with DW data", "UN DC re-coding of a DW code with data"])].copy()
ng = pair[(pair.iso3 == "NGA") & (pair.mcp_flow != "")]
nobs = ng.groupby(["undc_code", "undc_dcid"]).size().rename("n").reset_index()
frame = frame[frame.indicator_code.isin(nobs.undc_code)].copy()
frame["n_variants"] = frame.n_variants.astype(int)
frame = frame.sort_values(["dataflow", "indicator_code"]).reset_index(drop=True)

picked = []
for sec, g in frame.groupby("dataflow", sort=True):
    g = g.sort_values(["n_variants", "indicator_code"]); h = len(g) // 2
    lo, hi = g.iloc[:h], g.iloc[h:]
    if len(lo):
        picked.append((lo.iloc[rng.randint(len(lo))], "fewer"))
    picked.append((hi.iloc[rng.randint(len(hi))], "more"))
rows = []
for r, stratum in picked:
    cand = nobs[nobs.undc_code == r.indicator_code]
    rep = reps.loc[reps.indicator_code == r.indicator_code, "representative_dcid"].iloc[0]
    dcid = rep if rep in set(cand.undc_dcid) else cand.sort_values(["n", "undc_dcid"], ascending=[False, True]).undc_dcid.iloc[0]
    pr = ng[ng.undc_dcid == dcid]
    ucode, flow = pr.unicef_code.iloc[0], pr.mcp_flow.iloc[0]
    dims = {}
    for js in pr.required.tolist() + pr.mcp_dims.tolist():
        for k, v in (json.loads(js) if js else {}).items():
            dims.setdefault(k, set()).add(v)
    order = [d for d in flows.loc[flow, "dimensions_ordered"].split("|") if d != "TIME_PERIOD"]
    pinned = {k: next(iter(v)) for k, v in dims.items() if len(v) == 1 and k in order and k not in ("DATA_SOURCE", "REF_AREA", "INDICATOR")}
    vname = re.sub(r"\s*\[.*\]\s*$", "", pr.undc_dcid.iloc[0] and codes.set_index("indicator_code").loc[r.indicator_code, "undc_name"])
    dd = d360[(d360.indicator_code == r.indicator_code) & (d360.unicef_code == ucode)]
    rows.append(dict(sector=r.dataflow, stratum=stratum, undc_code=r.indicator_code, undc_variants=r.n_variants, undc_dcid=dcid,
                     unicef_code=ucode, flowRef=flows.loc[flow, "flowRef"], dim_order="|".join(order), pinned=json.dumps(pinned, sort_keys=True),
                     q1=cl.loc[ucode, "name"] if ucode in cl.index else vname, q2=vname,
                     d360_database=dd.d360_database_id.iloc[0] if len(dd) else "", d360_idno=dd.d360_idno.iloc[0] if len(dd) else ""))
s = pd.DataFrame(rows)
s.insert(0, "sid", [f"S{i+1:02d}" for i in range(len(s))])
rep12 = set(s.sid.iloc[sorted(rng.choice(len(s), size=12, replace=False))])
s["countries"] = s.sid.map(lambda x: "NGA;BRA;SOM" if x in rep12 else "NGA")
s.to_csv(OUT / "sample.csv", index=False)

CN = {"NGA": "Nigeria", "BRA": "Brazil", "SOM": "Somalia"}
def key(r, iso):
    p = json.loads(r.pinned); seg = []
    for d in r.dim_order.split("|"):
        seg.append(iso if d == "REF_AREA" else r.unicef_code if d == "INDICATOR" else p.get(d, ""))
    return ".".join(seg)
wh, un, wb = [], [], []
for r in s.itertuples(index=False):
    wh.append(dict(sid=r.sid, step="find", tool="find_indicator_candidates", args=json.dumps({"query": r.q1}), alt_args=json.dumps({"query": r.q2}), target=r.unicef_code, iso3=""))
    un.append(dict(sid=r.sid, step="metadata", tool="get_variable_metadata", args=json.dumps({"variable_dcids": [r.undc_dcid]}), alt_args="", target=r.undc_dcid, iso3=""))
    if r.d360_idno:
        wb.append(dict(sid=r.sid, step="search", tool="data360_search_indicators", args=json.dumps({"query": r.q1}), alt_args=json.dumps({"query": r.q2}), target=r.d360_idno, iso3=""))
        wb.append(dict(sid=r.sid, step="metadata", tool="data360_get_metadata", args=json.dumps({"database_id": r.d360_database, "indicator_id": r.d360_idno}), alt_args="", target=r.d360_idno, iso3=""))
    for iso in r.countries.split(";"):
        wh.append(dict(sid=r.sid, step="data", tool="query_data", args=json.dumps({"flowRef": r.flowRef, "key": key(r, iso), "startPeriod": "2000", "endPeriod": "2025", "format": "csv", "labels": "id"}), alt_args="", target=r.unicef_code, iso3=iso))
        un.append(dict(sid=r.sid, step="search", tool="search_indicators", args=json.dumps({"query": r.q1, "places": [CN[iso]], "per_search_limit": 10}), alt_args=json.dumps({"query": r.q2, "places": [CN[iso]], "per_search_limit": 10}), target=r.undc_dcid, iso3=iso))
        un.append(dict(sid=r.sid, step="data", tool="get_observations", args=json.dumps({"variable_dcid": r.undc_dcid, "place_dcid": f"country/{iso}", "date": "all"}), alt_args="", target=r.undc_dcid, iso3=iso))
        if r.d360_idno:
            wb.append(dict(sid=r.sid, step="data", tool="data360_get_data", args=json.dumps({"database_id": r.d360_database, "indicator_id": r.d360_idno, "country_code": iso, "start_year": 2000, "end_year": 2025, "limit": 100}), alt_args="", target=r.d360_idno, iso3=iso))
for f in sorted({x["args"] and json.loads(x["args"])["flowRef"] for x in wh if x["tool"] == "query_data"}):
    wh.append(dict(sid="", step="structure", tool="list_dimensions", args=json.dumps({"flowRef": f}), alt_args="", target="", iso3=""))
for name, lst in (("warehouse", wh), ("undc", un), ("d360", wb)):
    pd.DataFrame(lst).to_csv(OUT / f"spec_{name}.csv", index=False)
    print(name, len(lst), "scripted calls (before any retries)")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 55)
print(s[["sid", "sector", "stratum", "undc_code", "undc_variants", "unicef_code", "q1", "d360_idno", "countries"]].to_string(index=False))
