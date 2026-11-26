// EMS side of the isolated EMS-bus interface (V1 netlist 1:1, see docs/netlist_v1.json).
// Contains everything of V1 except P2, incl. OC1/OC2 and the MCU-side opto helpers
// (R13, R14, R18, R19, LD2, LD3, C7).  Net names follow docs/DESIGN_SPEC.md.
import { Opto6N137, Opto6N136 } from "../lib/opto_so8_gw300"
import { Mstba2, CapE5_10p5, Inductor3225, Inductor0520, Res2010Footprint } from "../lib/thtparts"

// ---------------------------------------------------------------------------
// Net table: net name -> physical pad connections "Ref.pad" (V1 pad numbers;
// diode/LED A=1 C=2, C12 +=1 -=2).  Pad N is always port `pinN` in tscircuit.
// ---------------------------------------------------------------------------
const NETS: Record<string, string[]> = {
  // EMS side
  V5_EMS: ["C6.2", "C8.1", "C11.1", "C13.2", "L3.1", "OC2.8", "R9.2", "R10.2", "R11.2", "R12.2", "R17.2", "U1.8"],
  GND_EMS: ["C4.1", "C5.1", "C6.1", "C8.2", "C10.1", "C11.2", "C12.2", "C13.1", "D2.1", "D4.1", "D5.1", "D6.2", "LD1.2", "OC2.5", "Q1.2", "R8.1", "R15.1", "U1.4", "U2.2"],
  EMS_N1: ["F2.2", "L2.1"],
  EMS_N10: ["C3.2", "R7.2", "R8.2", "U1.2"],
  EMS_N11: ["R3.2", "R4.1"],
  EMS_N12: ["R2.2", "R3.1"],
  EMS_N13: ["C4.2", "Q1.3", "R4.2"],
  EMS_N14: ["Q1.1", "R9.1", "U1.7"],
  EMS_N15: ["C5.2", "OC2.6", "R11.1", "U1.6"],
  EMS_N16: ["OC1.2", "R10.1"],
  EMS_N17: ["F1.1", "P1.1"],
  EMS_N18: ["OC1.3", "U1.1"],
  EMS_N2: ["F1.2", "L1.1"],
  EMS_N23: ["R12.1", "R15.2", "U2.3"],
  EMS_N25: ["C9.1", "U2.1"],
  EMS_N26: ["C9.2", "L3.2", "U2.6"],
  EMS_N27: ["LD1.1", "R17.1"],
  EMS_N29: ["R16.2", "U2.4"],
  EMS_N3: ["C1.1", "D1.1", "D2.2", "L2.2"],
  EMS_N4: ["C1.2", "D3.1", "D4.2", "L1.2"],
  EMS_N5: ["F2.1", "P1.2"],
  EMS_N6: ["D1.2", "D3.2", "D5.2", "D7.1", "R1.1", "R2.1"],
  EMS_N7: ["D6.1", "R5.1", "R6.1", "R7.1", "U1.5"],
  EMS_N8: ["C2.1", "C3.1", "R1.2", "R5.2"],
  EMS_N9: ["C2.2", "R6.2", "U1.3"],
  EMS_VIN: ["C10.2", "C12.1", "D7.2", "R16.1", "U2.5"],
  // MCU side (shared with src/mcu-side.tsx through these net names)
  GND: ["C7.1", "OC1.5"],
  MCU_RX: ["LD3.2", "OC1.6", "R13.1"],
  MCU_TX: ["LD2.2", "OC2.3"],
  V3V3: ["C7.2", "OC1.7", "OC1.8", "R13.2", "R14.1", "R18.2", "R19.1"],
  MCU_N19: ["OC2.2", "R14.2"],
  MCU_N20: ["LD2.1", "R19.2"],
  MCU_N24: ["LD3.1", "R18.1"],
}

// ---------------------------------------------------------------------------
// Placement: V1 board coordinates (docs/netlist_v1.md "Layout V1") mapped to the
// V2 board (centre 0,0, Y up): OC at x = 0, x stretched 0.95, y stretched 1.35.
// ---------------------------------------------------------------------------
const tx = (x: number) => +((x - 1.4) * 0.95 - 50.7).toFixed(2)
const ty = (y: number) => +((y - 16.83) * 1.35).toFixed(2)
const sch = (v: number) => +(v * 0.3).toFixed(2)

