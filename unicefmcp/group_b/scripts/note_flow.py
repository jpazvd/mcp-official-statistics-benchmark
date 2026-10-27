#!/usr/bin/env python3
"""Record per-flow status/notes for flows_<group>.csv. Usage: note_flow.py <group_dir> <flowRef> <inventory_status> <notes>"""
import json, os, sys
group_dir, flow_ref, status, notes = sys.argv[1:5]
p = os.path.join(group_dir, "raw", "flow_notes.json")
d = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
d[flow_ref] = {"inventory_status": status, "notes": notes}
json.dump(d, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("noted", flow_ref)
