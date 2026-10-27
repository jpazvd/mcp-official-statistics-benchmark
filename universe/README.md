# UNICEF indicator universe: UN System Data Commons vs World Bank Data360 vs IHME GBD 2023
Extracted through the three MCP servers on 2026-10-26. Countries for the value comparison: Nigeria, India, Brazil; years 2000-2025.

undc_unicef_variables.csv        247 UNICEF indicator codes from the UN DC UNICEF topic, with all 3,607 variant DCIDs (dimension suffixes)
undc_unicef_representatives.csv  one representative variable per code used for the metadata pull
undc_unicef_metadata.csv         UN DC get_variable_metadata output (name, facets, provenance, unit) — 260 facet rows
undc_unicef_codes.csv            code, name, dataflow, dimensions, coverage for the five test countries
d360_match_part1.csv / part2     Data360 candidates per code (search + metadata), match_quality same/related/none, unicef_sourced
extraction_pairs.csv             the 117 same-concept pairs used for the value comparison (UN DC variant DCID, Data360 id)
values_unicef_undc_1..3.csv      UN DC observations, verbatim (3,597 observations)
values_unicef_d360_1..2.csv      Data360 observations, verbatim incl. dimension codes and literal "null" rows (4,706 observations)
metadata_unicef_d360_1..2.csv    Data360 metadata per counterpart (sources, definition, version date, licence, unit)
log_*.md                         call-by-call logs with anomalies flagged by the extraction agents
out/unicef_universe_crosswalk.csv   247 codes with Data360 match status and counterpart
out/universe_summary_by_dataflow.csv
out/agreement_by_code.csv        verdict per matched code (identical / rounding / different / no overlap), coverage and latest year
out/paired_values.csv            every joined country-year with both values and the relative difference
out/coverage_by_code_country.csv
out/unicef_ihme_mapping.csv      247 codes mapped to GBD constructs; out/ihme_mapping_summary.csv
Scripts: ../analysis/unicef_compare.py, ../analysis/unicef_ihme_map.py (python3 -I)
