// EMS-ESP Isolated Interface V2.0 - complete board.
// Barrier line x = 0: EMS side at x < 0, MCU/USB side at x > 0; only OC1/OC2 straddle it.
import { EmsSide } from "./src/ems-side"
import { McuSide } from "./src/mcu-side"

const W = 110, H = 60
const SLOT_W = 2 // isolation slot width (mm), centred on x = 0
const POUR_GAP = 3 // pour edge distance from barrier centre (mm)
const ANT_X = 47.95 // start of the ESP32 antenna keepout (mm)

export default () => (
  <board width={`${W}mm`} height={`${H}mm`} layers={2} borderRadius="2mm"
    // fab rules, honoured by the autorouter (see docs/TSCIRCUIT_API.md "Fab settings"): via 0.3/0.6, min trace 0.2
    // (per-net widths via <trace thickness>, lib/netclass.ts), pad/trace/via clearance 0.25
    minTraceWidth="0.2mm" minViaHoleDiameter="0.3mm" minViaPadDiameter="0.6mm"
    minTraceToPadEdgeClearance="0.25mm" minPadEdgeToPadEdgeClearance="0.25mm" minViaEdgeToPadEdgeClearance="0.25mm">
    <EmsSide />
    <McuSide />

    {/* 4 x M3 mounting holes (3.2 mm NPTH), >= 6 mm from the other side's copper */}
    <hole name="MH1" diameter="3.2mm" pcbX={-52} pcbY={27.8} />
    <hole name="MH2" diameter="3.2mm" pcbX={-51} pcbY={-26} />
    <hole name="MH3" diameter="3.2mm" pcbX={8} pcbY={26.5} />
    <hole name="MH4" diameter="3.2mm" pcbX={52} pcbY={-26} />

    {/* isolation slots, 2 mm wide: from the board edge down to y = +-3.3, i.e. under each optocoupler body
        (between its pad rows, pad inner edges at x = +-3.85). A 6.6 mm bridge at y in [-3.3, 3.3] keeps the
        board in one piece; no copper crosses it. tscircuit flags "component overlaps cutout" for OC1/OC2:
        intended, built with --ignore-placement-drc. */}
    <cutout name="SLOT_TOP" shape="rect" width={`${SLOT_W}mm`} height="27.2mm" pcbX={0} pcbY={16.9} />
    <cutout name="SLOT_BOT" shape="rect" width={`${SLOT_W}mm`} height="27.2mm" pcbX={0} pcbY={-16.9} />

    {/* copper pours: GND_EMS only on the EMS side, GND only on the MCU side, both layers */}
    {(["top", "bottom"] as const).map((layer) => (
      <copperpour key={`e${layer}`} layer={layer} connectsTo="net.GND_EMS"
        outline={[{ x: -W / 2, y: H / 2 }, { x: -POUR_GAP, y: H / 2 }, { x: -POUR_GAP, y: -H / 2 }, { x: -W / 2, y: -H / 2 }]} />
    ))}
    {/* MCU pour: notch for the ESP32 antenna keepout (x >= 47.95, |y| <= 9.5; module at x 29.5..55) */}
    {(["top", "bottom"] as const).map((layer) => (
      <copperpour key={`m${layer}`} layer={layer} connectsTo="net.GND"
        outline={[
          { x: POUR_GAP, y: H / 2 }, { x: W / 2, y: H / 2 }, { x: W / 2, y: 9.5 }, { x: ANT_X, y: 9.5 },
          { x: ANT_X, y: -9.5 }, { x: W / 2, y: -9.5 }, { x: W / 2, y: -H / 2 }, { x: POUR_GAP, y: -H / 2 },
        ]} />
    ))}

    {/* silkscreen */}
    <silkscreentext text="EMS-ESP Isolated Interface V2.0" pcbX={-27} pcbY={28.2} fontSize="1.6mm" />
    <silkscreentext text="EMS BUS" pcbX={-50} pcbY={-8} fontSize="1.2mm" />
    <silkscreentext text="EMS SIDE (bus powered)" pcbX={-27} pcbY={-27.5} fontSize="1.0mm" />
    <silkscreentext text="MCU / USB SIDE" pcbX={41} pcbY={-28.5} fontSize="1.0mm" />
    <silkscreentext text="ISOLATION BARRIER" pcbX={0} pcbY={0} fontSize="0.8mm" />
    <silkscreenpath route={[{ x: 0, y: 3.6 }, { x: 0, y: 30 }]} />
    <silkscreenpath route={[{ x: 0, y: -3.6 }, { x: 0, y: -30 }]} />
    <silkscreentext text="P2: 1=3V3(JP2) 2=TX 3=RX 4=GND" pcbX={22} pcbY={-29} fontSize="0.8mm" />
  </board>
)
