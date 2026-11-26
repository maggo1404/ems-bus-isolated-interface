// EMS side of the isolated EMS-bus interface (V1 netlist 1:1, see docs/netlist_v1.json).
// Contains everything of V1 except P2, incl. OC1/OC2 and the MCU-side opto helpers
// (R13, R14, R18, R19, LD2, LD3, C7).  Net names follow docs/DESIGN_SPEC.md.
import { Opto6N137, Opto6N136 } from "../lib/opto_so8_gw300"
import { DiodeKA, DiodeAK, LedRed, LedYellow } from "../lib/diodes"
import { traceWidth } from "../lib/netclass"
import { Soic8Lm393Footprint } from "../lib/soic8_lm393"
import { PartDot, CathodeBar } from "../lib/silk"
import { Mstba2, CapE5_10p5, Inductor3225, Inductor0520, Res2010Footprint } from "../lib/thtparts"

// ---------------------------------------------------------------------------
// Net table: net name -> physical pad connections "Ref.pad" (V1 pad numbers;
// diode/LED: pad 1 = cathode C, pad 2 = anode A; C12 +=1 -=2).  Pad N is always port `pinN` in tscircuit.
// ---------------------------------------------------------------------------
const NETS: Record<string, string[]> = {
  // EMS side
  V5_EMS: ["C6.2", "C8.1", "C11.1", "C13.2", "L3.1", "OC2.8", "R9.2", "R10.2", "R11.2", "R12.2", "R17.2", "U1.8"],
  GND_EMS: ["C30.1", "C4.1", "C5.1", "C6.1", "C8.2", "C10.1", "C11.2", "C12.2", "C14.2", "C13.1", "D2.2", "D4.2", "D5.2", "D6.1", "LD1.1", "OC2.5", "Q1.2", "R8.1", "R15.1", "U1.4", "U2.2"],
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
  EMS_N27: ["LD1.2", "R17.1"],
  EMS_N29: ["R16.2", "U2.4"],
  EMS_N3: ["C1.1", "D1.2", "D2.1", "L2.2"],
  EMS_N4: ["C1.2", "D3.2", "D4.1", "L1.2"],
  EMS_N5: ["F2.1", "P1.2"],
  EMS_N6: ["D1.1", "D3.1", "D5.1", "D7.2", "R1.1", "R2.1"],
  EMS_N7: ["D6.2", "R5.1", "R6.1", "R7.1", "U1.5"],
  EMS_N8: ["C2.1", "C3.1", "R1.2", "R5.2"],
  EMS_N9: ["C2.2", "R6.2", "U1.3"],
  EMS_VIN: ["C10.2", "C30.2", "C12.1", "C14.1", "D7.1", "R16.1", "U2.5"],
  // MCU side (shared with src/mcu-side.tsx through these net names)
  GND: ["C7.1", "OC1.5"],
  MCU_RX: ["LD3.1", "OC1.6", "R13.1"],
  MCU_TX: ["LD2.1", "OC2.3"],
  V3V3: ["C7.2", "OC1.7", "OC1.8", "R13.2", "R14.1", "R18.2", "R19.1"],
  MCU_N19: ["OC2.2", "R14.2"],
  MCU_N20: ["LD2.2", "R19.2"],
  MCU_N24: ["LD3.2", "R18.1"],
}

// ---------------------------------------------------------------------------
// Placement: V1 board coordinates (docs/netlist_v1.md "Layout V1") mapped to the
// V2 board (centre 0,0, Y up): OC at x = 0, x stretched 0.95, y stretched 1.35.
// ---------------------------------------------------------------------------
const tx = (x: number) => +((x - 7.62) * 0.88 - 40.5).toFixed(2)
const ty = (y: number) => +((y - 16.83) * 1.35).toFixed(2)
const sch = (v: number) => +(v * 0.3).toFixed(2)

