#!/usr/bin/env bash
# runs the whole project in order and then opens the dashboard
# ./run_all.sh            -> run everything (about 13 min)
# ./run_all.sh ui         -> only open the dashboard
# ./run_all.sh train ...  -> only run the steps you list
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-.venv/bin/python}
STEPS=(prepare_data features train ablation evaluate explain cluster scenarios make_figures report_figures build_dashboard)

open_ui() {
  local page=dashboard/index.html
  echo "== opening $page"
  # explorer.exe on WSL returns 1 even when it works, so ignore that
  if command -v wslpath >/dev/null; then explorer.exe "$(wslpath -w "$page")" || true
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
