// Open solder jumper footprint: 2 pads 1.2 x 1.6 mm, gap 0.4 mm (pitch 1.6 mm), no paste, so a blob of solder closes it.
// Mask margin 0.22 mm per pad: the two openings (0.4 mm gap) merge into ONE opening over both pads and the gap (R5 m3/m7).
export const SolderJumper2Footprint = () => (
  <footprint>
    <smtpad portHints={["pin1"]} shape="rect" width="1.2mm" height="1.6mm" pcbX={-0.8} pcbY={0} noSolderPaste solderMaskMargin="0.22mm" />
    <smtpad portHints={["pin2"]} shape="rect" width="1.2mm" height="1.6mm" pcbX={0.8} pcbY={0} noSolderPaste solderMaskMargin="0.22mm" />
  </footprint>
)
