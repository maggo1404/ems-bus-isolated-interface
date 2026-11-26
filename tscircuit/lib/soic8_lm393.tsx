// SOIC-8 for U1 LM393DR (JLC C7955), copied from the EasyEDA footprint SOIC-8_L5.0-W4.0-P1.27-LS6.0-BL (scratch/easyeda/C7955.json).
// Frame = EasyEDA frame (y up): pads 0.568 (x) x 1.95 (y) at y = -/+2.705 (row centre-to-centre 5.41 mm, outer 7.4 mm),
// pin 1 at (-1.905, -2.705), pins 1-4 along the bottom row to +x, pins 5-8 along the top row back to -x (counter-clockwise).
// The CPL file therefore needs no extra rotation offset (scripts/cpl_check.py fits the same frame).  U1 is placed with pcbRotation 270,
// which puts pin 1 at the top-left (pins 1-4 down the left column) like the generic soic8 it replaces.
export const Soic8Lm393Footprint = () => {
  const xs = [-1.905, -0.635, 0.635, 1.905]
  return (
    <footprint>
      {xs.map((x, i) => (
        <smtpad key={`b${i}`} portHints={[`pin${i + 1}`]} shape="rect" width="0.568mm" height="1.95mm" pcbX={x} pcbY={-2.705} />
      ))}
      {xs.map((x, i) => (
        <smtpad key={`t${i}`} portHints={[`pin${8 - i}`]} shape="rect" width="0.568mm" height="1.95mm" pcbX={x} pcbY={2.705} />
      ))}
      {/* body 5.0 x 3.9: side lines only between the pad rows (no silk on pads) + pin-1 dot */}
      <silkscreenpath route={[{ x: -2.55, y: -1.5 }, { x: -2.55, y: 1.5 }]} />
      <silkscreenpath route={[{ x: 2.55, y: -1.5 }, { x: 2.55, y: 1.5 }]} />
      <silkscreencircle pcbX={-3.1} pcbY={-3.2} radius="0.25mm" />
    </footprint>
  )
}
