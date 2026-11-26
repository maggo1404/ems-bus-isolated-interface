// 6N137 / 6N136 in SMD-8 gull-wing 300 mil ("SO8-GW300" in Eagle EMSinterface_V1.0.lbr).
// Pads copied from the Eagle lbr: x = +-4.69 mm (row pitch 9.38), pitch 2.54 mm
// (y = +-1.27, +-3.937), pad 1.0 x 1.27 mm. Pin1 top-left.
import type { ChipProps } from "tscircuit"

export const OptoSo8Gw300Footprint = () => {
  const ys = [3.937, 1.27, -1.27, -3.937]
  return (
    <footprint>
      {ys.map((y, i) => (
        <smtpad key={`l${i}`} portHints={[`pin${i + 1}`]} shape="rect" width="1.0mm" height="1.27mm" pcbX={-4.69} pcbY={y} />
      ))}
      {ys.map((y, i) => (
        <smtpad key={`r${i}`} portHints={[`pin${8 - i}`]} shape="rect" width="1.0mm" height="1.27mm" pcbX={4.69} pcbY={-y} />
      ))}
      <silkscreenpath route={[{ x: -3.0, y: 4.5 }, { x: 3.0, y: 4.5 }, { x: 3.0, y: -4.5 }, { x: -3.0, y: -4.5 }, { x: -3.0, y: 4.5 }]} />
      <silkscreentext text="1" pcbX={-2.3} pcbY={3.9} fontSize="0.8mm" />
    </footprint>
  )
}

// 6N137: 1 NC, 2 Anode, 3 Cathode, 4 NC, 5 GND, 6 Vout, 7 VE (enable), 8 VCC
export const Opto6N137 = (props: Partial<ChipProps> & { name: string }) => (
  <chip
    manufacturerPartNumber="6N137S"
    pinLabels={{ pin1: ["NC1"], pin2: ["ANODE"], pin3: ["CATHODE"], pin4: ["NC4"], pin5: ["GND"], pin6: ["VO"], pin7: ["VE"], pin8: ["VCC"] }}
    footprint={<OptoSo8Gw300Footprint />}
    schPinArrangement={{ leftSide: { direction: "top-to-bottom", pins: ["ANODE", "CATHODE"] }, rightSide: { direction: "top-to-bottom", pins: ["VCC", "VE", "VO", "GND"] } }}
    {...(props as any)}
  />
)
// 6N136: same pinout but pin 7 = VB (base), pin 6 = VO
export const Opto6N136 = (props: Partial<ChipProps> & { name: string }) => (
  <chip
    manufacturerPartNumber="6N136S"
    pinLabels={{ pin1: ["NC1"], pin2: ["ANODE"], pin3: ["CATHODE"], pin4: ["NC4"], pin5: ["GND"], pin6: ["VO"], pin7: ["VB"], pin8: ["VCC"] }}
    footprint={<OptoSo8Gw300Footprint />}
    schPinArrangement={{ leftSide: { direction: "top-to-bottom", pins: ["ANODE", "CATHODE"] }, rightSide: { direction: "top-to-bottom", pins: ["VCC", "VB", "VO", "GND"] } }}
    {...(props as any)}
  />
)
