#!/usr/bin/env python3
"""Debug script to check entity ID suffix → translation_key mapping."""
import json

with open("/config/.storage/core.entity_registry") as f:
    reg = json.load(f)

prefix = "cm590_hc11_performance_4wd_rhd_apac_"
target_keys = {
    "driver_door", "passenger_door", "rear_left_door", "rear_right_door",
    "trunk", "engine_hood",
    "driver_window", "passenger_window", "rear_left_window", "rear_right_window",
    "sunroof_open",
    "door_lock_driver", "door_lock_passenger", "door_lock_rear_left",
    "door_lock_rear_right", "trunk_locked",
    "vehicle_image_path",
}

for e in reg["data"]["entities"]:
    if e.get("platform") != "hello_smart":
        continue
    tk = e.get("translation_key") or ""
    if tk not in target_keys:
        continue
    eid = e["entity_id"]
    oid = eid.split(".", 1)[1]
    suffix = oid[len(prefix):] if oid.startswith(prefix) else oid
    print(f"suffix={suffix:35s} tkey={tk}")
