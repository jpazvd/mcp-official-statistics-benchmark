# UNICEF SDMX warehouse (via the sdmx-mcp server) as the fourth platform

Extraction date: 27 October 2026. Server: `Unicef_MCP_Yves` = sdmx-mcp 1.2.214, backend `https://sdmx.data.unicef.org/ws/public/sdmxapi/rest`
(agencies UNICEF and UNPD, draft flows excluded). Countries: NGA, IND, BRA. Period: 2000–2025.

## Files
| Path | Content |
| --- | --- |
| `flows.txt`, `AGENT_BRIEF.md` | the 41 dataflows split into three extraction groups and the brief given to each extraction agent |
| `flows_all.csv` | one row per dataflow: name, description, version, isFinal, ordered dimensions, attributes, primary measure |
| `codelist_unicef_indicator.csv` | CL_UNICEF_INDICATOR v1.0: 803 codes, 476 with descriptions |
| `group_a|b|c/` | per-group outputs: `flows_*.csv`, `codelist_indicator_*.csv`, `unit_codelist_*.csv`, `obs_status_codelist_*.csv`, `inventory_*.csv`, `series_*.csv`, `log_*.md` (every call, key, status, rows), `raw/` (verbatim tool output), `scripts/` |
| `inventory_all.csv` | one row per (flow, indicator, country): series count, dimension codes seen, latest year, sources, units, share with bounds, status codes, country notes (4,998 rows) |
| `series_all.csv` | every national-total observation returned (84,442 rows): flowRef, indicator, iso3, dims_json, time_period, value, lower/upper bound, obs_status, data_source, unit_measure, ref_period, country_notes_flag, extra_attrs_json (UNIT_MULTIPLIER, footnotes, SOURCE_LINK, COVERAGE_TIME…) |
| `supplement/` | targeted breakdown pulls (2,537 rows) needed to match UN DC variants that carry a sex, marital-status, residence, wealth-quintile, statistical-population or disability breakdown; `build_supplement.py` rebuilds `series_supplement.csv` from `raw/` |
| `cost/` | the standard-query benchmark: `calls.csv` (19 calls on four servers, characters and observations per call), `log.md`, `raw/` (every response); for the metadata standard, `raw/E01`–`E04` (the UN DC and Data360 metadata calls for U5MR and DTP3) and `raw/B02b`, `B04b` (the Data360 data calls re-run for 2000–2025) |
| `out/` | all comparison outputs (below) |

## Outputs (`out/`)
| File | Content |
| --- | --- |
| `undc_vs_mcp_paired.csv` | every UN DC observation (3 countries) with the warehouse row it matched, dimension codes, source, status, bounds, unit multiplier, relative differences |
| `undc_vs_mcp_by_variable.csv` | one row per UN DC variable: warehouse code, match rule, shares identical, verdict, documented reason, vintage lag, historical revisions, label notes |
| `undc_vs_mcp_summary.csv`, `undc_vs_mcp_vintage.csv` | headline counts; latest year per code and country on both platforms |
| `d360_vs_mcp_paired.csv`, `d360_vs_mcp_by_indicator.csv` | Data360 values against the warehouse through the UN DC join |
| `d360_vs_dw_paired.csv`, `d360_vs_dw_by_indicator.csv`, `d360_vs_dw_summary.csv` | Data360 joined directly to the warehouse series (all years): verdicts, lags, revisions |
| `universe_dw_vs_undc_by_code.csv`, `universe_dw_summary.csv`, `universe_dw_by_flow.csv`, `universe_dw_codes_not_in_undc_by_flow.csv` | the 247 UN DC codes classified against the warehouse (verbatim / re-coded / codelist only / absent) and the warehouse codes UN DC lacks |
| `metadata_four_platforms.csv`, `dw_attribute_coverage_by_flow.csv` | the four-platform metadata matrix and the warehouse attribute fill rates per flow |
| `cost_standard_query.csv`, `cost_bulk_extraction.csv`, `cost_bulk_extraction_totals.csv` | call/character cost of the standard queries and subagent tokens per observation in bulk extraction |
| `crosswalk_four_platforms_long.csv`, `crosswalk_dw_agreement.csv`, `crosswalk_dw_latest.csv` | the round-1 crosswalk concepts with the warehouse as fourth platform (agreement and latest year) |
| `metadata_standard_elements.csv`, `metadata_standard_compliance.csv` | the minimum metadata standard (15 elements) and each server's status per element, with the evidence |
| `metadata_standard_frontier.csv` | cost and coverage of each way of answering two questions (Nigeria U5MR and DTP3, 2000–2025): calls, characters, applicable elements, share delivered, frontier flag; Data360's first runs kept and flagged |
| `metadata_standard_example_u5mr_nga.json`, `_abridged.json`, `metadata_standard_example_dtp3_nga.json`, `metadata_standard_example_sizes.json` | standard-compliant responses built from the warehouse values, unpublished fields left as placeholders; their size, and their size once the placeholders are filled at typical lengths |

