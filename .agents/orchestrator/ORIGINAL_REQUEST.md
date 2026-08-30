# Original User Request

## 2026-08-09T05:02:38Z

Implement a secure Mobile QR/Barcode scanning system for ERP with connected device token management in Personal Center, dual-mode sales (Mobile POS vs PC POS Push with Accept/Decline alert), and full transaction capabilities.

Working directory: /home/xasanboy/ERP
Integrity mode: development

## Requirements

### R1. Device Pairing, Token Authorization & Management (Personal Center)
- In http://localhost:4000/#/personal/personal-center, add a "Connected Devices" section with a QR code generator for device pairing.
- Store per-device access tokens tied to logged-in user account with strict backend role/permission checking for every scan request.
- Provide device revocation in Personal Center that destroys the token in DB. Invalid/revoked tokens redirect mobile scanner to re-pairing.

### R2. Mobile Dual Sales Modes (PC Sale vs Phone Sale)
- When opening mobile scanner view, provide 2 choices:
  - **Computer Sale Mode**: Scans items & amounts on phone, sends alert to PC.
  - **Phone Sale Mode**: Complete standalone POS terminal on phone (scanning, quantity, full/debt payments, cash/card).

### R3. PC POS Notification & Handover (`/sales/pos` — Yangi Sotuv)
- When "Computer Sale" is triggered from phone, send a real-time alert (Accept/Decline modal) to the PC.
- Upon pressing "Accept" on PC, automatically navigate/open http://localhost:4000/#/sales/pos (Yangi Sotuv / POS Kassa), pre-fill scanned items & quantities, allowing the cashier to continue editing/finalizing sale.

## Acceptance Criteria

### Security & Device Pairing
- [ ] Device token generated on PC personal center can be scanned and saved on mobile.
- [ ] Backend blocks requests from revoked or unauthenticated device tokens with forbidden status.
- [ ] Revoking a device in Personal Center invalidates it immediately on mobile.

### PC Sale Alert & Handover
- [ ] Scanned items from phone trigger Accept/Decline pop-up alert on active PC session.
- [ ] Pressing Accept opens /sales/pos (Yangi Sotuv) with all scanned items and amounts populated.
- [ ] Pressing Decline cancels the payload transfer and alerts phone.

### Mobile POS Terminal
- [ ] Phone Sale mode enables full POS workflow directly on mobile (scanning, amount input, debt/cash/card checkout).
