# Brief: UNICEF SDMX MCP catalogue and series extraction (one group of dataflows)

You are extracting the catalogue and observations of a group of SDMX dataflows from the "Unicef_MCP_Yves" MCP server (sdmx-mcp 1.2.214, backend https://sdmx.data.unicef.org). Write exactly what the tools return; never invent codes or values.

## Setup
1. ONE ToolSearch call: query "select:mcp__Unicef_MCP_Yves__list_dimensions,mcp__Unicef_MCP_Yves__get_flow_structure,mcp__Unicef_MCP_Yves__query_data,mcp__Unicef_MCP_Yves__describe_flow", max_results 4.
2. Your flow list is the block for your group in /home/claude/unicefmcp/flows.txt (lines between your GROUP_X header and the next GROUP header or end of file).
3. Work in /home/claude/unicefmcp/<group>/ (create it). Keep raw tool outputs there. Large tool results are not shown to you inline: the harness saves them to a file under /root/.claude/projects/.../tool-results/ and tells you the path — copy that file into your raw folder immediately (cp), then parse it with `python3 -I` scripts kept in /home/claude/unicefmcp/<group>/scripts/. Never try to read a 1 MB JSON with the Read tool.

## Per flow, in this order
A. list_dimensions(flowRef) → ordered dimension ids and codelist URNs.
B. get_flow_structure(flowRef) → large JSON (≈1.3 MB; it will be persisted to a file). From it extract:
   - dataflow id, name, description, version, isFinal, structure URN;
   - the DSD attribute list (id, assignmentStatus, relationship) and primary measure;
   - the CL_UNICEF_INDICATOR codelist (every code: id, name, description, parent) — write/append to codelist_indicator_<group>.csv, de-duplicated on id, with first_flow_seen; also the codelist's version;
   - CL_UNIT_MEASURE and CL_OBS_STATUS codes (id, name) once per group into unit_codelist_<group>.csv and obs_status_codelist_<group>.csv.
C. Inventory call: query_data(flowRef, key=K_INV, lastNObservations=1, allowUnboundedTime=true, format="csv", labels="id", maxObs=100000) where K_INV = "NGA+IND+BRA" followed by one "." for every remaining dimension (all wildcard). Example for 4 dimensions: "NGA+IND+BRA...". If the flow's REF_AREA codelist is subnational (CME_SUBNATIONAL, PT_CM_SUBNATIONAL, WASH_HOUSEHOLD_SUBNAT) the call may return nothing — record that and also try key with the first dimension wildcard ("...." all wildcard) with lastNObservations=1 and maxObs=2000 to capture what REF_AREA codes exist.
   From raw_csv (persisted to a file if large) write inventory_<group>.csv: one row per (flowRef, INDICATOR, REF_AREA) with: n_series, dimension_values (JSON: for each non-REF_AREA/INDICATOR dimension the set of codes seen, truncated to 12), latest_time_period, data_sources (set), unit_measure (set), share_with_lower_bound, obs_status (set), has_country_notes, example_value.
   If the response reports an error (e.g. too many observations, HTTP 4xx) log it and retry once with maxObs=100000 and key restricted to one country at a time ("NGA....", "IND....", "BRA....") and merge.
D. Series call (totals): query_data(flowRef, key=K_TOT, startPeriod="2000", endPeriod="2025", format="csv", labels="id", maxObs=100000) where K_TOT = "NGA+IND+BRA" then "." then for each remaining dimension: "" (wildcard) for INDICATOR and AGE, "_T" for every other dimension (SEX, WEALTH_QUINTILE, RESIDENCE, MATERNAL_EDU_LVL, HEAD_OF_HOUSE, and any other breakdown dimension) — i.e. totals on every breakdown except age, which stays wildcard. If a dimension's name suggests it is not a breakdown (e.g. VACCINE, WASH_SERVICE, UNIT, FREQ, TIME_PERIOD_METHOD, VALUE_TYPE) leave it wildcard too, and say so in the log. If the call errors because the key is too long or returns zero rows while the inventory had data, fall back to all-wildcard with startPeriod 2000 per country, and log it.
   Append every row verbatim to series_<group>.csv with columns:
   flowRef,indicator,iso3,dims_json,time_period,value,lower_bound,upper_bound,obs_status,data_source,unit_measure,ref_period,country_notes_flag,extra_attrs_json
   (dims_json = the non-REF_AREA/INDICATOR/TIME_PERIOD dimension codes of the row as compact JSON; value and bounds as the exact strings; country_notes_flag = 1 when COUNTRY_NOTES is non-empty; extra_attrs_json = any other attribute columns present in that flow's CSV, as compact JSON.)
   Use the csv module; append after each flow so nothing is lost.
E. Log every call in log_<group>.md: flow, key used, status, rows returned, file persisted (yes/no), errors, anomalies (e.g. dimensions whose total is not "_T", indicators with no total series, attribute columns that differ between flows, REF_AREA codes that are not ISO3).

## Output files (all under /home/claude/unicefmcp/<group>/)
flows_<group>.csv (flowRef, agency, id, name, description, version, isFinal, dimensions_ordered, attributes, measure, inventory_status, n_rows_inventory, n_rows_series, notes)
codelist_indicator_<group>.csv, unit_codelist_<group>.csv, obs_status_codelist_<group>.csv, inventory_<group>.csv, series_<group>.csv, log_<group>.md

Final message to me (max 12 lines): flows processed, rows per output file, flows with no data for the three countries, dimensions whose total code is not _T, anomalies. Do not paste the data.
