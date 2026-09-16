# Knit ERP Changelog

All notable changes to **Appix ERP** are documented in this file.

## [1.0.0] - 2026-09-01

### Added
- **AI Voice Assistant**: Rebranded to Appix ERP AI with dual visualizer modes (radial particle starburst and symmetric audio waveform) and 1.2s voice barge-in cancellation.
- **Role-Based Access Control (RBAC)**: Fine-grained permission mapping across all routes, sidebar menus, and backend AI tool calling functions.
- **Mobile QR/Barcode Dual POS Handover Engine**:
  - Standalone mobile scanner view (`/mobile/scanner`).
  - Computer Sale mode with WebSocket/Polling push notification alert modal and 1-click cart pre-fill.
  - Standalone Phone Sale checkout with Cash, Card, and Debt (Nasiya) support.
  - Secure device token pairing with QR code generator in Personal Center and instant revocation.
- **Sales POS & Nasiya Debt Engine**: Debtors list, debtor details, installment debt repayment receipts, and multi-unit product conversions.
- **Textile & Garment Production (Raskroy)**: Cutting orders with size breakdowns, multi-stage pipelines, and automated QR code bundle generation.
- **National MXIK Classifier Sync**: Indexed database with 411,022+ national commodity records.
- **Vercel Serverless & Cloud PostgreSQL Support**: Universal database migration script (`migrate_to_postgres.py`) and edge serverless API router.
