"""
Cost-frontier benchmark, step 3: every MCP call the benchmark agents made, measured exactly from their session
transcripts (tool input and the full tool result text the model received), saved verbatim to ../unicefmcp/frontier/raw/
and matched to the work-list row it executed. Oversized results that the harness saved to a file are read from that
file (their character count is the one the harness reported).
Input : ../unicefmcp/frontier/transcripts/, agent_*.csv
Output: ../unicefmcp/frontier/calls.csv
Run   : python3 -I frontier_extract.py
"""
import json, re
import pandas as pd
from pathlib import Path
F = Path(__file__).resolve().parent.parent / "unicefmcp" / "frontier"; RAW = F / "raw"; RAW.mkdir(exist_ok=True)
T = F / "transcripts"   # the agents' session transcripts, slimmed to messages and tool calls
AGENTS = {"wh1": "a1b89247e071b861a", "wh2": "a3029a88fecaaecd1", "un1": "a6191520c16400401", "un2": "ace7fa81e19bbf7fc",
          "un3": "a02beb73bf572bd0d", "wb1": "a92fe3db6ad663308", "wb2": "a1281d9678dadafc4", "un4": "a1d571f2cb7ad9b76"}
canon = lambda d: json.dumps(d if isinstance(d, dict) else json.loads(d), sort_keys=True)
BIG = re.compile(r"result \(([\d,]+) characters\) exceeds maximum allowed tokens\. Output has been saved to (\S+?\.txt)")
out = []
for g, aid in AGENTS.items():
    work = pd.read_csv(F / f"agent_{g}.csv", dtype=str, keep_default_na=False)
    idx = {}
    for r in work.itertuples(index=False):
        idx.setdefault((r.tool, canon(r.args)), []).append((r, "args"))
        if r.alt_args and canon(r.alt_args) != canon(r.args):
            idx.setdefault((r.tool, canon(r.alt_args)), []).append((r, "alt_args"))
    uses, seq = {}, 0
    for line in open(T / f"agent-{aid}.jsonl", encoding="utf-8"):
        o = json.loads(line); m = o.get("message", {})
        if not (isinstance(m, dict) and isinstance(m.get("content"), list)):
            continue
        for b in m["content"]:
            if b.get("type") == "tool_use" and b["name"].startswith("mcp__") and "Claude_Docs" not in b["name"]:
                uses[b["id"]] = (b["name"], b["input"], o.get("timestamp", ""))
            elif b.get("type") == "tool_result" and b.get("tool_use_id") in uses:
                name, inp, ts = uses.pop(b["tool_use_id"])
                c = b.get("content")
                text = c if isinstance(c, str) else "".join(x.get("text", "") for x in (c or []) if isinstance(x, dict) and x.get("type") == "text")
                big = BIG.search(text)
                if big:
                    p = T / Path(big.group(2)).name; full = p.read_text(encoding="utf-8") if p.exists() else ""
                    n = int(big.group(1).replace(",", "")); text_saved = full or text
                else:
                    n = len(text); text_saved = text
                seq += 1
                f = RAW / f"{g}_{seq:03d}.txt"; f.write_text(text_saved, encoding="utf-8")
                hits = idx.get((name, canon(inp)), [])
                r, which = hits[0] if hits else (None, "")
                err = bool(b.get("is_error")) or text.startswith(("Error", "MCP error")) or '"error":"' in text[:300] or "No data for data query" in text[:400]
                out.append(dict(agent=g, seq=seq, timestamp=ts, tool=name.split("__")[-1], row=r.row if r is not None else "", sid=r.sid if r is not None else "",
                                step=r.step if r is not None else "", iso3=r.iso3 if r is not None else "", target=r.target if r is not None else "",
                                attempt=which, chars=n, error=err, oversized=bool(big), raw=f.name, args=canon(inp)))
c = pd.DataFrame(out)
c.to_csv(F / "calls.csv", index=False)
print(c.groupby("agent").agg(calls=("seq", "size"), unmatched=("row", lambda s: (s == "").sum()), errors=("error", "sum"), chars=("chars", "sum")).to_string())
print(c[c.row == ""][["agent", "tool", "args"]].to_string()[:2000])
