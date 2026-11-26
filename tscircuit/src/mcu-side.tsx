// MCU side of the EMS-Bus interface V2: ESP32-S3-WROOM-1-N16R8, USB-C, LDO, ESD, buttons, LEDs, JP1, P2.
// Shared nets with the EMS side: V3V3, GND, MCU_RX, MCU_TX (ESP_TX/VBUS/USB_DP/USB_DN are local).
// Placement is absolute (board centre 0,0). MCU region x in [6,55], y in [-25,25].
import { Esp32S3Wroom1 } from "../lib/esp32s3wroom1"
import { UsbC16 } from "../lib/usbc16"
import { Tactile5x5, TantalumB, PinHeader1x4, Ptc1206Footprint } from "../lib/thtparts"
import { traceWidth } from "../lib/netclass"
import { sch } from "../lib/schlayout"
import { LedYellow } from "../lib/diodes"
import { PartDot, FS } from "../lib/silk"
import { SolderJumper2Footprint } from "../lib/jumper"

const T = (from: string, to: string) => (
  <trace key={`${from}|${to}`} from={from} to={to} thickness={traceWidth(to.startsWith("net.") ? to.slice(4) : undefined)} />
)
const J = (c: string) => ({ jlcpcb: [c] })
const R = (n: string, v: string, x: number, y: number, rot: number, lcsc?: string) => (
  <resistor name={n} resistance={v} footprint="0805" pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbX={x} pcbY={y} pcbRotation={rot} {...sch(n)}
    {...(lcsc ? { supplierPartNumbers: J(lcsc) } : {})} />
)
const C = (n: string, v: string, x: number, y: number, rot: number, lcsc?: string, fp = "0805") => (
  <capacitor name={n} capacitance={v} footprint={fp} pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbX={x} pcbY={y} pcbRotation={rot} {...sch(n)}
    {...(lcsc ? { supplierPartNumbers: J(lcsc) } : {})} />
)
// single-pad test point
const TestPad = (p: { name: string; x: number; y: number }) => (
  <chip name={p.name} pinLabels={{ pin1: ["TP"] }} pcbX={p.x} pcbY={p.y} {...sch(p.name)}
    footprint={<footprint><smtpad portHints={["pin1"]} shape="circle" radius="0.6mm" pcbX={0} pcbY={0} noSolderPaste /></footprint>}
    schPinArrangement={{ leftSide: { direction: "top-to-bottom", pins: ["TP"] } }} />
)

