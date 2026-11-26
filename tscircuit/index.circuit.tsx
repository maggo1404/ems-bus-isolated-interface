// EMS-ESP Isolated Interface V2.0 - complete board, 110 x 70 mm rectangle, 3D-printed enclosure (enclosure/, docs/ENCLOSURE.md).
// Barrier line x = 0: EMS side at x < 0 (terminal P1 at the LEFT short edge), MCU/USB side at x > 0
// (ESP32 antenna at the RIGHT short edge, USB-C J2 at the top long edge); only OC1/OC2 straddle the barrier.
import { EmsSide } from "./src/ems-side"
import { McuSide } from "./src/mcu-side"
import { NetDefs } from "./lib/netdefs"
import { FS } from "./lib/silk"
import { SchAnnotations } from "./lib/schannot"

const SLOT_W = 2 // isolation slot width (mm), centred on x = 0
const SLOT_Y0 = 2, SLOT_Y1 = 14 // slot y-range |y| (opto body 9.6 mm + 2 mm), OC1 at y = 8, OC2 at y = -8
const POUR_GAP = 3.2 // pour edge distance from barrier centre (mm) -> 6.4 mm EMS<->MCU
const PM = 0.5 // pour margin to the board edge
const ANT_X = 48 // ANTENNA ZONE x >= 48 (module at x 29.5..55), |y| <= ANT_Y: no copper, no parts, both layers
const ANT_Y = 24 // 9 (half module width) + 15 mm
const HOLE_X = 42.25, HOLE_Y = 19.75 // M3/#4 screw holes 3.5 mm NPTH, 84.5 x 39.5 grid
const KEEP_R = 4 // copper/part keepout around each hole (screw head 8 mm)

// board outline: plain rectangle 110 x 70 mm, sharp 90 deg corners (no notches, no radius, no panel rails).
// x -55..55, y -40..30: the board is 10 mm longer than the earlier 110 x 60 at the BOTTOM only, so that no part/trace moves
// (J2 stays flush on the top edge, P1 on the left edge, the antenna on the right edge); 70 x 70 mm minimum for JLC Economic delivery.
const X0 = -55, X1 = 55, Y0 = -40, Y1 = 30
const outline = [{ x: X0, y: Y0 }, { x: X1, y: Y0 }, { x: X1, y: Y1 }, { x: X0, y: Y1 }]

// pour outlines (inset PM from the board edge; no pour beyond the antenna zone x >= 48 and none in the barrier, which runs straight down to the bottom edge)
const EMS_POUR = [
  { x: -POUR_GAP, y: Y1 - PM }, { x: X0 + PM, y: Y1 - PM }, { x: X0 + PM, y: Y0 + PM }, { x: -POUR_GAP, y: Y0 + PM },
]
// V3V3 pour area for the AMS1117 tab (FIX_LIST #11): x 8..24.5, y 19..29.5 on both layers (~ 2 x 165 mm2 = 3.3 cm2)
const V_X0 = 8, V_X1 = 24.5, V_Y0 = 19, V_Y1 = 29.5
const VG = 0.8 // gap between the V3V3 pour and the GND pour
const MCU_POUR = [
  { x: POUR_GAP, y: Y1 - PM }, { x: V_X0 - VG, y: Y1 - PM }, { x: V_X0 - VG, y: V_Y0 - VG }, { x: V_X1 + VG, y: V_Y0 - VG },
  { x: V_X1 + VG, y: Y1 - PM }, { x: ANT_X - 1.4, y: Y1 - PM }, { x: ANT_X - 1.4, y: Y0 + PM }, { x: POUR_GAP, y: Y0 + PM },
]
const V3V3_POUR = [{ x: V_X0, y: V_Y0 }, { x: V_X1, y: V_Y0 }, { x: V_X1, y: V_Y1 }, { x: V_X0, y: V_Y1 }]

