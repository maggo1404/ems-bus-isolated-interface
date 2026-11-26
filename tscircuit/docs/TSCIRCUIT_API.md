# tscircuit API cheat sheet (every snippet below was built with `tsci build`, tscircuit 0.0.3296)

Test sources: `scratch/api.circuit.tsx`, `scratch/fp.circuit.tsx`, `scratch/lib.circuit.tsx`, `lib/*.tsx`.
Coordinates: mm, +X right, +Y UP (PCB and schematic). `pcbX/pcbY/pcbRotation` (deg), `schX/schY`.

```tsx
<board width="40mm" height="30mm" layers={2}>            // also: outline={[{x,y},...]}, borderRadius, thickness,
                                                         // fabricatorPreset="jlcpcb_standard"
  <net name="GND" />
  <resistor name="R1" resistance="10k" footprint="0805" pcbX={0} pcbY={10}
            supplierPartNumbers={{ jlcpcb: ["C17414"] }} />        // prop: supplierPartNumbers (keys jlcpcb|lcsc|mouser|digikey|pcbway|macrofab)
  <capacitor name="C1" capacitance="100nF" footprint="0603" pcbRotation={90} />
  <diode name="D1" footprint="sod123" />                 // pin1 = anode, pin2 = cathode
  <led name="LED1" footprint="0805" color="green" />
  <transistor name="Q1" type="npn" footprint="sot23" />  // npn: pin1=collector pin2=base pin3=emitter -- NOT the SOT-23 package order (BC817/BC847: 1=B 2=E 3=C); Q1 is therefore a <chip> with pinLabels B/E/C
  <chip name="U1" footprint="soic8"
        pinLabels={{ pin1: "A", pin2: "K", pin4: "GND" }}  // string or string[] aliases
        schPinArrangement={{ leftSide:{direction:"top-to-bottom",pins:["A","K"]}, rightSide:{direction:"top-to-bottom",pins:["OUT"]} }}
        manufacturerPartNumber="..." />
  <pinheader name="J2" pinCount={4} pitch="2.54mm" />
  <trace from=".U1 > .GND" to="net.GND" />               // selector: ".REF > .pinLabelOrpinN"; nets: "net.NAME"
  <hole diameter="3mm" pcbX={-17} pcbY={12} />           // NPTH
  <cutout shape="rect" width="1mm" height="12mm" pcbX={0} pcbY={-1} />   // board slot (isolation slot) ; also circle / polygon
  <keepout shape="rect" width="6mm" height="4mm" pcbX={15} pcbY={12} layers={["top","bottom"]} />  // -> pcb_keepout
  <copperpour layer="bottom" connectsTo="net.GND" />     // padMargin, traceMargin, clearance, boardEdgeMargin, cutoutMargin, outline, unbroken
  <group name="sub" pcbX={0} pcbY={0}> ... </group>      // subcircuit: <group subcircuit> or <subcircuit>, own autorouting
</board>
```

## Footprinter strings that build (pad count): `soic8`(8) `sot23`(3) `sot23_5`(5) `sot23_6`(6) `sot223`(4 incl. tab)
`sod123`(2) `sod323` `sma` `smb` `0603` `0805` `1206` `2010` `pinrow4`(4) `dip8_wide` `ssop8`, param form `soic8_w5.3mm_p1.27mm`.

## Custom footprint (chip with inline footprint)
```tsx
<chip name="U2" pinLabels={{ pin1:"P1", pin2:"P2" }}
  footprint={<footprint>
    <smtpad portHints={["pin1"]} shape="rect" width="0.8mm" height="1.2mm" pcbX={-1} pcbY={0} />
    <platedhole portHints={["pin3"]} shape="circle" holeDiameter="1mm" outerDiameter="1.6mm" pcbX={0} pcbY={3} />
    // shape="pill": outerWidth/outerHeight/holeWidth/holeHeight ; <hole/> for NPTH inside footprint
    <keepout shape="rect" .../>   <silkscreenpath route={[{x,y},...]} />   <silkscreentext text="U2" fontSize="1mm" />
  </footprint>} />
```
* Two pads with the SAME portHint are fine: tscircuit creates `pinN_internal_M` ports internally connected to
  the main port (used for USB-C duplicated GND/VBUS/D+/D- pads and shell legs, tactile switch, EP pads).
