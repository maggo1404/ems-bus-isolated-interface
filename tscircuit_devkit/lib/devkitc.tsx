// ESP32-S3-DevKitC-1 v1.1 plug-in module (hand-plugged, NOT in the BOM) on two 1x22 female sockets J1 / J3.
// Facts: docs/DEVKITC.md (Espressif user guide v1.1 + dimension drawing DXF_ESP32-S3-DevKitC-1_V1.1_20220429).
//   board 25.40 x 62.86 mm (+ 6.3 mm PCB antenna beyond the board edge = 69.15 mm), pin pitch 2.54, header rows 22.86 mm apart,
//   rows 1.27 mm inside the long edges, pin 1 (3V3 / G) 1.56 mm below the antenna end, pin 22 7.96 mm above the USB end.
// DevKitC drawing frame (x right, y up, antenna up): J1 at x = 1.27 (left), J3 at x = 24.13 (right), pin n at y = 61.30 - 2.54 (n - 1).
// It is placed UNROTATED here (long side along Y = parallel to the isolation barrier x = 0): origin (DK_X0, DK_Y0) = lower left
// corner of the DevKitC PCB (USB end) in board coordinates.
import type { ChipProps } from "tscircuit"
import { FS } from "./silk"

export const DK_X0 = 11.0, DK_Y0 = -32.9        // lower-left corner of the DevKitC PCB in board coordinates (USB end at the bottom)
export const DK_W = 25.4, DK_L = 62.86          // PCB outline
export const DK_ANT = 6.3                        // antenna beyond the PCB top edge (69.15 mm in total)
export const DK_PIN1_Y = 61.3                    // y of pin 1 above the USB-end edge
export const DK_ROW_DX = 22.86                   // distance J1 - J3
export const J1_X = DK_X0 + 1.27, J3_X = DK_X0 + 1.27 + DK_ROW_DX
export const PIN1_Y = DK_Y0 + DK_PIN1_Y         // board y of pin 1 of both sockets (28.4)

// Header tables (Espressif user guide v1.1, "Header Block"): pin number -> label (signal)
export const J1_PINS = ["3V3_A", "3V3_B", "RST", "IO4", "IO5", "IO6", "IO7", "IO15", "IO16", "IO17", "IO18", "IO8", "IO3", "IO46", "IO9", "IO10", "IO11", "IO12", "IO13", "IO14", "V5", "GND"]
export const J3_PINS = ["GND_A", "TX", "RX", "IO1", "IO2", "IO42", "IO41", "IO40", "IO39", "IO38", "IO37", "IO36", "IO35", "IO0", "IO45", "IO48", "IO47", "IO21", "IO20", "IO19", "GND_B", "GND_C"]

const labels = (names: string[]) => Object.fromEntries(names.map((n, i) => [`pin${i + 1}`, [n]]))

// 1x22 female socket 2.54 mm, THT (LCSC C20071202 F185-1122A0ASUC2, 8.5 mm body): origin = pin 1, the row runs along -Y, pin 1 = square pad
const SocketFootprint = ({ left = true }: { left?: boolean }) => (
  <footprint>
    {Array.from({ length: 22 }, (_, i) =>
      i === 0 ? (
        <platedhole key={i} portHints={["pin1"]} shape="circular_hole_with_rect_pad" holeDiameter="1.0mm" rectPadWidth="1.6mm" rectPadHeight="1.6mm" pcbX={0} pcbY={0} />
      ) : (
        <platedhole key={i} portHints={[`pin${i + 1}`]} shape="circle" holeDiameter="1.0mm" outerDiameter="1.6mm" pcbX={0} pcbY={-2.54 * i} />
      ),
    )}
    {/* socket body 2.54 x 55.88 */}
    {left ? (
      <silkscreenpath route={[{ x: -1.27, y: 1.27 }, { x: 1.27, y: 1.27 }, { x: 1.27, y: -2.54 * 21 - 1.27 }, { x: -1.27, y: -2.54 * 21 - 1.27 }, { x: -1.27, y: 1.27 }]} />
    ) : (
      // J1 (corridor side): no left line (the solder jumper JP2 pads sit 0.2 mm from the socket outline)
      <silkscreenpath route={[{ x: -1.27, y: 1.27 }, { x: 1.27, y: 1.27 }, { x: 1.27, y: -2.54 * 21 - 1.27 }, { x: -1.27, y: -2.54 * 21 - 1.27 }]} />
    )}
  </footprint>
)

const Socket = (names: string[], mpn: string, left = true) => (props: Partial<ChipProps> & { name: string }) => (
  <chip
    manufacturerPartNumber={mpn}
    supplierPartNumbers={{ jlcpcb: ["C20071202"] }}
    pinLabels={labels(names)}
    schPinArrangement={{ leftSide: { direction: "top-to-bottom", pins: names } }}
    footprint={<SocketFootprint left={left} />}
    {...(props as any)}
  />
)
export const DevKitSocketJ1 = Socket(J1_PINS, "F185-1122A0ASUC2", false)
export const DevKitSocketJ3 = Socket(J3_PINS, "F185-1122A0ASUC2")

/** documentation overlay (no copper, no silk): DevKitC PCB outline, antenna overhang, USB end (fabrication notes -> assembly drawing) */
export const DevKitOutline = () => (
  <>
    <fabricationnoterect pcbX={DK_X0 + DK_W / 2} pcbY={DK_Y0 + DK_L / 2} width={DK_W} height={DK_L} strokeWidth={0.1} isFilled={false} />
    <fabricationnoterect pcbX={DK_X0 + DK_W / 2} pcbY={DK_Y0 + DK_L + DK_ANT / 2} width={18} height={DK_ANT} strokeWidth={0.1} isFilled={false} />
    <fabricationnotetext pcbX={DK_X0 + DK_W / 2} pcbY={DK_Y0 + 3} text="ESP32-S3-DevKitC-1 (USB end)" fontSize="1mm" />
  </>
)
export { FS }
