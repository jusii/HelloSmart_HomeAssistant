# Research: Lovelace Vehicle Dashboard

**Feature**: 004-lovelace-dashboard  
**Date**: 2026-03-08  
**Spec**: [spec.md](spec.md)

## R1: Vehicle Image Assets in APK

**Task**: Investigate Hello Smart APK resources for extractable vehicle renders.

### Findings

Both APKs contain static vehicle images — no dynamic color/model mapping exists.

#### European APK (`hello_smart_europe.apk`)

| Asset | Size | Resolution | Description |
|-------|------|------------|-------------|
| `res/drawable/image_car_3x.png` | 97 KB | 495×372 | Generic Smart #1 side view, RGBA with transparency |
| `res/drawable/seu_activate_vehicle_main_bg.png` | 3.9 MB | 1500×3248 | Full activation flow background (too large for dashboard) |
| `res/drawable-xxxhdpi-v4/vehicle_hud_1.png` | 152 KB | 1112×668 | Vehicle HUD top-down view #1 (shows door/window outlines) |
| `res/drawable-xxxhdpi-v4/vehicle_hud_2.png` | 207 KB | 1112×668 | Vehicle HUD top-down view #2 (variant) |
| `res/drawable/pic_vehicle_body.xml` | 736 B | Vector | Android VectorDrawable — car body outline (rounded rect) |
| `res/drawable/pic_vehicle_roof.xml` | 1.4 KB | Vector | Android VectorDrawable — car roof with window cutouts |

#### International APK (`hello_smart_intl.xapk`)

| Asset | Size | Resolution | Description |
|-------|------|------------|-------------|
| `res/drawable/image_big_car_3x.png` | 324 KB | 981×484 | Larger Smart #1 side view, RGBA with transparency |
| `res/drawable/image_car_3x.png` | 97 KB | 495×372 | Same as EU APK |
| `res/mipmap-xxhdpi-v4/gsv_dev_ic_vehicle_main.png` | 111 KB | 522×255 | Smart vehicle main render (3/4 front view) |
| `res/mipmap-xxhdpi-v4/gsv_dev_ic_vehicle_45.png` | 61 KB | 375×185 | 45° angle vehicle render |

### Decision

