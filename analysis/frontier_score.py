"""
Automated scoring of an MCP answer against the 15-element minimum metadata standard (rules written ex ante and
validated by reproducing the hand scores of the pilot paths: python3 -I frontier_score.py runs the validation).
Status per element: meets / partial / missing / n/a. Applicability of O2, O4 and O5 for a question is read from what
the warehouse publishes for the series and country (the custodian's publication as served by UNICEF):
  O2 reference period: the series is survey-based (DATA_SOURCE names a survey) or carries COVERAGE_TIME/TIME_PERIOD_METHOD
  O4 uncertainty     : bounds published;   O5 footnote: any observation, series or country note published.
"""
import io, json, re
import pandas as pd
ELEMS = ["R1", "R2", "R3", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "O1", "O2", "O3", "O4", "O5"]
PTS = {"meets": 1.0, "partial": 0.5, "missing": 0.0}
SURVEY = re.compile(r"DHS|MICS|survey|SMART|census|LSMS|MIS\b|AIS\b|GSHS|PMA|SPA\b|WHS|FLS", re.I)
RELEASE = re.compile(r"revision|release|edition|round|estimates.{0,15}(?:19|20)\d{2}|(?:19|20)\d{2}.{0,8}estimates|\bWPP\b|\bWUP\b|\bGIDD\b|\bJME\b", re.I)
BARE = re.compile(r"^[A-Z0-9_]+_SRC_\d+$")

def jload(txt):
    try:
        return json.loads(txt)
    except Exception:
        return None

def wh_rows(txt):
    """Warehouse query_data response -> DataFrame of rows (empty if error or no data)."""
    d = jload(txt)
    if not isinstance(d, dict) or not d.get("raw_csv"):
        return pd.DataFrame()
    try:
        return pd.read_csv(io.StringIO(d["raw_csv"]), dtype=str, keep_default_na=False)
    except Exception:
        return pd.DataFrame()

def nonempty(df, col):
    return df[col].astype(str).str.strip().ne("") if col in df.columns else pd.Series(False, index=df.index)

def share(mask):
    return "meets" if len(mask) and mask.all() else "partial" if mask.any() else "missing"

def applicability(wh_data_txt):
    df = wh_rows(wh_data_txt)
    if df.empty:
        return {"answered": False, "O2": False, "O4": False, "O5": False, "unit": ""}
    src = " ".join(df.get("DATA_SOURCE", pd.Series(dtype=str)).astype(str))
    o2 = bool(SURVEY.search(src)) or nonempty(df, "COVERAGE_TIME").any() or nonempty(df, "TIME_PERIOD_METHOD").any()
    o4 = nonempty(df, "LOWER_BOUND").any() or nonempty(df, "UPPER_BOUND").any()
    o5 = any(nonempty(df, c).any() for c in ("OBS_FOOTNOTE", "SERIES_FOOTNOTE", "COUNTRY_NOTES"))
    unit = df["UNIT_MEASURE"].iloc[0] if "UNIT_MEASURE" in df.columns else ""
    return {"answered": True, "O2": o2, "O4": o4, "O5": o5, "unit": unit}

def finish(s, app):
    for e, k in (("O2", "O2"), ("O4", "O4"), ("O5", "O5")):
        if not app.get(k):
            s[e] = "n/a"
    return s

def score_warehouse(find_txt, data_txt, target, app):
    df = wh_rows(data_txt); d = jload(data_txt) or {}
    s = {e: "missing" for e in ELEMS}
    if df.empty:
        return finish(s, app)
    txt = data_txt
    s["R1"] = "meets" if "queryURL" in txt else "missing"
    s["R2"] = "meets" if re.search(r'"(retrieved|retrievedAt|timestamp)"', txt) and re.search(r'"(serverVersion|server_version)"', txt) else "missing"
    s["R3"] = "meets" if ("appliedDefaults" in txt and "maxObs" in txt) else "partial" if ("appliedDefaults" in txt or "maxObs" in txt) else "missing"
    s["S1"] = "partial" if nonempty(df, "INDICATOR").all() else "missing"
    f = jload(find_txt) or {}
    hit = [x for x in f.get("result", []) if isinstance(x, dict) and x.get("id") == target]
    s["S2"] = "partial" if hit and str(hit[0].get("description", "")).strip() else "missing"
    s["S3"] = share(nonempty(df, "UNIT_MEASURE"))
    s["S4"] = "meets"
    s["S5"] = "meets" if nonempty(df, "CUSTODIAN").all() else "partial" if (nonempty(df, "DATA_SOURCE").any() or nonempty(df, "CUSTODIAN").any()) else "missing"
    src = df.get("DATA_SOURCE", pd.Series("", index=df.index)).astype(str)
    s["S6"] = "partial" if src.str.contains(RELEASE).any() else "missing"
    s["S7"] = "missing"
    ok = nonempty(df, "DATA_SOURCE") & ~src.str.match(BARE)
    s["O1"] = "meets" if ok.all() else "partial" if nonempty(df, "DATA_SOURCE").any() else "missing"
    s["O2"] = share(nonempty(df, "COVERAGE_TIME") | nonempty(df, "TIME_PERIOD_METHOD"))
    st = df.get("OBS_STATUS", pd.Series("", index=df.index)).astype(str).str.strip()
    s["O3"] = "meets" if (st.ne("").all() and st.ne("A").any()) else "partial" if st.ne("").any() else "missing"
    bounds = nonempty(df, "LOWER_BOUND") | nonempty(df, "UPPER_BOUND")
    s["O4"] = ("meets" if nonempty(df, "CONF_INTVAL").any() else "partial") if bounds.any() else "missing"
    s["O5"] = "meets" if any(c in df.columns for c in ("OBS_FOOTNOTE", "SERIES_FOOTNOTE", "COUNTRY_NOTES")) else "missing"
    return finish(s, app)

