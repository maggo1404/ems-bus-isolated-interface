// Silkscreen helpers (R7 M1/m6): JLC wants characters >= 1.0 mm high and strokes >= 0.153 mm.
// tscircuit's stroke font has a cap height of ~0.475 x fontSize, so fontSize 1.85 mm gives a glyph envelope of ~1.04 mm incl. the 0.17 mm stroke
// (scripts/check_fab.py G5 measures the real glyph height in the silk Gerber).
export const FS = "1.85mm"
export const MARK_STROKE = "0.16mm"

/** polarity '+' as two short strokes (a '+' glyph would be < 1 mm high even at 1.6 mm font size) */
export const Plus = ({ x, y, s = 0.65 }: { x: number; y: number; s?: number }) => (
  <>
    <silkscreenpath route={[{ x: x - s, y }, { x: x + s, y }]} />
    <silkscreenpath route={[{ x, y: y - s }, { x, y: y + s }]} />
  </>
)

/** pin-1 dot (ring, 0.3 mm radius + 0.16 mm stroke); coordinates in the frame of the surrounding footprint / board */
export const Dot = ({ x, y, r = 0.3 }: { x: number; y: number; r?: number }) => (
  <silkscreencircle pcbX={x} pcbY={y} radius={`${r}mm`} strokeWidth={MARK_STROKE} />
)

export type Placed = { pcbX: number; pcbY: number; pcbRotation?: number }
/** local part coordinates -> board coordinates of a part placed at (pcbX, pcbY) with pcbRotation (deg, CCW) */
export const toWorld = (p: Placed, lx: number, ly: number) => {
  const a = ((p.pcbRotation ?? 0) * Math.PI) / 180
  return { x: +(p.pcbX + lx * Math.cos(a) - ly * Math.sin(a)).toFixed(3), y: +(p.pcbY + lx * Math.sin(a) + ly * Math.cos(a)).toFixed(3) }
}

/** board-level pin-1 dot of a part (footprinter packages have no pin-1 mark of their own) */
export const PartDot = ({ part, lx, ly }: { part: Placed; lx: number; ly: number }) => {
  const w = toWorld(part, lx, ly)
  return <Dot x={w.x} y={w.y} />
}

/** board-level cathode bar of a 2-pad SOD-123 diode (bar between the pads at local x = side * 0.9, y +-0.75) */
export const CathodeBar = ({ part, side }: { part: Placed; side: 1 | -1 }) => {
  const a = toWorld(part, side * 0.9, -0.75), b = toWorld(part, side * 0.9, 0.75)
  return <silkscreenpath route={[a, b]} />
}
