"""
Average effects with fixed effects and cluster-robust inference (paper Section 4.5 and Table 9).

Sector and country design (Q1-Q3), one row per answer (question i = series s x country c, server j):
    y_ij = alpha_i + beta_UN * UNDC_j + beta_D * Data360_j + e_ij
  alpha_i are question fixed effects, so beta compares servers within the same question; the warehouse is the base.
  Outcomes: share of the standard (percentage points; answered questions only) and ln(characters) (all questions).
  Standard errors clustered by series s (34 clusters; clustering by question is reported as a sensitivity check): series were the unit of random sampling, and the answers
  for one series share the discovery query and search results across servers and countries.

Model and effort design (Q4), one row per session (cell c = question q x server j, setting m):
    ln y_cm = alpha_c + sum_m gamma_m * Setting_m + u_cm
  alpha_c are cell fixed effects; Sonnet at medium effort is the base. Outcomes: ln(tokens sent), ln(tokens received),
  MCP calls. exp(gamma) - 1 is the proportional effect on the geometric mean. Contrasts: Opus high - Opus low,
  Sonnet high - Sonnet low, Haiku - Sonnet medium, Opus medium repeat - Opus medium.
  Standard errors clustered by cell (12 clusters): sessions in a cell share the question and the server, and the
  effect of a setting may differ across cells.

Inference: CR1 cluster-robust variance with t(G-1) reference distribution, and, because G is small, the wild cluster
restricted (WCR) bootstrap with Webb six-point weights (9,999 draws, fixed seed); HC1 shown for comparison.
Input : ../unicefmcp/frontier/questions.csv, ../unicefmcp/models/run_results.csv
Output: ../unicefmcp/out/effects.json, ../unicefmcp/out/effects.csv
Run   : python3 -I effects.py
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent / "unicefmcp"
B, SEED = 9999, 20261027
WEBB = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)])


def design(df, fe, treat, base):
    """Fixed-effect dummies (one per level of `fe`) and treatment dummies (all levels of `treat` except `base`)."""
    F = pd.get_dummies(df[fe], dtype=float)
    levels = [l for l in sorted(df[treat].unique()) if l != base]
    T = pd.DataFrame({l: (df[treat] == l).astype(float) for l in levels}, index=df.index)
    return pd.concat([T, F], axis=1), levels


def ols(X, y):
    XtXi = np.linalg.pinv(X.T @ X)
    b = XtXi @ X.T @ y
    return b, y - X @ b, XtXi


def cr1(X, e, XtXi, g):
    n, k = X.shape; G = len(np.unique(g))
    meat = np.zeros((k, k))
    for c in np.unique(g):
        s = X[g == c].T @ e[g == c]; meat += np.outer(s, s)
    k_eff = np.linalg.matrix_rank(X)
    return G / (G - 1) * (n - 1) / (n - k_eff) * XtXi @ meat @ XtXi


def hc1(X, e, XtXi):
    n = X.shape[0]; k_eff = np.linalg.matrix_rank(X)
    return n / (n - k_eff) * XtXi @ (X.T * e ** 2) @ X @ XtXi


def test(X, y, g, r, rng):
    """Estimate r'b, its CR1 and HC1 standard errors, and the WCR bootstrap p-value of H0: r'b = 0."""
    b, e, XtXi = ols(X, y)
    est = r @ b
    se = float(np.sqrt(r @ cr1(X, e, XtXi, g) @ r)); se_hc = float(np.sqrt(r @ hc1(X, e, XtXi) @ r))
    G = len(np.unique(g)); t = est / se
    # restricted estimate under H0 (r'b = 0) and its residuals
    br = b - XtXi @ r * (r @ b) / (r @ XtXi @ r)
    er = y - X @ br
    groups = np.unique(g); idx = np.searchsorted(groups, g)
    tstar = np.empty(B)
    for k in range(B):
        w = rng.choice(WEBB, size=len(groups))[idx]
        ys = X @ br + er * w
        bs, es, _ = ols(X, ys)
        tstar[k] = (r @ bs) / np.sqrt(r @ cr1(X, es, XtXi, g) @ r)
    return dict(estimate=float(est), se_cr1=se, se_hc1=se_hc, clusters=int(G), n=int(len(y)),
                t=float(t), p_cr1=float(2 * stats.t.sf(abs(t), G - 1)),
                ci95_low=float(est - stats.t.ppf(0.975, G - 1) * se), ci95_high=float(est + stats.t.ppf(0.975, G - 1) * se),
                p_wcr=float((np.abs(tstar) >= abs(t)).mean()))


rng = np.random.default_rng(SEED)
rows = []

# ---------------- sector and country design
q = pd.read_csv(ROOT / "frontier" / "questions.csv", dtype={"sid": str})
q["question"] = q.sid + "-" + q.iso3
q["ln_chars"] = np.log(q.chars)
for outcome, sample, label in (("share", q[q.answered.astype(bool)], "Share of the standard (pp)"),
                               ("ln_chars", q, "ln(characters)")):
    d = sample.reset_index(drop=True)
    X, lv = design(d, "question", "server", "warehouse")
    for l in lv:
        r = np.array([1.0 if c == l else 0.0 for c in X.columns])
        for cl, gv in (("series", d.sid.to_numpy()), ("question", d.question.to_numpy())):   # question: sensitivity only
            res = test(X.to_numpy(), d[outcome].to_numpy(float), gv, r, rng)
            rows.append(dict(design="sector", outcome=label, contrast=f"{ {'undc': 'UN DC', 'd360': 'Data360'}[l]} - warehouse",
                             cluster=cl, **res))

# ---------------- model and effort design
R = pd.read_csv(ROOT / "models" / "run_results.csv")
R["cell"] = R.qid + "-" + R.server
R["ln_sent"] = np.log(R.tokens_sent); R["ln_received"] = np.log(R.tokens_received)
X, lv = design(R, "cell", "config", "sonnet-medium")
cols = list(X.columns)
CONTRASTS = {"Opus high - Opus low": {"opus-high": 1, "opus-low": -1}, "Sonnet high - Sonnet low": {"sonnet-high": 1, "sonnet-low": -1},
             "Haiku medium - Sonnet medium": {"haiku-medium": 1}, "Opus medium repeat - Opus medium": {"opus-medium-rep2": 1, "opus-medium": -1}}
for outcome, label in (("ln_sent", "ln(tokens sent)"), ("ln_received", "ln(tokens received)"), ("mcp_calls", "MCP calls")):
    for name, w in CONTRASTS.items():
        r = np.array([float(w.get(c, 0)) for c in cols])
        res = test(X.to_numpy(), R[outcome].to_numpy(float), R.cell.to_numpy(), r, rng)
        rows.append(dict(design="model", outcome=label, contrast=name, cluster="cell", **res))

E = pd.DataFrame(rows)
E["pct_effect"] = np.where(E.outcome.str.startswith("ln("), (np.exp(E.estimate) - 1) * 100, np.nan)
E.to_csv(ROOT / "out" / "effects.csv", index=False, float_format="%.6g")
(ROOT / "out" / "effects.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
pd.set_option("display.width", 220)
print(E[["design", "outcome", "contrast", "estimate", "pct_effect", "se_cr1", "se_hc1", "clusters", "n", "p_cr1", "p_wcr"]].round(4).to_string(index=False))
