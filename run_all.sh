#!/usr/bin/env bash
# Full pipeline from raw CLEMD CSVs to every result and figure (~12 min, mostly train.py CV).
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-.venv/bin/python}  # override: PY=python ./run_all.sh
for step in prepare_data features train evaluate explain cluster scenarios make_figures build_dashboard; do
  echo "== $step"; $PY "$step.py"
done
