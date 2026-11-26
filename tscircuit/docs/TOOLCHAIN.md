# tscircuit toolchain (verified 2026-11-26)

Installed: `@tscircuit/cli@0.1.2488`, `tscircuit@0.0.3296`, `typescript@5.9.3`, `@types/react`.
Node v22.23.5 works (npm prints an EBADENGINE warning, "node 24.x" wanted; ignore).

```bash
cd tscircuit
npm i -D @tscircuit/cli tscircuit typescript @types/react   # already done; `npm ci` to restore
npx tsci build index.circuit.tsx --svgs      # -> dist/index/{circuit.json,pcb.svg,schematic.svg,assembly.svg}
npx tsci build                               # builds every *.circuit.tsx (entry from tscircuit.config.json / globs)
npx tsci export index.circuit.tsx -f gerbers -o dist/gerbers.zip      # F_Cu, B_Cu, masks, paste, silk, Edge_Cuts, bom.csv, pick_and_place.csv
npx tsci export index.circuit.tsx -f pcb-svg -o dist/pcb.svg
npx tsci export index.circuit.tsx -f schematic-svg -o dist/sch.svg
npx tsci export index.circuit.tsx -f readable-netlist -o dist/netlist.txt   # handy for diffing vs netlist_v1
npx tsci export index.circuit.tsx -f circuit-json -o dist/circuit.json
# other -f formats: kicad_pcb kicad_sch kicad_zip altium step glb gltf specctra-dsn pcb-png assembly-svg ...
npx tsci build index.circuit.tsx --kicad-project   # KiCad project dirs
npx tsci snapshot                                  # schematic+PCB snapshots of *.circuit.tsx
```

Useful `tsci build` flags: `--svgs`, `--pcb-svgs`, `--schematic-svgs`, `--3d`, `--show-courtyards`,
`--routing-disabled` (skip autorouter, fast), `--ignore-errors`, `--ignore-warnings`,
`--ignore-{netlist,pin-specification,placement,routing}-drc`, `--autorouter-timeout 120s`.
Exit code 1 on DRC errors unless `--ignore-errors`.

## Gotchas
* `tsci build` does NOT type-check. For types: `npx tsc --noEmit -p . | grep -v '^node_modules'`
  (node_modules/@tscircuit/fanout-solver prints unrelated errors; `key` on `<smtpad>` in `.map()` gives a
  harmless TS2322).
* Network: the agent proxy returns `403 Forbidden (agent proxy: no rule or network setting allows this host)`
  for tscircuit/JLCPCB hosts. So `tsci search`, `tsci import C2913202`, `tsci import --jlcpcb`, and the
  build-time supplier lookups ("Failed to fetch supplier part numbers ...", "may not have availability from
  jlcpcb") fail. These are only WARNINGS; the build still passes (exit 0). `npm`, `raw.githubusercontent.com`
  are reachable. With open network use `npx tsci import --jlcpcb "C2913202"` to compare against our
  hand-written footprints.
* Gerber export prints `cannot verify jlcpcb pick-and-place rotation (missing_supplier_pin1_location)`
  when the JLC part data cannot be fetched: check CPL rotations by hand at JLC's preview.
* `dist/`, `.tscircuit/` (autorouter artifacts), `node_modules/` are git-ignored.
* Build of hello world takes ~5 s (autorouter included).
