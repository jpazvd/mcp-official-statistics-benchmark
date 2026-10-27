#!/usr/bin/env python3
"""Build inventory rows from one or more persisted inventory query results.

Usage: python3 -I parse_inventory.py <flowRef> <group_dir> <group> <result1.json> [<result2.json> ...]

Appends to <group_dir>/inventory_<group>.csv one row per (flowRef, INDICATOR, REF_AREA).
Prints summary incl. per-dimension code sets (for deciding the totals key) and anomalies.
"""
import csv
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_result, latest_period, sset  # noqa: E402

FIELDS = ["flowRef", "INDICATOR", "REF_AREA", "n_series", "dimension_values", "latest_time_period",
          "data_sources", "unit_measure", "share_with_lower_bound", "obs_status", "has_country_notes",
          "example_value"]


def main():
    flow_ref, group_dir, group = sys.argv[1:4]
    paths = sys.argv[4:]
    all_rows = []
    dim_order = None
    columns = None
    seen_keys = set()
    for p in paths:
        r = load_result(p)
        print(f"[{os.path.basename(p)}] status={r['status']} key={r['key']} rows={len(r['rows'])} "
              f"raw_len={r['raw_len']} error={r['error']}")
        if r["dimensionOrder"]:
            dim_order = r["dimensionOrder"]
        if r["columns"]:
            columns = r["columns"]
        for row in r["rows"]:
            # de-duplicate identical rows across merged files
            k = tuple(row.get(c, "") for c in (columns or row.keys()))
            if k in seen_keys:
                continue
            seen_keys.add(k)
            all_rows.append(row)
    if not all_rows:
        print("NO ROWS")
        return
    if dim_order is None:
        print("WARNING: no dimensionOrder in provenance; inferring from columns up to TIME_PERIOD")
        dim_order = []
        for c in columns:
            if c == "TIME_PERIOD":
                break
            dim_order.append(c)
    area_col = "REF_AREA" if "REF_AREA" in dim_order else dim_order[0]
    if area_col != "REF_AREA":
        print(f"NOTE: no REF_AREA dimension; using first dimension {area_col} as the inventory REF_AREA column")
    other_dims = [d for d in dim_order if d not in (area_col, "INDICATOR")]
    groups = defaultdict(list)
    for row in all_rows:
        groups[(row.get("INDICATOR", ""), row.get(area_col, ""))].append(row)

    out_path = os.path.join(group_dir, f"inventory_{group}.csv")
    write_header = not os.path.exists(out_path)
    n_written = 0
    with open(out_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            w.writeheader()
        for (ind, area), rows in sorted(groups.items()):
            series_keys = {tuple(r.get(d, "") for d in dim_order) for r in rows}
            dim_vals = {}
            for d in other_dims:
                vals = sorted({r.get(d, "") for r in rows})
                dim_vals[d] = vals[:12] + ([f"...+{len(vals)-12}"] if len(vals) > 12 else [])
            n_lb = sum(1 for r in rows if (r.get("LOWER_BOUND") or "") != "")
            w.writerow({
                "flowRef": flow_ref,
                "INDICATOR": ind,
                "REF_AREA": area,
                "n_series": len(series_keys),
                "dimension_values": json.dumps(dim_vals, separators=(",", ":")),
                "latest_time_period": latest_period(r.get("TIME_PERIOD", "") for r in rows),
                "data_sources": sset(r.get("DATA_SOURCE", "") for r in rows),
                "unit_measure": sset(r.get("UNIT_MEASURE", "") for r in rows),
                "share_with_lower_bound": f"{n_lb/len(rows):.3f}",
                "obs_status": sset(r.get("OBS_STATUS", "") for r in rows),
                "has_country_notes": 1 if any((r.get("COUNTRY_NOTES") or "") != "" for r in rows) else 0,
                "example_value": rows[0].get("OBS_VALUE", ""),
            })
            n_written += 1

    # ---- summary for the log -----------------------------------------------
    print(f"rows_total={len(all_rows)} inventory_rows_written={n_written}")
    print("columns:", columns)
    print("dimensionOrder:", dim_order)
    areas = sorted({r.get(area_col, "") for r in all_rows})
    print(f"REF_AREA codes ({len(areas)}):", areas[:40], "..." if len(areas) > 40 else "")
    non_iso3 = [a for a in areas if not (len(a) == 3 and a.isalpha() and a.isupper())]
    print("REF_AREA not ISO3-shaped:", non_iso3[:40], f"(n={len(non_iso3)})")
    inds = sorted({r.get("INDICATOR", "") for r in all_rows})
    print(f"INDICATOR codes ({len(inds)}):", inds)
    for d in other_dims:
        cnt = defaultdict(int)
        for r in all_rows:
            cnt[r.get(d, "")] += 1
        items = sorted(cnt.items(), key=lambda x: -x[1])
        print(f"dim {d}: n_codes={len(items)} top={items[:15]}")
    # per indicator: has a row where all breakdown dims are _T (excluding AGE, DATA_SOURCE-like)?
    print("per-indicator latest period / n_rows:")
    for ind in inds:
        rr = [r for r in all_rows if r.get("INDICATOR") == ind]
        print(f"  {ind}: n={len(rr)} latest={latest_period(r.get('TIME_PERIOD','') for r in rr)} "
              f"units={sset(r.get('UNIT_MEASURE','') for r in rr)} areas={sorted({r.get(area_col) for r in rr})}")
    for c in ("OBS_STATUS", "UNIT_MEASURE", "TIME_PERIOD_METHOD", "OBS_CONF"):
        if columns and c in columns:
            print(f"{c} values:", sset(r.get(c, "") for r in all_rows))
    tps = sorted({r.get("TIME_PERIOD", "") for r in all_rows})
    odd_tp = [t for t in tps if not (len(t) == 4 and t.isdigit())]
    print("TIME_PERIOD non-YYYY examples:", odd_tp[:15], f"(n={len(odd_tp)})")
    for c in ("COUNTRY_NOTES", "LOWER_BOUND"):
        if columns and c in columns:
            print(f"{c}: non-empty rows =", sum(1 for r in all_rows if (r.get(c) or '') != ''))
        else:
            print(f"{c}: column absent")


if __name__ == "__main__":
    main()