type P = { x: number; y: number; r?: number }
// V1 (x, y, rot) per ref
const V1: Record<string, P> = {
  L1: { x: 10.79, y: 20.0, r: 270 }, L2: { x: 10.79, y: 12.38, r: 270 },
  C1: { x: 14.76, y: 9.54, r: 90 },
  D1: { x: 16.51, y: 5.71, r: 180 }, D2: { x: 16.51, y: 1.91 }, D3: { x: 16.51, y: 13.34, r: 180 }, D4: { x: 16.51, y: 17.14 },
  D5: { x: 21.59, y: 3.81, r: 90 },
  R1: { x: 22.54, y: 13.34 }, R2: { x: 21.59, y: 19.05, r: 90 }, R3: { x: 25.4, y: 19.05, r: 90 }, R4: { x: 29.21, y: 19.05, r: 90 },
  C2: { x: 28.57, y: 8.26 }, C3: { x: 28.57, y: 11.43 }, R5: { x: 24.77, y: 10.48, r: 90 },
  U1: { x: 36.83, y: 9.53, r: 90 }, D6: { x: 24.77, y: 3.81, r: 90 },
  R6: { x: 28.57, y: 5.71 }, R7: { x: 28.57, y: 1.91 }, R8: { x: 28.57, y: 13.97 },
  R9: { x: 43.81, y: 12.7, r: 90 }, Q1: { x: 42.7, y: 16.85, r: 90 }, C4: { x: 42.6, y: 20.32 },
  C5: { x: 43.81, y: 4.39, r: 90 }, C6: { x: 35.81, y: 5.71 }, R10: { x: 43.0, y: 24.13 },
  D7: { x: 16.51, y: 20.32 },
  U2: { x: 34.92, y: 24.77, r: 90 }, R12: { x: 39.6, y: 23.2, r: 90 }, R15: { x: 39.6, y: 19.7, r: 90 },
  C9: { x: 30.2, y: 24.45, r: 90 }, R16: { x: 35.24, y: 28.89 }, C10: { x: 32.07, y: 28.57, r: 90 }, C11: { x: 28.45, y: 34.98 },
  F1: { x: 7.62, y: 19.37, r: 90 }, F2: { x: 7.62, y: 14.29, r: 90 }, R17: { x: 43.0, y: 28.89 },
  L3: { x: 26.99, y: 27.62 }, LD1: { x: 46.67, y: 30.8 }, C12: { x: 14.61, y: 27.62, r: 90 },
  C8: { x: 43.0, y: 26.35 }, C13: { x: 47.62, y: 3.17, r: 90 },
}
// layout overrides (enclosure layout, FIX_LIST #22/#10): absolute board coordinates
const OVR: Record<string, P> = {
  C12: { x: -32.5, y: 22.5, r: 90 }, C14: { x: -13.5, y: -24.3, r: 0 }, C11: { x: -25.0, y: 19.0, r: 90 }, C1: { x: -28.0, y: -10.5, r: 90 }, C10: { x: -12.9, y: 11.1, r: 180 },
  // buck: C10 + C30 directly at U2 VIN (pin 5, x -15.18), L3 close to SW (R5 M2)
  C30: { x: -12.9, y: 12.9, r: 180 }, L3: { x: -20.6, y: 14.57, r: 0 }, R10: { x: -8.37, y: 9.86, r: 0 }, C8: { x: -8.37, y: 12.85, r: 0 },
  R16: { x: -14.6, y: 16.3, r: 0 },
  C13: { x: -7.0, y: -8.3, r: 90 }, R11: { x: -9.0, y: -11.57, r: 90 }, LD1: { x: -8, y: 24, r: 0 }, R17: { x: -14, y: 24, r: 0 },
}
const pos = (ref: string) => {
  const o = OVR[ref]
  const p = V1[ref]
  const x = o ? o.x : tx(p.x), y = o ? o.y : ty(p.y), r = o ? o.r ?? 0 : p.r ?? 0
  return { pcbX: x, pcbY: y, pcbRotation: r, schX: sch(x), schY: sch(y) }
}

// MCU-side opto helpers (x in [6, 18]); explicit absolute coordinates
const MCU_POS: Record<string, { pcbX: number; pcbY: number; pcbRotation: number }> = {
  C7: { pcbX: 8.5, pcbY: 8.0, pcbRotation: 90 },
  R13: { pcbX: 12.5, pcbY: 8.2, pcbRotation: 90 },
  R18: { pcbX: 16.0, pcbY: 8.2, pcbRotation: 90 },
  LD3: { pcbX: 16.0, pcbY: 13.6, pcbRotation: 90 },
  R14: { pcbX: 9.0, pcbY: -9.5, pcbRotation: 90 },
  R19: { pcbX: 12.5, pcbY: -9.5, pcbRotation: 90 },
  LD2: { pcbX: 12.5, pcbY: -13.8, pcbRotation: 90 },
}
const mpos = (ref: string) => {
  const p = MCU_POS[ref]
  return { ...p, schX: sch(p.pcbX) + 8, schY: sch(p.pcbY) }
}

