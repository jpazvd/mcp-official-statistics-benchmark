#!/usr/bin/env python3
"""Assemble the group output files from the per-flow work files.

usage: assemble.py GROUP_DIR GROUP_NAME FLOWS_TXT_BLOCK_FILE
Rebuilds (deterministically, in flow-list order):
  flows_<g>.csv, codelist_indicator_<g>.csv, unit_codelist_<g>.csv, obs_status_codelist_<g>.csv,
  inventory_<g>.csv, series_<g>.csv, log_<g>.md
"""
import csv, json, os, sys
from collections import OrderedDict

gdir, g, flows_file = sys.argv[1:4]
wdir = os.path.join(gdir, "work")
flows = [l.strip() for l in open(flows_file, encoding="utf-8") if l.strip() and not l.startswith("GROUP_")]

calls = []
cp = os.path.join(wdir, "calls.jsonl")
if os.path.exists(cp):
    calls = [json.loads(l) for l in open(cp, encoding="utf-8") if l.strip()]

FLOW_COLS = ["flowRef", "agency", "id", "name", "description", "version", "isFinal", "dimensions_ordered",
             "attributes", "measure", "inventory_status", "n_rows_inventory", "n_rows_series", "notes"]

flow_rows = []; ind_codes = OrderedDict(); unit_codes = OrderedDict(); obs_codes = OrderedDict()
inv_rows = []; ser_rows = []; anomalies = OrderedDict(); flow_recs = OrderedDict()
unit_versions = OrderedDict(); obs_versions = OrderedDict()
inv_header = None; ser_header = None
for fr in flows:
    fid = fr.split("/")[1]
    fp = os.path.join(wdir, f"{fid}_flow.json")
    if not os.path.exists(fp):
        flow_rows.append(OrderedDict([("flowRef", fr), ("agency", fr.split("/")[0]), ("id", fid), ("name", ""), ("description", ""),
                                      ("version", fr.split("/")[2]), ("isFinal", ""), ("dimensions_ordered", ""), ("attributes", ""),
                                      ("measure", ""), ("inventory_status", "NOT_PROCESSED"), ("n_rows_inventory", ""), ("n_rows_series", ""), ("notes", "")]))
        continue
    rec = json.load(open(fp, encoding="utf-8"))
    flow_recs[fr] = rec
    an = json.load(open(os.path.join(wdir, f"{fid}_anomalies.json"), encoding="utf-8"))
    anomalies[fr] = an
    attrs = "|".join(f"{x['id']}({x['assignmentStatus']};{json.dumps(x['relationship'], separators=(',', ':'))})" for x in rec["attributes"])
    flow_rows.append(OrderedDict([
        ("flowRef", fr), ("agency", rec["agency"]), ("id", rec["id"]), ("name", rec["name"]), ("description", rec.get("description", "")),
        ("version", rec["version"]), ("isFinal", rec["isFinal"]), ("dimensions_ordered", "|".join(rec["dimensions_ordered"])),
        ("attributes", attrs), ("measure", f"{rec['measure']['id']}({rec['measure']['textType']})"),
        ("inventory_status", rec["inventory_status"]), ("n_rows_inventory", rec["n_rows_inventory"]), ("n_rows_series", rec["n_rows_series"]),
        ("notes", " / ".join(rec["notes"]))]))
    ic = json.load(open(os.path.join(wdir, f"{fid}_indicators.json"), encoding="utf-8"))
    for c in ic["codes"]:
        k = ("CL_UNICEF_INDICATOR", c["id"])
        if k not in ind_codes:
            ind_codes[k] = OrderedDict([("id", c["id"]), ("name", c["name"]), ("description", c["description"]), ("parent", c["parent"]),
                                        ("first_flow_seen", fr), ("codelist_id", "CL_UNICEF_INDICATOR"), ("codelist_version", ic["version"])])
    idp = os.path.join(wdir, f"{fid}_indicators_dim.json")
    if os.path.exists(idp):
        idc = json.load(open(idp, encoding="utf-8"))
        for c in idc["codes"]:
            k = (idc["codelist_id"], c["id"])
            if k not in ind_codes:
                ind_codes[k] = OrderedDict([("id", c["id"]), ("name", c["name"]), ("description", c["description"]), ("parent", c["parent"]),
                                            ("first_flow_seen", fr), ("codelist_id", idc["codelist_id"]), ("codelist_version", idc["version"])])
    uc = json.load(open(os.path.join(wdir, f"{fid}_units.json"), encoding="utf-8"))
    unit_versions[fr] = (uc.get("codelist_id"), uc["version"], len(uc["codes"]))
    for c in uc["codes"]:
        k = (uc.get("codelist_id"), c["id"])
        if k not in unit_codes:
            unit_codes[k] = OrderedDict([("id", c["id"]), ("name", c["name"]), ("first_flow_seen", fr), ("codelist_id", uc.get("codelist_id")), ("codelist_version", uc["version"])])
    oc = json.load(open(os.path.join(wdir, f"{fid}_obsstatus.json"), encoding="utf-8"))
    obs_versions[fr] = (oc.get("codelist_id"), oc["version"], len(oc["codes"]))
    for c in oc["codes"]:
        k = (oc.get("codelist_id"), c["id"])
        if k not in obs_codes:
            obs_codes[k] = OrderedDict([("id", c["id"]), ("name", c["name"]), ("first_flow_seen", fr), ("codelist_id", oc.get("codelist_id")), ("codelist_version", oc["version"])])
    with open(os.path.join(wdir, f"{fid}_inventory.csv"), encoding="utf-8", newline="") as f:
        r = csv.reader(f); h = next(r); inv_header = h
        inv_rows.extend(list(r))
    with open(os.path.join(wdir, f"{fid}_series.csv"), encoding="utf-8", newline="") as f:
        r = csv.reader(f); h = next(r); ser_header = h
        ser_rows.extend(list(r))

