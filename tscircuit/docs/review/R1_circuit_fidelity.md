# R1 – Circuit fidelity review: EMS side and optocouplers (V1 Eagle vs. V2 tscircuit)

Reviewer: independent (R1). Date: 2026-11-26. Repo HEAD `e454bb9`.
Scope: V1↔V2 netlist equivalence, pad-number to physical-pin correctness, electrical review of the part substitutions, TX idle/polarity.
I did not use any project check script or report. Everything below comes from primary sources:
`hardware/EMSinterface_V1.0.sch` (Eagle XML), `tscircuit/dist/index/circuit.json` (built 07:43:15, newer than every
`.tsx` source, so I reused it), EasyEDA/LCSC component data (`easyeda.com/api/products/<C#>/components`) and the
LCSC parametrics from `jlcsearch.tscircuit.com`.

Scripts I wrote (scratchpad, run with `python3 -I`):
`/tmp/claude-0/-home-user-ems-bus-isolated-interface/5253066d-179b-5ef4-84d5-04e50bec02b1/scratchpad/r1/v1.py`
(Eagle parser: part → deviceset/device → `connect gate/pin → pad`, then net/segment/pinref → pad),
`.../r1/v2.py` and `.../r1/cmp.py` (circuit.json: union-find over `source_trace` port/net ids, then `source_port →
pcb_port → pcb_smtpad/pcb_plated_hole.port_hints` for the physical pad number), `.../r1/pads.py` (pad coordinates in the
component frame), `.../r1/eda.py` (EasyEDA symbol pin names and footprint pad coordinates).

## Summary

| # | Class | Finding |
|---|---|---|
| B1 | **BLOCKER** | The OC1/OC2 footprint (`OptoSo8Gw300Footprint`) has pads 5–8 mirrored: pad 5 is opposite pad 1, where pad 8 should be. Both optocouplers would be reverse-powered. OC1 would short V3V3 to GND. OC2 would leave the TX comparator in an undefined state, so the board could pull the EMS bus low with JP1 open. |
| M1 | MAJOR | MMBT3904 (Q1) replaces BC847B, but the base drive (R9 = 4.7 kΩ → IB ≈ 0.9 mA) is unchanged. At the TX sink current (~55–80 mA), the MMBT3904's guaranteed hFE (60 @ 50 mA, 30 @ 100 mA) is not enough to saturate it. In the worst case Q1 runs linear: TX current is lower and Q1 dissipates about 0.2 W in a 200 mW SOT-23. |
| m1–m9 | MINOR | LM393 commercial temperature range and output-sink margin into the OC1 LED; TX falling-edge delay from R11·C5 (inherited); JP1 gap; LED brightness; MPN strings; spec vs. implementation (C12); B5819W leakage; fuse voltage margin. |
| OK | OK | Every V1 connection exists in V2 (0 mismatches). Polarity and pinout are correct for every diode, LED, Q1, U1, U2, C12 and C14, and for opto pins 1–4. Values match BOM.csv and the .sch 1:1. TX/RX logic matches V1. Once B1 is fixed, JP1 open plus the 100 kΩ pull-up guarantees the bus is idle. |

---

## 1. Netlist comparison V1 ↔ V2

V1 extraction: 33 Eagle nets, 60 parts (supply symbols P+1..3 and GND1..3 were dropped). Diode/LED pads are named `A`/`C`
and C12 pads are named `+`/`-` in the Eagle library. For V2 I mapped them by **pin label** (`A`/`K`, `POS`/`NEG`), and
checked separately that the label sits on the correct physical pad (section 2). Every other pad was matched by its
physical pad number.

Result (`cmp.py`): **each of the 33 V1 nets maps onto exactly one V2 net, and no two V1 nets merge**. The only extra
members on the EMS side are the expected ones:

| V1 net | V2 net | Extra members in V2 |
|---|---|---|
| +5V | V5_EMS | – |
| GND | GND_EMS | C14.2 (NEG) |
| VIN | EMS_VIN | C14.1 (POS) → C12 ∥ C14 as intended |
| MCUVCC | V3V3 | ESP32/LDO/decoupling, R27.2, P2.1 |
| MCUTX | MCU_TX | JP1.2, R27.1 (P2.2 kept) |
| MCURX | MCU_RX | U3.5 (GPIO5) (P2.3 kept) |
| MCUGND | GND | MCU-side parts (P2.4 kept) |
| N$1…N$29 | EMS_N*/MCU_N* | none |

