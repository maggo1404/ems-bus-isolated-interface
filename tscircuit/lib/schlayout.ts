// Schematic placement table (schematic units, +X right, +Y up), see docs/TSCIRCUIT_API.md "Schematic conventions".
// Only sch* props are derived from here - the PCB placement (pcbX/pcbY/pcbRotation) is untouched.
// Signal flow left -> right: EMS bus (x < 0, isolated) | optocouplers on the barrier x = 0 | MCU side (x > 0).
// Rotation convention (tscircuit schRotation is counter-clockwise):  passives 0 = pin1 left, 90 = pin1 bottom,
// 270 = pin1 top; 2-pin chips with "left" pin first behave the same.
type L = [x: number, y: number, rot?: number]
export const SCHL: Record<string, L> = {
  // ---------------- 1 EMS: bus terminal, fuses, filter, bridge, clamp ----------------
  // bridge: two vertical legs, N4 row (top) feeds D3/D4 (x -35), N3 row (bottom) feeds D1/D2 (x -31); N6 = rectified rail, GND_EMS below
  P1: [-46, 16], F1: [-43, 19.5], F2: [-43, 12.5], L1: [-39.5, 19.5], L2: [-39.5, 12.5], C1: [-37.3, 16, 90],
  D3: [-35, 21.5, 90], D4: [-35, 17.5, 90], D1: [-31, 14.5, 90], D2: [-31, 10.5, 90], D5: [-28, 16, 90],
  // ---------------- 2 EMS: reverse diode, bulk, buck U2, 5 V rail ----------------
  D7: [-28, 20.5, 90], C12: [-25.5, 17, 270], C14: [-23, 17, 270], C10: [-20.8, 17, 90], C30: [-19.4, 17, 90],
  R16: [-17.6, 20, 270], U2: [-13.5, 16.5], C9: [-10.5, 20.5], L3: [-9, 17.5, 270],
  C11: [-7.2, 17.2, 270], C8: [-5.9, 17.2, 270], C6: [-4.6, 17.2, 90], C13: [-3.3, 17.2, 90],
  R12: [-12, 12.8, 90], R15: [-12, 10.5, 90], R17: [-6, 13, 90], LD1: [-6, 10.5, 270],
  // ---------------- 3 EMS: RX path (bus -> comparator A -> OC1) ----------------
  R1: [-45, 3.5], R5: [-42.7, 1.3, 90], D6: [-42.7, -1.4, 270], C2: [-39.5, 4, 90], C3: [-39.5, 1.5, 90], R6: [-36.5, 2, 90], R7: [-34.5, -0.5, 90], R8: [-32.5, -0.5, 90],
  U1: [-27, 1.5], R10: [-6, 4.5, 90],
  // ---------------- 4 EMS: TX path (OC2 -> comparator U1B -> Q1 -> bus load) ----------------
  R2: [-45, -10], R3: [-42, -10], R4: [-39, -10], Q1: [-35, -10], C4: [-37, -13, 90], R9: [-31.5, -8.3, 90],
  R11: [-8, -7, 90], C5: [-8, -11.5, 90],
  // ---------------- 5 isolation barrier ----------------
  OC1: [0, 2], OC2: [0, -9.5],
  // ---------------- 6 MCU: opto interface helpers ----------------
  C7: [4, 6, 90], R13: [7, 5.5, 90], R18: [10, 7, 90], LD3: [10, 4.6, 270],
  R14: [4, -6, 270], R19: [7.5, -5.5, 270], LD2: [7.5, -8, 270],
  // ---------------- 7 MCU: UART header, JP1 / JP2 ----------------
  R27: [16, -3, 90], JP2: [19.5, -2], JP1: [19.5, -6.5], P2: [25, -4.5],
  // ---------------- 8 MCU: USB-C, ESD, PTC ----------------
  J2: [6, 17], U4: [12, 20], F3: [12, 14.5], R23: [9, 11, 270], R24: [10.8, 11, 270], R25: [3, 11, 270], C21: [4.8, 11, 270],
  // ---------------- 9 MCU: LDO and 3V3 rail (incl. the U3 decoupling C22/C23) ----------------
  U5: [19.5, 14.5], C24: [16.5, 11.5, 270], C25: [18, 11.5, 270], C29: [22.5, 11.5, 270], C26: [24, 11.5, 270], C27: [25.5, 11.5, 270], C28: [27, 11.5, 270],
  C22: [28.5, 11.5, 270], C23: [30, 11.5, 270], R26: [32.5, 17.3, 270], LD5: [32.5, 15, 270],
  // ---------------- 10 MCU: ESP32-S3 and support ----------------
  U3: [48, 8], R20: [43.5, 13.3, 270], C20: [41.2, 11.8, 270], SW1: [39.8, 9.8], R21: [43.5, 6.5, 270], SW2: [40.2, 4.5],
  R22: [43.5, 0.5, 270], LD4: [43.5, -1.9, 270], TP1: [39, -5.5], TP2: [39, -7.5], TP3: [39, -9.5],
}
type Pins = string | string[]
const L1 = (p: Pins) => (Array.isArray(p) ? p : [p])
/** schematic props of `ref`.  Resistors/capacitors rotate with schRotation; a <chip> ignores schRotation, so for 2-sided chips pass
 *  `pair` = [pins on the left at rotation 0, pins on the right at rotation 0] and the table rotation is turned into a pin arrangement. */
export const SCALE = 1 // compaction of the hand-placed table above (keeps neighbours close, the parts themselves are small)
export const sch = (ref: string, pair?: [Pins, Pins]) => {
  const l = SCHL[ref]
  if (!l) throw new Error(`no schematic position for ${ref}`)
  const [x0, y0, r = 0] = l
  const schX = +(x0 * SCALE).toFixed(3), schY = +(y0 * SCALE).toFixed(3)
  if (!pair) return r ? { schX, schY, schRotation: r } : { schX, schY }
  const [a, b] = [L1(pair[0]), L1(pair[1])]
  const side = (pins: string[], dir: "top-to-bottom" | "left-to-right") => ({ direction: dir, pins })
  const arr: any =
    r === 0 ? { leftSide: side(a, "top-to-bottom"), rightSide: side(b, "top-to-bottom") }
    : r === 180 ? { leftSide: side(b, "top-to-bottom"), rightSide: side(a, "top-to-bottom") }
    : r === 90 ? { bottomSide: side(a, "left-to-right"), topSide: side(b, "left-to-right") }
    : { topSide: side(a, "left-to-right"), bottomSide: side(b, "left-to-right") }
  // vertical 2-pin boxes need room between the top and bottom pin labels (tsci check schematic-placement)
  const longLabel = [...a, ...b].some((n) => n.length > 2)
  return { schX, schY, schPinArrangement: arr, ...(r === 90 || r === 270 ? { schHeight: longLabel ? 0.95 : 0.55 } : {}) }
}