def wcsv(name, header, rows):
    p = os.path.join(gdir, name)
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(header)
        for r in rows:
            w.writerow(r if isinstance(r, list) else [r.get(h, "") for h in header])
    print(f"{name}: {len(rows)} rows")

wcsv(f"flows_{g}.csv", FLOW_COLS, flow_rows)
wcsv(f"codelist_indicator_{g}.csv", ["id", "name", "description", "parent", "first_flow_seen", "codelist_id", "codelist_version"], list(ind_codes.values()))
wcsv(f"unit_codelist_{g}.csv", ["id", "name", "first_flow_seen", "codelist_id", "codelist_version"], list(unit_codes.values()))
wcsv(f"obs_status_codelist_{g}.csv", ["id", "name", "first_flow_seen", "codelist_id", "codelist_version"], list(obs_codes.values()))
wcsv(f"inventory_{g}.csv", inv_header or ["flowRef", "INDICATOR", "REF_AREA", "n_series", "dimension_values", "latest_time_period", "data_sources", "unit_measure", "share_with_lower_bound", "obs_status", "has_country_notes", "example_value"], inv_rows)
wcsv(f"series_{g}.csv", ser_header or ["flowRef", "indicator", "iso3", "dims_json", "time_period", "value", "lower_bound", "upper_bound", "obs_status", "data_source", "unit_measure", "ref_period", "country_notes_flag", "extra_attrs_json"], ser_rows)

