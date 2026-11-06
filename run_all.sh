#!/usr/bin/env bash
# Full pipeline from raw CLEMD CSVs to every result and figure (~12 min, mostly train.py CV).
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
for step in prepare_data features train evaluate explain cluster scenarios make_figures; do
  echo "== $step"; $PY "$step.py"
done
