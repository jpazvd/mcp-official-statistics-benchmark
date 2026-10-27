"""
Model and effort benchmark, step 3: every summary figure quoted in the paper (Section 5.4).
Input : ../unicefmcp/models/run_results.csv, mcp_calls.csv, answers/, transcripts/, choices.csv, determinism.csv
Output: ../unicefmcp/models/summary.json
Run   : python3 -I models_summary.py   (after models_extract.py and models_analyse.py)
"""
import json, re
import pandas as pd
from pathlib import Path

M = Path(__file__).resolve().parent.parent / "unicefmcp" / "models"
R = pd.read_csv(M / "run_results.csv"); C = pd.read_csv(M / "mcp_calls.csv")
runs = pd.read_csv(M / "runs.csv", dtype=str).set_index("run")
ans = {int(r): json.load(open(M / "answers" / f"run{int(r):03d}.json")) for r in R.run}
NUM = re.compile(r"-?\d+(?:\.\d+)?")


def corpus(run):
    """Text of every tool result the agent of this run received."""
    out = []
    for line in open(M / "transcripts" / f"agent-{runs.loc[str(run), 'agent_id']}.jsonl", encoding="utf-8"):
        m = json.loads(line).get("message", {})
        for b in m.get("content", []) if isinstance(m.get("content"), list) else []:
            if b.get("type") == "tool_result":
                c = b.get("content")
                out.append(c if isinstance(c, str) else "".join(x.get("text", "") for x in c or [] if isinstance(x, dict)))
    return "\n".join(out)


# uncertainty bounds reported and found in the server's responses (verbatim or rounded to the precision reported)
b_rep = b_ok = 0
for r in R[R.has_uncertainty].run:
    nums = [float(x) for x in NUM.findall(corpus(r))]
    for pair in (ans[r].get("uncertainty") or {}).values():
        for v in pair if isinstance(pair, list) else []:
            d = len(str(v).split(".")[1]) if "." in str(v) else 0
            b_rep += 1; b_ok += any(round(x, d) == v for x in nums)

ch = pd.read_csv(M / "choices.csv"); det = pd.read_csv(M / "determinism.csv")
med = lambda cfg, col: float(R[R.config == cfg][col].median())
a = R[R.config == "opus-medium"].set_index(["qid", "server"]); b = R[R.config == "opus-medium-rep2"].set_index(["qid", "server"])
chg = (b.tokens_sent - a.tokens_sent) / a.tokens_sent
R["other"] = R.tokens_sent_growth - R.schema_tokens_resent
mc = C[C.mcp & ~C.oversized]
per_q = mc[mc.tool != "ReadMcpResourceTool"].groupby(["server", "run"]).chars.sum().groupby("server").median()
tool = mc.assign(t=mc.tool.str.split("__").str[-1])
norm = lambda s: re.split(r"\s", str(s).split("/")[-1])[0]   # 'WB_HCP/X' and 'X (database WB_HCP)' are the same series
spread = R.groupby(["qid", "server"]).meta_reported.agg(lambda s: s.max() - s.min())

