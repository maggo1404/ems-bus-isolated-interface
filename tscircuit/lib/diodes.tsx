// Diodes / LEDs with JLC pad numbering (verified against EasyEDA, see docs/FOOTPRINT_CHECK.md):
//  * 1N4148W C81598, B5819W C8598 (SOD-123):   pad 1 = cathode (K), pad 2 = anode (A)
//  * BAT42W  C22466362 (SOD-123):              pad 1 = ANODE (A),   pad 2 = cathode (K)
//  * LED red C84256 (0805):                    pad 1 = cathode, pad 2 = anode (pad 1 left)
//  * LED green C2297 (0805):                   pad 1 = ANODE (right), pad 2 = cathode (left)
// In every LED footprint the cathode is on the left (-X) at rotation 0, like the JLC footprint.
import type { ChipProps } from "tscircuit"

const kaArr = { leftSide: { direction: "top-to-bottom", pins: ["A"] }, rightSide: { direction: "top-to-bottom", pins: ["K"] } } as any

/** SOD-123 diode, pad 1 = K, pad 2 = A */
export const DiodeKA = (p: any) => (
  <chip pinLabels={{ pin1: ["K"], pin2: ["A"] }} schPinArrangement={kaArr} footprint="sod123" {...p} />
)
/** SOD-123 diode, pad 1 = A, pad 2 = K (BAT42W) */
export const DiodeAK = (p: any) => (
  <chip pinLabels={{ pin1: ["A"], pin2: ["K"] }} schPinArrangement={kaArr} footprint="sod123" {...p} />
)

const ledSilk = <silkscreenpath route={[{ x: -1.95, y: -0.8 }, { x: -1.95, y: 0.8 }]} />
/** 0805 red LED C84256: pad 1 = K at x=-1.05, pad 2 = A at x=+1.05 */
export const LedRed = (p: any) => (
  <chip pinLabels={{ pin1: ["K"], pin2: ["A"] }} schPinArrangement={kaArr}
    supplierPartNumbers={{ jlcpcb: ["C84256"] }} manufacturerPartNumber="NCD0805R1"
    footprint={<footprint>
      <smtpad portHints={["pin1"]} shape="rect" width="1.0mm" height="1.4mm" pcbX={-1.05} pcbY={0} />
      <smtpad portHints={["pin2"]} shape="rect" width="1.0mm" height="1.4mm" pcbX={1.05} pcbY={0} />
      {ledSilk}
    </footprint>} {...p} />
)
/** 0805 green LED C2297: pad 1 = A at x=+1.05, pad 2 = K at x=-1.05 (cathode left, as the JLC footprint) */
export const LedGreen = (p: any) => (
  <chip pinLabels={{ pin1: ["A"], pin2: ["K"] }} schPinArrangement={kaArr}
    supplierPartNumbers={{ jlcpcb: ["C2297"] }} manufacturerPartNumber="KT-0805G"
    footprint={<footprint>
      <smtpad portHints={["pin1"]} shape="rect" width="1.0mm" height="1.4mm" pcbX={1.05} pcbY={0} />
      <smtpad portHints={["pin2"]} shape="rect" width="1.0mm" height="1.4mm" pcbX={-1.05} pcbY={0} />
      {ledSilk}
    </footprint>} {...p} />
)
