# R2 review: isolation, layout and manufacturability (EMS-ESP Isolated Interface V2.0)

Reviewer: independent R2 (I did not use the project's check scripts or other agents' reports).
Inputs: `dist/index/circuit.json` (07:43:15), `fab/EMSinterface_V2.0-gerbers.zip` / `-BOM_JLCPCB.csv` / `-CPL_JLCPCB.csv` (07:43:33),
`dist/index/pcb.svg`, `docs/img/pcb.png`, sources `index.circuit.tsx`, `src/*.tsx`, `lib/*.tsx`.
The EasyEDA footprints and the Basic/Extended status of every LCSC number were fetched online (easyeda.com, jlcsearch.tscircuit.com).
jlcpcb.com could not be reached from this session (blocked host), so the JLC capability figures below come from JLC's published
2-layer rules as I know them. Check them on the JLC site before ordering.

My scripts (independent of `scripts/`) are in the session scratchpad
`/tmp/claude-0/-home-user-ems-bus-isolated-interface/5253066d-179b-5ef4-84d5-04e50bec02b1/scratchpad/r2/`:
- `gparse.py`: my own RS-274X parser, producing shapely geometry.
- `cj.py`: circuit.json loader with my own union-find netlist.
- `iso_cj.py` / `iso_gbr.py`: isolation checks on circuit.json and on the Gerbers.
- `drc_cj.py` / `drc2.py`: clearance checks.
- `conn.py`: copper connectivity.
- `widths.py`, `decap.py`, `ant.py`, `mech.py`, `silk.py`: trace widths, decoupling, antenna, mechanics, silkscreen.
- `rot.py`: CPL check against the EasyEDA footprints.
- `render.cjs`: SVG render.

No design files were modified.

---

## Summary

| # | Severity | Finding |
|---|---|---|
| B1 | **BLOCKER** | The fab Gerber zip has **no traces and no vias**: 0 draw commands on F_Cu/B_Cu and no via drills. It is an unrouted export. |
| B2 | **BLOCKER** | The opto footprint `OptoSo8Gw300Footprint` numbers pins 5–8 in **mirrored order**: pin 5 sits opposite pin 1 and pin 8 opposite pin 4. On the real 6N137/6N136 (and the EasyEDA footprint), VCC and GND end up swapped, and VO/VE (VO/VB) too, on OC1 and OC2. |
| B3 | **BLOCKER** | Vias are 0.2 mm drill / 0.3 mm pad, i.e. a **0.05 mm annular ring**. JLC 2-layer needs ≥0.3 mm drill and ≥~0.13 mm ring. All 104 vias are affected. |
| B4 | **BLOCKER** | The USB-C **B-row D+/D− pads (B6/B7) are not connected**. USB data works in only one plug orientation, and tscircuit shows no ratsnest because A/B pads share one port. |
| B5 | **BLOCKER** | P1 KF2EDGRC-5.08-2P is a **right-angle** header. With the CPL rotation (90°) and the EasyEDA footprint, its 12 mm body extends **into** the board over F1/F2/L1/L2, and the plug opening faces inward. |
| M1 | MAJOR | **CPL errors**: J2 rotation is 0° but must be **180°** (mid Y off by 0.125 mm). U3 (ESP32) Mid X is 41.98 but must be **38.61 mm**: a 3.37 mm offset that would push the module over the board edge. |
| M2 | MAJOR | **All 856 trace segments are 0.15 mm**, including VBUS, V3V3, GND, GND_EMS, V5_EMS, EMS_VIN, the buck SW node and the bus path. |
| M3 | MAJOR | 72 different-net copper pairs are closer than 0.15 mm (spec minimum), 47 closer than 0.127 mm, and 5 at 0.100 mm. |
| M4 | MAJOR | Buck hot loop: C10 is 5.9 mm from U2 VIN, C11 is 7 mm from L3, and every connection is 0.15 mm. Opto bypass caps: C7 is 8.9 mm from OC1. C13 is 12 mm from OC2 (V5_EMS) and also serves U1 at 11 mm. |
| M5 | MAJOR | AMS1117 (U5): the tab is a 2×3.8 mm pad fed by 0.15 mm traces, with no V3V3 copper area. At 0.3–0.5 A it dissipates 0.5–0.85 W. |
| M6 | MAJOR | ESP32 antenna: no copper under it (OK). But the GND pour on both layers and parts (C22, C23, R26/LD5, R22/LD4, SW1) sit 0.5–6 mm beside the antenna. The spec asks for ≥15 mm keep-out. |
| M7 | MAJOR | Mechanics: the two isolation slots leave the halves joined by a single **6.6 × 2 mm FR4 bridge**. The board is fragile in handling, reflow and depaneling, and the opto solder joints carry the strain. |
| M8 | MAJOR | Mounting holes: both pours (solder mask only) run to 0.19 mm from the M3 holes. Metal screws or standoffs on a common metal plate could bridge GND_EMS↔GND through the chassis. |
| m* | MINOR | Courtyard overlaps; silkscreen lines below 0.15 mm; silk over pads (ESP32, USB-C); pour 0.2 mm from the board edge; USB pair not length/pair-routed; VBUS 2nd pad open; 15 Extended parts; THT parts need THT assembly. |
| OK | OK | Isolation geometry ≥ 6.4 mm everywhere (circuit.json and Gerbers). No GND_EMS↔GND connection. Slots are in Edge_Cuts. BOM/CPL column format is valid. All other CPL rotations match EasyEDA. |

