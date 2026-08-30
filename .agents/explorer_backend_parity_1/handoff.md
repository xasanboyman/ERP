# Backend Parity Report: FastAPI vs Laravel

This report details the parity analysis between the FastAPI backend (`/home/xasanboy/ERP/Back`) and the Laravel backend (`/home/xasanboy/Knittix-new`).

---

## 1. Observation

### A. Cutting Orders & `responsible_user_ids`
#### FastAPI Implementation
* **Route definitions:** In `app/routers/cutting.py`:
  * Line 114: `@router.get("/cutting/order/list")`
  * Line 164: `@router.post("/cutting/order/save")`
* **Model definition:** In `app/models.py`, lines 168–179:
  ```python
  class CuttingOrder(Base):
      __tablename__ = "cutting_orders"
      id = Column(String, primary_key=True, index=True)
      order_number = Column(String, unique=True, index=True)
      ...
      responsible_user_ids = Column(JSON, default=list)
  ```
* **Schema definition:** In `app/schemas.py`, lines 259–283:
  ```python
  class CuttingOrderCreate(BaseModel):
      id: Optional[str] = None
      order_number: str
      ...
      responsible_user_ids: Optional[List[str]] = []
      status: Optional[str] = "created"
      items: List[CuttingOrderItemCreate]

  class CuttingOrderResponse(BaseModel):
      id: str
      order_number: str
      ...
      responsible_user_ids: List[str]
      status: str
      total_quantity: int
      createTime: str
      items: Optional[List[CuttingOrderItemResponse]] = []
  ```
* **CRUD operations:** In `app/crud.py`, lines 366–420, `create_cutting_order` maps `order.responsible_user_ids` (list of strings/usernames) directly to the database column `responsible_user_ids`. SQLAlchemy automatically serializes/deserializes it from/to JSON format in SQLite.

#### Laravel Implementation
* **Model definition:** In `app/Models/CuttingOrder.php`, lines 41–48:
  ```php
  protected $casts = [
      ...
      'responsible_user_ids' => 'array',
      ...
  ];
  ```
* **Validation & decoding:** In `app/Http/Controllers/CuttingOrderController.php`, lines 1344–1352 (validation) and lines 2136–2149 (`decodeResponsibleUserIds`):
  ```php
  'responsible_user_ids' => ['nullable', 'array'],
  'responsible_user_ids.*' => [
      'integer',
      Rule::exists('users', 'id')->where(...)
  ],
  ```
  ```php
  protected function decodeResponsibleUserIds(mixed $value): array
  {
      if (is_string($value)) {
          $decoded = json_decode($value, true);
          $value = is_array($decoded) ? $decoded : [];
      }
      return collect(is_array($value) ? $value : [])
          ->map(static fn ($id) => (int) $id)
          ->filter(static fn (int $id) => $id > 0)
          ->unique()
          ->values()
          ->all();
  }
  ```
* **Parity Difference:** FastAPI uses a list of **string usernames** (since FastAPI users are represented by string usernames), whereas Laravel uses a list of **integer IDs** (foreign keys targeting the auto-incrementing `id` column of the `users` table).

---

### B. Processes (CuttingProcess)
* **FastAPI:**
  * Model definition: `Column(JSON)` field named `stages` in `CuttingProcess` class (directly storing the JSON representation of the stage details/ids).
  * No separate pivot tables.
  * Fields: `id` (String), `name` (String), `remark` (Text, nullable), `stages` (JSON), `createTime` (String).
* **Laravel:**
  * Model definition: `stages()` belongs-to-many relationship using pivot table `cutting_process_stage`.
  * Fields: `id`, `company_id`, `created_by`, `updated_by`, `process_number`, `name`, `description` (mapped to `remark` in FastAPI), `status` ('active', 'archived').
  * Pivot fields: `sort_order`, `description`, `price_sum`, `duration_seconds`, `responsible_user_ids`.

---

### C. Stages (CuttingStage)
* **FastAPI:**
  * Fields: `id` (String), `name` (String), `is_system` (Integer, 0 or 1), `price` (Float, corresponding to `price_sum`), `duration` (Integer, corresponding to `duration_seconds`), `createTime` (String).
  * No user relationships are defined on the stage table level.
* **Laravel:**
  * Fields: `id`, `company_id`, `created_by`, `updated_by`, `stage_number`, `name`, `description`, `price_sum` (decimal), `duration_seconds` (integer), `status` ('active', 'archived'), `is_system` (boolean).
  * Many-to-many relationship with `User` via the `cutting_stage_user` pivot table representing responsible users.

---

### D. Salary
* **FastAPI:**
  * Model: `Salary` table.
  * Fields: `id` (String), `workerId` (String), `baseSalary` (Float), `allowance` (Float), `deduction` (Float), `netSalary` (Float), `payDate` (String), `status` (String, default "pending"), `remark` (Text).
  * Endpoints: POST `/salary/save`, POST `/salary/payout`, GET `/salary/list`. Real records are created, persisted, and updated in the SQLite database.
* **Laravel:**
  * Model: **No `Salary` model or database table exists**.
  * Mechanism: The payroll is generated on the fly via a Livewire component (`StaffPayrollCreate` / `StaffPayrollIndex`) by reading timesheets (`StaffTimesheet`), manual outputs (`StaffOutput`), cutting executions (`CuttingExecution`), QR code scans (`QrCode`), and staff adjustments (`StaffAdjustment`). It computes wages dynamically:
    `actual_salary = (Worker.salary / (Worker.days_per_month * Worker.hours_per_day)) * actual_hours`

