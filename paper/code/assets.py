"""
Builds every number, table and figure the paper uses, from the analysis outputs. Nothing in the paper's results is typed
by hand: the text cites the macros written to generated/numbers.tex, the tables are generated/tab*.tex and the figures
figures/fig*.pdf.
Input : ../../unicefmcp/out/, ../../unicefmcp/frontier/, ../../unicefmcp/models/ (written by the analysis scripts)
Output: ../generated/numbers.tex, ../generated/tab*.tex, ../figures/fig*.pdf and .png
Run   : python3 -I assets.py   (or `make paper` from the repository root)
"""
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
U = ROOT / "unicefmcp"
GEN = HERE.parent / "generated"; GEN.mkdir(exist_ok=True)
FIG = HERE.parent / "figures"; FIG.mkdir(exist_ok=True)

COL = {"warehouse": "#1f6fd1", "undc": "#e3672b", "d360": "#1aa37a", "data360": "#1aa37a", "compliant": "#222222"}
GREY, LIGHT = "#b9b8ad", "#e4e3dd"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlelocation": "left", "figure.dpi": 150,
                     "pdf.fonttype": 42, "svg.fonttype": "none"})

fs = json.loads((U / "frontier" / "summary.json").read_text())
ms = json.loads((U / "models" / "summary.json").read_text())
comp = pd.read_csv(U / "out" / "metadata_standard_compliance.csv")
elem = pd.read_csv(U / "out" / "metadata_standard_elements.csv")
pilot = pd.read_csv(U / "out" / "metadata_standard_frontier.csv")
pts = pd.read_csv(U / "frontier" / "frontier_points.csv")
qq = pd.read_csv(U / "frontier" / "questions.csv", dtype={"sid": str})
cfg = pd.read_csv(U / "models" / "summary_config.csv")
sizes = json.loads((U / "out" / "metadata_standard_example_sizes.json").read_text())


def n(x, d=0):
    """Number in LaTeX with a thin-space-free comma separator."""
    s = f"{x:,.{d}f}"
    return s.replace(",", "{,}")


def k(x, d=1):
    return f"{x / 1000:.{d}f}"


