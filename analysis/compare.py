"""
Three-platform comparison of child, women and family indicators
UN System Data Commons  vs  World Bank Data360  vs  IHME GBD 2023

Inputs : ../extract/values_*.csv (raw MCP extracts, values verbatim)
Outputs: harmonized_long.csv, comparison_wide.csv, pairwise_diffs.csv,
         summary_by_indicator.csv, latest_year.csv, snapshot_2022.csv,
         within_platform_alternates.csv, ihme_growth_failure_2022.csv
Run    : python3 -I compare.py
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path

EXTRACT = Path(__file__).resolve().parent.parent / "extract"
OUT = Path(__file__).resolve().parent
COUNTRIES = ["NGA", "ETH", "IND", "BGD", "BRA"]

# ---------------------------------------------------------------- load
undc = pd.concat([pd.read_csv(EXTRACT / "values_undc_a.csv", dtype=str),
                  pd.read_csv(EXTRACT / "values_undc_b.csv", dtype=str)], ignore_index=True)
wb = pd.read_csv(EXTRACT / "values_wb.csv", dtype=str)
ihme = pd.read_csv(EXTRACT / "values_ihme.csv", dtype=str)

for df in (undc, wb, ihme):
    df["value_num"] = pd.to_numeric(df["value"].replace({"null": np.nan, "": np.nan}), errors="coerce")
    df["year_num"] = pd.to_numeric(df["year"].str[:4], errors="coerce")

# ---------------------------------------------------------------- harmonisation rules
# IHME values come in GBD native units; convert to the units used by UN DC / WB
IHME_SCALE = {  # key -> multiplier to reach the common unit
    "dtp3": 100, "mcv1": 100, "mcv2": 100, "sba": 100, "anc1": 100, "anc4": 100,
    "fp_mod": 100, "cpr_mod": 100,          # proportion -> percent
    "sbr": 1000,                            # proportion of births -> per 1,000 total births
    "abr": 1000,                            # births per woman 15-19 -> per 1,000 women 15-19
    "anem_w": 1 / 1000,                     # per 100,000 -> percent
}
# keys compared numerically on all three platforms
NUMERIC_KEYS = ["u5mr", "nmr", "imr", "mmr", "sbr", "tfr", "abr", "le0", "pop_u5",
                "dtp3", "mcv1", "mcv2", "sba", "anc1", "anc4", "fp_mod", "cpr_mod", "anem_w"]
# keys compared numerically on UN DC and WB only (same-concept, different IHME construct)
TWO_WAY_KEYS = ["stunt", "wast", "ovwt", "lbw", "ebf", "ipv", "chmar", "breg"]

UNITS = {
    "u5mr": "deaths per 1,000 live births", "nmr": "deaths per 1,000 live births",
    "imr": "deaths per 1,000 live births", "mmr": "maternal deaths per 100,000 live births",
    "sbr": "stillbirths per 1,000 total births (>=28 wks)", "tfr": "births per woman",
    "abr": "births per 1,000 women 15-19", "le0": "years", "pop_u5": "persons",
    "dtp3": "% of target population", "mcv1": "%", "mcv2": "%", "sba": "% of births",
    "anc1": "% of pregnant women", "anc4": "% of pregnant women",
    "fp_mod": "% of women 15-49 (UNDC/WB) vs % of women with demand (IHME)",
    "cpr_mod": "% of married women 15-49 (WB) vs % of all women 15-49 (IHME)",
    "anem_w": "% of women 15-49", "stunt": "% of children <5", "wast": "% of children <5",
    "ovwt": "% of children <5", "lbw": "% of live births", "ebf": "% of infants <6 months",
    "ipv": "% of ever-partnered women 15-49 (12 months)", "chmar": "% women 20-24 married <18",
    "breg": "% children <5 registered",
}

def base_key(k):
    """strip alternate-source suffixes (mmr_unicef -> mmr); keep variant separately"""
    for suf in ["_unicef", "_undp", "_who", "_national", "_survey", "_unicefdw", "_allwomen", "_wdi"]:
        if k.endswith(suf):
            return k[: -len(suf)], suf[1:]
    return k, "headline"

rows = []
for platform, df, idcol in [("UN_DataCommons", undc, "platform_indicator_id"),
                            ("WorldBank_Data360", wb, "platform_indicator_id"),
                            ("IHME_GBD2023", ihme, "platform_indicator_id")]:
    for _, r in df.iterrows():
        k, variant = base_key(r["indicator_key"])
        if platform == "IHME_GBD2023":
            # one series per key: both-sexes where available, else the single sex published (mmr, anem_w)
            if k in ("stunt", "wast", "ebf", "ipv", "ovwt", "live_births"):
                continue  # handled separately (category/age-band constructs, not comparable)
            sex = r.get("sex", "")
            # women-only measures are published for females only; everything else: both sexes
            want = "female" if k in ("mmr", "anem_w", "tfr", "abr", "fp_mod", "cpr_mod") else "both"
            if sex != want:
                continue
            if k == "imr" and r.get("age_group", "") not in ("<1 year", "under_1", "Under 1"):
                pass  # age label as returned; keep
            v = r["value_num"] * IHME_SCALE.get(k, 1)
            lo = pd.to_numeric(r.get("lower"), errors="coerce") * IHME_SCALE.get(k, 1)
            hi = pd.to_numeric(r.get("upper"), errors="coerce") * IHME_SCALE.get(k, 1)
        else:
            v, lo, hi = r["value_num"], np.nan, np.nan
            if k == "chmar" and platform == "UN_DataCommons":
                continue  # UN DC PT_MRD_U18.SEX--F is a count, not a prevalence
        if pd.isna(v) or pd.isna(r["year_num"]):
            continue
        rows.append(dict(platform=platform, indicator_key=k, variant=variant,
                         platform_indicator_id=r[idcol], iso3=r["iso3"], year=int(r["year_num"]),
                         value=v, lower=lo, upper=hi, unit=UNITS.get(k, ""),
                         raw_value=r["value"], raw_unit_note=r.get("unit_note", "")))
long = pd.DataFrame(rows)
# de-duplicate exact duplicates (e.g. UNICEF_DW duplicate survey rows) keeping first
long = long.drop_duplicates(subset=["platform", "indicator_key", "variant", "iso3", "year"], keep="first")
long.to_csv(OUT / "harmonized_long.csv", index=False)

# ---------------------------------------------------------------- headline wide table
head = long[long.variant == "headline"]
wide = (head.pivot_table(index=["indicator_key", "iso3", "year"], columns="platform", values="value", aggfunc="first")
        .reset_index())
for c in ["UN_DataCommons", "WorldBank_Data360", "IHME_GBD2023"]:
    if c not in wide:
        wide[c] = np.nan
wide = wide.rename(columns={"UN_DataCommons": "undc", "WorldBank_Data360": "wb", "IHME_GBD2023": "ihme"})
wide["unit"] = wide.indicator_key.map(UNITS)
wide["n_platforms"] = wide[["undc", "wb", "ihme"]].notna().sum(axis=1)
wide.to_csv(OUT / "comparison_wide.csv", index=False)

# ---------------------------------------------------------------- pairwise differences
pairs = [("undc", "wb"), ("ihme", "undc"), ("ihme", "wb")]
diffs = []
for a, b in pairs:
    sub = wide.dropna(subset=[a, b])
    for _, r in sub.iterrows():
        d = r[a] - r[b]
        rel = 100 * d / ((r[a] + r[b]) / 2) if (r[a] + r[b]) != 0 else np.nan
        diffs.append(dict(indicator_key=r.indicator_key, iso3=r.iso3, year=r.year, pair=f"{a}-{b}",
                          value_a=r[a], value_b=r[b], diff=d, rel_diff_pct=rel))
diffs = pd.DataFrame(diffs)
diffs.to_csv(OUT / "pairwise_diffs.csv", index=False)

def summarise(g):
    ad = g.rel_diff_pct.abs()
    return pd.Series(dict(
        n=len(g), years=f"{g.year.min()}-{g.year.max()}",
        median_abs_diff=g["diff"].abs().median(), max_abs_diff=g["diff"].abs().max(),
        median_abs_rel_pct=ad.median(), max_abs_rel_pct=ad.max(),
        share_within_1pct=(ad <= 1).mean(), share_within_5pct=(ad <= 5).mean(),
        share_within_10pct=(ad <= 10).mean(),
        mean_signed_rel_pct=g.rel_diff_pct.mean(),
        pearson_r=g[["value_a", "value_b"]].corr().iloc[0, 1] if len(g) > 2 else np.nan,
    ))
summary = diffs.groupby(["indicator_key", "pair"]).apply(summarise).reset_index()
summary["unit"] = summary.indicator_key.map(UNITS)
summary.to_csv(OUT / "summary_by_indicator.csv", index=False)

# ---------------------------------------------------------------- latest year available (headline), per platform
lat = (head.groupby(["indicator_key", "platform", "iso3"]).year.max().unstack("iso3"))
lat["latest_any_country"] = lat.max(axis=1)
lat["earliest_of_latest"] = lat[COUNTRIES].min(axis=1)
lat = lat.reset_index()
lat.to_csv(OUT / "latest_year.csv", index=False)

# ---------------------------------------------------------------- 2022 snapshot (fallback to nearest year within 2020-2024 if 2022 missing)
snap_rows = []
for (k, iso), g in head.groupby(["indicator_key", "iso3"]):
    rec = dict(indicator_key=k, iso3=iso, unit=UNITS.get(k, ""))
    for p, tag in [("UN_DataCommons", "undc"), ("WorldBank_Data360", "wb"), ("IHME_GBD2023", "ihme")]:
        gp = g[g.platform == p]
        if gp.empty:
            rec[tag] = np.nan; rec[tag + "_year"] = ""
            continue
        exact = gp[gp.year == 2022]
        if not exact.empty:
            rec[tag] = exact.value.iloc[0]; rec[tag + "_year"] = "2022"
        else:
            gp2 = gp[(gp.year >= 2018) & (gp.year <= 2024)]
            if gp2.empty:
                rec[tag] = np.nan; rec[tag + "_year"] = ""
            else:
                gp2 = gp2.assign(dist=(gp2.year - 2022).abs()).sort_values(["dist", "year"], ascending=[True, False])
                rec[tag] = gp2.value.iloc[0]; rec[tag + "_year"] = str(int(gp2.year.iloc[0]))
    snap_rows.append(rec)
snap = pd.DataFrame(snap_rows)
snap.to_csv(OUT / "snapshot_2022.csv", index=False)

# ---------------------------------------------------------------- within-platform alternates (same platform, different source series)
alt_rows = []
for (p, k), g in long.groupby(["platform", "indicator_key"]):
    if g.variant.nunique() < 2:
        continue
    piv = g.pivot_table(index=["iso3", "year"], columns="variant", values="value", aggfunc="first")
    if "headline" not in piv:
        continue
    for var in [c for c in piv.columns if c != "headline"]:
        sub = piv.dropna(subset=["headline", var])
        if sub.empty:
            continue
        d = sub["headline"] - sub[var]
        rel = 100 * d / ((sub["headline"] + sub[var]) / 2)
        alt_rows.append(dict(platform=p, indicator_key=k, alternate=var, n=len(sub),
                             years=f"{sub.index.get_level_values('year').min()}-{sub.index.get_level_values('year').max()}",
                             median_abs_rel_pct=rel.abs().median(), max_abs_rel_pct=rel.abs().max(),
                             share_identical_1pct=(rel.abs() <= 1).mean(),
                             example=f"{sub.index[0][0]} {sub.index[0][1]}: {sub['headline'].iloc[0]:.4g} vs {sub[var].iloc[0]:.4g}"))
pd.DataFrame(alt_rows).to_csv(OUT / "within_platform_alternates.csv", index=False)

# ---------------------------------------------------------------- IHME child growth failure, 2022 (illustrative; categories NOT summed)
gf = ihme[ihme.indicator_key.isin(["stunt", "wast"]) & (ihme.year == "2022")].copy()
gf["series"] = gf.dimension_note.str.split("|").str[0].str.strip()
gf = gf[gf.age_group.isin(["12 to 23 months", "2 to 4"])]
gf_w = gf.pivot_table(index=["indicator_key", "iso3", "age_group", "series"], columns="sex", values="value_num", aggfunc="first").reset_index()
gf_w.to_csv(OUT / "ihme_growth_failure_2022.csv", index=False)

print("harmonized rows:", len(long), "| wide rows:", len(wide), "| pairwise rows:", len(diffs))
print(summary.round(3).to_string())
