# Tasks: Lovelace Vehicle Dashboard

**Input**: Design documents from `/specs/004-lovelace-dashboard/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Not requested — visual verification only per plan.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. Each user story adds cards to both the enhanced and basic dashboard YAML files.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure, extract APK image assets, initialize dashboard YAML scaffolds

- [x] T001 Create `dashboards/` and `dashboards/assets/` directory structure at repository root
- [x] T002 Extract `image_big_car_3x.png` (981×484) from `Hello_Smart_APK/hello_smart_intl.xapk` → `dashboards/assets/image_big_car_3x.png`
- [x] T003 Extract `vehicle_hud_1.png` (1112×668) from `Hello_Smart_APK/hello_smart_europe.apk` → `dashboards/assets/vehicle_hud_1.png`
- [x] T004 Extract `gsv_dev_ic_vehicle_main.png` (522×255) from `Hello_Smart_APK/hello_smart_intl.xapk` → `dashboards/assets/gsv_dev_ic_vehicle_main.png`
- [x] T005 [P] Create enhanced dashboard scaffold in `dashboards/smart-vehicle.yaml` with view title "Smart Vehicle", VIN placeholder comment header (find-replace `234118`), and empty card list
- [x] T006 [P] Create basic dashboard scaffold in `dashboards/smart-vehicle-basic.yaml` with view title "Smart Vehicle (Basic)", VIN placeholder comment header, and empty card list

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No blocking prerequisites — each user story adds independent card groups to the existing YAML scaffolds. Phase 1 completion unblocks all user stories.

**⚠️ NOTE**: This feature has no foundational phase. All user stories depend only on Phase 1 (Setup) completion. Proceed directly to user story phases.

---

## Phase 3: User Story 1 — Battery, Range & Charging (Priority: P1) 🎯 MVP

**Goal**: Display battery level gauge, estimated range, range at full charge, and full charging status with interactive controls (SOC slider, schedule time pickers, start/stop toggle)

**Independent Test**: Open dashboard → Battery & Range card shows gauge + range values. Charging Status card shows metrics + controls. SOC slider, time pickers, and charging switch are interactive.

### Implementation

- [x] T007 [US1] Add Battery & Range card to `dashboards/smart-vehicle.yaml` — mushroom-template-card with circular gauge for `sensor.smart_234118_battery_level`, entity rows for `sensor.smart_234118_range_remaining` and `sensor.smart_234118_range_at_full_charge`, card-mod CSS for Smart brand colors (#0078D4 primary)
- [x] T008 [US1] Add Charging Status card to `dashboards/smart-vehicle.yaml` — vertical-stack with: mushroom-entity-card for `sensor.smart_234118_charging_status`, mushroom-chips-card for `binary_sensor.smart_234118_charger_connected` + `binary_sensor.smart_234118_charge_lid_ac` + `binary_sensor.smart_234118_charge_lid_dc`, entity rows for `sensor.smart_234118_charge_voltage` + `sensor.smart_234118_charge_current` + `sensor.smart_234118_dc_charge_current` + `sensor.smart_234118_charging_power` + `sensor.smart_234118_time_to_full`, mushroom-entity-card for `number.smart_234118_smart_target_soc` (slider), entity rows for `sensor.smart_234118_charging_schedule_status` + `sensor.smart_234118_charging_target_soc`, entity rows for `time.smart_234118_smart_charging_start` + `time.smart_234118_smart_charging_end`, mushroom-entity-card for `switch.smart_234118_smart_charging` (toggle)
- [x] T009 [US1] Add Battery & Range card to `dashboards/smart-vehicle-basic.yaml` — gauge card for battery_level (0–100%, severity colors), entities card for range_remaining and range_at_full_charge
- [x] T010 [US1] Add Charging Status card to `dashboards/smart-vehicle-basic.yaml` — entities card with all charging sensors, number slider for target_soc, time entities, and charging switch toggle

**Checkpoint**: Battery & Range + Charging cards visible and functional in both dashboard versions

---

## Phase 4: User Story 2 — Vehicle Overview with Image (Priority: P2)

**Goal**: Display hero card at top of dashboard with vehicle image, model name, and status badges (lock, charging, power mode, online/offline)

**Independent Test**: Open dashboard → Hero card shows vehicle image (`image_big_car_3x.png`), vehicle name, lock badge, charging badge, power mode, online/offline indicator.

### Implementation

- [x] T011 [US2] Add Hero card to `dashboards/smart-vehicle.yaml` — mushroom-template-card with `image_big_car_3x.png` as background image (`/local/hello_smart/image_big_car_3x.png`), vehicle name as primary text, mushroom-chips-card row with: lock state chip from `lock.smart_234118_smart_door_lock`, charging state chip from `sensor.smart_234118_charging_status`, power mode chip from `sensor.smart_234118_power_mode`, connectivity chip from `binary_sensor.smart_234118_telematics_connected`, card-mod CSS for image sizing plus dark overlay gradient
- [x] T012 [US2] Add Hero card to `dashboards/smart-vehicle-basic.yaml` — picture-entity card with `image_big_car_3x.png` as image, entities card below with lock state + charging status + power mode + telematics_connected rows

**Checkpoint**: Hero card appears at top of both dashboards with vehicle image and status badges

---

## Phase 5: User Story 3 — Lock & Security Status (Priority: P3)

**Goal**: Display lock/unlock toggle, all door open/closed and lock statuses, engine hood, and visual top-down car diagram with door overlays

**Independent Test**: Open dashboard → Lock & Security card shows door lock toggle, individual door/trunk/hood status. Picture-elements diagram highlights open doors in red.

### Implementation

- [x] T013 [US3] Add Lock & Security card to `dashboards/smart-vehicle.yaml` — vertical-stack with: mushroom-lock-card for `lock.smart_234118_smart_door_lock`, picture-elements card using `vehicle_hud_1.png` (`/local/hello_smart/vehicle_hud_1.png`) as background with conditional state-icon overlays at percentage positions for `binary_sensor.smart_234118_driver_door` (left 18%, top 40%), `binary_sensor.smart_234118_passenger_door` (left 82%, top 40%), `binary_sensor.smart_234118_rear_left_door` (left 18%, top 60%), `binary_sensor.smart_234118_rear_right_door` (left 82%, top 60%), `binary_sensor.smart_234118_trunk` (left 50%, top 92%), `binary_sensor.smart_234118_engine_hood` (left 50%, top 8%) — green icon when closed, red when open. Add entities card section for individual lock statuses: `binary_sensor.smart_234118_door_lock_driver`, `binary_sensor.smart_234118_door_lock_passenger`, `binary_sensor.smart_234118_door_lock_rear_left`, `binary_sensor.smart_234118_door_lock_rear_right`, `binary_sensor.smart_234118_trunk_locked`
- [x] T014 [US3] Add Lock & Security card to `dashboards/smart-vehicle-basic.yaml` — entities card with lock toggle for `lock.smart_234118_smart_door_lock`, all 5 door binary_sensors, trunk, engine_hood, and all 5 door lock binary_sensors

**Checkpoint**: Lock & Security card visible in both dashboards, picture-elements diagram shows door positions, lock toggle functional

---

## Phase 6: User Story 4 — Tyre Status (Priority: P4)

**Goal**: Display tyre pressure and temperature for all 4 tyres in a spatial wheel-position layout (FL/FR top, RL/RR bottom) with warning highlighting

**Independent Test**: Open dashboard → Tyre Status card shows 4 pressure/temperature pairs in car wheel layout. Tyre warnings highlighted in red.

### Implementation

- [x] T015 [US4] Add Tyre Status card to `dashboards/smart-vehicle.yaml` — grid or horizontal/vertical-stack layout matching car wheel positions: top row (horizontal-stack) with FL (`sensor.smart_234118_tyre_pressure_fl` + `sensor.smart_234118_tyre_temp_fl` + `binary_sensor.smart_234118_tyre_warning_fl`) and FR (`sensor.smart_234118_tyre_pressure_fr` + `sensor.smart_234118_tyre_temp_fr` + `binary_sensor.smart_234118_tyre_warning_fr`), bottom row with RL (`sensor.smart_234118_tyre_pressure_rl` + `sensor.smart_234118_tyre_temp_rl` + `binary_sensor.smart_234118_tyre_warning_rl`) and RR (`sensor.smart_234118_tyre_pressure_rr` + `sensor.smart_234118_tyre_temp_rr` + `binary_sensor.smart_234118_tyre_warning_rr`). Use mushroom-template-card per tyre with conditional card-mod CSS: red text/border when tyre_warning is on, green/neutral when off.
- [x] T016 [US4] Add Tyre Status card to `dashboards/smart-vehicle-basic.yaml` — horizontal-stack of vertical-stacks: top row (FL, FR), bottom row (RL, RR). Each position uses entities card with pressure, temperature, and warning sensors.

**Checkpoint**: Tyre status displayed in spatial wheel layout in both dashboards

---

## Phase 7: User Story 5 — Windows Status (Priority: P5)

**Goal**: Display open/closed status and position percentage of all windows and sunroof, with "Close All Windows" button

**Independent Test**: Open dashboard → Windows card shows all 4 windows + sunroof status, position %, and "Close All Windows" button is functional.

### Implementation

- [x] T017 [US5] Add Windows card to `dashboards/smart-vehicle.yaml` — vertical-stack with: mushroom-entity-card rows for `binary_sensor.smart_234118_driver_window` (with `sensor.smart_234118_window_position_driver` as secondary), `binary_sensor.smart_234118_passenger_window` (with `sensor.smart_234118_window_position_passenger`), `binary_sensor.smart_234118_rear_left_window` (with `sensor.smart_234118_window_position_driver_rear`), `binary_sensor.smart_234118_rear_right_window` (with `sensor.smart_234118_window_position_passenger_rear`), `binary_sensor.smart_234118_sunroof_open` (with `sensor.smart_234118_sunroof_position`), mushroom-entity-card for `button.smart_234118_smart_close_windows` styled as action button
- [x] T018 [US5] Add Windows card to `dashboards/smart-vehicle-basic.yaml` — entities card with all 5 window binary_sensors, all 5 position sensors, and button entity for close_windows

**Checkpoint**: Windows card visible and Close All Windows button functional in both dashboards

---

## Phase 8: User Story 6 — Service Information (Priority: P6)

**Goal**: Display odometer, service countdown, fluid levels, firmware versions with update indicator, and diagnostic status

**Independent Test**: Open dashboard → Service card shows odometer, days/distance/hours to service, fluid levels, firmware versions, diagnostic info.

### Implementation

- [x] T019 [US6] Add Service card to `dashboards/smart-vehicle.yaml` — vertical-stack with sections: mushroom-entity-card for `sensor.smart_234118_odometer`, mushroom-chips-card with `sensor.smart_234118_days_to_service` + `sensor.smart_234118_distance_to_service` + `sensor.smart_234118_engine_hours_to_service`, mushroom-entity-card for `sensor.smart_234118_service_warning`, entities section for fluids: `sensor.smart_234118_washer_fluid_level` + `binary_sensor.smart_234118_brake_fluid_ok` + `sensor.smart_234118_engine_coolant_level`, entities section for firmware: `sensor.smart_234118_current_firmware_version` + `sensor.smart_234118_target_firmware_version` + `binary_sensor.smart_234118_update_available`, entities section for diagnostics: `sensor.smart_234118_diagnostic_status` + `sensor.smart_234118_diagnostic_code`
- [x] T020 [US6] Add Service card to `dashboards/smart-vehicle-basic.yaml` — entities card with all service sensors (odometer, days/distance/hours to service, service_warning, washer_fluid_level, brake_fluid_ok, engine_coolant_level, current/target firmware versions, update_available, diagnostic_status, diagnostic_code)

**Checkpoint**: Service card visible in both dashboards with all maintenance data

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, card ordering, brand styling, responsive layout, and final validation

- [x] T021 [P] Create installation and customization guide in `dashboards/README.md` — sections: Prerequisites (HA version, HACS, mushroom, card-mod), Image Setup (copy assets to `/config/www/hello_smart/`), Enhanced Dashboard Setup (import YAML via HA UI), Basic Dashboard Setup (import basic YAML), VIN Customization (find-replace `234118`), HACS Card Installation Instructions, Troubleshooting
- [x] T022 Finalize card ordering and section headers in `dashboards/smart-vehicle.yaml` — ensure card order is Hero → Battery/Range → Charging → Lock/Security → Tyres → Windows → Service per plan.md, add markdown section header cards between groups for visual separation, verify all entity IDs use `234118` placeholder consistently
- [x] T023 Finalize card ordering and section headers in `dashboards/smart-vehicle-basic.yaml` — same order and header structure as enhanced version, verify all entity IDs use `234118` placeholder
- [x] T024 Apply Smart brand CSS theming via card-mod in `dashboards/smart-vehicle.yaml` — add card-mod styles for dark-theme compatibility: card backgrounds (#1E1E1E), primary accent (#0078D4), success indicators (#4CAF50 for locked/closed/normal), warning indicators (#FF9800 for low fluid), error indicators (#F44336 for open doors/tyre warnings), text colors (#FFFFFF primary, #B3B3B3 secondary), responsive layout adjustments for mobile (375px) and desktop (1920px)
- [x] T025 Run quickstart.md validation — verify both dashboards load in HA UI, all 7 card groups visible on single view (SC-002), interactive controls functional (SC-003), mobile and desktop viewports render correctly (SC-004), dark theme has no contrast issues (SC-005)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **User Stories (Phases 3–8)**: All depend on Phase 1 completion only (no Phase 2 blockers)
  - User stories can proceed in priority order (P1 → P2 → P3 → P4 → P5 → P6)
  - Or in parallel — each story adds independent cards to the YAML files
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1) Battery/Charging**: Can start after Phase 1 — no dependencies on other stories
- **US2 (P2) Hero/Image**: Can start after Phase 1 — no dependencies on other stories
- **US3 (P3) Lock/Security**: Can start after Phase 1 — no dependencies on other stories
- **US4 (P4) Tyres**: Can start after Phase 1 — no dependencies on other stories
- **US5 (P5) Windows**: Can start after Phase 1 — no dependencies on other stories
- **US6 (P6) Service**: Can start after Phase 1 — no dependencies on other stories

### Within Each User Story

- Enhanced YAML card (mushroom) and Basic YAML card can be written in parallel
- Both files must be updated for the story to be complete

### Parallel Opportunities

- T002, T003, T004 can run in parallel (independent APK extractions)
- T005, T006 can run in parallel (independent file creation)
- Enhanced and Basic card tasks within each story can run in parallel
- All user stories can start in parallel after Phase 1

---

## Parallel Example: Phase 1 Setup

```bash
# Parallel batch 1: Extract all APK images simultaneously
Task T002: "Extract image_big_car_3x.png from intl XAPK"
Task T003: "Extract vehicle_hud_1.png from EU APK"
Task T004: "Extract gsv_dev_ic_vehicle_main.png from intl XAPK"

