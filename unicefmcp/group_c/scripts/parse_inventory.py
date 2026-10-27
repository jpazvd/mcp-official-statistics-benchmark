#!/usr/bin/env python3
"""Build inventory rows for one flow from one or more persisted query_data results.

Usage: python3 -I parse_inventory.py <flowRef> <result_json> [<result_json> ...]

Appends one row per (flowRef, INDICATOR, REF_AREA) to inventory_group_c.csv (header written
on first use). Rows from several result files (e.g. per-country retries) are merged and
de-duplicated on the full dimension key + TIME_PERIOD before aggregation.
Prints a JSON summary for the log.
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BASE, ISO3_RE, dims_for, load_query_result  # noqa: E402

flow_ref = sys.argv[1]
paths = sys.argv[2:]
dims = dims_for(flow_ref)
area_dim = dims[0]          # REF_AREA (or COUNTRY for SDG_PROG_ASSESSMENT)
ind_dim = "INDICATOR"
other_dims = [x for x in dims if x not in (area_dim, ind_dim)]

OUT = os.path.join(BASE, "inventory_group_c.csv")
COLS = ["flowRef", "INDICATOR", "REF_AREA", "n_series", "dimension_values", "latest_time_period",
        "data_sources", "unit_measure", "share_with_lower_bound", "obs_status",
        "has_country_notes", "example_value"]

all_rows = {}
headers = []
infos = []
for p in paths:
    d, rows, header, info = load_query_result(p)
    info["file"] = os.path.basename(p)
    info["n_rows"] = len(rows)
    infos.append(info)
    if header:
        headers.append(header)
    for r in rows:
        k = tuple(r.get(x, "") for x in dims) + (r.get("TIME_PERIOD", ""),)
        all_rows.setdefault(k, r)

header = headers[0] if headers else []
missing_dims = [x for x in dims if header and x not in header]

groups = {}
for r in all_rows.values():
    key = (r.get(ind_dim, ""), r.get(area_dim, ""))
    g = groups.setdefault(key, {"series": set(), "dimvals": {x: [] for x in other_dims},
                                "tp": [], "src": set(), "unit": set(), "lb": 0, "n": 0,
                                "obs": set(), "notes": 0, "example": None})
    g["series"].add(tuple(r.get(x, "") for x in dims))
    for x in other_dims:
        v = r.get(x, "")
        if v not in g["dimvals"][x]:
            g["dimvals"][x].append(v)
    g["tp"].append(r.get("TIME_PERIOD", ""))
    if r.get("DATA_SOURCE", "") != "":
        g["src"].add(r.get("DATA_SOURCE", ""))
    if r.get("UNIT_MEASURE", "") != "":
        g["unit"].add(r.get("UNIT_MEASURE", ""))
    if r.get("LOWER_BOUND", "") != "":
        g["lb"] += 1
    g["n"] += 1
    if r.get("OBS_STATUS", "") != "":
        g["obs"].add(r.get("OBS_STATUS", ""))
    if r.get("COUNTRY_NOTES", "") != "":
        g["notes"] += 1
    if g["example"] is None:
        g["example"] = r.get("OBS_VALUE", "")

write_header = not os.path.exists(OUT)
n_out = 0
with open(OUT, "a", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    if write_header:
        w.writerow(COLS)
    for (ind, area) in sorted(groups):
        g = groups[(ind, area)]
        dv = {x: (sorted(v)[:12] if len(v) > 12 else sorted(v)) for x, v in g["dimvals"].items()}
        w.writerow([
            flow_ref, ind, area, len(g["series"]),
            json.dumps(dv, separators=(",", ":"), ensure_ascii=False),
            max(g["tp"]) if g["tp"] else "",
            json.dumps(sorted(g["src"]), separators=(",", ":"), ensure_ascii=False),
            json.dumps(sorted(g["unit"]), separators=(",", ":"), ensure_ascii=False),
            f"{g['lb'] / g['n']:.3f}" if g["n"] else "",
            json.dumps(sorted(g["obs"]), separators=(",", ":"), ensure_ascii=False),
            1 if g["notes"] else 0,
            g["example"] if g["example"] is not None else "",
        ])
        n_out += 1

areas = sorted({r.get(area_dim, "") for r in all_rows.values()})
non_iso3 = [a for a in areas if not ISO3_RE.match(a)]
summary = {
    "flowRef": flow_ref,
    "dims_used": dims,
    "area_dim": area_dim,
    "calls": infos,
    "csv_header": header,
    "dims_missing_from_csv": missing_dims,
    "n_obs_rows_merged": len(all_rows),
    "n_inventory_rows_written": n_out,
    "n_indicators": len({k[0] for k in groups}),
    "ref_areas": areas if len(areas) <= 40 else areas[:40] + [f"... ({len(areas)} total)"],
    "ref_areas_non_iso3": non_iso3[:40],
    "has_COUNTRY_NOTES_col": "COUNTRY_NOTES" in header,
    "other_dim_codes_seen": {x: sorted({r.get(x, "") for r in all_rows.values()})[:40] for x in other_dims},
    "indicators_without_all_T_series": sorted({k[0] for k, g in groups.items()
                                               if other_dims and not any(all(s[dims.index(x)] == "_T" for x in other_dims) for s in g["series"])})[:60],
}
print(json.dumps(summary, ensure_ascii=False, indent=1))