---

### E. Workers
* **FastAPI:**
  * Model fields: `id` (String), `name` (String), `account` (String, unique), `email` (String), `phone` (String), `role` (String), `departmentId` (String, ForeignKey to departments), `hireDate` (String), `status` (Integer: 1 = active, 0 = suspended), `baseSalary` (Float), `remark` (Text).
  * Simpler model with no soft deletes or detailed personal info.
* **Laravel:**
  * Model fields: `id`, `company_id`, `employee_code`, `full_name`, `last_name`, `first_name`, `middle_name`, `date_of_birth`, `gender`, `department` (String), `position` (String), `salary` (Decimal), `hours_per_day` (Decimal), `days_per_month` (Integer), `phone`, `telegram`, `contact_details`, `description`, `photo`, timestamps, soft deletes (`deleted_at`).

---

### F. Products
* **FastAPI:**
  * Model fields: `id` (String), `productName` (String), `SKU` (String, unique), `category` (String), `price` (Float), `cost` (Float), `quantityInStock` (Integer), `status` (Integer: 1 = in stock, 0 = out of stock), `remark` (Text), `createTime` (String).
* **Laravel:**
  * Model fields: `id`, `company_id`, `created_by`, `updated_by`, `parent_product_id` (hierarchical variants support), `product_code`, `variant_index`, `variant_signature`, `variant_overrides` (JSON), `name` (maps to `productName`), `article` (maps to `SKU`), `color`, `barcode`, `price` (Decimal), `currency`, `unit`, `product_group_id`, `comments` (maps to `remark`), `photo`, `archived_at` (timestamp), `characteristics` (JSON), timestamps, soft deletes.

---

### G. Server Startup Verification
* **Command run:** `cd /home/xasanboy/ERP/Back && ./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8089`
* **Log Output:**
  ```
  INFO:     Started server process [24500]
  INFO:     Waiting for application startup.
  INFO:     Application startup complete.
  INFO:     Uvicorn running on http://127.0.0.1:8089 (Press CTRL+C to quit)
  ```
* **Result:** No syntax errors, import errors, or missing routes were encountered. The app successfully binds and listens.

---

## 2. Logic Chain

1. **Responsible User IDs Parity:**
   * *Observation 1:* FastAPI schemas specify `responsible_user_ids: List[str]` where elements are string usernames.
   * *Observation 2:* Laravel validator enforces `responsible_user_ids.*` to be `integer` and exist in `users.id`.
   * *Inference:* FastAPI correctly serializes list of string usernames, matching its internal database user system (`User.username`). Laravel correctly serializes list of integer user IDs. This is a functional disparity to note when synchronizing datasets.
2. **Database Column Types & Relationships:**
   * *Observation 3:* FastAPI uses SQLite with SQLAlchemy `Column(JSON)` to store list structures inline (e.g. `CuttingProcess.stages`).
   * *Observation 4:* Laravel uses relational pivot tables (e.g. `cutting_process_stage`).
   * *Inference:* FastAPI routes do not require relational joins to retrieve child items (stages), resolving them directly via serialization.
3. **Salary Management Difference:**
   * *Observation 5:* FastAPI router `app/routers/salary.py` handles persistent records on a `salaries` table.
   * *Observation 6:* Laravel component `StaffPayrollCreate.php` performs dynamic calculations on-the-fly and holds no dedicated `Salary` database table.
   * *Inference:* FastAPI persists historical payout state directly, whereas Laravel maintains dynamically aggregated views of outputs, timesheets, and adjustments.

---

## 3. Caveats
* The front-end interaction behavior was not verified. It is assumed the frontend adapts to payload differences (e.g., using `username` strings instead of `id` integers).
* Under Code-Only constraints, we did not execute external HTTP requests to test API integrations.

---

## 4. Conclusion
* **Parity Status:** FastAPI has functional parity at the high-level API endpoint structure, but exhibits schema field name differences (e.g. `productName` vs `name`, `SKU` vs `article`) and structural schema differences (e.g. inline JSON `stages` in processes instead of a pivot table, and a dedicated `salaries` DB table instead of dynamic runtime payroll logic).
* **Actionable Advice:** Keep the serialization format in mind when developing the frontend, as `responsible_user_ids` expects string usernames in the FastAPI backend instead of integer IDs.

---

## 5. Verification Method

### How to Start the FastAPI Server
Run the following commands in your terminal:
```bash
cd /home/xasanboy/ERP/Back
./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### How to Test the Endpoints
You can use `curl` or any API testing client to interact with the endpoints.

#### 1. Retrieve Cutting Orders list:
```bash
curl -X GET http://127.0.0.1:8000/cutting/order/list
```

#### 2. Save a Cutting Order:
```bash
curl -X POST http://127.0.0.1:8000/cutting/order/save \
     -H "Content-Type: application/json" \
     -d '{
       "order_number": "CO-TEST-1001",
       "project": "Test Project",
       "order_name": "Test Order",
       "document_date": "2026-07-07",
       "responsible_user_ids": ["admin", "testuser"],
       "status": "created",
       "items": [
         {
           "productId": "PROD001",
           "quantity": 150,
           "category": "T-shirt",
           "color": "Black",
           "code": "TS-BLK"
         }
       ]
     }'
```
