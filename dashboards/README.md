# Smart Vehicle Dashboard for Home Assistant

A ready-to-use Lovelace dashboard for the Hello Smart integration, displaying 7 card groups for comprehensive vehicle monitoring and control.

## Dashboard Versions

| Version | File | Requirements |
|---------|------|--------------|
| **Enhanced** | `smart-vehicle.yaml` | [mushroom](https://github.com/piitaya/lovelace-mushroom) + [card-mod](https://github.com/thomasloven/lovelace-card-mod) via HACS |
| **Basic** | `smart-vehicle-basic.yaml` | Built-in HA cards only — no HACS needed |

## Prerequisites

- **Home Assistant** 2025.x or later
- **Hello Smart integration** installed and configured with at least one vehicle
- **HACS** (for enhanced version only)

### HACS Card Installation (Enhanced Version)

1. Open HACS → Frontend
2. Search and install **Mushroom** (`piitaya/lovelace-mushroom`)
3. Search and install **card-mod** (`thomasloven/lovelace-card-mod`)
4. Refresh your browser (Ctrl+Shift+R / Cmd+Shift+R)

## Image Setup

Copy the vehicle image assets to your Home Assistant `www` folder:

```bash
# Create the target directory
mkdir -p /config/www/hello_smart/

# Copy images from this repository
cp dashboards/assets/image_big_car_3x.png /config/www/hello_smart/
cp dashboards/assets/vehicle_hud_1.png /config/www/hello_smart/
cp dashboards/assets/gsv_dev_ic_vehicle_main.png /config/www/hello_smart/
```

The images will be accessible at `/local/hello_smart/` in your dashboard YAML.

> **Note**: After copying files to `www/`, restart Home Assistant or clear your browser cache for the images to appear.

## Enhanced Dashboard Setup

1. Open `dashboards/smart-vehicle.yaml`
2. Find and replace all instances of `234118` with your vehicle's last 6 VIN digits
3. In Home Assistant: **Settings → Dashboards → Add Dashboard**
4. Choose **"Take control"** or YAML mode
5. Paste the contents of the YAML file
6. Save and refresh

## Basic Dashboard Setup

1. Open `dashboards/smart-vehicle-basic.yaml`
2. Find and replace all instances of `234118` with your vehicle's last 6 VIN digits
3. In Home Assistant: **Settings → Dashboards → Add Dashboard**
4. Choose **"Take control"** or YAML mode
5. Paste the contents of the YAML file
6. Save and refresh

## VIN Customization

Entity IDs use the pattern `sensor.smart_{vin6}_battery_level` where `{vin6}` is the last 6 characters of your vehicle's VIN.

**Example**: If your VIN is `HESCA2C42RS987654`, replace `234118` with `987654` throughout the YAML file.

```bash
# Quick find-and-replace using sed (macOS)
sed -i '' 's/234118/YOUR_VIN6/g' dashboards/smart-vehicle.yaml

# Quick find-and-replace using sed (Linux)
sed -i 's/234118/YOUR_VIN6/g' dashboards/smart-vehicle.yaml
```

## Card Groups

Both dashboard versions include these 7 card groups:

| # | Card Group | Description |
|---|-----------|-------------|
| 1 | **Hero** | Vehicle image with lock, charging, power mode, and connectivity badges |
| 2 | **Battery & Range** | Battery level gauge, range remaining, range at full charge |
| 3 | **Charging** | Charging status, voltage/current/power metrics, SOC slider, schedule, start/stop |
| 4 | **Lock & Security** | Lock toggle, door open/closed status with top-down diagram, individual lock states |
| 5 | **Tyre Status** | Tyre pressure and temperature in spatial wheel layout (FL/FR/RL/RR) with warnings |
| 6 | **Windows** | Window open/closed status with position %, sunroof, close-all button |
| 7 | **Service** | Odometer, service countdown, fluid levels, firmware versions, diagnostics |

## Troubleshooting

### Images not showing
- Verify files exist in `/config/www/hello_smart/`
- Restart Home Assistant after adding files to `www/`
- Clear browser cache (Ctrl+Shift+R)

### "Custom element doesn't exist" error
- Ensure mushroom and card-mod are installed via HACS (enhanced version only)
- Refresh the browser after HACS installation
- Try the basic version (`smart-vehicle-basic.yaml`) which needs no HACS cards

### Entities show "unavailable"
- Verify the Hello Smart integration is configured and running
- Check that the VIN last-6 digits are correct (find-replace `234118`)
- Ensure the vehicle has reported data at least once

### Dark theme contrast issues
- The enhanced dashboard uses card-mod CSS optimized for dark themes
- If using a custom theme, card backgrounds (#1E1E1E) and text colors (#FFFFFF) may need adjustment

## Assets

| File | Resolution | Description |
|------|-----------|-------------|
| `image_big_car_3x.png` | 981×484 | Vehicle side view (hero card) |
| `vehicle_hud_1.png` | 1112×668 | Top-down HUD diagram (door/tyre overlays) |
| `gsv_dev_ic_vehicle_main.png` | 522×255 | Compact vehicle icon |
