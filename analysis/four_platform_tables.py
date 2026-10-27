"""
Four-platform metadata matrix and call/token cost tables (UN DC, Data360, IHME GBD, UNICEF SDMX warehouse via MCP).
Inputs : ../unicefmcp/series_all.csv, flows_all.csv, codelist_unicef_indicator.csv, cost/calls.csv,
         ../universe/undc_unicef_metadata.csv, metadata_unicef_d360_*.csv, subagent token logs (hard-coded below from the run records)
Outputs: ../unicefmcp/out/metadata_four_platforms.csv, cost_standard_query.csv, cost_bulk_extraction.csv, dw_attribute_coverage_by_flow.csv
Run    : python3 -I four_platform_tables.py
"""
import json, glob
import pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
M, U = ROOT / "unicefmcp", ROOT / "universe"
OUT = M / "out"

# ---------------------------------------------------------------- warehouse attribute coverage (national flows, 3 countries)
s = pd.read_csv(M / "series_all.csv", dtype=str, keep_default_na=False)
s = s[~s.flowRef.str.contains("SUBNAT|CME_SUBNATIONAL|MG_FLOW")].copy()
s["flow"] = s.flowRef.str.split("/").str[1]
s["x"] = s.extra_attrs_json.map(lambda t: json.loads(t) if t else {})
def xs(a): return s.x.map(lambda x: bool(x.get(a)))
cov = s.groupby("flow").agg(n_obs=("value", "size"), bounds=("lower_bound", lambda c: (c != "").mean()), obs_status=("obs_status", lambda c: (c != "").mean()),
                            data_source=("data_source", lambda c: (c != "").mean()), unit_measure=("unit_measure", lambda c: (c != "").mean()),
                            country_notes=("country_notes_flag", lambda c: (c == "1").mean()))
for a in ["OBS_FOOTNOTE", "SERIES_FOOTNOTE", "SOURCE_LINK", "COVERAGE_TIME", "UNIT_MULTIPLIER", "WGTD_SAMPL_SIZE", "STD_ERR", "CUSTODIAN"]:
    cov[a.lower()] = xs(a).groupby(s.flow).mean()
cov.loc["ALL NATIONAL FLOWS"] = [len(s)] + [(s.lower_bound != "").mean(), (s.obs_status != "").mean(), (s.data_source != "").mean(), (s.unit_measure != "").mean(),
                                            (s.country_notes_flag == "1").mean()] + [xs(a).mean() for a in ["OBS_FOOTNOTE", "SERIES_FOOTNOTE", "SOURCE_LINK", "COVERAGE_TIME", "UNIT_MULTIPLIER", "WGTD_SAMPL_SIZE", "STD_ERR", "CUSTODIAN"]]
cov.round(3).to_csv(OUT / "dw_attribute_coverage_by_flow.csv")
tot = cov.loc["ALL NATIONAL FLOWS"]
cl = pd.read_csv(M / "codelist_unicef_indicator.csv", dtype=str, keep_default_na=False)
fl = pd.read_csv(M / "flows_all.csv", dtype=str, keep_default_na=False)
d360 = pd.concat([pd.read_csv(f, dtype=str, keep_default_na=False) for f in glob.glob(str(U / "metadata_unicef_d360_*.csv"))], ignore_index=True)
undc = pd.read_csv(U / "undc_unicef_metadata.csv", dtype=str, keep_default_na=False)
pct = lambda x: f"{100*x:.0f}%"

