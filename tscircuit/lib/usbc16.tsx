// USB-C 16-pin USB2.0 receptacle, HRO TYPE-C-31-M-12 (JLCPCB C165948).
// Footprint verified against EasyEDA (docs/FOOTPRINT_CHECK.md section 2, "Option B"):
// local origin = centre of the 12-pad signal row, mating face toward +Y (body y = +0.23 ... +7.57).
// Every physical contact (A/B duplicates, shell legs) is its own port; they are tied together at netlist level.
import type { ChipProps } from "tscircuit"

export const UsbC16Footprint = () => {
  // [x, port, width] - EVERY physical contact has its own port (no shared portHints), see PINS below.
  const row: [number, string, number][] = [
    [-3.2, "pin1", 0.6], [-2.4, "pin2", 0.6], [-1.75, "pin3", 0.3], [-1.25, "pin4", 0.3],
    [-0.75, "pin5", 0.3], [-0.25, "pin6", 0.3], [0.25, "pin7", 0.3], [0.75, "pin8", 0.3],
    [1.25, "pin9", 0.3], [1.75, "pin10", 0.3], [2.4, "pin11", 0.6], [3.2, "pin12", 0.6],
  ]
  const legs: [number, number, string, number, number, number, number][] = [
    // x, y, port, outerW, outerH, holeW, holeH
    [-4.325, 0.768, "pin13", 1.2, 2.0, 0.8, 1.5], [4.325, 0.768, "pin14", 1.2, 2.0, 0.8, 1.5],
    [-4.325, 4.948, "pin15", 1.2, 1.8, 0.8, 1.2], [4.325, 4.948, "pin16", 1.2, 1.8, 0.8, 1.2],
  ]
  return (
    <footprint>
      {row.map(([x, hint, w], i) => (
        <smtpad key={i} portHints={[hint]} shape="rect" width={`${w}mm`} height="1.3mm" pcbX={x} pcbY={0} />
      ))}
      {/* shell legs: rear pair (near SMD row) and front pair (near mating face), one port each */}
      {legs.map(([x, y, hint, ow, oh, hw, hh]) => (
        <platedhole key={hint} portHints={[hint]} shape="pill" pcbX={x} pcbY={y}
          outerWidth={`${ow}mm`} outerHeight={`${oh}mm`} holeWidth={`${hw}mm`} holeHeight={`${hh}mm`} />
      ))}
      {/* 2 x 0.6 mm NPTH positioning pegs */}
      <hole diameter="0.6mm" pcbX={-2.9} pcbY={1.268} />
      <hole diameter="0.6mm" pcbX={2.9} pcbY={1.268} />
      {/* U-shaped outline outside the shell legs (x = +-5.2), open towards the SMD row, 0.27 mm inside the mating face (= board edge) */}
      <silkscreenpath route={[{ x: -5.2, y: 0.0 }, { x: -5.2, y: 7.3 }, { x: 5.2, y: 7.3 }, { x: 5.2, y: 0.0 }]} />
    </footprint>
  )
}

/** Ports (pad order left to right with the mating face at +Y):
 *  pin1 GND_L, pin2 VBUS_L, pin3 CC2, pin4 SBU1, pin5 DP_L, pin6 DN_L, pin7 DP_R, pin8 DN_R, pin9 CC1, pin10 SBU2,
 *  pin11 VBUS_R, pin12 GND_R, pin13..16 SH1..SH4 (shell legs).  The physical pairs (both DP, both DN, both VBUS,
 *  both GND, all shell legs) are joined by explicit traces to the same net in src/mcu-side.tsx. */
export const UsbC16 = (props: Partial<ChipProps> & { name: string }) => (
  <chip
    manufacturerPartNumber="TYPE-C-31-M-12"
    supplierPartNumbers={{ jlcpcb: ["C165948"] }}
    pinLabels={{
      pin1: ["GND_L"], pin2: ["VBUS_L"], pin3: ["CC2"], pin4: ["SBU1"], pin5: ["DP_L"], pin6: ["DN_L"],
      pin7: ["DP_R"], pin8: ["DN_R"], pin9: ["CC1"], pin10: ["SBU2"], pin11: ["VBUS_R"], pin12: ["GND_R"],
      pin13: ["SH1"], pin14: ["SH2"], pin15: ["SH3"], pin16: ["SH4"],
    }}
    footprint={<UsbC16Footprint />}
    schPinArrangement={{
      leftSide: { direction: "top-to-bottom", pins: ["VBUS_L", "VBUS_R", "DP_L", "DP_R", "DN_L", "DN_R", "CC1", "CC2"] },
      rightSide: { direction: "top-to-bottom", pins: ["SBU1", "SBU2", "SH1", "SH2", "SH3", "SH4", "GND_L", "GND_R"] },
    }}
    {...(props as any)}
  />
)
