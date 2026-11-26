# JLCPCB Economic PCBA: rules and compliance of this board

Fetched and verified on 2026-11-26 (re-check at order time; JLC changes these pages).
Sources: https://jlcpcb.com/capabilities/pcb-assembly-capabilities (EN) and https://jlcpcb.com/de/capabilities/pcb-assembly-capabilities (DE, same table),
https://jlcpcb.com/help/article/98-pcb-assembly-faqs, https://jlcpcb.com/help/article/pcb-assembly-price,
https://jlcpcb.com/help/article/terms-and-conditions-of-jlcpcb-assembly-service, https://jlcpcb.com/solutions/pcb-prototype-assembly,
and the per-part page https://jlcpcb.com/partdetail/<LCSC> (field **PCBA Type**).

## Result: what blocked Economic

**Exactly one part: U3 = ESP32-S3-WROOM-1-N16R8 (C2913202). Its JLC part page says `PCBA Type: Standard Only`.**
Any single "Standard Only" part in the BOM forces the whole order to Standard PCBA. The capabilities table does not list this rule;
it is only visible per part (`jlcpcb.com/partdetail/C2913202` -> "PCBA Type | Standard Only"; Economic parts show "Economic and Standard").
Checked: **every** Espressif ESP32-S3 module in the JLC library is "Standard Only" (WROOM-1 N4/N8/N16/R2/R8, WROOM-1U, MINI-1/-1U, WROOM-2: 20 module part numbers
checked, e.g. C2913197/98/99, C2913201/03/04/05, C2913206, C2980296..300, C3013941..46, C42417293); there is no non-Espressif ESP32-S3 module in the library
(only the dev board C20626143). Only the bare chips are Economic (ESP32-S3R8 C2913194, S3FN8 C2913196, S3FH4R2 C3013940, ESP32-S3 C2913192; QFN-56 7x7), which would need a new RF/crystal/flash design: not done.

Everything else in the BOM (all 45 other LCSC numbers) is "Economic and Standard", including the THT parts and the USB-C (see table below). Per the capabilities page THT is allowed in Economic.

## Rules (verbatim from the capabilities page, Economic PCBA column unless noted)

| Feature | Economic PCBA | Standard PCBA |
|---|---|---|
| Assembly Types | "Single sided placement (SMT/Thru-hole)" | "Single & double sided placement (SMT/Thru-hole)" |
| PCB Layer | "2,4,6-layers" | "1 - 32 layers" |
| Thickness | "0.8mm - 1.6mm" | "No limit" |
| Dimension | "Single PCB Size: 10x10mm - 470x500mm; PCB Panel Size: 10x10mm - 250x250mm" | "70x70mm - 460x500mm" |
| Order Volume | "2 - 50 pcs" | "2 - 80000 pcs" |
| Surface Finish / Color | "Limited by specific options" (table: 1.6 mm green HASL (lead-free/leaded) or ENIG, 2-50 pcs; black HASL 2-50; 0.8/1.0/1.2 mm 2-30 pcs) | no limit |
| Delivery Format | "Single PCB, Panel with mouse bites" | + "Panel with V-cut" |
| Layer Stackup | "Standard stack-up only, special stack-up is not supported" | all |
| Gold Fingers/Castellated Holes/Edge Plating | "Not Support" | Support |
| Edge Rails / Fiducials | "Not necessary" | "Necessary" |
| Minimum Package | "0402" | "01005" |
| Minimum IC Pin Spacing | "0.4mm" | "0.35mm" |
| Minimum BGA Spacing | "0.5mm(center to center)" | "0.3mm" |
| Reflow temperature | "255+/-5 °C (not adjustable)" | "240+/-5 °C" |
| SPI | "No" | "Yes" (AOI, visual, X-ray for BGA: both) |
| Build time | "1 - 3 days" | ">= 4 days" |

