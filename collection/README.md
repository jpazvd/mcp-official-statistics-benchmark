# How the data were collected

All data were collected through public MCP servers by Claude agents (Claude Code subagents). Each agent worked from a written brief or prompt, and every call it made was logged. No value was typed by hand. The servers and their versions:

| Server | MCP name in the logs | Version / backend |
|---|---|---|
| UNICEF SDMX data warehouse | `Unicef_MCP_Yves` | sdmx-mcp 1.2.214, backend `https://sdmx.data.unicef.org/ws/public/sdmxapi/rest` |
| UN System Data Commons | `UN_System_Data_Commons` | public endpoint, accessed 25–27 October 2026 |
| World Bank Data360 | `World_Bank_Data360` | public endpoint; WDI version date 2026-07-01 |
| IHME GBD 2023 (round 1 only) | `IHME_GBD` | GBD 2023 |

## Stages, in the order they were run

| # | Date | Stage | Brief, protocol or prompt | Logs and raw output | Scripts that consume it |
|---|---|---|---|---|---|
| 1 | 25 Oct | First-round comparison: UN DC, Data360 and IHME, five countries | `docs/round1_three_platform_comparison.md` | `extract/log_*.md`, `extract/*.csv` | `analysis/compare.py`, `metadata_compare.py` |
| 2 | 26 Oct | UNICEF universe: all 247 UNICEF codes in UN DC, matched to Data360 | `universe/README.md` | `universe/log_*.md`, `universe/values_*.csv`, `metadata_*.csv` | `analysis/unicef_compare.py`, `unicef_ihme_map.py` |
| 3 | 27 Oct | Warehouse extraction: 41 dataflows in three groups, Nigeria, India, Brazil | `unicefmcp/AGENT_BRIEF.md`, `unicefmcp/flows.txt` | `unicefmcp/group_*/log_*.md`, `raw.tar.gz`, `scripts/` | `analysis/unicef_mcp_compare.py`, `unicef_mcp_universe.py`, `d360_vs_dw.py`, `four_platform_*.py` |
| 4 | 27 Oct | Pilot cost benchmark: two questions on each server | `unicefmcp/cost/log.md` | `unicefmcp/cost/raw/` (A = UN DC, B = Data360, C = IHME, D = warehouse, E = metadata calls), `calls.csv` | `analysis/d360_same_window_raw.py`, `metadata_standard_*.py` |
| 5 | 27 Oct | Sector and country benchmark: 34 series, 3 countries, fixed paths | `unicefmcp/frontier/protocol.md` (written before the first call), `sample.csv`, `spec_*.csv` | agent work lists `agent_*.csv`, `transcripts/`, `raw/`, `calls.csv` | `analysis/frontier_*.py` |
| 6 | 27 Oct | Model and effort benchmark: 4 series × 3 servers × 8 runs | `unicefmcp/models/prompt_template.txt`, `prompt_Q*_*.txt`, `questions.csv` | `runs.csv`, `transcripts/` | `analysis/models_*.py` |

## Notes on the raw material

- **Transcripts.** Agent session transcripts in `frontier/transcripts/` and `models/transcripts/` are slimmed to what the analysis needs: the role, model and per-request usage of each message, every tool call with its arguments, and every tool result as text. The harness's own system prompt is removed.
- **Oversized results.** Results too large for the client were saved to a file by the harness. Those files are kept beside the transcripts under their original names, and the extraction scripts read them from there.
- **Usage counting.** Usage is reported once per API response, but a transcript repeats it on each content block of that response. `models_extract.py` counts each message identifier once.
- **Pilot re-run.** The pilot's Data360 data calls were first made for 1960–2024 and 1980–2024. They were re-run for 2000–2025, and the re-run responses are rebuilt field by field by `d360_same_window_raw.py` (`B02b`, `B04b`). Both versions are kept, and the first is flagged as not comparable.
- **Failed calls.** In the sector benchmark, the first UN DC metadata calls (agents `un1`–`un3`) failed, because the work list omitted the required `entity_dcids`. They were re-run as agent `un4`; the failed calls are kept in `calls.csv` but excluded from costs.
- **Fable.** Claude Fable 5.1 sessions were attempted for the model benchmark. All twelve were refused with "out of usage credits" (HTTP 429) and are not registered.

## Rerunning a stage

1. Give an agent the same brief or prompt, with access to the one server it names.
2. Save every tool response verbatim, or save the session transcript in the slimmed form above.
3. For the model benchmark, record each session with
   `python3 -I unicefmcp/models/register.py <config> <model> <effort> <repeat> <12 agent ids>`.
   The 12 ids go in the order Q1 wh, un, wb, Q2 wh, …, Q4 wb.
4. Run `make all`. The analysis, tables, figures and paper will reflect the new collection; `make check` will then show what changed.