S = dict(
    sessions=int(len(R)), settings=int(R.config.nunique()),
    values_reported=int(R.years_reported.sum()), values_matched=int(R.years_correct.sum()),
    values_extra=int(R.extra_years.notna().sum()), values_grounded=int(R.values_grounded.sum()),
    bounds_reported=b_rep, bounds_grounded=b_ok,
    reference_years_per_setting=int(R[R.config == "opus-medium"].years_ref.sum()),
    cells=int(len(ch)), cells_same_values=int((ch.value_sets == 1).sum()), cells_same_series=int((ch.series_distinct == 1).sum()),
    meta_spread_max=int(spread.max()),
    repeat_same_series=int((a.indicator.map(norm) == b.indicator.map(norm)).sum()),
    repeat_same_values=int(sum(ans[x].get('values') == ans[y].get('values') for x, y in zip(a.run, b.run))),
    repeat_calls_differ=int((a.mcp_calls != b.mcp_calls).sum()),
    repeat_sent_change_max_pct=round(float(chg.abs().max() * 100)),
    repeat_sent_median_change_pct=round(float((med("opus-medium-rep2", "tokens_sent") / med("opus-medium", "tokens_sent") - 1) * 100)),
    opus_effort_sent_change_pct=round(float((med("opus-high", "tokens_sent") / med("opus-low", "tokens_sent") - 1) * 100)),
    haiku_vs_sonnet_medium_received=round(med("haiku-medium", "tokens_received") / med("sonnet-medium", "tokens_received"), 1),
    identical_call_signatures=int(len(det)), identical_content=int((det.contents == 1).sum()),
    undc_signatures=int((det.server == "un").sum()), undc_byte_different=int(((det.server == "un") & (det.responses > 1)).sum()),
    sent_per_received=round(float(R.tokens_sent.sum() / R.tokens_received.sum())),
    baseline_share_pct=round(float(R.tokens_sent_baseline.sum() / R.tokens_sent.sum() * 100)),
    cached_share_pct=round(float(R.tokens_sent_cached.sum() / R.tokens_sent.sum() * 100)),
    baseline_tokens_per_request=round(float((R.tokens_sent_baseline / R.turns).median()), -3),
    schema_tokens_median={s: round(float(R[R.server == s].schema_tokens.median()), -3) for s in ("un", "wh", "wb")},
    tokens_mean={s: {k: round(float(R[R.server == s][k].mean()), -2) for k in ("tokens_sent", "tokens_sent_baseline", "schema_tokens_resent", "other")}
                 for s in ("wh", "un", "wb")},
    requests_median={s: float(R[R.server == s].turns.median()) for s in ("wh", "un", "wb")},
    chars_per_question_excl_instructions={s: float(v) for s, v in per_q.items()},
    instruction_file_chars=float(tool[tool.t == "ReadMcpResourceTool"].chars.median()),
    d360_get_metadata_chars=float(tool[tool.t == "data360_get_metadata"].chars.median()),
    wh_get_time_series_calls=int((tool.t == "get_time_series").sum()), wh_query_data_calls=int((tool.t == "query_data").sum()),
    oversized=int(C.oversized.sum()), oversized_chars=int(C[C.oversized].chars.max()),
)


def sign_test(k, n):
    """Exact two-sided binomial (sign) test of k successes in n paired comparisons, p = 0.5."""
    from math import comb
    pr = [comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(x for x in pr if x <= pr[k] * (1 + 1e-12)))


# effort and repeat, compared within each question x server cell (the cell is the pair)
eff = {}
for v in ("tokens_sent", "tokens_received"):
    p = R.pivot_table(index=["qid", "server"], columns="config", values=v)
    for m in ("opus", "sonnet"):
        kk = int((p[f"{m}-high"] > p[f"{m}-low"]).sum())
        eff[f"{m}_{v}"] = dict(high_gt_low=kk, n=int(len(p)), p=sign_test(kk, int(len(p))),
                               median_ratio=round(float((p[f"{m}-high"] / p[f"{m}-low"]).median()), 3))
    rr = (p["opus-medium-rep2"] / p["opus-medium"] - 1).abs()
    eff[f"repeat_{v}"] = dict(median_abs_change=round(float(rr.median()), 3), max_abs_change=round(float(rr.max()), 3))
S["effort_within_cell"] = eff
# no wrong value in any session: one-sided 95% upper bounds on the error rate (values are clustered within sessions,
# so the session bound is the honest one; the per-value bound is shown for reference only)
S["error_bound_sessions_95"] = round(1 - 0.05 ** (1 / S["sessions"]), 4)
S["error_bound_values_95"] = round(1 - 0.05 ** (1 / S["values_matched"]), 5)
S["sessions_with_wrong_value"] = int(R.wrong_years.notna().sum())
(M / "summary.json").write_text(json.dumps(S, indent=1), encoding="utf-8")
print(json.dumps(S, indent=1))
