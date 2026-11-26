import { Esp32S3Wroom1 } from "../lib/esp32s3wroom1"
import { UsbC16 } from "../lib/usbc16"
import { Opto6N137, Opto6N136 } from "../lib/opto_so8_gw300"
import { Mstba2, CapE5_10p5, Inductor3225, Inductor0520, Res2010Footprint, Tactile5x5 } from "../lib/thtparts"

export default () => (
  <board width="90mm" height="70mm">
    <Esp32S3Wroom1 name="U1" pcbX={-30} pcbY={0} />
    <UsbC16 name="J1" pcbX={10} pcbY={25} />
    <Opto6N137 name="OC1" pcbX={0} pcbY={0} />
    <Opto6N136 name="OC2" pcbX={20} pcbY={0} />
    <Mstba2 name="P1" pcbX={30} pcbY={-25} />
    <CapE5_10p5 name="C12" pcbX={10} pcbY={-20} />
    <Inductor3225 name="L1" pcbX={35} pcbY={10} />
    <Inductor0520 name="L3" pcbX={35} pcbY={18} />
    <resistor name="R2" resistance="68" footprint={<Res2010Footprint />} pcbX={30} pcbY={0} />
    <Tactile5x5 name="SW1" pcbX={30} pcbY={-10} />
    <chip name="U2" footprint="sot23_5" pcbX={0} pcbY={-20} />
    <chip name="U3" footprint="sot23_6" pcbX={0} pcbY={-28} />
    <chip name="U4" footprint="sot223" pcbX={-10} pcbY={-28} />
    <chip name="U5" footprint="soic8" pcbX={-10} pcbY={-20} />
    <diode name="D1" footprint="sod123" pcbX={20} pcbY={-20} />
    <pinheader name="J2" pinCount={4} pitch="2.54mm" pcbX={20} pcbY={-28} />
    <capacitor name="C1" capacitance="22uF" footprint="1206" pcbX={40} pcbY={0} />
  </board>
)