export default () => (
  <board outline={outline} layers={2} autorouterEffortLevel="5x" routeRemaining pcbStyle={{ silkscreenFontSize: "1.85mm" }}
    // fab rules, honoured by the autorouter (see docs/TSCIRCUIT_API.md "Fab settings"): via 0.3/0.6, min trace 0.25
    // (per-net widths via <trace thickness>, lib/netclass.ts), pad/trace/via clearance 0.25
    minTraceWidth="0.4mm" minViaHoleDiameter="0.3mm" minViaPadDiameter="0.6mm"
    minTraceToHoleEdgeClearance="0.25mm" minTraceToPadEdgeClearance="0.2mm" minPadEdgeToPadEdgeClearance="0.2mm" minViaEdgeToPadEdgeClearance="0.2mm"
    // paste apertures = 100 % of the pad (tscircuit default would be 70 % x 70 % = 49 % area, R5 M1)
    minViaHoleEdgeToViaHoleEdgeClearance="0.5mm"
    defaultSolderPasteMargin="0mm">
    <NetDefs />
    <EmsSide />
    <McuSide />
    <SchAnnotations />

    {/* 4 x mounting holes 3.5 mm NPTH (84.5 x 39.5 grid of the printed-case posts, formerly Hammond 1591XX) + copper/part keepout 8 mm (screw head) */}
    {([[-1, 1, "MH1"], [-1, -1, "MH2"], [1, 1, "MH3"], [1, -1, "MH4"]] as const).map(([sx, sy, n]) => (
      <>
        <hole key={n} name={n} diameter="3.5mm" pcbX={sx * HOLE_X} pcbY={sy * HOLE_Y} />
        <keepout key={`k${n}`} shape="circle" radius={`${KEEP_R}mm`} pcbX={sx * HOLE_X} pcbY={sy * HOLE_Y} layers={["top", "bottom"]} />
      </>
    ))}

    {/* antenna zone: no copper and no parts on either layer beside/under the ESP32 antenna (>= 15 mm beside it) */}
    <keepout shape="rect" width={`${X1 - ANT_X + 2}mm`} height={`${2 * ANT_Y}mm`} pcbX={(X1 + ANT_X) / 2 + 1} pcbY={0} layers={["top", "bottom"]} />

    {/* isolation slots, 2 mm wide, only under the optocoupler bodies (body 9.6 mm + 2 mm), NOT to the board edge:
        the board stays one piece. tscircuit flags "component overlaps cutout" for OC1/OC2: intended. */}
    <cutout name="SLOT_TOP" shape="rect" width={`${SLOT_W}mm`} height={`${SLOT_Y1 - SLOT_Y0}mm`} pcbX={0} pcbY={(SLOT_Y0 + SLOT_Y1) / 2} />
    <cutout name="SLOT_BOT" shape="rect" width={`${SLOT_W}mm`} height={`${SLOT_Y1 - SLOT_Y0}mm`} pcbX={0} pcbY={-(SLOT_Y0 + SLOT_Y1) / 2} />

    {/* copper pours: GND_EMS only on the EMS side, GND only on the MCU side, both layers, 0.25 mm clearance (R7 m2: no slivers < 0.15 mm) */}
    {(["top", "bottom"] as const).map((layer) => (
      <copperpour key={`e${layer}`} layer={layer} connectsTo="net.GND_EMS" clearance="0.25mm" boardEdgeMargin="0.5mm" cutoutMargin="0.55mm" outline={EMS_POUR} />
    ))}
    {(["top", "bottom"] as const).map((layer) => (
      <copperpour key={`m${layer}`} layer={layer} connectsTo="net.GND" clearance="0.25mm" boardEdgeMargin="0.5mm" cutoutMargin="0.55mm" outline={MCU_POUR} />
    ))}
    {/* V3V3 heat spreader for the AMS1117 tab (both layers + thermal vias) */}
    {(["top", "bottom"] as const).map((layer) => (
      <copperpour key={`v${layer}`} layer={layer} connectsTo="net.V3V3" clearance="0.25mm" boardEdgeMargin="0.5mm" cutoutMargin="0.55mm" outline={V3V3_POUR} />
    ))}

    {/* thermal vias of the V3V3 heat spreader (AMS1117 tab): top pour <-> bottom pour, 2 x 4 grid beside the tab */}
    {[25.0, 27.5].flatMap((y) => [13.0, 16.0, 19.0, 22.0].map((x) => (
      <via key={`tv${x}_${y}`} pcbX={x} pcbY={y} fromLayer="top" toLayer="bottom" holeDiameter="0.3mm" outerDiameter="0.6mm" connectsTo="net.V3V3" />
    )))}

    {/* silkscreen: every text >= 1.0 mm glyph height (fontSize 1.85 mm, R7 M1); descriptive texts sit on free areas, the title on the bottom side */}
    <silkscreentext text="EMS-ESP Isolated Interface V2.0" pcbX={0} pcbY={26.5} layer="bottom" fontSize={FS} />
    <silkscreentext text="PWR" pcbX={-8} pcbY={26.2} fontSize={FS} />
    <silkscreentext text="RX" pcbX={13.2} pcbY={13.6} fontSize={FS} />
    <silkscreentext text="TX" pcbX={10.0} pcbY={-13.8} fontSize={FS} />
    <silkscreentext text="3V3" pcbX={26.0} pcbY={5.9} fontSize={FS} />
    <silkscreentext text="RESET" pcbX={33.5} pcbY={-28.2} fontSize={FS} />
    <silkscreentext text="BOOT" pcbX={27.6} pcbY={-14.8} fontSize={FS} />
    <silkscreentext text="EMS SIDE" pcbX={-27.5} pcbY={-35} fontSize={FS} />
    <silkscreentext text="MCU SIDE" pcbX={27.5} pcbY={-35} fontSize={FS} />
    <silkscreentext text="ISOLATION" pcbX={0} pcbY={0} fontSize={FS} />
    <silkscreenpath route={[{ x: 0, y: SLOT_Y1 + 0.5 }, { x: 0, y: 29 }]} />
    <silkscreenpath route={[{ x: 0, y: -SLOT_Y1 - 0.5 }, { x: 0, y: -33.5 }]} />
    {/* P2 pin labels (vertical, one per pin of the 2.54 mm header at x = 8.19 / 10.73 / 13.27 / 15.81, y = -26.5) */}
    <silkscreentext text="3V3" pcbX={8.19} pcbY={-23.2} pcbRotation={90} fontSize={FS} />
    <silkscreentext text="TX" pcbX={10.73} pcbY={-22.9} pcbRotation={90} fontSize={FS} />
    <silkscreentext text="RX" pcbX={13.27} pcbY={-22.9} pcbRotation={90} fontSize={FS} />
    <silkscreentext text="GND" pcbX={15.81} pcbY={-23.2} pcbRotation={90} fontSize={FS} />
  </board>
)
