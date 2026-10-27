"""Shared helpers for the group_c extraction scripts."""
import csv
import io
import json
import os
import re

import os as _os
BASE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # the group_c folder
DIMS_FILE = os.path.join(BASE, "raw", "list_dimensions_group_c.json")
ISO3_RE = re.compile(r"^[A-Z]{3}$")


def flow_id(flow_ref):
    return flow_ref.split("/")[1]


def dims_for(flow_ref):
    """Ordered dimension ids for a flow, from the saved list_dimensions output."""
    with open(DIMS_FILE, encoding="utf-8") as fh:
        d = json.load(fh)
    return [x["id"] for x in sorted(d[flow_ref]["result"], key=lambda x: x["position"])]


def load_query_result(path):
    """Load a persisted query_data result (JSON file). Returns (dict, rows, header, info).

    rows is a list of dicts (csv.DictReader over raw_csv); header the column list.
    info summarises status/error fields for the log.
    """
    with open(path, encoding="utf-8") as fh:
        txt = fh.read()
    try:
        d = json.loads(txt)
    except json.JSONDecodeError:
        return None, [], [], {"error": "not JSON", "head": txt[:300]}
    info = {
        "status": d.get("status"),
        "key": d.get("provenance", {}).get("key"),
        "queryURL": d.get("provenance", {}).get("queryURL"),
        "dimensionOrder": d.get("provenance", {}).get("dimensionOrder"),
        "notes": d.get("notes"),
    }
    for k in ("error", "errors", "message", "httpStatus", "statusCode", "warning", "warnings"):
        if k in d:
            info[k] = d[k]
    raw = d.get("raw_csv")
    if raw is None:
        info["raw_csv"] = None
        # some error payloads carry the body elsewhere
        for k in ("raw", "body", "detail"):
            if k in d:
                info[k] = str(d[k])[:500]
        return d, [], [], info
    if not raw.strip():
        info["raw_csv_len"] = 0
        return d, [], [], info
    info["raw_csv_len"] = len(raw)
    reader = csv.DictReader(io.StringIO(raw))
    rows = list(reader)
    header = reader.fieldnames or []
    return d, rows, header, info
