#!/usr/bin/env python3
"""Assemble flows_<group>.csv from raw/structure_summary_*.json, raw/flow_notes.json and the inventory/series CSVs.
Usage: python3 -I build_flows.py <group_dir> <group> <flows.txt> <GROUP_NAME>"""
import csv
import json
import os
import sys
from collections import Counter

group_dir, group, flows_txt, group_name = sys.argv[1:5]

# flow list for this group, in order
flows = []
with open(flows_txt, encoding="utf-8") as f:
    take = False
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line.startswith("GROUP_"):
            take = (line == group_name)
            continue
        if take:
            flows.append(line)

notes = json.load(open(os.path.join(group_dir, "raw", "flow_notes.json"), encoding="utf-8"))
inv_counts = Counter(r["flowRef"] for r in csv.DictReader(open(os.path.join(group_dir, f"inventory_{group}.csv"), encoding="utf-8")))
ser_counts = Counter(r["flowRef"] for r in csv.DictReader(open(os.path.join(group_dir, f"series_{group}.csv"), encoding="utf-8")))

fields = ["flowRef", "agency", "id", "name", "description", "version", "isFinal", "dimensions_ordered", "attributes",
          "measure", "inventory_status", "n_rows_inventory", "n_rows_series", "notes"]
out = os.path.join(group_dir, f"flows_{group}.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for fr in flows:
        flow_id = fr.split("/")[1]
        sp = os.path.join(group_dir, "raw", f"structure_summary_{flow_id}.json")
        s = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {}
        dims = s.get("dimensions") or []
        attrs = s.get("attributes")
        attr_str = "|".join(f"{a['id']}({a['assignmentStatus'][0] if a.get('assignmentStatus') else '?'})" for a in attrs) if attrs else "NOT_RETRIEVED"
        n = notes.get(fr, {})
        w.writerow({
            "flowRef": fr,
            "agency": s.get("agency") or fr.split("/")[0],
            "id": s.get("id") or flow_id,
            "name": s.get("name", ""),
            "description": s.get("description") or "",
            "version": s.get("version") or fr.split("/")[2],
            "isFinal": "" if s.get("isFinal") is None else s.get("isFinal"),
            "dimensions_ordered": "|".join(d["id"] for d in dims),
            "attributes": attr_str,
            "measure": s.get("primary_measure") or "",
            "inventory_status": n.get("inventory_status", ""),
            "n_rows_inventory": inv_counts.get(fr, 0),
            "n_rows_series": ser_counts.get(fr, 0),
            "notes": n.get("notes", ""),
        })
        print(f"{fr}: inv={inv_counts.get(fr,0)} ser={ser_counts.get(fr,0)} status={n.get('inventory_status','')}")
print("written", out)
