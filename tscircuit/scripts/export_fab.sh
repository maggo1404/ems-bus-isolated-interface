#!/usr/bin/env bash
# Fab export: build WITH autorouter -> Gerbers/drill exported FROM the routed dist/index/circuit.json
# -> JLCPCB BOM/CPL -> netlist check -> fab check.  Usage: scripts/export_fab.sh [autorouter-timeout, default 300s]
# (The Gerbers must come from dist/index/circuit.json: exporting index.circuit.tsx re-runs without traces/vias.)
set -euo pipefail
cd "$(dirname "$0")/.."
TIMEOUT="${1:-300s}"
ZIP=fab/EMSinterface_V2.0-gerbers.zip
mkdir -p fab

echo "== 1/5 build + autoroute"
npx tsci build index.circuit.tsx --svgs --ignore-placement-drc --autorouter-timeout "$TIMEOUT"
echo "== 1b bottom-side SVG (docs/img/pcb_bottom.png via scripts/render_png.cjs)"
node -e "const {convertCircuitJsonToPcbSvg}=require('circuit-to-svg');const fs=require('fs');fs.writeFileSync('dist/index/pcb_bottom.svg',convertCircuitJsonToPcbSvg(JSON.parse(fs.readFileSync('dist/index/circuit.json','utf8')),{layer:'bottom'}))"
echo "== 1c barcode square + swan logo into dist/index/pcb.svg (not native tscircuit elements; scripts/silk_extras.py)"
python3 scripts/inject_svg.py dist/index/pcb.svg dist/index/circuit.json
echo "== 2/5 gerbers from dist/index/circuit.json"
npx tsci export dist/index/circuit.json -f gerbers -o "$PWD/$ZIP"
echo "== 3/5 BOM / CPL (JLCPCB format; reads bom.csv/pick_and_place.csv from the zip BEFORE they are removed)"
python3 scripts/jlc_bom_cpl.py "$ZIP" fab/EMSinterface_V2.0 dist/index/circuit.json
echo "== 3b gerber post-processing (silk barcode square + logo regions, silk stroke >= 0.16 mm, pour slivers, paste on slots, JLC/KiCad file names, drop tscircuit bom.csv / pick_and_place.csv)"
python3 scripts/postprocess_gerbers.py "$ZIP" dist/index/circuit.json
echo "== 4/5 netlist check"
python3 scripts/check_netlist.py dist/index/circuit.json
echo "== 5/5 fab check (traces/vias/widths/clearance/keepouts/USB-C)"
rc=0
python3 scripts/check_fab.py "$ZIP" dist/index/circuit.json || rc=$?
python3 scripts/check_isolation.py dist/index/circuit.json || rc=$?
echo "export_fab.sh finished, check status = $rc (files in fab/)"
exit $rc