# ---------------------------------------------------------------- metadata matrix
rows = [
 ("Indicator definition / description",
  f"none: 0 of {len(undc)} UN DC facet rows carry a description; variable names only (e.g. 'Annual rate of reduction in mortality rate [Age=Under 5 years old]')",
  f"definition_long for {pct((d360.definition_long_300chars != '').mean())} of the 117 matched indicators; limitations text for {pct((d360.limitations_150chars != '').mean())}",
  "tool-level definitions (tool descriptions, define_term, covariate.description); measure codes such as 5q0",
  f"codelist description for {int((cl.description != '').sum())} of {len(cl)} CL_UNICEF_INDICATOR codes; dataflow descriptions for all {len(fl)} flows"),
 ("Original data producer / source per observation",
  "provenance 'United Nations' + https://data.unicef.org/ on every UNICEF facet; the producing programme (IGME, WUENIC, JMP, UNAIDS, DHS/MICS) is never named",
  f"'sources' field on 100% of matched indicators (database-level, e.g. 'UNICEF, WHO, World Bank, UN DESA'); authoring_entity for {pct((d360.authoring_entity != '').mean())}",
  "citation 'IHME GBD 2023' on every response; covariate framing text distinguishes modelled estimates from official WHO/UNICEF figures",
  f"DATA_SOURCE on {pct(tot.data_source)} of observations (100% in CME, IMMUNISATION, HIV_AIDS, MNCH, NUTRITION, DM, WASH; a dimension in MNCH and HIV_AIDS); SOURCE_LINK on {pct(tot.source_link)}; CUSTODIAN on {pct(tot.custodian)} (NUTRITION)"),
 ("Unit of measure",
  "unit on 94% of facets, as a label ('Percent', 'Count'); several mislabels found (CME_PND 0–1 fractions and PV_CHLD_DPRV averages labelled Percent)",
  f"UNIT_MEASURE code + label on {pct((d360.unit != '').mean())} of matched indicators",
  "in tool description / covariate unit (proportion 0–1, rate per 1,000); not repeated as a field on mortality trends",
  f"UNIT_MEASURE code on {pct(tot.unit_measure)} of observations; UNIT_MULTIPLIER on {pct(tot.unit_multiplier)} (thousands for DM population/births and JME counts, millions for ODA)"),
 ("Uncertainty bounds", "none", "none", "95% uncertainty interval on every value (lower/upper)",
  f"LOWER_BOUND/UPPER_BOUND on {pct(tot.bounds)} of observations: 100% CME and CME_CAUSE_OF_DEATH, 95% HIV_AIDS, 96% NUTRITION; none in IMMUNISATION, WASH, DM, MG"),
 ("Observation status flags", "none", "none", "none (modelled estimates throughout)",
  f"OBS_STATUS on {pct(tot.obs_status)} of observations (codes from UNICEF's CL_OBS_STATUS: A normal value, E estimated, RP reported, RA reanalysed, AD adjusted, MD modelled, PR projection, PRED predicted)"),
 ("Footnotes and country notes", "none", "none", "fixed methods/reporting rules text (~2.5k characters per response)",
  f"OBS_FOOTNOTE {pct(tot.obs_footnote)}, SERIES_FOOTNOTE {pct(tot.series_footnote)}, COUNTRY_NOTES {pct(tot.country_notes)} (e.g. the IGME disclaimer on India), COVERAGE_TIME {pct(tot.coverage_time)}"),
 ("Release / vintage identification",
  "none per series (facet importName only); values show which release was ingested (WUENIC 2024 revision, UNAIDS 2025, JMP 2025 round)",
  "version_statement.version_date on 100% of matched indicators (mostly 2024 dates) and time_periods; date_last_update null",
  "GBD round in the citation (GBD 2023); years_available per covariate",
  "release named inside DATA_SOURCE labels ('WHO/UNICEF estimates…, 2025 revision', 'UNAIDS 2026 estimates', 'GIDD, IDMC, 2026', 'WUP 2025'); dataflow isFinal flag; no series-level version date"),
 ("Sample size / standard error", "none", "none", "none (UI only)", f"WGTD_SAMPL_SIZE on {pct(tot.wgtd_sampl_size)}, STD_ERR on {pct(tot.std_err)} of observations (survey-based flows)"),
 ("Dimension model",
  "breakdowns encoded in DCID suffixes (AGE, SEX, VACCINE, WASH_SERVICE, GOVERNMENT_FUNCTION…): 3,607 variants for 247 codes; totals exist for 85 codes only",
  "disaggregation endpoint (SEX, URBANISATION, COMP_BREAKDOWN_1); most UNICEF-origin series carried as totals",
  "age group, sex, location tiers (global → admin1 for 17 countries), cause/risk hierarchies",
  "full SDMX DSD per flow: 2 (ECONOMIC) to 12 (PT_CM) dimensions, codelists for every dimension, _T totals; the same indicator also copied into GLOBAL_DATAFLOW with SEX only"),
 ("Machine-readable code lists", "no codelists; DCIDs + names via search", "codelist lookup tool (data360_find_codelist_value)", "lookup_term, list_children, resolve_location_group",
  f"complete SDMX structures: {len(cl)} indicator codes, {len(fl)} dataflows, unit and status codelists; get_flow_structure returns ~1.3 MB per flow"),
 ("Licence", "none exposed", "licence on 100% of matched indicators (CC BY 4.0; CC BY-NC 3.0 IGO for 7)", "citation only", "none in the SDMX payload (terms of use on the website only)"),
 ("Subnational data", "child-place tools (admin1/admin2 where ingested)", "none", "admin1 for 17 countries", "dedicated subnational flows (CME_SUBNATIONAL, PT_CM_SUBNATIONAL, WASH_HOUSEHOLD_SUBNAT) with REF_AREA_PARENT"),
]
pd.DataFrame(rows, columns=["metadata element", "UN System Data Commons", "World Bank Data360", "IHME GBD", "UNICEF SDMX warehouse (MCP)"]).to_csv(OUT / "metadata_four_platforms.csv", index=False)

# ---------------------------------------------------------------- cost: standard query (measured, cost/calls.csv)
c = pd.read_csv(M / "cost" / "calls.csv", dtype=str, keep_default_na=False)
c["chars"] = pd.to_numeric(c.chars); c["n_obs"] = pd.to_numeric(c.n_obs)
rows = []
for (plat, q), g in c.groupby(["platform", "question"], sort=False):
    rows.append(dict(platform=plat, question=q, calls=len(g), errors=int((g.status == "error").sum()), chars=int(g.chars.sum()),
                     chars_excl_setup=int(g[g.tool != "ReadMcpResourceTool"].chars.sum()), observations=int(g.n_obs.max()),
                     chars_per_obs=round(g.chars.sum() / max(g.n_obs.max(), 1)), bounds="yes" if (g.has_uncertainty.str.startswith("yes")).any() else "no",
                     obs_status="yes" if (g.has_obs_status.str.startswith("yes")).any() else "no", source="yes" if (g.has_source.str.startswith("yes")).any() else "partial/no",
                     vintage="yes" if (g.has_release_date.str.startswith("yes")).any() else ("partial" if (g.has_release_date.str.startswith("partial")).any() else "no")))
