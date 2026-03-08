# Feature Specification: Lovelace Vehicle Dashboard

**Feature Branch**: `004-lovelace-dashboard`  
**Created**: 2026-03-08  
**Status**: Draft  
**Input**: User description: "Create a Lovelace dashboard for the Hello Smart Home Assistant integration with vehicle image, lock/security, windows, tyre, battery/range, charging, and service cards"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Battery, Range & Charging Overview (Priority: P1) 🎯 MVP

As a Smart EV owner, I want to see my vehicle's battery level, estimated range, and charging status at a glance on my Home Assistant dashboard so I can quickly determine if I need to charge or if I have enough range for my next trip.

**Why this priority**: Battery and range are the most frequently checked pieces of information for any EV owner. This is the primary reason users install a vehicle integration. Without this card, the dashboard provides no core value.

**Independent Test**: Open the dashboard in a browser. The Battery & Range card displays current battery percentage as a visual gauge, estimated range in km, and range at full charge. The Charging Status card shows whether the charger is connected, current charging state, live power/voltage/current metrics, time to full, target SOC slider, charging schedule times, and a start/stop charging toggle. All values update on each coordinator poll cycle (60s).

**Acceptance Scenarios**:

1. **Given** the vehicle is parked and not charging, **When** the user opens the dashboard, **Then** the Battery & Range card shows the current battery percentage (e.g., 72%), estimated range (e.g., 285 km), and range at full charge. The Charging Status card shows "Not Charging" with no live metrics.
2. **Given** the vehicle is actively charging, **When** the user opens the dashboard, **Then** the Charging Status card shows "Charging", the charger connected indicator is active, live voltage/current/power values update every 60s, and time-to-full countdown is displayed.
3. **Given** the user adjusts the target SOC slider to 80%, **When** the slider value is changed, **Then** the number entity is updated and the new target SOC is sent to the vehicle.
4. **Given** the user taps the charging start/stop switch, **When** toggled, **Then** the charging command is sent and the status updates after the 8-second delayed refresh.

---

### User Story 2 — Vehicle Overview with Image (Priority: P2)

As a Smart EV owner, I want to see a visual representation of my vehicle on the dashboard — ideally in the correct exterior color — along with key status indicators (locked/unlocked, online/offline, power mode), so the dashboard feels personalized and gives me an instant snapshot of the vehicle's state.

**Why this priority**: The hero card establishes brand identity and provides the visual anchor for the entire dashboard. It contextualizes all other cards. However, it's P2 because the battery/range data is more actionable.

**Independent Test**: Open the dashboard. The hero card shows a vehicle image (color-matched if APK assets are available, otherwise a generic Smart silhouette). Below or overlaid on the image are status badges for lock state, charging state, power mode, and online/offline connectivity. The vehicle model name is displayed.

**Acceptance Scenarios**:

1. **Given** the vehicle is locked and online, **When** the dashboard loads, **Then** the hero card shows the vehicle image, a "Locked" badge with a lock icon, the current power mode, and an "Online" indicator.
2. **Given** the vehicle is offline (telematics_connected = false), **When** the dashboard loads, **Then** the hero card shows an "Offline" indicator.
3. **Given** the vehicle model is "CM590 HC11 Performance 4WD RHD APAC", **When** the dashboard loads, **Then** the vehicle name is displayed in a human-readable format.

---

### User Story 3 — Lock & Security Status (Priority: P3)

As a Smart EV owner, I want to see the lock status of all doors and the trunk, toggle the door lock, and see which doors or panels are open — ideally on a visual car diagram — so I can verify my vehicle is secure without walking outside.

**Why this priority**: Security is the second-most common reason users check a vehicle dashboard. The ability to lock/unlock remotely adds direct actionable value.

**Independent Test**: Open the dashboard. The Lock & Security card shows the main door lock toggle, individual lock status for driver/passenger/rear-left/rear-right doors and trunk, open/closed status for all 5 doors, trunk, and engine hood. Tapping the lock toggle sends the lock/unlock command. A visual top-down car diagram highlights which doors are open.

**Acceptance Scenarios**:

1. **Given** all doors are closed and locked, **When** the dashboard loads, **Then** the card shows all doors as closed (green/neutral) and the lock toggle shows "Locked".
2. **Given** the driver door is open, **When** the dashboard loads, **Then** the visual diagram highlights the driver door as open (red/warning color).
3. **Given** the user taps the unlock toggle, **When** the command is sent, **Then** the lock entity optimistically updates to "Unlocked" and the vehicle doors unlock within 15 seconds.
4. **Given** the trunk is open, **When** the dashboard loads, **Then** the trunk is highlighted as open on the diagram.

---

### User Story 4 — Tyre Status (Priority: P4)

As a Smart EV owner, I want to see tyre pressure and temperature for all four tyres in a visual layout matching the car's wheel positions, with warnings highlighted, so I can monitor tyre health before driving.

