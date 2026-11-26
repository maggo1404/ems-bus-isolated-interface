// USB-C 16-pin USB2.0 receptacle, HRO TYPE-C-31-M-12 (JLCPCB C165948).
// Footprint verified against EasyEDA (docs/FOOTPRINT_CHECK.md section 2, "Option B"):
// local origin = centre of the 12-pad signal row, mating face toward +Y (body y = +0.23 ... +7.57).
// A/B duplicates share one port (GND, VBUS, DP, DN).
import type { ChipProps } from "tscircuit"

export const UsbC16Footprint = () => {
  // [x, port, width]  (EasyEDA order mirrored in X for mating face at +Y)
  const row: [number, string, number][] = [
    [-3.2, "pin1", 0.6], [-2.4, "pin2", 0.6], [-1.75, "pin4", 0.3], [-1.25, "pin7", 0.3],
    [-0.75, "pin5", 0.3], [-0.25, "pin6", 0.3], [0.25, "pin5", 0.3], [0.75, "pin6", 0.3],
    [1.25, "pin3", 0.3], [1.75, "pin8", 0.3], [2.4, "pin2", 0.6], [3.2, "pin1", 0.6],
  ]
  return (
    <footprint>
      {row.map(([x, hint, w], i) => (
        <smtpad key={i} portHints={[hint]} shape="rect" width={`${w}mm`} height="1.3mm" pcbX={x} pcbY={0} />
      ))}
      {/* shell legs: rear pair (near SMD row) and front pair (near mating face) */}
      {[-4.325, 4.325].map((x) => (
        <platedhole key={`r${x}`} portHints={["pin9"]} shape="pill" pcbX={x} pcbY={0.768}
          outerWidth="1.2mm" outerHeight="2.0mm" holeWidth="0.8mm" holeHeight="1.5mm" />
      ))}
      {[-4.325, 4.325].map((x) => (
        <platedhole key={`f${x}`} portHints={["pin9"]} shape="pill" pcbX={x} pcbY={4.948}
          outerWidth="1.2mm" outerHeight="1.8mm" holeWidth="0.8mm" holeHeight="1.2mm" />
      ))}
      {/* 2 x 0.6 mm NPTH positioning pegs */}
      <hole diameter="0.6mm" pcbX={-2.9} pcbY={1.268} />
      <hole diameter="0.6mm" pcbX={2.9} pcbY={1.268} />
      <silkscreenpath route={[{ x: -4.47, y: 0.23 }, { x: 4.47, y: 0.23 }, { x: 4.47, y: 7.57 }, { x: -4.47, y: 7.57 }, { x: -4.47, y: 0.23 }]} />
    </footprint>
  )
}

export const UsbC16 = (props: Partial<ChipProps> & { name: string }) => (
  <chip
    manufacturerPartNumber="TYPE-C-31-M-12"
    supplierPartNumbers={{ jlcpcb: ["C165948"] }}
    pinLabels={{ pin1: ["GND"], pin2: ["VBUS"], pin3: ["CC1"], pin4: ["CC2"], pin5: ["DP"], pin6: ["DN"], pin7: ["SBU1"], pin8: ["SBU2"], pin9: ["SHELL"] }}
    footprint={<UsbC16Footprint />}
    schPinArrangement={{ leftSide: { direction: "top-to-bottom", pins: ["VBUS", "DP", "DN", "CC1", "CC2"] }, rightSide: { direction: "top-to-bottom", pins: ["SBU1", "SBU2", "SHELL", "GND"] } }}
    {...(props as any)}
  />
)
