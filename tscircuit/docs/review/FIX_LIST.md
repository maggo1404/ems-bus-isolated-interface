# Fix list V2.0 – consolidated from reviews R1, R2, R3 (+ user decisions)

Details/evidence: R1_circuit_fidelity.md, R2_isolation_layout_fab.md, R3_mcu_usb_emsesp.md.

## BLOCKER
1. **Opto footprint mirrored** (R1-B1, R2-B2): lib/opto_so8_gw300.tsx right column → pin5 opposite pin4, pin8 opposite pin1. Verify against EasyEDA C92651/C336082.
2. **USB-C duplicate pads not connected** (R2-B4, R3-B1): lib/usbc16.tsx – give A6/B6 (D+), A7/B7 (D-), each VBUS pad, each GND pad distinct ports; connect pairs with explicit traces/nets so both plug orientations work. Check for any other footprint using duplicate portHints for physically separate contacts (Tactile5x5, ESP32 EPAD, shell legs) – internal-connection only where the part really connects internally.
3. **Gerbers without traces/vias** (R2-B1, R3-B2): export from the routed dist/index/circuit.json (`tsci export dist/index/circuit.json -f gerbers`), add a script `scripts/export_fab.sh` doing build → export → BOM/CPL conversion → verification that copper layers contain trace draws and drill file contains vias.
4. **Vias too small** (R2-B3): ≥ 0.3 mm drill / ≥ 0.6 mm pad (JLC 2-layer: min 0.3/0.5, use 0.3/0.6). Find the tscircuit board/autorouter prop for via size.
5. **P1 terminal orientation** (R2-B5): KF2EDGRC-5.08-2P C441236 right-angle, plug opening must face out of the board edge; body must not cover other parts. Check CPL rotation vs EasyEDA footprint.

## MAJOR
6. **Q1 → BC817-40 C20069155** (user decision; R1-M1). Verify SOT-23 pinout (1=B 2=E 3=C) via EasyEDA. R9 stays 4k7.
7. **CPL rotation/position errors** (R2-M1): J2 rotation, U3 Mid X (footprint origin vs part centroid), verify every polarized/asymmetric part against EasyEDA footprint origin and rotation (JLC CPL convention). Document in docs/CPL_CHECK.md.
8. **Trace widths** (R2-M2): power nets ≥ 0.5 mm (VBUS, V3V3, GND, GND_EMS, V5_EMS, EMS_VIN, buck SW node, bus path F1/F2/L1/L2/bridge/R2–R4/Q1 ≥ 0.4 mm), signals 0.25 mm. Use per-net trace thickness / autorouter config; manual <trace> where needed.
9. **Clearance** (R2-M3): ≥ 0.2 mm between different nets everywhere (JLC min 0.127, target 0.2).
10. **Decoupling placement** (R2-M4): C10 (buck in) and C11/C8 tight loop at U2/L3; C7 at OC1 VCC/GND (pins 8/5), C13/C8 at OC2 supply, 100 nF at U1 VCC, ESP32 caps at 3V3 pin.
11. **AMS1117 thermal** (R2-M5): copper area on tab (V3V3) ≥ ~2–3 cm² both layers + thermal vias.
12. **Antenna keepout** (R2-M6, R3 minor): ESP32 antenna overhanging board edge OR ≥ 15 mm copper/part-free area around antenna on both layers (Espressif). Prefer: antenna part of module at the board edge with no copper underneath and nothing within 15 mm beside it.
13. **Mechanical strength** (R2-M7): isolation slots only under/near the opto bodies (e.g. 2 mm × ~12 mm each), NOT to the board edge; the 6.4 mm pour gap provides the barrier elsewhere. Keep ≥ 6 mm copper clearance across barrier incl. around slot ends.
14. **Mounting holes** (R2-M8): pour/copper keepout ≥ 2 mm around each M3 hole (insulating hardware advisable; holes on EMS side and MCU side are not shared).
15. **P2 pin 1 backfeed** (R3-M3): add **JP2** solder jumper (default OPEN) between V3V3 and P2.1, silkscreen "3V3 OUT". Label P2 accordingly.

## MINOR
16. AMS1117 stability: add **tantalum 100 µF/6.3 V TAJB107K006RNJ C16133 (Basic)** on V3V3 near U5 (or 10 µF/16 V C7171 basic); keep ceramics.
17. JP1: gap 0.3–0.5 mm, label "TX EN" directly next to it, no paste; same style for JP2.
18. DESIGN_SPEC.md / ESP32_EMSESP.md: C12+C14 2×1000 µF SMD, Q1 BC817-40, JP2, S32S3 is auto-selected on ESP32-S3 (per R3).
19. Courtyard overlaps (D5/D6 …), silkscreen line width ≥ 0.15 mm, text ≥ 0.8 mm height, no silk over pads, pour ≥ 0.5 mm from board edge.
20. USB D+/D- routed as a short pair, ESD close to connector.
21. Remove scratch/compare_netlist.py (superseded).
22. **Enclosure Hammond 1591XXCFLBK (Reichelt 221253)** – see docs/ENCLOSURE.md. Board outline 110.0 × 60.0 mm with 4 corner notches 5.5 (X) × 8.0 (Y) mm (R3.5) for the lid-screw bosses; 4 mounting holes Ø3.5 mm NPTH at (12.75|10.25), (97.25|10.25), (12.75|49.75), (97.25|49.75) mm from bottom-left (= ±42.25 / ±19.75 from centre), keepout for screw heads Ø7 mm. Inner height 36 mm. EMS terminal P1 at the LEFT short wall (cable entry), ESP32 antenna at the RIGHT short wall (≥ 15 mm free beside antenna, no copper under it), USB-C on a long wall near a corner (housing cut-out ~10 × 4 mm), LEDs (LD1–LD5) positioned so they can be seen via holes/light pipes in the lid; buttons internal.

## Acceptance
- scripts/check_netlist.py OK, scripts/check_isolation.py ≥ 6.0 mm both layers, DRC 0 errors (placement DRC only the intended opto/slot overlap if unavoidable).
- New scripts/check_fab.py on the Gerbers: trace draws present on both copper layers, all vias drill ≥ 0.3 mm & annular ≥ 0.13 mm, min trace width per net class, min clearance ≥ 0.2 mm, no copper in slots/antenna keepout, both USB D+ pads and both D- pads connected.
