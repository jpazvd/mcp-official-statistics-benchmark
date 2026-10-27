# Child, women and family indicators across three data warehouses

UN System Data Commons (UN DC) · World Bank Data360 · IHME GBD 2023 — extracted through their MCP servers on 2026-10-25.

Scope: Nigeria, Ethiopia, India, Bangladesh, Brazil; reference window 2015–2024 (IHME ends 2023 by construction).

## Folder layout

```
crosswalk.csv                 indicator concept -> platform identifiers, comparability class, notes
extract/
  values_undc_a.csv           UN DC observations, verbatim (mortality, fertility, LE, population) — 705 rows
  values_undc_b.csv           UN DC observations, verbatim (coverage, nutrition, protection)       — 645 rows
  values_wb.csv               Data360 observations, verbatim (OBS_VALUE as string; HNP "null" kept) — 1,000 rows
  values_ihme.csv             GBD 2023 estimates, verbatim full precision (fmt=csv)                 — 2,112 rows
  metadata_undc_*.csv         UN DC variable/facet/provenance metadata (get_variable_metadata)
  metadata_wb.csv             Data360 indicator metadata (get_metadata)
  metadata_ihme.csv           GBD framing notes, series_meta, uncertainty notes, methods-appendix excerpts
  log_*.md                    call-by-call logs with anomalies flagged by the extraction agents
analysis/
  compare.py                  harmonisation (units), pairwise differences, summaries, snapshot
  metadata_compare.py         one-row-per-indicator metadata side-by-side
  harmonized_long.csv         all platforms in common units (headline + alternate series)
  comparison_wide.csv         indicator x country x year: undc | wb | ihme
  pairwise_diffs.csv          undc-wb, ihme-undc, ihme-wb differences and relative differences
  summary_by_indicator.csv    agreement statistics per indicator and pair
  within_platform_alternates.csv  same concept, different source series inside one platform
  latest_year.csv             latest available year per platform, indicator, country
  snapshot_2022.csv           2022 values side by side (nearest year 2018-2024 when 2022 missing)
  ihme_growth_failure_2022.csv  GBD stunting/wasting exposure categories by age band (not summed)
  metadata_comparison.csv     provenance, vintage, units, uncertainty, agreement — three platforms
```

## Harmonisation rules (compare.py)

- IHME proportions x100 to percent (coverage covariates); stillbirth proportion x1000; ASFR 15-19 x1000; anaemia per 100,000 ÷ 1,000.
- IHME "both sexes" rows used, except women-only measures (MMR, anaemia, TFR, ASFR, contraception) which GBD publishes for females only.
- Relative difference = 100 x (a − b) / mean(a, b).
- UN DC `PT_MRD_U18.SEX--F` is a count and is excluded from the rate comparison.
- GBD growth-failure, breastfeeding, IPV and high-BMI exposures are kept as published categories (never summed) and compared qualitatively.

Re-run: `python3 -I analysis/compare.py && python3 -I analysis/metadata_compare.py`
