# Handoff Report: Milestone 3 - Frontend Personal Center Connected Devices UI (R1)

## 1. Observation

### 1.1 Scope Document Findings
- **File**: `/home/xasanboy/ERP/.agents/sub_orch_m3/SCOPE.md`
- **Requirements (R1)**:
  - Add "Connected Devices" section/tab in Personal Center (`http://localhost:4000/#/personal/personal-center`).
  - "Pair New Device" button: calls `POST /api/device/pair-token`, receives token & `qr_payload`, renders QR code alongside device pairing instructions.
  - Connected Devices List: calls `GET /api/device/list`, renders device name, pairing timestamp, status, and last active time.
  - Device Revocation: "Revoke" button calls `DELETE /api/device/revoke/{device_id}`. On success, updates device status in UI and revokes token.

### 1.2 Frontend Structure Findings
- **Personal Center Root View**:
  - **File**: `/home/xasanboy/ERP/Front/src/views/Personal/PersonalCenter/PersonalCenter.vue` (159 lines)
  - **Route**: Defined in `/home/xasanboy/ERP/Front/src/router/index.ts` lines 45-66 (`/personal/personal-center`).
  - **Current Template Layout**:
    - Left side: `<ContentWrap title="Shaxsiy ma'lumotlar" class="w-400px">` displaying avatar, username, real name, phone, email, and roles.
    - Right side: `<ContentWrap title="Asosiy ma'lumotlar" class="flex-[3] ml-20px">` wrapping `<ElTabs v-model="activeName">`.
    - Active tabs (lines 111-116):
      - Tab 1 (`first`): `<ElTabPane label="Asosiy ma'lumotlar" name="first">` with `<EditInfo :user-info="userInfo" />`
      - Tab 2 (`second`): `<ElTabPane label="Parolni o'zgartirish" name="second">` with `<EditPassword />`
- **Sub-components Directory**: `/home/xasanboy/ERP/Front/src/views/Personal/PersonalCenter/components/`
  - Existing files: `EditInfo.vue`, `EditPassword.vue`, `UploadAvatar.vue`.
- **Existing QR Code Component**:
  - **File**: `/home/xasanboy/ERP/Front/src/components/Qrcode/src/Qrcode.vue`
  - Reusable Vue 3 QR code component based on `qrcode` library (`qrcode: ^1.5.4` in `package.json`).
  - Accepts props: `text` (string/array), `width` (number), `logo` (string/object), `disabled` (boolean), `disabledText` (string).
- **UI Framework & Styling**:
  - Element Plus 2.9.2 (`ElTabs`, `ElTabPane`, `ElTable`, `ElTableColumn`, `ElButton`, `ElTag`, `ElDialog`, `ElForm`, `ElInput`, `ElMessage`, `ElMessageBox`, `ElPopconfirm`).
  - UnoCSS / Tailwind utility classes (`flex`, `w-full`, `justify-between`, `items-center`, `gap-4`).
  - Less styles (`<style lang="less" scoped>`).

### 1.3 Backend Endpoint & Data Contract Findings
- **Backend Device Router**: `/home/xasanboy/ERP/Back/app/routers/device.py`
  - `POST /api/device/pair-token`:
    - Body: `{ device_name: string, user_id?: number }`
    - Response structure:
      ```json
      {
        "code": 0,
        "message": "Device token created successfully",
        "data": {
          "pair_code": "STRING",
          "token": "STRING",
          "expires_at": "ISO_DATETIME",
          "device_name": "STRING",
          "user_id": 1,
          "qr_payload": "{\"token\": \"...\", \"device_name\": \"...\", \"user_id\": 1, \"pair_code\": \"...\", \"created_at\": \"...\"}",
          "created_at": "ISO_DATETIME"
        }
      }
      ```
  - `GET /api/device/list`:
    - Header: `Authorization: Bearer <token>`
    - Response structure:
      ```json
      {
        "code": 0,
        "message": "Success",
        "data": {
          "total": 1,
          "list": [
            {
              "id": 1,
              "user_id": 1,
              "device_name": "POS-Terminal-1",
              "token": "...",
              "pair_code": "...",
              "status": "active",
              "expires_at": "ISO_DATETIME",
              "created_at": "ISO_DATETIME",
              "last_used_at": "ISO_DATETIME"
            }
          ]
        }
      }
      ```
  - `DELETE /api/device/revoke/{device_id}`:
    - Path param: `device_id` (integer)
    - Response structure:
      ```json
      {
        "code": 0,
        "message": "Device token revoked",
        "device_id": 1,
        "data": { "id": 1, "status": "revoked" }
      }
      ```

---

## 2. Logic Chain

1. **Routing & Component Placement**:
   - The route `http://localhost:4000/#/personal/personal-center` maps directly to `Front/src/views/Personal/PersonalCenter/PersonalCenter.vue`.
   - The right panel in `PersonalCenter.vue` uses `<ElTabs v-model="activeName">` for tab switching.
   - Therefore, the cleanest and most modular way to add the "Connected Devices" section is to:
     a. Create a dedicated sub-component: `Front/src/views/Personal/PersonalCenter/components/ConnectedDevices.vue`.
     b. Add a 3rd tab (`name="third"`, `label="Ulangan qurilmalar"`) in `PersonalCenter.vue` referencing `<ConnectedDevices />`.

