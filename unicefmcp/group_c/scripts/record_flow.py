#!/usr/bin/env python3
"""Record per-flow run facts (merged into flows_group_c.csv at the end).

Usage: python3 -I record_flow.py <flowRef> <inventory_status> <n_rows_inventory> <n_rows_series> "<notes>"
"""
import json
import os
import sys

import os as _os
BASE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the group_c folder
FACTS = os.path.join(BASE, "raw", "run_facts.json")
flow_ref, status, n_inv, n_ser, notes = sys.argv[1:6]
facts = {}
if os.path.exists(FACTS):
    with open(FACTS, encoding="utf-8") as fh:
        facts = json.load(fh)
facts[flow_ref] = {"inventory_status": status, "n_rows_inventory": int(n_inv),
                   "n_rows_series": int(n_ser), "notes": notes}
with open(FACTS, "w", encoding="utf-8") as fh:
    json.dump(facts, fh, indent=1, ensure_ascii=False)
print("recorded", flow_ref, facts[flow_ref])
