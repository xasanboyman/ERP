## 2026-07-07T02:04:16Z
Role: Facade Fix Worker
Working directory: /home/xasanboy/ERP/.agents/teamwork_preview_worker_fix_facade
Task:
You must implement the fix for the department user save and delete facade endpoints.

### MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

### Implementation Requirements:
1. **Schemas (`Back/app/schemas.py`)**:
   Add models to parse the incoming department-user payload, supporting both nested department objects and flat paths (e.g. `department` or `department.id` or nested dictionary). For instance, define `DepartmentUserDept` and `DepartmentUserSave` schemas.

2. **CRUD (`Back/app/crud.py`)**:
   - Implement `save_department_user(db: Session, user_data: schemas.DepartmentUserSave)`:
     - Resolve the department ID from the request.
     - Resolve role names/IDs (mapping ID "1" to "admin" and "2" to "worker" or generic worker defaults).
     - Query if the user exists by `id`. If they do, update their `username`, `email`, `department_id`, `role`, and `roleId`.
     - If the user does not exist, create a new user in the database. Generate a default password hash (e.g. for default password "123456") using the existing hashing utilities context.
     - Commit the transaction.
   - Implement `delete_department_users(db: Session, user_ids: List[int])` to delete the users by their numeric IDs in a bulk delete statement.

3. **Routers (`Back/app/routers/department.py`)**:
   - Rewrite `@router.post("/department/user/save")` to use the dynamic `crud.save_department_user`.
   - Rewrite `@router.post("/department/user/delete")` to parse a list of numeric IDs (handling both single string/int and lists), call `crud.delete_department_users`, and return success.
   - Update `/department/users` listing endpoint to filter by department `id` query parameter (representing the selected department) and return a paginated user list containing usernames, emails, and creation times.

4. **Seeding (`Back/seed.py`)**:
   Update `seed_database` in `/home/xasanboy/ERP/Back/seed.py` so that user creation assigns departments (e.g., `department_id="DEPT-HQ"` for admin and `department_id="DEPT-RD"` for test), and seed another test user to verify department listing.

5. **Test Runner**:
   After applying the fixes, run `run_e2e_tests.sh` to verify that everything builds and all 60 tests pass. Also, verify manual functionality of the newly dynamic endpoints using curl or dynamic API tests.

6. Write a detailed handoff report in `/home/xasanboy/ERP/.agents/teamwork_preview_worker_fix_facade/handoff.md` showing pytest execution output and endpoint curl check verification.
7. Call send_message when complete.