## Rebuild
```
cd analysis
python3 -I unicef_mcp_compare.py      # UN DC and Data360 vs warehouse (uses undc_dw_crosswalk.py)
python3 -I unicef_mcp_universe.py     # universe classification
python3 -I d360_vs_dw.py              # Data360 joined directly to the warehouse
python3 -I four_platform_tables.py    # metadata matrix, cost tables
python3 -I four_platform_crosswalk.py # round-1 concepts with the warehouse
python3 -I d360_same_window_raw.py    # Data360 data calls re-run for 2000-2025 (writes cost/raw/B02b, B04b)
python3 -I metadata_standard_example.py  # compliant example responses
python3 -I metadata_standard_scoring.py  # standard, compliance matrix, efficiency frontier
```
Known server behaviour recorded in the logs: `get_flow_structure` returns ~1.3 MB per flow; `query_data` keys must carry exactly one segment per dimension
(the error names the order) and a leading wildcard REF_AREA with later non-empty segments is rewritten (use `filters`); `get_time_series` needs every
dimension fixed and drops bounds in compact mode; PT_CONFLICT returns HTTP 404 for every key; subnational flows need REF_AREA_PARENT filters.

## Sector and country benchmark (`frontier/`)
Pre-registered in `frontier/protocol.md`: 34 series drawn at random (seed 20261027) across UN DC's 17 UNICEF sectors, asked for Nigeria and 12 of them for Brazil and Somalia, on the warehouse MCP, UN DC and (14 series) Data360. `sample.csv` and `spec_*.csv` give every scripted call; `agent_*.csv` the work lists the call agents executed; `calls.csv` every call with its exact character count, measured from the agents' session transcripts, and `raw/` every response verbatim; `questions.csv` one row per question and server (cost by component, discovery, answered, latest year, agreement with the warehouse, element-by-element score); `frontier_points.csv` the chart data; `sector_table.md` the sector medians.
```
cd analysis
python3 -I frontier_sample.py    # sample and call specifications
python3 -I frontier_score.py     # validates the automated scoring against the 10 hand-scored pilot paths
python3 -I frontier_extract.py   # calls.csv and raw/ from the agent transcripts (needs the session transcripts)
python3 -I frontier_analyse.py   # questions.csv
```
The first UN DC metadata calls (agents un1–un3) failed because the work list omitted the required `entity_dcids`; they were rerun as `agent_un4.csv` and the failed calls are excluded from costs.

## Model and effort benchmark (`models/`)
Agents, not scripts, answered four questions for Nigeria, 2000–2025, on each of the three servers: under-five mortality, the maternal mortality ratio, at least basic drinking water, and four or more antenatal care visits. All three servers hold these series, and their values match the warehouse. Eight runs were made: Haiku 5.5 at medium effort; Sonnet 5.5 and Opus 5.5 at low, medium and high effort; and Opus at medium effort a second time. That is 96 sessions. Claude Fable 5.1 was attempted, but all 12 of its sessions failed with "out of usage credits" (HTTP 429), so it is not in the results.
- `questions.csv`, `prompt_template.txt` and `prompt_Q*_{wh,un,wb}.txt` hold the exact prompts. Each agent may use one server only, and must answer in a fixed JSON form with null for anything the server did not give.
- `reference_nga.json` holds the warehouse values, which are the reference.
- `runs.csv` holds the run register (setting, question, server, agent id), and `register.py` appends to it.
- `transcripts/` holds each session slimmed to its messages, the usage the API reported per request, and every tool call and response. It also holds the one oversized response the client refused, which was 1.3 million characters.
- `run_results.csv` has one row per session, with:
  - tokens: sent (cached, baseline, growth, tool-definition tokens and their re-sends), received and thinking;
  - MCP calls and characters, in total and in context;
  - the answer: years reported and correct against the reference, values grounded in the server's responses, and metadata fields reported and grounded.
- `mcp_calls.csv` has every call with its character count, a hash of the response, and a hash that ignores JSON key order.
- `answers/` holds the parsed answers.
- `summary_config.csv`, `summary_server.csv`, `choices.csv` and `determinism.csv` are the summaries; the full printout is in `analysis_output.txt`.
```
cd analysis
python3 -I models_extract.py   # run_results.csv, mcp_calls.csv, answers/ from models/transcripts
python3 -I models_analyse.py   # summaries
```
Tokens are counted once per API response. A transcript writes one line per content block and repeats the usage on each line, so lines are deduplicated by message id. To rerun with other models, run the prompts through any agent client, record the session ids in `runs.csv` with `register.py`, save the transcripts in the same slim form, and rerun the two scripts.
