# Laravel Backend Parity Analysis Handoff Report

## 1. Observation

This analysis is based on the source code of the Laravel backend situated at `/home/xasanboy/Knittix-new`. Below are specific direct observations of files, schemas, and configurations:

### Routing Configuration
- **API Entrypoint (`routes/api.php`)**:
  - Line 6-27: Defines versioned API routes under `/v1` prefix. Only status and dummy/placeholder QR scan endpoints are present:
    ```php
    Route::prefix('v1')->group(function () {
        Route::get('/status', function () { ... });
        Route::post('/qr/scan', function (Request $request) { ... });
    });
    ```
- **Mobile Web App (`routes/mobile.php`)**:
  - Line 37: `Route::get('/login', [AuthenticatedSessionController::class, 'create'])->name('login');`
  - Line 40: `Route::post('/login', [AuthenticatedSessionController::class, 'store'])->name('login.store');`
  - Line 57: `Route::get('/tasks', TaskWorkspaceController::class)->name('tasks.index');`
  - Line 58: `Route::get('/tasks/{taskUuid}', [TaskExecutionController::class, 'show'])->name('tasks.show');`
  - Line 59: `Route::post('/tasks/{taskUuid}/execute', [TaskExecutionController::class, 'store'])->name('tasks.execute');`
  - Line 60-63: Endpoints for execution history `/history`, `/history/{executionUuid}`, and archiving.
- **Main ERP Web Application (`routes/web.php`)**:
  - Defines admin/backoffice web pages using Livewire components and Laravel controllers.
  - Line 112-304: Scoped endpoints under middleware matrix `['auth', EnsureSupportImpersonationIsActive::class, 'verified', EnsureActiveUser::class, EnsureUserBelongsToCompany::class, 'access.matrix']` including `/products`, `/cutting`, `/techmaps`, `/qr`, `/staff`.

### Database Schema Migrations
- **Users Table Modifications (`database/migrations/2026_03_16_170000_prepare_users_for_staff_accounts.php`)**:
  - Line 16-24 adds columns: `first_name`, `last_name`, `position` (job title), `is_active` (boolean default true), `must_bind_email` (boolean default false), `created_by` (foreign key to users table), and `last_login_at`.
- **Cutting Orders Table (`database/migrations/2026_03_15_123500_create_cutting_orders_tables.php`)**:
  - Line 11-22: `cutting_orders` columns include `id`, `uuid` (unique), `company_id`, `order_number`, `project`, `order_name`, `total_quantity`, and timestamps.
  - Line 24-40: `cutting_order_items` columns include `id`, `uuid` (unique), `cutting_order_id`, `company_id`, `product_id`, `article`, `name`, `color`, `sizes`, `photo`, `quantity`, `position`.
- **Cutting Executions Table (`database/migrations/2026_03_26_110000_create_cutting_executions_table.php`)**:
  - Line 11-44: `cutting_executions` columns include `id`, `uuid` (unique), `company_id`, `created_by`, `updated_by`, `cutting_order_id`, `cutting_order_item_id`, `spread_sequence`, `spread_year`, `position_display_id`, `order_number`, `project`, `product_code`, `product_name`, `article`, `color`, `sizes`, `photo`, `spread_width`, `spread_length`, `fabric_density`, `layers_count`, `fabric_consumptions` (json), `size_breakdown` (json), `comments`, `total_quantity`.
- **Workers Table (`database/migrations/2024_03_10_000004_create_workers_table.php` & `2026_04_30_090000_add_employee_code_to_workers_table.php`)**:
  - `workers` columns include `id`, `company_id`, `employee_code` (unique, string(6)), `full_name`, `last_name`, `first_name`, `middle_name`, `position`, `phone`, `telegram`, `contact_details`, `description`, `photo`, and timestamps.
- **QR Codes Table (`database/migrations/2024_03_10_000005_create_qr_codes_table.php`)**:
  - `qr_codes` columns include `id`, `company_id`, `worker_id` (nullable), `unique_code` (unique), `status` (default 'created'), `metadata` (json), and timestamps.

### Model Behaviors & State Logic
- **`User` Model (`app/Models/User.php`)**:
  - Generates UUID automatically on creation.
  - Lowercases and trims `login` and `email` on save (Line 34-37).
  - Automatically compiles `name` from `first_name` and `last_name` on save (Line 38-43).
- **`Worker` Model (`app/Models/Worker.php`)**:
  - Automatically generates a unique 6-digit `employee_code` on creation (Line 190-199).
  - Automatically compiles `full_name` from `last_name`, `first_name`, and `middle_name` on save (Line 25-35).
- **`CuttingOrder` Model (`app/Models/CuttingOrder.php`)**:
  - Automatically resolves `order_year` and `order_sequence` (unique incremental value per company per year) (Line 407-451).
  - Implements statuses: `created`, `in_production`, `in_progress`, `completed`, `cancelled`, `partially_shipped`, `shipped`.
  - Dynamically calculates the status via `automaticStatus()` based on its items' statuses (Line 255-326).
