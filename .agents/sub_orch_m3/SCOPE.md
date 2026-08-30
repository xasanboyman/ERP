# Scope: Milestone 3 — Frontend Personal Center Connected Devices UI (R1)

## Mission
Implement the "Connected Devices" section in Personal Center (`http://localhost:4000/#/personal/personal-center`) in `Front/src/views/Personal/PersonalCenter.vue` (or equivalent personal center component) with a QR code generator for device pairing, device list display, and device revocation functionality.

## Requirements (R1)
- Add "Connected Devices" section/tab in Personal Center.
- "Pair New Device" button: calls `POST /api/device/pair-token`, receives token & `qr_payload`, renders QR code (using canvas/SVG QR generator or library) alongside device pair instructions.
- Connected Devices List: calls `GET /api/device/list`, renders device name, pairing timestamp, status, and last active time.
- Device Revocation: "Revoke" button calls `DELETE /api/device/revoke/{device_id}`. On success, updates the device status in UI and removes/invalidates device token.

## Target Files
- `Front/src/views/Personal/PersonalCenter.vue`
- Components/utilities created or modified under `Front/src/components/` or `Front/src/api/`
