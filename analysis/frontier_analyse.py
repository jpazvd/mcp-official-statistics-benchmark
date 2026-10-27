"""
Cost-frontier benchmark, step 4: one row per question (series x country) and server: characters by component,
discovery outcome, answered or not, observations, latest year, agreement with the warehouse, share of the standard.
Cost of a question as an agent answering it alone would pay: discovery (all attempts) + structure (list_dimensions of
the flow, warehouse only) + data call. The metadata call is reported separately (UN DC: the corrected calls of agent
un4; the first UN DC metadata calls failed on a missing argument in the work list and are excluded as protocol error).
Output: ../unicefmcp/frontier/questions.csv, summary printed
Run   : python3 -I frontier_analyse.py
"""
import json, io, re, sys
import numpy as np, pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import frontier_score as fs
F = Path(__file__).resolve().parent.parent / "unicefmcp" / "frontier"
c = pd.read_csv(F / "calls.csv", dtype=str, keep_default_na=False); c["chars"] = c.chars.astype(int)
s = pd.read_csv(F / "sample.csv", dtype=str, keep_default_na=False)
raw = lambda f: (F / "raw" / f).read_text(encoding="utf-8")
c = c[~((c.tool == "get_variable_metadata") & c.agent.isin(["un1", "un2", "un3"]))]   # protocol error, rerun as un4

def wh_values(txt):
    df = fs.wh_rows(txt)
    if df.empty or "OBS_VALUE" not in df.columns: return {}
    v = {}
    mult = df["UNIT_MULTIPLIER"] if "UNIT_MULTIPLIER" in df.columns else pd.Series("", index=df.index)
    for r, m in zip(df.itertuples(index=False), mult):
        try:
            x = float(r.OBS_VALUE); v.setdefault(str(r.TIME_PERIOD)[:4], []).append(x)
            if str(m).strip() not in ("", "0"):   # also compare in units, as published values are in 10^mult
                v[str(r.TIME_PERIOD)[:4]].append(x * 10 ** int(float(m)))
        except Exception: pass
    return v
def undc_values(txt):
    j = fs.jload(txt) or {}
    rows = ((j.get("data") or {}).get("rows")) or []
    return {str(r[1])[:4]: [float(r[2])] for r in rows if len(r) > 2 and r[2] is not None}
def d360_values(txt):
    j = fs.jload(txt) or {}
    out = {}
    for r in j.get("data") or []:
        try: out.setdefault(str(r.get("TIME_PERIOD"))[:4], []).append(float(r.get("OBS_VALUE")))
        except Exception: pass
    return out
def agree(v, ref):
    yrs = [y for y in v if y in ref]
    if not yrs: return np.nan, 0
    ok = [any(abs(a - b) <= 0.01 * max(abs(b), 1e-9) or abs(a - b) < 1e-9 for a in v[y] for b in ref[y]) for y in yrs]
    return round(100 * np.mean(ok), 1), len(yrs)
def rank_of(txt, target):
    j = fs.jload(txt)
    if isinstance(j, dict):
        for key in ("result", "indicators"):
            if isinstance(j.get(key), list):
                ids = [x.get("id") or x.get("idno") for x in j[key] if isinstance(x, dict)]
                return ids.index(target) + 1 if target in ids else None
        if "dcidNameMappings" in j:
            ids = list(j["dcidNameMappings"].keys())
            return ids.index(target) + 1 if target in ids else None
    return 1 if target in txt else None

