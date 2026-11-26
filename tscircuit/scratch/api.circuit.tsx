export default () => (
  <board width="40mm" height="30mm" layers={2}>
    <net name="GND" />
    <chip
      name="U1"
      footprint="soic8"
      pinLabels={{ pin1: "A", pin2: "K", pin3: "NC", pin4: "GND", pin5: "VCC", pin6: "OUT", pin7: "EN", pin8: "VCC2" }}
      schPinArrangement={{ leftSide: { direction: "top-to-bottom", pins: ["A", "K"] }, rightSide: { direction: "top-to-bottom", pins: ["OUT", "VCC"] } }}
      supplierPartNumbers={{ jlcpcb: ["C7950"] }}
      pcbX={-8} pcbY={5} schX={0} schY={0}
    />
    <chip
      name="U2"
      pcbX={8} pcbY={5}
      pinLabels={{ pin1: "P1", pin2: "P2" }}
      footprint={
        <footprint>
          <smtpad portHints={["pin1"]} pcbX={-1} pcbY={0} shape="rect" width="0.8mm" height="1.2mm" />
          <smtpad portHints={["pin2"]} pcbX={1} pcbY={0} shape="rect" width="0.8mm" height="1.2mm" layer="top" />
          <platedhole portHints={["pin3"]} pcbX={0} pcbY={3} shape="circle" holeDiameter="1mm" outerDiameter="1.6mm" />
          <silkscreentext text="U2" pcbY={-2} fontSize="1mm" />
        </footprint>
      }
    />
    <resistor name="R1" resistance="10k" footprint="0805" pcbX={0} pcbY={10} supplierPartNumbers={{ jlcpcb: ["C17414"] }} />
    <capacitor name="C1" capacitance="100nF" footprint="0603" pcbX={4} pcbY={10} pcbRotation={90} />
    <diode name="D1" footprint="sod123" pcbX={-12} pcbY={-5} />
    <led name="LED1" footprint="0805" color="green" pcbX={-8} pcbY={-5} />
    <transistor name="Q1" type="npn" footprint="sot23" pcbX={-3} pcbY={-5} />
    <solderjumper name="JP1" pinCount={2} footprint="solderjumper2" bridgedPins={[]} pcbX={5} pcbY={-5} />
    <solderjumper name="JP2" pinCount={2} footprint="solderjumper2" bridgedPins={[["1", "2"]]} pcbX={10} pcbY={-5} />
    <hole diameter="3mm" pcbX={-17} pcbY={12} />
    <cutout shape="rect" width="1mm" height="12mm" pcbX={0} pcbY={-1} />
    <keepout shape="rect" width="6mm" height="4mm" pcbX={15} pcbY={12} layers={["top", "bottom"]} />
    <copperpour layer="bottom" connectsTo="net.GND" />
    <group name="sub" pcbX={0} pcbY={0}>
      <resistor name="R2" resistance="1k" footprint="0603" pcbX={-15} pcbY={-10} />
    </group>
    <trace from=".U1 > .VCC" to=".R1 > .pin1" />
    <trace from=".U1 > .GND" to="net.GND" />
    <trace from=".R1 > .pin2" to=".C1 > .pin1" />
    <trace from=".D1 > .pin1" to=".LED1 > .pin1" />
    <trace from=".JP1 > .pin1" to=".U2 > .P1" />
  </board>
)
