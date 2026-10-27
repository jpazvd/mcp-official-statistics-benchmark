"""
Minimum metadata standard for official-statistics MCP servers: element list, compliance of the three servers
(UNICEF SDMX warehouse via sdmx-mcp, UN System Data Commons, World Bank Data360) and the cost/coverage points
of the efficiency frontier.

Judgements are recorded by hand from the raw responses in ../unicefmcp/cost/raw/ (A01-A05 UN DC, B01-B04 Data360,
D01-D06 warehouse, E01-E04 metadata calls) and the extraction files (series_all.csv, flows_all.csv); each judgement
carries its evidence string. Scores: meets = 1, partial = 0.5, missing = 0; elements not applicable to a query
(no bounds or notes published by the custodian, annual modelled series) are excluded from that query's denominator.
Characters: from cost/calls.csv and, for files written later, from the files themselves (E01-E04 metadata calls;
B02b and B04b, the Data360 data calls re-run for 2000-2025 so that every path returns 25-26 observations; see
d360_same_window_raw.py). Paths are counted as executed, failed calls included; UN DC's one-off playbook read
(11,997 characters) is excluded. The first Data360 runs (1960-2024 and 1980-2024) are kept, flagged, off the frontier.
Outputs: ../unicefmcp/out/metadata_standard_elements.csv, metadata_standard_compliance.csv, metadata_standard_frontier.csv
Run    : python3 -I metadata_standard_scoring.py
"""
import os
import pandas as pd
from pathlib import Path
M = Path(__file__).resolve().parent.parent / "unicefmcp"
OUT = M / "out"; RAW = M / "cost" / "raw"

ELEMENTS = [
 ("R1", "response", "Reproducible query", "required"), ("R2", "response", "Retrieval stamp", "required"),
 ("R3", "response", "Completeness statement", "required"), ("S1", "series", "Identifiers", "required"),
 ("S2", "series", "Name and definition", "required"), ("S3", "series", "Unit", "required"),
 ("S4", "series", "Breakdown", "required"), ("S5", "series", "Custodian and provenance chain", "required"),
 ("S6", "series", "Release and currency", "required"), ("S7", "series", "Licence and citation", "required"),
 ("O1", "observation", "Source", "required"), ("O2", "observation", "Reference period", "when published"),
 ("O3", "observation", "Nature and status", "required"), ("O4", "observation", "Uncertainty", "when published"),
 ("O5", "observation", "Footnote", "when published")]
pd.DataFrame(ELEMENTS, columns=["id", "tier", "element", "requirement"]).to_csv(OUT / "metadata_standard_elements.csv", index=False)

