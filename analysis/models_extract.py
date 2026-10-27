"""
Model and effort benchmark: per run, tokens sent and received (from the usage the API reported on every turn of the
agent's session), MCP calls and characters, the agent's final JSON answer, its accuracy against the warehouse
reference, whether its numbers and metadata are grounded in what the server returned, and which metadata it reported.
Input : ../unicefmcp/models/runs.csv, reference_nga.json, transcripts/ (the agents' sessions)
Output: ../unicefmcp/models/run_results.csv, mcp_calls.csv, answers/<run>.json
Run   : python3 -I models_extract.py
"""
import json, re, hashlib
import pandas as pd
from pathlib import Path
M = Path(__file__).resolve().parent.parent / "unicefmcp" / "models"; (M / "answers").mkdir(exist_ok=True)
# the agents' session transcripts, slimmed to messages, usage and tool calls (copied into the package);
# oversized responses the client refused are saved beside them under their original file name
T = M / "transcripts"
REF = json.load(open(M / "reference_nga.json"))
META = ["server_indicator_id", "series_label", "unit", "unit_multiplier", "source_or_custodian", "release_or_vintage", "uncertainty",
        "status_or_notes", "definition", "licence", "citation", "query_or_url"]
BIG = re.compile(r"result \(([\d,]+) characters\) exceeds maximum allowed tokens\. Output has been saved to (\S+?\.txt)")
NUM = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")

def parse_answer(text):
    t = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    i, j = t.find("{"), t.rfind("}")
    try:
        return json.loads(t[i:j + 1])
    except Exception:
        return None

def canon_sha(t):
    # the same content with JSON object keys in a different order counts as the same response
    try:
        t = json.dumps(json.loads(t), sort_keys=True)
    except Exception:
        pass
    return hashlib.sha256(t.encode()).hexdigest()[:16]

def decimals(v):
    s = repr(float(v)); return 0 if float(v).is_integer() else len(s.split(".")[1]) if "." in s and "e" not in s else 6