- **Use `image_big_car_3x.png` (981×484)** from the international APK as the primary hero card image. Best resolution and aspect ratio for a dashboard card.
- **Use `vehicle_hud_1.png` (1112×668)** as the top-down view for door/window/tyre status overlays.
- **Use `gsv_dev_ic_vehicle_main.png` (522×255)** as a compact alternative for smaller card contexts.
- **No color mapping exists** — images are generic (white/silver Smart #1). No paint code → image variant mapping in either APK. The API does not return exterior color data either.
- **VectorDrawable XMLs** (`pic_vehicle_body.xml`, `pic_vehicle_roof.xml`) are Android-specific and cannot be used directly in HTML. They contain simple rounded-rectangle shapes that could be recreated as SVGs if needed for a tyre/door overlay, but the HUD PNGs are more useful.

### Alternatives Considered

- Creating an SVG from scratch: Rejected — the HUD PNGs already provide top-down views suitable for overlays.
- CSS tinting the generic white image: Not needed — a single white/silver rendering works well on both light and dark themes.
- Downloading images from Smart website at runtime: Rejected — introduces SSRF risk and external dependency.

---

## R2: HACS Custom Card Options

**Task**: Research best HACS card options for vehicle dashboards in HA.

### Findings

| Card | HACS Stars | Purpose | License |
|------|------------|---------|---------|
| **mushroom** (piitaya/lovelace-mushroom) | 5.8k | Modern card collection — chips, entities, template cards | MIT |
| **vehicle-info-card** (ngocjohn/vehicle-info-card) | ~300 | Mercedes-style vehicle card with door/window diagrams | MIT |
| **ultra-vehicle-card** (WJDDesigns/ultra-vehicle-card) | ~200 | Generic vehicle card with image + status overlays | MIT |
| **bar-card** (custom-cards/bar-card) | 1.5k | Horizontal/vertical progress bars | MIT |
| **button-card** (custom-cards/button-card) | 3.8k | Highly customizable button cards with templates | MIT |
| **mini-graph-card** (kalkih/mini-graph-card) | 2.9k | Compact sensor graph cards | MIT |
| **stack-in-card** (custom-cards/stack-in-card) | 700 | Nest stacks within cards seamlessly | MIT |
| **card-mod** (thomasloven/lovelace-card-mod) | 3.1k | CSS styling for any card | MIT |
| **layout-card** (thomasloven/lovelace-layout-card) | 1.5k | Custom grid layouts | MIT |

### Decision

**Primary approach**: Use `mushroom` cards as the foundation for consistency and wide adoption. Supplement with `card-mod` for Smart brand styling.

- **Hero card**: `mushroom-template-card` with custom CSS for vehicle image background + status chips.
- **Battery gauge**: `mushroom-template-card` with circular gauge or `bar-card` for horizontal battery bar.
- **Door/tyre diagrams**: Custom `picture-elements` card using `vehicle_hud_1.png` as background with conditional overlays — no external card dependency for this.
- **Toggle controls**: `mushroom-entity-card` for lock, switch, button entities.
- **Status sensors**: `mushroom-entity-card` rows grouped in `vertical-stack`.

**Fallback approach**: Standard HA cards only — `gauge`, `entities`, `picture-elements`, `button`, `horizontal-stack`, `vertical-stack`. Functional but less polished.

### Alternatives Considered

- `vehicle-info-card` or `ultra-vehicle-card`: These are model-specific cards designed for specific brands. They include hardcoded vehicle diagrams and entity patterns that don't match our integration. Too rigid.
- `button-card`: More powerful than mushroom but steeper configuration complexity. Overkill for this use case.

---

## R3: Entity ID Mapping

**Task**: Map all spec functional requirements to concrete entity IDs.

### Findings

Entity ID pattern: `{domain}.smart_{vin_last6}_{key}` where `vin_last6` are the last 6 characters of the VIN.

**Example vehicle**: VIN `HESCA2C42RS234118` → `vin_last6 = 234118`

#### Battery & Range Card (FR-010 to FR-012)

| FR | Entity ID | Domain |
|----|-----------|--------|
| FR-010 | `sensor.smart_234118_battery_level` | sensor |
| FR-011 | `sensor.smart_234118_range_remaining` | sensor |
| FR-012 | `sensor.smart_234118_range_at_full_charge` | sensor |

#### Charging Status Card (FR-020 to FR-026)

| FR | Entity ID | Domain |
|----|-----------|--------|
| FR-020 | `sensor.smart_234118_charging_status` | sensor |
| FR-021 | `binary_sensor.smart_234118_charger_connected` | binary_sensor |
| FR-021 | `binary_sensor.smart_234118_charge_lid_ac` | binary_sensor |
| FR-021 | `binary_sensor.smart_234118_charge_lid_dc` | binary_sensor |
| FR-022 | `sensor.smart_234118_charge_voltage` | sensor |
| FR-022 | `sensor.smart_234118_charge_current` | sensor |
| FR-022 | `sensor.smart_234118_dc_charge_current` | sensor |
| FR-022 | `sensor.smart_234118_charging_power` | sensor |
| FR-022 | `sensor.smart_234118_time_to_full` | sensor |
| FR-023 | `number.smart_234118_smart_target_soc` | number |
| FR-024 | `sensor.smart_234118_charging_schedule_status` | sensor |
| FR-024 | `sensor.smart_234118_charging_schedule_start` | sensor |
| FR-024 | `sensor.smart_234118_charging_schedule_end` | sensor |
| FR-024 | `sensor.smart_234118_charging_target_soc` | sensor |
| FR-025 | `time.smart_234118_smart_charging_start` | time |
| FR-025 | `time.smart_234118_smart_charging_end` | time |
| FR-026 | `switch.smart_234118_smart_charging` | switch |

#### Lock & Security Card (FR-030 to FR-034)

| FR | Entity ID | Domain |
|----|-----------|--------|
| FR-030 | `lock.smart_234118_smart_door_lock` | lock |
| FR-031 | `binary_sensor.smart_234118_driver_door` | binary_sensor |
| FR-031 | `binary_sensor.smart_234118_passenger_door` | binary_sensor |
| FR-031 | `binary_sensor.smart_234118_rear_left_door` | binary_sensor |
| FR-031 | `binary_sensor.smart_234118_rear_right_door` | binary_sensor |
| FR-031 | `binary_sensor.smart_234118_trunk` | binary_sensor |
| FR-032 | `binary_sensor.smart_234118_door_lock_driver` | binary_sensor |
| FR-032 | `binary_sensor.smart_234118_door_lock_passenger` | binary_sensor |
| FR-032 | `binary_sensor.smart_234118_door_lock_rear_left` | binary_sensor |
| FR-032 | `binary_sensor.smart_234118_door_lock_rear_right` | binary_sensor |
| FR-032 | `binary_sensor.smart_234118_trunk_locked` | binary_sensor |
| FR-033 | `binary_sensor.smart_234118_engine_hood` | binary_sensor |

#### Windows Status Card (FR-040 to FR-043)

| FR | Entity ID | Domain |
|----|-----------|--------|
| FR-040 | `binary_sensor.smart_234118_driver_window` | binary_sensor |
| FR-040 | `binary_sensor.smart_234118_passenger_window` | binary_sensor |
| FR-040 | `binary_sensor.smart_234118_rear_left_window` | binary_sensor |
| FR-040 | `binary_sensor.smart_234118_rear_right_window` | binary_sensor |
| FR-040 | `binary_sensor.smart_234118_sunroof_open` | binary_sensor |
| FR-041 | `sensor.smart_234118_window_position_driver` | sensor |
| FR-041 | `sensor.smart_234118_window_position_passenger` | sensor |
| FR-041 | `sensor.smart_234118_window_position_driver_rear` | sensor |
| FR-041 | `sensor.smart_234118_window_position_passenger_rear` | sensor |
| FR-041 | `sensor.smart_234118_sunroof_position` | sensor |
| FR-042 | `button.smart_234118_smart_close_windows` | button |

#### Tyre Status Card (FR-050 to FR-052)

| FR | Entity ID | Domain |
|----|-----------|--------|
| FR-050 | `sensor.smart_234118_tyre_pressure_fl` | sensor |
| FR-050 | `sensor.smart_234118_tyre_pressure_fr` | sensor |
| FR-050 | `sensor.smart_234118_tyre_pressure_rl` | sensor |
| FR-050 | `sensor.smart_234118_tyre_pressure_rr` | sensor |
| FR-050 | `sensor.smart_234118_tyre_temp_fl` | sensor |
| FR-050 | `sensor.smart_234118_tyre_temp_fr` | sensor |
| FR-050 | `sensor.smart_234118_tyre_temp_rl` | sensor |
| FR-050 | `sensor.smart_234118_tyre_temp_rr` | sensor |
| FR-051 | `binary_sensor.smart_234118_tyre_warning_fl` | binary_sensor |
| FR-051 | `binary_sensor.smart_234118_tyre_warning_fr` | binary_sensor |
| FR-051 | `binary_sensor.smart_234118_tyre_warning_rl` | binary_sensor |
| FR-051 | `binary_sensor.smart_234118_tyre_warning_rr` | binary_sensor |

#### Service Card (FR-060 to FR-065)

| FR | Entity ID | Domain |
|----|-----------|--------|
| FR-060 | `sensor.smart_234118_odometer` | sensor |
| FR-061 | `sensor.smart_234118_days_to_service` | sensor |
| FR-061 | `sensor.smart_234118_distance_to_service` | sensor |
| FR-061 | `sensor.smart_234118_engine_hours_to_service` | sensor |
| FR-062 | `sensor.smart_234118_washer_fluid_level` | sensor |
| FR-062 | `binary_sensor.smart_234118_brake_fluid_ok` | binary_sensor |
| FR-062 | `sensor.smart_234118_engine_coolant_level` | sensor |
| FR-063 | `sensor.smart_234118_current_firmware_version` | sensor |
| FR-063 | `sensor.smart_234118_target_firmware_version` | sensor |
| FR-063 | `binary_sensor.smart_234118_update_available` | binary_sensor |
| FR-064 | `sensor.smart_234118_diagnostic_status` | sensor |
| FR-064 | `sensor.smart_234118_diagnostic_code` | sensor |
| FR-065 | `sensor.smart_234118_service_warning` | sensor |

#### Hero Card (FR-001)

| FR | Entity ID | Domain |
|----|-----------|--------|
| FR-001 | `lock.smart_234118_smart_door_lock` | lock (state = locked/unlocked) |
| FR-001 | `sensor.smart_234118_charging_status` | sensor (charging state) |
| FR-001 | `sensor.smart_234118_power_mode` | sensor (off/accessory/on/cranking) |
| FR-001 | `binary_sensor.smart_234118_telematics_connected` | binary_sensor (online/offline) |
| FR-001 | `device_tracker.smart_234118_location` | device_tracker (GPS) |

---

## R4: Lovelace Dashboard Architecture

**Task**: Determine the optimal dashboard structure and delivery mechanism.

### Decision

- **Format**: A single Lovelace dashboard YAML file (not a view within an existing dashboard) stored at `config/dashboards/smart-vehicle.yaml` with a `lovelace_dashboards:` entry in `configuration.yaml`.
- **Delivery**: The YAML file is included in the git repository under a `dashboards/` directory at project root. Users copy it to their HA config and add a dashboard reference.
- **Layout**: Single view with a `grid` layout (or `vertical-stack` for mobile). Cards are ordered per spec priority: Hero → Battery/Range → Charging → Lock/Security → Tyres → Windows → Service.
- **Entity ID parameterization**: Entity IDs use `smart_234118` (example VIN). A comment at the top of the YAML documents the find/replace pattern for other VINs.

### Alternatives Considered

- **Blueprint-based distribution**: HA blueprints are for automations, not dashboards. Not applicable.
- **Auto-generated dashboard via integration code**: Would require modifying `custom_components/` which violates FR-076. Also causes conflicts with user customizations.
- **Multiple views (tabs)**: Rejected — SC-002 requires all 7 card groups on a single view.

---

## R5: Smart Brand Color Palette

**Task**: Determine Smart brand colors for dark-theme dashboard styling.

### Decision

| Token | Color | Usage |
|-------|-------|-------|
| Primary | `#0078D4` | Headers, active indicators, primary buttons |
| Primary Dark | `#005A9E` | Hover states, card borders |
| Surface | `#1E1E1E` | Card backgrounds (dark theme) |
| Surface Light | `#2D2D2D` | Elevated card surfaces |
| Text Primary | `#FFFFFF` | Primary text on dark surfaces |
| Text Secondary | `#B3B3B3` | Secondary/muted text |
| Success | `#4CAF50` | Locked, normal pressure, closed windows |
| Warning | `#FF9800` | Low fluid, service due soon |
| Error | `#F44336` | Open doors, tyre warnings, unlocked |
| Charging Blue | `#00BCD4` | Active charging indicator |

Applied via `card-mod` CSS or HA theme variables. Colors work on both dark and light themes (sufficient contrast ratios).

---

## R6: Picture-Elements Overlay Strategy

**Task**: Determine how to overlay door/window/tyre status on the vehicle HUD image.

### Decision

Use HA's built-in `picture-elements` card with `vehicle_hud_1.png` as the background image. Position `state-icon` or `state-label` elements at percentage-based coordinates matching the door, window, and tyre positions on the image.

#### Coordinate Map (percentage-based, for `vehicle_hud_1.png` 1112×668)

| Position | Left % | Top % | Purpose |
|----------|--------|-------|---------|
| FL Tyre | 22% | 18% | Front-left tyre pressure |
| FR Tyre | 78% | 18% | Front-right tyre pressure |
| RL Tyre | 22% | 82% | Rear-left tyre pressure |
| RR Tyre | 78% | 82% | Rear-right tyre pressure |
| Driver Door | 18% | 40% | Driver door open/closed |
| Passenger Door | 82% | 40% | Passenger door open/closed |
| Rear-L Door | 18% | 60% | Rear-left door open/closed |
| Rear-R Door | 82% | 60% | Rear-right door open/closed |
| Trunk | 50% | 92% | Trunk open/closed |
| Hood | 50% | 8% | Engine hood open/closed |

These coordinates will need fine-tuning once the actual HUD image is rendered in HA. The YAML includes comments indicating adjustable positions.

### Alternatives Considered

- Separate tyre card and door card (no image overlay): This is the fallback approach. Less visual but no image dependency.
- Custom HTML/JS card: Would require a HACS card component. Overkill — `picture-elements` is a built-in HA card that handles this natively.