**Why this priority**: Tyre status is a safety-critical feature but is checked less frequently than battery or lock status. The visual layout adds significant UX value over raw sensor values.

**Independent Test**: Open the dashboard. The Tyre Status card shows a top-down car outline with pressure (kPa) and temperature (°C) displayed at each wheel position (FL, FR, RL, RR). Any active tyre warning is highlighted in red.

**Acceptance Scenarios**:

1. **Given** all tyre pressures are normal, **When** the dashboard loads, **Then** four pressure/temperature pairs are displayed in a car wheel layout, all in neutral/green color.
2. **Given** the front-left tyre has a warning, **When** the dashboard loads, **Then** the FL position is highlighted red with a warning icon.

---

### User Story 5 — Windows Status (Priority: P5)

As a Smart EV owner, I want to see the open/closed status and position percentage of all windows and the sunroof, with a button to close all windows remotely, so I can check if I left a window open and close them without going to the car.

**Why this priority**: Windows are checked occasionally but the close-all-windows remote action is highly valuable during unexpected rain or after parking.

**Independent Test**: Open the dashboard. The Windows card shows open/closed status for all 4 windows and the sunroof, position percentages where available, and a "Close All Windows" button. Tapping the button sends the close-windows command.

**Acceptance Scenarios**:

1. **Given** all windows are closed, **When** the dashboard loads, **Then** all windows show as closed with 0% position values.
2. **Given** the driver window is 50% open, **When** the dashboard loads, **Then** the driver window shows as open with a 50% position indicator.
3. **Given** the user taps "Close All Windows", **When** the command executes, **Then** all windows begin closing and status updates after the delayed refresh.

---

### User Story 6 — Service Information (Priority: P6)

As a Smart EV owner, I want to see maintenance and service data including odometer, service countdown, fluid levels, firmware versions, and diagnostic status, so I can plan service appointments and stay aware of vehicle health.

**Why this priority**: Service information is checked infrequently but is important for long-term vehicle maintenance. It's the least time-sensitive card.

**Independent Test**: Open the dashboard. The Service card shows odometer, days/distance/hours to service, service warning indicator, washer fluid level, brake fluid status, coolant level, firmware versions with update-available indicator, and diagnostic status/code.

**Acceptance Scenarios**:

1. **Given** service is due in 30 days, **When** the dashboard loads, **Then** the days-to-service shows "30" with an appropriate icon.
2. **Given** a firmware update is available, **When** the dashboard loads, **Then** the firmware section shows current and target versions with an "Update Available" badge.
3. **Given** washer fluid is low, **When** the dashboard loads, **Then** the washer fluid indicator shows a warning state.

---

### Edge Cases

- What happens when the vehicle is offline and entity data is stale? Cards display last-known values with an "Offline" indicator on the hero card; no controls are hidden.
- What happens when optional accessories (fridge, locker, fragrance) are not present? Those entities don't exist in the registry, so cards referencing them gracefully hide unused rows.
- What happens when the user has multiple vehicles? The dashboard is designed per-vehicle. Multiple vehicles would require duplicating the dashboard view or parameterizing entity IDs (future enhancement).
- What happens when HACS custom cards are not installed? The dashboard YAML includes a fallback using standard HA cards (entities card, gauge card, etc.) documented alongside the enhanced version.
- What happens when the vehicle image cannot be loaded? A CSS-styled fallback placeholder with the Smart logo and vehicle model name is shown instead of a broken image.

## Requirements *(mandatory)*

### Functional Requirements

#### Vehicle Image & Hero Card
- **FR-001**: The dashboard MUST display a vehicle overview card at the top with a vehicle image, model name, and key status badges (lock, charging, power mode, online/offline).
- **FR-002**: The dashboard MUST investigate the Hello Smart APK resources (Hello_Smart_APK/) for extractable vehicle render images and color-to-image mapping logic.
- **FR-003**: If vehicle images are found in the APK, the dashboard MUST extract them to a path accessible via HA's `/local/` URL scheme (e.g., `/config/www/hello_smart/`).
- **FR-004**: If the API provides a vehicle color/paint code, the dashboard MUST document the required `api.py` and `models.py` changes (without modifying integration code) and map the code to the correct image variant.
- **FR-005**: If no color-specific images are available, the dashboard MUST fall back to a generic Smart vehicle silhouette or SVG outline that can be CSS-tinted.

#### Battery & Range Card
- **FR-010**: The dashboard MUST display battery level as a visual gauge or progress bar with percentage text.
- **FR-011**: The dashboard MUST display estimated range in km prominently.
- **FR-012**: The dashboard MUST display range at full charge.

#### Charging Status Card
- **FR-020**: The dashboard MUST display the current charging state as prominent status text.
- **FR-021**: The dashboard MUST show charger connected and charge lid (AC/DC) indicators.
- **FR-022**: The dashboard MUST display live charging metrics: voltage, current (AC and DC), power, and time to full.
- **FR-023**: The dashboard MUST include an interactive target SOC slider (number entity).
- **FR-024**: The dashboard MUST display charging schedule information (status, start/end times, target SOC).
- **FR-025**: The dashboard MUST include time-picker controls for charging start and end times.
- **FR-026**: The dashboard MUST include a charging start/stop switch.

