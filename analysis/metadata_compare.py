"""Side-by-side metadata table: one row per indicator, three platforms. Run: python3 -I metadata_compare.py"""
import json
import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXTRACT = HERE.parent / "extract"
xw = pd.read_csv(HERE.parent / "crosswalk.csv", dtype=str).fillna("")
ua = pd.concat([pd.read_csv(EXTRACT / "metadata_undc_a.csv", dtype=str),
                pd.read_csv(EXTRACT / "metadata_undc_b.csv", dtype=str)]).fillna("")
wb = pd.read_csv(EXTRACT / "metadata_wb.csv", dtype=str).fillna("")
ih = pd.read_csv(EXTRACT / "metadata_ihme.csv", dtype=str).fillna("")
summ = pd.read_csv(HERE / "summary_by_indicator.csv")
lat = pd.read_csv(HERE / "latest_year.csv")

def undc_row(k):
    g = ua[ua.indicator_key == k]
    if g.empty:
        return {}
    # primary facet = the one with most observations
    g = g.assign(n=pd.to_numeric(g.obs_count, errors="coerce")).sort_values("n", ascending=False)
    r = g.iloc[0]
    return dict(undc_id=r.platform_indicator_id, undc_name=r.platform_indicator_name,
                undc_provenance_label=r.source_organisation, undc_custodian_url=r.source_url,
                undc_years=f"{r.date_range_start}-{r.date_range_end}", undc_obs=r.obs_count,
                undc_unit=r.unit, undc_n_facets=len(g), undc_uncertainty="none exposed")

def wb_row(k):
    g = wb[wb.indicator_key == k]
    if g.empty:
        return {}
    r = g.iloc[0]
    return dict(wb_id=r.platform_indicator_id, wb_name=r.platform_indicator_name, wb_database=r.database_name,
                wb_source=r.source_organisation[:160], wb_years=r.time_period_range, wb_latest=r.latest_data,
                wb_last_updated=r.last_updated, wb_periodicity=r.periodicity, wb_license=r.license[:12],
                wb_unit=r.unit, wb_definition=r.definition[:220], wb_uncertainty="none exposed")

def ih_row(k):
    g = ih[ih.indicator_key == k]
    if g.empty:
        return {}
    r = g.iloc[0]
    return dict(ihme_id=r.platform_indicator_id[:70], ihme_name=r.platform_indicator_name[:80], ihme_unit=r.unit[:60],
                ihme_years=r.years_available[:40], ihme_uncertainty=r.uncertainty_interval[:90],
                ihme_nature=r.modelled_vs_official_note[:160], ihme_citation=r.citation[:90])

def stats(k, pair):
    s = summ[(summ.indicator_key == k) & (summ.pair == pair)]
    if s.empty:
        return ""
    s = s.iloc[0]
    return f"n={int(s.n)}; median |rel diff| {s.median_abs_rel_pct:.1f}%; max {s.max_abs_rel_pct:.1f}%; within 1%: {100*s.share_within_1pct:.0f}%"

def latest(k, platform):
    s = lat[(lat.indicator_key == k) & (lat.platform == platform)]
    return "" if s.empty else str(int(s.latest_any_country.iloc[0])) + " (earliest country " + str(int(s.earliest_of_latest.iloc[0])) + ")"

rows = []
for _, x in xw.iterrows():
    k = x.indicator_key
    rec = dict(indicator_key=k, concept=x.concept, sdg=x.sdg_ref, comparability_class=x.comparability_class)
    rec.update(undc_row(k)); rec.update(wb_row(k)); rec.update(ih_row(k))
    rec["latest_undc"] = latest(k, "UN_DataCommons"); rec["latest_wb"] = latest(k, "WorldBank_Data360"); rec["latest_ihme"] = latest(k, "IHME_GBD2023")
    rec["agreement_undc_vs_wb"] = stats(k, "undc-wb"); rec["agreement_ihme_vs_undc"] = stats(k, "ihme-undc"); rec["agreement_ihme_vs_wb"] = stats(k, "ihme-wb")
    rows.append(rec)
out = pd.DataFrame(rows)
out.to_csv(HERE / "metadata_comparison.csv", index=False)
print(out[["indicator_key", "undc_custodian_url", "undc_years", "wb_database", "wb_last_updated", "wb_years", "ihme_years", "ihme_uncertainty"]].to_string())
