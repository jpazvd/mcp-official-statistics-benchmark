#!/usr/bin/env python3
"""Append series rows verbatim to series_<group>.csv from persisted query_data results.

Usage: python3 -I parse_series.py <flowRef> <group_dir> <group> <result1.json> [<result2.json> ...]

Columns: flowRef,indicator,iso3,dims_json,time_period,value,lower_bound,upper_bound,obs_status,
         data_source,unit_measure,ref_period,country_notes_flag,extra_attrs_json
ref_period := REF_PERIOD column if present, else COVERAGE_TIME column if present, else "" (logged).
extra_attrs_json := all other non-dimension, non-mapped columns with a non-empty value.
"""
import csv
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_result, latest_period, sset  # noqa: E402

FIELDS = ["flowRef", "indicator", "iso3", "dims_json", "time_period", "value", "lower_bound", "upper_bound",
          "obs_status", "data_source", "unit_measure", "ref_period", "country_notes_flag", "extra_attrs_json"]
MAPPED = {"REF_AREA", "INDICATOR", "TIME_PERIOD", "OBS_VALUE", "LOWER_BOUND", "UPPER_BOUND", "OBS_STATUS",
          "DATA_SOURCE", "UNIT_MEASURE", "COUNTRY_NOTES"}


def main():
    flow_ref, group_dir, group = sys.argv[1:4]
    paths = sys.argv[4:]
    out_path = os.path.join(group_dir, f"series_{group}.csv")
    write_header = not os.path.exists(out_path)
    n_written = 0
    seen = set()
    dup = 0
    stats = {"rows_in": 0, "ref_period_col": None, "columns": None, "dim_order": None}
    per_ind = defaultdict(int)
    per_area = defaultdict(int)
    tps = []
    with open(out_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            w.writeheader()
        for p in paths:
            r = load_result(p)
            print(f"[{os.path.basename(p)}] status={r['status']} key={r['key']} rows={len(r['rows'])} "
                  f"raw_len={r['raw_len']} error={r['error']}")
            if not r["rows"]:
                continue
            cols = r["columns"]
            dim_order = r["dimensionOrder"] or [c for c in cols[:cols.index("TIME_PERIOD")]]
            stats["columns"] = cols
            stats["dim_order"] = dim_order
            ref_col = "REF_PERIOD" if "REF_PERIOD" in cols else ("COVERAGE_TIME" if "COVERAGE_TIME" in cols else None)
            stats["ref_period_col"] = ref_col
            area_col = "REF_AREA" if "REF_AREA" in dim_order else dim_order[0]
            if area_col != "REF_AREA":
                print(f"NOTE: no REF_AREA dimension; iso3 column fed from first dimension {area_col}")
            other_dims = [d for d in dim_order if d not in (area_col, "INDICATOR", "TIME_PERIOD")]
            extra_cols = [c for c in cols if c not in MAPPED and c not in dim_order and c != ref_col]
            stats["extra_cols"] = extra_cols
            for row in r["rows"]:
                stats["rows_in"] += 1
                key = tuple(row.get(c, "") for c in cols)
                if key in seen:
                    dup += 1
                    continue
                seen.add(key)
                dims = {d: row.get(d, "") for d in other_dims}
                extra = {c: row.get(c, "") for c in extra_cols if (row.get(c) or "") != ""}
                w.writerow({
                    "flowRef": flow_ref,
                    "indicator": row.get("INDICATOR", ""),
                    "iso3": row.get(area_col, ""),
                    "dims_json": json.dumps(dims, separators=(",", ":")),
                    "time_period": row.get("TIME_PERIOD", ""),
                    "value": row.get("OBS_VALUE", ""),
                    "lower_bound": row.get("LOWER_BOUND", ""),
                    "upper_bound": row.get("UPPER_BOUND", ""),
                    "obs_status": row.get("OBS_STATUS", ""),
                    "data_source": row.get("DATA_SOURCE", ""),
                    "unit_measure": row.get("UNIT_MEASURE", ""),
                    "ref_period": row.get(ref_col, "") if ref_col else "",
                    "country_notes_flag": 1 if (row.get("COUNTRY_NOTES") or "") != "" else 0,
                    "extra_attrs_json": json.dumps(extra, separators=(",", ":"), ensure_ascii=False),
                })
                n_written += 1
                per_ind[row.get("INDICATOR", "")] += 1
                per_area[row.get(area_col, "")] += 1
                tps.append(row.get("TIME_PERIOD", ""))
    print(f"rows_in={stats['rows_in']} written={n_written} duplicates_skipped={dup}")
    print("columns:", stats["columns"])
    print("dim_order:", stats["dim_order"])
    print("ref_period_col:", stats["ref_period_col"], "extra_cols:", stats.get("extra_cols"))
    print("rows per REF_AREA:", dict(per_area))
    print(f"indicators with rows ({len(per_ind)}):", dict(sorted(per_ind.items())))
    if tps:
        print("TIME_PERIOD range:", min(tps), "..", latest_period(tps), "distinct:", len(set(tps)))


if __name__ == "__main__":
    main()
