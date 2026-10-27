#!/usr/bin/env python3
"""Process one dataflow's raw tool outputs into per-flow work files.

usage:
  process_flow.py --group-dir DIR --flow FLOWREF --dims DIMS.json --structure STRUCT.json
                  [--inventory FILE ...] [--series FILE ...]
                  [--inventory-status TEXT] [--note TEXT ...]

Inputs (--inventory / --series) may be either a persisted MCP query_data JSON
result (object with "raw_csv") or a plain CSV file (raw_csv written out verbatim).
Nothing is invented: every value is copied from the tool outputs.

Writes under DIR/work/:
  <ID>_flow.json, <ID>_indicators.json, <ID>_units.json, <ID>_obsstatus.json,
  <ID>_inventory.csv, <ID>_series.csv, <ID>_anomalies.json, <ID>_columns.json
"""
import argparse, csv, io, json, os, sys
from collections import OrderedDict, defaultdict

SERIES_COLS = ["flowRef", "indicator", "iso3", "dims_json", "time_period", "value",
               "lower_bound", "upper_bound", "obs_status", "data_source", "unit_measure",
               "ref_period", "country_notes_flag", "extra_attrs_json"]
INV_COLS = ["flowRef", "INDICATOR", "REF_AREA", "n_series", "dimension_values", "latest_time_period",
            "data_sources", "unit_measure", "share_with_lower_bound", "obs_status",
            "has_country_notes", "example_value"]
STD_ATTR = {"OBS_VALUE", "TIME_PERIOD", "LOWER_BOUND", "UPPER_BOUND", "OBS_STATUS",
            "DATA_SOURCE", "UNIT_MEASURE", "REF_PERIOD", "COUNTRY_NOTES"}
NON_BREAKDOWN_HINTS = ("VACCINE", "WASH_SERVICE", "UNIT", "FREQ", "TIME_PERIOD_METHOD",
                       "VALUE_TYPE", "CAUSE", "SERVICE", "DOMAIN", "HAZARD", "SOURCE", "THRESHOLD", "SERIES", "PARENT", "ADMIN")


def load_csv_text(path):
    """Return (csv_text, provenance_dict_or_None, persisted_flag)."""
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    s = txt.lstrip()
    if s.startswith("{"):
        d = json.loads(txt)
        prov = {k: v for k, v in d.items() if k != "raw_csv"}
        raw = d.get("raw_csv")
        if raw is None:
            return "", prov, True
        return raw, prov, True
    return txt, None, False


def parse_csv(text):
    if not text.strip():
        return [], []
    rdr = csv.reader(io.StringIO(text))
    rows = list(rdr)
    header = rows[0]
    body = [r for r in rows[1:] if any(c != "" for c in r)]
    out = []
    for r in body:
        if len(r) != len(header):
            # pad/truncate defensively but record
            r = (r + [""] * len(header))[:len(header)]
        out.append(OrderedDict(zip(header, r)))
    return header, out


