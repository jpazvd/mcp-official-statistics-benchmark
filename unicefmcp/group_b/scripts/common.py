"""Shared helpers for parsing persisted query_data results (sdmx-mcp, format=csv, labels=id)."""
import csv
import io
import json
import re

STD_COLS = {"TIME_PERIOD", "OBS_VALUE", "LOWER_BOUND", "UPPER_BOUND", "OBS_STATUS", "DATA_SOURCE",
            "UNIT_MEASURE", "REF_PERIOD", "COVERAGE_TIME", "COUNTRY_NOTES"}


def load_result(path):
    """Load a persisted query_data tool result. Returns dict with keys:
    status, error, provenance, dimensionOrder, rows (list of dict), columns (list), raw_len.
    Handles both JSON-wrapped results and plain error text."""
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    out = {"status": None, "error": None, "provenance": None, "dimensionOrder": None,
           "rows": [], "columns": [], "raw_len": 0, "key": None, "queryURL": None}
    try:
        d = json.loads(txt)
    except json.JSONDecodeError:
        out["status"] = "unparseable"
        out["error"] = txt[:2000]
        return out
    if not isinstance(d, dict):
        out["status"] = "unexpected"
        out["error"] = str(d)[:2000]
        return out
    out["status"] = d.get("status")
    prov = d.get("provenance") or {}
    out["provenance"] = prov
    out["dimensionOrder"] = prov.get("dimensionOrder")
    out["key"] = prov.get("key")
    out["queryURL"] = prov.get("queryURL")
    for k in ("error", "errors", "message", "detail", "httpStatus", "http_status"):
        if k in d and d[k]:
            out["error"] = (out["error"] or "") + f"{k}={json.dumps(d[k])[:2000]}; "
    raw = d.get("raw_csv")
    if raw is None:
        # maybe other shapes
        for k in ("raw", "data", "csv"):
            if isinstance(d.get(k), str):
                raw = d[k]
                break
    if isinstance(raw, str) and raw.strip():
        out["raw_len"] = len(raw)
        if raw.lstrip().startswith("<") or raw.lstrip().startswith("{"):
            out["error"] = (out["error"] or "") + "raw_csv not CSV: " + raw[:500]
            return out
        reader = csv.DictReader(io.StringIO(raw))
        out["columns"] = reader.fieldnames or []
        out["rows"] = list(reader)
    return out


def year_of(tp):
    m = re.search(r"(\d{4})", tp or "")
    return int(m.group(1)) if m else -1


def latest_period(periods):
    best = None
    for p in periods:
        if p is None or p == "":
            continue
        k = (year_of(p), p)
        if best is None or k > best[0]:
            best = (k, p)
    return best[1] if best else ""


def sset(values):
    return "|".join(sorted({v for v in values if v not in (None, "")}))
