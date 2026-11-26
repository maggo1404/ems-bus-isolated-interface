export default () => (
<board width="34mm" height="34mm" layers={2} defaultTraceWidth="0.4mm">
<resistor name="RH0a" resistance="1k" footprint="0603" pcbX={-12} pcbY={-4} />
<resistor name="RH0b" resistance="1k" footprint="0603" pcbX={12} pcbY={-4} />
<resistor name="RV0a" resistance="1k" footprint="0603" pcbX={-4} pcbY={-12} pcbRotation={90} />
<resistor name="RV0b" resistance="1k" footprint="0603" pcbX={-4} pcbY={12} pcbRotation={90} />
<trace from=".RH0a > .pin2" to=".RH0b > .pin1"  />
<trace from=".RV0a > .pin2" to=".RV0b > .pin1"  />
<resistor name="RH1a" resistance="1k" footprint="0603" pcbX={-12} pcbY={0} />
<resistor name="RH1b" resistance="1k" footprint="0603" pcbX={12} pcbY={0} />
<resistor name="RV1a" resistance="1k" footprint="0603" pcbX={0} pcbY={-12} pcbRotation={90} />
<resistor name="RV1b" resistance="1k" footprint="0603" pcbX={0} pcbY={12} pcbRotation={90} />
<trace from=".RH1a > .pin2" to=".RH1b > .pin1"  />
<trace from=".RV1a > .pin2" to=".RV1b > .pin1"  />
<resistor name="RH2a" resistance="1k" footprint="0603" pcbX={-12} pcbY={4} />
<resistor name="RH2b" resistance="1k" footprint="0603" pcbX={12} pcbY={4} />
<resistor name="RV2a" resistance="1k" footprint="0603" pcbX={4} pcbY={-12} pcbRotation={90} />
<resistor name="RV2b" resistance="1k" footprint="0603" pcbX={4} pcbY={12} pcbRotation={90} />
<trace from=".RH2a > .pin2" to=".RH2b > .pin1"  />
<trace from=".RV2a > .pin2" to=".RV2b > .pin1"  />
</board>
)
