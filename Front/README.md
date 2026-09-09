# Apex ERP - Frontend Client

<div align="center">
  <img width="120" src="./public/logo.png" alt="Apex ERP Logo">
  <h1>Apex ERP (Enterprise Resource Planning & POS)</h1>
  <p><strong>Developed & Maintained by Hasanboy Abdulkhayev</strong></p>
</div>

---

## 📌 Overview

**Apex ERP** is a modern, high-performance web interface for enterprise inventory, textile & garment manufacturing tracking, point of sale (POS) checkout, and AI voice assistance.

- **Framework**: Vue 3 (Composition API, `<script setup lang="ts">`) + Vite 6 + TypeScript 5.7
- **UI Architecture**: Element Plus + UnoCSS + Iconify Icons + ECharts
- **State & Routing**: Pinia (persisted store) + Vue Router (Dynamic RBAC permission resolution)
- **Scanning**: HTML5 QR Code & ZXing multi-engine barcode integration
- **AI Interface**: Web Audio API real-time FFT visualizers with Google Gemini API & voice barge-in cancellation

---

## 🚀 Key Modules

1. **Point of Sale (POS) & Dual Mode Handover** (`/sales/pos`, `/mobile/scanner`):
   - Desktop fast POS cashier terminal with multi-payment channels (Naqd, Karta, O'tkazma, Nasiya).
   - Mobile barcode scanning terminal with real-time PC push notifications.
2. **Textile / Garment Manufacturing & Cutting** (`/cutting`):
   - Batch cutting orders with size breakdowns, multi-stage tracking, and printable QR bundle tickets.
3. **Warehouse & Inventory** (`/product/list`):
   - 411,000+ national MXIK classifier integration, multi-unit packaging conversion, stock alerts.
4. **Human Resources & Payroll** (`/hr`):
   - Worker directory, attendance timesheets, piece-rate output (*vyrabotka*), and net payroll generation.
5. **AI Voice Assistant** (`/ai-assistant`):
   - Voice interaction with bidirectional ERP function execution and animated particle canvas visualizer.

---

## 💻 Development & Build

### Prerequisites
- Node.js >= 18.0.0
- pnpm >= 9.0.0

### Quick Start
```bash
# Install dependencies
pnpm install

# Start development server
pnpm run dev

# Build for production
pnpm run build:pro

# Preview production build
pnpm run serve:pro
```

---

## 📄 License

MIT License © 2026-present Hasanboy Abdulkhayev.