* `<keepout>` inside a `<footprint>` works (used for the ESP32 antenna keepout in `lib/esp32s3wroom1.tsx`).

## Solder jumper (default-open vs closed) - verified in circuit.json
```tsx
<solderjumper name="JP1" pinCount={2} footprint="solderjumper2" pcbX={5} pcbY={-5} />                          // OPEN (omit bridgedPins)
<solderjumper name="JP2" pinCount={2} footprint="solderjumper2" bridgedPins={[["1","2"]]} />                   // pre-bridged (internallyConnectedPins in circuit.json)
```
Ports are `.JP1 > .pin1`, `.pin2` (pinCount 3 also possible, footprint "solderjumper3").

## Warnings that are noise
"X is missing a name" (give `name` to traces), "No <schematicsheet>", "Port pinN missing a trace",
"overlaps" (schematic body overlaps: set schX/schY), "J/C/L prefix used with <chip>" (cosmetic), supplier
fetch failures when offline.

## Fab settings (verified with scratch boards `scratch/rt/*`, tscircuit 0.0.3296, 2-layer; also see `.claude/skills/tscircuit/elements/{board,trace,via,copperpour}.md`)
```tsx
<board layers={2}
  minViaHoleDiameter="0.3mm" minViaPadDiameter="0.6mm"      // vias: default 0.2/0.3 -> 0.3/0.6 (all autorouter vias). Documented equivalent: pcbStyle={{ viaHoleDiameter: "0.3mm", viaPadDiameter: "0.6mm" }} (both tested)
  minTraceWidth="0.2mm"                                      // router floor; with NO thickness all traces get 0.15 (default). Setting 0.4 makes EVERY trace >= 0.4 (honoured)
  // defaultTraceWidth / nominalTraceWidth="0.4mm" also set the width of all traces without thickness (tested)
  minTraceToPadEdgeClearance="0.25mm" minPadEdgeToPadEdgeClearance="0.25mm" minViaEdgeToPadEdgeClearance="0.25mm">
  <trace from=".U1 > .VCC" to="net.V3V3" thickness="0.5mm" />   // per-trace width ("width" is an alias); NO per-net prop -> lib/netclass.ts traceWidth(net)
  <copperpour layer="top" connectsTo="net.GND" clearance="0.25mm" padMargin traceMargin boardEdgeMargin cutoutMargin />   // pour clearance honoured (0.2 default -> gap 0.297 measured with 0.3)
  <via pcbX={0} pcbY={0} fromLayer="top" toLayer="bottom" holeDiameter="0.3mm" outerDiameter="0.6mm" connectsTo="net.GND" />   // hand-placed via (thermal/stitching)
</board>
```
Does the autorouter honour them? (measured with scripts/check_fab.py on the routed circuit.json)
* Via size: yes, exactly 0.3/0.6 (pcb_via + ViaDrill T0.3 in drill-L1-L2.drl). Without the props: 0.2/0.3 (fails JLC ring/drill).
* Trace width: `thickness` is only the NOMINAL width: in tight spots the router narrows the trace down to `minTraceWidth` (we saw 0.2 mm segments on 0.5 mm power nets and 0.35/0.45 stubs at narrow pads). To GUARANTEE a width: raise the board `minTraceWidth` (applies to all nets, then fine-pitch USB-C/SOT-23-6 breakouts violate clearance), or hand-route with `pcbPath` (elements/trace.md) / loosen the placement around the net.
* Clearance: `min*Clearance` props are honoured but only as router preference: 0.25 gives 0 DRC errors, 0.3 gives 14 `pcb_pad_trace_clearance_error` (build exit 1) because the 0.5 mm-pitch USB-C pads (gap 0.2) cannot satisfy it. Defaults give 0.10 mm gaps. Trace-to-trace default gap is not configurable separately; check_fab.py reports the real minimum.
* Pour: `clearance` honoured for straight traces; around WIDE DIAGONAL traces the pour hole was observed to be too small (gap 0.05 mm, see check_fab.py). Pour edge/NPTH margin is 0.2 by default (`boardEdgeMargin`, `cutoutMargin` raise it; check_fab wants 0.3 / 0.25).
* Keepouts/cutouts: pours and traces respected them in our build (no copper in slots/antenna area).
* `<solderpaste>`: pads take `noSolderPaste` (used in lib/jumper.tsx -> no paste aperture, verified in F_Paste.gbr).
* Gerber export: `npx tsci export dist/index/circuit.json -f gerbers -o <ABSOLUTE zip path>` (relative -o is resolved inside dist/index/). Exporting index.circuit.tsx directly re-runs without autorouting. Full flow: `scripts/export_fab.sh` (build ~20-40 s incl. autorouter), check: `scripts/check_fab.py [zip] [circuit.json]` (use `-` as zip for geometry-only).
* Documented checks worth running (skill CHECKLIST.md): `tsci check netlist`, `tsci check placement`, `tsci check shorts`.