UNIT_CLASS = [("per1000", r"PER_1000|PER1000|1,?\s?000|D_PER_1000"), ("percent", r"PCNT|PERCENT|^%$|^PT$|Percentage"),
              ("years", r"\bYR\b|YEAR"), ("currency", r"USD|CURRENCY|DOLLAR"), ("index", r"INDEX|IDX|GINI|SCORE"),
              ("count", r"NUMBER|COUNT|PERSONS|^PS$|^NB$|^PERS")]
def uclass(u):
    for k, pat in UNIT_CLASS:
        if re.search(pat, str(u), re.I):
            return k
    return "other:" + str(u)

def score_undc(search_txt, obs_txt, meta_txt, target, app):
    s = {e: "missing" for e in ELEMS}
    o = jload(obs_txt) or {}
    rows = ((o.get("data") or {}).get("rows")) or []
    if not rows:
        return finish(s, app)
    s["R1"] = "partial"
    s["S1"] = "partial"
    desc = ""
    for t in (search_txt, meta_txt or ""):
        j = jload(t) or {}
        vs = j.get("variables") if isinstance(j, dict) else None
        v = vs.get(target, {}) if isinstance(vs, dict) else next((x for x in (vs or []) if isinstance(x, dict) and x.get("dcid") == target), {})
        desc = desc or str(v.get("description", "") or "")
    s["S2"] = "partial" if desc.strip() else "missing"
    unit = ((o.get("sourceMetadata") or {}).get("unit")) or ""
    s["S3"] = "missing" if not unit else "meets" if (app.get("unit") and uclass(unit) == uclass(app["unit"])) else "partial"
    s["S4"] = "partial"
    src = json.dumps(o.get("sourceMetadata", {})) + (meta_txt or "")
    named = re.search(r'"source"\s*:\s*"(?!United Nations")[^"]+"', src)
    s["S5"] = "partial" if named else "missing"
    return finish(s, app)

def score_d360(search_txt, data_txt, meta_txt, target, app):
    s = {e: "missing" for e in ELEMS}
    d = jload(data_txt) or {}
    rows = d.get("data") or []
    if not rows:
        return finish(s, app)
    s["R1"] = "partial"
    s["R3"] = "partial" if "has_more" in d else "missing"
    s["S1"] = "partial"
    sr = jload(search_txt) or {}
    inds = sr.get("indicators") or [x for r in (sr.get("results") or []) for x in (r.get("indicators") or [])]
    hit = [x for x in inds if isinstance(x, dict) and x.get("idno") == target]
    s["S2"] = "partial" if hit and str(hit[0].get("truncated_definition") or "").strip() else "missing"
    keys = ("UNIT_MEASURE", "UNIT_MEASURE_NAME", "UNIT_MULT")
    s["S3"] = "meets" if all(all(r.get(k) not in (None, "") for k in keys) for r in rows) else "partial" if any(r.get("UNIT_MEASURE") for r in rows) else "missing"
    s["S4"] = "partial"
    s["O1"] = "partial" if any(str(r.get(k, "") or "").strip() for r in rows for k in ("SOURCE", "DATA_SOURCE", "COMP_BREAKDOWN_1", "SURVEY")) else "missing"
    m = (jload(meta_txt) or {}).get("indicator_metadata") if meta_txt else None
    if m:
        if str(m.get("definition_long") or "").strip():
            s["S2"] = "meets"
        if (m.get("sources") or m.get("authoring_entity")):
            s["S5"] = "meets"
        vs = m.get("version_statement") or {}
        if (isinstance(vs, dict) and vs.get("version_date")) or m.get("date_released") or m.get("date_last_update"):
            s["S6"] = "partial"
        lic = m.get("license") or m.get("licence")
        cit = m.get("citation_requirement")
        s["S7"] = "meets" if (lic and cit) else "partial" if (lic or cit) else "missing"
    return finish(s, app)