---

## 1. Isolation

### 1.1 Copper clearance across the barrier: OK (6.40 mm minimum)

**circuit.json** (`iso_cj.py`):
- Nets come from my own union-find over `source_trace`/`source_net`/internal connections. Named nets are classified by name. Unnamed nets go by owning part, and OC NC/VB pins by package side.
- Every pad, PTH, trace segment (with its width), via and pour (brep with inner rings) was classified. Nothing was left unclassified, and no net contains both EMS and MCU names.

| Layer | EMS copper x_max | MCU copper x_min | Min EMS↔MCU gap | Where |
|---|---|---|---|---|
| top | −3.200 | +3.200 | **6.400 mm** | GND_EMS pour ↔ GND pour (pour edges at x = ±3.2) |
| bottom | −3.200 | +3.200 | **6.400 mm** | same |
| projected, any layer | | | 6.400 mm | |

Gaps by object type (top):
- pad↔pad 7.70 mm (OC pad inner edges at ±3.85)
- pad↔pour 7.05 mm
- trace↔pour 7.875 mm
- pour↔pour 6.40 mm

No trace or via comes closer to the barrier than |x| = 3.9 mm.

**Gerbers** (`iso_gbr.py`, own parser, dark/clear polarity applied in order):
- F_Cu: 206 copper islands, none crossing x = 0. The left↔right minimum is **6.400 mm** and the opto pad↔pad distance is 7.70 mm.
- B_Cu: the left↔right minimum is 6.400 mm.
- There is zero copper in the band |x| ≤ 1.2 mm on either layer.
- I re-ran the check on a Gerber set exported from the routed circuit.json (see B1). It also gives 6.400 mm, with no island crossing.

### 1.2 Creepage / slots: OK

- `Edge_Cuts.gbr` contains the slots as part of the board outline. There are two 2.0 mm wide notches (x = −1…+1):
  - from the bottom edge to y = −3.3;
  - from the top edge to y = +3.3.