FAQ on the same page: "Can you assemble THT components? ... Yes. JLCPCB supports Through-Hole Technology (THT) component assembly and mixed-technology (SMD + THT) PCB assembly within a single PCBA order. SMD components are typically assembled using reflow soldering, while THT components are assembled using wave soldering. This service is available under both the Economic and Standard PCBA."
Help FAQ 98: "Now JLCPCB can support through-hole components by offering wave soldering services, like connectors. The part's assembly type marked with 'wave soldering' in our assembly parts library will be assembled manually." / "for Economic assembly, please panelize your boards with mouse-bites."
Pricing page: "Extended Components Fee: For Economic PCBA orders, an additional labor fee applies to extended components that require extra feeder setup" (Basic and Preferred-Extended parts are free); Economic setup 8.18 USD vs 25.56 USD single-sided Standard; "Handling Fee: When both Economic PCBA and Standard PCBA are available ... price difference must be at least $14.93".
Terms (both services): "The distance between the body of the components and the edge of the board must be equal or greater than 2.5mm." / "Tooling holes, Edge rails and Fiducials are required for PCB assembly orders ... we will help to add or modify them by default." / "For Economic PCBA, orders from different customers are combined and produced together" / part placement/gap "medium density or low density standards of IPC-7351B".
Part-level fields (partdetail page): "Assembly Type: SMT Assembly | Wave Soldering", "PCBA Type: Economic and Standard | Standard Only". The parts-list API (`selectSmtComponentList`) does NOT expose either field; they are only in the part page HTML.

## Check of this board (scripts/jlc_economic.py, scripts/check_fab.py "Economic PCBA compliance")

| Item | Board | Verdict |
|---|---|---|
| Layers / thickness / size | 2 / 1.6 mm / 110 x 60 mm | ok |
| Sides | all parts Top, nothing on Bottom | ok (single-sided) |
| Smallest package / IC pitch | 0805 (2010, SOT-23, SOP-8 2.54 mm, ESP32 1.27 mm) / >= 0.95 mm | ok |
| THT parts | P1 (C441236), P2 (C32713270): "Wave Soldering", PCBA Type Economic and Standard | allowed; kept assembled |
| J2 USB-C (C165948) | "SMT Assembly" (shell legs are part of the SMT part), PCBA Type Economic and Standard | ok, **not changed** |
| C12/C14 SMD electrolytic C49256851 | SMT Assembly, Economic and Standard | ok |
| Fiducials / rails | none needed in Economic | ok |
| Qty / finish / colour (order form) | 2-50 pcs; choose HASL or ENIG, 1.6 mm, green (or black HASL) | user choice |
| **U3 ESP32-S3-WROOM-1-N16R8 C2913202** | **Standard Only** | **BLOCKER -> DNP, hand-solder** |
| Part-edge >= 2.5 mm | pads of C12 0.75 mm / R25 2.07 mm from edge (bodies: C12 ~2.35 mm), J2 is an edge connector | advisory only (same rule applies to Standard); JLC DFM preview decides |

No placement change was needed: the board is 100 % identical (Gerbers byte-identical apart from timestamps); only U3 is excluded from BOM/CPL.

## Consequences / hand-solder list
* **U3 (ESP32-S3-WROOM-1-N16R8, LCSC C2913202)**: marked `doNotPlace` in `src/mcu-side.tsx`, kept in the design and in the Gerbers (pads, paste, silk, keepout), removed from BOM/CPL. Order the module separately (LCSC C2913202) and solder it yourself (pads on the module edge + GND thermal pad: hot-air or hot plate with paste, or solder the EPAD through the 9 GND ports via the module; see docs/FAB_CHECKLIST.md). The list is generated into `fab/EMSinterface_V2.0-HANDSOLDER.csv`.
* P1 (bus terminal) and P2 (programming header) stay assembled by JLC's wave soldering. If JLC rejects THT in the order form anyway, mark P1/P2 as "do not place" in the parts step (or remove them from the BOM) and hand-solder; no design change needed. The enclosure assumptions (P1 at the left edge facing out, height/opening) are unchanged.
* Alternative if hand-soldering the module is not acceptable: order Standard PCBA (module and all other parts then assembled by JLC; setup/stencil about 17 USD / 7 USD more, >= 4 days).
