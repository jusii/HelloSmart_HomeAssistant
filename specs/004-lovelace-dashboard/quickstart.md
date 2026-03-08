# Quickstart: Lovelace Vehicle Dashboard

**Feature**: 004-lovelace-dashboard  
**Date**: 2026-03-08

## What This Feature Delivers

A ready-to-use Lovelace dashboard for the Hello Smart integration displaying 7 card groups: vehicle hero image, battery/range, charging status with controls, lock/security with visual diagram, tyre status in spatial layout, windows with close-all action, and service/maintenance data.

## Deliverables

| Artifact | Path | Description |
|----------|------|-------------|
| Enhanced Dashboard | `dashboards/smart-vehicle.yaml` | Full dashboard using mushroom + card-mod HACS cards |
| Basic Dashboard | `dashboards/smart-vehicle-basic.yaml` | Fallback using only built-in HA cards |
| Vehicle Images | `dashboards/assets/` | 3 PNG images extracted from APK |
| Installation Guide | `dashboards/README.md` | Setup and customization instructions |

## Prerequisites

1. **Hello Smart integration** installed and configured with at least one vehicle
2. **Home Assistant** 2025.x or later
3. **HACS** installed (for enhanced version only)
4. **HACS cards** installed (for enhanced version):
   - `mushroom` (piitaya/lovelace-mushroom)
   - `card-mod` (thomasloven/lovelace-card-mod)

## Installation Steps

### Enhanced Version (Recommended)

1. Install HACS cards: `mushroom` and `card-mod` via HACS Frontend
2. Copy `dashboards/assets/*.png` to `/config/www/hello_smart/`
3. Open `dashboards/smart-vehicle.yaml`
4. Find-and-replace `234118` with your vehicle's last 6 VIN digits
5. Add dashboard via HA Settings → Dashboards → Add Dashboard → YAML mode, paste contents
6. Refresh browser

### Basic Version (No HACS)

1. Copy `dashboards/assets/*.png` to `/config/www/hello_smart/`
2. Open `dashboards/smart-vehicle-basic.yaml`
3. Find-and-replace `234118` with your vehicle's last 6 VIN digits
4. Add dashboard via HA Settings → Dashboards → Add Dashboard → YAML mode, paste contents

## Files Changed (vs. current main)

### New Files

| File | Purpose |
|------|---------|
| `dashboards/smart-vehicle.yaml` | Enhanced Lovelace dashboard YAML |
| `dashboards/smart-vehicle-basic.yaml` | Basic Lovelace dashboard YAML (built-in cards only) |
| `dashboards/assets/image_big_car_3x.png` | Vehicle side-view image (981×484) |
| `dashboards/assets/vehicle_hud_1.png` | Vehicle top-down HUD image (1112×668) |
| `dashboards/assets/gsv_dev_ic_vehicle_main.png` | Compact vehicle icon (522×255) |
| `dashboards/README.md` | Installation and customization guide |

### Modified Files

None. This feature does not modify any integration source code (`custom_components/hello_smart/`).

## Entity Count Reference

The dashboard references entities from the existing integration:

| Domain | Count Used | Card Groups |
|--------|-----------|-------------|
| sensor | ~40 | Battery, Charging, Tyres, Service, Hero |
| binary_sensor | ~25 | Doors, Windows, Tyres, Charging, Hero |
| lock | 1 | Lock/Security, Hero |
| switch | 1 | Charging |
| button | 1 | Windows |
| number | 1 | Charging |
| time | 2 | Charging |
| **Total** | **~71** | |

## Verification

After installation:

1. Open the Smart Vehicle dashboard
2. Verify hero card shows vehicle image and status badges
3. Verify battery gauge shows current SOC percentage
4. Verify door lock toggle works (lock/unlock)
5. Verify charging controls respond (SOC slider, start/stop)
6. Verify tyre pressures display in spatial layout
7. Verify "Close All Windows" button is visible
8. Verify service data (odometer, firmware) is populated