- The slots are therefore present, routed as outline and NPTH-milled, and 2.0 mm wide (≥ JLC's ~1.0 mm minimum for a milled slot).
- Both slots run under the full body of each optocoupler (OC pads span |y| 3.49…12.51).
- The shortest surface path is straight across the 6.6 mm bridge (|y| ≤ 3.3) between the pour edges: **6.40 mm**. Elsewhere the slot forces a path through air of ≥ 2.2 + 2 + 2.2 mm, and the creepage path around a notch that is open to the board edge does not exist.
- Mounting holes are NPTH (`drill_npth.drl` T11 3.2 mm). No copper is plated in them.
- Only silkscreen crosses the barrier: the barrier line and the "ISOLATION BARRIER" text.

### 1.3 GND_EMS vs GND: OK

- My union-find shows the two grounds are never in the same net.
- The geometric check (`drc_cj.py`) finds no overlapping copper of different nets on either layer.
- Pours:
  - GND_EMS: `pcb_copper_pour_0` (top) and `_8` (bottom), both entirely at x ≤ −3.2.
  - GND: `_10` and `_32`, plus three small top islands `_13`, `_23`, `_25`, all at x ≥ 3.2.
- Each of the small islands touches GND pads, traces or vias, so none is floating.

### 1.4 Is 6 mm adequate? Recommendation

- The EMS bus is SELV (≈15–24 V). The barrier exists for ground-loop and noise immunity, not for safety.
- Under IEC 60664-1 (pollution degree 2, FR4 material group IIIb), 6.4 mm of creepage would cover functional or basic insulation for a working voltage of a few hundred volts. That is far more than SELV needs.
- The optocouplers are rated 5000 Vrms (Lite-On 6N137S / 6N136S). The 300-mil SMD-8 package has an external creepage of about 7 mm, so the PCB gap of 6.4 mm is the limiting element. That is acceptable here.
- **Verdict: 6 mm is adequate.** The slots are optional for this voltage class.
- Given M7, I recommend one of two changes:
  - keep only short slots between the opto pad rows (e.g. the opto body length plus 1 mm) and leave the rest of the barrier as an unslotted 6.4 mm copper-free strip; or
  - keep the slots but add a second bridge near each board edge.
- Fix M8 (mounting-hole pour keep-out) so the barrier is not bypassed through the enclosure.

---

## 2. Electrical layout

### 2.1 BLOCKER B4: USB-C second D+/D− pads unconnected

`conn.py` (copper connectivity per net) and J2 pad inspection:

| Net | J2 pad (x, y) | Connected? |
|---|---|---|
| USB_DN | (23.75, 22.4) | yes |
| USB_DN | (24.75, 22.4) | **no copper touches it** |
| USB_DP | (23.25, 22.4) | yes |
| USB_DP | (24.25, 22.4) | **no** |
| VBUS | (21.6, 22.4) | yes |
| VBUS | (26.4, 22.4) | **no** |
| GND | both pads | yes (trace and pour) |

- A USB 2.0 plug has D+/D− only on A6/A7. When the plug is flipped, they land on the receptacle's B6/B7, which are not connected here. **USB data and programming fail in one plug orientation.**
- `lib/usbc16.tsx` gives both pads the same port (`pin5`/`pin6`), so the router treats the port as done after reaching one pad. No ratsnest is shown and no error is raised.
- Fix: route DP_A6↔DP_B6 and DN_A7↔DN_B7 (short jumpers under the connector), or split the pads into separate ports and join them with traces.
- The open VBUS second pad is MINOR: the plug ties all VBUS contacts together, so it only halves contact capacity.
- The SW1/SW2 second pads and the J2 shell legs are open too, but they are joined inside the part, so that is OK.

### 2.2 MAJOR M2: trace widths (`widths.py`)

**All 856 segments are 0.15 mm.** The board defines no power widths. Per net:

| Net | Width min/max (mm) | Length (mm) top/bot | Vias | Current / comment |
|---|---|---|---|---|
| GND (MCU) | 0.15/0.15 | 196 (171/25) | 14 | return of ≤500 mA; pours help |
| GND_EMS | 0.15/0.15 | 162 (134/28) | 12 | bus/buck return |
| V3V3 | 0.15/0.15 | 156 (116/40) | 16 | ESP32 peaks ~350–500 mA |
| V5_EMS | 0.15/0.15 | 94 (72/23) | 8 | buck output |
| EMS_VIN | 0.15/0.15 | 47 | 0 | buck input from bridge/D7 |
| VBUS | 0.15/0.15 | 32 | 0 | up to 500 mA into AMS1117 |
| EMS_N26 (SW node) | 0.15/0.15 | 10.3 | 0 | buck switch node, U2–L3 |
| EMS_N3 / EMS_N4 (bridge AC) | 0.15 | 18.5 / 20.1 | 0 | bus path L1/L2 → bridge |
| EMS_N6 (bridge +) | 0.15 | 37 | 6 | bus path to R2/D7 |
| EMS_N17/N5/N2/N1 (P1→F→L) | 0.15 | 8.3/10.8/3.6/6.1 | 0–1 | bus input |
| EMS_N11/N12/N13 (R2–R4–Q1) | 0.15 | 5.9/5.9/18.4 | 0–2 | TX load current |
| USB_DP / USB_DN | 0.15 | 20.2 / 21.7 | 6 / 4 | see 2.5 |
| others (signals) | 0.15 | — | — | fine |

The electrical limits of a 0.15 mm, 1 oz trace:
- **Resistance:** ≈ 3.3 mΩ/mm, so the VBUS tree of 32 mm is ≈ 0.1 Ω.
- **Current:** IPC-2221 external, ΔT = 10 °C gives ≈ 0.6 A. The traces will not burn, but:
  - V3V3 drop and inductance with WiFi TX bursts at 300–500 mA cause ripple and brown-out risk at the ESP32;
  - VBUS to the LDO drops about 50 mV;
  - the buck VIN/SW/GND loop gains inductance, which costs EMI and efficiency.

Recommendation:
- VBUS, V3V3, V5_EMS and EMS_VIN at **≥ 0.5 mm**.
- The SW node, buck VIN and GND as short **≥ 0.6 mm** copper areas.
- The bus path P1→F1/F2→L1/L2→bridge→D7 and R2–R4→Q1 at **≥ 0.4 mm**, mainly for surge and ESD robustness and lower impedance.
- Signals can stay at 0.15–0.2 mm.

### 2.3 MAJOR M3: spacing

- No shorts were found.
- Different-net copper pairs (excluding pours) closer than:
  - 0.15 mm: **72** (below the spec's "≥ 0.15 mm track/space");
  - 0.127 mm: **47**;
  - 0.100 mm: **5**.
- Examples at 0.100 mm:
  - D2 pad (EMS_N3) ↔ GND_EMS trace;
  - U2 pad (EMS_N26) ↔ EMS_VIN trace;
  - R22 pad ↔ IO2 trace;
  - V5_EMS trace ↔ GND_EMS via_87.
- The board's DRC settings in circuit.json allow 0.1 mm (`min_trace_to_pad_edge_clearance: 0.1`).
- Recommendation: set the autorouter clearance to 0.15–0.2 mm.

### 2.4 MAJOR M4: decoupling and hot loop (`decap.py`, pad edge-to-edge distances)

| Cap | IC | Net | Supply pad ↔ IC pin | GND pad ↔ IC GND pin | Note |
|---|---|---|---|---|---|
| C10 10 µF | U2 JW5017S | EMS_VIN | 5.93 mm | 3.41 mm | buck input cap: should be ≤ 1–2 mm, wide copper |
| C12/C14 bulk | U2 | EMS_VIN | 28 / 17 mm | | bulk, acceptable |
| C9 bootstrap | U2 | SW | 4.58 mm | | OK-ish; short is better |
| L3 / C11 | U2 / L3 | SW / V5 | L3 ~8 mm from U2, C11 7 mm from L3 | | output loop is large |
| C6 100 nF | U1 LM393 | V5_EMS | 6.18 mm | 2.26 mm | acceptable |
| C7 100 nF | OC1 6N137 | V3V3 | **8.87 mm** | 3.08 mm | the 6N137 datasheet requires 0.1 µF directly at pins 8–5 (≤ ~1 cm of loop); marginal |
| C13 100 nF | OC2 / U1 | V5_EMS | 12.1 / 11.2 mm | 6.35 | too far |
| C8 100 nF | OC2 | V5_EMS | 16.7 mm | | too far |
| C22 10 µF / C23 100 nF | U3 | V3V3 | 1.88 / 3.63 mm | 3.7 / 4.1 | OK |
| C26 22 µF | U5 out | V3V3 | 1.98 mm | 8.3 | OK |
| C27/C28 | U5 out | V3V3 | 5.15 mm | 11.5 | OK |
| C24/C25 | U5 in | VBUS | 4.8 / 3.15 mm | 3.3 | OK |

These placements come from the stretched V1 layout. Move C10 next to U2 pins 5/2, L3 and C11 next to U2, and the bypass caps next to OC1/OC2.

### 2.5 USB D+/D−: MINOR (apart from B4)

- Routing: 0.15 mm, not routed as a pair.
- Lengths: DP 20.2 mm with 6 vias; DN 21.7 mm with 4 vias. The totals include the ESD (U4) branches; the two pads per line are on U4.
- One USB_DN↔USB_DP via pair is 0.117 mm apart (vias 2 and 6), and several DP/DN traces run 0.11–0.12 mm from the other line's vias.
- At 12 Mbit/s full speed this is tolerable. For the redesign: route as a 90 Ω-ish pair (~0.3 mm/0.15 mm on 1.6 mm FR4 is not achievable, so just keep it short and parallel), with ≤ 2 vias, ESD at the connector, and no stubs.

### 2.6 MAJOR M5: AMS1117 thermal

- The U5 tab (pin 4 = VOUT) is a 2.0 × 3.8 mm pad (7.6 mm²). It connects only through 0.15 mm traces, with no V3V3 copper area and no thermal vias.
- Dissipation is (5.0 − 3.3) V × I: 0.5 W at 300 mA and 0.85 W at 500 mA.
- With SOT-223 on minimal copper (θJA ≈ 90–130 °C/W), that means a rise of +45…110 °C.
- Add ≥ 2–4 cm² of V3V3 copper on the tab (both layers, with vias), or change to a buck or a lower-dropout regulator.

### 2.7 MAJOR M6: ESP32 antenna (`ant.py`)

- **Placement:** module U3 at rotation −90°, body x 29.5…55.0. The antenna end is flush with the right board edge (x = 55), as Espressif's preferred "antenna at edge" placement requires (OK).
- **Under the antenna:** the antenna region per the EasyEDA outline is x 48.97…55, |y| ≤ 9. It has **0 mm² copper on both layers** (pour notch x ≥ 47.95, |y| ≤ 9.5, plus a tscircuit keepout). OK.
- **Beside the antenna:** x ≥ 48.97 with 9 < |y| ≤ 15 holds **119.6 mm²** of copper:
  - the GND pour on top and bottom, 0.5 mm from the antenna sides;
  - C23 pads, R22 pads, V3V3/GND traces and via_17.
- **Parts within ~6 mm of the antenna:** C22 (47.5, 12.8), C23 (50.5, 12.8), R26 (53, 17), LD5 (53, 21), R22 (50.5, −14), LD4 (50.5, −17.5).
- `DESIGN_SPEC.md` asks for "keepout ≥ 15 mm × module width beyond antenna region, or antenna overhanging the edge". Neither is met.
- Recommendation: either let the antenna overhang the edge by ≥ 6 mm, or widen the pour and parts keep-out to |y| ≥ 15 mm for x ≥ 49 (both layers) and move C22/C23/R26/LD5/R22/LD4 away.

---

## 3. JLCPCB manufacturability

### 3.1 BLOCKER B1: Gerbers without traces and vias

`fab/EMSinterface_V2.0-gerbers.zip`, parsed with my own parser:

| Layer | Content |
|---|---|
| F_Cu | 267 pad flashes; **0 draw (D01 with aperture) commands**; 2 dark pour regions with 160 clear regions |
| B_Cu | 2 pour regions; THT pads only; **0 draws** |
| `drill-L1-L2.drl` | only P1 (1.8 mm), J2 shell slots (0.8 mm) and P2 (1.0 mm); **no via hits** |

Meanwhile `dist/index/circuit.json` has 160 `pcb_trace` (1120 wire points) and 104 `pcb_via`.

The zip was evidently produced by `tsci export index.circuit.tsx -f gerbers` (see `docs/TOOLCHAIN.md`), which re-evaluates the board **without** the autorouter result. A board made from this zip would have every signal pad isolated in a GND flood.

I verified a fix in the scratchpad:
- `npx tsci export dist/index/circuit.json -f gerbers -o …` produces F_Cu with 4255 D01s, B_Cu with 2809 D01s, and 114 drill hits (10 PTH + 104 vias, T13 = 0.2 mm).
- Its isolation also measures 6.400 mm.
- **Export the fab data from the routed circuit.json**, then re-check (and fix B3 first).

`scripts/jlc_bom_cpl.py` reads that same zip, but its BOM/CPL content does not depend on routing.

### 3.2 BLOCKER B3: vias

- All 104 vias are 0.2 mm hole / 0.3 mm diameter (`pcb_via.hole_diameter/outer_diameter`), giving a 0.05 mm annular ring.
- JLC standard 2-layer limits:
  - via drill ≥ 0.3 mm (0.15–0.2 mm only on 4+ layers);
  - via diameter ≥ 0.5–0.6 mm;
  - annular ring ≥ 0.13 mm.
- This will fail DFM or produce breakouts.
- Set the via size to 0.3/0.6 mm and re-route; the spec itself says "0.3 mm drill".

### 3.3 Other fab rules

| Item | Value found | JLC 2-layer | Verdict |
|---|---|---|---|
| Min trace width | 0.15 mm | 0.127 mm (0.1 mm limit) | OK |
| Min spacing | 0.100 mm (5 pairs) | 0.127 mm std | MAJOR (M3) |
| PTH drills | 1.8 (P1), 1.0 (P2), 0.8 slots (J2, 1.5 / 1.2 long via G85) | ≥ 0.2 / plated slot ≥ 0.5 | OK |
| NPTH | 0.6 (USB pegs), 3.2 (MH) | ≥ 0.5 | OK |
| Isolation slots | 2.0 mm routed in Edge_Cuts | ≥ 1.0 mm milled | OK |
| Board | 110 × 60 mm, r = 2 mm corners, 2 layers, 1.6 mm | | OK |
| Pour to board edge | 0.20 mm | ≥ 0.3 mm recommended | MINOR (pull back to 0.5 mm) |
| Pour / trace to NPTH | 0.19 / 0.21 mm | ≥ 0.2–0.3 mm | MINOR, and see M8 |
| Silkscreen line width | 0.036–0.15 mm (1652 strokes at 0.036 mm) | ≥ 0.15 mm, text ≥ 1 mm | MINOR: small refdes texts will not print legibly |
| Silk over exposed pads | 5.5 mm² (ESP32 outline over all module pads, USB-C outline over shell legs) | JLC clips silk | MINOR |
| Assembly side | all 80 CPL rows Top, all SMD pads top | single-sided | OK |
| Pad-to-pad between different parts | no pair < 0.35 mm | | OK |
| Courtyard overlaps | D5/D6 3.86 mm², C26/C27 1.82, JP1/R27 1.52, C20/R20, C22/C23, C22/R20 0.68, C4/R15 0.54, C10/R16 0.51, R10/R12 0.08 | | MINOR (0805 parts, no pad clash); D5/D6 worth spreading |

### 3.4 BLOCKER B2: opto footprint pin order (found by the CPL cross-check)

`lib/opto_so8_gw300.tsx` places the right-hand pads `pin${8 - i}` at `pcbY = -y`, with ys = [3.81, 1.27, −1.27, −3.81]. Pin 5 is therefore at the top-right (beside pin 1) and pin 8 at the bottom-right (beside pin 4).

On the real DIP/SMD-8 (and the EasyEDA footprint of C92651/C336082), pins 1–4 run down one side and **5–8 come back up the other**. Pin 8 is opposite pin 1.

`rot.py` finds a 7.62 mm residual for every rotation, so no CPL rotation can fix it. Once assembled, the real part's pins land on these nets:

| Optocoupler | Real VCC (pin 8) on | Real GND (pin 5) on | Signal pins |
|---|---|---|---|
| OC1 (6N137) | GND | V3V3 | VO (6) on the VE net, VE (7) on MCU_RX |
| OC2 (6N136) | GND_EMS | V5_EMS | VO/VB swapped |

The supply is reverse-polarised and the parts are non-functional or destroyed.

Fix: number the right column bottom-to-top (pin 5 at y = −3.81 … pin 8 at y = +3.81), then re-route. The isolation geometry is unchanged.

### 3.5 CPL rotations vs EasyEDA (`rot.py`)

Method:
- Each part's EasyEDA footprint is rotated by the CPL angle and placed at the CPL mid.
- Each pad number is compared with our pad of the same pin number.

Results:
- **These parts match** (within the footprint size difference, ≤ 0.26 mm; U1 0.56 mm from the LS6.0 vs tscircuit soic8 row): P1, P2, F1, F2, L1–L3, all R/C, D1–D7 (BAT42W pad 1 = A handled), LD1–LD5, Q1, U1, U2, U4, U5, C12/C14 (pad 1 = +).
- **SW1/SW2**: the pads coincide. The pin assignment (top row = one terminal) is consistent with EasyEDA pads 1/2 being the 6 mm-spaced pair. OK.
- **J2 USB-C (MAJOR M1)**: the EasyEDA footprint at 0° has its mating face toward −Y. Ours faces +Y (board edge), so the **rotation must be 180°** (CPL says 0) and Mid Y should be 24.874 mm (CPL 24.999). tscircuit itself warns `incompatible_pin1_locations` for J2.
- **U3 ESP32 (MAJOR M1)**: the rotation (270) is correct, but the EasyEDA origin is the centre of the pad array, not the tscircuit component centre. The **correct Mid X is 38.615 mm**; the CPL says 41.98, a 3.37 mm error toward the antenna edge, so the module would overhang the board. The EPAD position agrees once corrected.
- **P1 (BLOCKER B5)**: the 2 pads match at 90°, but the EasyEDA outline of C441236 (right-angle "弯插") spans y = −10.9…+1.3 about its pins.
  - At 90° the 11.8 × 12.2 mm body covers x −52.3…−40.1, |y| ≤ 5.9. That is over F1/F2 (x −44.8) and L1/L2 (x −41.8), and the plug opening faces the board interior.
  - The local footprint (`Mstba2`, silk ±5 mm centred) hides this.
  - Fix: rotate to 270° with the pin order adapted, or use a vertical terminal, and keep that area clear.
- R2–R4 (C53284030): no EasyEDA footprint is available. A 2010 part is symmetric, so this is OK.
- The CPL has 80 rows. The BOM has 44 lines covering 80 designators, and the two sets agree.

### 3.6 BOM/CPL format, LCSC and Extended parts

- **BOM:** header `Comment,Designator,Footprint,LCSC Part #`, with designators comma-joined in quotes. This is a valid JLC format.
- **CPL:** header `Designator,Mid X,Mid Y,Layer,Rotation`, values with an `mm` suffix, `Top`. Valid; negative coordinates are accepted by JLC.
- Both files use CRLF line endings, which is fine.
- **Missing LCSC numbers:** TP1, TP2, TP3 and JP1. These are intentionally unassembled (test pads and solder jumper). The mounting holes have none, as expected. No assembled part is missing an LCSC number.
- **Extended parts (jlcsearch `is_basic = false`, `is_preferred = false`): 15 unique, about 15 × $3 setup.**
  - C107120 (C1 68 pF)
  - C17384 (R15 1.3 k): could be replaced by a Basic E24 value
  - C910822 (F1/F2)
  - C98021 (L1/L2)
  - C43183 (L3)
  - C49256851 (C12/C14)
  - C53284030 (R2–R4)
  - C371172 (JW5017S)
  - C92651 (6N137S)
  - C336082 (6N136S)
  - C2913202 (ESP32-S3)
  - C165948 (USB-C)
  - C7519 (USBLC6)
  - C441236 (P1)
  - C32713270 (P2)
- **Preferred-extended (no fee):** C1717, C17590, C22466362 (BAT42W).
- Everything else is Basic.
- P1, P2 and the J2 shell legs are THT, so JLC "Standard" PCBA with THT soldering is required. Stock could not be read (jlcsearch returns `stock: null`).

---

## 4. Visual check (`pcb.svg` rendered at deviceScaleFactor 1, and `docs/img/pcb.png`)

- Both images agree. All nets look routed and **no ratsnest lines are visible**. B4 is invisible because the open pads share a port.
- No part's pads lie outside the board. The cutouts are drawn as magenta slots under OC1/OC2 as intended.
- The ESP32 keepout hatching sits at the right edge, and the antenna lines up with the edge.
- The SVG/PNG show traces, but the shipped Gerbers do not (B1).
- The P1 silk box (local footprint) overhangs the left edge by 0.6 mm (intended for a terminal at the edge). The real part is right-angle and inward-facing (B5).
- C12/C14 silk shows two "+" marks each, one inside and one outside the body (MINOR, cosmetic).
- Small refdes texts are hair-line (silk widths, see 3.3).

---

## 5. Required actions before ordering (in order)

1. Fix the opto footprint pin order (B2).
2. Set vias to 0.3/0.6 mm, set clearance ≥ 0.15–0.2 mm and widen power traces (B3, M2, M3), then re-route.
3. Connect the USB-C B6/B7 pads (B4). Rework the P1 orientation or footprint (B5).
4. Move the buck parts and opto bypass caps (M4). Add AMS1117 tab copper (M5). Widen the antenna keep-out (M6).
5. Add a second bridge or shorten the slots (M7). Add a pour keep-out of r ≥ 3.5–4 mm around the mounting holes, or require nylon hardware (M8).
6. Export the Gerbers **from `dist/index/circuit.json`** (B1). Regenerate the CPL, then fix the J2 rotation (180°) and the U3 mid point (38.615 mm) (M1).
7. Re-run the isolation check on the new Gerbers. The current value is 6.40 mm, which is adequate for SELV.