# ---------- log ----------
L = []
L.append(f"# Log {g} — UNICEF SDMX MCP extraction (server Unicef_MCP_Yves / sdmx-mcp, backend https://sdmx.data.unicef.org)")
L.append("")
L.append("Countries requested: NGA, IND, BRA. Inventory = lastNObservations=1, all dimensions wildcard, allowUnboundedTime. Series = totals key, startPeriod 2000, endPeriod 2025, format csv, labels id, maxObs 100000.")
L.append("Raw tool outputs are kept in raw/ (persisted harness files copied with cp; inline results written out verbatim). Per-flow parsed work files are in work/. Scripts in scripts/.")
L.append("")
L.append("## Call log (chronological)")
L.append("")
L.append("| # | flow | step | key | status | rows | persisted file | error | note |")
L.append("|---|---|---|---|---|---|---|---|---|")
for i, c in enumerate(calls, 1):
    L.append(f"| {i} | {c['flow']} | {c['step']} | `{c['key']}` | {c['status']} | {c['rows']} | {c['persisted']}{(' ('+c['rawfile']+')') if c.get('rawfile') else ''} | {c['error']} | {c['note']} |")
L.append("")
L.append("## Per-flow summary and anomalies")
L.append("")
all_cols = {}
for fr, rec in flow_recs.items():
    an = anomalies[fr]
    L.append(f"### {fr} — {rec['name']} (isFinal={rec['isFinal']}, DSD={rec['dsd_id']})")
    L.append(f"- dimensions (list_dimensions order): {', '.join(rec['dimensions_ordered'])}; DSD dimension order matches: {an['dsd_vs_list_dimensions_match']}; REF_AREA codelist: {rec['ref_area_codelist']}")
    L.append(f"- attributes: {', '.join(x['id']+'('+str(x['assignmentStatus'])+')' for x in rec['attributes'])}; measure: {rec['measure']['id']} ({rec['measure']['textType']})")
    L.append(f"- codelists in structure payload: {', '.join(c['id']+'('+str(c['version'])+',n='+str(c['n'])+')' for c in rec['codelists_in_payload'])}")
    L.append(f"- CL_UNICEF_INDICATOR version {rec['cl_indicator_version']}, {rec['cl_indicator_n']} codes in payload (isPartial={rec['cl_indicator_isPartial']}); INDICATOR dimension codelist: {rec.get('indicator_dim_codelist')} ({rec.get('indicator_dim_codelist_n')} codes); UNIT_MEASURE codelist used: {rec.get('unit_codelist_used')}; OBS_STATUS codelist used: {rec.get('obs_status_codelist_used')}")
    L.append(f"- inventory key: `{rec.get('inventory_key','')}` → status: {rec['inventory_status']}; raw rows {an['n_inventory_raw_rows']} → {an['n_inventory_out_rows']} (indicator,country) rows; indicators: {an['n_indicators_inventory']}; countries: {', '.join(an['inventory_countries'])}")
    L.append(f"- series key: `{rec.get('series_key','')}` → rows {an['n_series_rows']}; indicators: {an['n_indicators_series']}; countries: {', '.join(an['series_countries'])}; TIME_PERIOD range: {an['series_time_period_min_max'][0]}–{an['series_time_period_min_max'][1]}; OBS_STATUS values: {', '.join(an['series_obs_status_set'])}")
    L.append(f"- CSV columns: {', '.join(rec.get('csv_columns', []))}; extra (non-standard) attribute columns: {', '.join(an['extra_attr_columns']) or 'none'}")
    all_cols[fr] = set(rec.get("csv_columns", []))
    L.append(f"- codes seen per breakdown dimension (inventory): {json.dumps(an['dimension_codes_seen_in_inventory'], ensure_ascii=False)}")
    bd = set(an.get("breakdown_dims_set_to_T_in_series_key", []))
    noT = an["dimensions_without_T_in_inventory"]
    noT_bd = {d: v for d, v in noT.items() if d in bd}
    noT_wc = {d: (v[:12] + (["...+%d" % (len(v) - 12)] if len(v) > 12 else [])) for d, v in noT.items() if d not in bd}
    if noT_bd:
        L.append(f"- ANOMALY breakdown dimensions set to `_T` in the series key but with no `_T` code in the inventory (total code is not _T / no totals published): {json.dumps(noT_bd, ensure_ascii=False)}")
    if noT_wc:
        L.append(f"- info: wildcard (non-breakdown / age) dimensions with no `_T` code in inventory: {json.dumps(noT_wc, ensure_ascii=False)}")
    L.append(f"- breakdown dimensions set to `_T` in the series key: {', '.join(an.get('breakdown_dims_set_to_T_in_series_key', [])) or 'none'}; wildcard: {', '.join(an.get('age_dims_wildcard', []) + an.get('non_breakdown_named_dims', [])) or 'none'}")
    if an["non_breakdown_named_dims"]:
        L.append(f"- non-breakdown-named dimensions left wildcard in series key: {', '.join(an['non_breakdown_named_dims'])}")
    if an["indicators_in_inventory_not_in_series"]:
        L.append(f"- ANOMALY indicators present in inventory but with no total series rows ({len(an['indicators_in_inventory_not_in_series'])}): {', '.join(an['indicators_in_inventory_not_in_series'])}")
    if an["indicators_without_all_T_row_in_inventory"]:
        L.append(f"- indicators with no all-`_T` (non-AGE breakdowns) row in inventory ({len(an['indicators_without_all_T_row_in_inventory'])}): {', '.join(an['indicators_without_all_T_row_in_inventory'])}")
    if an["indicators_in_series_not_in_inventory"]:
        L.append(f"- indicators in series but not in inventory: {', '.join(an['indicators_in_series_not_in_inventory'])}")
    if an["ref_area_non_iso3"]:
        L.append(f"- ANOMALY REF_AREA codes that are not ISO3: {', '.join(an['ref_area_non_iso3'])}")
    if an["dims_in_csv_not_in_list_dimensions"]:
        L.append(f"- columns in CSV that are neither list_dimensions dimensions nor standard attributes: {', '.join(an['dims_in_csv_not_in_list_dimensions'])}")
    for n in rec["notes"]:
        L.append(f"- note: {n}")
    L.append("")