# ---------------------------------------------------------------- numbers
cnt = comp.groupby(["platform", "status"]).size().unstack(fill_value=0)
pc = pilot[pilot.comparable]
u5 = pc[(pc.question == "U5MR") & (pc.server != "compliant")]
dt = pc[(pc.question == "DTP3") & (pc.server != "compliant")]
cheap_u5 = u5.loc[u5.characters.idxmin()]
comp_u5 = pc[(pc.question == "U5MR") & (pc.server == "compliant")].iloc[0]
comp_dt = pc[(pc.question == "DTP3") & (pc.server == "compliant")].iloc[0]
d360meta = pc[pc.path.str.contains("get_metadata")]
tm = ms["tokens_mean"]
N = {
    # standard
    "whMeets": cnt.loc["warehouse", "meets"], "whPartial": cnt.loc["warehouse", "partial"],
    "dMeets": cnt.loc["data360", "meets"], "dPartial": cnt.loc["data360", "partial"],
    "unMeets": cnt.loc["undc", "meets"] if "meets" in cnt else 0, "unPartial": cnt.loc["undc", "partial"],
    # pilot
    "pilotPaths": len(pc), "cheapUChars": n(cheap_u5.characters), "cheapUShare": n(cheap_u5.share_delivered),
    "compUChars": n(comp_u5.characters), "compDChars": n(comp_dt.characters),
    "compUOverCheap": n((comp_u5.characters / cheap_u5.characters - 1) * 100),
    "compliantResp": n(sizes["U5MR"]["characters"]), "compliantFilled": n(sizes["U5MR"]["filled"]),
    "dMetaShareMin": n(d360meta.share_delivered.min()), "dMetaShareMax": n(d360meta.share_delivered.max()),
    "unPilotShareMin": n(pc[pc.server == "undc"].share_delivered.min()), "unPilotShareMax": n(pc[pc.server == "undc"].share_delivered.max()),
    "whDtpChars": n(dt[dt.server == "warehouse"].characters.min()), "whDtpShare": n(dt[dt.server == "warehouse"].share_delivered.max()),
    # sector and country
    "nSeries": fs["series"], "nQuestions": fs["questions"], "nQuestionsD": fs["questions_d360"], "nAnswers": len(pts),
    "callsUsed": fs["calls_used"], "answeredBoth": fs["answered_both"],
    "whShareMin": n(fs["wh_share_min"]), "whShareMax": n(fs["wh_share_max"]), "unShareMax": n(fs["un_share_max"]),
    "dShareMin": n(fs["wb_share_min"]), "dShareMax": n(fs["wb_share_max"]), "unCheaper": fs["un_cheaper"],
    "medWh": k(fs["median_chars"]["warehouse"]), "medUn": k(fs["median_chars"]["undc"]), "medD": k(fs["median_chars"]["d360"]),
    "discUn": n(fs["discovery_share"]["undc"]), "discWh": n(fs["discovery_share"]["warehouse"]), "structWh": n(fs["structure_share"]["warehouse"]),
    "dataUn": n(fs["data_share"]["undc"]), "dataWh": n(fs["data_share"]["warehouse"]),
    "dataCallWh": k(fs["median_data_call"]["warehouse"]), "dataCallUn": k(fs["median_data_call"]["undc"]),
    "searchWh": k(fs["median_search_wh"]), "unMaxChars": n(fs["un_max_chars"] / 1000),
    "dFound": fs["d360_found"], "dSeries": fs["d360_series"],
    "braAns": fs["answered_by_country"]["warehouse"]["BRA"], "somAns": fs["answered_by_country"]["warehouse"]["SOM"],
    "braQ": fs["questions_by_country"]["BRA"], "somQ": fs["questions_by_country"]["SOM"],
    "noDataWh": k(fs["nodata_median_chars"]["warehouse"]), "noDataUn": k(fs["nodata_median_chars"]["undc"]),
    "rhoUn": f"{fs['rank_corr_variants']['undc']:.2f}", "rhoWh": f"{fs['rank_corr_variants']['warehouse']:.2f}",
    "unAgree": fs["un_agree_full"], "unCommon": fs["un_answered_common"], "unLatSame": fs["un_latest_same"],
    "unLatEarlier": fs["un_latest_earlier"], "unLatLater": fs["un_latest_later"], "dAgree": fs["wb_agree_full"], "dCommon": fs["wb_common"],
    "dLatSame": fs["wb_latest_same"], "dLatEarlier": fs["wb_latest_earlier"], "dLatN": fs["wb_latest_n"],
    # models
    "sessions": ms["sessions"], "valuesRep": n(ms["values_reported"]), "valuesOK": n(ms["values_matched"]),
    "valuesGrounded": n(ms["values_grounded"]), "boundsRep": ms["bounds_reported"], "boundsOK": ms["bounds_grounded"],
    "refYears": ms["reference_years_per_setting"], "cellsSameVal": ms["cells_same_values"], "cellsSameSeries": ms["cells_same_series"],
    "cells": ms["cells"], "metaSpread": ms["meta_spread_max"], "repSeries": ms["repeat_same_series"], "repCalls": ms["repeat_calls_differ"],
    "repMax": ms["repeat_sent_change_max_pct"], "repMed": abs(ms["repeat_sent_median_change_pct"]), "opusEffort": ms["opus_effort_sent_change_pct"],
    "haikuRatio": ms["haiku_vs_sonnet_medium_received"], "sigs": ms["identical_call_signatures"], "sigsSame": ms["identical_content"],
    "unSigs": ms["undc_signatures"], "unByteDiff": ms["undc_byte_different"], "sentPerRecv": ms["sent_per_received"],
    "baseShare": ms["baseline_share_pct"], "cacheShare": ms["cached_share_pct"], "baseTok": n(ms["baseline_tokens_per_request"]),
    "schemaUn": n(ms["schema_tokens_median"]["un"]), "schemaWh": n(ms["schema_tokens_median"]["wh"]), "schemaD": n(ms["schema_tokens_median"]["wb"]),
    "defMin": n(min(v["schema_tokens_resent"] for v in tm.values()) / 1000), "defMax": n(max(v["schema_tokens_resent"] for v in tm.values()) / 1000),
    "respMin": n(min(v["other"] for v in tm.values()) / 1000), "respMax": n(max(v["other"] for v in tm.values()) / 1000),
    "reqMin": n(min(ms["requests_median"].values())), "reqMax": n(max(ms["requests_median"].values())),
    "charsUnNoFile": k(ms["chars_per_question_excl_instructions"]["un"]), "charsWhAg": k(ms["chars_per_question_excl_instructions"]["wh"]),
    "charsDAg": k(ms["chars_per_question_excl_instructions"]["wb"]), "instrChars": n(round(ms["instruction_file_chars"], -3)),
    "dMetaChars": n(round(ms["d360_get_metadata_chars"], -2)), "tsCalls": ms["wh_get_time_series_calls"], "qdCalls": ms["wh_query_data_calls"],
    "oversizedM": f"{ms['oversized_chars'] / 1e6:.1f}",
}
for c in cfg.itertuples():
    key = "".join(w.capitalize() for w in c.config.replace("-rep2", "-repeat").split("-"))
    N[f"recv{key}"] = n(c.received_median); N[f"calls{key}"] = c.mcp_calls_total; N[f"sent{key}"] = n(c.sent_k_median)
