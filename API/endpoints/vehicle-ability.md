# Vehicle Ability

Vehicle configuration, remote control capabilities, and color-matched image URLs from the Vehicle Configuration (VC) service.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {vc_base_url}/vehicle/v1/ability/{modelCode}/{vin}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| `modelCode` | Path | Yes | Vehicle model code (e.g., `HC1H2D3B6213-01_IL`) |
| `vin` | Path | Yes | Vehicle VIN |

### Base URLs

| Region | URL |
|--------|-----|
| INTL | `https://sg-app-api.smart.com/vc` |
| EU | `https://vehicle.vbs.srv.smart.com` |

> **Note**: This endpoint uses a **different host and signing scheme** from the standard vehicle data API. See [VC Signing](#vc-signing-intl-only) below.

### Headers

For **INTL**, this endpoint requires [Alibaba Cloud API Gateway HMAC-SHA256 signing](../common-patterns.md#vc-signing) — not the standard HMAC-SHA1 used by vehicle data endpoints.

| Header | Description |
|--------|-------------|
| `x-ca-key` | API Gateway app key (`204587190`) |
| `x-ca-nonce` | UUID v4 |
| `x-ca-timestamp` | Epoch milliseconds |
| `x-ca-signature-method` | `HmacSHA256` |
| `x-ca-signature-headers` | Comma-separated sorted list of `x-ca-*` header names |
| `x-ca-signature` | Base64 HMAC-SHA256 of the canonical string-to-sign |
| `CA_VERSION` | `1` |
| `x-smart-id` | User ID from authentication |
| `authorization` | API access token |
| `Xs-Auth-Token` | `idToken` from INTL login step 1 (Gigya) |
| `accept` | `application/json;charset=UTF-8` |
| `content-type` | `application/json;charset=UTF-8` |

For **EU**, standard `x-smart-id` + `authorization` headers are sufficient.

---

## VC Signing (INTL Only)

The VC service uses **Alibaba Cloud API Gateway** HMAC-SHA256 signing, which is entirely different from the vehicle data API's custom HMAC-SHA1.

### String-to-Sign

```
METHOD\n
Accept\n
Content-MD5\n
Content-Type\n
Date\n
x-ca-key:{value}\n
x-ca-nonce:{value}\n
x-ca-signature-method:HmacSHA256\n
x-ca-timestamp:{value}\n
{path}
```

- **Content-MD5**: Empty string for GET requests
- **Date**: HTTP date format (`Mon, 08 Mar 2026 09:00:00 GMT`)
- Headers are sorted alphabetically by key
- Path includes the full URL path (e.g., `/vc/vehicle/v1/ability/HC1.../HESCA2...`)
- Query parameters are appended if present: `{path}?{sorted_query}`

### Signature Computation

```python
signature = base64(hmac_sha256(app_secret, string_to_sign))
```

### Keys

| Key | Value | Source |
|-----|-------|--------|
| App Key | `204587190` | `libnative-lib.so` → `getAppKeyReleaseFromJni` |
| App Secret | *(32-char alphanumeric)* | `libnative-lib.so` → `getAppSecretReleaseFromJni` |

> Keys are extracted from the native JNI library bundled in the INTL APK. The `adrp + add` instructions at each function's entry point reference string literals in `.rodata`.

---

## Response

```json
{
  "code": "200",
  "message": "Operation is Successful",
  "result": {
    "id": 179,
    "pno1810": 2,
    "bluetooth": false,
    "vehicleName": "HC11",
    "vehicleCode": "HC11",
    "vehicleYearCode": "HC11",
    "modelCode": "HC1H2D3B6213-01_IL",
    "modelName": "CM590_HC11_Performance_4WD_RHD_APAC",
    "abilityCount": 11,
    "saleName": "BRABUS",
    "nationCode": "AU",
    "abilities": [
      {
        "id": 1,
        "abilityCode": "remote_control_window",
        "name": "车窗",
        "controlWays": ["BLUETOOTH", "REMOTE"],
        "limitSettings": [],
        "extras": ""
      },
      {
        "id": 2,
        "abilityCode": "remote_control_doorlock",
        "name": "车锁",
        "controlWays": ["BLUETOOTH", "REMOTE"],
        "limitSettings": [],
        "extras": ""
      }
    ],
    "vscData": {
      "imagesPath": "https://sg-app.smart.com/static/vehicle/1740729823393/HC1H2D3B6213001257--1.png",
      "topImagesPath": "https://sg-app.smart.com/static/vehicle/1740729823393/HC1H2D3B6213001257--2.png",
      "interiorImagesPath": "",
      "batteryImagesPath": "https://sg-app.smart.com/static/vehicle/1740729823393/HC1H2D3B6213001257--4.png",
      "pno18": "...",
      "colorCode": "...",
      "modelCodeVdp": "...",
      "modelCodeMss": "...",
      "contrastColorCode": "...",
      "vehicleName": "HC11",
      "modelName": "...",
      "seriesCodeMss": "...",
      "colorNameMss": "Meta Black Metallic",
      "interiorColorNameMss": "...",
      "hubCode": "...",
      "vehicleNickname": "",
      "licensePlateNumber": "...",
      "nationCode": "AU"
    }
  }
}
```

> **Important**: This endpoint returns `"code": "200"` (string) and uses `result` as the data key — unlike standard vehicle endpoints which return `"code": 1000` (integer) with a `data` key.

### Response Fields (Top Level)

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Vehicle config record ID |
| `pno1810` | int | Platform number |
| `bluetooth` | bool | Bluetooth capability flag |
| `vehicleName` | string | Internal vehicle code |
| `vehicleCode` | string | Vehicle code |
| `vehicleYearCode` | string | Model year code |
| `modelCode` | string | Full model code |
| `modelName` | string | Technical model name (e.g., `CM590_HC11_Performance_4WD_RHD_APAC`) |
| `abilityCount` | int | Number of remote control capabilities |
| `saleName` | string | Sales/trim name (e.g., `BRABUS`) |
| `nationCode` | string | Country code |
| `abilities` | array | List of remote control capabilities |
| `vscData` | object | Vehicle visual configuration data |

### Ability Entry

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Ability ID |
| `abilityCode` | string | Machine-readable capability code |
| `name` | string | Display name (Chinese) |
| `controlWays` | array | Control methods: `BLUETOOTH`, `REMOTE` |
| `limitSettings` | array | Restriction rules (typically empty) |
| `extras` | string | Additional configuration (typically empty) |

### Known Ability Codes

| Code | Description |
|------|-------------|
| `remote_control_window` | Window open/close |
| `remote_control_doorlock` | Door lock/unlock |
| `remote_control_honk_flash` | Find my car (honk + flash) |
| `remote_control_hrunklock` | Trunk open |
| `remote_contro_AC` | Air conditioning |
| `remote_contro_seat_heating` | Seat heating |
| `remote_contro_steeringwheel_heating` | Steering wheel heating |
| `remote_contro_seat_ventilating` | Seat ventilation |
| `remote_control_parkcomfort` | Park comfort mode |
| `remote_control_chargeplan` | Charging schedule |
| `condition_PM2.5` | PM2.5 air quality sensor |

> Note: Some codes have typos in the API (e.g., `remote_contro_AC` missing `l`). These are preserved as-is.

### vscData Fields

| Field | Type | Description |
|-------|------|-------------|
| `imagesPath` | string | Side-view vehicle image URL (color-matched) |
| `topImagesPath` | string | Top-down vehicle image URL (color-matched) |
| `interiorImagesPath` | string | Interior image URL (may be empty) |
| `batteryImagesPath` | string | Battery/charging image URL |
| `colorCode` | string | Exterior color code |
| `colorNameMss` | string | Exterior color name (e.g., `Meta Black Metallic`) |
| `contrastColorCode` | string | Contrast/accent color code |
| `interiorColorNameMss` | string | Interior color name |
| `modelCodeVdp` | string | VDP model code |
| `modelCodeMss` | string | MSS model code |
| `seriesCodeMss` | string | Series code |
| `hubCode` | string | Hub/dealership code |
| `vehicleName` | string | Internal vehicle name |
| `modelName` | string | Model name |
| `vehicleNickname` | string | User-assigned nickname |
| `licensePlateNumber` | string | Registration plate number |
| `nationCode` | string | Country code |
| `pno18` | string | PNO18 configuration code |

### Image CDN

All image URLs are served from `https://sg-app.smart.com/static/vehicle/` (INTL). Images are PNGs with transparent backgrounds, sized for mobile display. The naming convention is `{modelConfigCode}--{index}.png` where index is:

| Index | Content |
|-------|---------|
| `1` | Side view |
| `2` | Top-down view |
| `4` | Battery/charging view |

---

## Data Model

Returns: [`VehicleAbility`](../models.md#vehicleability)

| Model Field | Source |
|-------------|--------|
| `images_path` | `vscData.imagesPath` |
| `top_images_path` | `vscData.topImagesPath` |
| `interior_images_path` | `vscData.interiorImagesPath` |
| `battery_images_path` | `vscData.batteryImagesPath` |
| `color_code` | `vscData.colorCode` |
| `color_name_mss` | `vscData.colorNameMss` |
| `contrast_color_code` | `vscData.contrastColorCode` |
| `contrast_color_name` | `vscData.contrastColorNameMSS` |
| `interior_color_name` | `vscData.interiorColorNameMss` |
| `hub_code` | `vscData.hubCode` |
| `hub_name` | `vscData.hubNameMSS` |
| `model_code_mss` | `vscData.modelCodeMss` |
| `model_code_vdp` | `vscData.modelCodeVdp` |
| `model_name` | `vscData.modelName` |
| `vehicle_name` | `vscData.vehicleName` |
| `vehicle_nickname` | `vscData.vehicleNickname` |
| `side_logo_light_name` | `vscData.sideLogoLightNameMSS` |
| `license_plate_number` | `vscData.licensePlateNumber` |

---

## Related Entities

| Entity | Platform | Description |
|--------|----------|-------------|
| `vehicle_image_path` | sensor | Local path to downloaded side-view image |

---

## Integration Behavior

The coordinator downloads vehicle images on first load and caches them locally:

| Image | Filename | Source |
|-------|----------|--------|
| Side view | `{vin}_side.png` | `vscData.imagesPath` |
| Top-down view | `{vin}_top.png` | `vscData.topImagesPath` |
| Interior | `{vin}_interior.png` | `vscData.interiorImagesPath` |

Images are stored in `{ha_config}/www/hello_smart/` and served at `/local/hello_smart/{filename}`. Downloads are skipped if the file already exists.

---

## Discovery Notes

- **Source**: Decompiled from `GSVApi.java` in INTL APK (`@GET("vehicle/v1/ability/{modelCode}/{vin}")`)
- **Retrofit service**: `GSVRequestService` with `VehicleNetworkConfig` base URL
- **Signing**: `GlobalHeaderInterceptor` adds Alibaba Cloud API Gateway HMAC-SHA256 via `ApiRequestMaker` → `SignUtil`
- **Native keys**: App key and secret loaded via JNI from `libnative-lib.so` (`getAppKeyReleaseFromJni`, `getAppSecretReleaseFromJni`)