P2: V1 pads 1/2/3/4 = MCUVCC/MCUTX/MCURX/MCUGND (sch `CON-LSTB_04` connects). V2 P2 pins 1/2/3/4 =
V3V3/MCU_TX/MCU_RX/GND, the same assignment. OC1.1/.4 and OC2.1/.4/.7 (VB) are unconnected in both designs. There are no
`*_error` elements in circuit.json.

Note: this equivalence is at the **pad-number** level only. It does not account for B1, where the pad numbers are
assigned to the wrong physical positions.

## 2. Pad number ↔ physical pin

For each part I compared three things: the EasyEDA symbol (pin number → name), the EasyEDA footprint (pad number → x/y,
plus the "+"/"–" marks on the document layer and the pin-1 dot), and the V2 pads from circuit.json in the component frame.

| Part | EasyEDA (pin: name @ position) | V2 (pad: label @ local x,y) | Verdict |
|---|---|---|---|
| D1–D5 BAT42W C22466362 (SOD-123_L2.8-W1.8-LS3.9-FD) | 1 = **A** @ −1.70 ("+" mark left), 2 = K @ +1.70 | `DiodeAK`: 1 = A @ −1.65, 2 = K @ +1.65 (e.g. D1 → EMS_N3 = V1 D1.A) | OK |
| D6 1N4148W C81598 (SOD-123F) | 1 = **K** @ −1.735, 2 = A ("+" right) | `DiodeKA`: 1 = K, 2 = A; D6.1 → GND_EMS = V1 D6.C | OK |
| D7 B5819W C8598 | 1 = "–" (K) @ −1.70, 2 = "+" (A) | 1 = K → EMS_VIN, 2 = A → EMS_N6 = V1 D7.C/D7.A | OK |
| LD1 red C84256 (LED0805-RD, MPN NCD0805R1) | 1 = "–" (K) @ −1.10, 2 = "+" @ +1.10 | `LedRed`: 1 = K @ −1.05 → GND_EMS, 2 = A → R17 | OK |
| LD2/LD3 green C2297 (LED0805-R-RD) | 1 = **A** @ +1.05, 2 = K @ −1.05 | `LedGreen`: 1 = A @ +1.05, 2 = K @ −1.05; K → MCU_TX / MCU_RX = V1 LD2.C / LD3.C | OK |
| Q1 MMBT3904 C20526 (SOT-23-3) | 1 = B, 2 = E, 3 = C; pads 1/2 on one side, 3 opposite | sot23: 1 = B (−1.14, +0.95), 2 = E (−1.14, −0.95), 3 = C (+1.14, 0). Same chirality as the EasyEDA footprint rotated 180° and as Eagle SOT23 (B 1, E 2, C 3) | OK |
| U1 LM393DR2G C7955 (SOIC-8) | 1 OUTA, 2 IN−A, 3 IN+A, 4 GND, 5 IN+B, 6 IN−B, 7 OUTB, 8 VCC; counter-clockwise | soic8: 1–4 left column top→bottom, 5–8 right column bottom→top (counter-clockwise); labels the same | OK |
| U2 JW5017S C371172 (SOT-23-6) | 1 BST, 2 GND, 3 FB, 4 EN, 5 VIN, 6 SW; counter-clockwise | sot23_6 counter-clockwise, same labels; matches Eagle SOT23-6 connects | OK |
| C12/C14 JVJ25V1000M10X12 C49256851 | pad 1 @ −4.5 = "+" (document-layer "+" and body chamfer on pad-1 side), pad 2 @ +4.5 | `CapE5_10p5`: 1 = POS @ −4.5 → EMS_VIN, 2 = NEG → GND_EMS | OK |
| F1/F2 BSMD0805-050-24V C910822 | non-polar | 0805 | OK |
| **OC1 6N137S-TA1-L C92651 / OC2 6N136S-TA1-L C336082** (SOP-8 2.54) | pad 1 (−3.81,−4.545) … pad 4 (+3.81,−4.545), pad 5 (+3.81,+4.545) … **pad 8 (−3.81,+4.545)**: counter-clockwise, **pad 8 opposite pad 1** | pad 1 (−4.75,+3.81) … pad 4 (−4.75,−3.81); **pad 5 (+4.75,+3.81)**, pad 6 (+4.75,+1.27), pad 7 (+4.75,−1.27), **pad 8 (+4.75,−3.81)**: **pad 5 opposite pad 1** | **BLOCKER B1** |