# design section: paired sign tests and zero-error bounds


def pval(x):
    """p-value for the text: exact when not tiny, otherwise an upper bound."""
    for b in (1e-12, 1e-9, 1e-6, 1e-4):
        if x < b:
            return f"$<10^{{{int(round(__import__('math').log10(b)))}}}$"
    return f"{x:.1g}" if x < 0.01 else f"{x:.2f}"


T = fs["tests"]; E = ms["effort_within_cell"]
N.update({
    "tShareUnK": T["share_wh_gt_un"]["k"], "tShareUnN": T["share_wh_gt_un"]["n"], "tShareUnP": pval(T["share_wh_gt_un"]["p"]),
    "tCostUnK": T["cheaper_un_than_wh"]["k"], "tCostUnN": T["cheaper_un_than_wh"]["n"], "tCostUnP": pval(T["cheaper_un_than_wh"]["p"]),
    "tShareDK": T["share_wh_gt_d360"]["k"], "tShareDN": T["share_wh_gt_d360"]["n"], "tShareDP": pval(T["share_wh_gt_d360"]["p"]),
    "tCostDK": T["cheaper_d360_than_wh"]["k"], "tCostDN": T["cheaper_d360_than_wh"]["n"], "tCostDP": pval(T["cheaper_d360_than_wh"]["p"]),
    "effOpusK": E["opus_tokens_sent"]["high_gt_low"], "effSonnetK": E["sonnet_tokens_sent"]["high_gt_low"], "effN": E["opus_tokens_sent"]["n"],
    "effOpusRecvK": E["opus_tokens_received"]["high_gt_low"], "effSonnetRecvK": E["sonnet_tokens_received"]["high_gt_low"],
    "effP": pval(E["opus_tokens_sent"]["p"]),
    "effOpusPct": n((E["opus_tokens_sent"]["median_ratio"] - 1) * 100), "effSonnetPct": n((E["sonnet_tokens_sent"]["median_ratio"] - 1) * 100),
    "effOpusRecvPct": n((E["opus_tokens_received"]["median_ratio"] - 1) * 100), "effSonnetRecvPct": n((E["sonnet_tokens_received"]["median_ratio"] - 1) * 100),
    "repCellMed": n(E["repeat_tokens_sent"]["median_abs_change"] * 100), "repCellMax": n(E["repeat_tokens_sent"]["max_abs_change"] * 100),
    "errBoundSess": f"{ms['error_bound_sessions_95'] * 100:.1f}", "errBoundVal": f"{ms['error_bound_values_95'] * 100:.2f}",
    "wrongSessions": ms["sessions_with_wrong_value"],
})
lines = ["% generated by paper/code/assets.py -- do not edit"]
for name, v in N.items():
    lines.append(f"\\newcommand{{\\{name}}}{{{v}}}")
