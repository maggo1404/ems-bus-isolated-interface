# Fix list (coordinator) – to be applied in the fix pass after all reviews

## From R1
- [B1] lib/opto_so8_gw300.tsx: right pad column numbering mirrored → pin 5 must be opposite pin 4, pin 8 opposite pin 1 (`pin${5+i}` at pcbY=-y). Re-route, regenerate CPL.
- [M1] Q1 → **BC817-40** (user decision), LCSC **C20069155** (Preferred-Extended, no fee, 132k stock). Verify SOT-23 pinout 1=B 2=E 3=C via EasyEDA. Keep R9 4k7 (hFE 250–600).
- [m] DESIGN_SPEC.md: C12 is now C12+C14 2×1000 µF SMD (C49256851); Q1 BC817-40.
- [m] JP1 gap 1.04 mm → reduce to ~0.3–0.5 mm (easy to bridge), keep NO paste.
- [m] other R1 minors: see R1_circuit_fidelity.md.
