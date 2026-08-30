# BRIEFING — 2026-07-07T01:49:43Z

## Mission
Explore Laravel backend in Knittix-new to find model schemas, endpoints, and behaviors to establish API parity.

## 🔒 My Identity
- Archetype: Teamwork explorer
- Roles: Parity Reference Explorer
- Working directory: /home/xasanboy/ERP/.agents/teamwork_preview_explorer_exploration_3
- Original parent: 42cf058f-95f6-4f3b-b7c8-2dc92d58d438
- Milestone: Laravel backend parity analysis

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- Network mode: CODE_ONLY (No external API or web access)
- Write only to own folder (/home/xasanboy/ERP/.agents/teamwork_preview_explorer_exploration_3)

## Current Parent
- Conversation ID: 42cf058f-95f6-4f3b-b7c8-2dc92d58d438
- Updated: 2026-07-07T01:49:43Z

## Investigation State
- **Explored paths**:
  - `routes/api.php`, `routes/mobile.php`, `routes/web.php`
  - Models: `User`, `Worker`, `CuttingOrder`, `CuttingOrderItem`, `CuttingProcess`, `CuttingStage`, `CuttingTask`, `CuttingExecution`, `CuttingTaskExecution`, `QrCode`, `Techmap`, `TechmapItem`, `TechmapBinding`, `TechmapOperation`, `Product`
  - Services/Controllers: `QrGeneratorService`, `MobileAvailableTaskService`, `MobileWorkspaceAccessService`, `AuthenticatedSessionController`, `TaskWorkspaceController`, `TaskExecutionController`
  - Database Migrations: `0001_01_01_000000_create_users_table.php`, `2026_03_15_123500_create_cutting_orders_tables.php`, `2026_03_26_110000_create_cutting_executions_table.php`, `2026_03_28_111500_add_kanban_positions_to_cutting_orders_and_items_tables.php`, `2024_03_10_000004_create_workers_table.php`, `2026_04_14_170000_expand_workers_table_for_staff_cards.php`, `2026_04_30_090000_add_employee_code_to_workers_table.php`, `2024_03_10_000005_create_qr_codes_table.php`
- **Key findings**:
  - Laravel backend models, schemas, unique behaviors (e.g. sequence generation for cutting orders, product codes, tasks; status autocalculation).
  - Mobile web-based endpoints and middleware logic for authentication and task executions in the mobile workspace.
  - The QR code generation structure and metadata layout.
- **Unexplored areas**:
  - billing-related models (`CompanyWallet`, `CompanySubscription`, `CompanyWalletTransaction`)
  - details of staff payroll and timesheets
  - Livewire ERP web controllers / views (as they are not mapped as JSON API endpoints but form the core admin web UI)

## Key Decisions Made
- Analysed the schema definitions, relational integrity, business rules, and state machine transitions of the cutting order, worker, and QR code models.

## Artifact Index
- /home/xasanboy/ERP/.agents/teamwork_preview_explorer_exploration_3/handoff.md — Analysis & handoff report (planned)
