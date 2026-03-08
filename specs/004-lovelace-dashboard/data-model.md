# Data Model: Lovelace Vehicle Dashboard

**Feature**: 004-lovelace-dashboard  
**Date**: 2026-03-08

## Overview

This feature does not introduce new code entities, dataclasses, or database models. The "data model" is the dashboard structure itself — a Lovelace YAML view definition and its supporting assets.

## Dashboard Structure

### View: Smart Vehicle Dashboard

```
smart-vehicle-dashboard (single view)
├── Hero Card (vehicle image + status badges)
├── Battery & Range Card (gauge + range values)
├── Charging Status Card (metrics + controls)
├── Lock & Security Card (diagram + toggles)
├── Tyre Status Card (spatial pressure/temp layout)
├── Windows Card (status + close-all button)
└── Service Card (odometer, fluids, firmware)
```

### Entity Relationships

```
hello_smart integration (coordinator)
    │
    ├── sensor.* (55 entities) ──────────┐
    ├── binary_sensor.* (55 entities) ───┤
    ├── lock.* (2 entities) ─────────────┤── Referenced by
    ├── switch.* (5 entities) ───────────┤   Dashboard YAML
    ├── button.* (4 entities) ───────────┤
    ├── number.* (1 entity) ────────────┤
    ├── time.* (3 entities) ────────────┤
    ├── select.* (4 entities) ──────────┤
    └── device_tracker.* (1 entity) ────┘
                                         │
                                         ▼
                               Dashboard YAML File
                               (read-only consumer)
```

## Card Definitions

### 1. Hero Card

| Field | Source Entity | Type | Notes |
|-------|-------------|------|-------|
| Vehicle Image | Static asset | `/local/hello_smart/image_big_car_3x.png` | From APK extraction |
| Lock Status | `lock.smart_{vin6}_smart_door_lock` | lock | locked/unlocked badge |
| Charging Status | `sensor.smart_{vin6}_charging_status` | sensor | State text badge |
| Power Mode | `sensor.smart_{vin6}_power_mode` | sensor | off/accessory/on/cranking |
| Online Status | `binary_sensor.smart_{vin6}_telematics_connected` | binary_sensor | on=online |

### 2. Battery & Range Card

| Field | Source Entity | Display |
|-------|-------------|---------|
| Battery Level | `sensor.smart_{vin6}_battery_level` | Gauge (0-100%) |
| Range Remaining | `sensor.smart_{vin6}_range_remaining` | Value + unit (km) |
| Range at Full | `sensor.smart_{vin6}_range_at_full_charge` | Value + unit (km) |

### 3. Charging Status Card

| Field | Source Entity | Display |
|-------|-------------|---------|
| Charging State | `sensor.smart_{vin6}_charging_status` | Status text |
| Charger Connected | `binary_sensor.smart_{vin6}_charger_connected` | Icon indicator |
| AC Charge Lid | `binary_sensor.smart_{vin6}_charge_lid_ac` | Icon indicator |
| DC Charge Lid | `binary_sensor.smart_{vin6}_charge_lid_dc` | Icon indicator |
| Voltage | `sensor.smart_{vin6}_charge_voltage` | Value (V) |
| AC Current | `sensor.smart_{vin6}_charge_current` | Value (A) |
| DC Current | `sensor.smart_{vin6}_dc_charge_current` | Value (A) |
| Power | `sensor.smart_{vin6}_charging_power` | Value (kW) |
| Time to Full | `sensor.smart_{vin6}_time_to_full` | Value (min) |
| Target SOC | `number.smart_{vin6}_smart_target_soc` | Slider (50-100%) |
| Schedule Status | `sensor.smart_{vin6}_charging_schedule_status` | Status text |
| Schedule Start | `time.smart_{vin6}_smart_charging_start` | Time picker |
| Schedule End | `time.smart_{vin6}_smart_charging_end` | Time picker |
| Schedule Target SOC | `sensor.smart_{vin6}_charging_target_soc` | Value (%) |
| Charging Switch | `switch.smart_{vin6}_smart_charging` | Toggle |

### 4. Lock & Security Card

| Field | Source Entity | Display |
|-------|-------------|---------|
| Door Lock Toggle | `lock.smart_{vin6}_smart_door_lock` | Lock toggle |
| Driver Door | `binary_sensor.smart_{vin6}_driver_door` | Open/closed |
| Passenger Door | `binary_sensor.smart_{vin6}_passenger_door` | Open/closed |
| Rear Left Door | `binary_sensor.smart_{vin6}_rear_left_door` | Open/closed |
| Rear Right Door | `binary_sensor.smart_{vin6}_rear_right_door` | Open/closed |
| Trunk | `binary_sensor.smart_{vin6}_trunk` | Open/closed |
| Engine Hood | `binary_sensor.smart_{vin6}_engine_hood` | Open/closed |
| Door Lock Driver | `binary_sensor.smart_{vin6}_door_lock_driver` | Locked/unlocked |
| Door Lock Passenger | `binary_sensor.smart_{vin6}_door_lock_passenger` | Locked/unlocked |
| Door Lock Rear L | `binary_sensor.smart_{vin6}_door_lock_rear_left` | Locked/unlocked |
| Door Lock Rear R | `binary_sensor.smart_{vin6}_door_lock_rear_right` | Locked/unlocked |
| Trunk Lock | `binary_sensor.smart_{vin6}_trunk_locked` | Locked/unlocked |

