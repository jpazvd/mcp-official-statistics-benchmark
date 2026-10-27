#!/usr/bin/env python3
"""Append one MCP call record to work/calls.jsonl.

usage: logcall.py GROUP_DIR FLOWREF STEP KEY STATUS ROWS PERSISTED [ERROR] [NOTE] [RAWFILE]
STEP: list_dimensions | get_flow_structure | inventory | inventory_retry | series | series_fallback | describe_flow
"""
import json, os, sys, datetime

gdir, flow, step, key, status, rows, persisted = sys.argv[1:8]
error = sys.argv[8] if len(sys.argv) > 8 else ""
note = sys.argv[9] if len(sys.argv) > 9 else ""
rawfile = sys.argv[10] if len(sys.argv) > 10 else ""
os.makedirs(os.path.join(gdir, "work"), exist_ok=True)
rec = {
    "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "flow": flow, "step": step, "key": key, "status": status,
    "rows": rows, "persisted": persisted, "error": error, "note": note, "rawfile": rawfile,
}
with open(os.path.join(gdir, "work", "calls.jsonl"), "a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("logged:", json.dumps(rec, ensure_ascii=False))
