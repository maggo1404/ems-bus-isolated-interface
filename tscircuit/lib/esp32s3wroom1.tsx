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
// Hand-soldering aid (R8): the module is NOT placed by JLC (doNotPlace), so every U3 pad has noSolderPaste and the castellated pads are
// extended OUTWARD by 1.0 mm beyond the Espressif land pattern. Inner end stays where the land pattern has it (x = +-8.0 / y = -11.79);
// outside the module body edge (x = +-9.0, y = -12.75) 1.5 mm of copper stay free for the iron tip.
const EXT = 1.07
const W_SIDE = 1.5 + EXT      // side pads: 2.5 mm long (x), inner end -8.0 / +8.0, outer end -10.5 / +10.5
const W_BOT = 1.5 + EXT       // bottom pads: 2.5 mm long (y), inner end -11.79, outer end -14.29
// EPAD: 3x3 grid (pitch 1.4, centre (-1.5,-2.47)). The 4 corner pads + centre pad are plated through-holes (hole 0.8 / pad 1.3 ring 0.25 mm)
// connected to a 4.2 x 4.2 mm exposed GND pad on the BOTTOM layer: heat the pad from below, solder flows through the holes to the module EPAD.
const EP_X = [-2.9, -1.5, -0.1]
const EP_Y = [-3.87, -2.47, -1.07]
export const EPAD_HOLE_D = 0.8
export const EPAD_HOLE_PAD = 1.3
export const Esp32S3Footprint = () => {
  const pads: any[] = []
  // left: pins 1..14, y from +? (top, antenna side) downwards
  for (let i = 0; i < 14; i++) {
    pads.push(
      <smtpad key={`l${i}`} portHints={[`pin${1 + i}`]} shape="rect" width={`${W_SIDE}mm`} height="0.9mm"
        pcbX={-8.0 - W_SIDE / 2} pcbY={5.26 - i * P} noSolderPaste />,
    )
  }
  // bottom: pins 15..26 left->right
  for (let i = 0; i < 12; i++) {
    pads.push(
      <smtpad key={`b${i}`} portHints={[`pin${15 + i}`]} shape="rect" width="0.9mm" height={`${W_BOT}mm`}
        pcbX={-6.985 + i * P} pcbY={-11.79 - W_BOT / 2} noSolderPaste />,
    )
  }
  // right: pins 27..40 bottom->top
  for (let i = 0; i < 14; i++) {
    pads.push(
      <smtpad key={`r${i}`} portHints={[`pin${27 + i}`]} shape="rect" width={`${W_SIDE}mm`} height="0.9mm"
        pcbX={8.0 + W_SIDE / 2} pcbY={-11.26 + i * P} noSolderPaste />,
    )
  }
  return (
    <footprint>
      {pads}
      {/* EPAD ports pin41..pin49 (index xi*3+yi); corner + centre = plated holes, the 4 edge-centre ones stay 0.9 mm SMD pads */}
      {EP_X.flatMap((x, xi) => EP_Y.map((y, yi) => {
        const hole = (xi !== 1 && yi !== 1) || (xi === 1 && yi === 1)
        return hole
          ? <platedhole key={`e${x}_${y}`} portHints={[`pin${41 + xi * 3 + yi}`]} shape="circle" holeDiameter={`${EPAD_HOLE_D}mm`} outerDiameter={`${EPAD_HOLE_PAD}mm`} pcbX={x} pcbY={y} />
          : <smtpad key={`e${x}_${y}`} portHints={[`pin${41 + xi * 3 + yi}`]} shape="rect" width="0.9mm" height="0.9mm" pcbX={x} pcbY={y} noSolderPaste />
      }))}
      {/* exposed GND pad on the bottom layer (hand-soldering from below); same port as the centre EPAD pad (internal duplicate port) */}
      <smtpad portHints={["pin45"]} layer="bottom" shape="rect" width="4.2mm" height="4.2mm" pcbX={-1.5} pcbY={-2.47} noSolderPaste />
      {/* antenna keepout: no copper on any layer under/around antenna end */}
      <keepout shape="rect" width="18.6mm" height="7mm" pcbX={0} pcbY={9.25} layers={["top", "bottom"]} />
      {/* module body outline 18.0 x 25.5 (x +-9.0, y -12.75 .. +12.75). Full lines along the antenna part (y > 5.9, no pads there); along the pad rows the
          outline is drawn only as corner marks (0.7 mm legs) because the extended pads cover the body edge (silk on pads is clipped by JLC). */}
      <silkscreenpath route={[{ x: -9, y: 5.9 }, { x: -9, y: 12.45 }, { x: 9, y: 12.45 }, { x: 9, y: 5.9 }]} />
      <silkscreenpath route={[{ x: -9, y: -12.1 }, { x: -9, y: -12.75 }, { x: -8.1, y: -12.75 }]} />
      <silkscreenpath route={[{ x: 9, y: -12.1 }, { x: 9, y: -12.75 }, { x: 8.1, y: -12.75 }]} />
      {/* module shoulder (end of the pad rows, y = 5.9) and the pad-row side limits just outside the extended pads */}
      <silkscreenpath route={[{ x: -10.9, y: 5.9 }, { x: -9, y: 5.9 }]} />
      <silkscreenpath route={[{ x: 10.9, y: 5.9 }, { x: 9, y: 5.9 }]} />
      {/* pin-1 dot outside the extended pad 1 (left, in line with the pad); the module label is dropped (silk text must be >= 1 mm high) */}
      <Dot x={-11.4} y={5.26} />
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
      // grouped by function: left = pins used on this board (power, reset/boot strapping, EMS UART, status LED, UART0 test pads, USB),
      // right = unused GPIOs (all left open), bottom = ground pads
      leftSide: { direction: "top-to-bottom", pins: ["V3V3", "EN", "IO0", "IO5", "IO17", "IO2", "TXD0", "RXD0", "IO19", "IO20"] },
      rightSide: { direction: "top-to-bottom", pins: ["IO1", "IO3", "IO4", "IO6", "IO7", "IO8", "IO9", "IO10", "IO11", "IO12", "IO13", "IO14", "IO15", "IO16", "IO18", "IO21", "IO35", "IO36", "IO37", "IO38", "IO39", "IO40", "IO41", "IO42", "IO45", "IO46", "IO47", "IO48"] },
      bottomSide: { direction: "left-to-right", pins: ["GND1", "GND2", "GND_EP1", "GND_EP2", "GND_EP3", "GND_EP4", "GND_EP5", "GND_EP6", "GND_EP7", "GND_EP8", "GND_EP9"] },
    }}
    {...(props as any)}
  />
)
