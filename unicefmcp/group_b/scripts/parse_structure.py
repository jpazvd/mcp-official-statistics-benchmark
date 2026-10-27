#!/usr/bin/env python3
"""Parse a persisted get_flow_structure JSON for one flow.

Usage: python3 -I parse_structure.py <structure.json> <flowRef> <group_dir> <group>

Writes/updates:
  <group_dir>/raw/structure_summary_<flowid>.json   (dataflow meta, attributes, measure, codelist versions)
  <group_dir>/codelist_indicator_<group>.csv        (append, de-dup on id, first_flow_seen)
  <group_dir>/unit_codelist_<group>.csv             (written once per group, from first flow that has it)
  <group_dir>/obs_status_codelist_<group>.csv       (written once per group)
Prints a compact summary to stdout.
"""
import csv
import json
import os
import re
import sys


def main():
    path, flow_ref, group_dir, group = sys.argv[1:5]
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    data = d["data"]
    dfs = data.get("dataflows", [])
    if not dfs:
        print("NO DATAFLOW IN STRUCTURE")
        sys.exit(1)
    df = dfs[0]
    flow_id = df["id"]
    summary = {
        "flowRef": flow_ref,
        "agency": df.get("agencyID"),
        "id": flow_id,
        "name": df.get("name"),
        "description": df.get("description"),
        "version": df.get("version"),
        "isFinal": df.get("isFinal"),
        "structure": df.get("structure"),
    }
    dsds = data.get("dataStructures", [])
    attrs = []
    measure = None
    dims = []
    if dsds:
        dsd = dsds[0]
        comp = dsd.get("dataStructureComponents", {})
        for a in comp.get("attributeList", {}).get("attributes", []):
            rel = a.get("attributeRelationship", {})
            attrs.append({
                "id": a.get("id"),
                "assignmentStatus": a.get("assignmentStatus"),
                "relationship": rel,
                "codelist": (a.get("localRepresentation") or {}).get("enumeration"),
            })
        pm = comp.get("measureList", {}).get("primaryMeasure")
        if pm:
            measure = pm.get("id")
        dl = comp.get("dimensionList", {})
        for dim in dl.get("dimensions", []):
            dims.append({"id": dim["id"], "position": dim.get("position"),
                         "codelist": (dim.get("localRepresentation") or {}).get("enumeration")})
        for dim in dl.get("timeDimensions", []):
            dims.append({"id": dim["id"], "position": dim.get("position"), "codelist": None})
        summary["dsd_id"] = dsd.get("id")
        summary["dsd_name"] = dsd.get("name")
        summary["dsd_version"] = dsd.get("version")
    summary["attributes"] = attrs
    summary["primary_measure"] = measure
    summary["dimensions"] = sorted(dims, key=lambda x: x["position"] or 0)

    codelists = data.get("codelists", [])
    summary["codelists"] = [{"agency": c.get("agencyID"), "id": c.get("id"), "version": c.get("version"),
                             "n_codes": len(c.get("codes", []))} for c in codelists]

    def find_cl(cl_id):
        # prefer the UNICEF-agency codelist (the DSD references UNICEF:CL_UNIT_MEASURE / CL_OBS_STATUS);
        # fall back to any agency; if several versions, take the highest-numbered UNICEF one.
        cands = [c for c in codelists if c.get("id") == cl_id]
        if not cands:
            return None
        uni = [c for c in cands if c.get("agencyID") == "UNICEF"]
        pool = uni or cands
        return sorted(pool, key=lambda c: str(c.get("version")))[-1]

    # --- indicator codelist (CL_UNICEF_INDICATOR, or whatever the INDICATOR dimension references) ---------
    ind_dim = next((x for x in dims if x["id"] == "INDICATOR"), None)
    ind_cl_urn = (ind_dim or {}).get("codelist") or ""
    m = re.search(r"Codelist=([^:]+):([^(]+)\(([^)]+)\)", ind_cl_urn)
    ind_cl_agency, ind_cl_id, ind_cl_ver = (m.group(1), m.group(2), m.group(3)) if m else ("UNICEF", "CL_UNICEF_INDICATOR", None)
    ind = None
    for c in codelists:
        if c.get("id") == ind_cl_id and (c.get("agencyID") == ind_cl_agency) and (ind_cl_ver is None or str(c.get("version")) == ind_cl_ver):
            ind = c
            break
    if ind is None:
        ind = find_cl(ind_cl_id)
    summary["indicator_codelist_urn"] = ind_cl_urn
    ind_path = os.path.join(group_dir, f"codelist_indicator_{group}.csv")
    n_new = 0
    header = ["codelist_id", "id", "name", "description", "parent", "codelist_version", "first_flow_seen"]
    existing = set()
    if os.path.exists(ind_path):
        with open(ind_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if rows and "codelist_id" not in rows[0]:
            # migrate older file (written before codelist_id existed): all rows were CL_UNICEF_INDICATOR
            with open(ind_path, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=header)
                w.writeheader()
                for r in rows:
                    r["codelist_id"] = "CL_UNICEF_INDICATOR"
                    w.writerow(r)
        for r in rows:
            existing.add((r.get("codelist_id") or "CL_UNICEF_INDICATOR", r["id"]))
    if ind is not None:
        summary["indicator_codelist_id"] = ind.get("id")
        summary["indicator_codelist_agency"] = ind.get("agencyID")
        summary["indicator_codelist_version"] = ind.get("version")
        summary["indicator_codelist_n_codes"] = len(ind.get("codes", []))
        write_header = not os.path.exists(ind_path)
        with open(ind_path, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if write_header:
                w.writerow(header)
            for c in ind.get("codes", []):
                key = (ind.get("id"), c.get("id"))
                if key in existing:
                    continue
                existing.add(key)
                w.writerow([ind.get("id"), c.get("id"), c.get("name", ""), c.get("description", ""), c.get("parent", ""),
                            ind.get("version"), flow_ref])
                n_new += 1
    else:
        summary["indicator_codelist_id"] = ind_cl_id
        summary["indicator_codelist_version"] = None
        summary["indicator_codelist_n_codes"] = 0
    summary["indicator_codes_appended"] = n_new

    # --- CL_UNIT_MEASURE / CL_OBS_STATUS once per group ----------------------
    for cl_id, fname in (("CL_UNIT_MEASURE", f"unit_codelist_{group}.csv"),
                         ("CL_OBS_STATUS", f"obs_status_codelist_{group}.csv")):
        cl = find_cl(cl_id)
        out = os.path.join(group_dir, fname)
        if cl is None:
            summary[f"{cl_id}_present"] = False
            continue
        summary[f"{cl_id}_present"] = True
        summary[f"{cl_id}_version"] = cl.get("version")
        summary[f"{cl_id}_n_codes"] = len(cl.get("codes", []))
        if not os.path.exists(out):
            with open(out, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["id", "name", "codelist_version", "source_flow"])
                for c in cl.get("codes", []):
                    w.writerow([c.get("id"), c.get("name", ""), cl.get("version"), flow_ref])
            summary[f"{cl_id}_written"] = True
        else:
            # check for codes not already present (log only, do not duplicate)
            with open(out, newline="", encoding="utf-8") as f:
                have = {r["id"] for r in csv.DictReader(f)}
            missing = [c.get("id") for c in cl.get("codes", []) if c.get("id") not in have]
            summary[f"{cl_id}_written"] = False
            summary[f"{cl_id}_codes_missing_from_group_file"] = missing
            if missing:
                with open(out, "a", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    for c in cl.get("codes", []):
                        if c.get("id") in missing:
                            w.writerow([c.get("id"), c.get("name", ""), cl.get("version"), flow_ref])

    out_path = os.path.join(group_dir, "raw", f"structure_summary_{flow_id}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)

    # compact stdout
    print(f"flowRef={flow_ref} id={flow_id} agency={summary['agency']} name={summary['name']!r} "
          f"version={summary['version']} isFinal={summary['isFinal']}")
    print(f"description={str(summary['description'])[:300]!r}")
    print(f"structure={summary['structure']}")
    print(f"dsd={summary.get('dsd_id')} v{summary.get('dsd_version')} measure={measure}")
    print("dimensions:", [(x["id"], (x["codelist"] or "").split("=")[-1]) for x in summary["dimensions"]])
    print("attributes:")
    for a in attrs:
        print(f"  {a['id']}: {a['assignmentStatus']} rel={json.dumps(a['relationship'])} cl={(a['codelist'] or '').split('=')[-1]}")
    print("codelists:", [(c["id"], c["version"], c["n_codes"]) for c in summary["codelists"]])
    print(f"INDICATOR codelist {summary.get('indicator_codelist_id')} ({summary.get('indicator_codelist_agency')}): version={summary.get('indicator_codelist_version')} "
          f"n={summary.get('indicator_codelist_n_codes')} appended_new={n_new}")
    for cl_id in ("CL_UNIT_MEASURE", "CL_OBS_STATUS"):
        print(f"{cl_id}: present={summary.get(cl_id+'_present')} version={summary.get(cl_id+'_version')} "
              f"n={summary.get(cl_id+'_n_codes')} written_now={summary.get(cl_id+'_written')} "
              f"missing_added={summary.get(cl_id+'_codes_missing_from_group_file')}")


if __name__ == "__main__":
    main()