rows = []
for q in s.itertuples(index=False):
    for iso in q.countries.split(";"):
        whd = c[(c.sid == q.sid) & (c.tool == "query_data") & (c.iso3 == iso)]
        wh_txt = raw(whd.raw.iloc[0]) if len(whd) else ""
        app = fs.applicability(wh_txt)
        ref = wh_values(wh_txt)
        for srv in ("warehouse", "undc", "d360"):
            if srv == "warehouse":
                disc = c[(c.sid == q.sid) & (c.tool == "find_indicator_candidates")]
                flow = json.loads(q.flowRef and json.dumps({"f": q.flowRef}))["f"]
                struct = c[(c.tool == "list_dimensions") & c.args.str.contains(f'"{flow}"', regex=False)]
                data = whd; meta = c.iloc[0:0]; target = q.unicef_code
            elif srv == "undc":
                disc = c[(c.sid == q.sid) & (c.tool == "search_indicators") & (c.iso3 == iso)]
                struct = c.iloc[0:0]
                data = c[(c.sid == q.sid) & (c.tool == "get_observations") & (c.iso3 == iso)]
                meta = c[(c.sid == q.sid) & (c.tool == "get_variable_metadata")]; target = q.undc_dcid
            else:
                if not q.d360_idno: continue
                disc = c[(c.sid == q.sid) & (c.tool == "data360_search_indicators")]
                struct = c.iloc[0:0]
                data = c[(c.sid == q.sid) & (c.tool == "data360_get_data") & (c.iso3 == iso)]
                meta = c[(c.sid == q.sid) & (c.tool == "data360_get_metadata")]; target = q.d360_idno
            dtx = raw(data.raw.iloc[0]) if len(data) else ""
            mtx = raw(meta.raw.iloc[0]) if len(meta) else None
            first = disc[disc.attempt == "args"]; ftx = raw(first.raw.iloc[0]) if len(first) else ""
            found_first = bool(len(first)) and target in ftx
            found_any = any(target in raw(f) for f in disc.raw)
            last_found = next((raw(f) for f in disc.raw if target in raw(f)), ftx)
            if srv == "warehouse":
                sc = fs.score_warehouse(last_found, dtx, target, app); vals = ref
            elif srv == "undc":
                sc = fs.score_undc(last_found, dtx, None, target, app); scm = fs.score_undc(last_found, dtx, mtx, target, app); vals = undc_values(dtx)
            else:
                sc = fs.score_d360(last_found, dtx, None, target, app); scm = fs.score_d360(last_found, dtx, mtx, target, app); vals = d360_values(dtx)
            sm = fs.summarise(sc); smm = fs.summarise(scm) if srv != "warehouse" else sm
            ag, n_common = agree(vals, ref) if srv != "warehouse" else (np.nan, 0)
            rows.append(dict(sid=q.sid, sector=q.sector, stratum=q.stratum, undc_variants=int(q.undc_variants), iso3=iso, server=srv,
                             disc_calls=len(disc), disc_chars=int(disc.chars.sum()), struct_chars=int(struct.chars.sum()), data_chars=int(data.chars.sum()),
                             meta_chars=int(meta.chars.sum()), chars=int(disc.chars.sum() + struct.chars.sum() + data.chars.sum()),
                             calls=len(disc) + (1 if len(struct) else 0) + len(data),
                             found_first=found_first, found_after_retry=found_any, rank_first=rank_of(ftx, target) if len(first) else None,
                             answered=bool(vals), n_years=len(vals), latest=max(vals) if vals else "",
                             wh_answered=app["answered"], agree_pct=ag, n_common_years=n_common,
                             applicable=sm["applicable"], share=sm["share_delivered"], share_with_meta=smm["share_delivered"],
                             **{f"el_{e}": sc[e] for e in fs.ELEMS}))
Q = pd.DataFrame(rows)
Q.to_csv(F / "questions.csv", index=False)
pd.set_option("display.width", 250)
g = Q.groupby("server")
print(g.agg(questions=("sid", "size"), answered=("answered", "mean"), found_first=("found_first", "mean"), found_any=("found_after_retry", "mean"),
            chars_median=("chars", "median"), chars_p25=("chars", lambda x: x.quantile(.25)), chars_p75=("chars", lambda x: x.quantile(.75)),
            disc_share=("disc_chars", lambda x: x.sum()), share_median=("share", "median"), share_mean=("share", "mean"), agree_median=("agree_pct", "median")).to_string())