### 5. Tyre Status Card

| Field | Source Entity | Display |
|-------|-------------|---------|
| FL Pressure | `sensor.smart_{vin6}_tyre_pressure_fl` | Value (kPa) |
| FR Pressure | `sensor.smart_{vin6}_tyre_pressure_fr` | Value (kPa) |
| RL Pressure | `sensor.smart_{vin6}_tyre_pressure_rl` | Value (kPa) |
| RR Pressure | `sensor.smart_{vin6}_tyre_pressure_rr` | Value (kPa) |
| FL Temperature | `sensor.smart_{vin6}_tyre_temp_fl` | Value (°C) |
| FR Temperature | `sensor.smart_{vin6}_tyre_temp_fr` | Value (°C) |
| RL Temperature | `sensor.smart_{vin6}_tyre_temp_rl` | Value (°C) |
| RR Temperature | `sensor.smart_{vin6}_tyre_temp_rr` | Value (°C) |
| FL Warning | `binary_sensor.smart_{vin6}_tyre_warning_fl` | Warning icon |
| FR Warning | `binary_sensor.smart_{vin6}_tyre_warning_fr` | Warning icon |
| RL Warning | `binary_sensor.smart_{vin6}_tyre_warning_rl` | Warning icon |
| RR Warning | `binary_sensor.smart_{vin6}_tyre_warning_rr` | Warning icon |

### 6. Windows Card

| Field | Source Entity | Display |
|-------|-------------|---------|
| Driver Window | `binary_sensor.smart_{vin6}_driver_window` | Open/closed |
| Passenger Window | `binary_sensor.smart_{vin6}_passenger_window` | Open/closed |
| Rear Left Window | `binary_sensor.smart_{vin6}_rear_left_window` | Open/closed |
| Rear Right Window | `binary_sensor.smart_{vin6}_rear_right_window` | Open/closed |
| Sunroof | `binary_sensor.smart_{vin6}_sunroof_open` | Open/closed |
| Driver Position | `sensor.smart_{vin6}_window_position_driver` | Value (%) |
| Passenger Position | `sensor.smart_{vin6}_window_position_passenger` | Value (%) |
| Rear L Position | `sensor.smart_{vin6}_window_position_driver_rear` | Value (%) |
| Rear R Position | `sensor.smart_{vin6}_window_position_passenger_rear` | Value (%) |
| Sunroof Position | `sensor.smart_{vin6}_sunroof_position` | Value (%) |
| Close All | `button.smart_{vin6}_smart_close_windows` | Button |

### 7. Service Card

| Field | Source Entity | Display |
|-------|-------------|---------|
| Odometer | `sensor.smart_{vin6}_odometer` | Value (km) |
| Days to Service | `sensor.smart_{vin6}_days_to_service` | Value (days) |
| Distance to Service | `sensor.smart_{vin6}_distance_to_service` | Value (km) |
| Engine Hours to Service | `sensor.smart_{vin6}_engine_hours_to_service` | Value (h) |
| Service Warning | `sensor.smart_{vin6}_service_warning` | Status text |
| Washer Fluid | `sensor.smart_{vin6}_washer_fluid_level` | Level indicator |
| Brake Fluid | `binary_sensor.smart_{vin6}_brake_fluid_ok` | OK/warning |
| Coolant Level | `sensor.smart_{vin6}_engine_coolant_level` | Level indicator |
| Current Firmware | `sensor.smart_{vin6}_current_firmware_version` | Version string |
| Target Firmware | `sensor.smart_{vin6}_target_firmware_version` | Version string |
| Update Available | `binary_sensor.smart_{vin6}_update_available` | Badge |
| Diagnostic Status | `sensor.smart_{vin6}_diagnostic_status` | Status text |
| Diagnostic Code | `sensor.smart_{vin6}_diagnostic_code` | DTC code |

## File Assets

| Asset | Source | Destination | Purpose |
|-------|--------|-------------|---------|
| `image_big_car_3x.png` | Intl APK | `/config/www/hello_smart/` | Hero card vehicle image |
| `vehicle_hud_1.png` | EU APK | `/config/www/hello_smart/` | Top-down diagram for door/tyre overlays |
| `gsv_dev_ic_vehicle_main.png` | Intl APK | `/config/www/hello_smart/` | Compact vehicle icon |
| `smart-vehicle.yaml` | New file | `dashboards/` | Enhanced dashboard (mushroom + card-mod) |
| `smart-vehicle-basic.yaml` | New file | `dashboards/` | Fallback dashboard (built-in cards only) |