# Parallel batch 2: Create both YAML scaffolds
Task T005: "Create enhanced dashboard scaffold"
Task T006: "Create basic dashboard scaffold"
```

## Parallel Example: User Story 1

```bash
# Parallel: Write enhanced and basic cards simultaneously
Task T007: "Add Battery & Range card to smart-vehicle.yaml"
Task T009: "Add Battery & Range card to smart-vehicle-basic.yaml"

# Then parallel:
Task T008: "Add Charging Status card to smart-vehicle.yaml"
Task T010: "Add Charging Status card to smart-vehicle-basic.yaml"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (extract images, create scaffolds)
2. Complete Phase 3: User Story 1 — Battery, Range & Charging
3. **STOP and VALIDATE**: Test battery gauge, range display, and charging controls in HA
4. Dashboard is usable with just battery/charging info

### Incremental Delivery

1. Complete Setup → directory + assets ready
2. Add US1 (Battery/Charging) → core EV monitoring dashboard (MVP!)
3. Add US2 (Hero/Image) → visual identity and overview
4. Add US3 (Lock/Security) → security monitoring and remote control
5. Add US4 (Tyres) → safety monitoring
6. Add US5 (Windows) → window monitoring and remote close
7. Add US6 (Service) → maintenance planning
8. Polish → brand styling, documentation, responsive layout
9. Each story adds a complete card group without breaking previous cards
