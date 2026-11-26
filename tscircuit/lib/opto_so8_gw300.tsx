// 6N137 / 6N136 in SMD-8 gull-wing 300 mil ("SO8-GW300" in Eagle EMSinterface_V1.0.lbr).
// Verified (docs/FOOTPRINT_CHECK.md): rows at x = +-4.75 mm (9.5 mm centre-to-centre), pitch 2.54 mm
// (y = +-1.27, +-3.81), pads 1.8 (across) x 1.4 (along) mm; covers JLC C92651 / C336082 (9.09 mm rows).
// Pin1 top-left, pins 1-4 down the left column, 5-8 UP the right column (pin5 opposite pin4, pin8 opposite pin1;
// counter-clockwise like the EasyEDA C92651/C336082 footprint: pin1 (-3.81,-4.545) .. pin8 (-3.81,+4.545) in its frame).
import type { ChipProps } from "tscircuit"
import { Dot } from "./silk"

export const OptoSo8Gw300Footprint = () => {
  const ys = [3.81, 1.27, -1.27, -3.81]
  return (
    <footprint>
      {ys.map((y, i) => (
        <smtpad key={`l${i}`} portHints={[`pin${i + 1}`]} shape="rect" width="1.8mm" height="1.4mm" pcbX={-4.75} pcbY={y} />
      ))}
      {ys.map((y, i) => (
        <smtpad key={`r${i}`} portHints={[`pin${8 - i}`]} shape="rect" width="1.8mm" height="1.4mm" pcbX={4.75} pcbY={y} />
      ))}
      <silkscreenpath route={[{ x: -3.0, y: 4.5 }, { x: 3.0, y: 4.5 }, { x: 3.0, y: -4.5 }, { x: -3.0, y: -4.5 }, { x: -3.0, y: 4.5 }]} />
      {/* pin-1 dot above pad 1 (R7 m6) */}
      <Dot x={-4.75} y={5.3} />
    </footprint>
  )
}

// 6N137: 1 NC, 2 Anode, 3 Cathode, 4 NC, 5 GND, 6 Vout, 7 VE (enable), 8 VCC
export const Opto6N137 = (props: Partial<ChipProps> & { name: string }) => (
  <chip
    manufacturerPartNumber="6N137S-TA1-L"
    supplierPartNumbers={{ jlcpcb: ["C92651"] }}
    pinLabels={{ pin1: ["NC1"], pin2: ["ANODE"], pin3: ["CATHODE"], pin4: ["NC4"], pin5: ["GND"], pin6: ["VO"], pin7: ["VE"], pin8: ["VCC"] }}
    footprint={<OptoSo8Gw300Footprint />}
    schPinArrangement={{ leftSide: { direction: "top-to-bottom", pins: ["ANODE", "CATHODE"] }, rightSide: { direction: "top-to-bottom", pins: ["VCC", "VE", "VO", "GND"] } }}
    {...(props as any)}
  />
)
// 6N136: same pinout but pin 7 = VB (base), pin 6 = VO
export const Opto6N136 = (props: Partial<ChipProps> & { name: string }) => (
  <chip
    manufacturerPartNumber="6N136S-TA1-L"
    supplierPartNumbers={{ jlcpcb: ["C336082"] }}
    pinLabels={{ pin1: ["NC1"], pin2: ["ANODE"], pin3: ["CATHODE"], pin4: ["NC4"], pin5: ["GND"], pin6: ["VO"], pin7: ["VB"], pin8: ["VCC"] }}
    footprint={<OptoSo8Gw300Footprint />}
    // EMS side (VCC/VB/VO/GND) on the left, LED (MCU side) on the right: the symbol straddles the barrier, OC2 is mirrored w.r.t. OC1
    schPinArrangement={{ leftSide: { direction: "top-to-bottom", pins: ["VCC", "VB", "VO", "GND"] }, rightSide: { direction: "top-to-bottom", pins: ["ANODE", "CATHODE"] } }}
    {...(props as any)}
  />
)
