#!/usr/bin/env python3
"""Assemble flows_group_c.csv from raw/meta_<FLOW>.json and raw/run_facts.json, in flows.txt order."""
import csv
import json
import os

import os as _os
BASE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the group_c folder
ORDER = ["UNICEF/GLOBAL_DATAFLOW/1.0", "UNICEF/EDUCATION/1.0", "UNICEF/EDUCATION_FLS/1.0",
         "UNICEF/EDUCATION_LG/1.0", "UNICEF/EDUCATION_UIS_SDG/1.0", "UNICEF/SOC_PROTECTION/1.0",
         "UNICEF/CHILD_RELATED_SDG/1.0", "UNICEF/SDG_PROG_ASSESSMENT/1.1",
         "UNICEF/WASH_HEALTHCARE_FACILITY/1.0", "UNICEF/WASH_HOUSEHOLDS/1.0",
         "UNICEF/WASH_HOUSEHOLD_MH/1.0", "UNICEF/WASH_HOUSEHOLD_SUBNAT/1.0", "UNICEF/WASH_SCHOOLS/1.0"]
with open(os.path.join(BASE, "raw", "run_facts.json"), encoding="utf-8") as fh:
    facts = json.load(fh)
out = os.path.join(BASE, "flows_group_c.csv")
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["flowRef", "agency", "id", "name", "description", "version", "isFinal",
                "dimensions_ordered", "attributes", "measure", "inventory_status",
                "n_rows_inventory", "n_rows_series", "notes"])
    for ref in ORDER:
        fid = ref.split("/")[1]
        with open(os.path.join(BASE, "raw", f"meta_{fid}.json"), encoding="utf-8") as mh:
            m = json.load(mh)
        df = m["dataflow"]
        dims = [d["id"] for d in m["dimensions"]] + m["timeDimensions"]
        attrs = [f"{a['id']}({(a['assignmentStatus'] or '')[:1]})" for a in m["attributes"]]
        f = facts[ref]
        w.writerow([ref, df["agencyID"], df["id"], df["name"], df["description"] if df["description"] is not None else "",
                    df["version"], df["isFinal"], "|".join(dims), "|".join(attrs),
                    m["primaryMeasure"]["id"], f["inventory_status"], f["n_rows_inventory"],
                    f["n_rows_series"], f["notes"]])
print("wrote", out)