#### Lock & Security Card
- **FR-030**: The dashboard MUST display a door lock/unlock toggle using the lock entity.
- **FR-031**: The dashboard MUST show individual open/closed status for all 5 doors (driver, passenger, rear-left, rear-right, trunk).
- **FR-032**: The dashboard MUST show individual lock status for all door locks and trunk lock.
- **FR-033**: The dashboard MUST show engine hood open/closed status.
- **FR-034**: The dashboard SHOULD display a visual top-down car diagram highlighting open doors/panels.

#### Windows Status Card
- **FR-040**: The dashboard MUST display open/closed status for all 4 windows and sunroof.
- **FR-041**: The dashboard MUST display window position percentages where available.
- **FR-042**: The dashboard MUST include a "Close All Windows" button entity.
- **FR-043**: The dashboard SHOULD display a visual car diagram showing window positions.

#### Tyre Status Card
- **FR-050**: The dashboard MUST display pressure (kPa) and temperature (°C) for all 4 tyres.
- **FR-051**: The dashboard MUST display tyre warnings with red/warning highlighting.
- **FR-052**: The dashboard SHOULD lay out tyre data in a spatial arrangement matching the car's wheel positions (FL/FR top, RL/RR bottom).

#### Service Information Card
- **FR-060**: The dashboard MUST display odometer reading.
- **FR-061**: The dashboard MUST display service countdown data (days, distance, engine hours to service).
- **FR-062**: The dashboard MUST display fluid levels: washer fluid, brake fluid status, engine coolant level.
- **FR-063**: The dashboard MUST display firmware versions (current and target) with an update-available indicator.
- **FR-064**: The dashboard MUST display diagnostic status and code.
- **FR-065**: The dashboard MUST display service warning status.

#### Design & Compatibility
- **FR-070**: The dashboard MUST be defined in standard HA Lovelace YAML format, importable via the HA UI or configuration.yaml.
- **FR-071**: The dashboard MUST be dark-theme compatible with Smart brand colors (primary #0078D4 blue, white/grey accents).
- **FR-072**: The dashboard MUST be responsive — usable on both mobile and desktop HA views.
- **FR-073**: The dashboard MUST document all required HACS custom card dependencies with installation instructions.
- **FR-074**: The dashboard MUST provide a fallback version using only standard HA built-in cards if HACS cards are not available.
- **FR-075**: The dashboard MUST group cards into a single view with logical sections.
- **FR-076**: The dashboard MUST NOT modify any integration source code (`custom_components/hello_smart/`). If new API data is needed, changes are documented only.

### Key Entities

- **Dashboard YAML**: The primary deliverable — a Lovelace dashboard view definition containing all 7 card groups, referencing existing `hello_smart` entities by their entity IDs.
- **Vehicle Image Assets**: Static images (PNG/SVG) placed in `/config/www/hello_smart/` accessible via `/local/hello_smart/` URLs in Lovelace cards.
- **HACS Card Dependencies**: Third-party frontend cards from HACS that enhance the visual presentation (e.g., mushroom cards, gauge cards, vehicle diagram cards).

## Assumptions

- Entity IDs follow the pattern `{domain}.cm590_hc11_performance_4wd_rhd_apac_{key}` based on the current vehicle's model_name. Users with different vehicles will need to adjust entity IDs.
- The HA instance uses a dark theme or the dashboard is designed to look good on both light and dark themes (dark-first design).
- HACS is the preferred card distribution mechanism, but a standard-cards-only fallback ensures the dashboard works without HACS.
- The vehicle image investigation may reveal no extractable assets from the APK; the spec accounts for this with fallback strategies.
- The dashboard targets a single vehicle. Multi-vehicle support (parameterized entity IDs) is out of scope for this feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user opening the dashboard can determine the vehicle's battery level and estimated range within 2 seconds of page load.
- **SC-002**: All 7 card groups (hero, lock/security, windows, tyres, battery/range, charging, service) are visible on a single dashboard view without requiring navigation to sub-pages.
- **SC-003**: All interactive controls (lock toggle, charging switch, SOC slider, close-windows button, time pickers) are functional and trigger the corresponding integration commands.
- **SC-004**: The dashboard renders correctly on both mobile (375px width) and desktop (1920px width) viewports.
- **SC-005**: The dashboard supports dark themes with no unreadable text, invisible icons, or broken contrast.
- **SC-006**: Vehicle image is displayed on the hero card — either color-matched from APK assets or as a generic fallback silhouette.
- **SC-007**: Tyre pressure/temperature data is displayed in a spatial layout matching the physical wheel positions of the vehicle (not just a flat list).
- **SC-008**: Open doors and windows are visually distinguishable from closed ones through color, icon, or diagram changes.
