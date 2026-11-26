// MCU side of the EMS-Bus interface V2: ESP32-S3-WROOM-1-N16R8, USB-C, LDO, ESD, buttons, LEDs, JP1, P2.
// Shared nets with the EMS side: V3V3, GND, MCU_RX, MCU_TX (ESP_TX/VBUS/USB_DP/USB_DN are local).
// Placement is absolute (board centre 0,0). MCU region x in [6,55], y in [-25,25].
import { Esp32S3Wroom1 } from "../lib/esp32s3wroom1"
import { UsbC16 } from "../lib/usbc16"
import { Tactile5x5, TantalumB } from "../lib/thtparts"
import { LedGreen } from "../lib/diodes"
import { SolderJumper2Footprint } from "../lib/jumper"

const T = (from: string, to: string) => <trace key={`${from}|${to}`} from={from} to={to} />
const J = (c: string) => ({ jlcpcb: [c] })
const R = (n: string, v: string, x: number, y: number, rot: number, lcsc?: string, sx = 0, sy = 0) => (
  <resistor name={n} resistance={v} footprint="0805" pcbX={x} pcbY={y} pcbRotation={rot} schX={sx} schY={sy}
    {...(lcsc ? { supplierPartNumbers: J(lcsc) } : {})} />
)
const C = (n: string, v: string, x: number, y: number, rot: number, lcsc?: string, fp = "0805", sx = 0, sy = 0) => (
  <capacitor name={n} capacitance={v} footprint={fp} pcbX={x} pcbY={y} pcbRotation={rot} schX={sx} schY={sy}
    {...(lcsc ? { supplierPartNumbers: J(lcsc) } : {})} />
)
// single-pad test point
const TestPad = (p: { name: string; x: number; y: number; sx: number; sy: number }) => (
  <chip name={p.name} pinLabels={{ pin1: ["TP"] }} pcbX={p.x} pcbY={p.y} schX={p.sx} schY={p.sy}
    footprint={<footprint><smtpad portHints={["pin1"]} shape="circle" radius="0.6mm" pcbX={0} pcbY={0} /></footprint>}
    schPinArrangement={{ leftSide: { direction: "top-to-bottom", pins: ["TP"] } }} />
)

