"""
UNICEF indicator universe: UN System Data Commons vs World Bank Data360
Inputs : ../universe/*.csv (enumeration, matching, verbatim values, metadata)
Outputs: ../universe/out/*.csv
Run    : python3 -I unicef_compare.py
"""
import json, re
import numpy as np, pandas as pd
from pathlib import Path

U = Path(__file__).resolve().parent.parent / "universe"
OUT = U / "out"; OUT.mkdir(exist_ok=True)
COUNTRIES = ["NGA", "IND", "BRA"]

# ------------------------------------------------------------ universe + matching
codes = pd.read_csv(U / "undc_unicef_codes.csv", dtype=str).fillna("")
match = pd.concat([pd.read_csv(U / "d360_match_part1.csv", dtype=str), pd.read_csv(U / "d360_match_part2.csv", dtype=str)], ignore_index=True).fillna("")
match["rank"] = match.match_quality.map({"same": 0, "related": 1, "none": 2}) + match.unicef_sourced.map({"yes": 0}).fillna(0.5)
best = match.sort_values(["indicator_code", "rank"]).groupby("indicator_code").head(1).copy()
n_same = match[match.match_quality == "same"].groupby("indicator_code").size().rename("n_same_candidates")
n_unicef = match[(match.match_quality == "same") & (match.unicef_sourced == "yes")].groupby("indicator_code").size().rename("n_unicef_sourced_candidates")
dbs = match[match.match_quality == "same"].groupby("indicator_code").d360_database_id.agg(lambda s: ";".join(sorted(set(s)))).rename("d360_databases_same")
universe = codes.merge(best[["indicator_code", "match_quality", "unicef_sourced", "d360_idno", "d360_database_id", "d360_name", "d360_source", "notes"]], on="indicator_code", how="left") \
    .merge(n_same, on="indicator_code", how="left").merge(n_unicef, on="indicator_code", how="left").merge(dbs, on="indicator_code", how="left")
universe[["n_same_candidates", "n_unicef_sourced_candidates"]] = universe[["n_same_candidates", "n_unicef_sourced_candidates"]].fillna(0).astype(int)
universe["in_data360"] = np.where(universe.match_quality == "same", "same concept", np.where(universe.match_quality == "related", "related only", "absent"))
universe["has_data_5_countries"] = universe.undc_obs_5countries.astype(str).str.strip() != ""
universe.to_csv(OUT / "unicef_universe_crosswalk.csv", index=False)

summ = universe.groupby("dataflow").agg(n_codes=("indicator_code", "size"),
                                         same=("in_data360", lambda s: (s == "same concept").sum()),
                                         related=("in_data360", lambda s: (s == "related only").sum()),
                                         absent=("in_data360", lambda s: (s == "absent").sum()),
                                         unicef_sourced=("n_unicef_sourced_candidates", lambda s: (s > 0).sum()),
                                         no_data_5_countries=("has_data_5_countries", lambda s: (~s).sum()))
summ.loc["TOTAL"] = summ.sum()
summ.to_csv(OUT / "universe_summary_by_dataflow.csv")

# ------------------------------------------------------------ values
u = pd.concat([pd.read_csv(U / f"values_unicef_undc_{i}.csv", dtype=str, keep_default_na=False) for i in (1, 2, 3)], ignore_index=True)
d = pd.concat([pd.read_csv(U / f"values_unicef_d360_{i}.csv", dtype=str, keep_default_na=False) for i in (1, 2)], ignore_index=True)
u = u[(u.year != "") & (u.value != "")].copy(); d = d[(d.year != "") & (d.value != "") & (d.value != "null")].copy()
u["v"] = pd.to_numeric(u.value, errors="coerce"); d["v"] = pd.to_numeric(d.value, errors="coerce")
u["yr"] = u.year.str[:4].astype(int); d["yr"] = d.year.str[:4].astype(int)

def is_total(dims):
    """keep Data360 rows whose dimensions are totals / the single matched breakdown"""
    if dims == "": return True
    try: j = json.loads(dims)
    except Exception: return True
    for k, val in j.items():
        if k == "SEX" and val not in ("_T", "T", "F"):  # F kept for women-only indicators, filtered later
            return False
        if k in ("URBANISATION", "URBANIZATION") and val not in ("URB", "_T", "T"):
            return False
        if k == "COMP_BREAKDOWN_1":
            continue
    return True