export const McuSide = () => (
  <group name="mcu" pcbX={0} pcbY={0} schX={0} schY={0}>
    {/* ---------------- ESP32-S3 module: antenna to +X board edge ---------------- */}
    <Esp32S3Wroom1 name="U3" schHeight={7.3} pcbX={42.25} pcbY={0} pcbRotation={-90} {...sch("U3")} doNotPlace />
    {/* GND pads + EPAD */}
    {T(".U3 > .GND1", "net.GND")}{T(".U3 > .GND2", "net.GND")}
    {/* EPAD = 9 separate pads (ports GND_EP1..9), each tied to GND explicitly */}
    {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => T(`.U3 > .GND_EP${i}`, "net.GND"))}
    {T(".U3 > .V3V3", "net.V3V3")}
    {/* R7 m4: the 100 nF (C23) sits next to U3 pin 2 (3V3), the 10 uF (C22) behind it */}
    {/* R7 m4: the 100 nF (C23) sits next to U3 pin 2 (3V3), the 10 uF (C22) behind it */}
    {C("C23", "100nF", 46.9, 12.0, 90, "C49678", "0805")}
    {C("C22", "10uF", 46.9, 16.0, 90, "C15850", "0805")}
    {T(".C22 > .pin1", "net.V3V3")}{T(".C22 > .pin2", "net.GND")}
    {T(".C23 > .pin1", "net.V3V3")}{T(".C23 > .pin2", "net.GND")}

        {/* EN: pull-up + 1uF + RESET */}
    {R("R20", "10k", 44.4, 11.4, 270, "C17414")}
    {C("C20", "1uF", 38.6, 12.8, 180, "C28323", "0805")}
    <Tactile5x5 name="SW1" pcbX={33.5} pcbY={-23.5} pcbRotation={0} {...sch("SW1", [["A1", "A2"], ["B1", "B2"]])} />
    {T(".U3 > .EN", "net.EN")}
    {T(".R20 > .pin1", "net.V3V3")}{T(".R20 > .pin2", "net.EN")}
    {T(".C20 > .pin1", "net.EN")}{T(".C20 > .pin2", "net.GND")}
    {/* tactile: pads A1/A2 and B1/B2 are joined inside the switch, every pad is tied to its net explicitly */}
    {T(".SW1 > .A1", "net.EN")}{T(".SW1 > .A2", "net.EN")}{T(".SW1 > .B1", "net.GND")}{T(".SW1 > .B2", "net.GND")}

    {/* BOOT: GPIO0 + pull-up + button (bottom edge) */}
    <Tactile5x5 name="SW2" pcbX={34.0} pcbY={-14.8} pcbRotation={0} {...sch("SW2", [["A1", "A2"], ["B1", "B2"]])} />
    {R("R21", "10k", 28.0, -12.5, 90, "C17414")}
    {T(".U3 > .IO0", "net.BOOT")}
    {T(".R21 > .pin1", "net.V3V3")}{T(".R21 > .pin2", "net.BOOT")}
    {T(".SW2 > .A1", "net.BOOT")}{T(".SW2 > .A2", "net.BOOT")}{T(".SW2 > .B1", "net.GND")}{T(".SW2 > .B2", "net.GND")}

    {/* EMS UART: GPIO5 = MCU_RX, GPIO17 = ESP_TX (-> JP1 -> MCU_TX) */}
    {T(".U3 > .IO5", "net.MCU_RX")}
    {T(".U3 > .IO17", "net.ESP_TX")}

    {/* status LED GPIO2 (S32S3 profile: LED=GPIO2, active high) */}
    {R("R22", "330", 47.0, -12.5, 90, "C17630")}
    <LedYellow name="LD4" pcbX={47.0} pcbY={-16.5} pcbRotation={90} {...sch("LD4", ["A", "K"])} />
    {T(".U3 > .IO2", ".R22 > .pin1")}
    {T(".R22 > .pin2", ".LD4 > .A")}{T(".LD4 > .K", "net.GND")}

    {/* UART0 test pads */}
    <TestPad name="TP1" x={41.3} y={-13} />
    <TestPad name="TP2" x={43.2} y={-13} />
    <TestPad name="TP3" x={45.1} y={-13} />
    {T(".U3 > .TXD0", ".TP1 > .TP")}{T(".U3 > .RXD0", ".TP2 > .TP")}{T(".TP3 > .TP", "net.GND")}
    {/* the UART0 pad labels (TX RX G) were dropped: at >= 1 mm glyph height they do not fit between the router's vias (docs/ESP32_EMSESP.md lists the pads) */}

    {/* ---------------- USB-C at bottom edge ---------------- */}
    <UsbC16 name="J2" schWidth={2.12} pcbX={33} pcbY={22.43} pcbRotation={0} {...sch("J2")} />
    {/* every physical contact is its own port; the A/B duplicates are tied together by the nets (both plug orientations) */}
    {T(".J2 > .VBUS_L", "net.VBUS")}{T(".J2 > .VBUS_R", "net.VBUS")}
    {T(".J2 > .GND_L", "net.GND")}{T(".J2 > .GND_R", "net.GND")}
    {T(".J2 > .DP_L", "net.USB_DP")}{T(".J2 > .DP_R", "net.USB_DP")}
    {T(".J2 > .DN_L", "net.USB_DN")}{T(".J2 > .DN_R", "net.USB_DN")}
    {R("R23", "5.1k", 28.6, 19.2, 90, "C27834")}
    {R("R24", "5.1k", 37.0, 20.3, 90, "C27834")}
    {T(".J2 > .CC1", ".R23 > .pin1")}{T(".R23 > .pin2", "net.GND")}
    {T(".J2 > .CC2", ".R24 > .pin1")}{T(".R24 > .pin2", "net.GND")}
    {R("R25", "1M", 26.6, 26.5, 90, "C17514")}
    {C("C21", "4.7nF", 26.6, 23.0, 90, "C1744", "0805")}
    {["SH1", "SH2", "SH3", "SH4"].map((h) => T(`.J2 > .${h}`, "net.SHELL"))}
    {T(".R25 > .pin1", "net.SHELL")}{T(".C21 > .pin1", "net.SHELL")}
    {T(".R25 > .pin2", "net.GND")}{T(".C21 > .pin2", "net.GND")}

    {/* ESD: USBLC6-2SC6 pins 1,6 = I/O1; 3,4 = I/O2; 2 = GND; 5 = VBUS */}
    <PartDot part={{ pcbX: 32.3, pcbY: 17.4 }} lx={-2.35} ly={0.95} />
    <chip name="U4" pcbStyle={{ silkscreenTextVisibility: "hidden" }} footprint="sot23_6" manufacturerPartNumber="USBLC6-2SC6" supplierPartNumbers={J("C7519")}
      pcbX={32.3} pcbY={17.4} pcbRotation={0} {...sch("U4")}
      pinLabels={{ pin1: ["IO1a"], pin2: ["GND"], pin3: ["IO2a"], pin4: ["IO2b"], pin5: ["VBUS"], pin6: ["IO1b"] }}
      schPinArrangement={{ leftSide: { direction: "top-to-bottom", pins: ["IO1a", "IO2a", "GND"] }, rightSide: { direction: "top-to-bottom", pins: ["IO1b", "IO2b", "VBUS"] } }} />
    {T(".U4 > .IO1a", "net.USB_DP")}{T(".U4 > .IO1b", "net.USB_DP")}
    {T(".U4 > .IO2a", "net.USB_DN")}{T(".U4 > .IO2b", "net.USB_DN")}
    {T(".U4 > .GND", "net.GND")}{T(".U4 > .VBUS", "net.VBUS")}
    {T(".U3 > .IO19", "net.USB_DN")}{T(".U3 > .IO20", "net.USB_DP")}

    {/* VBUS PTC F3 (SMD1206B110TFT C269119: 1.1 A hold, 0.21 ohm max, 8 V; R6 m2 / R7 m9, replaces the 0.5 A 0805 type): connector side net VBUS (J2, U4 ESD) -> VBUS_F (U5, C24, C25) */}
    <chip name="F3" pcbStyle={{ silkscreenTextVisibility: "hidden" }} footprint={<Ptc1206Footprint />} pcbX={26.2} pcbY={15.0} pcbRotation={180} {...sch("F3")} manufacturerPartNumber="SMD1206B110TFT" supplierPartNumbers={J("C269119")}
      pinLabels={{ pin1: ["VBUS"], pin2: ["VBUS_F"] }} />
    {T(".F3 > .pin1", "net.VBUS")}{T(".F3 > .pin2", "net.VBUS_F")}

    {/* ---------------- LDO AMS1117-3.3, SOT-223: 1=GND/ADJ 2=VOUT 3=VIN 4(tab)=VOUT ---------------- */}
    <PartDot part={{ pcbX: 20.5, pcbY: 18.2, pcbRotation: 90 }} lx={-4.85} ly={2.3} />
    <chip name="U5" pcbStyle={{ silkscreenTextVisibility: "hidden" }} footprint="sot223" manufacturerPartNumber="AMS1117-3.3" supplierPartNumbers={J("C6186")}
      pcbX={20.5} pcbY={18.2} pcbRotation={90} {...sch("U5")}
      pinLabels={{ pin1: ["GND"], pin2: ["VOUT"], pin3: ["VIN"], pin4: ["TAB"] }}
      schPinArrangement={{ leftSide: { direction: "top-to-bottom", pins: ["VIN", "GND"] }, rightSide: { direction: "top-to-bottom", pins: ["VOUT", "TAB"] } }} />
    {T(".U5 > .VIN", "net.VBUS_F")}{T(".U5 > .GND", "net.GND")}
    {T(".U5 > .VOUT", "net.V3V3")}{T(".U5 > .TAB", "net.V3V3")}
    {C("C24", "10uF", 22.5, 11.6, 90, "C15850", "0805")}
    {C("C25", "100nF", 20.0, 11.6, 90, "C49678", "0805")}
    {T(".C24 > .pin1", "net.VBUS_F")}{T(".C24 > .pin2", "net.GND")}
    {T(".C25 > .pin1", "net.VBUS_F")}{T(".C25 > .pin2", "net.GND")}
    {/* tantalum 100 uF / 6.3 V (C16133, Basic) for AMS1117 output stability; pad 1 = + */}
    <TantalumB name="C29" pcbX={14.6} pcbY={18.3} pcbRotation={270} {...sch("C29", ["POS", "NEG"])} />
    {T(".C29 > .pin1", "net.V3V3")}{T(".C29 > .pin2", "net.GND")}
    {C("C26", "22uF", 6.5, 20, 90, "C12891", "1206")}
    {C("C27", "10uF", 14.8, 22.6, 90, "C15850", "0805")}
    {C("C28", "100nF", 7.0, 25.5, 180, "C49678", "0805")}
    {["C26", "C27", "C28"].map((c) => [T(`.${c} > .pin1`, "net.V3V3"), T(`.${c} > .pin2`, "net.GND")])}

    {/* power LED on V3V3 */}
    {R("R26", "330", 24.0, 8.5, 90, "C17630")}
    <LedYellow name="LD5" pcbX={28.0} pcbY={8.5} pcbRotation={90} {...sch("LD5", ["A", "K"])} />
    {T(".R26 > .pin1", "net.V3V3")}{T(".R26 > .pin2", ".LD5 > .A")}{T(".LD5 > .K", "net.GND")}

    {/* ---------------- JP1 (open) ESP_TX <-> MCU_TX, R_PU, P2 ---------------- */}
    <solderjumper name="JP1" pinCount={2} footprint={<SolderJumper2Footprint />} pcbX={21} pcbY={-9.5} pcbRotation={90} {...sch("JP1")} />
    {T(".JP1 > .pin1", "net.ESP_TX")}{T(".JP1 > .pin2", "net.MCU_TX")}
    <silkscreentext text="TX EN" pcbX={20} pcbY={-11.9} fontSize={FS} />
    {R("R27", "100k", 16.5, -9.5, 90, "C149504")}
    {T(".R27 > .pin1", "net.MCU_TX")}{T(".R27 > .pin2", "net.V3V3")}
    {/* JP2 (default OPEN): V3V3 -> P2 pin 1 (net P2_3V3); close only if the 3V3 rail of this board may feed the header */}
    <solderjumper name="JP2" pinCount={2} footprint={<SolderJumper2Footprint />} pcbX={26} pcbY={-21} pcbRotation={90} {...sch("JP2")} />
    {T(".JP2 > .pin1", "net.V3V3")}{T(".JP2 > .pin2", "net.P2_3V3")}
    <silkscreentext text="3V3 OUT" pcbX={22.5} pcbY={-18.3} fontSize={FS} />
    <PinHeader1x4 name="P2" schWidth={1.67} pcbX={12} pcbY={-26.5} pcbRotation={0} {...sch("P2")} />
    {T(".P2 > .pin1", "net.P2_3V3")}{T(".P2 > .pin2", "net.MCU_TX")}
    {T(".P2 > .pin3", "net.MCU_RX")}{T(".P2 > .pin4", "net.GND")}
  </group>
)