export const McuSide = () => (
  <group name="mcu" pcbX={0} pcbY={0}>
    {/* ---------------- ESP32-S3 module: antenna to +X board edge ---------------- */}
    <Esp32S3Wroom1 name="U3" pcbX={42.25} pcbY={0} pcbRotation={-90} schX={0} schY={0} />
    {/* GND pads + EPAD */}
    {T(".U3 > .GND1", "net.GND")}{T(".U3 > .GND2", "net.GND")}
    {/* EPAD = 9 separate pads (ports GND_EP1..9), each tied to GND explicitly */}
    {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => T(`.U3 > .GND_EP${i}`, "net.GND"))}
    {T(".U3 > .V3V3", "net.V3V3")}
    {C("C22", "10uF", 47.5, 12.8, 90, "C15850", "0805", -8, 8)}
    {C("C23", "100nF", 50.5, 12.8, 90, "C49678", "0805", -8, 6)}
    {T(".C22 > .pin1", "net.V3V3")}{T(".C22 > .pin2", "net.GND")}
    {T(".C23 > .pin1", "net.V3V3")}{T(".C23 > .pin2", "net.GND")}

    {/* EN: pull-up + 1uF + RESET */}
    {R("R20", "10k", 44.5, 12.8, 90, "C17414", -8, 4)}
    {C("C20", "1uF", 41.5, 12.8, 90, "C28323", "0805", -8, 2)}
    <Tactile5x5 name="SW1" pcbX={46} pcbY={18.5} pcbRotation={0} schX={-12} schY={2} />
    {T(".U3 > .EN", "net.EN")}
    {T(".R20 > .pin1", "net.V3V3")}{T(".R20 > .pin2", "net.EN")}
    {T(".C20 > .pin1", "net.EN")}{T(".C20 > .pin2", "net.GND")}
    {/* tactile: pads A1/A2 and B1/B2 are joined inside the switch, every pad is tied to its net explicitly */}
    {T(".SW1 > .A1", "net.EN")}{T(".SW1 > .A2", "net.EN")}{T(".SW1 > .B1", "net.GND")}{T(".SW1 > .B2", "net.GND")}

    {/* BOOT: GPIO0 + pull-up + button (bottom edge) */}
    <Tactile5x5 name="SW2" pcbX={40} pcbY={-22} pcbRotation={0} schX={-12} schY={-2} />
    {R("R21", "10k", 31.5, -14, 90, "C17414", -8, -2)}
    {T(".U3 > .IO0", "net.BOOT")}
    {T(".R21 > .pin1", "net.V3V3")}{T(".R21 > .pin2", "net.BOOT")}
    {T(".SW2 > .A1", "net.BOOT")}{T(".SW2 > .A2", "net.BOOT")}{T(".SW2 > .B1", "net.GND")}{T(".SW2 > .B2", "net.GND")}

    {/* EMS UART: GPIO5 = MCU_RX, GPIO17 = ESP_TX (-> JP1 -> MCU_TX) */}
    {T(".U3 > .IO5", "net.MCU_RX")}
    {T(".U3 > .IO17", "net.ESP_TX")}

    {/* status LED GPIO2 (S32S3 profile: LED=GPIO2, active high) */}
    {R("R22", "1k", 50.5, -14, 90, "C17513", -8, -6)}
    <LedGreen name="LD4" pcbX={50.5} pcbY={-17.5} pcbRotation={90} schX={-8} schY={-8} />
    {T(".U3 > .IO2", ".R22 > .pin1")}
    {T(".R22 > .pin2", ".LD4 > .A")}{T(".LD4 > .K", "net.GND")}

    {/* UART0 test pads */}
    <TestPad name="TP1" x={44.45} y={-14.5} sx={14} sy={-6} />
    <TestPad name="TP2" x={41.5} y={-14.5} sx={14} sy={-8} />
    <TestPad name="TP3" x={47.5} y={-14.5} sx={14} sy={-10} />
    {T(".U3 > .TXD0", ".TP1 > .TP")}{T(".U3 > .RXD0", ".TP2 > .TP")}{T(".TP3 > .TP", "net.GND")}
    <silkscreentext text="TX" pcbX={44.45} pcbY={-16.3} fontSize="0.9mm" />
    <silkscreentext text="RX" pcbX={41.5} pcbY={-16.3} fontSize="0.9mm" />
    <silkscreentext text="G" pcbX={47.5} pcbY={-16.3} fontSize="0.9mm" />

    {/* ---------------- USB-C at bottom edge ---------------- */}
    <UsbC16 name="J2" pcbX={24} pcbY={22.4} pcbRotation={0} schX={-24} schY={0} />
    {/* every physical contact is its own port; the A/B duplicates are tied together by the nets (both plug orientations) */}
    {T(".J2 > .VBUS_L", "net.VBUS")}{T(".J2 > .VBUS_R", "net.VBUS")}
    {T(".J2 > .GND_L", "net.GND")}{T(".J2 > .GND_R", "net.GND")}
    {T(".J2 > .DP_L", "net.USB_DP")}{T(".J2 > .DP_R", "net.USB_DP")}
    {T(".J2 > .DN_L", "net.USB_DN")}{T(".J2 > .DN_R", "net.USB_DN")}
    {R("R23", "5.1k", 19.5, 13, 90, "C27834", -20, -6)}
    {R("R24", "5.1k", 28.5, 13, 90, "C27834", -20, -8)}
    {T(".J2 > .CC1", ".R23 > .pin1")}{T(".R23 > .pin2", "net.GND")}
    {T(".J2 > .CC2", ".R24 > .pin1")}{T(".R24 > .pin2", "net.GND")}
    {R("R25", "1M", 15, 27, 0, "C17514", -20, -12)}
    {C("C21", "4.7nF", 15, 24.5, 0, "C1744", "0805", -20, -14)}
    {["SH1", "SH2", "SH3", "SH4"].map((h) => T(`.J2 > .${h}`, "net.SHELL"))}
    {T(".R25 > .pin1", "net.SHELL")}{T(".C21 > .pin1", "net.SHELL")}
    {T(".R25 > .pin2", "net.GND")}{T(".C21 > .pin2", "net.GND")}

    {/* ESD: USBLC6-2SC6 pins 1,6 = I/O1; 3,4 = I/O2; 2 = GND; 5 = VBUS */}
    <chip name="U4" footprint="sot23_6" manufacturerPartNumber="USBLC6-2SC6" supplierPartNumbers={J("C7519")}
      pcbX={24} pcbY={14.5} pcbRotation={0} schX={-16} schY={0}
      pinLabels={{ pin1: ["IO1a"], pin2: ["GND"], pin3: ["IO2a"], pin4: ["IO2b"], pin5: ["VBUS"], pin6: ["IO1b"] }}
      schPinArrangement={{ leftSide: { direction: "top-to-bottom", pins: ["IO1a", "IO2a", "GND"] }, rightSide: { direction: "top-to-bottom", pins: ["IO1b", "IO2b", "VBUS"] } }} />
    {T(".U4 > .IO1a", "net.USB_DP")}{T(".U4 > .IO1b", "net.USB_DP")}
    {T(".U4 > .IO2a", "net.USB_DN")}{T(".U4 > .IO2b", "net.USB_DN")}
    {T(".U4 > .GND", "net.GND")}{T(".U4 > .VBUS", "net.VBUS")}
    {T(".U3 > .IO19", "net.USB_DN")}{T(".U3 > .IO20", "net.USB_DP")}

    {/* ---------------- LDO AMS1117-3.3, SOT-223: 1=GND/ADJ 2=VOUT 3=VIN 4(tab)=VOUT ---------------- */}
    <chip name="U5" footprint="sot223" manufacturerPartNumber="AMS1117-3.3" supplierPartNumbers={J("C6186")}
      pcbX={40} pcbY={24.5} pcbRotation={0} schX={-16} schY={-8}
      pinLabels={{ pin1: ["GND"], pin2: ["VOUT"], pin3: ["VIN"], pin4: ["TAB"] }}
      schPinArrangement={{ leftSide: { direction: "top-to-bottom", pins: ["VIN", "GND"] }, rightSide: { direction: "top-to-bottom", pins: ["VOUT", "TAB"] } }} />
    {T(".U5 > .VIN", "net.VBUS")}{T(".U5 > .GND", "net.GND")}
    {T(".U5 > .VOUT", "net.V3V3")}{T(".U5 > .TAB", "net.V3V3")}
    {C("C24", "10uF", 32, 28, 90, "C15850", "0805", -20, -16)}
    {C("C25", "100nF", 32, 24.5, 90, "C49678", "0805", -20, -18)}
    {T(".C24 > .pin1", "net.VBUS")}{T(".C24 > .pin2", "net.GND")}
    {T(".C25 > .pin1", "net.VBUS")}{T(".C25 > .pin2", "net.GND")}
    {/* tantalum 100 uF / 6.3 V (C16133, Basic) for AMS1117 output stability; pad 1 = + */}
    <TantalumB name="C29" pcbX={36} pcbY={20} pcbRotation={0} schX={-12} schY={-14} />
    {T(".C29 > .pin1", "net.V3V3")}{T(".C29 > .pin2", "net.GND")}
    {C("C26", "22uF", 47, 24, 90, "C12891", "1206", -12, -16)}
    {C("C27", "10uF", 50, 24, 90, "C15850", "0805", -12, -18)}
    {C("C28", "100nF", 50, 27.5, 90, "C49678", "0805", -12, -20)}
    {["C26", "C27", "C28"].map((c) => [T(`.${c} > .pin1`, "net.V3V3"), T(`.${c} > .pin2`, "net.GND")])}

    {/* power LED on V3V3 */}
    {R("R26", "1k", 53, 17, 90, "C17513", -4, -16)}
    <LedGreen name="LD5" pcbX={53} pcbY={21} pcbRotation={90} schX={-4} schY={-18} />
    {T(".R26 > .pin1", "net.V3V3")}{T(".R26 > .pin2", ".LD5 > .A")}{T(".LD5 > .K", "net.GND")}

    {/* ---------------- JP1 (open) ESP_TX <-> MCU_TX, R_PU, P2 ---------------- */}
    <solderjumper name="JP1" pinCount={2} footprint={<SolderJumper2Footprint />} pcbX={36.1} pcbY={15} pcbRotation={90} schX={-4} schY={8} />
    {T(".JP1 > .pin1", "net.ESP_TX")}{T(".JP1 > .pin2", "net.MCU_TX")}
    <silkscreentext text="TX EN - open = RX only" pcbX={47.5} pcbY={14.6} fontSize="0.9mm" />
    {R("R27", "100k", 39.5, 16, 90, "C149504", -4, 12)}
    {T(".R27 > .pin1", "net.MCU_TX")}{T(".R27 > .pin2", "net.V3V3")}
    {/* JP2 (default OPEN): V3V3 -> P2 pin 1 (net P2_3V3); close only if the 3V3 rail of this board may feed the header */}
    <solderjumper name="JP2" pinCount={2} footprint={<SolderJumper2Footprint />} pcbX={28} pcbY={-21} pcbRotation={90} schX={-4} schY={-8} />
    {T(".JP2 > .pin1", "net.V3V3")}{T(".JP2 > .pin2", "net.P2_3V3")}
    <silkscreentext text="3V3 OUT" pcbX={31.5} pcbY={-21} fontSize="0.9mm" />
    <pinheader name="P2" pinCount={4} pitch="2.54mm" supplierPartNumbers={J("C32713270")} manufacturerPartNumber="PZ2.54-1x4P" pcbX={22} pcbY={-26.5} pcbRotation={0} schX={-4} schY={-4}
      pinLabels={["V3V3", "MCU_TX", "MCU_RX", "GND"]} />
    {T(".P2 > .pin1", "net.P2_3V3")}{T(".P2 > .pin2", "net.MCU_TX")}
    {T(".P2 > .pin3", "net.MCU_RX")}{T(".P2 > .pin4", "net.GND")}
  </group>
)