### B1 – BLOCKER: OC1/OC2 footprint has pins 5–8 mirrored

- Source: `tscircuit/lib/opto_so8_gw300.tsx:8` (`ys = [3.81, 1.27, -1.27, -3.81]`) and `:15` (`portHints={[`pin${8 - i}`]} … pcbY={-y}`).
  Pad `pin8` lands at y = −3.81 (next to pin 4), and `pin5` at y = +3.81 (next to pin 1). The two inversions (8−i and −y)
  cancel each other.
- circuit.json confirms it: OC1 (rot 0) pad pin5 GND @ (4.75, 11.81) is level with pin1 @ (−4.75, 11.81), and pin8 VCC
  @ (4.75, 4.19) is level with pin4. OC2 is the same in its rotated frame.
- References:
  - V1 Eagle `SO8-GW300` (`hardware/EMSinterface_V1.0.sch:408-415`): pad 5 @ (4.69, −3.937) and pad 8 @ (4.69, +3.937),
    i.e. pin 8 opposite pin 1 (standard DIP/SMD-8).
  - EasyEDA SOP-8_L9.8-W6.6-P2.54-LS10.3-BL for C92651/C336082 (table above).
  - The comment "Verified (docs/FOOTPRINT_CHECK.md)" in the source covers row pitch and pad size only, not the pin order.
- Effect when the real part is placed by JLC with pin 1 on pad 1. Each physical pin lands on the pad listed:

| Physical pin | OC1 (6N137) lands on | OC2 (6N136) lands on |
|---|---|---|
| 8 VCC | pad 5 = **GND** | pad 5 = **GND_EMS** |
| 7 | VE → pad 6 = MCU_RX | VB → pad 6 = **EMS_N15** (U1 IN−B) |
| 6 VO | pad 7 = V3V3 | pad 7 = n.c. |
| 5 GND | pad 8 = **V3V3** | pad 8 = **V5_EMS** |

  - **OC1:** reverse-powered. The substrate/ESD diode (GND pin to VCC pin) forward-biases straight across V3V3. Expect
    the AMS1117 to go into current limit, OC1 to be destroyed or overheat, and ESP32 brown-out. RX does not work.
  - **OC2:** reverse-powered on the EMS 5 V rail. The photodiode (anode = VB, cathode = VCC pin) is now forward-biased
    from EMS_N15 through R11 to GND_EMS, which clamps U1 IN−B to ≈ 0.6–0.7 V. U1 IN+B (EMS_N7) is also ≈ 0.6–0.7 V
    (D6 clamp). The TX comparator therefore sits at its decision point, and Q1 can switch on randomly or continuously.
    **The board can pull the boiler's EMS bus low even with JP1 open**, which defeats the "ex works cannot transmit"
    requirement (DESIGN_SPEC.md:11).
- Fix: pads 5–8 must be at `(+4.75, −3.81)=5, (+4.75, −1.27)=6, (+4.75, +1.27)=7, (+4.75, +3.81)=8`, i.e.
  `portHints={[`pin${5 + i}`]}` with `pcbY={-y}`, or `pin${8 - i}` with `pcbY={y}`. Then re-route, re-check the
  isolation slot / creepage (the pads move only within the same column) and regenerate the CPL.

## 3. Electrical review of substitutions (vs. V1 .sch / BOM.csv)

Values: every R/C value in V2 equals the V1 .sch value (`R1…R19`, `C1…C13`; e.g. R2–R4 68 Ω 2010, R10 470 Ω, R11/R9/R13
4.7 kΩ, R14 270 Ω, R12/R15 6.8 k/1.3 k, C5 10 nF, C12 2200 µF → 2 × 1000 µF). BOM.csv lists U1 as "LM393", while the
.sch part value and README say LMV393IDR. **OK.**

Circuit operation as extracted from the V1 netlist (needed to judge the substitutions):