## Autorouter-Erkenntnisse (AP7b, tscircuit 0.0.3296 / capacity-autorouter 0.0.1156)
* Breiten: `<net name="X" nominalTraceWidth=...>` + `thickness` pro `<trace>` setzen die Nennbreite; der Router schnuert Zweige von Mehrpin-Netzen (MST-Kanten) auf `min(board.minTraceWidth, kleinste Verbindungsbreite)` ein. Garantiert breit: `<trace from to thickness pcbPath={[...]}>`. `pcbPath`-Punkte sind im Rahmen des `from`-Bauteils (Drehung beachten) oder Strings `"D3.pin1"` (Port-Position).
* `routingPhaseIndex` auf `<net>` (mehrere Durchlaeufe) fuehrte hier zu ueberlappenden Bahnen; ein Durchlauf ist robuster. `autorouterEffortLevel` hat nichts geaendert.
* Board-Umriss mit Eckausschnitten: `<board outline={[{x,y},...]}>` (ccw, auch Bogenpunkte). Pour: `<copperpour outline=[...] boardEdgeMargin cutoutMargin clearance>`; Kreis-Keepouts werden vom Router nicht beachtet (Pour schon), Rechteck-Keepouts nur annaehernd.
* Handplatzierte `<via connectsTo="net.X">` verbinden einen Pour der anderen Lage (ohne Via wird ein Pour ohne Verbindung entfernt).

## Review-Fix-Erkenntnisse (R4/R5, tscircuit 0.0.3296)
* **Paste**: tscircuit schreibt standardmaessig 70 % x 70 % der Padgroesse (`getSolderPasteSize`, Core). Board-Prop `defaultSolderPasteMargin="0mm"` = 100 % (Margin je Seite: Pad + 2 x Margin); `noSolderPaste` pro Pad (JP1/JP2/TP). Auch Pill-Langloecher (J2-Schale) bekommen Paste: `scripts/postprocess_gerbers.py` entfernt sie.
* **Maske**: `solderMaskMargin` am `<smtpad>` wird in F_Mask uebernommen (JP1/JP2: 0,22 mm -> eine gemeinsame Oeffnung). Ohne Angabe Expansion 0.
* **Silk**: Strichbreite im Gerber = 0,09 x Schrifthoehe (0,072 mm bei 0,8 mm), Pfade 0,1 mm, nicht einstellbar -> `postprocess_gerbers.py` hebt auf 0,15 mm. Refdes der 0805-R/C: `pcbStyle={{ silkscreenTextVisibility: "hidden" }}` am Bauteil; Board-`pcbStyle={{ silkscreenFontSize: "1mm" }}` setzt alle uebrigen Refdes auf 1,0 mm.
* **Via-Abstand**: Board-Prop `minViaHoleEdgeToViaHoleEdgeClearance="0.25mm"` wird vom Autorouter beachtet (kein Via-Paar < 0,25 mm Loch-Rand zu Loch-Rand). `minTraceToPadEdgeClearance`/`minPadEdgeToPadEdgeClearance`/`minViaEdgeToPadEdgeClearance` 0,22..0,25 mm sowie `minTraceClearance` 0,25 mm fuehrten in dieser Platzierung zu Dutzenden Clearance-Fehlern bzw. Routingabbruch -> bei 0,2 mm geblieben.
* **`routeRemaining`**: ab mehr als 50 noch nicht verlegten Verbindungen (nach den `pcbPath`-Handbahnen) bricht tscircuit ohne `<board routeRemaining>` mit "Remaining routes left unrouted" ab; `routeRemaining` am Board setzen.
* **1-mm-Limit**: Eine Handbahn `<trace from="U2.pin5" to="C10.pin2">` zwischen Chip-Versorgungspin und Kondensator loest das automatische 1-mm-Decoupling-Limit aus ("Autorouting was skipped because the 1mm maximum length"). `maxDecouplingTraceLength={20}` am Kondensator hebt es auf (das Limit gilt sonst auch fuer das GND-Bein, das mit 2 mm Grenze 13,7 mm lang geroutet wurde und den Build mit Fehlern beendete).
* **Autorouter bleibt fragil**: schon 0,5 mm Verschiebung von L3, R16 oder R24 kippte das ganze Ergebnis (>100 Fehler). Vorgehen: einzeln aendern, `scripts/export_fab.sh` ablesen, bei Fehlern Teil um 0,3..1 mm verschieben. Gefundene Platzierung: C10/C30 rot 180 bei (-12,9 / 11,1) und (-12,9 / 12,9), R10/C8 1 mm nach rechts, R11 (-9,0 / -11,57), L3 (-20,6 / 14,57), R16 (-14,6 / 16,3), R24 (37,0 / 20,3), C29 (14,6 / 18,3) rot 270, F3 (26,2 / 15,0).
* Handverlegte VBUS-Bahnen am J2 (`pcbPath` J2.11 -> F3, U4.5 -> J2.11) erzeugten Kurzschluesse mit den USB-/CC-Bahnen: verworfen, VBUS bleibt autogeroutet (Verengung nur nahe der Feinraster-Pads).