# ---------------------------------------------------------------- platform-level compliance (status, evidence)
# meets = present in the response to a data query; partial = incomplete, uneven across flows, or only through a separate call
C = {
 "warehouse": {
  "R1": ("meets", "echoes queryURL with flow, key and period"),
  "R2": ("missing", "no timestamp or server version in responses"),
  "R3": ("meets", "appliedDefaults, maxObs and the padded key are returned"),
  "S1": ("partial", "custodian code and flow key; no SDG series link"),
  "S2": ("partial", "definition only from the discovery call; no methodology link"),
  "S3": ("meets", "UNIT_MEASURE code and UNIT_MULTIPLIER; labels on request"),
  "S4": ("meets", "full SDMX key with _T totals"),
  "S5": ("partial", "DATA_SOURCE mixes custodian, survey and pipe; CUSTODIAN only in nutrition"),
  "S6": ("partial", "release named inside DATA_SOURCE text for some flows; no date or series status"),
  "S7": ("missing", "no licence or citation in the payload"),
  "O1": ("partial", "DATA_SOURCE on 59% of observations; MNCH as bare codes"),
  "O2": ("partial", "COVERAGE_TIME filled in six flows, nutrition and HIV among them (9% of observations); not in MNCH"),
  "O3": ("partial", "OBS_STATUS on 49%; none in WASH, gender, education, economic flows"),
  "O4": ("partial", "bounds on 52% of observations; interval level never stated"),
  "O5": ("meets", "observation, series and country notes passed through")},
 "undc": {
  "R1": ("partial", "variable, place and date reproduce the call; no query returned"),
  "R2": ("missing", "none"),
  "R3": ("missing", "search returns 10 variables with no total or ranking rule"),
  "S1": ("partial", "SDG code or re-coded UNICEF code inside the variable id"),
  "S2": ("missing", "variable name only"),
  "S3": ("partial", "unit on every facet, wrong or uninformative for about 1 in 5"),
  "S4": ("partial", "breakdowns encoded in variable ids; 162 codes lack a total"),
  "S5": ("missing", "\"United Nations\" on every UNICEF facet"),
  "S6": ("missing", "nothing; withdrawn series served unflagged"),
  "S7": ("missing", "none"),
  "O1": ("missing", "none"), "O2": ("missing", "plain years"), "O3": ("missing", "none"),
  "O4": ("missing", "bounds dropped"), "O5": ("missing", "notes dropped")},
 "data360": {
  "R1": ("partial", "indicator and database ids; no query; metadata call gives a generic link"),
  "R2": ("missing", "none (a 'stale' flag only)"),
  "R3": ("partial", "has_more flags rows; period window not stated"),
  "S1": ("partial", "World Bank code; DCS code and SDG number only in metadata notes"),
  "S2": ("partial", "100-character excerpt in search; full definition via the metadata call"),
  "S3": ("meets", "code, label and UNIT_MULT on every row"),
  "S4": ("partial", "WDI series carry no dimension fields"),
  "S5": ("partial", "authoring_entity and sources via the metadata call; UNICEF credited on 65 of 117"),
  "S6": ("partial", "version_date of the World Bank database, not the custodian release"),
  "S7": ("partial", "licence via the metadata call; citation_requirement null"),
  "O1": ("partial", "survey name in some HCP rows only"),
  "O2": ("missing", "plain years"), "O3": ("missing", "none"), "O4": ("missing", "none"), "O5": ("missing", "none")}}
rows = []
for plat, d in C.items():
    for eid, (st, ev) in d.items():
        rows.append(dict(platform=plat, element=eid, status=st, evidence=ev))
comp = pd.DataFrame(rows)
comp.to_csv(OUT / "metadata_standard_compliance.csv", index=False)
score = comp.assign(pts=comp.status.map({"meets": 1, "partial": 0.5, "missing": 0})).groupby("platform").agg(
    meets=("status", lambda s: (s == "meets").sum()), partial=("status", lambda s: (s == "partial").sum()),
    missing=("status", lambda s: (s == "missing").sum()), points=("pts", "sum"))
print(score.to_string())

# ---------------------------------------------------------------- per-query paths (cost vs coverage)
calls = pd.read_csv(M / "cost" / "calls.csv", dtype=str, keep_default_na=False)
ch = {r.raw_file.split("/")[-1]: int(r.chars) for r in calls.itertuples(index=False)}
for f in ("E01_undc_varmeta_u5mr.json", "E02_undc_varmeta_dtp3.json", "E03_d360_meta_u5mr.json", "E04_d360_meta_dtp3.json",
          "B02b_d360_data_u5mr_2000.json", "B04b_d360_data_dpt_2000.json"):
    ch[f] = len(open(RAW / f, encoding="utf-8").read())
