#!/usr/bin/env python3
"""Anomaly check: which indicators (per flow) have no series where every *breakdown*
dimension equals _T, and which codes each breakdown dimension takes.

Usage: python3 -I check_totals.py <flowRef> <breakdown_dims_comma_separated> <inventory_json> [...]
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import dims_for, load_query_result  # noqa: E402

flow_ref, bd, paths = sys.argv[1], sys.argv[2], sys.argv[3:]
bdims = [x for x in bd.split(",") if x]
dims = dims_for(flow_ref)
rows = []
for p in paths:
    _, r, _, _ = load_query_result(p)
    rows.extend(r)
by_ind = {}
for r in rows:
    by_ind.setdefault(r["INDICATOR"], []).append(r)
no_total = sorted(i for i, rs in by_ind.items()
                  if not any(all(r.get(x, "") == "_T" for x in bdims) for r in rs))
codes = {x: sorted({r.get(x, "") for r in rows}) for x in dims[1:]}
print(json.dumps({"flowRef": flow_ref, "breakdown_dims": bdims, "n_indicators": len(by_ind),
                  "indicators_without_total_series": no_total,
                  "codes_per_dimension": codes}, ensure_ascii=False, indent=1))
