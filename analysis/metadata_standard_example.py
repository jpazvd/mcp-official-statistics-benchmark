"""
Builds a response that meets the minimum metadata standard for Nigeria's under-five mortality rate (2000-2024),
from the warehouse values extracted on 27 October 2026, and measures its size against the measured responses.
Values, bounds, codes, definition, unit and query come from the warehouse; fields the warehouse does not publish
are left as <placeholders> rather than invented.
Outputs: ../unicefmcp/out/metadata_standard_example_u5mr_nga.json (full, compact), _abridged.json (3 observations, indented),
         metadata_standard_example_dtp3_nga.json, and metadata_standard_example_sizes.json (characters, and characters once
         the six placeholders are filled at typical lengths)
Run    : python3 -I metadata_standard_example.py
"""
import json
import pandas as pd
from pathlib import Path
M = Path(__file__).resolve().parent.parent / "unicefmcp"
s = pd.read_csv(M / "series_all.csv", dtype=str, keep_default_na=False)
d = s[(s.flowRef == "UNICEF/CME/1.0") & (s.indicator == "CME_MRY0T4") & (s.iso3 == "NGA")].copy()
d["dims"] = d.dims_json.map(json.loads)
d = d[d.dims.map(lambda x: x.get("SEX") == "_T" and x.get("WEALTH_QUINTILE") == "_T")].sort_values("time_period")
assert len(d) == 25, len(d)

def response(rows):
    return {
     "response": {
      "query": "https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/data/UNICEF,CME,1.0/NGA.CME_MRY0T4._T._T?startPeriod=2000&endPeriod=2025&format=csv&labels=id",
      "server": "<server name and version>", "retrieved": "<UTC timestamp>",
      "applied_defaults": {}, "truncated": False},
     "series": [{
      "id": {"custodian_code": "CME_MRY0T4", "server_id": "UNICEF/CME/1.0:NGA.CME_MRY0T4._T._T", "sdg_series": "SH_DYN_MORT"},
      "name": "Under-five mortality rate",
      "definition": "Probability of dying between birth and exactly 5 years of age, expressed per 1,000 live births",
      "methodology": "https://childmortality.org/",
      "unit": {"code": "D_PER_1000_B", "label": "Deaths per 1,000 live births", "multiplier": 0},
      "breakdown": {"REF_AREA": ["NGA", "Nigeria"], "SEX": ["_T", "Total"], "WEALTH_QUINTILE": ["_T", "Total"]},
      "custodian": "UN Inter-agency Group for Child Mortality Estimation (UN IGME)",
      "provenance": ["UN IGME", "UNICEF Data Warehouse, UNICEF/CME/1.0"],
      "release": {"name": "UN IGME, Levels and Trends in Child Mortality, Report 2025", "date": "<release date>", "ingested": "<date>", "status": "current"},
      "licence": "<licence URL>", "citation": "<recommended citation: custodian, release, access date>",
      "observation_defaults": {"interval": "90% uncertainty interval", "source": "UN IGME model", "nature": "MD (modelled)"}}],
     "observations": {
      "columns": ["time_period", "value", "lower", "upper"],
      "rows": [[r.time_period, float(r.value), float(r.lower_bound), float(r.upper_bound)] for r in rows.itertuples(index=False)]}}

full = json.dumps(response(d), separators=(",", ":"), ensure_ascii=False)
(M / "out" / "metadata_standard_example_u5mr_nga.json").write_text(full, encoding="utf-8")
abr = json.dumps(response(d.tail(3)), indent=1, ensure_ascii=False)
abr2 = json.dumps(response(d.tail(3)), ensure_ascii=False, indent=None, separators=(", ", ": "))
(M / "out" / "metadata_standard_example_u5mr_nga_abridged.json").write_text(abr, encoding="utf-8")
hdr = json.dumps({k: v for k, v in response(d.head(0)).items()}, separators=(",", ":"), ensure_ascii=False)
print("compliant response, 25 observations:", len(full), "characters; header with no rows:", len(hdr), "; per observation:", round((len(full) - len(hdr)) / 25, 1))
print("measured, same 25 years: warehouse query_data 3,790 | Data360 get_data 5,601 (B02b) | UN DC get_observations 1,377 (no metadata)")
print(abr)