2. **API Layer Modularization**:
   - Currently, API calls are organized per domain under `Front/src/api/` (e.g., `login/index.ts`, `sales/index.ts`).
   - There is no `Front/src/api/device/` directory yet.
   - We should create `Front/src/api/device/index.ts` defining `getDeviceListApi()`, `createPairTokenApi()`, and `revokeDeviceApi()`.

3. **Connected Devices Component Design (`ConnectedDevices.vue`)**:
   - **State**:
     - `deviceList`: Ref array of `DeviceItem`
     - `loading`: Boolean loading flag for table
     - `pairDialogVisible`: Boolean flag for pair dialog
     - `deviceName`: Ref string for pair device input (default: "Mobil POS Terminal")
     - `pairData`: Ref object holding response from `createPairTokenApi` (including `qr_payload`, `pair_code`, `expires_at`)
     - `pairLoading`: Boolean loading flag when generating QR token
   - **Operations**:
     - `fetchDevices()`: Calls `getDeviceListApi()`, extracts `res.data.list` or `res.list`, updates `deviceList`. Called on component `onMounted()`.
     - `handlePairDevice()`: Validates `deviceName`, calls `createPairTokenApi({ device_name: deviceName.value })`, stores response in `pairData`, and shows QR code inside `ElDialog`.
     - `handleRevokeDevice(device)`: Displays `ElMessageBox.confirm("Qurilmani bekor qilishni tasdiqlaysizmi?", "Eslatma")`. On confirmation, calls `revokeDeviceApi(device.id)`, shows success notification `ElMessage.success("Qurilma muvaffaqiyatli o'chirildi")`, and refreshes `fetchDevices()`.
   - **UI Elements**:
     - Top bar with title / description and a "Yangi qurilmani ulash" button (`ElButton type="primary"`).
     - `ElTable` displaying:
       - Device Name (`device_name`) with mobile/device icon
       - Pair Code (`pair_code`)
       - Status (`status`): `ElTag type="success"` for 'active' ("Faol"), `ElTag type="danger"` for 'revoked' ("Bekor qilingan")
       - Pairing Time (`created_at` formatted)
       - Last Active Time (`last_used_at` formatted or "-")
       - Action column with "Bekor qilish" (Revoke) `ElButton type="danger" link`.
     - `ElDialog` for QR code display:
       - Displays `<Qrcode :text="pairData.qr_payload" :width="220" />`
       - Displays manual pair code text: `pairData.pair_code`
       - Clear instruction steps: "1. Mobil POS ilovasini oching. 2. QR kodni skanerlang yoki juftlik kodini kiriting."
       - Button to close and refresh list.

---

## 3. Caveats

- **Mock vs Live Backend**: If running frontend dev server in isolated mock mode, network requests to `/api/device/*` may need to fall back or be mocked by Vite mock plugin if backend server is not running locally. However, backend router `Back/app/routers/device.py` is fully implemented and tested.
- **Language/i18n**: The Personal Center UI strings in `PersonalCenter.vue` are currently written in Uzbek ("Shaxsiy ma'lumotlar", "Asosiy ma'lumotlar", "Parolni o'zgartirish"). We recommend using Uzbek labels consistent with the existing page ("Ulangan qurilmalar", "Yangi qurilmani ulash", "Bekor qilish").

---

## 4. Conclusion

The "Connected Devices" section for Milestone 3 should be integrated cleanly into `PersonalCenter.vue` by creating:
1. `Front/src/api/device/index.ts` — API module for `/api/device/pair-token`, `/api/device/list`, and `/api/device/revoke/{device_id}`.
2. `Front/src/views/Personal/PersonalCenter/components/ConnectedDevices.vue` — Component containing device table, status badges, QR code pair modal (using `<Qrcode />`), and revocation handler.
3. `Front/src/views/Personal/PersonalCenter/PersonalCenter.vue` — Added `ElTabPane` for "Ulangan qurilmalar" (`name="third"`).

---

## 5. Verification Method

1. **File Inspection**:
   - Verify `Front/src/api/device/index.ts` exists and exports `getDeviceListApi`, `createPairTokenApi`, `revokeDeviceApi`.
   - Verify `Front/src/views/Personal/PersonalCenter/components/ConnectedDevices.vue` exists and imports `Qrcode` from `@/components/Qrcode`.
   - Verify `Front/src/views/Personal/PersonalCenter/PersonalCenter.vue` imports `ConnectedDevices` and renders `<ElTabPane label="Ulangan qurilmalar" name="third">`.
2. **Build / Type Check**:
   - Run `pnpm ts:check` or `npm run ts:check` in `Front/` to verify zero TypeScript errors.
   - Run `pnpm build:dev` in `Front/` to verify build succeeds.
3. **Runtime Invalidation**:
   - Navigate to `http://localhost:4000/#/personal/personal-center` in browser.
   - Click "Ulangan qurilmalar" tab.
   - Click "Yangi qurilmani ulash", enter device name, confirm QR code renders correctly.
   - Verify device appears in device list table.
   - Click "Bekor qilish" (Revoke) and verify status updates to 'revoked'.
