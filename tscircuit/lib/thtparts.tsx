// THT / odd footprints taken from Eagle EMSinterface_V1.0.lbr
import type { ChipProps } from "tscircuit"

// 2-pin 5.08 mm header KF2EDGRC-5.08-2P (JLC C441236; replaces Phoenix MSTBA): pads 2.5 mm, drill 1.8 mm, pin1 left
export const Mstba2 = (props: Partial<ChipProps> & { name: string }) => (
  <chip
    manufacturerPartNumber="KF2EDGRC-5.08-2P"
    supplierPartNumbers={{ jlcpcb: ["C441236"] }}
    pinLabels={{ pin1: ["P1"], pin2: ["P2"] }}
    footprint={
      <footprint>
        <platedhole portHints={["pin1"]} shape="circle" holeDiameter="1.8mm" outerDiameter="2.5mm" pcbX={-2.54} pcbY={0} />
        <platedhole portHints={["pin2"]} shape="circle" holeDiameter="1.8mm" outerDiameter="2.5mm" pcbX={2.54} pcbY={0} />
        <silkscreenpath route={[{ x: -5.0, y: 4.6 }, { x: 5.0, y: 4.6 }, { x: 5.0, y: -4.6 }, { x: -5.0, y: -4.6 }, { x: -5.0, y: 4.6 }]} />
      </footprint>
    }
    {...(props as any)}
  />
)

// SMD aluminium electrolytic 1000uF/25V, JVJ25V1000M10X12 (JLC C49256851), EasyEDA CAP-SMD_BD10.0-L10.3-W10.3-LS11.0-FD:
// pads 4.5 x 1.65 mm at x = +-4.5; pad 1 = POSITIVE (left, chamfered body corner = + side), pad 2 = NEGATIVE.
export const CapE5_10p5 = (props: Partial<ChipProps> & { name: string }) => (
  <chip
    pinLabels={{ pin1: ["POS"], pin2: ["NEG"] }}
    manufacturerPartNumber="JVJ25V1000M10X12"
    supplierPartNumbers={{ jlcpcb: ["C49256851"] }}
    footprint={
      <footprint>
        <smtpad portHints={["pin1"]} shape="rect" width="4.5mm" height="1.65mm" pcbX={-4.5} pcbY={0} />
        <smtpad portHints={["pin2"]} shape="rect" width="4.5mm" height="1.65mm" pcbX={4.5} pcbY={0} />
        {/* body outline 10.4 x 10.4, chamfered on the + side (left); side lines stop short of the pads */}
        <silkscreenpath route={[{ x: -5.2, y: 1.5 }, { x: -5.2, y: 3.1 }, { x: -3.1, y: 5.2 }, { x: 5.2, y: 5.2 }, { x: 5.2, y: 1.5 }]} />
        <silkscreenpath route={[{ x: -5.2, y: -1.5 }, { x: -5.2, y: -3.1 }, { x: -3.1, y: -5.2 }, { x: 5.2, y: -5.2 }, { x: 5.2, y: -1.5 }]} />
        <silkscreentext text="+" pcbX={-3.2} pcbY={3.2} fontSize="1.6mm" />
        <silkscreentext text="+" pcbX={-7.4} pcbY={2.0} fontSize="1.6mm" />
      </footprint>
    }
    {...(props as any)}
  />
)

// Inductor 3225 (L3225M in lbr): pads 1.6 x 2.2 at +-1.4 mm
export const Inductor3225 = (props: Partial<ChipProps> & { name: string }) => (
  <chip pinLabels={{ pin1: ["A"], pin2: ["B"] }}
    manufacturerPartNumber="LQH32PN4R7NN0L"
    supplierPartNumbers={{ jlcpcb: ["C98021"] }}
    footprint={<footprint>
      <smtpad portHints={["pin1"]} shape="rect" width="1.6mm" height="2.2mm" pcbX={-1.4} pcbY={0} />
      <smtpad portHints={["pin2"]} shape="rect" width="1.6mm" height="2.2mm" pcbX={1.4} pcbY={0} />
    </footprint>}
    {...(props as any)} />
)

// Inductor 5x5x2 SWPA5020S4R7MT (JLC C43183): pads 2.124 x 4.22 mm at x = +-2.0 mm
export const Inductor0520 = (props: Partial<ChipProps> & { name: string }) => (
  <chip pinLabels={{ pin1: ["A"], pin2: ["B"] }}
    manufacturerPartNumber="SWPA5020S4R7MT"
    supplierPartNumbers={{ jlcpcb: ["C43183"] }}
    footprint={<footprint>
      <smtpad portHints={["pin1"]} shape="rect" width="2.124mm" height="4.22mm" pcbX={-2.0} pcbY={0} />
      <smtpad portHints={["pin2"]} shape="rect" width="2.124mm" height="4.22mm" pcbX={2.0} pcbY={0} />
    </footprint>}
    {...(props as any)} />
)

// Resistor 2010 (CL2010FN68RB, JLC C53284030) with the lbr's pad dims (1.8 x 2.7 at +-2.2 mm)
export const Res2010Footprint = () => (
  <footprint>
    <smtpad portHints={["pin1"]} shape="rect" width="1.8mm" height="2.7mm" pcbX={-2.2} pcbY={0} />
    <smtpad portHints={["pin2"]} shape="rect" width="1.8mm" height="2.7mm" pcbX={2.2} pcbY={0} />
  </footprint>
)

// Tactile switch SMD 5.1 x 5.1, TS-1187A-B-A-B (JLC C318884), EasyEDA SW-SMD_4P-L5.1-W5.1-P3.70-LS6.5.
// Pads 1+2 (top row, y=+1.85) are one terminal (A), pads 3+4 (bottom row, y=-1.85) the other (B);
// pressing the button connects the two rows.
export const Tactile5x5 = (props: Partial<ChipProps> & { name: string }) => (
  <chip pinLabels={{ pin1: ["A"], pin2: ["B"] }}
    manufacturerPartNumber="TS-1187A-B-A-B"
    supplierPartNumbers={{ jlcpcb: ["C318884"] }}
    footprint={<footprint>
      {[-3.0, 3.0].map((x) => (
        <smtpad key={`a${x}`} portHints={["pin1"]} shape="rect" width="1.0mm" height="0.75mm" pcbX={x} pcbY={1.85} />
      ))}
      {[-3.0, 3.0].map((x) => (
        <smtpad key={`b${x}`} portHints={["pin2"]} shape="rect" width="1.0mm" height="0.75mm" pcbX={x} pcbY={-1.85} />
      ))}
      <silkscreenpath route={[{ x: -2.55, y: 2.55 }, { x: 2.55, y: 2.55 }, { x: 2.55, y: -2.55 }, { x: -2.55, y: -2.55 }, { x: -2.55, y: 2.55 }]} />
    </footprint>}
    {...(props as any)} />
)
