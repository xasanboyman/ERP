# Scope: Milestone 4 — Backend Sales Push & Mobile Checkout API (R2 & R3)

## Architecture & Requirements
- Target Directory: `Back/app/`
- Target Router: `Back/app/routers/sales.py` (or `Back/app/routers/pos.py`)
- Database Models, Schemas, CRUD operations for Sales Push and Mobile Checkout.
- Device Token Security: Mobile endpoints must use `get_current_device_token` dependency from `Back/app/auth.py`.

## Detailed Requirements
1. **Computer Sale Push**:
   - `POST /api/sales/push-pc-sale`: PC sends sale push payload to cash register.
   - `GET /api/sales/pending-pushes`: Fetch list of pending sales pushed from PCs.
   - `POST /api/sales/respond-push`: Cashier accepts or declines a push payload (Accept/Decline).
   - `GET /api/sales/push-payload/{push_id}`: Fetch detailed payload for a specific push ID.

2. **Mobile Standalone Checkout**:
   - `POST /api/sales/phone-checkout`: Mobile phone completes checkout directly (scanning items, quantity input, full/debt payments, cash/card).
   - Enforce `get_current_device_token` dependency for authentication and authorization of mobile device.

3. **Database & Logic**:
   - Updates inventory, records transaction, creates debt if payment < total, handles payment splits (cash vs card), updates customer debt records if applicable.

## Milestone Status
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M4 | Sales Push & Mobile Checkout | DB Models, Schemas, CRUD, FastAPI Endpoints, Tests | Auth, Inventory DB | IN_PROGRESS |
