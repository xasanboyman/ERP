# Codebase Comparison & Frontend Plan Analysis

This report compares the reference Laravel backend (`/home/xasanboy/Knittix-new`) with the FastAPI backend (`/home/xasanboy/ERP/Back`) and details the plan for the frontend changes in `/home/xasanboy/ERP/Front`.

---

## 1. Backend Comparison: Laravel vs. FastAPI

### A. Cutting Orders Module

#### Reference Laravel Backend
* **Database Models:**
  * `App\Models\CuttingOrder`
    * Table: `cutting_orders`
    * Fields: `id`, `uuid`, `company_id`, `created_by`, `order_number` (string), `order_year` (int), `order_sequence` (int), `project` (string), `order_name` (string), `document_date` (datetime), `responsible_user_ids` (array JSON of user IDs), `status` (string), `status_locked` (boolean), `total_quantity` (integer), `kanban_position` (integer).
    * Handles auto-generation of sequence and year on creation (`booted` event).
    * Statuses: `created`, `in_production`, `in_progress`, `completed`, `cancelled`, `partially_shipped`, `shipped`.
    * Implements `refreshStatusFromExecutions()` to dynamically recalculate status based on quantities and tasks.
  * `App\Models\CuttingOrderItem`
    * Table: `cutting_order_items`
    * Fields: `cutting_order_id`, `product_id`, `article`, `name`, `color`, `sizes`, `photo`, `quantity`, `position`, `cutting_process_id`, `cutting_process_snapshot_name`, `cutting_process_snapshot_description`, `cutting_process_snapshot_stages` (JSON), `size_breakdown` (JSON), `material_consumptions` (JSON), `status`, `status_locked`, `kanban_position`.
    * Implements snapshots of the technical processes and stages.

#### FastAPI Backend
* **Database Models:**
  * `CuttingOrder` (`Back/app/models.py`)
    * Table: `cutting_orders`
    * Fields: `id` (String PK), `order_number` (String unique), `project` (String), `order_name` (String), `document_date` (String), `responsible_user_ids` (JSON, default list), `status` (String, default "created"), `total_quantity` (Integer), `createTime` (String).
    * Uses a simple random string generator for primary keys (`CO` + random digits).
  * `CuttingOrderItem` (`Back/app/models.py`)
    * Table: `cutting_order_items`
    * Fields: `id` (String PK), `orderId` (String FK), `productId` (String FK), `category` (String), `color` (String), `code` (String), `cuttingProcessId` (String FK), `quantity` (Integer), `size_breakdown` (JSON dict), `material_consumptions` (JSON list), `process_snapshot` (JSON list).

#### Functional Gaps (Cutting Orders)
1. **Sequence and Display ID Generation:** Laravel uses a year + company-scoped sequential integer sequence (from a locked table `cutting_order_sequences`) to format order IDs like `00001`. FastAPI uses random UUID substrings (`CO` + digits), which do not form a clean sequence.
2. **Dynamic Status Transitions:** Laravel dynamically calculates status (e.g. `shipped`, `partially_shipped`, `in_progress`, `completed`) by checking item completion and tasks execution counts. FastAPI only supports basic static string status setting.
3. **Audit History & Logs:** Laravel logs creations, updates (with exact changes), and deletions of cutting orders via polymorphic `ActivityLog` models. FastAPI only writes simple static action strings in `activity_logs`.
4. **Data Type Mismatches:** 
   * `responsible_user_ids` in Laravel contains integers (DB primary keys of users).
   * `responsible_user_ids` in FastAPI contains strings (usernames).

---

### B. Processes, Stages, Salary, Workers, and Products

| Module | Laravel (Reference) | FastAPI | Gaps & Parity Issues |
|---|---|---|---|
| **Processes** | `App\Models\CuttingProcess`<br>Pivot table: `cutting_process_stage` (with `sort_order`, `description`, `price_sum`, `duration_seconds`, `responsible_user_ids` override JSON). | `CuttingProcess`<br>Stores stages as a flat JSON list of stage objects or IDs in the `stages` column of the `cutting_processes` table. | **Major architectural gap:** Laravel uses a relational many-to-many join table with stage overrides per process. FastAPI stores a denormalized JSON array in a single column. |
| **Stages** | `App\Models\CuttingStage`<br>Fields: `price_sum` (decimal), `duration_seconds` (integer), `is_system` (boolean), `status` ('active'/'archived'), `stage_number` (int). Many-to-many relationship with users (`cutting_stage_user`). | `CuttingStage`<br>Fields: `price` (float), `duration` (integer), `is_system` (integer), `createTime` (string). No status or stage number fields. | Name mismatches: `price_sum` vs `price`, `duration_seconds` vs `duration`. Type mismatches: `is_system` boolean vs integer. Default responsible users mapping is absent in FastAPI. |
| **Salary** | Calculated dynamically in the UI (`StaffPayrollCreate`) based on workers' hours, attendance logs (`StaffTimesheet`), pieces produced (`StaffOutput`, task executions), and adjustments (`StaffAdjustment`). | Dedicated table `salaries` (`Salary` model).<br>Fields: `id`, `workerId`, `baseSalary`, `allowance`, `deduction`, `netSalary`, `payDate`, `status` (paid/pending), `remark`. | **Parity gap:** Laravel computes monthly payroll dynamically. FastAPI stores static flat records in the DB and uses a bulk `/salary/payout` endpoint to post static values. |
| **Workers** | `App\Models\Worker`<br>Fields: name split (`first_name`, `last_name`, `middle_name`), `salary` (decimal), `hours_per_day`, `days_per_month`, birthday, gender, photo, telegram. Soft deletes. | `Worker`<br>Fields: `id`, `name` (full name string), `account` (unique login name), `email`, `phone`, `role`, `departmentId`, `baseSalary`, `remark`, status. | Schema mismatches: split names vs single name, `salary` vs `baseSalary`, relational `departmentId` vs string `department` in Laravel. |
| **Products** | `App\Models\Product`<br>Fields: `name`, `article`, `color`, `barcode`, `price`, `unit`, `characteristics` (JSON), variants structure (`parent_product_id`), auto product codes. | `Product`<br>Fields: `productName`, `SKU`, `category`, `price`, `cost`, `quantityInStock`, `status`, `remark`. | Schema mismatches: `productName` vs `name`, `SKU` vs `article`/`product_code`, lack of variants support, units, colors, and barcodes in FastAPI. |

