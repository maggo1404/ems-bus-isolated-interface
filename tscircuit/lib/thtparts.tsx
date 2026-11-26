// THT / odd footprints taken from Eagle EMSinterface_V1.0.lbr
import type { ChipProps } from "tscircuit"

// Phoenix MSTBA 2,5/2-G-5,08 : 2 pins, 5.08 mm pitch, drill 1.397 (lbr), pin1 left
export const Mstba2 = (props: Partial<ChipProps> & { name: string }) => (
  <chip
    manufacturerPartNumber="MSTBA 2,5/2-G-5,08"
    pinLabels={{ pin1: ["P1"], pin2: ["P2"] }}
    footprint={
      <footprint>
        <platedhole portHints={["pin1"]} shape="circle" holeDiameter="1.4mm" outerDiameter="2.8mm" pcbX={-2.54} pcbY={0} />
        <platedhole portHints={["pin2"]} shape="circle" holeDiameter="1.4mm" outerDiameter="2.8mm" pcbX={2.54} pcbY={0} />
        <silkscreenpath route={[{ x: -5.0, y: 4.6 }, { x: 5.0, y: 4.6 }, { x: 5.0, y: -4.6 }, { x: -5.0, y: -4.6 }, { x: -5.0, y: 4.6 }]} />
      </footprint>
    }
    {...(props as any)}
  />
)

// Electrolytic E5-10.5 (radial, 5.08 mm pitch, D=10.5 mm); lbr: drill 1.016, pad 2.54
export const CapE5_10p5 = (props: Partial<ChipProps> & { name: string }) => (
  <chip
    pinLabels={{ pin1: ["POS"], pin2: ["NEG"] }}
    footprint={
      <footprint>
        <platedhole portHints={["pin1"]} shape="circle" holeDiameter="1.016mm" outerDiameter="2.54mm" pcbX={-2.54} pcbY={0} />
        <platedhole portHints={["pin2"]} shape="circle" holeDiameter="1.016mm" outerDiameter="2.54mm" pcbX={2.54} pcbY={0} />
        <silkscreencircle radius="5.25mm" pcbX={0} pcbY={0} />
        <silkscreentext text="+" pcbX={-4.3} pcbY={3.5} fontSize="1.5mm" />
      </footprint>
    }
    {...(props as any)}
  />
)

// Inductor 3225 (L3225M in lbr): pads 1.6 x 2.2 at +-1.4 mm
export const Inductor3225 = (props: Partial<ChipProps> & { name: string }) => (
  <chip pinLabels={{ pin1: ["A"], pin2: ["B"] }}
    footprint={<footprint>
      <smtpad portHints={["pin1"]} shape="rect" width="1.6mm" height="2.2mm" pcbX={-1.4} pcbY={0} />
      <smtpad portHints={["pin2"]} shape="rect" width="1.6mm" height="2.2mm" pcbX={1.4} pcbY={0} />
    </footprint>}
    {...(props as any)} />
)

// Inductor 0520 (INDUCTOR_0520 in lbr): pads 2.0 x 2.5 at +-2.5 mm
export const Inductor0520 = (props: Partial<ChipProps> & { name: string }) => (
  <chip pinLabels={{ pin1: ["A"], pin2: ["B"] }}
    footprint={<footprint>
      <smtpad portHints={["pin1"]} shape="rect" width="2.0mm" height="2.5mm" pcbX={-2.5} pcbY={0} />
      <smtpad portHints={["pin2"]} shape="rect" width="2.0mm" height="2.5mm" pcbX={2.5} pcbY={0} />
    </footprint>}
    {...(props as any)} />
)

// Resistor 2010 with the lbr's pad dims (1.8 x 2.7 at +-2.2 mm)
export const Res2010Footprint = () => (
  <footprint>
    <smtpad portHints={["pin1"]} shape="rect" width="1.8mm" height="2.7mm" pcbX={-2.2} pcbY={0} />
    <smtpad portHints={["pin2"]} shape="rect" width="1.8mm" height="2.7mm" pcbX={2.2} pcbY={0} />
  </footprint>
)

// Tactile switch SMD 5.1 x 5.1 (e.g. TS-1187A-B-A-B). Two pads per side share a port.
// Pad positions approximate (verify against vendor drawing).
export const Tactile5x5 = (props: Partial<ChipProps> & { name: string }) => (
  <chip pinLabels={{ pin1: ["A"], pin2: ["B"] }}
    footprint={<footprint>
      {[-1.85, 1.85].map((y) => (
        <smtpad key={`a${y}`} portHints={["pin1"]} shape="rect" width="1.4mm" height="1.0mm" pcbX={-3.0} pcbY={y} />
      ))}
      {[-1.85, 1.85].map((y) => (
        <smtpad key={`b${y}`} portHints={["pin2"]} shape="rect" width="1.4mm" height="1.0mm" pcbX={3.0} pcbY={y} />
      ))}
      <silkscreenpath route={[{ x: -2.55, y: 2.55 }, { x: 2.55, y: 2.55 }, { x: 2.55, y: -2.55 }, { x: -2.55, y: -2.55 }, { x: -2.55, y: 2.55 }]} />
    </footprint>}
    {...(props as any)} />
)
