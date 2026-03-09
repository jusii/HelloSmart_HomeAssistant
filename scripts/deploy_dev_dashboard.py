#!/usr/bin/env python3
"""Generate dev dashboard YAML with actual entity IDs for the HA container."""
import os

# Entity key name mappings: dashboard template → actual
key_map = {
    "smart_door_lock": "driver_door_lock",
    "charging_schedule_status": "scheduled_charging",
    "window_position_driver_rear": "rear_left_window_position",
    "window_position_passenger_rear": "rear_right_window_position",
    "window_position_driver": "driver_window_position",
    "window_position_passenger": "passenger_window_position",
    "current_firmware_version": "firmware_version",
    "target_firmware_version": "available_firmware_version",
    "engine_coolant_level": "coolant_level",
    "tyre_pressure_fl": "tyre_pressure_front_left",
    "tyre_pressure_fr": "tyre_pressure_front_right",
    "tyre_pressure_rl": "tyre_pressure_rear_left",
    "tyre_pressure_rr": "tyre_pressure_rear_right",
    "tyre_temp_fl": "tyre_temperature_front_left",
    "tyre_temp_fr": "tyre_temperature_front_right",
    "tyre_temp_rl": "tyre_temperature_rear_left",
    "tyre_temp_rr": "tyre_temperature_rear_right",
    "tyre_warning_fl": "tyre_warning_front_left",
    "tyre_warning_fr": "tyre_warning_front_right",
    "tyre_warning_rl": "tyre_warning_rear_left",
    "tyre_warning_rr": "tyre_warning_rear_right",
    "door_lock_driver": "driver_door_lock",
    "door_lock_passenger": "passenger_door_lock",
    "door_lock_rear_left": "rear_left_door_lock",
    "door_lock_rear_right": "rear_right_door_lock",
    "charging_target_soc": "charge_target",
    "smart_target_soc": "charge_target",
    "smart_charging_start": "charging_start_time",
    "smart_charging_end": "charging_end_time",
    "smart_close_windows": "close_windows",
    "smart_charging": "charging",
    "dc_charge_current": "dc_charging_current",
    "charge_current": "charging_current",
    "charge_voltage": "charging_voltage",
    "charger_connected": "charger",
    "charge_lid_ac": "ac_charge_lid",
    "charge_lid_dc": "dc_charge_lid",
    "range_remaining": "estimated_range",
    "time_to_full": "time_to_full_charge",
    "telematics_connected": "vehicle_online",
    "trunk_locked": "boot_lock",
    "trunk": "boot",
    "engine_hood": "bonnet",
    "sunroof_open": "sunroof",
    "days_to_service": "service_due_in",
    "distance_to_service": "service_due_distance",
    "washer_fluid_low": "washer_fluid",
    "brake_fluid_ok": "brake_fluid",
    "update_available": "firmware_update_available",
    "diagnostic_code": "diagnostic_trouble_code",
}

prefix_old = "smart_234118_"
prefix_new = "cm590_hc11_performance_4wd_rhd_apac_"

for src, dst in [
    ("dashboards/smart-vehicle.yaml", "docker/ha-config/dashboards/smart-vehicle.yaml"),
    ("dashboards/smart-vehicle-basic.yaml", "docker/ha-config/dashboards/smart-vehicle-basic.yaml"),
]:
    with open(src) as f:
        content = f.read()

    # Replace specific key names first (before prefix change)
    for old_key, new_key in key_map.items():
        content = content.replace(prefix_old + old_key, prefix_old + new_key)

    # Replace the prefix
    content = content.replace(prefix_old, prefix_new)

    # Fix lock entity references: no lock.* entity exists, use binary_sensor
    content = content.replace(
        "lock." + prefix_new + "driver_door_lock",
        "binary_sensor." + prefix_new + "driver_door_lock",
    )

    # Fix mushroom-lock-card → mushroom-entity-card (lock card needs lock entity)
    content = content.replace("type: custom:mushroom-lock-card", "type: custom:mushroom-entity-card")

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w") as f:
        f.write(content)

    print(f"Created {dst}")

    # Verify no leftover placeholders
    count = content.count("234118")
    print(f"  Remaining '234118' refs: {count}")
    if count > 0:
        for i, line in enumerate(content.split("\n"), 1):
            if "234118" in line:
                print(f"    Line {i}: {line.strip()}")

print("\nDone!")
