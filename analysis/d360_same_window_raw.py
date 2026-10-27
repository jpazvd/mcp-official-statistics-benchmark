"""
Writes the two Data360 get_data responses re-run on 27 October 2026 for the 2000-2025 window (the warehouse and UN DC
windows), so that the characters on the efficiency frontier compare like with like. The first Data360 runs asked for
1960-2024 (U5MR, 61 observations) and 1980-2024 (DTP3, 41 observations).
The responses are rebuilt field by field from the tool output (compact JSON, same key order) and written to
../unicefmcp/cost/raw/B02b_d360_data_u5mr_2000.json and B04b_d360_data_dpt_2000.json.
Run: python3 -I d360_same_window_raw.py
"""
import json
from pathlib import Path
RAW = Path(__file__).resolve().parent.parent / "unicefmcp" / "cost" / "raw"
FV = ["ref_area_filter=member_economies_only applies only when REF_AREA is unpinned (omit country_code and do not set REF_AREA to specific codes); filter was not applied."]
u5 = [("2024","115.6","95b4eda2"),("2023","116.8","af53c5aa"),("2022","117.5","0e95df7a"),("2021","117.6","e916d6b1"),("2020","117.4","c8719d2c"),
      ("2019","117.4","8c78d070"),("2018","117.2","b412dda2"),("2017","117.2","2c718632"),("2016","117.4","141b8be0"),("2015","117.8","a496fbde"),
      ("2014","118.7","73d362df"),("2013","119.9","4248b8b4"),("2012","121.6","4a144ba5"),("2011","123.8","6f884cad"),("2010","126.3","de239e57"),
      ("2009","129.2","672b8d24"),("2008","132.5","af47a24f"),("2007","136.5","df7a57bd"),("2006","140.9","9fd6ea84"),("2005","145.8","a69a4592"),
      ("2004","151.4","60e7de2d"),("2003","157.4","d08b3f7b"),("2002","163.9","da7b188a"),("2001","170.5","0c1b83ab"),("2000","177.3","7faf5f92")]
d3 = [("2024","67","ce9105a5"),("2023","67","0aef8d71"),("2022","59","4768189b"),("2021","61","4475ee35"),("2020","62","6338df97"),
      ("2019","66","ee7c9188"),("2018","61","7a2e671f"),("2017","55","19bd4254"),("2016","53","d7f4049e"),("2015","42","18bca7b4"),
      ("2014","43","8bc6f6ac"),("2013","39","f98932ca"),("2012","36","d0954c76"),("2011","53","c442a886"),("2010","56","e4273eab"),
      ("2009","63","0107321e"),("2008","53","f6e68850"),("2007","42","5771b781"),("2006","40","2a27367e"),("2005","36","c55c3490"),
      ("2004","33","e539a2bd"),("2003","29","ea76d0cd"),("2002","25","2d467e96"),("2001","27","19a23ba2"),("2000","29","6aa5f543")]
def resp(rows, unit, unit_name, meta):
    data = [{"OBS_VALUE": v, "UNIT_MULT": 0, "REF_AREA": "NGA", "TIME_PERIOD": y, "UNIT_MEASURE": unit, "claim_id": c,
             "REF_AREA_NAME": "Nigeria", "UNIT_MEASURE_NAME": unit_name} for y, v, c in rows]
    return {"count": len(rows), "total_count": None, "offset": 0, "has_more": False, "next_offset": None, "data": data,
            "metadata": meta, "error": None, "failed_validation": FV}
m_u5 = {"idno": "WB_WDI_SH_DYN_MORT", "name": "Mortality rate, under-5 (per 1,000 live births)", "database_id": "WB_WDI",
        "database_name": "World Development Indicators (WDI)", "measurement_unit": "Per 1000 live births", "periodicity": "Annual", "definition_short": None}
m_d3 = {"idno": "WB_WDI_SH_IMM_IDPT", "name": "Immunization, DPT (% of children ages 12-23 months)", "database_id": "WB_WDI",
        "database_name": "World Development Indicators (WDI)", "measurement_unit": "Percentage", "periodicity": "Annual", "definition_short": None}
for name, obj in (("B02b_d360_data_u5mr_2000.json", resp(u5, "DT_10P3BR_L", "Deaths per 1 000 live births", m_u5)),
                  ("B04b_d360_data_dpt_2000.json", resp(d3, "PT", "Percentage", m_d3))):
    txt = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    (RAW / name).write_text(txt, encoding="utf-8")
    print(name, len(txt), "characters,", obj["count"], "observations")
