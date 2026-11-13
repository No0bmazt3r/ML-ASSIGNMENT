#!/usr/bin/env bash
# Full pipeline from raw CLEMD CSVs to every result and figure (~13 min, mostly train.py CV), then opens the UI.
#   ./run_all.sh              run every step, then open the dashboard
#   ./run_all.sh ui           just open the dashboard (no rerun)
#   ./run_all.sh <step> ...   run only those steps, e.g. ./run_all.sh ablation build_dashboard
#   PY=python ./run_all.sh    use another interpreter
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-.venv/bin/python}
STEPS=(prepare_data features train ablation evaluate explain cluster scenarios make_figures report_figures build_dashboard)

open_ui() {
  local page=dashboard/index.html
  echo "== opening $page"
  if command -v wslpath >/dev/null; then explorer.exe "$(wslpath -w "$page")" || true  # explorer.exe exits 1 on success
  elif command -v xdg-open >/dev/null; then xdg-open "$page"
  elif command -v open >/dev/null; then open "$page"
  else echo "open $PWD/$page in a browser"; fi
}

[[ ${1:-} == ui ]] && { open_ui; exit; }
for step in "${@:-${STEPS[@]}}"; do
  [[ -f $step.py ]] || { echo "unknown step '$step'; steps: ${STEPS[*]}"; exit 1; }
  echo "== $step"; $PY "$step.py"
done
open_ui