- **Bridge and supply:** bus → F1/F2 → L1/L2 → bridge D1–D4 → EMS_N6 (rectified +). EMS_N6 → D7 → EMS_VIN (C12/C14
  hold-up) → JW5017S → +5 V.
- **RX:** EMS_N6 → R1 10 k → N8 → R5 390 → N7, with D6 clamping N7 to about 0.65 V.
  - U1A compares IN−A (N10 = R7/R8 divider of N7, plus C3 speed-up from N8) with IN+A (N9 = N7 averaged by R6·C2 ≈ 0.47 s).
  - OUTA sinks the OC1 LED (R10 from +5 V), and OC1 drives MCU_RX.
- **TX:** MCU_TX low → OC2 LED (R14 from V3V3) → OC2 VO pulls N15 (IN−B, R11 pull-up to +5 V, C5) low → IN+B (N7
  ≈ 0.65 V) > IN−B → OUTB released → R9 drives Q1 → Q1 sinks the bus through R2+R3+R4 = 204 Ω.

### U1 LMV393IDR → LM393DR2G (C7955) – OK, with notes m1/m2

- **Input common-mode range.** LM393 CMR is 0 … VCC−1.5 V (3.5 V at 5 V; VCC−2 V over temperature).
  - RX inputs N9/N10 are ≈ 0.6 V, and TX IN+B (N7) is ≤ 0.7 V: all inside the range.
  - IN−B sits at +5 V (= VCC via R11) when idle, which is outside the range. It was outside for the LMV393 too (CMR
    ≈ VCC−0.8 to −1 V), so this is inherited.
  - For the LM393/LM339 family, the output is correct as long as the *other* input is within CMR (TI LM393/LM339
    application note). IN+B ≈ 0.65 V is in range, so OUTB = low → Q1 off → idle. The inputs tolerate up to 36 V without
    damage.
  - Not a regression.
- **Output.** Open collector, same as LMV393.
  - Pull-up/LED loads: OUTA sinks the OC1 LED, ≈ (5 − 1.4 − VOL)/470 ≈ 6.5–7 mA. OUTB sinks R9, 1.06 mA.
  - LM393DR2G guarantees ISINK ≥ 6 mA at VO ≤ 1.5 V and VOL ≤ 0.4 V at 4 mA. See m2.
- **Supply current.** LM393 ICC is 0.4 mA typ / 1 mA max at 5 V (LCSC: 400 µA), against ≈ 0.2 mA typ for the LMV393.
  - The extra ≤ 0.2 mA typ (≤ 0.8 mA worst) at 5 V is roughly ≤ 0.1–0.3 mA of bus current through the buck.
  - That is negligible next to the existing 5 V loads: LD1 ≈ 2.7 mA, R9 1.06 mA continuous, OC1 LED ≈ 7 mA.
  - OK for the bus-powered budget.
- **Speed.** Response time is 1.3 µs (300 ns TTL step), against a 104 µs bit at 9600 Bd. OK.
- **Offset / bias.** 5 mV / 250 nA max; ≤ 12 mV error on the 47 k node. Comparable to the LMV393. OK.

### BAT42 → BAT42W (C22466362) – OK

Same die in SOD-123: 30 V, 200 mA, IR 500 nA @ 25 V, VF 650 mV @ 50 mA (LCSC). Peak bridge current is about 80 mA
(Q1 TX), within 200 mA. The reverse voltage is the bus voltage, below 30 V. Polarity is verified (section 2).

### BC847B → MMBT3904 (C20526) – **MAJOR M1**

- **TX sink current.** IC ≈ (V_N6 − VCEsat)/204 Ω ≈ 55–80 mA for a rectified bus of 12–17 V.
- **Base current.** R9 is unchanged at 4.7 kΩ (`src/ems-side.tsx:156`), so IB = (5 − 0.8)/4.7 k ≈ 0.9 mA. Saturation
  needs hFE ≥ ~80.
- **BC847B (V1):** hFE 200–450 (at 2 mA) and still typically ≥ 150 near 70 mA, so V1 saturated with large margin. Its
  100 mA IC max is tight but adequate.
- **MMBT3904:** datasheet minima are hFE 60 @ 50 mA and 30 @ 100 mA (VCE = 1 V). The LCSC "RANGE:100-300" bin is
  specified at 10 mA.