# minimal paths for the UNICEF MCP (measured in the same run)
rows.append(dict(platform="Unicef_MCP_Yves (minimal: find + list_dimensions + query_data)", question="U5MR", calls=3, errors=0, chars=6220 + 932 + 3790, chars_excl_setup=6220 + 932 + 3790, observations=25, chars_per_obs=round((6220 + 932 + 3790) / 25), bounds="yes", obs_status="yes", source="yes", vintage="no"))
rows.append(dict(platform="Unicef_MCP_Yves (minimal: find + get_time_series)", question="U5MR", calls=2, errors=0, chars=6220 + 2591, chars_excl_setup=6220 + 2591, observations=25, chars_per_obs=round((6220 + 2591) / 25), bounds="no (compact mode drops them)", obs_status="no", source="partial", vintage="no"))
pd.DataFrame(rows).to_csv(OUT / "cost_standard_query.csv", index=False)

# ---------------------------------------------------------------- cost: bulk extraction by subagents (tokens from the run records of this study)
bulk = pd.DataFrame([
 ("UN System Data Commons", "round 1 crosswalk values A", 246866, 130, 705), ("UN System Data Commons", "round 1 crosswalk values B", 273291, 179, 645),
 ("UN System Data Commons", "round 2 universe values 1", 272209, 256, 1088), ("UN System Data Commons", "round 2 universe values 2", 283423, 255, 1443),
 ("UN System Data Commons", "round 2 universe values 3", 254995, 170, 1066), ("UN System Data Commons", "round 2 remaining codes 1", 267646, 215, 1272),
 ("UN System Data Commons", "round 2 remaining codes 2", 303349, 199, 1306), ("UN System Data Commons", "round 2 remaining codes 3", 272801, 186, 598),
 ("World Bank Data360", "round 1 crosswalk values (+32 metadata calls)", 481381, 126, 1000), ("World Bank Data360", "round 2 universe values 1 (+59 metadata)", 720579, 167, 2491),
 ("World Bank Data360", "round 2 universe values 2 (+58 metadata)", 299510, 267, 2216),
 ("IHME GBD", "round 1 crosswalk values", 471322, 115, 2112),
 ("UNICEF SDMX MCP", "round 3 catalogue + series, flow group A (14 flows)", 612112, 145, 28986), ("UNICEF SDMX MCP", "round 3 flow group B (14 flows)", 634121, 160, 26012),
 ("UNICEF SDMX MCP", "round 3 flow group C (13 flows)", 552146, 134, 29444),
], columns=["platform", "task", "subagent_tokens", "tool_calls", "observations_retrieved"])
# split the 84,442 warehouse rows across groups in proportion to the series files
try:
    import csv
    n = {g: len(pd.read_csv(M / f"group_{g}" / f"series_group_{g}.csv", dtype=str, keep_default_na=False)) for g in ("a", "b", "c")}
    bulk.loc[bulk.task.str.contains("group A"), "observations_retrieved"] = n["a"]; bulk.loc[bulk.task.str.contains("group B"), "observations_retrieved"] = n["b"]; bulk.loc[bulk.task.str.contains("group C"), "observations_retrieved"] = n["c"]
except Exception as e:
    print("group series counts not found:", e)
bulk["tokens_per_call"] = (bulk.subagent_tokens / bulk.tool_calls).round(0)
bulk["tokens_per_observation"] = (bulk.subagent_tokens / bulk.observations_retrieved).round(0)
tot_b = bulk.groupby("platform").agg(subagent_tokens=("subagent_tokens", "sum"), tool_calls=("tool_calls", "sum"), observations_retrieved=("observations_retrieved", "sum"))
tot_b["tokens_per_call"] = (tot_b.subagent_tokens / tot_b.tool_calls).round(0); tot_b["tokens_per_observation"] = (tot_b.subagent_tokens / tot_b.observations_retrieved).round(0)
tot_b["observations_per_call"] = (tot_b.observations_retrieved / tot_b.tool_calls).round(1)
bulk.to_csv(OUT / "cost_bulk_extraction.csv", index=False); tot_b.to_csv(OUT / "cost_bulk_extraction_totals.csv")
print(pd.DataFrame(rows).to_string(index=False)); print(tot_b.to_string())
print(cov.round(2).loc[["CME", "IMMUNISATION", "NUTRITION", "HIV_AIDS", "MNCH", "DM", "WASH_HOUSEHOLDS", "GLOBAL_DATAFLOW", "ALL NATIONAL FLOWS"]].to_string())
