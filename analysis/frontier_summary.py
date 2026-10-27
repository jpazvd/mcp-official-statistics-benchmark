"""
Cost-frontier benchmark, step 4: chart data, the sector table and every summary figure quoted in the paper (Section 5.3).
Input : ../unicefmcp/frontier/questions.csv
Output: ../unicefmcp/frontier/frontier_points.csv, sector_table.md, summary.json
Run   : python3 -I frontier_summary.py
"""
import json
import pandas as pd
from pathlib import Path

F = Path(__file__).resolve().parent.parent / "unicefmcp" / "frontier"
q = pd.read_csv(F / "questions.csv", dtype={"sid": str})
q["answered"] = q.answered.astype(bool)
q["share0"] = q.share.where(q.answered, 0.0).fillna(0.0)

SECTORS = {"CME": "Child mortality", "DM": "Demography", "ECD": "Early childhood development", "ECON": "Economy and aid",
           "ED": "Education", "FD": "Functional difficulty", "GN": "Gender", "HVA": "HIV/AIDS", "IM": "Immunization",
           "MG": "Migration", "MNCH": "Maternal, newborn and child health", "NT": "Nutrition", "PT": "Child protection",
           "PV": "Child poverty", "SPP": "Social policy", "WS": "WASH", "WT": "Adolescents"}
SERVERS = [("warehouse", "UNICEF SDMX MCP"), ("undc", "UN DC MCP"), ("d360", "Data360 MCP")]

# chart data (one point per answer)
pts = q.assign(id=q.sid + "-" + q.iso3 + "-" + q.server)[["id", "sid", "iso3", "sector", "server", "chars", "share0", "answered"]]
pts = pts.rename(columns={"share0": "share"}).assign(answered=lambda d: d.answered.astype(int))
pts.to_csv(F / "frontier_points.csv", index=False)

# sector table: median characters and median share, unanswered questions included at 0%
lines = ["| Sector | Questions | " + " | ".join(n for _, n in SERVERS) + " |", "| --- | --- | --- | --- | --- |"]
for code, name in SECTORS.items():
    g = q[q.sector == code]
    cells = []
    for s, _ in SERVERS:
        h = g[g.server == s]
        cells.append("—" if h.empty else f"{h.chars.median() / 1000:.1f}k · {h.share0.median():.0f}%")
    lines.append(f"| {name} | {len(g[g.server == 'warehouse'])} | " + " | ".join(cells) + " |")
(F / "sector_table.md").write_text("\n".join(lines), encoding="utf-8")