d["is_total"] = d.dimensions.map(is_total)
# women-only indicators where Data360 carries SEX=F
women = {"GN_ED_ATTN": "F", "GN_TIMEUSE": "F", "PT_FGM_ELIM": "F", "MNCH_LIFE_EXPECTANCY": "F"}
def keep_row(r):
    if not r.is_total: return False
    if r.dimensions and "SEX" in r.dimensions:
        sex = json.loads(r.dimensions).get("SEX")
        if r.indicator_code in women: return sex == women[r.indicator_code]
        return sex in ("_T", "T")
    return True
d = d[d.apply(keep_row, axis=1)].copy()
# de-duplicate (UNICEF_DW duplicate survey clusters): keep first per code/iso3/year
d_dup = d[d.duplicated(["indicator_code", "iso3", "yr"], keep=False)]
d = d.drop_duplicates(["indicator_code", "iso3", "yr"], keep="first")
u = u.drop_duplicates(["indicator_code", "iso3", "yr"], keep="first")

# per-code coverage
cov_u = u.groupby(["indicator_code", "iso3"]).agg(undc_first=("yr", "min"), undc_last=("yr", "max"), undc_n=("yr", "size")).reset_index()
cov_d = d.groupby(["indicator_code", "iso3"]).agg(d360_first=("yr", "min"), d360_last=("yr", "max"), d360_n=("yr", "size")).reset_index()
cov = cov_u.merge(cov_d, on=["indicator_code", "iso3"], how="outer")
cov.to_csv(OUT / "coverage_by_code_country.csv", index=False)

# join on code/iso3/year
j = u[["indicator_code", "undc_dcid_queried", "iso3", "yr", "v", "value"]].rename(columns={"v": "undc", "value": "undc_raw"}) \
     .merge(d[["indicator_code", "d360_idno", "d360_database_id", "iso3", "yr", "v", "value"]].rename(columns={"v": "d360", "value": "d360_raw"}),
            on=["indicator_code", "iso3", "yr"], how="inner")
j["diff"] = j.undc - j.d360
j["rel_diff_pct"] = np.where((j.undc + j.d360) != 0, 100 * j["diff"] / ((j.undc + j.d360) / 2), np.nan)
j.to_csv(OUT / "paired_values.csv", index=False)

def summarise(g):
    ad = g.rel_diff_pct.abs()
    return pd.Series(dict(n_pairs=len(g), countries=",".join(sorted(g.iso3.unique())), years=f"{g.yr.min()}-{g.yr.max()}",
                          median_abs_rel_pct=ad.median(), max_abs_rel_pct=ad.max(), share_within_1pct=(ad <= 1).mean(),
                          share_within_5pct=(ad <= 5).mean(), mean_signed_rel_pct=g.rel_diff_pct.mean()))
agree = j.groupby(["indicator_code", "d360_idno", "d360_database_id"]).apply(summarise).reset_index()
# coverage totals per code
covc = cov.groupby("indicator_code").agg(undc_last=("undc_last", "max"), d360_last=("d360_last", "max"),
                                         undc_obs=("undc_n", "sum"), d360_obs=("d360_n", "sum")).reset_index()
agree = agree.merge(covc, on="indicator_code", how="left")
def verdict(r):
    if r.n_pairs == 0: return "no overlapping years"
    if r.share_within_1pct == 1: return "identical (within 1%)"
    if r.share_within_5pct >= 0.9: return "rounding / minor"
    return "different series or vintage"
agree["verdict"] = agree.apply(verdict, axis=1)
# codes matched but with no overlapping years
pairs = pd.read_csv(U / "extraction_pairs.csv", dtype=str).fillna("")
no_overlap = pairs[~pairs.indicator_code.isin(agree.indicator_code)][["indicator_code", "undc_dcid", "d360_idno", "d360_database_id", "unicef_sourced"]].merge(covc, on="indicator_code", how="left")
no_overlap["verdict"] = np.where(no_overlap.undc_obs.isna() & no_overlap.d360_obs.isna(), "no data on either platform (3 countries)",
                         np.where(no_overlap.undc_obs.isna(), "no UN DC data (3 countries)", np.where(no_overlap.d360_obs.isna(), "no Data360 data (3 countries)", "no overlapping years")))
agree = pd.concat([agree, no_overlap], ignore_index=True)
agree = agree.merge(pairs[["indicator_code", "unicef_sourced", "undc_name"]].drop_duplicates("indicator_code"), on="indicator_code", how="left", suffixes=("", "_p"))
agree["unicef_sourced"] = agree.unicef_sourced.fillna(agree.get("unicef_sourced_p"))
agree.to_csv(OUT / "agreement_by_code.csv", index=False)
print(agree.verdict.value_counts().to_string())
print(agree.groupby(["unicef_sourced", "verdict"]).size().unstack(fill_value=0).to_string())
print("duplicate Data360 rows dropped:", len(d_dup))
print(summ.to_string())