#### Backend API Endpoints (FastAPI)
* **Stages:** `/cutting/stage/list` (GET), `/cutting/stage/save` (POST), `/cutting/stage/delete` (POST).
* **Processes:** `/cutting/process/list` (GET), `/cutting/process/save` (POST), `/cutting/process/delete` (POST).
* **Salary:** `/salary/list` (GET), `/salary/save` (POST), `/salary/delete` (POST), `/salary/payout` (POST).
* **Workers:** `/worker/list` (GET), `/worker/save` (POST), `/worker/delete` (POST).
* **Products:** `/product/list` (GET), `/product/save` (POST), `/product/delete` (POST).

---

## 2. Frontend Analysis & Implementation Plan

### A. Cutting Orders Retrieval & Display
* **Location:** `/home/xasanboy/ERP/Front/src/views/Cutting/Cutting.vue`
* **Retrieval Method:** Calls `getOrderListApi()` from `@/api/cutting`. Local reactive search variables (`searchQuery.order_number` and `searchQuery.project`) filter the list locally client-side.
* **Table Columns:** `Buyurtma #` (`order_number`), `Buyurtma nomi` (`order_name`), `Loyiha` (`project`), `Hujjat sanasi` (`document_date`), `Jami miqdor` (`total_quantity`), `Holati` (`status`).

### B. Add/Edit Dialog & Form Structure
* **Dialog State:** Managed by reactive variables `dialogVisible`, `dialogType` ('add' or 'edit'), and `form` object.
* **Form Data Structure:**
  ```ts
  const form = reactive({
    id: '',
    order_number: '',
    project: '',
    order_name: '',
    document_date: '',
    responsible_user_ids: [] as string[],
    status: 'created',
    items: [] as any[]
  })
  ```
* **Fetch User List:** Can be retrieved using `getUserListApi` from `@/api/login/index.ts` which requests `/mock/user/list` (redirects to backend `/user/list` when mock is disabled).
* **Gaps:** The current add/edit form dialog does not have any select/picker UI element to assign or modify `responsible_user_ids`! It needs a multi-select dropdown for users.

### C. Overlapping Avatar Stack Implementation
To show the overlapping responsible users (stacking avatar elements with tooltip on hover) inside the table:

1. **Import the `<Avatars>` component and default avatar image:**
   ```ts
   import { Avatars } from '@/components/Avatars'
   import avatarImg from '@/assets/imgs/avatar.jpg'
   ```

2. **Map the `responsible_user_ids` usernames list into `AvatarItem` format:**
   ```ts
   const getAvatarData = (responsibleUserIds: string[] | undefined) => {
     return (responsibleUserIds || []).map((username) => ({
       name: username,
       url: avatarImg
     }))
   }
   ```

3. **In the table template, add the column:**
   ```html
   <el-table-column label="Mas'ullar" width="180">
     <template #default="scope">
       <Avatars :data="getAvatarData(scope.row.responsible_user_ids)" :max="3" size="small" />
     </template>
   </el-table-column>
   ```

4. **Style override to ensure the overlap is >50%:**
   The Element Plus small avatar size is `24px`. To overlay the second over the first by >50%, we style the sibling margin-left to be negative (e.g. `-16px` margin-left, representing `66.7%` overlap):
   ```css
   <style scoped>
   :deep(.el-avatar + .el-avatar) {
     margin-left: -16px !important;
   }
   </style>
   ```

---

## 3. Database Configurations & Seeds

* **Laravel:** Relies on migrations under `database/migrations/` and seeders under `database/seeders/` run via Artisan commands.
* **FastAPI:** Relies on SQLAlchemy models in `Back/app/models.py`. The tables are automatically generated by `Base.metadata.create_all(bind=engine)` inside `Back/app/main.py` when the app is initialized. The seed data is loaded via a standalone script `Back/seed.py` which drops and refills the SQLite `erp.db` file.

---

## 4. Test Suite Configuration
* **Frontend:** No test scripts are defined in `package.json`. No testing library is installed.
* **FastAPI:** No tests directory or files exist. No testing libraries (e.g., `pytest`) are specified in `requirements.txt`.
* **Laravel:** Contains a PHPUnit test suite located in `tests/`. Tests can be executed using:
  ```bash
  php artisan test
  # or
  ./vendor/bin/phpunit
  ```