(GEN / "numbers.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- tables
def esc(s):
    return str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")


what = {"R1": "the canonical request that returns the same data", "R2": "server name and version; retrieval time (UTC)",
        "R3": "every default or filter applied; whether truncated", "S1": "custodian code unchanged, server id, SDG series code",
        "S2": "name, short definition, link to methodology", "S3": "unit code and label, unit multiplier",
        "S4": "every dimension coded, explicit totals", "S5": "estimating agency and each republisher",
        "S6": "release, date, ingest date, current or replaced", "S7": "licence and recommended citation",
        "O1": "survey round, administrative system or model", "O2": "the period the value refers to, if different",
        "O3": "reported, adjusted, modelled, projected; provisional", "O4": "lower and upper bounds, interval type and level",
        "O5": "the custodian's note, verbatim"}
reuses = {"R1": "SDMX REST query", "R2": "MCP serverInfo; ISO 8601", "R3": "warehouse MCP appliedDefaults", "S1": "SDMX INDICATOR; SDG SERIES",
          "S2": "SDMX codelists; SDG metadata", "S3": "SDMX UNIT\\_MEASURE, UNIT\\_MULT", "S4": "SDMX dimensions, \\_T totals",
          "S5": "SDG custodian role; CCSA principle 4", "S6": "SDMX dataflow version", "S7": "FAIR R1.1",
          "O1": "SDMX DATA\\_SOURCE; SDG SOURCE\\_DETAIL", "O2": "SDG TIME\\_DETAIL; COVERAGE\\_TIME", "O3": "SDMX OBS\\_STATUS; SDG NATURE",
          "O4": "LOWER\\_BOUND, UPPER\\_BOUND", "O5": "SDG COMMENT\\_OBS; OBS\\_FOOTNOTE"}
rows = [f"{e.id} & {esc(e.element)}{'$^{*}$' if e.requirement != 'required' else ''} & {what[e.id]} & {reuses[e.id]} \\\\" for e in elem.itertuples()]
(GEN / "tab1_standard.tex").write_text("\n".join(rows) + "\n", encoding="utf-8")

mark = {"meets": "M", "partial": "P", "missing": "--"}
piv = comp.pivot(index="element", columns="platform", values="status").reindex(elem.id)
rows = [f"{e.id} {esc(e.element)} & {mark[piv.loc[e.id, 'warehouse']]} & {mark[piv.loc[e.id, 'undc']]} & {mark[piv.loc[e.id, 'data360']]} & "
        f"{esc(comp[(comp.element == e.id) & (comp.platform == 'warehouse')].evidence.iloc[0])} \\\\" for e in elem.itertuples()]
(GEN / "tab3_compliance.tex").write_text("\n".join(rows) + "\n", encoding="utf-8")

md = (U / "frontier" / "sector_table.md").read_text(encoding="utf-8").splitlines()[2:]
rows = [" & ".join(esc(c.strip()).replace("—", "--").replace("·", "\\textperiodcentered") for c in l.strip("|").split("|")) + " \\\\" for l in md]
(GEN / "tab4_sectors.tex").write_text("\n".join(rows) + "\n", encoding="utf-8")

LABEL = {"haiku-medium": "Haiku, medium", "sonnet-low": "Sonnet, low", "sonnet-medium": "Sonnet, medium", "sonnet-high": "Sonnet, high",
         "opus-low": "Opus, low", "opus-medium": "Opus, medium", "opus-medium-rep2": "Opus, medium (repeat)", "opus-high": "Opus, high"}
rows = [f"{LABEL[c.config]} & {c.sent_k_median}k & {n(c.received_median)} & {c.mcp_calls_total} & {c.mcp_chars_median / 1000:.1f}k & "
        f"{c.years_correct} / {c.years_reported} & {c.meta_mean:.1f} \\\\" for c in cfg.itertuples()]
(GEN / "tab5_models.tex").write_text("\n".join(rows) + "\n", encoding="utf-8")

t6 = [("Question $\\times$ server cells where all 8 runs returned identical values", f"{ms['cells_same_values']} of {ms['cells']}"),
      ("Cells where all 8 runs chose the same series identifier", f"{ms['cells_same_series']} of {ms['cells']}"),
      ("Largest spread in metadata fields reported within a cell", f"{ms['meta_spread_max']} fields"),
      ("Repeat run: same series and values", f"{ms['repeat_same_values']} of {ms['cells']} cells"),
      ("Repeat run: same number of MCP calls", f"{ms['cells'] - ms['repeat_calls_differ']} of {ms['cells']} cells"),
      ("Identical calls in different sessions returning identical content", f"{ms['identical_content']} of {ms['identical_call_signatures']}"),
      ("Reported values found in the server's responses", f"{n(ms['values_grounded'])} of {n(ms['values_reported'])}"),
      ("Reported uncertainty bounds found in the server's responses", f"{ms['bounds_grounded']} of {ms['bounds_reported']}")]
(GEN / "tab6_consistency.tex").write_text("\n".join(f"{a} & {b} \\\\" for a, b in t6) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- figures
def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight"); fig.savefig(FIG / f"{name}.png", bbox_inches="tight", dpi=200); plt.close(fig)


# Figure 1: compliance counts
order = [("warehouse", "UNICEF SDMX warehouse MCP"), ("data360", "World Bank Data360 MCP"), ("undc", "UN System Data Commons MCP")]
fig, ax = plt.subplots(figsize=(6.5, 2.3))
for i, (p, lab) in enumerate(order):
    left = 0
    for st, colr, a in (("meets", COL["warehouse"], 1), ("partial", COL["warehouse"], 0.4), ("missing", GREY, 1)):
        v = int(cnt.loc[p].get(st, 0))
        ax.barh(i, v, left=left, color=colr, alpha=a, edgecolor="white", label=st if i == 0 else None)
        if v:
            ax.text(left + v / 2, i, str(v), ha="center", va="center", fontsize=9)
        left += v
ax.set_yticks(range(3), [l for _, l in order]); ax.invert_yaxis(); ax.set_xlim(0, 15); ax.set_xlabel("Elements of the standard (of 15)")
ax.legend(["Meets", "Partly meets", "Missing"], ncol=3, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0))
save(fig, "fig1_compliance")

# Figure 2: pilot frontier
fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.9), sharey=True)
for ax, (qn, title) in zip(axes, (("U5MR", "Under-five mortality (13 elements apply)"), ("DTP3", "DTP3 coverage (12 elements apply)"))):
    d = pc[pc.question == qn]
    fr = d[d.on_frontier].sort_values("characters")
    ax.plot(fr.characters / 1000, fr.share_delivered, ls="--", color="#888", lw=1)
    for r in d.itertuples():
        ax.scatter(r.characters / 1000, r.share_delivered, color=COL[r.server], s=28, zorder=3)
    ax.set_title(title, fontsize=9, fontweight="normal"); ax.set_xlim(0, 30); ax.set_ylim(0, 105); ax.set_xlabel("Characters returned (thousands)")
    ax.grid(axis="y", color=LIGHT)
