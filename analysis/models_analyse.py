"""
Model and effort benchmark: summaries of tokens, accuracy, grounding, choices and stability.
Input : ../unicefmcp/models/run_results.csv, mcp_calls.csv, answers/, reference_nga.json
Output: ../unicefmcp/models/summary_config.csv, summary_server.csv, choices.csv, determinism.csv, models_table.md (printed too)
Run   : python3 -I models_analyse.py
"""
import json
import pandas as pd
from pathlib import Path
M = Path(__file__).resolve().parent.parent / "unicefmcp" / "models"
R = pd.read_csv(M / "run_results.csv"); C = pd.read_csv(M / "mcp_calls.csv")
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
ORDER = ["haiku-medium", "sonnet-low", "sonnet-medium", "sonnet-high", "opus-low", "opus-medium", "opus-high", "opus-medium-rep2"]
SRV = {"wh": "UNICEF SDMX", "un": "UN DC", "wb": "Data360"}

def summarise(g):
    return pd.Series(dict(
        model_id=";".join(sorted(set(";".join(g.model_id).split(";")))),
        runs=len(g), answered=int((g.years_reported > 0).sum()),
        sent_k_median=round(g.tokens_sent.median() / 1e3), sent_k_total=round(g.tokens_sent.sum() / 1e3),
        sent_uncached_k_total=round((g.tokens_sent - g.tokens_sent_cached).sum() / 1e3),
        growth_k_median=round(g.tokens_sent_growth.median() / 1e3, 1),
        schema_k_median=round(g.schema_tokens.median() / 1e3, 1), schema_resent_k_median=round(g.schema_tokens_resent.median() / 1e3, 1),
        other_growth_k_median=round((g.tokens_sent_growth - g.schema_tokens_resent).median() / 1e3, 1),
        received_median=int(g.tokens_received.median()), received_total=int(g.tokens_received.sum()),
        thinking_total=int(g.thinking_tokens.sum()),
        turns_median=g.turns.median(), mcp_calls_median=g.mcp_calls.median(), mcp_calls_total=int(g.mcp_calls.sum()),
        mcp_chars_median=int(g.mcp_chars_in_context.median()), mcp_chars_total=int(g.mcp_chars_in_context.sum()), oversized=int(g.mcp_oversized.sum()),
        years_reported=int(g.years_reported.sum()), years_correct=int(g.years_correct.sum()),
        years_ref=int(g.years_ref.sum()), values_grounded=int(g.values_grounded.sum()),
        meta_mean=round(g.meta_reported.mean(), 1)))

S = R.groupby("config").apply(summarise).reindex(ORDER)
S["accuracy"] = (S.years_correct / S.years_reported).round(3)
S["completeness"] = (S.years_correct / S.years_ref).round(3)
S.to_csv(M / "summary_config.csv")
print("=== by configuration (12 questions each) ===\n", S.to_string())

V = R.groupby(["server", "config"]).apply(summarise).reset_index()
V.to_csv(M / "summary_server.csv", index=False)
print("\n=== by server (all configs) ===")
print(R.groupby("server").agg(turns_med=("turns", "median"), schema_k_med=("schema_tokens", lambda x: round(x.median() / 1e3, 1)),
                              schema_resent_k_med=("schema_tokens_resent", lambda x: round(x.median() / 1e3, 1)), sent_k_med=("tokens_sent", lambda x: round(x.median() / 1e3)), growth_k_med=("tokens_sent_growth", lambda x: round(x.median() / 1e3, 1)),
                              recv_med=("tokens_received", "median"), calls_med=("mcp_calls", "median"), chars_med=("mcp_chars_in_context", "median"),
                              chars_max=("mcp_chars_in_context", "max"), rep=("years_reported", "sum"), cor=("years_correct", "sum"), ref=("years_ref", "sum"),
                              meta=("meta_reported", "mean")).to_string())
print("\n=== by server x model family ===")
print(R.groupby(["server", "model"]).agg(growth_k_med=("tokens_sent_growth", lambda x: round(x.median() / 1e3, 1)), recv_med=("tokens_received", "median"),
                                          chars_med=("mcp_chars_in_context", "median"), calls_med=("mcp_calls", "median")).to_string())