def summarise(s):
    app = [e for e in ELEMS if s[e] != "n/a"]
    pts = sum(PTS[s[e]] for e in app)
    return dict(applicable=len(app), meets=sum(s[e] == "meets" for e in app), partial=sum(s[e] == "partial" for e in app),
                share_delivered=round(100 * pts / len(app), 1))

if __name__ == "__main__":   # validation against the pilot hand scores (metadata_standard_scoring.py)
    from pathlib import Path
    R = Path(__file__).resolve().parent.parent / "unicefmcp" / "cost" / "raw"
    rd = lambda f: (R / f).read_text(encoding="utf-8")
    import importlib.util, contextlib, os
    spec = importlib.util.spec_from_file_location("ms", Path(__file__).resolve().parent / "metadata_standard_scoring.py")
    ms = importlib.util.module_from_spec(spec)
    with open(os.devnull, "w") as dn, contextlib.redirect_stdout(dn):
        spec.loader.exec_module(ms)
    hand = {k: v[3] for k, v in ms.P.items()}
    a_u5, a_d3 = applicability(rd("D03b_yves_query_u5mr_retry.json")), applicability(rd("D06_yves_query_dtp3.json"))
    auto = {
     "Warehouse MCP: find + list_dimensions + query_data, one failed key (U5MR)": score_warehouse(rd("D01_yves_find_u5mr.json"), rd("D03b_yves_query_u5mr_retry.json"), "CME_MRY0T4", a_u5),
     "Warehouse MCP: find + query_data (DTP3)": score_warehouse(rd("D05_yves_find_dtp3.json"), rd("D06_yves_query_dtp3.json"), "IM_DTP3", a_d3),
     "UN DC: search + get_observations (U5MR)": score_undc(rd("A02_undc_search_u5mr.json"), rd("A03_undc_obs_u5mr.json"), None, "undata/sdg/SH_DYN_MORT.AGE--Y0T4", a_u5),
     "UN DC: + get_variable_metadata (U5MR)": score_undc(rd("A02_undc_search_u5mr.json"), rd("A03_undc_obs_u5mr.json"), rd("E01_undc_varmeta_u5mr.json"), "undata/sdg/SH_DYN_MORT.AGE--Y0T4", a_u5),
     "UN DC: search + get_observations (DTP3)": score_undc(rd("A04_undc_search_dtp3.json"), rd("A05_undc_obs_dtp3.json"), None, "undata/unicef/IM_VACC.AGE--M12T23__VACCINE--DTP3", a_d3),
     "UN DC: + get_variable_metadata (DTP3)": score_undc(rd("A04_undc_search_dtp3.json"), rd("A05_undc_obs_dtp3.json"), rd("E02_undc_varmeta_dtp3.json"), "undata/unicef/IM_VACC.AGE--M12T23__VACCINE--DTP3", a_d3),
     "Data360: search + get_data (U5MR)": score_d360(rd("B01_d360_search_u5mr.json"), rd("B02b_d360_data_u5mr_2000.json"), None, "WB_WDI_SH_DYN_MORT", a_u5),
     "Data360: + get_metadata (U5MR)": score_d360(rd("B01_d360_search_u5mr.json"), rd("B02b_d360_data_u5mr_2000.json"), rd("E03_d360_meta_u5mr.json"), "WB_WDI_SH_DYN_MORT", a_u5),
     "Data360: search (two tries) + get_data (DTP3)": score_d360(rd("B03b_d360_search_dpt_retry.json"), rd("B04b_d360_data_dpt_2000.json"), None, "WB_WDI_SH_IMM_IDPT", a_d3),
     "Data360: + get_metadata (DTP3)": score_d360(rd("B03b_d360_search_dpt_retry.json"), rd("B04b_d360_data_dpt_2000.json"), rd("E04_d360_meta_dtp3.json"), "WB_WDI_SH_IMM_IDPT", a_d3)}
    bad = 0
    for k, s in auto.items():
        h = {e: ("n/a" if v == "n/a" else v) for e, v in hand[k].items()}
        diff = {e: (h[e], s[e]) for e in ELEMS if h[e] != s[e]}
        bad += bool(diff)
        print(("OK  " if not diff else "DIFF") + f" {k}: {summarise(s)['share_delivered']}%" + (f"  hand vs auto {diff}" if diff else ""))
    print("paths reproduced:", len(auto) - bad, "of", len(auto))
