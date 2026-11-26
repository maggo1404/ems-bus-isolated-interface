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
  <transistor name="Q1" type="npn" footprint="sot23" />  // npn: pin1=collector pin2=base pin3=emitter (labels .collector .base .emitter) -- NOT the SOT-23 package order; check vs BC847/MMBT3904 pinout (1=B 2=E 3=C)
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
