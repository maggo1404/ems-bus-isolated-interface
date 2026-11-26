// EMS-ESP Isolated Interface V2.0 - complete board, for enclosure Hammond 1591XXCFLBK (docs/ENCLOSURE.md).
// Barrier line x = 0: EMS side at x < 0 (terminal P1 at the LEFT short edge), MCU/USB side at x > 0
// (ESP32 antenna at the RIGHT short edge, USB-C J2 at the top long edge); only OC1/OC2 straddle the barrier.
import { EmsSide } from "./src/ems-side"
import { McuSide } from "./src/mcu-side"
import { NetDefs } from "./lib/netdefs"

const W = 110, H = 60
const NX = 5.5, NY = 8.0, NR = 3.5 // corner notch (X, Y) for the lid-screw bosses, R3.5 on the inner corner
const SLOT_W = 2 // isolation slot width (mm), centred on x = 0
const SLOT_Y0 = 2, SLOT_Y1 = 14 // slot y-range |y| (opto body 9.6 mm + 2 mm), OC1 at y = 8, OC2 at y = -8
const POUR_GAP = 3.2 // pour edge distance from barrier centre (mm) -> 6.4 mm EMS<->MCU
const PM = 0.5 // pour margin to the board edge
const ANT_X = 48 // ANTENNA ZONE x >= 48 (module at x 29.5..55), |y| <= ANT_Y: no copper, no parts, both layers
const ANT_Y = 24 // 9 (half module width) + 15 mm
const HOLE_X = 42.25, HOLE_Y = 19.75 // M3/#4 screw holes 3.5 mm NPTH, 84.5 x 39.5 grid
const KEEP_R = 4 // copper/part keepout around each hole (screw head 8 mm)

// board outline, counter-clockwise from the lower left; the notch inner corners get an R3.5 fillet
type Pt = { x: number; y: number }
const arc = (cx: number, cy: number, a0: number, a1: number, n = 6): Pt[] =>
  Array.from({ length: n + 1 }, (_, i) => {
    const a = ((a0 + ((a1 - a0) * i) / n) * Math.PI) / 180
    return { x: +(cx + NR * Math.cos(a)).toFixed(3), y: +(cy + NR * Math.sin(a)).toFixed(3) }
  })
const hx = W / 2, hy = H / 2
const OUTLINE: Pt[] = [
  // bottom-left notch
  { x: -hx, y: -hy + NY }, { x: -hx + NX, y: -hy + NY },
  { x: -hx + NX, y: -hy + NY }, // fillet below (corner (-hx+NX, -hy+NY) rounded)
  { x: -hx + NX, y: -hy },
  // bottom edge -> bottom-right notch
  { x: hx - NX, y: -hy }, { x: hx - NX, y: -hy + NY }, { x: hx, y: -hy + NY },
  // right edge -> top-right notch
  { x: hx, y: hy - NY }, { x: hx - NX, y: hy - NY }, { x: hx - NX, y: hy },
  // top edge -> top-left notch
  { x: -hx + NX, y: hy }, { x: -hx + NX, y: hy - NY }, { x: -hx, y: hy - NY },
]
// replace the 4 inner notch corners by fillets (concave corner of the board, R3.5)
const OUTLINE_R: Pt[] = (() => {
  const o: Pt[] = []
  const c = (x: number, y: number, sx: number, sy: number) => {
    // corner at (x, y); sx/sy point from the corner into the board material along both notch edges
    const e0 = { x: x, y: y + sy * NR }, e1 = { x: x + sx * NR, y: y }
    return { e0, e1 }
  }
  void c
  return o
})()
void OUTLINE_R
// simple explicit polygon with fillets (ccw)
const fil = (cx: number, cy: number, a0: number, a1: number) => arc(cx, cy, a0, a1)
const BOARD: Pt[] = [
  { x: -hx, y: -hy + NY + 0 }, // left edge bottom (below the BL notch top)
  ...[] as Pt[],
]
void BOARD
const pts: Pt[] = [
  // start at left edge, just above the bottom-left notch, go clockwise... (ccw below)
  { x: -hx, y: -hy + NY },
  // BL notch: material boundary goes right along y = -hy+NY then DOWN along x = -hx+NX (fillet at the corner)
  ...fil(-hx + NX - NR + 0, -hy + NY - NR + 0, 90, 0).slice(0, 0),
  { x: -hx + NX - NR, y: -hy + NY }, ...fil(-hx + NX - NR, -hy + NY - NR, 90, 0), { x: -hx + NX, y: -hy },
  { x: hx - NX, y: -hy }, ...fil(hx - NX + NR, -hy + NY - NR, 180, 90), { x: hx - NX + NR, y: -hy + NY }, { x: hx, y: -hy + NY },
  { x: hx, y: hy - NY }, { x: hx - NX + NR, y: hy - NY }, ...fil(hx - NX + NR, hy - NY + NR, 270, 180), { x: hx - NX, y: hy },
  { x: -hx + NX, y: hy }, ...fil(-hx + NX - NR, hy - NY + NR, 360, 270), { x: -hx + NX - NR, y: hy - NY }, { x: -hx, y: hy - NY },
]
// remove consecutive duplicates
const outline = pts.filter((p, i) => i === 0 || p.x !== pts[i - 1].x || p.y !== pts[i - 1].y)

