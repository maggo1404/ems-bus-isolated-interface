// Net classes as <net> elements (FIX_LIST #8): nominalTraceWidth per net.  tscircuit routes everything in one
// autorouting pass (several routing phases produced overlapping copper, see docs/FAB_CHECKLIST.md).
import { POWER_NETS, BUS_NETS, POWER_W, BUS_W } from "./netclass"

export const NetDefs = () => (
  <>
    {POWER_NETS.map((n) => (
      <net key={n} name={n} isPowerNet nominalTraceWidth={`${POWER_W}mm`} />
    ))}
    <net name="GND" isGroundNet nominalTraceWidth="0.25mm" />
    <net name="GND_EMS" isGroundNet nominalTraceWidth="0.25mm" />
    {BUS_NETS.map((n) => (
      <net key={n} name={n} nominalTraceWidth={`${BUS_W}mm`} />
    ))}
  </>
)
