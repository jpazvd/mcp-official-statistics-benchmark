# Replication of "Metadata, cost and accuracy of official statistics served to AI agents: evidence from three MCP servers"
#
#   make all       rebuild every analysis output, the paper's numbers, tables and figures, and paper/paper.pdf
#   make analysis  rerun the analysis scripts on the saved server responses and agent transcripts
#   make assets    regenerate paper/generated/*.tex and paper/figures/*
#   make paper     compile paper/paper.pdf
#   make check     rebuild everything, then fail if any committed output changed (the replication test)
#   make clean     remove LaTeX build files
#
# Nothing here calls a live server: collection is documented in collection/README.md.

PY ?= python3 -I
A  := analysis

# Fixed build date, so rebuilt PDFs (paper and figures) are byte-identical rather than differing only in their
# embedded timestamps. matplotlib and pdfTeX both read SOURCE_DATE_EPOCH; 1793059200 = 2026-10-27 00:00 UTC.
export SOURCE_DATE_EPOCH := 1793059200
export FORCE_SOURCE_DATE := 1

# order matters: each step reads what the previous ones wrote
ROUND1   := compare metadata_compare
UNIVERSE := unicef_compare unicef_ihme_map
WAREHOUSE:= unicef_mcp_compare unicef_mcp_universe d360_vs_dw four_platform_tables four_platform_crosswalk
STANDARD := d360_same_window_raw metadata_standard_example metadata_standard_scoring
FRONTIER := frontier_sample frontier_score frontier_extract frontier_analyse frontier_summary
MODELS   := models_extract models_analyse models_summary
STEPS    := $(ROUND1) $(UNIVERSE) $(WAREHOUSE) $(STANDARD) $(FRONTIER) $(MODELS)

.PHONY: all analysis assets paper check clean

all: analysis assets paper

analysis:
	@set -e; for s in $(STEPS); do echo "== $$s"; $(PY) $(A)/$$s.py > /dev/null; done
	@$(PY) $(A)/models_analyse.py > unicefmcp/models/analysis_output.txt

assets:
	$(PY) paper/code/assets.py

paper:
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error paper.tex > /dev/null && echo "paper/paper.pdf built"

check: all
	@git diff --quiet -- . ':(exclude)paper/paper.pdf' ':(exclude)paper/figures/*.pdf' ':(exclude)paper/figures/*.png' \
	  && echo "OK: every committed output was reproduced exactly" \
	  || (git --no-pager diff --stat -- . ':(exclude)paper/paper.pdf' ':(exclude)paper/figures/*.pdf' ':(exclude)paper/figures/*.png'; \
	      echo "Some outputs differ from the committed versions"; exit 1)

clean:
	cd paper && latexmk -C > /dev/null; rm -f paper/*.bbl paper/*.run.xml