- **`QrCode` Model (`app/Models/QrCode.php`)**:
  - Automatically generates `unique_code` on creation using `Str::ulid()`.

---

## 2. Logic Chain

To establish baseline API parity for a Laravel-equivalent backend:

1. **Entities & Identifiers**:
   - Every major model entity (Users, Cutting Orders, Items, Executions, Tasks, QR Codes) is identified in business APIs using a generated standard identifier: `uuid` (UUID v4) for users/orders/executions, `employee_code` (6-digit unique string) for workers, and `unique_code` (ULID) for QR codes.
   - Database schemas should reflect these identifier formats and generate them automatically at the database or model-booting level.

2. **Automated Sequence & Display IDs**:
   - Parity requires custom sequence tables or locks.
   - For example, `CuttingOrder` uses a `cutting_order_sequences` table containing `scope_key` (`company:<id>:year:<year>`) to safely lock and increment the `next_sequence`, formatting it as a padded 5-digit string (e.g. `00001`).
   - For `Product`, `product_code_sequences` table behaves similarly, producing sequential 5-digit codes.

3. **Status Transitions & Aggregation**:
   - Order-level statuses (e.g. `CuttingOrder::status`) must not be directly written by clients arbitrarily. They depend on item and execution state aggregation.
   - Specifically, if all items are cancelled, the order is `cancelled`. If all items are completed/shipped, the order is `completed`. If there is any work-in-progress, it transitions to `in_progress`.

4. **Mobile Workspace Authorization**:
   - Authenticated sessions in the mobile workspace must check `can_use_mobile_workspace` and `is_active` along with the company association.
   - In Laravel, this checks `MobileWorkspaceAccessService::canEnter` which allows super-users (`accessRole->is_super`) or users with explicit `can_use_mobile_workspace` permissions.

---

## 3. Caveats

- **Web ERP Controllers**: The main backoffice/admin interface in Knittix is built primarily with Livewire components inside `app/Livewire/Pages`. These do not expose traditional REST API endpoints, so establishing API parity requires rebuilding them as structured REST APIs based on the database state and transaction operations.
- **External QR Scan**: The QR scan endpoint `/v1/qr/scan` defined in `api.php` is explicitly disabled (returning a 501 Unimplemented status). Therefore, it should not be treated as part of the current active API surface unless device authentication is enabled.

---

## 4. Conclusion

To achieve Laravel parity, an ERP backend must implement the following schemas and behaviors:

### Target Database Models & Field Layouts
- **User**:
  - Primary identifier for API: `uuid` (UUID v4).
  - Key attributes: `login` (case-insensitive), `email` (case-insensitive), `is_active` (bool), `can_use_mobile_workspace` (bool), `worker_id` (foreign key to Workers).
- **Worker (Employee)**:
  - Primary identifier: `employee_code` (unique, generated 6-digit random string).
  - Key attributes: `full_name` (compiled last+first+middle), `salary`, `hours_per_day`, `days_per_month`.
- **Cutting Order**:
  - Primary identifier: `uuid`.
  - Sequential Display ID: `order_sequence` (padded 5-digit number scoped to company and year).
  - Key attributes: `status` (auto-calculated from child items), `responsible_user_ids` (json array).
- **Cutting Execution (Nastil)**:
  - Primary identifier: `uuid`.
  - Key attributes: `spread_sequence`, `spread_year`, `total_quantity`, `fabric_consumptions` (json), `size_breakdown` (json).
- **QR Code**:
  - Primary identifier: `unique_code` (ULID).
  - Key attributes: `worker_id` (assignee), `status` (created, printed, scanned, assigned, replaced, archived), `metadata` (json snapshot of order and execution values).

### Endpoints
- **Mobile Auth**: `POST /mobile/login` using `login`/`email` and `password`, validating active status and mobile permissions.
- **Mobile Task Workspace**: `GET /mobile/tasks` returning available cutting tasks assigned to or visible to the authenticated user.
- **Task Execution**: `POST /mobile/tasks/{taskUuid}/execute` recording execution metrics (worker, quantity) under transactional constraints.

---

## 5. Verification Method

To verify the parity setup, perform the following steps:

1. **Verify Database Seed & Schemas**:
   Inspect the DB migration files and check the presence of constraint indexes, sequence tables (`cutting_order_sequences`, `product_code_sequences`), and UUID columns.
2. **Execute Backend Tests**:
   Run the PHPUnit test suite:
   ```bash
   vendor/bin/phpunit
   ```
   Alternatively, run the dedicated test scripts located in the project root:
   ```bash
   php test_cutting_users.php
   ```
3. **Invalidation Conditions**:
   - Unique code generation: check that creating a `Worker` without `employee_code` generates a 6-digit unique value. Check that creating a `User` or `CuttingOrder` populates a UUID.
   - Status updates: verify that changing the status of a `CuttingOrderItem` triggers a cascade updating the parent `CuttingOrder`'s status.