# summary figures quoted in the text
wh, un, wb = (q[q.server == s].set_index(["sid", "iso3"]) for s in ("warehouse", "undc", "d360"))
both = wh.answered & un.answered.reindex(wh.index)
tot = q.groupby("server")[["disc_chars", "struct_chars", "data_chars", "chars"]].sum()
ans_un = un[un.answered & wh.answered.reindex(un.index)]
lat = (ans_un.latest - wh.latest.reindex(ans_un.index))
wb_common = wb[wb.answered & (wb.n_common_years > 0)]
wb_lat = (wb[wb.answered & wh.answered.reindex(wb.index)].latest - wh.latest.reindex(wb[wb.answered & wh.answered.reindex(wb.index)].index))
nodata = q[~q.answered]
S = dict(
    questions=int(len(wh)), questions_d360=int(len(wb)), series=int(q.sid.nunique()), calls_executed=int(len(pd.read_csv(F / 'calls.csv'))),
    calls_used=int(len(pd.read_csv(F / 'calls.csv').query("not (agent in ['un1', 'un2', 'un3'] and tool == 'get_variable_metadata')"))),  # failed metadata calls rerun by un4
    answered_both=int(both.sum()),
    wh_share_min=float(wh[both].share.min()), wh_share_max=float(wh[both].share.max()),
    un_share_max=float(un.share[un.answered].max()),
    wb_share_min=float(wb.share[wb.answered].min()), wb_share_max=float(wb.share[wb.answered].max()),
    wh_beats_un_on_standard=int((wh[both].share > un.share.reindex(wh[both].index)).sum()),
    un_cheaper=int((un.chars < wh.chars.reindex(un.index)).sum()),
    median_chars={s: float(q[q.server == s].chars.median()) for s, _ in SERVERS},
    median_share={s: float(q[q.server == s].share0.median()) for s, _ in SERVERS},
    discovery_share={s: round(100 * tot.loc[s, "disc_chars"] / tot.loc[s, "chars"], 1) for s, _ in SERVERS},
    structure_share={s: round(100 * tot.loc[s, "struct_chars"] / tot.loc[s, "chars"], 1) for s, _ in SERVERS},
    data_share={s: round(100 * tot.loc[s, "data_chars"] / tot.loc[s, "chars"], 1) for s, _ in SERVERS},
    median_data_call={s: float(q[q.server == s].data_chars.median()) for s, _ in SERVERS},
    median_search_wh=float(q[q.server == "warehouse"].drop_duplicates("sid").disc_chars.median()),
    d360_found=int(wb.drop_duplicates(subset=None).reset_index().drop_duplicates("sid").found_after_retry.astype(bool).sum()),
    d360_series=int(wb.reset_index().sid.nunique()),
    answered_by_country={s: {c: int(q[(q.server == s) & (q.iso3 == c)].answered.sum()) for c in ("NGA", "BRA", "SOM")} for s, _ in SERVERS},
    questions_by_country={c: int(len(wh.xs(c, level="iso3"))) for c in ("NGA", "BRA", "SOM")},
    nodata_median_chars={s: float(nodata[nodata.server == s].chars.median()) for s in ("warehouse", "undc")},
    rank_corr_variants={s: round(float(q[q.server == s][["undc_variants", "disc_chars"]].corr(method="spearman").iloc[0, 1]), 2)
                        for s in ("undc", "warehouse")},
    un_agree_full=int((ans_un.agree_pct == 100).sum()), un_answered_common=int(len(ans_un)),
    un_latest_same=int((lat == 0).sum()), un_latest_earlier=int((lat < 0).sum()), un_latest_later=int((lat > 0).sum()),
    wb_agree_full=int((wb_common.agree_pct == 100).sum()), wb_common=int(len(wb_common)),
    wb_latest_same=int((wb_lat == 0).sum()), wb_latest_earlier=int((wb_lat < 0).sum()), wb_latest_n=int(len(wb_lat)),
    un_max_chars=float(un.chars.max()),
)


def sign_test(k, n):
    """Exact two-sided binomial (sign) test of k successes in n paired comparisons, p = 0.5."""
    from math import comb
    pr = [comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(x for x in pr if x <= pr[k] * (1 + 1e-12)))


wbx = wb.answered & wh.answered.reindex(wb.index)
k1 = int((wh[both].share > un.share.reindex(wh[both].index)).sum())
k3 = int((wh.share.reindex(wb.index)[wbx] > wb.share[wbx]).sum())
k4 = int((wb.chars < wh.chars.reindex(wb.index)).sum())
S["tests"] = dict(share_wh_gt_un=dict(k=k1, n=int(both.sum()), p=sign_test(k1, int(both.sum()))),
                  cheaper_un_than_wh=dict(k=S["un_cheaper"], n=int(len(un)), p=sign_test(S["un_cheaper"], int(len(un)))),
                  share_wh_gt_d360=dict(k=k3, n=int(wbx.sum()), p=sign_test(k3, int(wbx.sum()))),
                  cheaper_d360_than_wh=dict(k=k4, n=int(len(wb)), p=sign_test(k4, int(len(wb)))))
(F / "summary.json").write_text(json.dumps(S, indent=1), encoding="utf-8")
print(json.dumps(S, indent=1))
