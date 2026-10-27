#!/bin/bash
# Re-run process_flow.py for every flow already processed, using the exact args recorded in work/<ID>_args.txt
cd "$(dirname "$0")/.."
for f in work/*_args.txt; do bash "$f" | sed -n 3p; done
