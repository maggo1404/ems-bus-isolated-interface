// ESP32-S3-WROOM-1-N16R8 (JLCPCB C2913202), module 18.0 x 25.5 mm.
// Pad numbering per Espressif datasheet (40 pads + EPAD, here split in 9 ports pin41..49): 1-14 left (top->bottom),
// 15-26 bottom (left->right), 27-40 right (bottom->top), 41 = GND thermal pad.
// Local origin = module centre, antenna end at +Y (top). Land pattern follows
// the datasheet/KiCad lib (0.9 x 1.5 mm pads, 1.27 mm pitch); EPAD position is
// verified against EasyEDA C2913202 (docs/FOOTPRINT_CHECK.md): 3x3 EPAD at (-1.5,-2.47), bottom row y=-12.54.
import type { ChipProps } from "tscircuit"
import { Dot } from "./silk"

export const ESP32S3_PINLABELS = {
  pin1: ["GND1"], pin2: ["V3V3"], pin3: ["EN"], pin4: ["IO4"], pin5: ["IO5"],
  pin6: ["IO6"], pin7: ["IO7"], pin8: ["IO15"], pin9: ["IO16"], pin10: ["IO17"],
  pin11: ["IO18"], pin12: ["IO8"], pin13: ["IO19"], pin14: ["IO20"],
  pin15: ["IO3"], pin16: ["IO46"], pin17: ["IO9"], pin18: ["IO10"], pin19: ["IO11"],
  pin20: ["IO12"], pin21: ["IO13"], pin22: ["IO14"], pin23: ["IO21"], pin24: ["IO47"],
  pin25: ["IO48"], pin26: ["IO45"], pin27: ["IO0"], pin28: ["IO35"], pin29: ["IO36"],
  pin30: ["IO37"], pin31: ["IO38"], pin32: ["IO39"], pin33: ["IO40"], pin34: ["IO41"],
  pin35: ["IO42"], pin36: ["RXD0"], pin37: ["TXD0"], pin38: ["IO2"], pin39: ["IO1"],
  pin40: ["GND2"],
  // EPAD: 9 separate 0.9 mm pads, one port each (pin41..pin49), all tied to GND explicitly in src/mcu-side.tsx
  pin41: ["GND_EP1"], pin42: ["GND_EP2"], pin43: ["GND_EP3"], pin44: ["GND_EP4"], pin45: ["GND_EP5"],
  pin46: ["GND_EP6"], pin47: ["GND_EP7"], pin48: ["GND_EP8"], pin49: ["GND_EP9"],
} as const

const P = 1.27
export const Esp32S3Footprint = () => {
  const pads: any[] = []
  // left: pins 1..14, y from +? (top, antenna side) downwards
  for (let i = 0; i < 14; i++) {
    pads.push(
      <smtpad key={`l${i}`} portHints={[`pin${1 + i}`]} shape="rect" width="1.5mm" height="0.9mm"
        pcbX={-8.75} pcbY={5.26 - i * P} />,
    )
  }
  // bottom: pins 15..26 left->right
  for (let i = 0; i < 12; i++) {
    pads.push(
      <smtpad key={`b${i}`} portHints={[`pin${15 + i}`]} shape="rect" width="0.9mm" height="1.5mm"
        pcbX={-6.985 + i * P} pcbY={-12.54} />,
    )
  }
  // right: pins 27..40 bottom->top
  for (let i = 0; i < 14; i++) {
    pads.push(
      <smtpad key={`r${i}`} portHints={[`pin${27 + i}`]} shape="rect" width="1.5mm" height="0.9mm"
        pcbX={8.75} pcbY={-11.26 + i * P} />,
    )
  }
  return (
    <footprint>
      {pads}
      {/* EPAD (pin 41): 3x3 array of 0.9 x 0.9 pads, pitch 1.4, centred at (-1.5, -2.47) (EasyEDA C2913202) */}
      {[-2.9, -1.5, -0.1].flatMap((x, xi) => [-3.87, -2.47, -1.07].map((y, yi) => (
        <smtpad key={`e${x}_${y}`} portHints={[`pin${41 + xi * 3 + yi}`]} shape="rect" width="0.9mm" height="0.9mm" pcbX={x} pcbY={y} />
      )))}
      {/* antenna keepout: no copper on any layer under/around antenna end */}
      <keepout shape="rect" width="18.6mm" height="7mm" pcbX={0} pcbY={9.25} layers={["top", "bottom"]} />
      {/* module outline only where there are no pads (antenna part, y > 5.9); the pad rows are marked by the pads themselves.
          Top edge 0.3 mm inside the module end so the silk does not sit on the board edge; lower outline 0.35 mm outside the pads. */}
      <silkscreenpath route={[{ x: -9, y: 5.9 }, { x: -9, y: 12.45 }, { x: 9, y: 12.45 }, { x: 9, y: 5.9 }]} />
      <silkscreenpath route={[{ x: -9.85, y: 5.9 }, { x: -9.85, y: -13.4 }, { x: 9.85, y: -13.4 }, { x: 9.85, y: 5.9 }]} />
      {/* pin-1 dot inside the module outline next to pad 1 (R7 m6); the module label is dropped (silk text must be >= 1 mm high and the EPAD sits in the middle) */}
      <Dot x={-7.3} y={6.9} />
    </footprint>
  )
}

export const Esp32S3Wroom1 = (props: Partial<ChipProps> & { name: string }) => (
  <chip
    manufacturerPartNumber="ESP32-S3-WROOM-1-N16R8"
    supplierPartNumbers={{ jlcpcb: ["C2913202"] }}
    pinLabels={ESP32S3_PINLABELS as any}
    footprint={<Esp32S3Footprint />}
    schPinArrangement={{
      leftSide: { direction: "top-to-bottom", pins: ["V3V3", "EN", "IO0", "IO4", "IO5", "IO6", "IO7", "IO15", "IO16", "IO17", "IO18", "IO8"] },
      rightSide: { direction: "top-to-bottom", pins: ["IO1", "IO2", "IO3", "IO9", "IO10", "IO11", "IO12", "IO13", "IO14", "IO21", "IO38", "IO39", "IO40", "IO41", "IO42", "IO47", "IO48", "IO45", "IO46", "RXD0", "TXD0", "IO19", "IO20"] },
      bottomSide: { direction: "left-to-right", pins: ["GND1", "GND2", "GND_EP1", "GND_EP2", "GND_EP3", "GND_EP4", "GND_EP5", "GND_EP6", "GND_EP7", "GND_EP8", "GND_EP9"] },
    }}
    {...(props as any)}
  />
)
