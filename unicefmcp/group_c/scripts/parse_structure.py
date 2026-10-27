#!/usr/bin/env python3
"""Parse a persisted get_flow_structure payload for one flow.

Usage: python3 -I parse_structure.py <flowRef> <structure_json_path>

Writes/updates (under unicefmcp/group_c/):
  raw/meta_<FLOWID>.json           extracted dataflow/DSD metadata (one per flow)
  codelist_indicator_group_c.csv   every code of the INDICATOR codelist(s), de-duplicated on
                                   (codelist_id, id) with first_flow_seen
  unit_codelist_group_c.csv        CL_UNIT_MEASURE codes (written once; later flows are
                                   compared and differences reported on stdout)
  obs_status_codelist_group_c.csv  CL_OBS_STATUS codes (same rule)
Prints a short summary (JSON) on stdout for the log.
"""
import csv
import json
import os
import sys

import os as _os
BASE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the group_c folder
flow_ref, path = sys.argv[1], sys.argv[2]
flow_id = flow_ref.split("/")[1]

with open(path, encoding="utf-8") as fh:
    d = json.load(fh)

data = d["data"]
df = data["dataflows"][0]
dsd = data["dataStructures"][0]
comps = dsd["dataStructureComponents"]

dims = [(x["position"], x["id"], x.get("localRepresentation", {}).get("enumeration"))
        for x in comps["dimensionList"].get("dimensions", [])]
dims.sort()
time_dims = [x["id"] for x in comps["dimensionList"].get("timeDimensions", [])]
attrs = []
for a in comps["attributeList"].get("attributes", []):
    attrs.append({
        "id": a["id"],
        "assignmentStatus": a.get("assignmentStatus"),
        "relationship": a.get("attributeRelationship"),
        "codelist": a.get("localRepresentation", {}).get("enumeration"),
    })
pm = comps["measureList"].get("primaryMeasure", {})
measure = {"id": pm.get("id"), "representation": pm.get("localRepresentation")}

codelists = {c["id"]: c for c in data.get("codelists", [])}
cl_versions = {c["id"]: {"version": c.get("version"), "agencyID": c.get("agencyID"),
                         "n_codes": len(c.get("codes", []))} for c in data.get("codelists", [])}

# which codelist does the INDICATOR dimension use?
ind_cl_urn = None
for _, did, urn in dims:
    if did == "INDICATOR":
        ind_cl_urn = urn
ind_cl_id = ind_cl_urn.split("=")[1].split(":")[1].split("(")[0] if ind_cl_urn else None

meta = {
    "flowRef": flow_ref,
    "dataflow": {k: df.get(k) for k in ("id", "name", "description", "version", "isFinal",
                                        "agencyID", "structure", "isExternalReference")},
    "dsd": {"id": dsd.get("id"), "name": dsd.get("name"), "version": dsd.get("version"),
            "agencyID": dsd.get("agencyID"), "isFinal": dsd.get("isFinal")},
    "dimensions": [{"position": p, "id": i, "codelist": u} for p, i, u in dims],
    "timeDimensions": time_dims,
    "attributes": attrs,
    "primaryMeasure": measure,
    "indicator_codelist": ind_cl_id,
    "codelists": cl_versions,
    "hierarchicalCodelists_n": len(d.get("hierarchicalCodelists", [])),
    "meta_prepared": d.get("meta", {}).get("prepared"),
}
with open(os.path.join(BASE, "raw", f"meta_{flow_id}.json"), "w", encoding="utf-8") as fh:
    json.dump(meta, fh, indent=1, ensure_ascii=False)


def write_or_compare(cl_id, out_name):
    """Write codelist once per group; if the file exists, compare and report differences."""
    out = os.path.join(BASE, out_name)
    cl = codelists.get(cl_id)
    if cl is None:
        return f"{cl_id}: NOT PRESENT in this structure"
    rows = [(c["id"], c.get("name", "")) for c in cl.get("codes", [])]
    if not os.path.exists(out):
        with open(out, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["id", "name", "codelist_id", "codelist_version", "first_flow_seen"])
            for cid, name in rows:
                w.writerow([cid, name, cl_id, cl.get("version"), flow_ref])
        return f"{cl_id} v{cl.get('version')}: written ({len(rows)} codes)"
    with open(out, newline="", encoding="utf-8") as fh:
        existing = {r["id"]: r for r in csv.DictReader(fh)}
    new = [(cid, name) for cid, name in rows if cid not in existing]
    missing = [cid for cid in existing if cid not in {r[0] for r in rows}]
    if new:
        with open(out, "a", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            for cid, name in new:
                w.writerow([cid, name, cl_id, cl.get("version"), flow_ref])
    ver_existing = {r["codelist_version"] for r in existing.values()}
    return (f"{cl_id} v{cl.get('version')}: {len(rows)} codes; new vs file: {len(new)} "
            f"{[n[0] for n in new][:20]}; absent here but in file: {len(missing)} {missing[:20]}; "
            f"file version(s) {sorted(ver_existing)}")


unit_msg = write_or_compare("CL_UNIT_MEASURE", "unit_codelist_group_c.csv")
obs_msg = write_or_compare("CL_OBS_STATUS", "obs_status_codelist_group_c.csv")

# indicator codelist: CL_UNICEF_INDICATOR always if present, plus the flow's own INDICATOR codelist
ind_out = os.path.join(BASE, "codelist_indicator_group_c.csv")
targets = []
if "CL_UNICEF_INDICATOR" in codelists:
    targets.append("CL_UNICEF_INDICATOR")
if ind_cl_id and ind_cl_id in codelists and ind_cl_id not in targets:
    targets.append(ind_cl_id)
existing = set()
if os.path.exists(ind_out):
    with open(ind_out, newline="", encoding="utf-8") as fh:
        existing = {(r["codelist_id"], r["id"]) for r in csv.DictReader(fh)}
else:
    with open(ind_out, "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerow(["id", "name", "description", "parent", "codelist_id",
                                 "codelist_version", "first_flow_seen"])
added = {}
ind_info = {}
with open(ind_out, "a", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    for cl_id in targets:
        cl = codelists[cl_id]
        ind_info[cl_id] = {"version": cl.get("version"), "n_codes": len(cl.get("codes", []))}
        n = 0
        for c in cl.get("codes", []):
            key = (cl_id, c["id"])
            if key in existing:
                continue
            existing.add(key)
            w.writerow([c["id"], c.get("name", ""), c.get("description", ""), c.get("parent", ""),
                        cl_id, cl.get("version"), flow_ref])
            n += 1
        added[cl_id] = n

summary = {
    "flowRef": flow_ref,
    "dataflow": meta["dataflow"],
    "dsd": meta["dsd"],
    "dimensions": [i for _, i, _ in dims] + time_dims,
    "attributes": [(a["id"], a["assignmentStatus"], json.dumps(a["relationship"])) for a in attrs],
    "measure": measure["id"],
    "indicator_codelist_of_flow": ind_cl_id,
    "indicator_codelists_parsed": ind_info,
    "indicator_codes_added": added,
    "unit": unit_msg,
    "obs_status": obs_msg,
    "codelists_in_payload": {k: v["n_codes"] for k, v in cl_versions.items()},
}
print(json.dumps(summary, ensure_ascii=False, indent=1))
