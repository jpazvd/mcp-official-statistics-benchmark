#!/usr/bin/env python3
"""Peek at a persisted query_data result: provenance, status, header, row count, per-dimension code sets."""
import json, csv, io, sys
from collections import Counter
p = sys.argv[1]
d = json.load(open(p, encoding="utf-8"))
print("status:", d.get("status"), "| error:", d.get("error"), "| key:", d.get("provenance", {}).get("key"), "| dims:", d.get("provenance", {}).get("dimensionOrder"))
print("queryURL:", d.get("provenance", {}).get("queryURL"))
for k in d:
    if k not in ("sourceScope", "provenance", "status", "assistant_guidance", "notes", "raw_csv"):
        print("other field:", k, "=", str(d[k])[:500])
raw = d.get("raw_csv")
if raw is None:
    print("raw_csv: None"); sys.exit()
rows = list(csv.reader(io.StringIO(raw)))
if not rows:
    print("raw_csv empty"); sys.exit()
h = rows[0]; body = [r for r in rows[1:] if any(r)]
print("header:", h); print("rows:", len(body))
dims = d.get("provenance", {}).get("dimensionOrder", [])
for c in h:
    if c in dims or c in ("UNIT_MEASURE", "OBS_STATUS", "DATA_SOURCE", "TIME_PERIOD"):
        idx = h.index(c); vals = Counter(r[idx] for r in body if idx < len(r))
        items = sorted(vals.items(), key=lambda x: -x[1])
        print(f"  {c}: {len(vals)} distinct -> {items[:25]}{' ...' if len(items) > 25 else ''}")
