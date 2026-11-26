# R6 - Circuit and parts review (round 3, independent)

Scope: electrical correctness and parts (V2.0 tscircuit port of EMSinterface V1.0 + ESP32-S3 + USB-C).
Primary data used (docs/review/* was NOT read): `hardware/EMSinterface_V1.0.sch` (parsed with an own XML script),
`tscircuit/dist/index/circuit.json` (10:40, newer than all sources), `src/*.tsx`, `lib/*.tsx`, `fab/*BOM*.csv`, `fab/*CPL*.csv`,
EasyEDA API (`easyeda.com/api/products/<LCSC>/components`, 56 of 57 codes; C53284030 = 404), JLCPCB API (`selectSmtComponentList`),
LCSC datasheets (6N137S-TA1-L, 6N136S-TA1-L, JW5017S, AMS1117, BSMD0805-050-24V, BAT42W, KT-0805G, NCD0805R1, LM393, ESP32-S3-WROOM-1),
EMS-ESP32 `src/core/system.cpp` (branch `dev`, `load_board_profile`).

## Verdict
**0 BLOCKER, 1 MAJOR, 9 MINOR, plus INFO.**  The V1 circuit is reproduced 1:1 in real copper, the MCU additions are electrically
correct, and the fab data (BOM/CPL) is consistent with the EasyEDA/JLC libraries.  One real design-input error was found
(green LED forward voltage), everything else is margin/verification work.

## What was verified (positive findings)
1. **V1 parity from copper, not from source nets.**  Own geometry-based connectivity extraction from `circuit.json`
   (pads, plated holes, trace segments with width, vias, both layers, 10 brep pours, shapely union-find): 84 physical copper nets,
   **0 shorts, 0 opens**, no pad of any named net floating, min. clearance between different nets 0.152 mm (U4.6 pad / VBUS trace),
   no copper inside the antenna keepout (x 48..57), **min. EMS-to-MCU copper distance 7.05 mm** (at the opto slot).
   All 33 V1 nets (pin-for-pin incl. JLC pad numbering, C12->C12+C14, C10->C10+C30) match the parsed Eagle netlist; the only
   deviation is `MCUVCC` P2.1 -> `P2_3V3` behind open JP2 (intended).  `scripts/check_netlist.py` also run: **ALL OK**.
2. **Pin 1 / polarity vs EasyEDA symbols**: BAT42W pad1=A (D1-D5 ok), 1N4148W pad1=K (D6 ok), B5819W pad1=K (D7 ok),
   NCD0805R1 pad1=K (LD1 ok), KT-0805G pad1=A (LD2-5 ok), tantalum and JVJ electrolytic pad1=+ (C29, C12, C14 ok),
   BC817-40 1=B 2=E 3=C (ok), USBLC6 1/6=IO1, 2=GND, 3/4=IO2, 5=VBUS (ok), AMS1117 1=GND 2=VOUT 3=VIN 4=VOUT (ok),
   LM393 pad map (ok), JW5017S 1=BST 2=GND 3=FB 4=EN 5=VIN 6=SW (ok), 6N137 1 NC 2 A 3 K 5 GND 6 VO 7 VE 8 VCC and
   6N136 7=VB (ok).  J2: every contact mapped by coordinates to the EasyEDA pad name: B1A12/A1B12 -> GND, A4B9/B4A9 -> VBUS,
   A5 -> CC1, B5 -> CC2, A6+B6 -> D+, A7+B7 -> D-, A8/B8 -> SBU (NC), legs -> SHELL.  D+ -> GPIO20 (U3.14), D- -> GPIO19 (U3.13) correct.
3. **CPL vs EasyEDA geometry** (own script, not the repo's): for all 83 BOM refs the EasyEDA pad set (origin = footprint origin,
   y flipped, 0.254 mm/unit) rotated by theta=CPL rotation (CCW) and translated to the CPL mid point lands on the real pads
   (max error 0.00-0.27 mm = generic-footprint tolerance, see m8; ESP32 EPAD, J2 and all numbered pads matched, 0 pad-number
   mismatches).  CPL mids/rotations are therefore self-consistent.  Open point: m1.
4. **EMS-ESP32 S32S3** (system.cpp): `data = {led 2, dallas 18, rx 5, tx 17, button 0}`, `valid_system_gpios_ = {0,2,5,17,18}`.
   Board: GPIO5 = MCU_RX (U3.5), GPIO17 = ESP_TX (U3.10), GPIO2 = LED (U3.38), GPIO0 = BOOT (U3.27).  Matches.
5. **ESP32-S3 strapping / USB**: GPIO0 10k pull-up + button, GPIO3/45/46 unconnected (internal defaults: JTAG eFuse, VDD_SPI and ROM
   log default low), GPIO35-37 (octal PSRAM) not wired, EN 10k + 1 uF + button (Espressif reference RC), native USB D+/D- with
   USBLC6-2SC6 (ESD IC 5-6 mm from J2), 2 x 5.1k CC, shell 1M || 4.7 nF, VBUS PTC F3 before the LDO.
6. **JP1 open = bus idle**: MCU_TX is pulled to V3V3 by R27 100k, both OC2 LED branches (R14 and R19+LD2) and P2.2 see ~0 V,
   OC2 LED off -> VO high (R11 to 5V) -> U1B IN- > IN+ -> U1B output low -> Q1 off.  Also idle when ESP32 is in reset (GPIO17 Hi-Z,
   R27 holds) and when V3V3 is unpowered.  JP2 open: P2.1 only on `P2_3V3` (2 pads), no copper to V3V3.
7. **Stock / class (JLCPCB API, all codes)**: every BOM part is orderable, lowest stock L3 C43183 1885, L1/L2 5897, P1 20985,
   BAT42W 22090.  Values and packages match (R14 150R = C17471 0805W8F1500T5E; 68R 2010 = CL2010FN68RB 750 mW; C5 10nF, C21 4.7nF,
   C20 1uF 50V X7R etc.).  Basic: C15850, C46653, C1710, C49678, C12891, C28323, C1744, C16133, C81598, C8598, LED C84256/C2297,
   SW C318884, U1 C7955, U5 C6186 and all resistors except C17384/C53284030.

## Recomputed values

### Optocouplers (datasheet: Lite-On 6N137-L series, 6N135/6N136-L series)
| item | formula / inputs | result | limit |
|---|---|---|---|
| V5 (JW5017S) | 0.8 V x (1 + 6.8k/1.3k), VFB 0.776-0.824, R 1% | 4.985 V typ, 4.78-5.19 V | OC2/U1 ok (U1 36 V) |
| OC1 LED (R10 470R, U1A sink) | (V5 - Vf 1.38..1.70 - VOL 0.15..0.5)/470 | typ 7.2 mA, worst 5.5 mA, max 8.3 mA | IFH 5-15 mA, IF max 20 mA ok |
| OC1 real need | ITH 5 mA max is defined at IOL = 13 mA; real load = R13 0.7 mA + LD3 ~1 mA | ~1 mA needed | margin > 5x (LM393 VOL 400 mV only guaranteed to 4 mA, irrelevant here) |
| OC1 supply | VCC 3.3 V | datasheet has a 2.7-3.6 V column, VE (pin 7) tied to VCC ok | RL 330R-4k recommended: R13 = 4.7k is above (m5) |
| OC2 LED (R14 150R) | (V3V3 3.27..3.33 - Vf 1.2..1.7 - VOL 0.10..0.40)/150 | typ 10.5 mA, worst 7.8 mA, max 13.5 mA | IF max 25 mA ok (270R gave 5.2-6 mA) |
| ESP32 GPIO17 sink | OC2 LED + LD2 branch ~0.5-3 mA | 11-16 mA | ESP32-S3 IOL 28 mA @ VOL 0.495 V, VOL <= 0.1 VDD; ok |
| OC2 output needed for TX | VO must drop below comparator ref 0.65 V: Ic >= (4.8-0.65)/4.7k | 0.9 mA | CTR 19 % min (IF 16 mA): 7.8 mA x 0.19 x ~0.9 = 1.3 mA -> margin 1.4x worst case BOL (was < 1x with 270R), typ 2.5 mA |
| OC1 (VCC 3.3 V) pull-up current | 3.3/4.7k | 0.7 mA | IOL 13 mA ok |

### LEDs
| LED | circuit | datasheet Vf | I (nominal / realistic) |
|---|---|---|---|
| LD1 red NCD0805R1, 1k2 from 5 V | (4.985-2.0)/1200 | 1.5-2.6 V @20 mA | 2.5 mA (dim, 115 mcd@20 mA, ok) |
| LD2/LD3/LD4/LD5 green KT-0805G, 220R from 3.3 V | (3.3 - Vf)/220, LD2/LD3 also minus 0.2-0.3 V (GPIO17 / OC1 VO low) | **2.6-3.1 V @5 mA** | 0.9-3.2 mA (LD5, LD4), **0-2.3 mA (LD2, LD3)**, dark in the 3.0-3.1 V bins -> M1 |

### Comparators (U1, LM393DR2G)
N$7 = Vf(D6 1N4148W at (Vbus-0.65)/10.39k ~ 1.4 mA) = 0.62-0.68 V (0.55 V at 60 C).  U1A: IN+ = N$7 (via R6 47k), IN- = 0.909 x N$7 (R7/R8) ->
idle margin 55-62 mV vs worst offset 5 mV (max, LM393) + 250 nA x (47k - 9.1k) = 9.5 mV -> >= 39 mV margin, no false trigger.
Detection: N$8 = N$7 + I x R5 ~ 1.2 V, so a bus step dVbus appears as 3.75 % on N$8 -> IN+ is pulled down by ~0.037 dVbus (C2 10uF
passes it, IN- sees ~0.27 of it through C3): trigger at dVbus ~ 2 V (EMS bus level step is much larger).  IN+ stays > 0.4 V,
inside the LM393 input range (-0.3 V .. VCC-1.5 V).  U1B: IN+ = N$7 (0.65 V), IN- = OC2 VO (see above).  All unchanged vs V1.

### Buck (JW5017S 4.5-26 V, 1.2 A, 1.2 MHz, VFB 0.8 V)
* 5 V: 4.985 V typ (datasheet table uses 16k/3.0k = 5.07 V); feedback current 0.6 mA; BST C9 100 nF ok; EN pulled to VIN through 100k (EN rated 26 V) ok.
* Inductor L3 SWPA5020S4R7MT: 4.7 uH, Isat 2.7 A, Irms 2.2 A, DCR 74 mOhm.  Ripple dI = 5 x (1-5/16)/(4.7u x 1.2M) = 0.61 A pp (0.70 A at 24 V),
  load < 0.1 A, switch limit 2 A < Isat 2.7 A -> ok.  Min on time at 24 V: 174 ns > 80 ns ok.  UVLO 4.2 V.
* Caps: input C10 10 uF/25 V X5R (+C30 100 nF 50 V) + 2 x 1000 uF/25 V, output C11 22 uF/25 V X5R (datasheet recommends 22 uF), all >= 1.5x working voltage at the
  nominal 15-16 V bus; at a 24 V bus the 25 V parts are at 96 % (m9).
* Power path: D7 B5819W 1 A/40 V, bridge D1-D5 BAT42W VRRM 30 V / 0.2 A avg / IFSM 4 A.  TX stage: Q1 on = 15 V / 204 R = 73 mA, 0.36 W per 68R (750 mW) ok.

### USB / LDO
* AMS1117-3.3: dropout 1.3 V max @0.8 A (~1.1 V @0.4 A).  VBUS 4.75 V - PTC (0.1 Ohm min .. 0.85 Ohm max R1max) x 0.35 A = 4.45..4.72 V at U5 -> only 0.05-0.1 V above the
  worst dropout at WiFi peaks (m2).  LDO dissipation (5-3.3) x 0.15 A = 0.26 W avg, 0.6 W at 350 mA, 90 K/W SOT-223 -> +23 K / +54 K (copper pour on tab net, ok).
* PTC F3 BSMD0805-050-24V: Ihold 0.5 A, Itrip 1.0 A, Vmax 24 V, R 0.1-0.85 Ohm.  Ihold derates to ~0.35-0.4 A at 50-60 C (enclosure).
* C29 TAJB107K006RNJ: 100 uF 6.3 V, ESR 1.7 Ohm @100 kHz, used at 3.3 V = 52 % of rating (m6).

## Findings

### BLOCKER
none.

### MAJOR
**M1  Green LEDs LD2-LD5 (KT-0805G, LCSC C2297) have Vf = 2.6-3.1 V @ 5 mA, not ~2 V; with 220R on a 3.3 V rail they are dim to dark.**
Evidence: datasheet "0805 emerald green" (513-528 nm InGaN), section 5: `VF min 2.6 max 3.1 V @ IF = 5 mA`, VF bins VM 2.6-2.7 ... VQ 3.0-3.1 V.
R18/R19 were changed from 1k2 (V1) to 220R in V2 on the assumption of a ~2 V LED.  At V3V3 = 3.27-3.33 V: LD5 (R26) 0.9-3.2 mA, LD4 (GPIO2, VOH ~3.2 V) 0.5-2.7 mA,
LD3 (cathode = OC1 VO low 0.15-0.3 V) 0-2.3 mA, LD2 (cathode = GPIO17 low 0.1-0.4 V) 0-2.3 mA; for the VP/VQ bins (Vf >= 2.9 V) LD2/LD3 do not light at all.
These are the RX/TX activity indicators (diagnostics, not function), but the documented 4-5 mA is wrong and the result depends on the LED bin.
Fix (pick one): (a) change LD2-LD5 to a true green/yellow-green AlGaInP 0805 (Vf ~2.0-2.2 V), e.g. C2292 KT-0805YG (Extended) or C98221 LTST-C170KGKT (Extended), keep 220R;
(b) use the Basic red NCD0805R1 (C84256, Vf 1.5-2.6 V, 20 mA test) for them, 220R gives 3-5 mA; (c) keep C2297 and accept dim LEDs, but then use 100R for LD4/LD5 only
(LD2/LD3 cannot be fixed with R alone).  Then update docs (4.1 mA claims) and the BOM/CPL.

### MINOR
**m1  CPL rotation sign must be confirmed in the JLC preview before paying.**  Everything is consistent under "positive CPL rotation = CCW" (my independent check matches
the repo's assumption).  The sign is not provable offline; it matters (mod 180) only for asymmetric parts at 90/270: D5, D6 (90), LD2-LD5 (90), C29 (270), U1, U3, U4, U5, OC1, Q1 (270), OC2 (90), P1 (270).
J2 (180), D1-D4 (0/180), SW, R/C/L (symmetric) are insensitive.  Open the JLC assembly viewer and check pin-1 dots of U1, U3, OC1/OC2, Q1, U4, U5, D5, D6, LD*, C29.

**m2  AMS1117 headroom behind the PTC at USB-host minimum voltage.**  See numbers above: 4.75 V host, PTC up to 0.85 Ohm, 0.35-0.4 A WiFi bursts -> Vin ~4.4-4.45 V vs 3.3 V + 1.1..1.2 V dropout;
V3V3 may sag a few 10 mV during bursts, F3 runs close to its hot hold current.  Fix: use a 0.75 A hold / 0.1 Ohm class PTC (BSMD0805-075-xx has 12/16 V only) or a 1206 1 A 6-16 V PTC;
or replace AMS1117 by a low-dropout 3.3 V LDO (SOT-223 AP2114H-3.3, ~0.25 V).  Cheapest: accept (ESP32 brown-out at 2.7 V is far away).

**m3  Capacitance behind the PTC/LDO >> USB 10 uF rule.**  C24 10 + C26 22 + C27 10 + C29 100 + 2 x 0.1 = ~142 uF, hot-plug charge ~470 uC at 3.3 V; the LDO has no soft start (limit ~1 A).  Host ports may droop/
reset at plug-in.  Mitigation if seen: drop C26 (22 uF) and/or use C29 = 47 uF, or accept (typical ESP32 dev boards do the same).

**m4  TX falling-edge delay from C5 10 nF (inherited from V1).**  VO falls through the phototransistor with Ic_net = Ic - (5 V - VO)/4.7k: t ~ 10 nF x 4.35 V / I_avg =
~22 us (typ CTR), ~46 us (CTR min), ~90 us (CTR min + aging) vs the rising edge ~5 us, bit time 104 us.  Receiver sampling at mid-bit still works for <= ~50 us.
With R14 = 150R this is 2x better than V1 (270R); if bench shows TX framing errors, reduce C5 to 2.2-4.7 nF or R11 to 3.3k.  Needs bench verification.

**m5  R13 4.7k exceeds the 6N137 recommended RL range (330R-4k).**  Functionally irrelevant at 9600 baud (rise ~0.1 us), but out of datasheet recommendation.  3.3k 0805 1% (a Basic value, look up the C-code) or keep and note.

**m6  Tantalum C29 6.3 V at 3.3 V = 52 % (AVX/Kyocera recommend <= 50 % for low-impedance sources) and 32 uF ceramic in parallel (C26 + C27) removes the ESR zero above ~4 kHz.**  Standard ESP32 AMS1117 boards work, but if the 3V3 rail rings/oscillates at bring-up, DNP C26 first.  A 10 V tantalum (TAJB107K010RNJ) is the cleaner choice.

**m7  EMS bus inrush into C12+C14 (2000 uF) through BAT42W (IFSM 4 A, 30 V VRRM) is only limited by the bus master and PTC/L1/L2 (DCR 0.2 Ohm, Isat 1 A).**  Inherited from V1 (2200 uF), listed for completeness; V_RRM 30 V leaves 20 % over a 24 V worst-case bus, C12/C14/C10 25 V are at 96 % of rating there.

**m8  Footprints are generic approximations of EasyEDA, not copies.**  Max centre deviation: 0805 R/C 0.09 mm, 1206 0.13, F0805 PTC 0.19 (generic 0805 pitch 1.83 vs 2.20, body is 2.0 mm so fine), OC1/OC2 0.205 (rows 9.5 mm vs EasyEDA 9.09 / Lite-On recommended 9.0 mm, pads 1.8 x 1.4 vs 1.5 x 1.5: toe overhang 0.4 mm, acceptable and keeps creepage),
Q1 0.2, U4 0.15, U5 0.27 (tab 3.8 x 2.0 vs 3.6 x 2.34).  R2-R4 (CL2010FN68RB) have no EasyEDA record (404), generic 2010 pads 1.8 x 2.7 @ +-2.2 mm, JLC assembles with its own library footprint, rotation irrelevant (symmetric).  No pin-1/polarity effect found.

**m9  Extended parts (18 types, ~USD 3 setup each at JLC economy/standard assembly):** C107120, C1717 (C4 1.5nF), C49256851, C22466362, C910822, C165948, C98021, C43183, C92651, C336082, C441236, C32713270, C20069155, C17384 (R15 1.3k), C53284030, C371172, C2913202, C7519.
Avoidable: R15 1.3k (use Basic 1.2k + R12 6.2k -> 4.93 V, or 1.5k + 7.5k/7.87k) and C4 (1.5 nF -> Basic 1 nF/2.2 nF, value is a V1 filter choice, check).  Not a defect.
THT parts P1, P2 and the J2 shell legs are THT in an SMT order: confirm JLC "through-hole/hand soldering" option (FAB checklist item).

**m10  Doc inconsistency:** `docs/ESP32_EMSESP.md` still says "R22 1 k" for the GPIO2 LED; BOM/TSX use 220R (C17557).  Also correct the LED current claims after M1.

### INFO (no action needed)
* LM393 VOL guarantee is 400 mV @ 4 mA only; OC1 IF = 5.5-8 mA is far above what the real load needs (~1 mA), see table.  LMV393 -> LM393DR2G is acceptable.
* OC2 pin 7 (VB) open as in V1.  Bypass for OC2 VCC is C13 (7 mm), OC1 C7 (4 mm).
* VBUS trace necks down to 0.275 mm for ~2.4 mm (autorouter); at <= 0.5 A (IPC-2221 external: ~0.1 mm needed for 20 K) irrelevant.
* P2 external-MCU scenario: V1 powered the header MCU from P2.1; V2 needs JP2 closed (and USB unplugged, or else the 3.3 V rail is back-fed: AMS1117 has no reverse protection).  Documented in DESIGN_SPEC; keep the silk "3V3 OUT" warning.
* EMS-ESP default `tx_mode` is on: with JP1 open firmware tries to transmit into an idle line (ack timeouts in the log).  Set Tx mode "off"/ignore until JP1 is bridged.
* ESP32 N16R8: GPIO45/46/3 unconnected is correct for 3.3 V flash/octal PSRAM; GPIO47/48 free.

## Suggested actions (ordered)
1. M1: change LD2-LD5 LED type (or at least verify visually on first board).  2. m1: JLC viewer check of polarized parts (gate before payment).
3. m2/m6: decide on PTC/LDO headroom and tantalum rating (cheap: 10 V tantalum).  4. m4: plan a bench check of the TX path with JP1 bridged (scope on MCU_TX / Q1 collector), C5 fallback value 2.2-4.7 nF.
5. m5, m9, m10: optional BOM/doc clean-ups.

## Reproduction
Own scripts (scratchpad `/tmp/claude-0/s/`): `phys.py` (geometry connectivity, clearance, isolation, keepout), `cmp.py` (Eagle vs physical nets), `fpcmp.py` (EasyEDA vs actual pads, CPL rotation, J2 map), `jlc.py`/`q.py` (JLC API).
Repo script: `python3 scripts/check_netlist.py` (ALL OK).
