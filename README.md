# Metadata, cost and accuracy of official statistics served to AI agents

Replication package for the working paper *Metadata, cost and accuracy of official statistics served to AI agents: evidence from three MCP servers* (João Pedro Azevedo, UNICEF, 27 October 2026).

The paper proposes a minimum metadata standard of fifteen elements for Model Context Protocol (MCP) servers that republish official statistics. It scores three public servers against the standard: the UNICEF SDMX data warehouse MCP, the UN System Data Commons and World Bank Data360. It then measures what answering a question costs on each server in three benchmarks:

| Benchmark | Scale | What it measures |
|---|---|---|
| Pilot | 2 series × 13 answer paths | characters and share of the standard; the efficiency frontier |
| Sector and country | 34 series in 17 sectors; Nigeria, Brazil, Somalia; 140 answers, 325 calls | cost by component; discovery; agreement with the warehouse |
| Model and effort | 4 series × 3 servers × 8 runs (Claude Haiku, Sonnet and Opus at several effort levels); 96 agent sessions | tokens sent and received, accuracy, grounding, stability |

## Replicate in three commands

```bash
pip install -r requirements.txt   # Python 3.13; pandas, numpy, matplotlib
make all                          # analysis -> paper numbers, tables and figures -> paper/paper.pdf
make check                        # same, then fails if any committed output changed
```

`make all` takes about a minute and needs no network access. It needs a LaTeX distribution with `latexmk`, `natbib`, `booktabs`, `tabularx` and `enumitem` for the final step. `make check` is the replication test. It rebuilds everything from the saved server responses and agent transcripts, then compares the result with the committed outputs using `git diff`. On the reference machine every output, from the first CSV to the paper's macros and tables, is reproduced byte for byte. The PDF and the images are excluded from the comparison, because they embed build timestamps.

## How a number gets into the paper

```
saved server responses and agent transcripts      (unicefmcp/cost/raw, frontier/raw + transcripts, models/transcripts, universe/, extract/)
        │  analysis/*.py                           (run in the order listed in the Makefile)
        ▼
analysis outputs                                   (unicefmcp/out/*.csv, frontier/questions.csv + summary.json, models/run_results.csv + summary.json)
        │  paper/code/assets.py
        ▼
paper/generated/numbers.tex (130 macros), tab*.tex, paper/figures/fig*.pdf
        │  latexmk
        ▼
paper/paper.pdf
```

The paper's text, tables and figures take every result from the generated files, so no result is typed by hand. To trace a number, find its macro in `paper/paper.tex` (for example `\unCheaper`), then its definition in `paper/code/assets.py`. That definition reads a field of `unicefmcp/frontier/summary.json` or `unicefmcp/models/summary.json`, and the field is computed in `analysis/frontier_summary.py` or `analysis/models_summary.py`.

## Repository layout

| Path | Content |
|---|---|
| `paper/` | `paper.tex`, `references.bib`, `code/assets.py`, generated macros and tables, figures, the built `paper.pdf` |
| `analysis/` | every analysis script (Python, run with `python3 -I`); each script's docstring states its inputs and outputs |
| `unicefmcp/` | the UNICEF SDMX warehouse extraction and the three benchmarks (see below) |
| `unicefmcp/out/` | the four-platform comparison and metadata-standard outputs: compliance matrix, standard elements, pilot frontier, example compliant responses |
| `unicefmcp/cost/` | pilot: every response in `raw/`, plus `calls.csv` and `log.md` |
| `unicefmcp/frontier/` | sector and country benchmark: the pre-registered `protocol.md` and `sample.csv` (seed 20261027), call specifications `spec_*.csv`, agent work lists `agent_*.csv`, session transcripts in `transcripts/`, every response in `raw/`, `calls.csv`, `questions.csv`, `summary.json` |
| `unicefmcp/models/` | model and effort benchmark: `questions.csv`, the prompts, `reference_nga.json`, the run register `runs.csv`, the 96 session transcripts in `transcripts/`, parsed `answers/`, `run_results.csv`, `mcp_calls.csv`, summaries |
| `unicefmcp/series_all.csv`, `inventory_all.csv`, `flows_all.csv`, `codelist_unicef_indicator.csv`, `supplement/` | the warehouse extraction: 84,442 national observations from 41 dataflows for Nigeria, India and Brazil, 2000–2025 |
| `unicefmcp/group_[abc]/` | the extraction by dataflow group: logs, scripts and tables, with the verbatim tool output compressed in `raw.tar.gz` (and `work.tar.gz` for group A) |
| `universe/` | the UN DC and Data360 extractions for the 247 UNICEF codes: values, metadata, matches and logs |
| `extract/`, `crosswalk.csv` | the first-round comparison (UN DC, Data360, IHME; five countries), which the standard's evidence also draws on |
| `collection/README.md` | how every dataset was collected, by whom (which agent and brief) and with which server versions |
| `docs/` | the READMEs of the earlier comparison packages |

## What is and is not reproducible

**Analysis (fully reproducible).** Every result in the paper is recomputed by `make all` from data saved in this repository: the verbatim server responses, the slimmed agent transcripts, the per-request token usage reported by the API, and the agents' final answers.

**Collection (documented, not re-executable bit for bit).** The data were collected on 25–27 October 2026 through the public MCP servers, by Claude agents following the briefs and prompts saved here. The servers change over time, and agents are not deterministic, so a new collection will differ. `collection/README.md` describes how to rerun each stage. For the model benchmark: run the prompts, register the sessions with `unicefmcp/models/register.py`, save the transcripts, and rerun `make all`.

## Known limitations

These are discussed in Sections 4.5 and 8 of the paper:
- **Panel size.** The agentic panel has four series for one country, and the repeat covers one setting only.
- **Reference.** The warehouse is both a server under test and the accuracy reference.
- **Client baseline.** The baseline of about 97,000 tokens per request belongs to the agent harness used.
- **Fable.** Claude Fable 5.1 could not be run, because the account had no usage credits for it.
- **Supplement.** `supplement/build_supplement.py` expects verbatim responses in `supplement/raw/`, which were not retained, so `series_supplement.csv` is provided as extracted.

## Citation

See `CITATION.cff`.