runs = pd.read_csv(M / "runs.csv", dtype=str)
rows, calls = [], []
for r in runs.itertuples(index=False):
    f = T / f"agent-{r.agent_id}.jsonl"
    if not f.exists():
        continue
    turns, uses, mcp_text, last_text, models = {}, {}, [], "", set()
    for line in open(f, encoding="utf-8"):
        o = json.loads(line); m = o.get("message", {})
        if not isinstance(m, dict):
            continue
        if m.get("role") == "assistant" and m.get("usage"):
            # one API response is written as several transcript lines (one per content block) that repeat the same usage:
            # count each response once, keyed by its message id
            u = m["usage"]; models.add(m.get("model", "")); k = m.get("id") or len(turns)
            t = turns.setdefault(k, dict(tools=set()))
            t.update(sent=u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0),
                     cached=u.get("cache_read_input_tokens", 0), received=u.get("output_tokens", 0),
                     thinking=(u.get("output_tokens_details") or {}).get("thinking_tokens", 0) or 0)
            t["tools"].update(b.get("name") for b in m.get("content", []) if isinstance(b, dict) and b.get("type") == "tool_use")
        if isinstance(m.get("content"), list):
            for b in m["content"]:
                if b.get("type") == "text" and m.get("role") == "assistant":
                    last_text = b.get("text", "") or last_text
                if b.get("type") == "tool_use":
                    uses[b["id"]] = (b["name"], b["input"])
                    if b["name"] == "SubagentHandback":
                        last_text = str(b["input"].get("message", "")) or last_text
                elif b.get("type") == "tool_result" and b.get("tool_use_id") in uses:
                    name, inp = uses.pop(b["tool_use_id"])
                    c = b.get("content"); txt = c if isinstance(c, str) else "".join(x.get("text", "") for x in (c or []) if isinstance(x, dict) and x.get("type") == "text")
                    big = BIG.search(txt)
                    if big and (T / Path(big.group(2)).name).exists():
                        txt_full = (T / Path(big.group(2)).name).read_text(encoding="utf-8"); n = int(big.group(1).replace(",", ""))
                    else:
                        txt_full, n = txt, len(txt)
                    is_mcp = name.startswith("mcp__") or name == "ReadMcpResourceTool"
                    if is_mcp:
                        mcp_text.append(txt_full)
                    calls.append(dict(run=r.run, config=r.config, server=r.server, qid=r.qid, tool=name, mcp=is_mcp, chars=n,
                                      args=json.dumps(inp, sort_keys=True), sha=hashlib.sha256(txt_full.encode()).hexdigest()[:16],
                                      sha_canon=canon_sha(txt_full), oversized=bool(big)))
    turns = list(turns.values())
    # tokens of tool definitions loaded by ToolSearch (jump in context on the next request) and how often they were re-sent
    schema_tokens = schema_resent = 0
    for i, t in enumerate(turns[:-1]):
        if "ToolSearch" in t["tools"]:
            sch = turns[i + 1]["sent"] - t["sent"] - t["received"]; schema_tokens += sch; schema_resent += sch * (len(turns) - i - 1)
    ans = parse_answer(last_text) or {}
    json.dump(ans, open(M / "answers" / f"run{int(r.run):03d}.json", "w"), indent=1)
    corpus = "\n".join(mcp_text); low = corpus.lower()
    nums = [float(x) for x in NUM.findall(corpus)] if corpus else []
    numset = set(nums)
    ref = REF[r.qid]["values"]
    vals = ans.get("values") or {}
    vals = {str(k)[:4]: v for k, v in vals.items() if isinstance(v, (int, float))}
    correct = sum(any(abs(v - x) <= max(0.005 * abs(x), 0.51 if float(v).is_integer() else 0.051) for x in ref[y]) for y, v in vals.items() if y in ref)
    wrong_years = [y for y, v in vals.items() if y in ref and not any(abs(v - x) <= max(0.005 * abs(x), 0.51 if float(v).is_integer() else 0.051) for x in ref[y])]
    extra = [y for y in vals if y not in ref]
    def grounded_num(v):
        d = min(decimals(v), 6)
        return v in numset or any(round(x, d) == v for x in nums)
    g_vals = sum(grounded_num(v) for v in vals.values())
    def grounded_text(s):
        words = [w for w in re.findall(r"[a-z0-9]{4,}", str(s).lower())]
        return None if not words else round(sum(w in low for w in words) / len(words), 2)
    gt = {k: grounded_text(ans.get(k)) for k in ("source_or_custodian", "release_or_vintage", "definition", "licence", "citation") if ans.get(k)}
    t0 = turns[0]["sent"] if turns else 0
    rows.append(dict(run=int(r.run), config=r.config, model=r.model, effort=r.effort, repeat=r.repeat, qid=r.qid, server=r.server,
                     model_id=";".join(sorted(models)), turns=len(turns),
                     tokens_sent=sum(t["sent"] for t in turns), tokens_sent_cached=sum(t["cached"] for t in turns),
                     tokens_sent_baseline=t0 * len(turns), tokens_sent_growth=sum(t["sent"] - t0 for t in turns),
                     schema_tokens=schema_tokens, schema_tokens_resent=schema_resent,
                     tokens_received=sum(t["received"] for t in turns), thinking_tokens=sum(t["thinking"] for t in turns),
                     final_context=turns[-1]["sent"] if turns else 0,
                     mcp_calls=len(mcp_text), mcp_chars=sum(len(x) for x in mcp_text), mcp_oversized=sum(1 for c in calls if c['run'] == r.run and c['oversized']),
                     mcp_chars_in_context=sum(c['chars'] for c in calls if c['run'] == r.run and c['mcp'] and not c['oversized']),
                     parsed=bool(ans), found=ans.get("found"), indicator=ans.get("server_indicator_id"),
                     years_reported=len(vals), years_ref=len(ref), years_correct=correct, wrong_years=";".join(wrong_years),
                     extra_years=";".join(extra), values_grounded=g_vals,
                     meta_reported=sum(1 for k in META if ans.get(k) not in (None, "", [], {})),
                     **{f"has_{k}": ans.get(k) not in (None, "", [], {}) for k in META},
                     **{f"grounded_{k}": v for k, v in gt.items()}))
R = pd.DataFrame(rows).sort_values("run"); R.to_csv(M / "run_results.csv", index=False)
pd.DataFrame(calls).to_csv(M / "mcp_calls.csv", index=False)
pd.set_option("display.width", 250)
print(R[["run", "config", "qid", "server", "model_id", "turns", "tokens_sent", "tokens_sent_growth", "tokens_received", "thinking_tokens", "mcp_calls", "mcp_chars", "years_reported", "years_correct", "values_grounded", "meta_reported"]].to_string(index=False))
gcols = [c for c in R.columns if c.startswith("grounded_")]
print(R[["run", "server"] + gcols].to_string(index=False))