// pour outlines (inset PM from the board edge/notches; no pour beyond the antenna zone x >= 48 and none in the barrier)
const NXi = hx - NX - PM // x of the notch wall (inset), 49.0
const NYi = hy - NY - PM // y of the notch floor (inset), 21.5
const EMS_POUR = [
  { x: -POUR_GAP, y: hy - PM }, { x: -NXi, y: hy - PM }, { x: -NXi, y: NYi }, { x: -hx + PM, y: NYi },
  { x: -hx + PM, y: -NYi }, { x: -NXi, y: -NYi }, { x: -NXi, y: -hy + PM }, { x: -POUR_GAP, y: -hy + PM },
]
// V3V3 pour area for the AMS1117 tab (FIX_LIST #11): x 8..24.5, y 19..29.5 on both layers (~ 2 x 165 mm2 = 3.3 cm2)
const V_X0 = 8, V_X1 = 24.5, V_Y0 = 19, V_Y1 = 29.5
const VG = 0.6 // gap between the V3V3 pour and the GND pour
const MCU_POUR = [
  { x: POUR_GAP, y: hy - PM }, { x: V_X0 - VG, y: hy - PM }, { x: V_X0 - VG, y: V_Y0 - VG }, { x: V_X1 + VG, y: V_Y0 - VG },
  { x: V_X1 + VG, y: hy - PM }, { x: ANT_X - 0.4, y: hy - PM }, { x: ANT_X - 0.4, y: -hy + PM }, { x: POUR_GAP, y: -hy + PM },
]
const V3V3_POUR = [{ x: V_X0, y: V_Y0 }, { x: V_X1, y: V_Y0 }, { x: V_X1, y: V_Y1 }, { x: V_X0, y: V_Y1 }]