const GND_VIAS: [number, number][] = [[-19.0, 10.0], [-12.6, 16.6], [-27.4, 22.4], [-12.4, 1.2], [-10.6, 6.7], [-10.9, 11.25]]
const J = (...c: string[]) => ({ jlcpcb: c })
// refdes of the passives, diodes, fuses and small ICs are not printed: silk text must be >= 1.0 mm high (JLC, R7 M1) and does not fit between the
// pads (docs/img/assembly.png has the refdes). Polarity/pin 1 is marked by cathode bars / dots instead (lib/silk.tsx)
const NOREF = { silkscreenTextVisibility: "hidden" } as const

const Res = (ref: string, v: string, lcsc?: string, fp: any = "0805") => (
  <resistor name={ref} resistance={v} footprint={fp} pcbStyle={NOREF} {...pos(ref)} {...(lcsc ? { supplierPartNumbers: J(lcsc) } : {})} />
)
const Cap = (ref: string, v: string, lcsc?: string, fp: any = "0805", extra: any = {}) => (
  <capacitor name={ref} capacitance={v} footprint={fp} pcbStyle={NOREF} {...pos(ref)} {...extra} {...(lcsc ? { supplierPartNumbers: J(lcsc) } : {})} />
)
// Diodes: D1-D5 BAT42W (JLC pad 1 = ANODE), D6/D7 pad 1 = cathode; LD1 red pad 1 = K, LD2/LD3 green pad 1 = A.
// The NETS table keeps the V1 convention pad 1 = cathode, pad 2 = anode; the pads of the parts whose
// JLC footprint is numbered the other way round are swapped in selector().
const PAD_SWAP = new Set(["D1", "D2", "D3", "D4", "D5", "LD2", "LD3"])
const Dio = (ref: string, mpn: string, lcsc: string) => {
  const D = PAD_SWAP.has(ref) ? DiodeAK : DiodeKA
  const p = pos(ref)
  // cathode bar between the pads: SOD-123 pad 1 is at local -x, pad 2 at +x; D1-D5 (BAT42W) cathode = pad 2, D6/D7 cathode = pad 1
  return (
    <>
      <D name={ref} manufacturerPartNumber={mpn} supplierPartNumbers={J(lcsc)} pcbStyle={NOREF} {...p} />
      <CathodeBar part={p} side={PAD_SWAP.has(ref) ? 1 : -1} />
    </>
  )
}

const selector = (pin: string) => {
  const [ref, pad0] = pin.split(".")
  const pad = PAD_SWAP.has(ref) ? { "1": "2", "2": "1" }[pad0] : pad0
  return `.${ref} > .pin${pad}`
}