print("\n=== wrong or extra years ===")
print(R[(R.wrong_years.notna()) | (R.extra_years.notna())][["run", "config", "qid", "server", "indicator", "years_reported", "years_correct", "wrong_years", "extra_years"]].to_string(index=False))
print("\n=== values not found verbatim/rounded in server responses ===")
print(R[R.values_grounded < R.years_reported][["run", "config", "qid", "server", "years_reported", "values_grounded"]].to_string(index=False))

# answers: series chosen and value sets
ans = {int(r): json.load(open(M / "answers" / f"run{int(r):03d}.json")) for r in R.run}
def vkey(a):
    v = a.get("values") or {}
    return tuple(sorted((str(k)[:4], round(float(x), 1)) for k, x in v.items() if isinstance(x, (int, float))))
R["series"] = [str(ans[r].get("server_indicator_id")) for r in R.run]
R["vkey"] = [hash(vkey(ans[r])) for r in R.run]
R["years_span"] = [(lambda k: f"{k[0][0]}-{k[-1][0]}" if k else "")(vkey(ans[r])) for r in R.run]
ch = R.groupby(["qid", "server"]).agg(series_distinct=("series", "nunique"), value_sets=("vkey", "nunique"),
                                      series=("series", lambda s: " | ".join(f"{k} ({v})" for k, v in s.value_counts().items()))).reset_index()
ch.to_csv(M / "choices.csv", index=False)
print("\n=== series chosen and distinct value sets (values rounded to 0.1) per question x server, 8 runs each ===\n", ch.to_string(index=False))

# metadata elements reported
has = [c for c in R.columns if c.startswith("has_")]
print("\n=== share of runs reporting each field, by server ===\n", R.groupby("server")[has].mean().round(2).T.to_string())
gr = [c for c in R.columns if c.startswith("grounded_")]
print("\n=== text fields with < 60% of their words found in the server's responses ===")
low = R.melt(id_vars=["run", "config", "qid", "server"], value_vars=gr).dropna()
print(low[low.value < 0.6].sort_values("value").to_string(index=False))
for _, x in low[low.value < 0.6].iterrows():
    print(x.run, x.variable, "->", str(ans[x.run].get(x.variable.replace("grounded_", "")))[:200])

# repeat stability: opus-medium vs rep2
a = R[R.config == "opus-medium"].set_index(["qid", "server"]); b = R[R.config == "opus-medium-rep2"].set_index(["qid", "server"])
rep = pd.DataFrame(dict(series1=a.series, series2=b.series, same_values=a.vkey == b.vkey, calls1=a.mcp_calls, calls2=b.mcp_calls,
                        chars1=a.mcp_chars, chars2=b.mcp_chars, sent1_k=(a.tokens_sent / 1e3).round(), sent2_k=(b.tokens_sent / 1e3).round(),
                        recv1=a.tokens_received, recv2=b.tokens_received, meta1=a.meta_reported, meta2=b.meta_reported))
print("\n=== repeat stability (opus-medium run twice) ===\n", rep.to_string())

# server determinism: identical tool + arguments in different runs -> identical response?
m = C[C.mcp & (C.tool != "ReadMcpResourceTool")]
d = m.groupby(["server", "tool", "args"]).agg(runs=("run", "nunique"), responses=("sha", "nunique"), contents=("sha_canon", "nunique"), chars=("chars", lambda s: ";".join(map(str, sorted(set(s)))))).reset_index()
d = d[d.runs > 1]; d.to_csv(M / "determinism.csv", index=False)
print("\n=== identical calls repeated across runs ===")
print(d.groupby("server").agg(call_signatures=("runs", "size"), identical_bytes=("responses", lambda s: int((s == 1).sum())),
                                identical_content=("contents", lambda s: int((s == 1).sum()))).to_string())
print(d[d.contents > 1][["server", "tool", "args", "runs", "responses", "contents", "chars"]].to_string(index=False))
print("\n=== responses too large for the client (refused, never entered the context) ===")
print(C[C.oversized][["run", "config", "server", "qid", "tool", "chars", "args"]].to_string(index=False))
R.drop(columns=["vkey"]).to_csv(M / "run_results_annotated.csv", index=False)