- **Worst case.** IC can be limited to ≈ 30–55 mA. Q1 then operates linear, with VCE ≈ 4–8 V and P ≈ 0.2–0.25 W in a
  part rated 200 mW (LCSC). The TX "0" level on the bus becomes weaker and part-dependent.
- **Typical parts.** hFE is ≈ 100–150 at 50–70 mA, so they work. This is a margin issue, not a certain failure.
- **Fix options:**
  - Use a higher-gain NPN (BC817-40 class, 500 mA, hFE 250–600, or BC847C).
  - Or lower R9 to about 2.2 kΩ. Cost: +1.2 mA continuous on +5 V, because R9 is sunk by OUTB in idle.
  - Re-check the C4/R4 edge shaping afterwards.

### PMEG3020EGW → B5819W (C8598) – OK, note m7

- **Forward.** VF at the ≈ 5–20 mA buck input current is ≈ 0.25–0.35 V, comparable to the PMEG3020EGW. IFSM 9 A
  covers the C12/C14 inrush; the bus is current-limited anyway.
- **Reverse leakage.** B5819W is 1N5819-class: IR up to ~1 mA at 40 V / 25 °C, rising about 10× at 100 °C, and higher
  than the PMEG3020EGW. In this circuit D7 only sees a few volts of reverse bias, when the bus is pulled low
  (VIN − V_N6). Expected leakage is tens of µA at 60 °C, against the buck input current of a few mA. Hold-up loss is
  < 2–3 %. OK.

### C12 2200 µF THT → C12 + C14 = 2 × 1000 µF / 25 V SMD (JVJ25V1000M10X12, C49256851) – OK, note m8

- **Capacitance.** 2000 µF is −9 % of nominal and inside the e-cap tolerance.
- **Hold-up history.** README: 470 µF caused errors, 1000 µF was OK, and 2200 µF was chosen "with margin". At −20 %
  tolerance the pair is 1600 µF, still above the 1000 µF that worked.
- **Voltage.** 25 V rating, same as V1. VIN ≈ bus − 1 V.
- **ESR / ripple.** Not published by LCSC; the EasyEDA datasheet link points to an unrelated part. Ripple duty is small:
  C10 10 µF MLCC takes the 1.2 MHz switching ripple at U2, and the e-caps only buffer bit-rate dips at the mA level. Two
  in parallel halve the ESR.
- **Leakage.** ≤ 2 × 250 µA (0.01 CV), the same as the 2200 µF.
- **Polarity.** Verified OK.
- **Unverified.** Lifetime/temperature grade of this no-name part (likely 85 °C or 105 °C). Check before ordering.

### Fuses F1/F2 BSMD0805-050-24V (C910822) – OK, note m9

- **Ratings (LCSC).** Hold 0.5 A, trip 1 A, Vmax 24 V, Imax 40 A, R 0.1–0.85 Ω, −40…+85 °C.
- **Series resistance.** ≤ 1.7 Ω for both together, against the 204 Ω TX load: negligible. V1 used an unspecified
  "FUSE0805".
- **Voltage.** Vmax only matters when the fuse has tripped (it then blocks the full source voltage). The EMS bus is
  normally 12–18 V and below 24 V, so it is OK.

### Other parts (spot check, LCSC)

- **JW5017S:** VIN 4.5–26 V, VFB 0.8 V. R12/R15 give 0.8·(1 + 6.8/1.3) = 4.98 V. OK.
- **6N136S-TA1-L:** VCC 4.5–15 V on +5 V, CTR ≥ 19 %. OK.
- **6N137S-TA1-L:** VCC 2.7–5.5 V, so 3.3 V operation is in spec. OK.
- **1N4148W:** 75 V. OK.
- **Inductors:** LQH32PN4R7NN0L 1 A / 216 mΩ, SWPA5020S4R7MT 2.2 A. OK.

## 4. TX path, idle and polarity

Netlist (circuit.json):

- MCU_TX = {OC2.3 (LED cathode), LD2.K, P2.2, JP1.2, R27.1}.
- R27.2 → V3V3. OC2.2 (anode) → R14 270 Ω → V3V3.
- ESP_TX = {U3 GPIO17, JP1.1} only.

JP1 open in copper:

- The pads are separate 1.5 × 1.5 mm pads at 2.54 mm pitch, with a 1.04 mm gap (`src/mcu-side.tsx:118`).
- No `pcb_trace` touches both pads: ESP_TX traces touch only pad 1, MCU_TX traces only pad 2.
- There is no `source_component_internal_connection` for JP1.

Idle logic, valid **once B1 is fixed**:

- JP1 open, no P2 driver: MCU_TX is pulled to V3V3 by R27 and the R19/LD2 path. No node sinks current, so the OC2 LED
  carries no current and OC2 is off. N15 = +5 V via R11, OUTB = low, so Q1 is off and the **bus is idle**.
- Board unpowered on the MCU side (V3V3 = 0): there is no LED current either, so the bus is idle.
- **Regression: none.** The netlist matches V1. P2.2 can still drive TX as in V1 (intended).

Polarity:

- **TX:** UART idle high → OC2 off → Q1 off → no bus load. Start bit / "0" → OC2 on → Q1 on → bus loaded. Same as V1,
  since the netlist is identical.
- **RX:** OC1 (inverting 6N137 output with R13 pull-up) → MCU_RX/GPIO5, unchanged vs V1.

**Caveat:** as built (with B1), idle is **not** guaranteed. See B1.

## MINOR findings

- **m1** – LM393DR2G (C7955) is rated 0…+70 °C (LCSC); the V1 LMV393IDR was −40…+125 °C. Fine indoors, but it is the
  narrowest temperature range on the EMS side. LMV393IDR or LM393DT/LM2903 (−40…+125 °C) are drop-in options.
- **m2** – OC1 LED drive margin.
  - IF = (VCC − VF − VOL)/R10. Typical ≈ 6.5–7 mA. Worst case is (4.75 − 1.75 − ~1.0)/470 ≈ 4.3 mA, below the 6N137
    IFT max of 5 mA, because LM393 VOL is only guaranteed ≤ 1.5 V at 6 mA.
  - Mostly inherited; the LM393 sinks slightly worse than the LMV393.
  - Optional: R10 → 390 Ω (IF typ ≈ 8.5 mA).
- **m3** – TX falling-edge delay (inherited, unchanged).
  - C5 10 nF ∥ R11 4.7 k on IN−B gives τ = 47 µs. OC2 (CTR 19 % min × IF ≈ 6.5 mA ≈ 1.2 mA) has to discharge it from
    5 V to ≈ 0.65 V.
  - Delay ≈ 26 µs typ, up to ≈ 70 µs worst case. Release takes ≈ 5 µs. So low bits shrink by 20–65 % of a 104 µs bit in
    the worst case.
  - Field-proven in V1 with the same 6N136S-TA1-L, so no change is required. Worth a scope check on the first V2 board;
    C5 = 2.2–4.7 nF would add margin.
- **m4** – JP1 is a 2.54 mm-pitch pad pair with a 1.04 mm gap, which is awkward to bridge with solder. JLC paste will
  put solder on both pads. Consider a proper solder-jumper footprint (gap ≤ 0.3–0.5 mm) or a 0 Ω 0805 DNP.
- **m5** – KT-0805G green (C2297) has VF 2.6–3.1 V (LCSC). On 3.3 V through 1.2 kΩ, LD2/LD3 get ≤ 0.5 mA and will be
  very dim. Not functional: they are not in the opto current path.
- **m6** – MPN strings: U1 `manufacturerPartNumber="LM393DR"` but C7955 is LM393DR2G (onsemi) (`src/ems-side.tsx`
  U1). Cosmetic for the BOM; the C-number decides.
- **m7** – B5819W leakage is higher than the PMEG3020EGW's (see §3). Acceptable; mentioned because of the hold-up
  question.
- **m8** – `docs/DESIGN_SPEC.md:36` still says "C12 2200 µF/25 V THT". The implementation is 2 × 1000 µF SMD. Update
  the spec. The C49256851 ESR/ripple/lifetime are unpublished, so verify them before ordering.
- **m9** – 24 V PTC rating gives about 6 V of margin over the highest commonly reported EMS bus voltages. I could not
  confirm a maximum bus voltage from a primary source. If the target boilers stay ≤ 20 V it is OK; otherwise use the
  30 V variant.

## Not in scope / not checked

PCB copper connectivity of routed traces (only JP1 was checked), creepage/clearance and slot, CPL rotations, MCU-side
circuit beyond the TX/RX nets.