type P = { x: number; y: number; r?: number }
// V1 (x, y, rot) per ref
const V1: Record<string, P> = {
  L1: { x: 10.79, y: 20.0, r: 90 }, L2: { x: 10.79, y: 12.38, r: 90 },
  C1: { x: 14.76, y: 9.54, r: 90 },
  D1: { x: 16.51, y: 5.71, r: 180 }, D2: { x: 16.51, y: 1.91 }, D3: { x: 16.51, y: 13.34, r: 180 }, D4: { x: 16.51, y: 17.14 },
  D5: { x: 21.59, y: 3.81, r: 90 },
  R1: { x: 22.54, y: 13.34 }, R2: { x: 21.59, y: 19.05, r: 90 }, R3: { x: 25.4, y: 19.05, r: 90 }, R4: { x: 29.21, y: 19.05, r: 90 },
  C2: { x: 28.57, y: 8.26 }, C3: { x: 28.57, y: 11.43 }, R5: { x: 24.77, y: 10.48, r: 90 },
  U1: { x: 36.83, y: 9.53, r: 90 }, D6: { x: 24.77, y: 3.81, r: 90 },
  R6: { x: 28.57, y: 5.71 }, R7: { x: 28.57, y: 1.91 }, R8: { x: 28.57, y: 13.97 },
  R9: { x: 43.81, y: 12.7, r: 90 }, Q1: { x: 42.7, y: 16.85, r: 90 }, C4: { x: 42.6, y: 20.32 },
  C5: { x: 43.81, y: 4.39, r: 90 }, C6: { x: 35.81, y: 5.71 }, R10: { x: 42.23, y: 24.13 },
  R11: { x: 43.81, y: 8.26, r: 90 }, D7: { x: 16.51, y: 20.32 },
  U2: { x: 34.92, y: 24.77, r: 90 }, R12: { x: 39.6, y: 24.45, r: 90 }, R15: { x: 39.6, y: 20.95, r: 90 },
  C9: { x: 30.2, y: 24.45, r: 90 }, R16: { x: 35.24, y: 28.89 }, C10: { x: 32.07, y: 28.57, r: 90 }, C11: { x: 21.91, y: 31.43 },
  F1: { x: 7.62, y: 19.37, r: 90 }, F2: { x: 7.62, y: 14.29, r: 90 }, R17: { x: 42.23, y: 28.89 },
  L3: { x: 26.99, y: 27.62 }, LD1: { x: 46.67, y: 30.8 }, C12: { x: 14.61, y: 27.62, r: 90 },
  C8: { x: 42.23, y: 26.35 }, C13: { x: 47.62, y: 3.17, r: 90 },
}
const pos = (ref: string) => {
  const p = V1[ref]
  return { pcbX: tx(p.x), pcbY: ty(p.y), pcbRotation: p.r ?? 0, schX: sch(tx(p.x)), schY: sch(ty(p.y)) }
}

// MCU-side opto helpers (x in [6, 18]); explicit absolute coordinates
const MCU_POS: Record<string, { pcbX: number; pcbY: number; pcbRotation: number }> = {
  C7: { pcbX: 9, pcbY: 15.5, pcbRotation: 90 },
  R13: { pcbX: 13, pcbY: 15.5, pcbRotation: 90 },
  R18: { pcbX: 17, pcbY: 15.5, pcbRotation: 90 },
  LD3: { pcbX: 17, pcbY: 19.5, pcbRotation: 90 },
  R14: { pcbX: 9, pcbY: -15.5, pcbRotation: 90 },
  R19: { pcbX: 13, pcbY: -15.5, pcbRotation: 90 },
  LD2: { pcbX: 13, pcbY: -19.5, pcbRotation: 90 },
}
const mpos = (ref: string) => {
  const p = MCU_POS[ref]
  return { ...p, schX: sch(p.pcbX) + 8, schY: sch(p.pcbY) }
}

