// USB-C 16-pin USB2.0 receptacle, HRO TYPE-C-31-M-12 (JLCPCB C165948).
// Shared ports: A/B duplicates are tied to one port (GND, VBUS, DP, DN).
// Local origin = centre of the 12-pad signal row; mating face toward +Y.
// Pad X positions are the standard 16P pattern (0.5 mm signal pitch, 0.8 mm
// to power pads). Y offsets / shell hole sizes are APPROXIMATE: verify against
// the HRO drawing or `tsci import C165948` (needs jlcsearch access) before fab.
import type { ChipProps } from "tscircuit"

export const UsbC16Footprint = () => {
  const row: [number, string, number][] = [
    [-3.2, "pin1", 0.6], [-2.4, "pin2", 0.6], [-1.75, "pin8", 0.3], [-1.25, "pin3", 0.3],
    [-0.75, "pin6", 0.3], [-0.25, "pin5", 0.3], [0.25, "pin6", 0.3], [0.75, "pin5", 0.3],
    [1.25, "pin7", 0.3], [1.75, "pin4", 0.3], [2.4, "pin2", 0.6], [3.2, "pin1", 0.6],
  ]
  return (
    <footprint>
      {row.map(([x, hint, w], i) => (
        <smtpad key={i} portHints={[hint]} shape="rect" width={`${w}mm`} height="1.15mm" pcbX={x} pcbY={0} />
      ))}
      {/* shell legs: front pair (near mating face) and rear pair */}
      {[-4.32, 4.32].map((x) => (
        <platedhole key={`f${x}`} portHints={["pin9"]} shape="pill" pcbX={x} pcbY={4.5}
          outerWidth="1.0mm" outerHeight="2.1mm" holeWidth="0.6mm" holeHeight="1.7mm" />
      ))}
      {[-4.32, 4.32].map((x) => (
        <platedhole key={`r${x}`} portHints={["pin9"]} shape="pill" pcbX={x} pcbY={0}
          outerWidth="1.0mm" outerHeight="1.6mm" holeWidth="0.6mm" holeHeight="1.2mm" />
      ))}
      <silkscreenpath route={[{ x: -4.47, y: -1.0 }, { x: 4.47, y: -1.0 }, { x: 4.47, y: 6.35 }, { x: -4.47, y: 6.35 }, { x: -4.47, y: -1.0 }]} />
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