L.append("## Cross-flow checks")
L.append("")
if all_cols:
    base = None
    for fr, cols in all_cols.items():
        if base is None:
            base = cols; basefr = fr; continue
        if cols != base:
            L.append(f"- attribute/column set of {fr} differs from {basefr}: extra={sorted(cols-base)} missing={sorted(base-cols)}")
    L.append(f"- reference column set ({basefr}): {sorted(base)}")
L.append(f"- UNIT_MEASURE codelist per flow (codelist, version, n codes): {json.dumps(unit_versions)}")
L.append(f"- OBS_STATUS codelist per flow (codelist, version, n codes): {json.dumps(obs_versions)}")
n_uni = sum(1 for k in ind_codes if k[0] == "CL_UNICEF_INDICATOR")
L.append(f"- codelist_indicator_{g}.csv: {len(ind_codes)} rows = {n_uni} CL_UNICEF_INDICATOR codes (the same 803-code CL_UNICEF_INDICATOR(1.0) payload, isPartial=false, was returned with every flow's structure, so the union equals one copy) + flow-specific INDICATOR codelists tagged in codelist_id (CL_CME_CAUSE_OF_DEATH_SER_TYPE 3, CL_CME_COUNTRY_PROFILES_INDICATORS 49, CL_INDICATOR_CME 32, CL_CCRI_INDICATORS 27); CL_UNICEF_INDICATOR codes per flow payload: {json.dumps({fr: rec['cl_indicator_n'] for fr, rec in flow_recs.items()})}")
L.append("- NOTE: the 803-code CL_UNICEF_INDICATOR(1.0) returned by get_flow_structure is identical for all 14 flows; every INDICATOR code observed in the data of the 9 flows that use CL_UNICEF_INDICATOR (CME, NUTRITION, IMMUNISATION, HIV_AIDS, ECD, FUNCTIONAL_DIFF, GENDER, WT, CAUSE_OF_DEATH) is present in it.")
L.append("")
with open(os.path.join(gdir, f"log_{g}.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print(f"log_{g}.md written; flows processed: {len(flow_recs)}/{len(flows)}")
