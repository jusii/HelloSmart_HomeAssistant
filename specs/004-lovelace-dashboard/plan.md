# Implementation Plan: Lovelace Vehicle Dashboard

**Branch**: `004-lovelace-dashboard` | **Date**: 2026-03-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-lovelace-dashboard/spec.md`

## Summary

Create a Lovelace dashboard for the Hello Smart HA integration with 7 card groups: vehicle hero image (from APK-extracted assets), battery/range gauge, charging status with interactive controls, lock/security with top-down vehicle diagram overlay, tyre status in spatial wheel-position layout, windows status with close-all button, and service/maintenance info. Two versions are delivered — an enhanced version using `mushroom` + `card-mod` HACS cards, and a basic fallback using only built-in HA cards. No integration source code is modified (FR-076).

## Technical Context

**Language/Version**: YAML (Home Assistant Lovelace dashboard format)  
**Primary Dependencies**: Home Assistant 2025.x+, HACS (optional), mushroom cards (optional), card-mod (optional)  
**Storage**: N/A — static YAML files and PNG image assets  
**Testing**: Manual visual testing in HA browser UI  
**Target Platform**: Home Assistant (any OS — HassOS, Docker, venv)  
**Project Type**: Dashboard configuration (YAML + static assets)  
**Performance Goals**: Dashboard loads and renders all 7 cards in <2s (SC-001)  
**Constraints**: No integration code changes (FR-076); must work on both mobile (375px) and desktop (1920px) viewports (FR-072); dark theme compatible (FR-071)  
**Scale/Scope**: Single vehicle per dashboard; ~71 entities referenced across 7 card groups

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. HA Compatibility** | ✅ PASS | Dashboard YAML is standard Lovelace format. No Python code changes. HACS cards are optional with a built-in fallback. |
| **II. Security-First** | ✅ PASS | No credentials, API calls, or code execution. Vehicle images are static local assets — no external URL fetches at runtime. No SSRF vectors. |
| **III. Minimal Footprint** | ✅ PASS | Zero changes to `custom_components/`. Deliverables are pure YAML and PNG files in a separate `dashboards/` directory. |
| **IV. Organized Testing** | ✅ PASS | Dashboard YAML is validated visually in the HA UI. No test files needed — this is configuration, not code. |
| **V. Simplicity** | ✅ PASS | Uses standard HA card types (gauge, entities, picture-elements, mushroom). No custom JS, no abstractions. Two YAML files (enhanced + basic). |

**Gate result**: PASS — proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/004-lovelace-dashboard/
├── plan.md              # This file
├── research.md          # Phase 0 output — APK analysis, HACS card research, entity mapping
├── data-model.md        # Phase 1 output — dashboard structure, card definitions, entity references
├── quickstart.md        # Phase 1 output — installation steps and verification
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
dashboards/
├── smart-vehicle.yaml              # Enhanced dashboard (mushroom + card-mod)
├── smart-vehicle-basic.yaml        # Basic dashboard (built-in HA cards only)
├── README.md                       # Installation and customization guide
└── assets/
    ├── image_big_car_3x.png        # Vehicle side view (981×484, from intl APK)
    ├── vehicle_hud_1.png           # Top-down HUD diagram (1112×668, from EU APK)
    └── gsv_dev_ic_vehicle_main.png # Compact vehicle icon (522×255, from intl APK)
```

**Structure Decision**: New `dashboards/` directory at repository root, separate from `custom_components/`. This keeps dashboard configuration cleanly isolated from integration code and prevents any risk of shipping dashboard assets to HA's custom_components directory. Users copy only the assets they need.

---

## Phase 0: Research

**Output**: [research.md](research.md)

### Key Research Findings

| # | Topic | Decision |
|---|-------|----------|
| 1 | APK vehicle images | 6 usable images found across both APKs. Best: `image_big_car_3x.png` (981×484), `vehicle_hud_1.png` (1112×668), `gsv_dev_ic_vehicle_main.png` (522×255). No color/model-specific variants exist. |
| 2 | Color mapping | No paint code or exterior color data in API or APK. Images are generic white/silver. Fallback strategy: use as-is — works well on both light/dark themes. |
| 3 | HACS card selection | `mushroom` (5.8k stars) for card foundation, `card-mod` (3.1k stars) for Smart brand CSS. Both MIT-licensed, actively maintained. |
| 4 | Vehicle diagram approach | Built-in `picture-elements` card with `vehicle_hud_1.png` as background. Overlay `state-icon`/`state-label` elements at percentage coordinates for doors, windows, and tyres. |
| 5 | Entity ID pattern | `{domain}.smart_{vin_last6}_{key}`. Example: `sensor.smart_234118_battery_level`. 71 entities referenced across all 7 card groups. |
| 6 | Dashboard delivery | Static YAML file in `dashboards/` directory. User copies assets to `/config/www/hello_smart/` and imports YAML via HA UI. |
| 7 | Brand colors | Primary `#0078D4` blue, success `#4CAF50` green, error `#F44336` red, warning `#FF9800` orange. Applied via `card-mod` CSS. |
| 8 | Fallback strategy | Basic version uses `gauge`, `entities`, `picture-elements`, `button`, `horizontal-stack`, `vertical-stack` — all built-in. |

---

## Phase 1: Design & Contracts

### Outputs

- [data-model.md](data-model.md) — Dashboard structure, 7 card definitions with all entity references, file asset inventory
- [quickstart.md](quickstart.md) — Installation steps for both enhanced and basic versions, verification checklist

### Design Decisions

1. **Two dashboard versions** — Enhanced (mushroom + card-mod) and Basic (built-in cards only). Different files, not conditional logic within one file.
2. **Static YAML files** — Not generated by integration code. Users copy and customize. Keeps integration code clean per FR-076.
3. **`picture-elements` for diagrams** — Built-in HA card type, no external dependency. Vehicle HUD image as background with positioned overlays for doors/tyres.
4. **No contracts directory** — This feature has no external interfaces, APIs, or contracts. The dashboard is a static YAML consumer of existing entities.
5. **VIN parameterization** — Entity IDs use placeholder `234118` (example VIN last 6). A find-and-replace instruction + comment header makes customization trivial.
6. **Dashboard card order** — Hero → Battery/Range → Charging → Lock/Security → Tyres → Windows → Service. Matches spec priority (P1 at top) with Hero bumped up for visual impact.
7. **Image asset extraction** — 3 PNGs extracted from APKs and committed to `dashboards/assets/`. Users copy to their HA's `www/` directory.

---

## Post-Design Constitution Re-Check

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. HA Compatibility** | ✅ PASS | Standard Lovelace YAML format. HACS cards are optional. Compatible with HA 2025.x+. |
| **II. Security-First** | ✅ PASS | All assets are local static files. No runtime URL fetches, no credentials, no external dependencies. Images extracted from official Smart APK (same data the user already has). |
| **III. Minimal Footprint** | ✅ PASS | Zero changes to `custom_components/`. 3 PNG files (~500 KB total), 2 YAML files, 1 README. All in separate `dashboards/` directory. |
| **IV. Organized Testing** | ✅ PASS | Visual verification only. No test code needed for static YAML configuration. |
| **V. Simplicity** | ✅ PASS | Two flat YAML files with no templating engine, no JS, no abstractions. Copy-paste installation. |

**Post-design gate result**: PASS — ready for task generation via `/speckit.tasks`.