# ---------------------------------------------------------------- DTP3 (WUENIC): same construction, no bounds published
t = s[(s.flowRef == "UNICEF/IMMUNISATION/1.0") & (s.indicator == "IM_DTP3") & (s.iso3 == "NGA")].sort_values("time_period")
t = t.drop_duplicates("time_period")
src = sorted(set(t.data_source))
def response_dtp3(rows):
    return {
     "response": {"query": "https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/data/UNICEF,IMMUNISATION,1.0/NGA.IM_DTP3..?startPeriod=2000&endPeriod=2025&format=csv&labels=id",
                  "server": "<server name and version>", "retrieved": "<UTC timestamp>", "applied_defaults": {"key": "NGA.IM_DTP3.. (padded)"}, "truncated": False},
     "series": [{
      "id": {"custodian_code": "IM_DTP3", "server_id": "UNICEF/IMMUNISATION/1.0:NGA.IM_DTP3.DTP3.M12T23", "sdg_series": "SH_ACS_DTP3"},
      "name": "Percentage of surviving infants who received the third dose of DTP-containing vaccine",
      "definition": "Percentage of surviving infants who received three doses of diphtheria, pertussis and tetanus vaccine",
      "methodology": "https://data.unicef.org/topic/child-health/immunization/",
      "unit": {"code": "PCNT", "label": "%", "multiplier": 0},
      "breakdown": {"REF_AREA": ["NGA", "Nigeria"], "VACCINE": ["DTP3", "DTP3"], "AGE": ["M12T23", "12 to 23 months"]},
      "custodian": "WHO and UNICEF (WUENIC)",
      "provenance": ["WHO/UNICEF estimates of national immunization coverage", "UNICEF Data Warehouse, UNICEF/IMMUNISATION/1.0"],
      "release": {"name": src[0] if len(src) == 1 else "; ".join(src), "date": "<release date>", "ingested": "<date>", "status": "current"},
      "licence": "<licence URL>", "citation": "<recommended citation: custodian, release, access date>",
      "observation_defaults": {"source": "WUENIC estimate", "nature": "E (estimated)"}}],
     "observations": {"columns": ["time_period", "value"], "rows": [[r.time_period, float(r.value)] for r in rows.itertuples(index=False)]}}
full_d = json.dumps(response_dtp3(t), separators=(",", ":"), ensure_ascii=False)
(M / "out" / "metadata_standard_example_dtp3_nga.json").write_text(full_d, encoding="utf-8")
print("DTP3 compliant response:", len(t), "observations,", len(full_d), "characters; release label:", src)

# ---------------------------------------------------------------- size once the six placeholders are filled
# Lengths typical of each field; these are assumptions about length only, not values for the fields.
CITE = {"U5MR": "UN IGME, Levels and Trends in Child Mortality, Report 2025; UNICEF Data Warehouse, UNICEF/CME/1.0, accessed 27 October 2026",
        "DTP3": "WHO and UNICEF, WHO/UNICEF estimates of national immunization coverage, 2025 revision; UNICEF Data Warehouse, UNICEF/IMMUNISATION/1.0, accessed 27 October 2026"}
def typical(q):
    return {"<server name and version>": len("sdmx-mcp 1.2.214"),            # the server read in this benchmark
            "<UTC timestamp>": len("2026-10-27T09:39:00Z"),                  # ISO 8601, UTC
            "<release date>": len("YYYY-MM-DD"), "<date>": len("YYYY-MM-DD"),  # ISO 8601 dates
            "<licence URL>": len("https://creativecommons.org/licenses/by/4.0/"),  # a typical licence URL
            "<recommended citation: custodian, release, access date>": len(CITE[q])}
def filled_len(txt, q):
    t = typical(q); assert sum(txt.count(k) for k in t) == 6, "six placeholders expected"
    return len(txt) + sum(txt.count(k) * (v - len(k)) for k, v in t.items())
sizes = {"U5MR": {"observations": len(d), "characters": len(full), "filled": filled_len(full, "U5MR")},
         "DTP3": {"observations": len(t), "characters": len(full_d), "filled": filled_len(full_d, "DTP3")}}
(M / "out" / "metadata_standard_example_sizes.json").write_text(json.dumps(sizes, indent=1), encoding="utf-8")
print("sizes:", sizes)