def is_iso3(code):
    return len(code) == 3 and code.isalpha() and code.isupper()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group-dir", required=True)
    ap.add_argument("--flow", required=True)
    ap.add_argument("--dims", required=True)
    ap.add_argument("--structure", required=True)
    ap.add_argument("--inventory", action="append", default=[])
    ap.add_argument("--series", action="append", default=[])
    ap.add_argument("--inventory-status", default="")
    ap.add_argument("--note", action="append", default=[])
    ap.add_argument("--series-key", default="")
    ap.add_argument("--inventory-key", default="")
    a = ap.parse_args()

    gdir = a.group_dir
    wdir = os.path.join(gdir, "work")
    os.makedirs(wdir, exist_ok=True)
    flow_ref = a.flow
    agency, fid, ver = flow_ref.split("/")

    # ---------- A. dimensions ----------
    dims_doc = json.load(open(a.dims, encoding="utf-8"))
    dims = dims_doc["result"] if isinstance(dims_doc, dict) and "result" in dims_doc else dims_doc
    dims = sorted(dims, key=lambda x: x.get("position", 0))
    dim_ids = [d["id"] for d in dims]
    dim_cl = {d["id"]: d.get("codelist") for d in dims}

    # ---------- B. structure ----------
    st = json.load(open(a.structure, encoding="utf-8"))
    data = st.get("data", {})
    dfs = data.get("dataflows", [])
    df = dfs[0] if dfs else {}
    dsd = (data.get("dataStructures") or [{}])[0]
    comp = dsd.get("dataStructureComponents", {})
    attrs = []
    for at in comp.get("attributeList", {}).get("attributes", []):
        rel = at.get("attributeRelationship", {})
        attrs.append({"id": at["id"], "assignmentStatus": at.get("assignmentStatus"),
                      "relationship": rel,
                      "codelist": (at.get("localRepresentation") or {}).get("enumeration")})
    pm = comp.get("measureList", {}).get("primaryMeasure", {})
    measure = {"id": pm.get("id"), "textType": ((pm.get("localRepresentation") or {}).get("textFormat") or {}).get("textType")}
    dsd_dims = [d["id"] for d in sorted(comp.get("dimensionList", {}).get("dimensions", []), key=lambda x: x.get("position", 0))]
    time_dims = [d["id"] for d in comp.get("dimensionList", {}).get("timeDimensions", [])]

    codelists = {}
    for cl in data.get("codelists", []):
        codelists[(cl.get("agencyID"), cl["id"], cl.get("version"))] = cl

    def find_cl(cid, prefer_agency="UNICEF"):
        hits = [cl for (ag, i, v), cl in codelists.items() if i == cid]
        for cl in hits:
            if cl.get("agencyID") == prefer_agency:
                return cl
        return hits[0] if hits else None

    def find_cl_by_urn(urn):
        # urn like urn:sdmx:org.sdmx.infomodel.codelist.Codelist=UNICEF:CL_X(1.0)
        if not urn:
            return None
        tail = urn.split("=")[-1]
        ag, rest = tail.split(":", 1)
        cid, ver = rest.split("(")[0], rest.split("(")[1].rstrip(")")
        return codelists.get((ag, cid, ver))

    cl_ind = find_cl("CL_UNICEF_INDICATOR")
    ind_codes = []
    if cl_ind:
        for c in cl_ind.get("codes", []):
            ind_codes.append({"id": c["id"], "name": c.get("name", ""), "description": c.get("description", ""),
                              "parent": c.get("parent", "")})
    cl_unit = find_cl("CL_UNIT_MEASURE")
    cl_obs = find_cl("CL_OBS_STATUS")
    # prefer the codelists actually referenced by the DSD attributes
    for at in attrs:
        if at["id"] == "UNIT_MEASURE" and at.get("codelist"):
            cl_unit = find_cl_by_urn(at["codelist"]) or cl_unit
        if at["id"] == "OBS_STATUS" and at.get("codelist"):
            cl_obs = find_cl_by_urn(at["codelist"]) or cl_obs
    # the codelist actually used by the INDICATOR dimension
    ind_dim_cl = find_cl_by_urn(dim_cl.get("INDICATOR"))
    ind_dim_codes = []
    if ind_dim_cl is not None and ind_dim_cl.get("id") != "CL_UNICEF_INDICATOR":
        for c in ind_dim_cl.get("codes", []):
            ind_dim_codes.append({"id": c["id"], "name": c.get("name", ""), "description": c.get("description", ""),
                                  "parent": c.get("parent", "")})
    unit_codes = [{"id": c["id"], "name": c.get("name", "")} for c in (cl_unit or {}).get("codes", [])]
    obs_codes = [{"id": c["id"], "name": c.get("name", "")} for c in (cl_obs or {}).get("codes", [])]
    # REF_AREA codelist info
    ref_cl_urn = dim_cl.get("REF_AREA", "")
    ref_cl_id = ref_cl_urn.split("=")[-1].split("(")[0].split(":")[-1] if ref_cl_urn else ""

    flow_rec = {
        "flowRef": flow_ref, "agency": df.get("agencyID", agency), "id": df.get("id", fid),
        "name": df.get("name", ""), "description": df.get("description", ""),
        "version": df.get("version", ver), "isFinal": df.get("isFinal"),
        "structure": df.get("structure", ""), "dsd_id": dsd.get("id"), "dsd_name": dsd.get("name"),
        "dimensions_ordered": dim_ids, "dsd_dimensions": dsd_dims, "time_dimensions": time_dims,
        "dimension_codelists": dim_cl, "attributes": attrs, "measure": measure,
        "codelists_in_payload": [{"agency": k[0], "id": k[1], "version": k[2], "n": len(v.get("codes", []))} for k, v in codelists.items()],
        "cl_indicator_version": (cl_ind or {}).get("version"), "cl_indicator_n": len(ind_codes),
        "cl_indicator_isPartial": (cl_ind or {}).get("isPartial"),
        "cl_unit_version": (cl_unit or {}).get("version"), "cl_obs_status_version": (cl_obs or {}).get("version"),
        "ref_area_codelist": ref_cl_id,
        "indicator_dim_codelist": (ind_dim_cl or {}).get("id"), "indicator_dim_codelist_version": (ind_dim_cl or {}).get("version"),
        "indicator_dim_codelist_n": len((ind_dim_cl or {}).get("codes", [])),
        "unit_codelist_used": f"{(cl_unit or {}).get('agencyID')}:{(cl_unit or {}).get('id')}({(cl_unit or {}).get('version')})",
        "obs_status_codelist_used": f"{(cl_obs or {}).get('agencyID')}:{(cl_obs or {}).get('id')}({(cl_obs or {}).get('version')})",
        "inventory_status": a.inventory_status, "notes": list(a.note),
        "inventory_key": a.inventory_key, "series_key": a.series_key,
    }

    # ---------- C. inventory ----------
    inv_rows = []
    inv_headers = []
    inv_prov = []
    for p in a.inventory:
        text, prov, persisted = load_csv_text(p)
        h, rows = parse_csv(text)
        inv_headers.append({"file": p, "header": h, "n": len(rows), "persisted": persisted})
        if prov:
            inv_prov.append({"file": p, "provenance": prov.get("provenance"), "status": prov.get("status"), "notes": prov.get("notes"), "error": prov.get("error")})
        inv_rows.extend(rows)
    # de-duplicate exact duplicate rows across merged files
    seen = set(); dedup = []
    for r in inv_rows:
        k = tuple(r.items())
        if k in seen:
            continue
        seen.add(k); dedup.append(r)
    inv_rows = dedup

    other_dims = [d for d in dim_ids if d not in ("REF_AREA", "INDICATOR")]
    grp = OrderedDict()
    for r in inv_rows:
        key = (r.get("INDICATOR", ""), r.get("REF_AREA", ""))
        grp.setdefault(key, []).append(r)

    inv_out = []
    for (ind, ra), rows in grp.items():
        series_keys = set(tuple(r.get(d, "") for d in dim_ids) for r in rows)
        dv = OrderedDict()
        for d in other_dims:
            vals = sorted(set(r.get(d, "") for r in rows))
            dv[d] = vals[:12] + (["...+%d" % (len(vals) - 12)] if len(vals) > 12 else [])
        tps = [r.get("TIME_PERIOD", "") for r in rows if r.get("TIME_PERIOD", "") != ""]
        latest = max(tps) if tps else ""
        ds = sorted(set(r.get("DATA_SOURCE", "") for r in rows if r.get("DATA_SOURCE", "") != ""))
        um = sorted(set(r.get("UNIT_MEASURE", "") for r in rows if r.get("UNIT_MEASURE", "") != ""))
        obs = sorted(set(r.get("OBS_STATUS", "") for r in rows if r.get("OBS_STATUS", "") != ""))
        n_lb = sum(1 for r in rows if r.get("LOWER_BOUND", "") != "")
        has_cn = 1 if any(r.get("COUNTRY_NOTES", "") != "" for r in rows) else 0
        ex = rows[0].get("OBS_VALUE", "")
        inv_out.append(OrderedDict([
            ("flowRef", flow_ref), ("INDICATOR", ind), ("REF_AREA", ra), ("n_series", len(series_keys)),
            ("dimension_values", json.dumps(dv, separators=(",", ":"), ensure_ascii=False)),
            ("latest_time_period", latest), ("data_sources", "|".join(ds)), ("unit_measure", "|".join(um)),
            ("share_with_lower_bound", round(n_lb / len(rows), 4) if rows else ""),
            ("obs_status", "|".join(obs)), ("has_country_notes", has_cn), ("example_value", ex)]))

    with open(os.path.join(wdir, f"{fid}_inventory.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=INV_COLS)
        w.writeheader()
        for r in inv_out:
            w.writerow(r)

    # ---------- D. series ----------
    ser_headers = []
    ser_prov = []
    ser_rows = []
    for p in a.series:
        text, prov, persisted = load_csv_text(p)
        h, rows = parse_csv(text)
        ser_headers.append({"file": p, "header": h, "n": len(rows), "persisted": persisted})
        if prov:
            ser_prov.append({"file": p, "provenance": prov.get("provenance"), "status": prov.get("status"), "notes": prov.get("notes"), "error": prov.get("error")})
        ser_rows.extend(rows)
    seen = set(); dedup = []
    for r in ser_rows:
        k = tuple(r.items())
        if k in seen:
            continue
        seen.add(k); dedup.append(r)
    ser_rows = dedup

    dims_in_row = [d for d in dim_ids if d not in ("REF_AREA", "INDICATOR", "TIME_PERIOD")]
    all_cols = set()
    for h in ser_headers:
        all_cols |= set(h["header"])
    extra_cols = sorted(c for c in all_cols if c not in STD_ATTR and c not in dim_ids and c != "TIME_PERIOD")

    with open(os.path.join(wdir, f"{fid}_series.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(SERIES_COLS)
        for r in ser_rows:
            dj = OrderedDict((d, r.get(d, "")) for d in dims_in_row)
            extra = OrderedDict((c, r[c]) for c in extra_cols if c in r and r[c] != "")
            w.writerow([flow_ref, r.get("INDICATOR", ""), r.get("REF_AREA", ""),
                        json.dumps(dj, separators=(",", ":"), ensure_ascii=False),
                        r.get("TIME_PERIOD", ""), r.get("OBS_VALUE", ""), r.get("LOWER_BOUND", ""), r.get("UPPER_BOUND", ""),
                        r.get("OBS_STATUS", ""), r.get("DATA_SOURCE", ""), r.get("UNIT_MEASURE", ""), r.get("REF_PERIOD", ""),
                        1 if r.get("COUNTRY_NOTES", "") != "" else 0,
                        json.dumps(extra, separators=(",", ":"), ensure_ascii=False)])

    # ---------- anomalies ----------
    anomalies = OrderedDict()
    # dimensions whose total is not _T (from inventory codes)
    dim_codes_seen = {d: sorted(set(r.get(d, "") for r in inv_rows)) for d in other_dims}
    no_T = {d: v for d, v in dim_codes_seen.items() if inv_rows and "_T" not in v}
    anomalies["dimensions_without_T_in_inventory"] = no_T
    anomalies["dimension_codes_seen_in_inventory"] = {d: (v[:40] + (["...+%d" % (len(v) - 40)] if len(v) > 40 else [])) for d, v in dim_codes_seen.items()}
    # dims with non-breakdown-looking names
    anomalies["non_breakdown_named_dims"] = [d for d in other_dims if any(h in d for h in NON_BREAKDOWN_HINTS) or dim_cl.get(d) is None]
    anomalies["age_dims_wildcard"] = [d for d in other_dims if "AGE" in d]
    # indicators with no total series: present in inventory but absent in series rows
    inv_inds = set(k[0] for k in grp.keys())
    ser_inds = set(r.get("INDICATOR", "") for r in ser_rows)
    anomalies["indicators_in_inventory_not_in_series"] = sorted(inv_inds - ser_inds)
    anomalies["indicators_in_series_not_in_inventory"] = sorted(ser_inds - inv_inds)
    # indicators where no inventory row has _T on every breakdown dim (AGE excluded)
    bd = [d for d in other_dims if "AGE" not in d and d not in anomalies["non_breakdown_named_dims"]]
    anomalies["breakdown_dims_set_to_T_in_series_key"] = bd
    no_total = []
    for ind in sorted(inv_inds):
        rows = [r for (i, ra), rs in grp.items() if i == ind for r in rs]
        if bd and not any(all(r.get(d, "") == "_T" for d in bd) for r in rows):
            no_total.append(ind)
    anomalies["indicators_without_all_T_row_in_inventory"] = no_total
    # REF_AREA codes not ISO3
    ras = sorted(set(r.get("REF_AREA", "") for r in inv_rows) | set(r.get("REF_AREA", "") for r in ser_rows))
    anomalies["ref_area_codes_seen"] = ras[:60] + (["...+%d" % (len(ras) - 60)] if len(ras) > 60 else [])
    anomalies["ref_area_non_iso3"] = [x for x in ras if not is_iso3(x)][:60]
    # series: indicators / countries counts
    anomalies["series_time_period_min_max"] = [min((r.get("TIME_PERIOD", "") for r in ser_rows), default=""), max((r.get("TIME_PERIOD", "") for r in ser_rows), default="")]
    anomalies["series_obs_status_set"] = sorted(set(r.get("OBS_STATUS", "") for r in ser_rows))
    anomalies["series_countries"] = sorted(set(r.get("REF_AREA", "") for r in ser_rows))
    anomalies["inventory_countries"] = sorted(set(r.get("REF_AREA", "") for r in inv_rows))
    anomalies["n_inventory_raw_rows"] = len(inv_rows)
    anomalies["n_inventory_out_rows"] = len(inv_out)
    anomalies["n_series_rows"] = len(ser_rows)
    anomalies["n_indicators_inventory"] = len(inv_inds)
    anomalies["n_indicators_series"] = len(ser_inds)
    anomalies["inventory_headers"] = inv_headers
    anomalies["series_headers"] = ser_headers
    anomalies["extra_attr_columns"] = extra_cols
    anomalies["inventory_provenance"] = inv_prov
    anomalies["series_provenance"] = ser_prov
    anomalies["dsd_vs_list_dimensions_match"] = (dsd_dims == dim_ids)
    anomalies["dims_in_csv_not_in_list_dimensions"] = sorted(c for c in all_cols if c not in dim_ids and c not in STD_ATTR and c != "TIME_PERIOD")

    flow_rec["n_rows_inventory"] = len(inv_out)
    flow_rec["n_rows_series"] = len(ser_rows)
    flow_rec["csv_columns"] = sorted(all_cols | set().union(*[set(h["header"]) for h in inv_headers]) if (inv_headers or ser_headers) else [])
    flow_rec["extra_attr_columns"] = extra_cols

    json.dump(flow_rec, open(os.path.join(wdir, f"{fid}_flow.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump({"version": (cl_ind or {}).get("version"), "codes": ind_codes}, open(os.path.join(wdir, f"{fid}_indicators.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump({"codelist_id": (ind_dim_cl or {}).get("id"), "version": (ind_dim_cl or {}).get("version"), "codes": ind_dim_codes}, open(os.path.join(wdir, f"{fid}_indicators_dim.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump({"codelist_id": f"{(cl_unit or {}).get('agencyID')}:{(cl_unit or {}).get('id')}", "version": (cl_unit or {}).get("version"), "codes": unit_codes}, open(os.path.join(wdir, f"{fid}_units.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump({"codelist_id": f"{(cl_obs or {}).get('agencyID')}:{(cl_obs or {}).get('id')}", "version": (cl_obs or {}).get("version"), "codes": obs_codes}, open(os.path.join(wdir, f"{fid}_obsstatus.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(anomalies, open(os.path.join(wdir, f"{fid}_anomalies.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # summary
    print(f"FLOW {flow_ref}: name={flow_rec['name']!r} isFinal={flow_rec['isFinal']} dims={dim_ids}")
    print(f"  attrs={[x['id'] for x in attrs]} measure={measure}")
    print(f"  CL_UNICEF_INDICATOR v{flow_rec['cl_indicator_version']} n={len(ind_codes)} | units {flow_rec['unit_codelist_used']} n={len(unit_codes)} | obs_status {flow_rec['obs_status_codelist_used']} n={len(obs_codes)} | REF_AREA cl={ref_cl_id} | INDICATOR dim cl={flow_rec['indicator_dim_codelist']} n={flow_rec['indicator_dim_codelist_n']}")
    print(f"  inventory: raw rows={len(inv_rows)} -> out rows={len(inv_out)}; indicators={len(inv_inds)}; countries={anomalies['inventory_countries']}")
    print(f"  series: rows={len(ser_rows)}; indicators={len(ser_inds)}; countries={anomalies['series_countries']}; time={anomalies['series_time_period_min_max']}")
    print(f"  dims without _T in inventory: {no_T}")
    print(f"  non-breakdown-named dims: {anomalies['non_breakdown_named_dims']}")
    print(f"  indicators in inventory not in series ({len(anomalies['indicators_in_inventory_not_in_series'])}): {anomalies['indicators_in_inventory_not_in_series'][:30]}")
    print(f"  indicators w/o all-_T row in inventory ({len(no_total)}): {no_total[:30]}")
    print(f"  extra attr cols: {extra_cols}; ref_area non-iso3: {anomalies['ref_area_non_iso3'][:10]}")
    print(f"  csv columns: {flow_rec['csv_columns']}")


if __name__ == "__main__":
    main()
