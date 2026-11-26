// Net classes -> trace width (FIX_LIST #8). tscircuit has no per-net width prop: the width is set per <trace> with
// `thickness`, so every <trace ... net.X> gets thickness={traceWidth("X")}. The board sets minTraceWidth = SIGNAL_W.
export const POWER_NETS = ["VBUS", "V3V3", "V5_EMS", "EMS_VIN"]
// GND / GND_EMS: solid pours on both layers carry the return current; their stitching traces are routed last at signal width
export const GND_NETS = ["GND", "GND_EMS"]
// bus path (F1/F2, L1/L2, bridge D1-D4, R2-R4, Q1 collector) and the buck switch node (EMS_N26 = U2.SW / L3 / C9)
export const BUS_NETS = ["EMS_N1", "EMS_N2", "EMS_N3", "EMS_N4", "EMS_N5", "EMS_N6", "EMS_N11", "EMS_N12", "EMS_N13", "EMS_N17", "EMS_N26"]
export const POWER_W = 0.5
export const BUS_W = 0.4
export const SIGNAL_W = 0.25
export const traceWidth = (net?: string): string =>
  `${net && POWER_NETS.includes(net) ? POWER_W : net && BUS_NETS.includes(net) ? BUS_W : SIGNAL_W}mm`