const J = (...c: string[]) => ({ jlcpcb: c })

const Res = (ref: string, v: string, lcsc?: string, fp: any = "0805") => (
  <resistor name={ref} resistance={v} footprint={fp} {...pos(ref)} {...(lcsc ? { supplierPartNumbers: J(lcsc) } : {})} />
)
const Cap = (ref: string, v: string, lcsc?: string, fp: any = "0805") => (
  <capacitor name={ref} capacitance={v} footprint={fp} {...pos(ref)} {...(lcsc ? { supplierPartNumbers: J(lcsc) } : {})} />
)
// diodes: pin1 = anode (A), pin2 = cathode (C)
const Dio = (ref: string, mpn: string, lcsc?: string) => (
  <diode name={ref} footprint="sod123" manufacturerPartNumber={mpn} {...pos(ref)} {...(lcsc ? { supplierPartNumbers: J(lcsc) } : {})} />
)

const selector = (pin: string) => {
  const [ref, pad] = pin.split(".")
  return `.${ref} > .pin${pad}`
}

export const EmsSide = () => (
  <group name="ems">
    {/* ---- bus terminal, fuses, input filter (L1/L2), bridge D1-D4, clamp D5 ---- */}
    <Mstba2 name="P1" pcbX={-50} pcbY={0} pcbRotation={90} schX={-12} schY={0} />
    {/* fuses: 2-pad 0805 chips, pad1 = bus side, pad2 = inductor side */}
    <chip name="F1" footprint="0805" pcbX={tx(7.62)} pcbY={ty(19.37)} pcbRotation={90} schX={-9} schY={3} manufacturerPartNumber="FUSE 0805" />
    <chip name="F2" footprint="0805" pcbX={tx(7.62)} pcbY={ty(14.29)} pcbRotation={90} schX={-9} schY={-3} manufacturerPartNumber="FUSE 0805" />
    <Inductor3225 name="L1" {...pos("L1")} />
    <Inductor3225 name="L2" {...pos("L2")} />
    {Cap("C1", "68pF")}
    {Dio("D1", "BAT42")}
    {Dio("D2", "BAT42")}
    {Dio("D3", "BAT42")}
    {Dio("D4", "BAT42")}
    {Dio("D5", "BAT42")}
    {Dio("D7", "B5819W", "C8598")}
    <CapE5_10p5 name="C12" {...pos("C12")} />
    {Cap("C10", "10uF", "C15850")}

    {/* ---- RX comparator (U1A) and TX comparator (U1B), Q1 bus load ---- */}
    {Res("R1", "10k", "C17414")}
    {Res("R2", "68", undefined, <Res2010Footprint />)}
    {Res("R3", "68", undefined, <Res2010Footprint />)}
    {Res("R4", "68", undefined, <Res2010Footprint />)}
    {Cap("C2", "10uF", "C15850")}
    {Cap("C3", "1nF", "C46653")}
    {Cap("C4", "1.5nF")}
    {Cap("C5", "10nF", "C1710")}
    {Cap("C6", "100nF", "C49678")}
    {Res("R5", "390", "C17655")}
    {Res("R6", "47k", "C17713")}
    {Res("R7", "10k", "C17414")}
    {Res("R8", "100k", "C149504")}
    {Res("R9", "4.7k", "C17673")}
    {Res("R10", "470", "C17710")}
    {Res("R11", "4.7k", "C17673")}
    {Dio("D6", "1N4148W", "C81598")}
    {/* LM393 SOIC-8: 1 OUTA 2 IN-A 3 IN+A 4 GND 5 IN+B 6 IN-B 7 OUTB 8 VCC (pad numbers = datasheet) */}
    <chip
      name="U1"
      footprint="soic8"
      manufacturerPartNumber="LM393DR"
      supplierPartNumbers={J("C7955")}
      pinLabels={{ pin1: ["OUTA"], pin2: ["INA_N"], pin3: ["INA_P"], pin4: ["GND"], pin5: ["INB_P"], pin6: ["INB_N"], pin7: ["OUTB"], pin8: ["VCC"] }}
      schPinArrangement={{
        leftSide: { direction: "top-to-bottom", pins: ["INA_P", "INA_N", "INB_P", "INB_N"] },
        rightSide: { direction: "top-to-bottom", pins: ["VCC", "OUTA", "OUTB", "GND"] },
      }}
      {...pos("U1")}
      pcbRotation={0}
    />
    {/* Q1 MMBT3904 SOT-23: pad 1 = B, 2 = E, 3 = C (chip so pad numbers equal package pins) */}
    <chip
      name="Q1"
      footprint="sot23"
      manufacturerPartNumber="MMBT3904"
      supplierPartNumbers={J("C20526")}
      pinLabels={{ pin1: ["B"], pin2: ["E"], pin3: ["C"] }}
      {...pos("Q1")}
    />

    {/* ---- buck converter U2 JW5017S, L3, 5 V rail, power LED ---- */}
    {/* JW5017S SOT-23-6: 1 BST 2 GND 3 FB 4 EN 5 VIN 6 SW */}
    <chip
      name="U2"
      footprint="sot23_6"
      manufacturerPartNumber="JW5017S"
      pinLabels={{ pin1: ["BST"], pin2: ["GND"], pin3: ["FB"], pin4: ["EN"], pin5: ["VIN"], pin6: ["SW"] }}
      schPinArrangement={{
        leftSide: { direction: "top-to-bottom", pins: ["VIN", "EN", "BST"] },
        rightSide: { direction: "top-to-bottom", pins: ["SW", "FB", "GND"] },
      }}
      {...pos("U2")}
      pcbRotation={0}
    />
    <Inductor0520 name="L3" {...pos("L3")} />
    {Res("R12", "6.8k", "C17772")}
    {Res("R15", "1.3k")}
    {Res("R16", "100k", "C149504")}
    {Cap("C9", "100nF", "C49678")}
    {Cap("C11", "22uF", "C12891", "1206")}
    {Cap("C8", "100nF", "C49678")}
    {Cap("C13", "100nF", "C49678")}
    {Res("R17", "1.2k", "C17379")}
    <led name="LD1" footprint="0805" color="red" supplierPartNumbers={J("C84256")} {...pos("LD1")} />

    {/* ---- optocouplers on the barrier (x = 0), slot/cutout is added in index.circuit.tsx ---- */}
    {/* OC1 6N137: pins 1-4 (LED, EMS) at x<0, pins 5-8 (MCU) at x>0 */}
    <Opto6N137 name="OC1" pcbX={0} pcbY={8} schX={sch(0)} schY={sch(8) + 2} />
    {/* OC2 6N136: LED side (2,3) is MCU side, output side (5,6,8) is EMS -> rotated 180 deg */}
    <Opto6N136 name="OC2" pcbX={0} pcbY={-8} pcbRotation={180} schX={sch(0)} schY={sch(-8) - 2} />

    {/* ---- MCU-side opto helpers ---- */}
    <capacitor name="C7" capacitance="100nF" footprint="0805" supplierPartNumbers={J("C49678")} {...mpos("C7")} />
    <resistor name="R13" resistance="4.7k" footprint="0805" supplierPartNumbers={J("C17673")} {...mpos("R13")} />
    <resistor name="R14" resistance="270" footprint="0805" supplierPartNumbers={J("C17697")} {...mpos("R14")} />
    <resistor name="R18" resistance="1.2k" footprint="0805" supplierPartNumbers={J("C17379")} {...mpos("R18")} />
    <resistor name="R19" resistance="1.2k" footprint="0805" supplierPartNumbers={J("C17379")} {...mpos("R19")} />
    <led name="LD2" footprint="0805" color="green" {...mpos("LD2")} />
    <led name="LD3" footprint="0805" color="green" {...mpos("LD3")} />

    {/* ---- connectivity (V1 netlist) ---- */}
    {Object.entries(NETS).flatMap(([net, pins]) =>
      pins.map((p) => <trace key={`${net}-${p}`} from={selector(p)} to={`net.${net}`} />),
    )}
  </group>
)

export default EmsSide