export default () => (
  <board outline={outline} layers={2} autorouterEffortLevel="5x" routeRemaining pcbStyle={{ silkscreenFontSize: "1mm" }}
    // fab rules, honoured by the autorouter (see docs/TSCIRCUIT_API.md "Fab settings"): via 0.3/0.6, min trace 0.25
    // (per-net widths via <trace thickness>, lib/netclass.ts), pad/trace/via clearance 0.25
    minTraceWidth="0.4mm" minViaHoleDiameter="0.3mm" minViaPadDiameter="0.6mm"
    minTraceToHoleEdgeClearance="0.25mm" minTraceToPadEdgeClearance="0.2mm" minPadEdgeToPadEdgeClearance="0.2mm" minViaEdgeToPadEdgeClearance="0.2mm"
    // paste apertures = 100 % of the pad (tscircuit default would be 70 % x 70 % = 49 % area, R5 M1)
    minViaHoleEdgeToViaHoleEdgeClearance="0.25mm"
    defaultSolderPasteMargin="0mm">
    <NetDefs />
    <EmsSide />
    <McuSide />

    {/* 4 x mounting holes 3.5 mm NPTH (84.5 x 39.5 grid of the Hammond 1591XX posts) + copper/part keepout 8 mm (screw head) */}
    {([[-1, 1, "MH1"], [-1, -1, "MH2"], [1, 1, "MH3"], [1, -1, "MH4"]] as const).map(([sx, sy, n]) => (
      <>
        <hole key={n} name={n} diameter="3.5mm" pcbX={sx * HOLE_X} pcbY={sy * HOLE_Y} />
        <keepout key={`k${n}`} shape="circle" radius={`${KEEP_R}mm`} pcbX={sx * HOLE_X} pcbY={sy * HOLE_Y} layers={["top", "bottom"]} />
      </>
    ))}

    {/* antenna zone: no copper and no parts on either layer beside/under the ESP32 antenna (>= 15 mm beside it) */}
    <keepout shape="rect" width={`${hx - ANT_X + 2}mm`} height={`${2 * ANT_Y}mm`} pcbX={(hx + ANT_X) / 2 + 1} pcbY={0} layers={["top", "bottom"]} />

    {/* isolation slots, 2 mm wide, only under the optocoupler bodies (body 9.6 mm + 2 mm), NOT to the board edge:
        the board stays one piece. tscircuit flags "component overlaps cutout" for OC1/OC2: intended. */}
    <cutout name="SLOT_TOP" shape="rect" width={`${SLOT_W}mm`} height={`${SLOT_Y1 - SLOT_Y0}mm`} pcbX={0} pcbY={(SLOT_Y0 + SLOT_Y1) / 2} />
    <cutout name="SLOT_BOT" shape="rect" width={`${SLOT_W}mm`} height={`${SLOT_Y1 - SLOT_Y0}mm`} pcbX={0} pcbY={-(SLOT_Y0 + SLOT_Y1) / 2} />

    {/* copper pours: GND_EMS only on the EMS side, GND only on the MCU side, both layers, 0.3 mm clearance */}
    {(["top", "bottom"] as const).map((layer) => (
      <copperpour key={`e${layer}`} layer={layer} connectsTo="net.GND_EMS" clearance="0.3mm" boardEdgeMargin="0.5mm" cutoutMargin="0.55mm" outline={EMS_POUR} />
    ))}
    {(["top", "bottom"] as const).map((layer) => (
      <copperpour key={`m${layer}`} layer={layer} connectsTo="net.GND" clearance="0.3mm" boardEdgeMargin="0.5mm" cutoutMargin="0.55mm" outline={MCU_POUR} />
    ))}
    {/* V3V3 heat spreader for the AMS1117 tab (both layers + thermal vias) */}
    {(["top", "bottom"] as const).map((layer) => (
      <copperpour key={`v${layer}`} layer={layer} connectsTo="net.V3V3" clearance="0.3mm" boardEdgeMargin="0.5mm" cutoutMargin="0.55mm" outline={V3V3_POUR} />
    ))}

    {/* thermal vias of the V3V3 heat spreader (AMS1117 tab): top pour <-> bottom pour, 2 x 4 grid beside the tab */}
    {[25.0, 27.5].flatMap((y) => [13.0, 16.0, 19.0, 22.0].map((x) => (
      <via key={`tv${x}_${y}`} pcbX={x} pcbY={y} fromLayer="top" toLayer="bottom" holeDiameter="0.3mm" outerDiameter="0.6mm" connectsTo="net.V3V3" />
    )))}

    {/* silkscreen */}
    <silkscreentext text="EMS-ESP Isolated Interface V2.0" pcbX={-14} pcbY={28.2} fontSize="1.0mm" />
    <silkscreentext text="PWR" pcbX={-8} pcbY={26.2} fontSize="1.0mm" />
    <silkscreentext text="RX" pcbX={13.2} pcbY={13.6} fontSize="1.0mm" />
    <silkscreentext text="TX" pcbX={10.0} pcbY={-13.8} fontSize="1.0mm" />
    <silkscreentext text="3V3" pcbX={26.0} pcbY={5.9} fontSize="1.0mm" />
    <silkscreentext text="EMS SIDE (bus powered)" pcbX={-27} pcbY={-28.0} fontSize="1.0mm" />
    <silkscreentext text="MCU / USB SIDE" pcbX={20} pcbY={-29.0} fontSize="1.0mm" />
    <silkscreentext text="ISOLATION BARRIER" pcbX={0} pcbY={0} fontSize="1.0mm" />
    <silkscreenpath route={[{ x: 0, y: SLOT_Y1 + 0.5 }, { x: 0, y: 29 }]} />
    <silkscreenpath route={[{ x: 0, y: -SLOT_Y1 - 0.5 }, { x: 0, y: -29 }]} />
    <silkscreentext text="P2 3V3(JP2) TX RX GND" pcbX={16.5} pcbY={-23.9} fontSize="1.0mm" />
  </board>
)