axes[0].set_ylabel("Share of standard delivered (%)")
handles = [plt.Line2D([], [], marker="o", ls="", color=COL[s]) for s in ("warehouse", "undc", "d360", "compliant")]
fig.legend(handles, ["UNICEF SDMX MCP", "UN DC MCP", "Data360 MCP", "Compliant answer (estimated)"], ncol=4, frameon=False,
           loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=8)
save(fig, "fig2_pilot_frontier")

# Figure 3: sector and country scatter
fig, ax = plt.subplots(figsize=(6.5, 3.3))
names = {"warehouse": "UNICEF SDMX MCP", "undc": "UN DC MCP", "d360": "Data360 MCP"}
for s in ("undc", "d360", "warehouse"):
    d = pts[pts.server == s]
    ax.scatter(d.chars, d.share, s=14, alpha=0.6, color=COL[s], label=f"{names[s]} (median {d.chars.median() / 1000:.1f}k)")
    ax.axvline(d.chars.median(), color=COL[s], ls="--", lw=0.8)
ax.set_xscale("log"); ax.set_xlim(400, 200000); ax.set_ylim(-3, 80)
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v / 1000:g}k"))
ax.set_xlabel("Characters returned per question (log scale)"); ax.set_ylabel("Share of standard delivered (%)"); ax.grid(axis="y", color=LIGHT)
ax.legend(frameon=False, fontsize=8, loc="upper left", ncol=1)
save(fig, "fig3_sector_scatter")

