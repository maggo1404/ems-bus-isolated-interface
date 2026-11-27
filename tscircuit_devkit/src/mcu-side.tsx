// MCU side of the EMS-Bus interface, DevKitC variant: the ESP32-S3-DevKitC-1 (N16R8) is plugged into two 1x22 female sockets J1 / J3
// (hand-plugged, not in the BOM).  The DevKitC brings USB, 3V3 LDO, EN/BOOT buttons and the ESP32 module: none of that is on this board.
// Shared nets with the EMS side: V3V3 (= DevKitC 3V3 pin), GND, MCU_RX, MCU_TX (ESP_TX is local).
// Placement is absolute (board centre 0,0).  Geometry of the DevKitC: lib/devkitc.tsx, docs/DEVKITC.md.
import { DevKitSocketJ1, DevKitSocketJ3, DevKitOutline, J1_X, J3_X, PIN1_Y } from "../lib/devkitc"
import { PinHeader1x4 } from "../lib/thtparts"
import { traceWidth } from "../lib/netclass"
import { sch } from "../lib/schlayout"
import { LedYellow } from "../lib/diodes"
import { FS } from "../lib/silk"
import { SolderJumper2Footprint } from "../lib/jumper"

const T = (from: string, to: string) => (
  <trace key={`${from}|${to}`} from={from} to={to} thickness={traceWidth(to.startsWith("net.") ? to.slice(4) : undefined)} />
)
const J = (c: string) => ({ jlcpcb: [c] })
const R = (n: string, v: string, x: number, y: number, rot: number, lcsc?: string) => (
  <resistor name={n} resistance={v} footprint="0805" pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbX={x} pcbY={y} pcbRotation={rot} {...sch(n)}
    {...(lcsc ? { supplierPartNumbers: J(lcsc) } : {})} />
)

export const McuSide = () => (
  <group name="mcu" pcbX={0} pcbY={0} schX={0} schY={0}>
    {/* ---------------- ESP32-S3-DevKitC-1 on two 1x22 female sockets (origin of a socket = its pin 1) ---------------- */}
    <DevKitSocketJ1 name="J1" pcbX={J1_X} pcbY={PIN1_Y} {...sch("J1")} />
    <DevKitSocketJ3 name="J3" pcbX={J3_X} pcbY={PIN1_Y} {...sch("J3")} />
    <DevKitOutline />
    {/* 3V3 pins (output of the DevKitC LDO) = V3V3; GND pins; every other pin (5V, RST, GPIO0 ...) stays open */}
    {T(".J1 > .3V3_A", "net.V3V3")}{T(".J1 > .3V3_B", "net.V3V3")}
    {T(".J1 > .GND", "net.GND")}
    {T(".J3 > .GND_A", "net.GND")}{T(".J3 > .GND_B", "net.GND")}{T(".J3 > .GND_C", "net.GND")}
    {/* EMS UART (EMS-ESP32 profile S32S3: Rx = GPIO5, Tx = GPIO17, LED = GPIO2): GPIO5 = MCU_RX, GPIO17 = ESP_TX (-> JP1 -> MCU_TX) */}
    {T(".J1 > .IO5", "net.MCU_RX")}
    {T(".J1 > .IO17", "net.ESP_TX")}

    {/* status LED GPIO2 (S32S3 profile: LED = GPIO2, active high) beside the DevKitC (visible) */}
    {R("R22", "330", 38.4, 12.0, 90, "C17630")}
    <LedYellow name="LD4" pcbX={38.4} pcbY={7.4} pcbRotation={90} {...sch("LD4", ["A", "K"])} />
    {T(".J3 > .IO2", ".R22 > .pin1")}
    {T(".R22 > .pin2", ".LD4 > .A")}{T(".LD4 > .K", "net.GND")}

    {/* ---------------- JP1 (open) ESP_TX <-> MCU_TX, R27 pull-up ---------------- */}
    <solderjumper name="JP1" pinCount={2} footprint={<SolderJumper2Footprint />} pcbX={8.0} pcbY={1.0} pcbRotation={270} {...sch("JP1")} />
    {T(".JP1 > .pin1", "net.ESP_TX")}{T(".JP1 > .pin2", "net.MCU_TX")}
    {R("R27", "100k", 10.0, -2.0, 90, "C149504")}
    {T(".R27 > .pin1", "net.MCU_TX")}{T(".R27 > .pin2", "net.V3V3")}
    {/* JP2 (default OPEN): V3V3 -> P2 pin 1 (net P2_3V3); close only to feed an external device from the DevKitC 3V3 (never while P2 feeds 3V3 in) */}
    <solderjumper name="JP2" pinCount={2} footprint={<SolderJumper2Footprint />} pcbX={10.3} pcbY={-18.2} pcbRotation={270} {...sch("JP2")} />
    {T(".JP2 > .pin1", "net.V3V3")}{T(".JP2 > .pin2", "net.P2_3V3")}
    <PinHeader1x4 name="P2" schWidth={1.67} pcbX={8.6} pcbY={-24.1} pcbRotation={270} {...sch("P2")} />
    {T(".P2 > .pin1", "net.P2_3V3")}{T(".P2 > .pin2", "net.MCU_TX")}
    {T(".P2 > .pin3", "net.MCU_RX")}{T(".P2 > .pin4", "net.GND")}
  </group>
)
