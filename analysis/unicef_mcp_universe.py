"""
Indicator universe: UNICEF SDMX warehouse (via MCP) vs the 247 UNICEF codes in UN DC (and Data360 / IHME classes from round 2).
Inputs : ../unicefmcp/inventory_all.csv, codelist_unicef_indicator.csv, flows_all.csv, out/undc_vs_mcp_by_variable.csv,
         ../universe/undc_unicef_codes.csv, ../universe/out/unicef_universe_crosswalk.csv, unicef_ihme_mapping.csv
Outputs: ../unicefmcp/out/universe_dw_vs_undc_by_code.csv, universe_dw_summary.csv, universe_dw_by_flow.csv
Run    : python3 -I unicef_mcp_universe.py
"""
import pandas as pd, numpy as np
from pathlib import Path
import sys; sys.path.insert(0, str(Path(__file__).resolve().parent))   # allow -I runs
ROOT = Path(__file__).resolve().parent.parent
M, U = ROOT / "unicefmcp", ROOT / "universe"
OUT = M / "out"
inv = pd.read_csv(M / "inventory_all.csv", dtype=str, keep_default_na=False)
inv["flow"] = inv.flowRef.str.split("/").str[1]
nat = inv[~inv.flow.str.contains("SUBNAT|CME_SUBNATIONAL|MG_FLOW")]
cl = pd.read_csv(M / "codelist_unicef_indicator.csv", dtype=str, keep_default_na=False)
codes = pd.read_csv(U / "undc_unicef_codes.csv", dtype=str, keep_default_na=False)
byvar = pd.read_csv(OUT / "undc_vs_mcp_by_variable.csv", dtype=str, keep_default_na=False)
xw = pd.read_csv(U / "out" / "unicef_universe_crosswalk.csv", dtype=str, keep_default_na=False)
ihme = pd.read_csv(U / "out" / "unicef_ihme_mapping.csv", dtype=str, keep_default_na=False)
from undc_dw_crosswalk import map_code, parse_dims
variants = pd.read_csv(U / "undc_unicef_variables.csv", dtype=str, keep_default_na=False)

dw_codes_with_data = set(nat.INDICATOR)                       # codes with ≥1 observation for NGA/IND/BRA in a national flow
dw_codes_thematic = set(nat[nat.flow != "GLOBAL_DATAFLOW"].INDICATOR)
dw_flows_per_code = nat.groupby("INDICATOR").flow.agg(lambda s: ";".join(sorted(set(s))))
# map every UN DC variant DCID (with or without data) to its DW code
known = set(cl.id) | set(inv.INDICATOR)
vrows = []
for _, r in variants.iterrows():
    vs = [v for v in r.variants.split("|") if v] + ([""] if r.headline_variant_present == "True" or r.variants == "" else [])
    for v in vs:
        vrows.append((r.indicator_code, map_code(r.indicator_code, parse_dims(v), known)[0]))
vm = pd.DataFrame(vrows, columns=["code", "dw_code"])
mapped = vm[vm.dw_code != "?"].groupby("code").dw_code.agg(lambda s: ";".join(sorted(set(s)))).rename("dw_codes_mapped")
mapped_data = byvar.groupby("undc_code").unicef_code.agg(lambda s: ";".join(sorted(set(s))))
rows = []
for _, r in codes.iterrows():
    c = r.indicator_code
    m = mapped.get(c, "")
    targets = [t for t in m.split(";") if t]
    verbatim = c in dw_codes_with_data
    recoded = (not verbatim) and any(t in dw_codes_with_data for t in targets if t != c)
    in_cl = c in set(cl.id) or any(t in set(cl.id) for t in targets)
    status = ("verbatim code with DW data" if verbatim else "UN DC re-coding of a DW code with data" if recoded
              else "code in DW codelist, no DW data (3 countries)" if in_cl else "not in DW codelist")
    rows.append(dict(indicator_code=c, dataflow=r.dataflow, undc_name=r.undc_name, dw_status=status, dw_codes_mapped=m,
                     dw_flows=";".join(sorted({f for t in targets + [c] for f in dw_flows_per_code.get(t, "").split(";") if f})),
                     in_data360=xw.set_index("indicator_code").in_data360.get(c, ""), ihme_class=ihme.set_index("indicator_code").ihme_class.get(c, "")))
u = pd.DataFrame(rows)
u.to_csv(OUT / "universe_dw_vs_undc_by_code.csv", index=False)
summary = pd.DataFrame([
    dict(metric="DW indicator codes in CL_UNICEF_INDICATOR v1.0", value=len(cl)),
    dict(metric="DW codes with descriptions", value=int((cl.description != "").sum())),
    dict(metric="DW dataflows catalogued (UNICEF + UNPD)", value=inv.flowRef.nunique()),
    dict(metric="DW codes with ≥1 observation for NGA/IND/BRA (national flows)", value=len(dw_codes_with_data)),
    dict(metric="  of which only in GLOBAL_DATAFLOW", value=len(dw_codes_with_data - dw_codes_thematic)),
    dict(metric="UN DC UNICEF codes", value=len(codes)),
    dict(metric="  verbatim DW code with data", value=int((u.dw_status == "verbatim code with DW data").sum())),
    dict(metric="  UN DC re-coding of a DW code with data", value=int((u.dw_status == "UN DC re-coding of a DW code with data").sum())),
    dict(metric="  in DW codelist, no DW data for the 3 countries", value=int((u.dw_status == "code in DW codelist, no DW data (3 countries)").sum())),
    dict(metric="  not in DW codelist", value=int((u.dw_status == "not in DW codelist").sum())),
    dict(metric="DW codes with data that UN DC does not carry (any form)", value=len(dw_codes_with_data - set(codes.indicator_code) - {t for m in mapped for t in m.split(";")})),
])
summary.to_csv(OUT / "universe_dw_summary.csv", index=False)
# by UN DC dataflow
bf = u.groupby("dataflow").dw_status.value_counts().unstack(fill_value=0); bf["n_codes"] = bf.sum(axis=1); bf.loc["TOTAL"] = bf.sum()
bf.to_csv(OUT / "universe_dw_by_flow.csv")
# DW flows: codes with data not in UN DC, by flow
undc_all = set(codes.indicator_code) | {t for m in mapped for t in m.split(";")}
extra = nat[(~nat.INDICATOR.isin(undc_all)) & (nat.flow != "GLOBAL_DATAFLOW")].groupby("flow").INDICATOR.nunique().sort_values(ascending=False)
extra.to_csv(OUT / "universe_dw_codes_not_in_undc_by_flow.csv")
print(summary.to_string(index=False)); print(bf.to_string()); print("\nDW codes with data not in UN DC, by thematic flow:"); print(extra.to_string())