# Figure 4: cost components
tot = qq.groupby("server")[["disc_chars", "struct_chars", "data_chars", "chars"]].sum()
nq = qq.groupby("server").size()
fig, ax = plt.subplots(figsize=(6.5, 2.2))
for i, s in enumerate(("warehouse", "undc", "d360")):
    left = 0
    for c, colr, a in (("disc_chars", COL["warehouse"], 1), ("struct_chars", GREY, 0.45), ("data_chars", GREY, 1)):
        f = tot.loc[s, c] / tot.loc[s, "chars"] * 100
        ax.barh(i, f, left=left, color=colr, alpha=a, edgecolor="white")
        if f >= 5:
            ax.text(left + f / 2, i, f"{f:.0f}%", ha="center", va="center", fontsize=8)
        left += f
    ax.text(102, i, f"mean {tot.loc[s, 'chars'] / nq[s] / 1000:.1f}k, {nq[s]} questions", va="center", fontsize=8)
ax.set_yticks(range(3), [names[s] for s in ("warehouse", "undc", "d360")]); ax.invert_yaxis(); ax.set_xlim(0, 100)
ax.set_xlabel("Share of all characters returned (%)")
ax.legend([plt.Rectangle((0, 0), 1, 1, color=COL["warehouse"]), plt.Rectangle((0, 0), 1, 1, color=GREY, alpha=0.45), plt.Rectangle((0, 0), 1, 1, color=GREY)],
          ["Discovery (search)", "Structure (dimensions)", "Data call (carries the metadata)"], ncol=3, frameon=False, loc="lower center",
          bbox_to_anchor=(0.5, 1.0), fontsize=8)
save(fig, "fig4_cost_components")

# Figure 5: model and effort settings
fig, ax = plt.subplots(figsize=(6.5, 3.0))
c5 = cfg.set_index("config").loc[list(LABEL)]
ax.barh(range(len(c5)), c5.received_median, color=[COL["warehouse"] if i.startswith("haiku") else GREY for i in c5.index])
for i, r in enumerate(c5.itertuples()):
    ax.text(r.received_median + 40, i, f"{r.received_median:,.0f}   ({r.mcp_calls_total} calls; {r.years_correct}/{r.years_reported} years correct)",
            va="center", fontsize=8)
ax.set_yticks(range(len(c5)), [LABEL[i] for i in c5.index]); ax.invert_yaxis(); ax.set_xlim(0, 5200)
ax.set_xlabel("Tokens received per question (median)")
save(fig, "fig5_model_effort")

# Figure 6: tokens sent by component
fig, ax = plt.subplots(figsize=(6.5, 2.2))
lab6 = {"wh": "UNICEF SDMX MCP", "un": "UN DC MCP", "wb": "Data360 MCP"}
for i, s in enumerate(("wh", "un", "wb")):
    v = tm[s]; left = 0
    for c, colr, a in (("tokens_sent_baseline", GREY, 0.35), ("schema_tokens_resent", COL["warehouse"], 1), ("other", GREY, 1)):
        ax.barh(i, v[c] / 1000, left=left, color=colr, alpha=a, edgecolor="white"); left += v[c] / 1000
    ax.text(v["tokens_sent_baseline"] / 2000, i, f"{v['tokens_sent_baseline'] / 1000:.0f}k", ha="center", va="center", fontsize=8)
    ax.text(left + 8, i, f"+{v['schema_tokens_resent'] / 1000:.0f}k definitions, +{v['other'] / 1000:.0f}k responses", va="center", fontsize=8)
ax.set_yticks(range(3), [lab6[s] for s in ("wh", "un", "wb")]); ax.invert_yaxis(); ax.set_xlim(0, 1050)
ax.set_xlabel("Tokens sent per question, thousands (mean of 32 sessions per server)")
ax.legend([plt.Rectangle((0, 0), 1, 1, color=GREY, alpha=0.35), plt.Rectangle((0, 0), 1, 1, color=COL["warehouse"]), plt.Rectangle((0, 0), 1, 1, color=GREY)],
          ["Client baseline (re-sent each request)", "Server tool definitions", "Responses and reasoning"], ncol=3, frameon=False,
          loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=8)
save(fig, "fig6_tokens_sent")
print(f"wrote {len(N)} numbers, 5 tables, 6 figures")
