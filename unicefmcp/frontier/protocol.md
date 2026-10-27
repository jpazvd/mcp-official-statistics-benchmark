# Cost-frontier benchmark across sectors and countries — protocol (fixed before any call, 27 October 2026)

## Question
Does the efficiency frontier measured on two questions (Nigeria U5MR and DTP3) hold across sectors, breakdown
richness and countries? Unit of analysis: one question = one series × one country × 2000–2025, answered on one server.

## Sample (`sample.csv`, `analysis/frontier_sample.py`, seed 20261027)
- Frame: UN DC UNICEF codes whose series maps to a warehouse series with Nigerian data (210 codes).
- Strata: UN DC's 17 UNICEF sector groups × breakdown richness (codes ranked by number of UN DC variables, split
  into lower and upper halves). One code per stratum: 34 series.
- Series: the code's representative UN DC variable if matched for Nigeria, else its matched variable with most
  Nigerian observations; warehouse series = the matched one, with DATA_SOURCE and any dimension that varies across
  matched rows left open.
- Countries: Nigeria for all 34; Brazil and Somalia (data-sparse) for 12 drawn series → 58 questions per server.
- Data360: the 14 series with a Data360 counterpart judged the same series in the earlier direct join → 20 questions.

## Paths (one canonical path per server, scripted)
| Server | Discovery | Structure | Data | Metadata (once per series) |
|---|---|---|---|---|
| UNICEF SDMX MCP | `find_indicator_candidates(q1)` | `list_dimensions(flow)` (once per flow) | `query_data(flow, key, 2000–2025, csv, labels=id)` | — |
| UN DC | `search_indicators(q1, places=[country], per_search_limit=10)` | — | `get_observations(dcid, country, all)` | `get_variable_metadata(dcid)` |
| Data360 | `data360_search_indicators(q1)` | — | `data360_get_data(db, id, country, 2000–2025, limit 100)` | `data360_get_metadata(db, id)` |

- q1 = the warehouse codelist name (the custodian's name); if the target identifier is absent from the discovery
  response, one retry with q2 = the UN DC variable name. Discovery success, rank and retries are recorded; the data
  call always uses the target identifier (oracle fallback), so retrieval cost is measured even when discovery fails.
- Every call is counted as executed, failures included. UN DC's one-off playbook read is excluded.

## Measures
- Characters of every response, measured exactly from the agent transcripts (not self-reported); every response is
  saved verbatim to `raw/`. Cost of a question = discovery + structure (per flow) + data; the metadata call is
  reported as an option, as in the doc.
- Share of the standard delivered, scored automatically (`analysis/frontier_score.py`; the rules reproduce the
  hand scores of all 10 pilot paths element by element). O2, O4 and O5 apply when the warehouse publishes a
  reference period/survey source, bounds or notes for that series and country.
- Answered or not; observations returned; latest year; agreement of values with the warehouse (within 1%).

## Analysis
Frontier per sector and per country; median and spread of characters and share by server; how characters scale with
the number of UN DC variables for the code and with observations returned; sensitivity: answered questions only,
and with the metadata call.
