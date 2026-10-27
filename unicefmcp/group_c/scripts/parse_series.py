#!/usr/bin/env python3
"""Append series rows for one flow to series_group_c.csv.

Usage: python3 -I parse_series.py <flowRef> <result_json> [<result_json> ...]

Columns: flowRef,indicator,iso3,dims_json,time_period,value,lower_bound,upper_bound,obs_status,
         data_source,unit_measure,ref_period,country_notes_flag,extra_attrs_json
dims_json        = non-REF_AREA/INDICATOR/TIME_PERIOD dimension codes (dimension order from
                   list_dimensions), compact JSON
extra_attrs_json = every other column of that flow's CSV (attributes other than the ones that
                   have their own column), compact JSON; empty-string attributes are omitted
                   (the full column list is reported in the summary / log).
Rows coming from several result files are de-duplicated on full dimension key + TIME_PERIOD.
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BASE, dims_for, load_query_result  # noqa: E402

flow_ref = sys.argv[1]
paths = sys.argv[2:]
dims = dims_for(flow_ref)
area_dim = dims[0]
ind_dim = "INDICATOR"
other_dims = [x for x in dims if x not in (area_dim, ind_dim)]
FIXED = {"TIME_PERIOD", "OBS_VALUE", "LOWER_BOUND", "UPPER_BOUND", "OBS_STATUS", "DATA_SOURCE",
         "UNIT_MEASURE", "REF_PERIOD", "COUNTRY_NOTES"}

OUT = os.path.join(BASE, "series_group_c.csv")
COLS = ["flowRef", "indicator", "iso3", "dims_json", "time_period", "value", "lower_bound",
        "upper_bound", "obs_status", "data_source", "unit_measure", "ref_period",
        "country_notes_flag", "extra_attrs_json"]

seen = set()
infos = []
header = []
n_written = 0
n_dup = 0
tp_min, tp_max = None, None
indicators = set()
areas = set()
write_header = not os.path.exists(OUT)
with open(OUT, "a", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    if write_header:
        w.writerow(COLS)
    for p in paths:
        d, rows, hdr, info = load_query_result(p)
        info["file"] = os.path.basename(p)
        info["n_rows"] = len(rows)
        infos.append(info)
        if hdr and not header:
            header = hdr
        extra_cols = [c for c in hdr if c not in dims and c not in FIXED]
        for r in rows:
            k = tuple(r.get(x, "") for x in dims) + (r.get("TIME_PERIOD", ""),)
            if k in seen:
                n_dup += 1
                continue
            seen.add(k)
            dj = {x: r.get(x, "") for x in other_dims}
            extra = {c: r[c] for c in extra_cols if r.get(c, "") != ""}
            tp = r.get("TIME_PERIOD", "")
            tp_min = tp if tp_min is None or tp < tp_min else tp_min
            tp_max = tp if tp_max is None or tp > tp_max else tp_max
            indicators.add(r.get(ind_dim, ""))
            areas.add(r.get(area_dim, ""))
            w.writerow([
                flow_ref, r.get(ind_dim, ""), r.get(area_dim, ""),
                json.dumps(dj, separators=(",", ":"), ensure_ascii=False),
                tp, r.get("OBS_VALUE", ""), r.get("LOWER_BOUND", ""), r.get("UPPER_BOUND", ""),
                r.get("OBS_STATUS", ""), r.get("DATA_SOURCE", ""), r.get("UNIT_MEASURE", ""),
                r.get("REF_PERIOD", ""), 1 if r.get("COUNTRY_NOTES", "") != "" else 0,
                json.dumps(extra, separators=(",", ":"), ensure_ascii=False),
            ])
            n_written += 1

summary = {
    "flowRef": flow_ref,
    "calls": infos,
    "csv_header": header,
    "extra_attr_columns": [c for c in header if c not in dims and c not in FIXED],
    "fixed_cols_missing_from_csv": sorted(FIXED - set(header)) if header else None,
    "n_rows_written": n_written,
    "n_duplicates_skipped": n_dup,
    "time_period_range": [tp_min, tp_max],
    "n_indicators": len(indicators),
    "ref_areas": sorted(areas)[:40],
}
print(json.dumps(summary, ensure_ascii=False, indent=1))
