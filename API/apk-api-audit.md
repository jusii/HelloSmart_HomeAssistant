# Smart APK API Audit — Complete Endpoint Inventory

> **Generated from jadx decompilation of both APKs.**
> INTL: `hello_smart_intl.xapk` (13,372 Java files) · EU: `hello_smart_europe.apk` (20,461 Java files)

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Base URLs & Authentication](#base-urls--authentication)
- [Platform Differences Summary](#platform-differences-summary)
- [Shared APIs (Both APKs)](#shared-apis-both-apks)
  - [IoV WebServiceInterface (~195 endpoints)](#iov-webserviceinterface)
  - [GidServiceInterface (24 endpoints)](#gidserviceinterface)
  - [Digital Key HttpInterface (67 endpoints)](#digital-key-httpinterface)
  - [Car Sharing v2 Signed (26 endpoints)](#car-sharing-v2-signed)
  - [CerServiceInterface — PKI (4 endpoints)](#cerserviceinterface--pki)
  - [SmartLog Upload (1 endpoint)](#smartlog-upload)
  - [Weather / Air Quality (3 endpoints)](#weather--air-quality)
  - [GSVApi — Global Vehicle Service (shared subset)](#gsvapi--global-vehicle-service)
- [EU-Only APIs](#eu-only-apis)
  - [EcoPlatform Auth (LoginAppApi, UserInfoApi)](#ecoplatform-auth)
  - [Vehicle Activation (VehicleActivationApi)](#vehicle-activation)
  - [Vehicle Data (VehicleDataApi)](#vehicle-data)
  - [DCS — Digital Charging Solutions (10 endpoints)](#dcs--digital-charging-solutions)
  - [OTA App Info (AWS-based)](#ota-app-info)
  - [Push Notifications](#push-notifications)
  - [Lokalise SDK](#lokalise-sdk)
  - [OneTrust Privacy SDK](#onetrust-privacy-sdk)
- [INTL-Only APIs](#intl-only-apis)
  - [AccountIAMApi (14 endpoints)](#accountiamapi)
  - [AccountUCApi (4 endpoints)](#accountucapi)
  - [AccountVerifyApi (1 endpoint)](#accountverifyapi)
  - [AgreementApi (2 endpoints)](#agreementapi)
  - [VehicleVCApi (3 endpoints)](#vehiclevcapi)
- [Endpoint Totals](#endpoint-totals)
- [Already Implemented](#already-implemented)
- [Candidates for Integration](#candidates-for-integration)

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        Smart Mobile App                         │
├──────────────┬──────────────┬────────────────┬──────────────────┤
│  EU-Only     │  Shared ECARX IoV Platform    │  INTL-Only       │
│              │  (api.xchanger.cn →            │  (Smart Global   │
│  EcoPlatform │   *.ecloudeu.com)             │   Platform)      │
│  DCS Charging│                               │                  │
│  AWS OTA     │  Digital Key · Car Sharing    │  IAM · UC        │
│  Push Svc    │  Weather · Log Upload · PKI   │  Agreements      │
│              │                               │  Vehicle Settings│
├──────────────┴──────────────┴────────────────┴──────────────────┤
│  GSV — Global Smart Vehicle Service (VC)                        │
│  sg-app-api.smart.com  (shared, minor path differences)         │
└─────────────────────────────────────────────────────────────────┘
```

Both APKs share the **ECARX IoV platform** as their backbone — the same `WebServiceInterface` (~195 endpoints), `GidServiceInterface` (auth, 24 endpoints), `HttpInterface` (digital key, 67 endpoints), and `CarShare` (26 endpoints). The EU APK layers additional EU-specific services on top (EcoPlatform, DCS charging, AWS OTA). The INTL APK instead layers the Smart Global Platform (IAM, UC, VC modules).

---

## Base URLs & Authentication

### Shared (ECARX IoV)

| Service | `urlname` Header | Production URL |
|---------|------------------|----------------|
| User API | `user-api` | `https://user-api.ecloudeu.com` |
| Device API | `device-api` | `https://device-api.ecloudeu.com` |
| VLog API | `vlog-api` | `https://vlog-api.ecloudeu.com` |
| OTA API | `ota-api` | `https://ota-api.ecloudeu.com` |
| EAS API | `eas-api` | `https://eas-api.ecloudeu.com` |
| SDK API | `api-sdk` | `https://api-sdk.ecloudeu.com` |
| CSP API | `csp-api` | `https://csp-api.ecloudeu.com` |
| Default (no header) | — | `https://api.xchanger.cn` |

Routing: A custom OkHttp interceptor reads the `urlname` header and replaces the base URL at request time.

Regional variants:
- China: `*.xchanger.cn`
- APAC: `*.ecloudkr.com`
- NA: `*.ecloudus.com`
- Zeekr: `*.zeekrline.com`
- Lotus: `*.lotuscars.link`

### EU-Only

| Service | Base URL |
|---------|----------|
| EcoPlatform Login | `https://api.app-auth.srv.smart.com/v1/` |
| EcoPlatform Vehicle | `https://vcrm.srv.smart.com/v1/` |
| Push Notifications | `https://app-api.push.srv.smart.com` |
| DCS API | `https://api.prod.digitalchargingsolutions.com/` |
| DCS Auth (MS OAuth) | `https://login.microsoftonline.com/{tenant}/` |
| OTA App Info | `https://hzm8dn2rt8.execute-api.eu-central-1.amazonaws.com/` |
| ChargedDot Cloud | `https://abb-api.chargedot.com/evci/` |

### INTL-Only (Smart Global Platform)

| Service | Base URL |
|---------|----------|
| IAM, UC, VC host | `https://sg-app-api.smart.com/` |
| Static assets/CDN | `https://sg-app.smart.com/` |

### Authentication Headers

| Variant | Mechanism | Key Headers |
|---------|-----------|-------------|
| **ECARX (Both)** | Session token from GID login | `Authorization: Bearer {token}`, `X-B3-TraceId`, `X-B3-SpanId` |
| **EU GlobalHeaderInterceptor** | App-level HMAC-SHA256 | `Xs-Channel-Id: APP_EU`, `Xs-Sign-Type: SHA256`, `Xs-Sign-Timestamp`, `Xs-Sign-UUID`, `Xs-Sign-Value: SHA256("APP_EU&{uuid}&{ts}&SHA256&{secret}")`, `Xs-Auth-Token` |
| **INTL VC (Alibaba Cloud)** | API Gateway HMAC-SHA256 | `X-Ca-Key`, `X-Ca-Timestamp`, `X-Ca-Nonce`, `X-Ca-Signature`, `X-Ca-Signature-Headers`, plus `x-smart-id` |

---

## Platform Differences Summary

### Completely Different Between EU and INTL

| Domain | EU Approach | INTL Approach |
|--------|-------------|---------------|
| **App Login** | EcoPlatform OAuth (`api.app-auth.srv.smart.com`) — Gigya-based, token/revoke | Smart Global IAM (`sg-app-api.smart.com/iam/`) — email/password sign-up, Google bind, forgot-password |
| **User Profile** | EcoPlatform `user-info` endpoint | Smart Global UC (`sg-app-api.smart.com/uc/`) with modify, agreements, base info |
| **Vehicle Pairing** | `vcrm.srv.smart.com/v1/vehicle-pairing` | GSVApi `vehicle/v1/ownership/bind` |
| **Vehicle Data** | `vcrm.srv.smart.com/v1/vehicle-information` | Not present (uses IoV endpoints directly) |
| **Charging POI/Tariffs** | DCS platform (DigitalChargingSolutions.com) — POI search, tariffs, PnC contracts | Not present (likely uses in-app map SDKs) |
| **OTA Info** | AWS Lambda (`hzm8dn2rt8.execute-api...`) | ECARX OTA API (`ota-api` urlname) |
| **Push Notifications** | Dedicated push service (`app-api.push.srv.smart.com`) | Not a separate API (likely FCM native) |
| **Privacy/Consent** | OneTrust SDK integration | Not present |
| **Localization** | Lokalise SDK | Not present (likely built-in) |
| **CAPTCHA** | — | `captcha/generator/captcha/email/{appId}/{sessionId}` |
| **Agreements** | — | `static/user/agreement/{type}`, `static/smart-region-1.0.json` |

### GSVApi Differences (mostly shared, some path divergence)

| Endpoint | EU | INTL |
|----------|----|----|
| `vehicle/v1/ability/{modelCode}/{vin}` | ✅ | ✅ |
| `vehicle/v1/ownership/bind` | ✅ | ✅ |
| `vehicle/v1/ownership/unbind` | ✅ | ✅ |
| `vehicle/v1/ownership/list` | ✅ | ✅ |
| `vehicle/v1/vehicleCustomerInfo` (query/post) | ✅ path: `.../query` | ✅ path: direct POST |
| `vehicle/v1/vehicleCustomerInfo/save` | ✅ | — |
| `vehicle/v1/vehicleCustomerInfo/cleanVehicleNickname` | ✅ | — |
| `vehicle/v1/vehicleCustomerInfo/averagePowerOffset/{vin}` | — | ✅ |
| `vehicle/v1/vehicleCustomerInfo/modify` | — | ✅ (via VehicleVCApi) |
| `vehicle/v1/ability/bluetooth/{vin}` | — | ✅ |
| `vehicle/v1/ota/findVersion` | ✅ | — |
| `vehicle/v1/ota/findVersion/one` | ✅ | — |
| `vehicle/v1/favourite/*` (query/save/delete) | ✅ (new path) | ✅ (`vehicleFavouriteSetting/*`) |
| `service/api/v1/oauth20/authorize` | — | ✅ |
| `api/user/toc/base/detail` | — | ✅ |

### HostAppApi Differences

| Endpoint | EU | INTL |
|----------|----|----|
| Credentials | `aliCloud/credentials/{type}` | `vc/oss/credentials/{type}` |
| Token Refresh | — | `iam/service/api/v1/refresh/` |
| Device ClientId | — | `iam/service/api/v1/device/updateClientId` |

---

## Shared APIs (Both APKs)

### IoV WebServiceInterface

**Source**: `com.ecarx.open.http.iovfor` (INTL) / `com.ecarx.open.http.iovif` (EU)
**Base URL**: `https://api.xchanger.cn` with `urlname` routing
**~195 endpoints** — identical in both APKs

Organized by domain:

#### Vehicle Status & Telematics (~21 endpoints)
| Method | Path | urlname | Description |
|--------|------|---------|-------------|
| GET | `/remote-control/vehicle/status/{vin}` | `device-api` | Full vehicle status (battery, doors, windows, tyres, GPS, climate) |
| GET | `/remote-control/vehicle/status` | — | Vehicle status (query-param variant) |
| GET | `/remote-control/vehicle/status/state/{vin}` | `device-api` | Running state (power mode, speed) |
| GET | `/remote-control/vehicle/status/location` | — | GPS position |
| GET | `/remote-control/vehicle/status/soc/{vin}` | — | SOC / charging detail |
| GET | `/remote-control/vehicle/status/history/diagnostic/{vin}` | `device-api` | DTC history |
| GET | `/geelyTCAccess/tcservices/vehicle/status/qrvs/{vin}` | — | QRVS status |
| GET | `/geelyTCAccess/tcservices/vehicle/status/powerMode/{vin}` | — | Power mode status |
| PUT | `/remote-control/vehicle/telematics/{vin}` | `device-api` | Remote control command |
| PUT | `/geelyTCAccess/tcservices/vehicle/telematics/{vin}` | — | Diagnostics command |
| PUT | `/geelyTCAccess/tcservices/vehicle/telematics/activate/{vin}` | — | Activate telematics |
| GET | `/geelyTCAccess/tcservices/vehicle/telematics/activate/{vin}` | — | Activation status |
| POST | `/remote-control/user/authorization/status/journalLog/{vin}` | — | Authorized journal log command |
| GET | `/remote-control/user/authorization/vehicle/status/{vin}` | — | Authorized vehicle status |
| GET | `/remote-control/getVtmSettingStatus` | — | VTM settings |

#### Charging (~16 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/charge-server/ecarx_charge_set/{vin}` | Last charge settings |
| GET | `/charge-server/ecarx_charge_set/{vin}?bizType=` | Charge settings by type |
| GET | `/charge-server/ecarx_charge_set/v2/{vin}?bizType=` | Charge settings v2 |
| GET | `/charge-server/ecarx_charge_set/{vin}?bizType=&mode=` | Temp control settings |
| POST | `/charge-server/ecarx_charge_set/{vin}` | Set charging (6 body variants: now, once, preferential, reservation, travel plan, general, temp control) |
| GET | `/charge-server/charge_status/{vin}` | Charging state |
| GET | `/charge-server/charge_record/{vin}` | Charge records (EU only adds this path) |
| GET | `/charge-server/ecarx_charge_record/{vin}` | Charge records (paginated) |
| GET | `/charge-server/charge_config/nextTravelTime?vin=` | Next travel time config |
| GET | `/remote-control/charging/reservation/{vin}` | Charging reservation (IHU history) |

#### Journey Logs & Trips (~9 endpoints)
| Method | Path | urlname | Description |
|--------|------|---------|-------------|
| GET | `/geelyTCAccess/tcservices/vehicle/status/journalLogV4/{vin}` | `vlog-api` | Trip journal v4 |
| GET | `/geelyTCAccess/tcservices/vehicle/status/historyV2/{vin}` | `vlog-api` | Trip track history v2 |
| GET | `/geelyTCAccess/tcservices/vehicle/status/getTotalDistanceByLabel/{vin}` | `vlog-api` | Total distance by label |
| GET | `/geelyTCAccess/tcservices/vehicle/status/journalLogLongTerm/{vin}` | `vlog-api` | Long-term journal |
| POST | `/geelyTCAccess/tcservices/vehicle/status/journalLog/mark/{vin}` | `vlog-api` | Mark/favorite trip |
| POST | `/geelyTCAccess/tcservices/vehicle/status/journalLog/delete/{vin}` | — | Delete trip |
| GET | `/vehicle-history-service/journal-service/vehicle/status/journalLog/{vin}` | `vlog-api` | Journal log (v2 path) |
| GET | `/vehicle-history-service/journal-service/vehicle/status/history/{vin}?source=tc` | `vlog-api` | Trip track (v2 path) |
| PUT | `/remote-control/vehicle/status/journalLog/{vin}` | `device-api` | Trip log remote command |

#### Energy Rankings (~4 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/geelyTCAccess/tcservices/vehicle/status/ranking/odometer/vehicleModel/{vin}?topn=100` | Odometer ranking |
| GET | `/geelyTCAccess/tcservices/vehicle/status/ranking/aveFuelConsumption/vehicleModel/{vin}?topn=100` | Fuel consumption ranking |
| GET | `/geelyTCAccess/tcservices/vehicle/status/ranking/aveEnergyConsumption/vehicleModel/{vin}?topn=100` | Energy consumption ranking |
| GET | `vehicleowner/drivingbehavior/powerConsumption` | Driving behavior |

#### Geofences (~13 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/geelyTCAccess/tcservices/vehicle/geofence/all/{vin}` | All geofences |
| GET | `/geelyTCAccess/tcservices/vehicle/geofence/latest/{vin}` | Latest geofence |
| POST | `/geelyTCAccess/tcservices/vehicle/geofence` | Create geofence |
| PUT | `/geelyTCAccess/tcservices/vehicle/geofence` | Update geofence |
| DELETE | `/geelyTCAccess/tcservices/vehicle/geofence/{id}` | Delete geofence |
| GET | `lbs/ecarx_electric_fences/all/{vin}` | Electric fences (legacy) |
| POST | `lbs/ecarx_electric_fence` | Create electric fence (legacy) |
| PUT | `lbs/ecarx_electric_fence` | Update electric fence (legacy) |
| DELETE | `lbs/ecarx_electric_fence/{id}` | Delete electric fence (legacy) |
| GET | `/remote-control/user/authorization/vehicle/geofence/all/{vin}` | Authorized geofences |
| POST | `/remote-control/user/authorization/vehicle/geofence` | Create authorized geofence |
| PUT | `/remote-control/user/authorization/vehicle/geofence` | Update authorized geofence |
| DELETE | `/remote-control/user/authorization/vehicle/geofence/{id}` | Delete authorized geofence |

#### Locker / Fridge / Fragrance / Climate (~5 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/remote-control/locker/secret/{vin}` | Locker secret/PIN |
| GET | `/remote-control/getLocker/status/{vin}` | Locker status |
| GET | `/remote-control/getFridge/status/{vin}` | Fridge status |
| GET | `/remote-control/vehicle/fragrance/{vin}` | Fragrance status |
| GET | `/remote-control/schedule/{vin}` | Climate schedule |

#### Visitor
| Method | Path | Description |
|--------|------|-------------|
| POST | `/remote-control/visitor/secret` | Visitor captcha |

#### GDPR / Authorization (~6 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/remote-control/user/authorization/insert` | Insert authorization |
| POST | `/remote-control/user/authorization/selectRecordList` | List authorization records |
| POST | `/remote-control/user/authorization/selectRecord` | Get authorization record |
| POST | `/remote-control/user/authorization/selectStatus` | Get authorization status |
| POST | `/remote-control/user/authorization/send/to/car` | Send GDPR consent to car |
| POST | `/remote-control/user/authorization/userDeleteAccount` | Delete account (GDPR) |

#### Face Recognition (~5 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/remote-control/app/faceInfo/delete` | Delete face |
| POST | `/remote-control/app/faceInfo/insert` | Register face |
| GET | `/remote-control/vehicle/face/del` | Query face deletion status |
| DELETE | `/remote-control/vehicle/face/del` | Delete face from vehicle |
| POST | `/remote-control/vehicle/face/register` | Register face on vehicle |

#### OTA / FOTA (~2 endpoints)
| Method | Path | urlname | Description |
|--------|------|---------|-------------|
| POST | `/fota/geea/assignment/notification` | — | FOTA notification |
| POST | `/app/ecarx_ecu_ota/detail` | `ota-api` | ECU OTA update status |

#### Auth / Login / Account (~12 endpoints)
| Method | Path | urlname | Description |
|--------|------|---------|-------------|
| POST | `/auth/oauth2/auth_token/gid50e31eb1fa822b9` | — | OAuth2 token |
| POST | `/auth/account/session/secure` | `user-api` | Login (multiple overloads) |
| PUT | `/auth/account/session/secure` | `user-api` | Refresh token |
| DELETE | `/auth/account/session/secure` | `user-api` | Logout |
| PUT | `/gid/resetPassword` | `user-api` | Reset password |
| PUT | `/gid/changePassword` | `user-api` | Change password |
| PUT | `/auth/account/resetuser/secure` | `user-api` | Reset user |
| POST | `/auth/customer` | `user-api` | Register customer |
| GET | `/auth/account/baidu/relation` | — | Baidu account relation |
| GET | `/auth/account/baidu/openid` | — | Baidu OpenID |

#### User / Member / Profile (~23 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/gid/vehicle/{userId}` | User vehicles |
| PUT | `/member/user/{userId}` | Update user |
| GET | `/member/user/{userId}` | Get user |
| GET | `/member/pin/status` | PIN status |
| POST | `/member/pin` | Create PIN |
| POST | `/member/pin/verify` | Verify PIN |
| PUT | `/member/pin/status` | Toggle PIN |
| POST | `/member/invitationrequest` | Create invitation |
| DELETE | `/member/invitationrequest` | Delete invitation |
| GET | `/member/invitationrequest/{invatationId}` | Get invitation |
| GET | `/profile/notification` | Notification switches |
| POST | `/profile/notification` | Set notification switches |
| POST | `/profile/faceinfo` | Set face info |
| GET | `/profile/faceinfo` | Get face info |
| DELETE | `/profile/faceinfo` | Delete face info |
| POST | `/profile/concurrently/switch` | Bluetooth switch |
| POST | `/profile/concurrently/switch/status` | Bluetooth switch status |
| POST | `/profile/protocol` | Accept protocol |
| POST | `/profile/protocols` | List protocols |
| GET | `/profile/protocol/relieve/{id}` | Revoke protocol |
| POST | `/profile/examResult` | Submit exam result |
| POST | `/profile/examResult/search` | Search exam results |
| GET | `/profile/setting/language` | Language setting |

#### CSP / Platform User (~10 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/csp-center/csp/user` | Create CSP user |
| PUT | `/csp-center/csp/user` | Update CSP user |
| POST | `/csp-center/csp/user/vehicle` | Link CSP vehicle |
| GET | `/csp-center/csp/verification/mobilePhone` | CSP phone verification (2 overloads) |
| GET | `/csp-center/csp/platform/csp/verification/mobilePhone/{mobilePhone}` | CSP phone code verify |
| POST | `/csp-center/platform/csp/user` | Create platform user |
| PUT | `/csp-center/platform/csp/resetPassword` | Reset platform password |
| POST | `/csp-center/platform/relation` | Create platform relation |

#### Account Affection (~4 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/account-center/account/affection` | Get linked accounts |
| GET | `/account-center/account/affectionInfo` | Get linked account info |
| POST | `/account-center/account/affection` | Link account |
| POST | `/account-center/affection/unbind` | Unlink account |

#### Verification / Identity (~8 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/identify/verification` | Slider verification |
| GET | `/identify/verificationCode` | Send verification code |
| GET | `/identify/verification` | Verify code (2 overloads) |
| GET | `/identify/validity` | Check code validity |
| GET | `/identify/captcha` | Request captcha |
| POST | `/identify/slider` | Request slider captcha |
| GET | `/api/v1/verification/mobilePhone/{mobile}` | Mobile verification |
| GET | `/api/v1/verification/{mobile}` | Verify mobile code |

#### Device / Dealer / Platform (~10 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/device-platform/ecarx_car/target/{targetId}` | Vehicle info by target |
| GET | `/device-platform/ecarx_device/device/{deviceId}/config/secure` | Device config |
| GET | `/device-platform/dealers` | Search dealers |
| GET | `/device-platform/user/dealer?type=preferred` | Preferred dealer |
| POST | `/device-platform/user/dealer` | Set preferred dealer |
| POST | `/device-platform/user/session/update` | Update session |
| GET | `/device-platform/user/vehicle/secure` | List vehicles |
| PUT | `/platform/user/operation/{userId}?operation=mod` | Modify user |
| PUT | `/platform/user/operation/{userId}?operation=bind` | Bind vehicle |
| PUT | `/platform/user/operation/{userId}?operation=unbind` | Unbind vehicle |
| PUT | `/platform/user/operation/{userId}?operation=confirm` | Confirm operation |
| GET | `/platform/user/info/{userId}` | User info |
| GET | `/platform/user/vehicle/mobilePhone/{mobile}` | Vehicles by phone |

#### Misc (~16 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/device/{targetClient}/session` | Create device session |
| GET | `/api/v1/datasync/poistars` | POI favorites |
| POST | `/api/v1/datasync/poistar` | Save POI |
| DELETE | `/api/v1/datasync/poistar/{collectionId}` | Delete POI |
| POST | `api/v1/wallet/sign` | Wallet signature |
| POST | `/api/v1/image` | Upload image |
| GET | `/api/v1/flowinfo` | SIM data flow info |
| GET | `/api/v1/user/verify` | Verify user (3 overloads) |
| GET | `/push-platform/cache/message/{vin}` | Cached push messages |
| POST | `/geelyTCAccess/tcservices/sent2car/sent` | Send to car |
| POST | `/geelyTCAccess/tcservices/appSent2Ihu/byTp` | Send location to IHU (Zeekr) |
| POST | `/geelyTCAccess/tcservices/ihu/send/to/car` | Send to car (CMA) |
| GET | `/geelyTCAccess/tcservices/internal/services/purchase-history` | Purchase history |
| GET | `/geelyTCAccess/tcservices/internal/services/service/in-use-tservice/` | In-use services |
| GET | `/geelyTCAccess/tcservices/data/dictionary` | Data dictionary |
| GET | `/geelyTCAccess/tcservices/carConfig/{vin}` | Car configuration |
| PUT | `/geelyTCAccess/tcservices/customer/vehicle/plantNo/{vin}` | Set plant number |
| POST | `/remote-control/vehicle/familyNumber/AppWakeUpTcam/{vin}` | Wake up TCAM |
| POST | `/upload/sign/resource` | Upload resource |
| POST | `/lotus-service/auth/code` | Lotus QR login |
| POST | `/user-service/device/code` | Device code |

#### NFC / Digital Key (deprecated copies in WebServiceInterface)
~14 endpoints duplicated from HttpInterface, marked deprecated. See Digital Key section below.

---

### GidServiceInterface

**Source**: `blldo.bllif.bllif.bllnew` (both APKs, identical)
**Base URL**: `https://api.xchanger.cn` with `urlname` routing
**24 endpoints**

| Method | Path | urlname | Description |
|--------|------|---------|-------------|
| POST | `/auth-center/account/session` | `user-api` | Login (auth center) |
| POST | `/auth/lid/token` | `user-api` | Lynk&Co login token |
| DELETE | `/auth/account/session/secure` | `user-api` | Logout |
| GET | `/geelyTCAccess/tcservices/capability/{vin}` | — | Vehicle capabilities |
| GET | `/device-platform/user/vehicle/secure` | `device-api` | List vehicles |
| POST | `/auth/account/session/secure` | `user-api` | Login (multiple overloads with B3 tracing) |
| GET | `/hf-capability-center/api/v2/ability/{vin}` | — | Ability v2 (ECARX-native, different from GSV ability) |
| PUT | `/auth/account/session/secure` | `user-api` | Refresh token (Call + Observable variants) |
| POST | `/auth/cert/file` | `api-sdk` | Cert file upload |
| POST | `/dk-pki/api/v1/cert/client` | — | DK PKI cert |
| POST | `/auth/cert/info` | `api-sdk` | Cert info check |

---

### Digital Key HttpInterface

**Source**: `com.base.bluetooth.dk.http.HttpInterface` (both APKs, identical)
**Base URL**: ECARX IoV platform
**67 endpoints** — Digital Key v1+v2, NFC cards, Car Sharing v1, PKI

| Domain | Count | Key Paths |
|--------|-------|-----------|
| DK v1 CRUD | ~15 | `/digitalkey-service-20/api/v1/digitalkeys{/*}` |
| DK v2 CRUD | ~15 | `/digitalkey-service-20/api/v2/digitalkeys{/*}` |
| DK Calibration | ~6 | `/digitalkey-service-20/api/v{1,2}/calibration-gears{/*}` |
| DK Auth/RPA | ~4 | `/digitalkey-service-20/api/v{1,2}/digitalkeys/auth`, `.../rpa/auth` |
| DK Sync | ~4 | `/digitalkey-service-20/api/v{1,2}/digitalkeys/sync`, `freeze`, `unFreeze` |
| DK Status | ~3 | `/digitalkey-service-20/api/v{1,2}/getDkStatus`, `getDkSyncResult`, `getDksOfCem` |
| NFC v1 | 3 | `/digitalkey-service-20/api/v1/nfc/card/{lock,unlock,write}` |
| NFC v2 | 3 | `/digitalkey-service-20/api/v2/nfc/card/{lock,unlock,write}` |
| Car Sharing v1 | 7 | `/tsp-carsharing-platform/api/v1/{create,accept,cancel,reject,finish,update,detail,...}` |
| PKI | 4 | `/dk-pki/api/v1/cert/client` (POST/GET/PUT/DELETE) |
| Token Refresh | 1 | `/api/v1/access_token/{token}` |
| File Download | 1 | Dynamic `@Url` → `Call<ResponseBody>` |
| DK Owners v2 | 3 | `/digitalkey-service-20/api/v2/digitalkeys-owners{/*}` |
| Shared DK List | 2 | `/digitalkey-service-20/api/v{1,2}/shared-digitalkeys` |
| Key Use Records | 2 | `/digitalkey-service-20/api/v{1,2}/getKeyUseRecords` |

---

### Car Sharing v2 Signed

**Source**: `com.ecarx.carShare.b.b` (both APKs, identical)
**Base URL**: Dynamic via `CommonOpenApi.getInstance().getHostUrl(areaType)`
**26 endpoints** — all under `/tsp-carsharing-platform/api-sign/v{1,2}/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `.../v1/vehicle-bind-list` | Vehicles available for sharing |
| POST | `.../v1/create-car-sharing` | Create sharing invitation |
| POST | `.../v1/sub-create-car-sharing` | Create sub-sharing |
| PUT | `.../v2/update-car-sharing` | Update sharing |
| GET | `.../v1/social-sharing-info` | Social sharing URL |
| GET | `.../v1/car-sharing-detail` | Sharing detail |
| GET | `.../v1/car-sharing-in-progress` | In-progress sharings |
| GET | `.../v1/vehicle-status` | Vehicle status during sharing |
| GET | `.../v1/verify-acceptor` | Verify acceptor eligibility |
| POST | `.../v1/sub-car-sharing-reference` | Sub-sharing reference |
| POST | `.../v2/limited-polling` | Limited poll (2 overloads) |
| GET | `.../v1/vehicle-sharing-list` | All vehicle sharings |
| GET | `.../v1/car-sharing-info` | Sharing info by VIN |
| GET | `.../v1/car-sharing-histories` | Sharing history |
| POST | `.../v1/upload-base64-file` | Upload file for sharing |
| POST | `.../v2/finish-car-sharing` | Finish sharing |
| GET | `.../v1/vehicle-sharing-platform` | Sharing platform by VIN |
| GET | `.../v1/accept-car-sharing-in-progress` | Accepted sharings in progress |
| POST | `.../v1/delete-car-sharing-histories` | Delete sharing history |
| GET | `.../v1/accept-car-sharing-histories` | Accepted sharing history |
| POST | `.../v1/reject-car-sharing` | Reject sharing |
| POST | `.../v2/force-finish-car-sharing` | Force finish |
| POST | `.../v2/cancel-car-sharing` | Cancel sharing |
| PUT | `.../v2/extend-car-sharing-time` | Extend sharing time |
| POST | `.../v2/accept-car-sharing` | Accept sharing |

---

### CerServiceInterface — PKI

**Source**: `com.hf.heartbeat.cer.net.CerServiceInterface` (both, identical)
**4 endpoints** — Certificate management for heartbeat/DK

| Method | Path | Description |
|--------|------|-------------|
| POST | `/dk-pki/api/v1/cert/client` | Create client certificate |
| DELETE | `/dk-pki/api/v1/cert/client` | Delete client certificate |
| GET | `/dk-pki/api/v1/cert/client` | Get client certificate |
| PUT | `/dk-pki/api/v1/cert/client` | Update client certificate |

---

### SmartLog Upload

**Source**: `com.huanfu.smartlog.logsend.http.WebServiceInterface` (both, identical)
**1 endpoint**

| Method | Path | Key Headers | Description |
|--------|------|-------------|-------------|
| POST | `/ecarx-terminal-service/logan/upload.json` | `X-LogUpload`, `X-APP-VERSION`, `X-LOGSTORE-NAME`, `X-VIN`, `X-GID`, `X-FileName`, `X-FilePath` | Upload device logs |

---

### Weather / Air Quality

**Source**: `com.ecarx.open.http.iovfor.iovdo` (both, identical)
**3 endpoints**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/security2/v2/weather/observe` | Current weather observation |
| GET | `/security2/v2/city_code/geo_location` | Geo-location city lookup |
| GET | `/security2/v2/weather/index` | Air quality index |

---

### GSVApi — Global Vehicle Service

**Source**: INTL `com.smart.global.app.service.http.GSVApi` / EU `com.global.vehicle.common.service.http.GSVApi`
**Base URL**: `https://sg-app-api.smart.com/` (via SDK config)

See [GSVApi Differences table above](#gsvapi-differences-mostly-shared-some-path-divergence) for per-endpoint EU/INTL availability.

Shared endpoints:

| Method | Path | Headers | Description |
|--------|------|---------|-------------|
| GET | `vehicle/v1/ability/{modelCode}/{vin}` | `x-smart-id` | Vehicle abilities + images |
| POST | `vehicle/v1/ownership/bind` | `x-smart-id` | Bind vehicle to account |
| POST | `vehicle/v1/ownership/unbind` | `x-smart-id` | Unbind vehicle |
| POST | `vehicle/v1/ownership/list` | `x-smart-id` | List owned vehicles |
| POST | `vehicle/v1/vehicleCustomerInfo` | `x-smart-id` | Query vehicle customer info |

---

## EU-Only APIs

### EcoPlatform Auth

**Source**: `com.smart.hello.data.api.apis.ecoplatform`
**Base URLs**: `https://api.app-auth.srv.smart.com/v1/`, `https://vcrm.srv.smart.com/v1/`

#### LoginAppApi (2 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| POST | `token` | Refresh/exchange token |
| POST | `revoke` | Revoke token |

#### UserInfoApi (1 endpoint)
| Method | Path | Description |
|--------|------|-------------|
| GET | `user-info` | Get authenticated user info |

---

### Vehicle Activation

**Source**: `com.smart.hello.data.api.apis.ecoplatform.VehicleActivationApi`
**Base URL**: `https://vcrm.srv.smart.com/v1/`

| Method | Path | Headers | Description |
|--------|------|---------|-------------|
| POST | `vehicle-pairing` | `id-token`, `access-token` | Pair vehicle to account |
| POST | `vehicle-unpairing` | `id-token`, `access-token` | Unpair vehicle |

---

### Vehicle Data

**Source**: `com.smart.hello.data.api.apis.VehicleDataApi`
**Base URL**: `https://vcrm.srv.smart.com/v1/`

| Method | Path | Description |
|--------|------|-------------|
| GET | `vehicle-information?vin={vin}` | Vehicle info from VCRM |

---

### DCS — Digital Charging Solutions

**Source**: `com.smart.hello.data.api.apis.dcs`
**Base URL**: `https://api.prod.digitalchargingsolutions.com/`
**10 endpoints** across 4 interfaces

#### AuthTokenApi (1 endpoint)
| Method | Path | Description |
|--------|------|-------------|
| POST | `oauth2/token` (via `login.microsoftonline.com/{tenant}/`) | Microsoft OAuth for DCS access. Tenant: `a60cd2d9-82a0-4bff-b9e9-8d71626abb0e` |

#### ContractsApi (4 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| GET | `usergateway/private/customer-data/v3/oems/{oemGroupId}/customers/{userId}/contracts` | List charging contracts |
| PUT | `usergateway/private/pnc/v1/oems/{oemId}/contracts/{evcoId}` | Update PnC contract |
| GET | `usergateway/private/plug-and-charge-service/v1/contracts/{contractId}/pnc` | Get PnC details |
| POST | `usergateway/private/plug-and-charge-service/v1/contracts/{contractId}/pnc/terminate` | Terminate PnC |

#### PoiTariffsApi (2 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| POST | `usergateway/public/customer-service/v3/companycodes/{companyCodeId}/tariffs/{tariffId}/prices` | Get tariff prices |
| GET | `usergateway/public/customer-service/v3/companycodes/{companyCodeId}/tariffs` | List tariffs |

#### PoisApi (3 endpoints)
| Method | Path | Description |
|--------|------|-------------|
| POST | `usergateway/public/poi-static-data/v1/poi-cluster-search` | Search charging station clusters |
| POST | `usergateway/public/poi-static-data/v1/pool-search` | Search charging pools |
| POST | `usergateway/public/poi-availability/v2/charge-points/query` | Charge point live availability |

---

### OTA App Info

**Source**: `com.smart.hello.data.api.apis.OTAApi`
**Base URL**: `https://hzm8dn2rt8.execute-api.eu-central-1.amazonaws.com/`

| Method | Path | Headers | Description |
|--------|------|---------|-------------|
| GET | `app/info/{vin}` | `access_token` | OTA app info for vehicle (AWS Lambda) |

---

### Push Notifications

**Source**: `com.smart.hello.data.api.apis.PushNotificationApi`
**Base URL**: `https://app-api.push.srv.smart.com`

| Method | Path | Description |
|--------|------|-------------|
| POST | `sync/{userId}/{fid}` | Sync push notification preferences |
| DELETE | `sync/{userId}/{type}/{id}` | Remove push notification subscription |

---

### Lokalise SDK

**Source**: `com.lokalise.sdk.api.SdkEndpoints`
**3 endpoints** — runtime localization bundle fetching (third-party SDK, not Smart API)

---

### OneTrust Privacy SDK

**Source**: `com.onetrust.otpublishers.headless.Internal.Network.a`
**3 endpoints** — consent/privacy management (third-party SDK, not Smart API)

---

## INTL-Only APIs

### AccountIAMApi

**Source**: `com.smart.module.common.account.api.AccountIAMApi`
**Base URL**: `https://sg-app-api.smart.com/`
**14 endpoints**

| Method | Path | Description |
|--------|------|-------------|
| POST | `iam/service/api/v1/signUp` | Sign up with email |
| POST | `iam/service/api/v1/login` | Login |
| POST | `iam/service/api/v1/login/{type}` | Login by type (e.g. social) |
| POST | `iam/service/api/v1/logout` | Logout |
| POST | `iam/service/api/v1/logoff` | Account logoff/deactivate |
| POST | `iam/service/api/v1/refresh/` | Refresh token |
| POST | `iam/service/api/v1/forgotPassword` | Forgot password |
| POST | `iam/service/api/v1/changeEmail` | Change email |
| POST | `iam/service/api/v1/checkEmailCode` | Check email verification code |
| POST | `iam/service/api/v1/checkEmailExist` | Check if email exists |
| POST | `iam/service/api/v1/device/updateClientId` | Update push client ID |
| POST | `iam/service/api/v1/thirdPart/google/bind` | Bind Google account |
| POST | `iam/service/api/v1/thirdPart/google/unbind` | Unbind Google account |
| GET | `iam/service/api/v1/thirdPart/query` | Query linked third-party accounts |

---

### AccountUCApi

**Source**: `com.smart.module.common.account.api.AccountUCApi`
**Base URL**: `https://sg-app-api.smart.com/`
**4 endpoints**

| Method | Path | Description |
|--------|------|-------------|
| POST | `uc/api/user/toc/base/modify` | Modify user profile |
| POST | `uc/api/user/toc/agreement/list` | List user agreements |
| GET | `uc/api/user/toc/base/info` | Get user base info |
| GET | `uc/api/user/toc/vehicle/ownership/list` | List vehicle ownerships |

---

### AccountVerifyApi

**Source**: `com.smart.module.common.account.api.AccountVerifyApi`
**Base URL**: `https://sg-app-api.smart.com/`
**1 endpoint**

| Method | Path | Description |
|--------|------|-------------|
| POST | `captcha/generator/captcha/email/{appId}/{sessionId}` | Generate email CAPTCHA |

---

### AgreementApi

**Source**: `com.smart.module.common.account.api.AgreementApi`
**Base URL**: `https://sg-app.smart.com/` (static CDN)
**2 endpoints**

| Method | Path | Description |
|--------|------|-------------|
| GET | `static/user/agreement/{type}` | Get agreement content by type |
| GET | `static/smart-region-1.0.json` | Region configuration data |

---

### VehicleVCApi

**Source**: `com.smart.global.app.view.page.vehicle_settings.api.VehicleVCApi`
**Base URL**: `https://sg-app-api.smart.com/vc/`
**3 endpoints**

| Method | Path | Description |
|--------|------|-------------|
| POST | `vehicle/v1/vehicleCustomerInfo/modify` | Modify vehicle customer info |
| POST | `vehicle/v1/ownership/list` | List ownerships (VC-scoped) |
| POST | `vehicle/v1/ownership/unbind` | Unbind vehicle (VC-scoped) |

---

## Endpoint Totals

| Interface | INTL | EU | Shared? |
|-----------|------|-----|---------|
| IoV WebServiceInterface | ~202 | ~195 | ✅ Near-identical |
| GidServiceInterface | 24 | 24 | ✅ Identical |
| Digital Key HttpInterface | 67 | 67 | ✅ Identical |
| Car Sharing v2 Signed | 26 | 26 | ✅ Identical |
| CerServiceInterface (PKI) | 4 | 4 | ✅ Identical |
| SmartLog Upload | 1 | 1 | ✅ Identical |
| Weather/Air | 3 | 3 | ✅ Identical |
| GSVApi | 14 | 9 | ⚠️ Partial overlap |
| HostAppApi | 3 | 1 | ⚠️ Different paths |
| AccountIAMApi | 14 | — | ❌ INTL only |
| AccountUCApi | 4 | — | ❌ INTL only |
| AccountVerifyApi | 1 | — | ❌ INTL only |
| AgreementApi | 2 | — | ❌ INTL only |
| VehicleVCApi | 3 | — | ❌ INTL only |
| EcoPlatform (Login+User+Activation) | — | 5 | ❌ EU only |
| VehicleDataApi | — | 1 | ❌ EU only |
| DCS (Auth+Contracts+Tariffs+POIs) | — | 10 | ❌ EU only |
| OTAApi (AWS) | — | 1 | ❌ EU only |
| PushNotificationApi | — | 2 | ❌ EU only |
| Lokalise SDK | — | 3 | ❌ EU only (3rd party) |
| OneTrust SDK | — | 3 | ❌ EU only (3rd party) |
| **TOTALS** | **~368** | **~355** | |

---

## Already Implemented

Endpoints currently used by the Hello Smart HA integration:

| Endpoint | Status | Notes |
|----------|--------|-------|
| `/auth/account/session/secure` (POST) | ✅ INTL login | via GidServiceInterface |
| EU Gigya OAuth flow | ✅ EU login | Multi-step external |
| `/device-platform/user/vehicle/secure` (GET) | ✅ | List vehicles |
| `/device-platform/user/session/update` (POST) | ✅ | Select vehicle |
| `/remote-control/vehicle/status/{vin}` (GET) | ✅ | Full vehicle status |
| `/remote-control/vehicle/status/soc/{vin}` (GET) | ✅ | SOC/charging |
| `/remote-control/vehicle/status/state/{vin}` (GET) | ✅ | Running state |
| `/remote-control/vehicle/telematics/{vin}` (PUT) | ✅ | Remote commands |
| `/remote-control/vehicle/status/history/diagnostic/{vin}` (GET) | ✅ | Diagnostics |
| `/remote-control/charging/reservation/{vin}` (GET) | ✅ | Charging schedule |
| `/remote-control/schedule/{vin}` (GET) | ✅ | Climate schedule |
| `/remote-control/getFridge/status/{vin}` (GET) | ✅ | Fridge |
| `/remote-control/getLocker/status/{vin}` (GET) | ✅ | Locker |
| `/remote-control/locker/secret/{vin}` (POST) | ✅ | Locker PIN |
| `/remote-control/vehicle/fragrance/{vin}` (GET) | ✅ | Fragrance |
| `/remote-control/getVtmSettingStatus` (GET) | ✅ | VTM |
| `/geelyTCAccess/tcservices/vehicle/geofence/all/{vin}` (GET) | ✅ | Geofences |
| `/geelyTCAccess/tcservices/vehicle/status/journalLogV4/{vin}` (GET) | ✅ | Trip journal |
| `/geelyTCAccess/tcservices/vehicle/status/getTotalDistanceByLabel/{vin}` (GET) | ✅ | Total distance |
| `/geelyTCAccess/tcservices/capability/{vin}` (GET) | ✅ | Capabilities |
| `/fota/geea/assignment/notification` (POST) | ✅ | FOTA notification |
| `/geelyTCAccess/tcservices/customer/vehicle/plantNo/{vin}` (PUT) | ✅ | Plant number |
| `/geelyTCAccess/tcservices/vehicle/status/ranking/*` (GET) | ✅ | Energy rankings |
| `vehicle/v1/ability/{modelCode}/{vin}` (GET, VC) | ✅ | Vehicle ability + images |

---

## Candidates for Integration

High-value endpoints not yet implemented that could enrich the HA integration:

| Priority | Endpoint | Value |
|----------|----------|-------|
| 🟢 High | `/charge-server/charge_status/{vin}` | Real-time charging state (plugged, charging, complete) |
| 🟢 High | `/charge-server/ecarx_charge_record/{vin}` | Charging history / session records |
| 🟢 High | `/geelyTCAccess/tcservices/vehicle/status/historyV2/{vin}` | Trip track GPS traces |
| 🟡 Medium | `/vehicle-history-service/journal-service/vehicle/status/journalLog/{vin}` | Alternative trip journal endpoint |
| 🟡 Medium | `/remote-control/vehicle/status/location` | Standalone GPS endpoint (lighter than full status) |
| 🟡 Medium | `/geelyTCAccess/tcservices/vehicle/status/journalLogLongTerm/{vin}` | Long-term trip archive |
| 🟡 Medium | `/charge-server/charge_config/nextTravelTime` | Next planned travel departure |
| 🟡 Medium | `/hf-capability-center/api/v2/ability/{vin}` | ECARX-native ability (different from VC) |
| 🟡 Medium | `vehicle/v1/ability/bluetooth/{vin}` | BLE ability flags (INTL only) |
| 🔵 Low | `/remote-control/visitor/secret` | Visitor access captcha |
| 🔵 Low | `/geelyTCAccess/tcservices/carConfig/{vin}` | Car configuration metadata |
| 🔵 Low | `/geelyTCAccess/tcservices/data/dictionary` | Data dictionary (enum mappings) |
| 🔵 Low | EU DCS POI/Tariffs endpoints | Charging station map data (EU only) |
| ⚪ Niche | Digital Key / Car Sharing | Require BLE hardware, complex pairing |
| ⚪ Niche | Face Recognition | Requires camera, enrollment flow |
| ⚪ Niche | Weather / Air Quality | HA has native weather integrations |