NA = "n/a"
P = {  # path -> (question, server, files, judgements per element)
 "Warehouse MCP: find + list_dimensions + query_data, one failed key (U5MR)": ("U5MR", "warehouse", ["D01_yves_find_u5mr.json", "D02_yves_list_dimensions_cme.json", "D03_yves_query_u5mr_error.txt", "D03b_yves_query_u5mr_retry.json"],
   dict(R1="meets", R2="missing", R3="meets", S1="partial", S2="partial", S3="meets", S4="meets", S5="partial", S6="missing", S7="missing", O1="meets", O2=NA, O3="partial", O4="partial", O5=NA)),
 "Warehouse MCP: find + get_time_series (U5MR, compact)": ("U5MR", "warehouse", ["D01_yves_find_u5mr.json", "D04_yves_time_series_u5mr.json"],
   dict(R1="meets", R2="missing", R3="meets", S1="partial", S2="partial", S3="meets", S4="meets", S5="missing", S6="missing", S7="missing", O1="missing", O2=NA, O3="missing", O4="missing", O5=NA)),
 "UN DC: search + get_observations (U5MR)": ("U5MR", "undc", ["A02_undc_search_u5mr.json", "A03_undc_obs_u5mr.json"],
   dict(R1="partial", R2="missing", R3="missing", S1="partial", S2="missing", S3="meets", S4="partial", S5="missing", S6="missing", S7="missing", O1="missing", O2=NA, O3="missing", O4="missing", O5=NA)),
 "UN DC: + get_variable_metadata (U5MR)": ("U5MR", "undc", ["A02_undc_search_u5mr.json", "A03_undc_obs_u5mr.json", "E01_undc_varmeta_u5mr.json"],
   dict(R1="partial", R2="missing", R3="missing", S1="partial", S2="missing", S3="meets", S4="partial", S5="missing", S6="missing", S7="missing", O1="missing", O2=NA, O3="missing", O4="missing", O5=NA)),
 "Data360: search + get_data, first run 1960-2024 (U5MR)": ("U5MR", "data360", ["B01_d360_search_u5mr.json", "B02_d360_data_u5mr.json"],
   dict(R1="partial", R2="missing", R3="partial", S1="partial", S2="partial", S3="meets", S4="partial", S5="missing", S6="missing", S7="missing", O1="missing", O2=NA, O3="missing", O4="missing", O5=NA)),
 "Data360: search + get_data (U5MR)": ("U5MR", "data360", ["B01_d360_search_u5mr.json", "B02b_d360_data_u5mr_2000.json"],
   dict(R1="partial", R2="missing", R3="partial", S1="partial", S2="partial", S3="meets", S4="partial", S5="missing", S6="missing", S7="missing", O1="missing", O2=NA, O3="missing", O4="missing", O5=NA)),
 "Data360: + get_metadata (U5MR)": ("U5MR", "data360", ["B01_d360_search_u5mr.json", "B02b_d360_data_u5mr_2000.json", "E03_d360_meta_u5mr.json"],
   dict(R1="partial", R2="missing", R3="partial", S1="partial", S2="meets", S3="meets", S4="partial", S5="meets", S6="partial", S7="partial", O1="missing", O2=NA, O3="missing", O4="missing", O5=NA)),
 "Warehouse MCP: find + query_data (DTP3)": ("DTP3", "warehouse", ["D05_yves_find_dtp3.json", "D06_yves_query_dtp3.json"],
   dict(R1="meets", R2="missing", R3="meets", S1="partial", S2="partial", S3="meets", S4="meets", S5="partial", S6="partial", S7="missing", O1="meets", O2=NA, O3="meets", O4=NA, O5=NA)),
 "UN DC: search + get_observations (DTP3)": ("DTP3", "undc", ["A04_undc_search_dtp3.json", "A05_undc_obs_dtp3.json"],
   dict(R1="partial", R2="missing", R3="missing", S1="partial", S2="missing", S3="meets", S4="partial", S5="missing", S6="missing", S7="missing", O1="missing", O2=NA, O3="missing", O4=NA, O5=NA)),
 "UN DC: + get_variable_metadata (DTP3)": ("DTP3", "undc", ["A04_undc_search_dtp3.json", "A05_undc_obs_dtp3.json", "E02_undc_varmeta_dtp3.json"],
   dict(R1="partial", R2="missing", R3="missing", S1="partial", S2="missing", S3="meets", S4="partial", S5="missing", S6="missing", S7="missing", O1="missing", O2=NA, O3="missing", O4=NA, O5=NA)),
 "Data360: search (two tries) + get_data, first run 1980-2024 (DTP3)": ("DTP3", "data360", ["B03_d360_search_dtp3.json", "B03b_d360_search_dpt_retry.json", "B04_d360_data_dpt.json"],
   dict(R1="partial", R2="missing", R3="partial", S1="partial", S2="partial", S3="meets", S4="partial", S5="missing", S6="missing", S7="missing", O1="missing", O2=NA, O3="missing", O4=NA, O5=NA)),
 "Data360: search (two tries) + get_data (DTP3)": ("DTP3", "data360", ["B03_d360_search_dtp3.json", "B03b_d360_search_dpt_retry.json", "B04b_d360_data_dpt_2000.json"],
   dict(R1="partial", R2="missing", R3="partial", S1="partial", S2="partial", S3="meets", S4="partial", S5="missing", S6="missing", S7="missing", O1="missing", O2=NA, O3="missing", O4=NA, O5=NA)),
 "Data360: + get_metadata (DTP3)": ("DTP3", "data360", ["B03_d360_search_dtp3.json", "B03b_d360_search_dpt_retry.json", "B04b_d360_data_dpt_2000.json", "E04_d360_meta_dtp3.json"],
   dict(R1="partial", R2="missing", R3="partial", S1="partial", S2="meets", S3="meets", S4="partial", S5="meets", S6="partial", S7="partial", O1="missing", O2=NA, O3="missing", O4=NA, O5=NA)),
}
fr = []
for path, (q, srv, files, j) in P.items():
    app = {k: v for k, v in j.items() if v != NA}
    pts = sum({"meets": 1, "partial": 0.5, "missing": 0}[v] for v in app.values())
    fr.append(dict(path=path, question=q, server=srv, calls=len(files), characters=sum(ch[f] for f in files),
                   applicable=len(app), meets=sum(v == "meets" for v in app.values()), partial=sum(v == "partial" for v in app.values()),
                   points=pts, share_delivered=round(100 * pts / len(app), 1), files=";".join(files)))