## Review-Fix-Erkenntnisse (R6/R7 = FIX_LIST_R3.md, tscircuit 0.0.3296)
* **Silk-Text**: Gerber-Glyphenhoehe = 0,475 x fontSize + Strich (Strich 0,09 x fontSize); fontSize 1,85 mm -> 1,044 mm Glyphe, 0,167 mm Strich. `<silkscreentext pcbRotation={90}>` und `layer="bottom"` funktionieren (Bottom-Text wird gespiegelt). `<silkscreencircle radius strokeWidth>` = Ring (Pin-1-Punkt), Funktionskomponenten (`lib/silk.tsx`) duerfen innerhalb von `<footprint>` verwendet werden. Footprinter-Gehaeuse (sod123, sot23, sot23_6, sot223) haben keine Pin-1-Marke: Board-Ebene mit `toWorld()` aus Position/Drehung.
* **Pour-Splitter**: `clearance` 0,2/0,22/0,25/0,28 liefert jeweils andere 0,04-0,13-mm-Finger an anderen Stellen; kein Pour-Parameter dafuer. Loesung: Nachbearbeitung im Gerber (`scripts/slivers.py`).
* **Router**: `minViaHoleEdgeToViaHoleEdgeClearance="0.5mm"` wird eingehalten (kleinster Abstand 0,500 mm), aber ein handplatziertes Via neben einem Pad kollidiert mit dem Router-Via am selben Pad (Fehler `same_net_vias_close`) -> Hand-Via entfernt. C22/C23-Tausch: C22 rot 270 erzeugte 12 Routingfehler (V3V3-Hals an der Antenne), rot 90 laeuft sauber; F3 als 1206-Footprint (Pads 1,19 x 1,73 bei +-1,445) ohne Folgen fuer den Router.
* Gerber-Namen werden nur im ZIP geaendert (`postprocess_gerbers.py`), die Pruefskripte lesen sie ueber die JLC-Namen.
* **Gefuellte Silk-Flaechen (Barcode-Quadrat, Logo)**: tscircuit kennt fuer Silk nur Striche/Text/Kreise/Rechtecke (Gerber: Striche 0,1 mm); gefuellte Polygone gibt es nicht (`<silkscreenrect filled>` nicht getestet). Loesung: `scripts/silk_extras.py` (Geometrie, Logo aus `assets/blackswan.svg`), `postprocess_gerbers.py` haengt G36/G37-Regionen (LPD/LPC) an `F_Silkscreen`, `scripts/inject_svg.py` ergaenzt `dist/index/pcb.svg` fuer die PNGs. Platzierung aendert die Leiterbahnen nicht (kein Router-Einfluss).