export const EmsSide = () => (
  <group name="ems" pcbX={0} pcbY={0}>
    {/* ---- bus terminal, fuses, input filter (L1/L2), bridge D1-D4, clamp D5 ---- */}
    <Mstba2 name="P1" pcbX={-44.1} pcbY={0} pcbRotation={270} schX={-12} schY={0} />
    {/* fuses: 2-pad 0805 chips, pad1 = bus side, pad2 = inductor side */}
    <chip name="F1" pcbStyle={NOREF} footprint="0805" pcbX={tx(7.62)} pcbY={ty(19.37)} pcbRotation={90} schX={-9} schY={3} manufacturerPartNumber="BSMD0805-050-24V" supplierPartNumbers={J("C910822")} />
    <chip name="F2" pcbStyle={NOREF} footprint="0805" pcbX={tx(7.62)} pcbY={ty(14.29)} pcbRotation={270} schX={-9} schY={-3} manufacturerPartNumber="BSMD0805-050-24V" supplierPartNumbers={J("C910822")} />
    <Inductor3225 name="L1" {...pos("L1")} />
    <Inductor3225 name="L2" {...pos("L2")} />
    {Cap("C1", "68pF", "C107120")}
    {Dio("D1", "BAT42W", "C22466362")}
    {Dio("D2", "BAT42W", "C22466362")}
    {Dio("D3", "BAT42W", "C22466362")}
    {Dio("D4", "BAT42W", "C22466362")}
    {Dio("D5", "BAT42W", "C22466362")}
    {Dio("D7", "B5819W", "C8598")}
    {/* C12 + C14: 2 x 1000 uF/25 V SMD electrolytic in parallel (replaces the V1 2200 uF), rotated 90 deg */}
    <CapE5_10p5 name="C12" {...pos("C12")} />
    <CapE5_10p5 name="C14" {...pos("C14")} schY={sch(-24.3) + 3} />
    {/* the hand-routed VIN pin -> C10 trace (1.5 mm) is longer than tscircuit's automatic 1 mm decoupling limit; its GND leg is routed to the pour (R5 M2) */}
    {Cap("C10", "10uF", "C15850", "0805", { maxDecouplingTraceLength: 20 })}
    {Cap("C30", "100nF", "C49678", "0805", {})}

    {/* ---- RX comparator (U1A) and TX comparator (U1B), Q1 bus load ---- */}
    {Res("R1", "10k", "C17414")}
    {Res("R2", "68", "C53284030", <Res2010Footprint />)}
    {Res("R3", "68", "C53284030", <Res2010Footprint />)}
    {Res("R4", "68", "C53284030", <Res2010Footprint />)}
    {Cap("C2", "10uF", "C15850")}
    {Cap("C3", "1nF", "C46653")}
    {Cap("C4", "1.5nF", "C1717")}
    {Cap("C5", "4.7nF", "C1744")}
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
      footprint={<Soic8Lm393Footprint />}
      manufacturerPartNumber="LM393DR"
      supplierPartNumbers={J("C7955")}
      pinLabels={{ pin1: ["OUTA"], pin2: ["INA_N"], pin3: ["INA_P"], pin4: ["GND"], pin5: ["INB_P"], pin6: ["INB_N"], pin7: ["OUTB"], pin8: ["VCC"] }}
      schPinArrangement={{
        leftSide: { direction: "top-to-bottom", pins: ["INA_P", "INA_N", "INB_P", "INB_N"] },
        rightSide: { direction: "top-to-bottom", pins: ["VCC", "OUTA", "OUTB", "GND"] },
      }}
      {...pos("U1")}
      pcbRotation={270}
    />
    {/* Q1 BC817-40 SOT-23 (EasyEDA C20069155 verified): pad 1 = B, 2 = E, 3 = C (chip so pad numbers equal package pins) */}
    <PartDot part={pos("Q1")} lx={-2.35} ly={0.95} />
    <chip
      name="Q1"
      pcbStyle={NOREF}
      footprint="sot23"
      manufacturerPartNumber="BC817-40"
      supplierPartNumbers={J("C20069155")}
      pinLabels={{ pin1: ["B"], pin2: ["E"], pin3: ["C"] }}
      {...pos("Q1")}
    />

    {/* ---- buck converter U2 JW5017S, L3, 5 V rail, power LED ---- */}
    {/* JW5017S SOT-23-6: 1 BST 2 GND 3 FB 4 EN 5 VIN 6 SW */}
    <PartDot part={{ ...pos("U2"), pcbRotation: 0 }} lx={-2.35} ly={0.95} />
    <chip
      name="U2"
      pcbStyle={NOREF}
      footprint="sot23_6"
      manufacturerPartNumber="JW5017S"
      supplierPartNumbers={J("C371172")}
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
    {Res("R15", "1.3k", "C17384")}
    {Res("R16", "100k", "C149504")}
    {Cap("C9", "100nF", "C49678")}
    {Cap("C11", "22uF", "C12891", "1206")}
    {Cap("C8", "100nF", "C49678")}
    {Cap("C13", "100nF", "C49678")}
    {Res("R17", "1.2k", "C17379")}
    <LedRed name="LD1" {...pos("LD1")} />

    {/* ---- optocouplers on the barrier (x = 0), slot/cutout is added in index.circuit.tsx ---- */}
    {/* OC1 6N137: pins 1-4 (LED, EMS) at x<0, pins 5-8 (MCU) at x>0 */}
    <Opto6N137 name="OC1" pcbX={0} pcbY={8} schX={sch(0)} schY={sch(8) + 2} />
    {/* OC2 6N136: LED side (2,3) is MCU side, output side (5,6,8) is EMS -> rotated 180 deg */}
    <Opto6N136 name="OC2" pcbX={0} pcbY={-8} pcbRotation={180} schX={sch(0)} schY={sch(-8) - 2} />

    {/* ---- MCU-side opto helpers ---- */}
    <capacitor name="C7" pcbStyle={NOREF} capacitance="100nF" footprint="0805" supplierPartNumbers={J("C49678")} {...mpos("C7")} />
    <resistor name="R13" pcbStyle={NOREF} resistance="3.3k" footprint="0805" supplierPartNumbers={J("C26010")} {...mpos("R13")} />
    <resistor name="R14" pcbStyle={NOREF} resistance="150" footprint="0805" supplierPartNumbers={J("C17471")} {...mpos("R14")} />
    <resistor name="R18" pcbStyle={NOREF} resistance="330" footprint="0805" supplierPartNumbers={J("C17630")} {...mpos("R18")} />
    <resistor name="R19" pcbStyle={NOREF} resistance="330" footprint="0805" supplierPartNumbers={J("C17630")} {...mpos("R19")} />
    <LedYellow name="LD2" {...mpos("LD2")} />
    <LedYellow name="LD3" {...mpos("LD3")} />

    {/* GND_EMS stitching vias next to the buck / feedback pads: the router connects the pad to the via, the via drops into the
        bottom GND_EMS pour (keeps the congested bus/buck area routable, FIX_LIST #10) */}
    {GND_VIAS.map(([x, y], i) => (
      <via key={`gv${i}`} name={`VG${i}`} pcbX={x} pcbY={y} fromLayer="top" toLayer="bottom" holeDiameter="0.3mm" outerDiameter="0.6mm" connectsTo="net.GND_EMS" />
    ))}

    {/* bridge rectifier: hand-routed 0.4 mm runs (FIX_LIST #8; the autorouter necks branches of multi-pin nets to 0.25 mm).
        pcbPath points are in the frame of the `from` part (D4/D2 are unrotated, centre x = -32.68):
        N4 = D4.K - D3.A - C1.2, N3 = D2.K - D1.A - C1.1 (right column x = -31.03), N6 = D3.K - D1.K (left column x = -34.33) */}
    <trace from="D4.pin2" to="C1.pin2" thickness="0.4mm" pcbPath={["D3.pin1", { x: 1.65, y: -10.01 }]} />
    <trace from="D2.pin2" to="C1.pin1" thickness="0.4mm" pcbPath={["D1.pin1", { x: 1.65, y: 8.73 }]} />
    <trace from="D3.pin2" to="D1.pin2" thickness="0.4mm" pcbPath={["D3.pin2"]} />
    <trace from="L1.pin2" to="D4.pin2" thickness="0.4mm" pcbPath={[{ x: 1.4, y: 5.31 }, { x: 3.86, y: 5.31 }]} />
    {/* N6 (rectified bus +): R1.1 - R2.1 and D7.K - R2.1;  N13 (Q1 collector): R4.2 - C4.2 - Q1.C (frame of R4: rot 90, centre -21.5/3.0);
        N26 (buck switch node): C9.2 - L3.2 - U2.SW */}
    <trace from="R1.pin1" to="R2.pin1" thickness="0.4mm" pcbPath={["R1.pin1"]} />
    <trace from="D7.pin2" to="R2.pin1" thickness="0.4mm" pcbPath={[{ x: 1.65, y: -1.41 }, { x: 3.88, y: -2.11 }]} />
    <trace from="R4.pin2" to="Q1.pin3" thickness="0.4mm"
      pcbPath={[{ x: 3.0, y: -0.7 }, { x: 3.0, y: -12.69 }, "C4.pin2", { x: 0, y: -12.69 }, { x: -0.6, y: -11.87 }]} />
    <trace from="C9.pin2" to="L3.pin2" thickness="0.4mm" pcbPath={["C9.pin2"]} />
    <trace from="U2.pin6" to="L3.pin2" thickness="0.4mm" pcbPath={[{ x: 1.3, y: 2.28 }, { x: -2.12, y: 2.28 }]} />

    {/* buck input: hand-routed VIN (0.5 mm) U2.VIN -> C10.2 -> C30.2, shorter than 2 mm, no vias (R5 M2); frame of U2 (centre -16.48/10.72) */}
    <trace from="U2.pin5" to="C10.pin2" thickness="0.5mm" pcbPath={[{ x: 2.48, y: 0 }]} />
    <trace from="C10.pin2" to="C30.pin2" thickness="0.5mm" pcbPath={["C10.pin2"]} />

    {/* ---- connectivity (V1 netlist) ---- */}
    {Object.entries(NETS).flatMap(([net, pins]) =>
      pins.map((p) => <trace key={`${net}-${p}`} from={selector(p)} to={`net.${net}`} thickness={traceWidth(net)} />),
    )}
  </group>
)

export default EmsSide
