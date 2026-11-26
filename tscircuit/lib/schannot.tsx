// Schematic-only annotations (no PCB / netlist effect): functional group frames with titles and the isolation barrier.
// Frames are <schematicbox> (dashed), the barrier is a dashed <schematicline> with labels.  Coordinates: schematic units, see lib/schlayout.ts.
import { SCALE } from "./schlayout"
type Frame = { title: string; right?: boolean; x0: number; x1: number; y0: number; y1: number }
export const FRAMES: Frame[] = [
  { title: "1  EMS bus input: fuses, filter, Schottky bridge, clamp", x0: -48.5, x1: -26.2, y0: 7, y1: 23.5 },
  { title: "2  Buck converter JW5017S: rectified bus (VIN) to 5 V (V5_EMS)", x0: -26, x1: -1.5, y0: 7.5, y1: 23.5 },
  { title: "3  RX path: bus level -> comparator U1A -> OC1 (EMS to MCU)", x0: -48.5, x1: -1.5, y0: -4.5, y1: 6.5 },
  { title: "4  TX path: OC2 -> comparator U1B -> Q1 bus load (MCU to EMS, drawn right to left)", x0: -48.5, x1: -1.5, y0: -16, y1: -5.5, right: true },
  { title: "5  Isolation", x0: -2.4, x1: 2.4, y0: -13, y1: 5 },
  { title: "6  MCU side opto interface", x0: 3, x1: 13.8, y0: -11, y1: 8.5 },
  { title: "7  UART header P2, JP1 / JP2", x0: 15, x1: 28, y0: -9, y1: 0 },
  { title: "8  USB-C input, ESD, PTC", x0: 1, x1: 14.5, y0: 9.5, y1: 23 },
  { title: "9  LDO AMS1117-3.3 and 3V3 rail", x0: 15, x1: 34.5, y0: 9.5, y1: 23 },
  { title: "10  ESP32-S3-WROOM-1 (U3, DNP) with reset, boot, LED, test pads", x0: 36, x1: 57, y0: -11, y1: 19 },
]
export const SchAnnotations = () => (
  <>
    {FRAMES.map((f) => (
      <schematicbox key={f.title} schX={((f.x0 + f.x1) / 2) * SCALE} schY={((f.y0 + f.y1) / 2) * SCALE} width={(f.x1 - f.x0) * SCALE} height={(f.y1 - f.y0) * SCALE}
        title={f.title} titleAlignment={f.right ? "top_right" : "top_left"} strokeStyle="dashed" />
    ))}
    <schematicline x1={0} y1={-17 * SCALE} x2={0} y2={24.5 * SCALE} strokeWidth={0.04} isDashed />
    <schematictext schX={-6 * SCALE} schY={25.5 * SCALE} text="EMS SIDE (GND_EMS): galvanically isolated, bus powered" fontSize={0.35} />
    <schematictext schX={6 * SCALE} schY={25.5 * SCALE} text="MCU SIDE (GND): USB powered" fontSize={0.35} />
  </>
)
