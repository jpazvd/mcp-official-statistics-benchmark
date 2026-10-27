#!/usr/bin/env python3
"""Print K_INV and K_TOT for a flow from its list_dimensions JSON, applying the brief's rule:
wildcard for INDICATOR and any dim containing 'AGE'; wildcard for non-breakdown-named dims or dims with no codelist; '_T' otherwise."""
import json, sys
HINTS = ("VACCINE", "WASH_SERVICE", "UNIT", "FREQ", "TIME_PERIOD_METHOD", "VALUE_TYPE", "CAUSE", "SERVICE", "DOMAIN", "HAZARD", "SOURCE", "THRESHOLD", "SERIES", "PARENT", "ADMIN")
d = json.load(open(sys.argv[1]))
dims = sorted(d["result"], key=lambda x: x["position"])
ids = [x["id"] for x in dims]
rest = ids[1:]
k_inv = "NGA+IND+BRA" + "." * len(rest)
parts = []
why = []
for x in dims[1:]:
    i = x["id"]
    if i == "INDICATOR" or "AGE" in i:
        parts.append(""); why.append(f"{i}=wildcard(indicator/age)")
    elif any(h in i for h in HINTS) or x.get("codelist") is None:
        parts.append(""); why.append(f"{i}=wildcard(non-breakdown{'/no codelist' if x.get('codelist') is None else ''})")
    else:
        parts.append("_T"); why.append(f"{i}=_T")
k_tot = "NGA+IND+BRA." + ".".join(parts)
print("dims:", ids)
print("K_INV:", k_inv)
print("K_TOT:", k_tot)
print("rule:", "; ".join(why))
