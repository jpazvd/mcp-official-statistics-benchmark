"""Convert the targeted UNICEF SDMX MCP pulls (breakdown rows that the totals extraction did not cover)
into the series_all.csv schema -> supplement/series_supplement.csv.
Raw inputs (verbatim tool output, query_data format=csv labels=id, startPeriod 2000 endPeriod 2025):
  raw/DM_residence.json          UNICEF/DM/1.0            key NGA+IND+BRA.DM_POP_URBN+DM_POP_U_GRT+DM_POP_DOU+DM_BU_PC_DOU+DM_POP_DOU_GRT.U+R+CITY+TSUB._T._T
  raw/MG_statpop.json            UNICEF/MG/1.0            key NGA+IND+BRA.<7 MG codes>..  (AGE and STAT_POP wildcard)
  raw/PT_CM_marital.csv          UNICEF/PT_CM/1.0         key NGA+IND+BRA.<7 PT_CM codes>._T.Y20T24._T x7.MRD_NEVER+MRD_18PLUS+MRD_U18
  raw/GENDER_sex_subset.csv      UNICEF/GENDER/1.0        key NGA+IND+BRA.<7 GN codes>.F+M.._T._T  (only GN_ED_ATTN, GN_TIMEUSE, GN_IT_MOB_OWN rows kept)
  raw/SOC_PROTECTION_quintiles.csv UNICEF/SOC_PROTECTION/1.0 keys ...Q1+Q2+Q3+Q4+Q5. and NGA+IND+BRA.SPP_CHLD_POV_PROF._T._T..
  raw/HIV_AIDS_prev_sex.csv      UNICEF/HIV_AIDS/1.0      key NGA+IND+BRA.HVA_PREV_KNOW+HVA_PREV_KNOW_TEST+HVA_PREV_CNDM_MULT.Y15T19+Y15T24+Y20T24.F+M._T._T.
  raw/FD_CHLD_PVTY.csv           UNICEF/FUNCTIONAL_DIFF/1.0 key NGA+IND+BRA.FD_ANAR+FD_FUNC_DIFFICULTY._T.._T._T._T....0.  and UNICEF/CHLD_PVTY/1.0 key NGA+IND+BRA.PV_ADOLESCENT.F._T
Run: python3 -I build_supplement.py
"""
import csv, io, json
from pathlib import Path
H = Path(__file__).resolve().parent
RAW = H / "raw"
COLS = ["flowRef", "indicator", "iso3", "dims_json", "time_period", "value", "lower_bound", "upper_bound", "obs_status", "data_source",
        "unit_measure", "ref_period", "country_notes_flag", "extra_attrs_json"]
NONDIM = {"TIME_PERIOD", "OBS_VALUE", "LOWER_BOUND", "UPPER_BOUND", "OBS_STATUS", "DATA_SOURCE", "UNIT_MEASURE", "REF_PERIOD", "COUNTRY_NOTES",
          "REF_AREA", "INDICATOR", "flowRef"}
DIMS = {  # ordered dimension ids per flow (from flows_all.csv)
    "UNICEF/DM/1.0": ["RESIDENCE", "SEX", "AGE"],
    "UNICEF/MG/1.0": ["AGE", "STAT_POP"],
    "UNICEF/PT_CM/1.0": ["SEX", "AGE", "EDUCATION_LEVEL", "WEALTH_QUINTILE", "RESIDENCE", "SCHOOL_ED_LEVEL", "RELIGIOUS_GROUP", "ETHNIC_GROUP", "PROJ_SCENARIO", "CH_MARRIAGE_STATUS"],
    "UNICEF/GENDER/1.0": ["SEX", "AGE", "RESIDENCE", "EDUCATION_LEVEL"],
    "UNICEF/SOC_PROTECTION/1.0": ["SEX", "RESIDENCE", "WEALTH_QUINTILE", "POV_THRESHOLD"],
    "UNICEF/HIV_AIDS/1.0": ["AGE", "SEX", "WEALTH_QUINTILE", "RESIDENCE", "DATA_SOURCE"],
    "UNICEF/FUNCTIONAL_DIFF/1.0": ["SEX", "AGE", "RESIDENCE", "WEALTH_QUINTILE", "ETHNIC_GROUP", "EDUCATION_LEVEL", "DISABILITY_STATUS", "DATA_SOURCE", "ADMIN_LEVEL", "REF_AREA_PARENT"],
    "UNICEF/CHLD_PVTY/1.0": ["SEX", "RESIDENCE"],
}
def rows_from(flow, rows):
    out = []
    for r in rows:
        dims = {k: r.get(k, "") for k in DIMS[flow] if k in r}
        extra = {k: v for k, v in r.items() if k not in NONDIM and k not in dims and v not in ("", None)}
        out.append(dict(flowRef=flow, indicator=r["INDICATOR"], iso3=r["REF_AREA"], dims_json=json.dumps(dims, separators=(",", ":")),
                        time_period=r["TIME_PERIOD"], value=r["OBS_VALUE"], lower_bound=r.get("LOWER_BOUND", ""), upper_bound=r.get("UPPER_BOUND", ""),
                        obs_status=r.get("OBS_STATUS", ""), data_source=r.get("DATA_SOURCE", ""), unit_measure=r.get("UNIT_MEASURE", ""),
                        ref_period=r.get("REF_PERIOD", ""), country_notes_flag=1 if r.get("COUNTRY_NOTES") else 0,
                        extra_attrs_json=json.dumps(extra, separators=(",", ":"))))
    return out
all_rows = []
for f, flow in [("DM_residence.json", "UNICEF/DM/1.0"), ("MG_statpop.json", "UNICEF/MG/1.0")]:
    j = json.load(open(RAW / f)); all_rows += rows_from(flow, csv.DictReader(io.StringIO(j["raw_csv"])))
for f, flow in [("PT_CM_marital.csv", "UNICEF/PT_CM/1.0"), ("GENDER_sex_subset.csv", "UNICEF/GENDER/1.0"),
                ("SOC_PROTECTION_quintiles.csv", "UNICEF/SOC_PROTECTION/1.0"), ("HIV_AIDS_prev_sex.csv", "UNICEF/HIV_AIDS/1.0")]:
    all_rows += rows_from(flow, csv.DictReader(open(RAW / f, newline="")))
for r in csv.DictReader(open(RAW / "FD_CHLD_PVTY.csv", newline="")):
    all_rows += rows_from(r["flowRef"], [r])
with open(H / "series_supplement.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(all_rows)
from collections import Counter
print(len(all_rows), "rows"); print(Counter(r["flowRef"] for r in all_rows))
