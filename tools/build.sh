#!/usr/bin/env bash
# Rebuild every generated view and PDF from the data files.
#   ./tools/build.sh
# Requires python3 (+PyYAML) and Chromium/Chrome for the PDFs
# (override the browser with CHROMIUM=/path/to/chrome).
set -euo pipefail
cd "$(dirname "$0")/.."

CHROMIUM="${CHROMIUM:-$(command -v chromium || command -v chromium-browser || command -v google-chrome || echo /opt/pw-browsers/chromium)}"

python3 tools/generate_org_views.py
python3 tools/generate_counterpart_map.py

pdf() {  # pdf <in.html> <out.pdf>
  "$CHROMIUM" --headless --disable-gpu --no-sandbox --no-pdf-header-footer \
    --print-to-pdf="$2" "file://$PWD/$1" 2>/dev/null
  echo "Wrote $2"
}

pdf 02-organization/generated/print-dashboard.html 02-organization/generated/dashboard.pdf
pdf 06-toolkit/generated/print-matrix.html         06-toolkit/generated/counterpart-matrix.pdf
pdf 06-toolkit/generated/print-cards.html          06-toolkit/generated/counterpart-cards.pdf