fr = pd.DataFrame(fr)
fr["comparable"] = ~fr.path.str.contains("first run")   # same 2000-2025 window (25-26 observations)
# efficiency frontier per question, among comparable paths: a path is on the frontier if no other comparable path for the
# same question has <= characters and >= share (one strictly)
def on_frontier(r):
    if not r.comparable:
        return False
    o = fr[(fr.question == r.question) & (fr.path != r.path) & fr.comparable]
    return not ((o.characters <= r.characters) & (o.share_delivered >= r.share_delivered) & ((o.characters < r.characters) | (o.share_delivered > r.share_delivered))).any()
fr["on_frontier"] = fr.apply(on_frontier, axis=1)
# standard-compliant answer (estimate): the warehouse discovery call + a compliant data response with placeholders
# filled at typical lengths (metadata_standard_example.py); delivers every applicable element by construction
import json
FILLED = {k: v["filled"] for k, v in json.loads((OUT / "metadata_standard_example_sizes.json").read_text()).items()}  # from metadata_standard_example.py
DISC = {"U5MR": "D01_yves_find_u5mr.json", "DTP3": "D05_yves_find_dtp3.json"}
for q in ("U5MR", "DTP3"):
    n_app = int(fr[(fr.question == q)].applicable.iloc[0])
    fr.loc[len(fr)] = dict(path=f"Standard-compliant answer, estimated ({q})", question=q, server="compliant", calls=2,
                           characters=ch[DISC[q]] + FILLED[q], applicable=n_app, meets=n_app, partial=0, points=float(n_app),
                           share_delivered=100.0, files=DISC[q] + ";metadata_standard_example_" + q.lower() + "_nga.json (filled)",
                           comparable=True, on_frontier=False)
fr.to_csv(OUT / "metadata_standard_frontier.csv", index=False)
cheap = fr[fr.comparable & (fr.server != "compliant")].sort_values("characters").groupby("question").first()
for q in ("U5MR", "DTP3"):
    c = fr[(fr.question == q) & (fr.server == "compliant")].characters.iloc[0]
    print(f"{q}: compliant {c:,} vs cheapest measured {cheap.loc[q].characters:,} ({cheap.loc[q].path}, {cheap.loc[q].share_delivered}%): {100 * (c / cheap.loc[q].characters - 1):+.1f}%")
pd.set_option("display.width", 220); pd.set_option("display.max_colwidth", 60)
print(fr[["path", "calls", "characters", "applicable", "meets", "partial", "share_delivered", "comparable", "on_frontier"]].to_string(index=False))
