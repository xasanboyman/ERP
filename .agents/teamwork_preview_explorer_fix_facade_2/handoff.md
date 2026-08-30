# Handoff Report — Facade Fix Explorer 2

This report provides a read-only investigation and proposal to fix the facade implementation in the department-user mapping endpoints: `/department/user/save` and `/department/user/delete`.

---

## 1. Observation

### A. Database Models (`Back/app/models.py`)
- **`User` Model** (lines 17-27):
  ```python
  class User(Base):
      __tablename__ = "users"
      id = Column(Integer, primary_key=True, index=True)
      username = Column(String, unique=True, index=True)
      hashed_password = Column(String)
      role = Column(String, default="worker")
      roleId = Column(String, default="2")
      email = Column(String, nullable=True)
      department_id = Column(String, nullable=True)
      create_time = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
      permissions = Column(JSON, default=list)
  ```
- **`Department` Model** (lines 38-45):
  ```python
  class Department(Base):
      __tablename__ = "departments"
      id = Column(String, primary_key=True, index=True)
      departmentName = Column(String)
      parentId = Column(String, nullable=True)
      status = Column(Integer, default=1)  # 1 = active, 0 = inactive
      remark = Column(Text, nullable=True)
      createTime = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
  ```
- **Analysis**:
  - The `User` model has a `department_id` string column that aligns with the string `id` column of the `Department` model.
  - Currently, there is **no explicit ForeignKey constraint** or SQLAlchemy relationship (e.g. `relationship()`) defined between them.
  - **Inconsistency**: While `User` uses `department_id` (snake_case), other models like `Worker` and `Position` use `departmentId` (camelCase):
    - `Worker.departmentId` (line 69): `departmentId = Column(String, nullable=True)`
    - `Position.departmentId` (line 143): `departmentId = Column(String, nullable=True)`
    - `Department.parentId` (line 42): `parentId = Column(String, nullable=True)`

### B. Schemas (`Back/app/schemas.py`)
- The existing user schemas include `UserCreate` (lines 16-23) and `UserResponse` (lines 25-36). None of them model the nested `department: { id: "dept_id" }` object structure sent by the frontend during user save operations.

### C. Facade Routes (`Back/app/routers/department.py`)
- **Verbatim Code** (lines 91-107):
  ```python
  @router.post("/department/user/save")
  def department_user_save(body: dict = Body(...), db: Session = Depends(get_db)):
      # Mock return success
      return {
          "code": 0,
          "data": "success"
      }

  @router.post("/department/user/delete")
  def department_user_delete(body: dict = Body(...), db: Session = Depends(get_db)):
      ids = body.get("ids")
      if not ids:
          return {"code": 500, "message": "请选择需要删除的数据"}
      return {
          "code": 0,
          "data": "success"
      }
  ```
- **Listing Route** (lines 59-89):
  - The endpoint `/department/users` returns all users without filtering by the department ID query parameter (`id`) sent by the frontend:
    ```python
    @router.get("/department/users")
    def get_department_users(
        pageSize: int = Query(10),
        pageIndex: int = Query(1),
        db: Session = Depends(get_db)
    ):
        users = db.query(models.User).all()
        # ...
    ```

### D. Frontend API & View Integration (`Front/src/views/Authorization/User/User.vue`)
- The frontend form schema includes the field `'department.id'` which translates to a nested department object:
  ```json
  {
    "id": 1, // optional (edit mode)
    "username": "user1",
    "account": "user1",
    "email": "user1@example.com",
    "department": {
      "id": "DEPT-HQ"
    },
    "role": ["2"]
  }
  ```
- The delete action sends a payload containing the key `ids` representing user IDs:
  ```json
  {
    "ids": ["1", "2"]
  }
  ```

---

## 2. Logic Chain

1. **Facade Verification**: Based on the Forensic Auditor's handoff report and `/home/xasanboy/ERP/Back/app/routers/department.py`, the save and delete endpoints return hardcoded success responses and do not perform any database operations.
2. **Current Link**: In `models.py`, `User.department_id` is defined as a loose string field that refers to `Department.id` by value.
3. **Database Integrity**: An explicit ForeignKey constraint and SQLAlchemy relationship between `User.department_id` and `Department.id` will enforce relational integrity at the database level.
4. **CRUD Requirements**: 
   - When **saving** a department-user mapping, if the user exists, their `department_id` is updated. If the user does not exist, a new user is created with a default hashed password (e.g. `"123456"`) and mapped to the selected department.
   - When **deleting** a department-user mapping, the users identified by the given IDs must be removed from the database or unlinked (by setting `department_id = None`). The frontend UI for deleting users in `User.vue` is designed to delete the users, which can be accomplished by executing a bulk delete query.
   - For `/department/users` listing to work dynamically with the UI tree selection, it must accept the department ID (as `id` query parameter) and filter users accordingly.

---

## 3. Caveats

- **Default Password**: The frontend user creation form does not prompt for or send a user password. Therefore, new user creation requires generating a default hashed password (e.g., `"123456"`) using the backend's existing hashing utility (`pwd_context` or similar) to ensure the account is functional.
- **CamelCase vs snake_case Inconsistency**: `User.department_id` uses snake_case, whereas `Worker.departmentId` uses camelCase. Database schema modifications should keep `User.department_id` for backward compatibility or define aliases.
- **Nested Objects**: The incoming request body uses path keys like `'department.id'` which Pydantic/FastAPI parses as a nested `department` dictionary containing `id`. The schema and CRUD logic must handle this nested structure robustly.

---

## 4. Conclusion & Proposed Fixes

To resolve the facade implementation, the following changes are proposed:

### A. Proposed SQLAlchemy Schema Change (`Back/app/models.py`)

Optionally update the `User` class to declare a formal foreign key and backref relationship to `Department`:

```python
# Back/app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="worker")
    roleId = Column(String, default="2")
    email = Column(String, nullable=True)
    
    # Establish formal foreign key relationship
    department_id = Column(String, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    
    create_time = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    permissions = Column(JSON, default=list)

    # SQLAlchemy relationship
    department = relationship("Department", backref="users")
```

### B. Proposed Schema Modifications (`Back/app/schemas.py`)

Add the following classes to validate the `/department/user/save` payload:

```python
# Back/app/schemas.py
from pydantic import BaseModel
from typing import List, Optional, Union

class DepartmentUserDept(BaseModel):
    id: str

class DepartmentUserSave(BaseModel):
    id: Optional[Union[int, str]] = None
    username: str
    account: Optional[str] = None
    email: Optional[str] = None
    role: Optional[Union[str, List[str]]] = None
    department: Optional[DepartmentUserDept] = None
```

### C. Proposed CRUD Changes (`Back/app/crud.py`)

Add functions to handle user upserting and bulk deletion:

```python
# Back/app/crud.py
from sqlalchemy.orm import Session
from app import models, schemas
from app.utils import get_password_hash # Assuming get_password_hash is available (often imported from auth utilities)

def save_department_user(db: Session, user_data: schemas.DepartmentUserSave) -> models.User:
    # 1. Extract department ID
    dept_id = None
    if user_data.department:
        dept_id = user_data.department.id

    # 2. Map role fields
    role_name = "worker"
    role_id = "2"
    if user_data.role:
        if isinstance(user_data.role, list) and len(user_data.role) > 0:
            role_id = str(user_data.role[0])
        elif isinstance(user_data.role, str):
            role_id = user_data.role
        
        # Map IDs to human-readable role names
        if role_id == "1":
            role_name = "admin"
        elif role_id == "2":
            role_name = "worker"

    # 3. Check if user is being updated or created
    db_user = None
    if user_data.id:
        db_user = db.query(models.User).filter(models.User.id == int(user_data.id)).first()

    if db_user:
        db_user.username = user_data.username
        db_user.email = user_data.email
        db_user.department_id = dept_id
        db_user.role = role_name
        db_user.roleId = role_id
    else:
        # Generate default password for new users (e.g. "123456")
        # Ensure fallback hash generation
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("123456")
        
        db_user = models.User(
            username=user_data.username,
            hashed_password=hashed_password,
            role=role_name,
            roleId=role_id,
            email=user_data.email,
            department_id=dept_id,
            permissions=["*.*.*"] if role_name == "admin" else []
        )
        db.add(db_user)

    db.commit()
    db.refresh(db_user)
    return db_user

def delete_department_users(db: Session, user_ids: List[int]) -> bool:
    db.query(models.User).filter(models.User.id.in_(user_ids)).delete(synchronize_session=False)
    db.commit()
    return True
```

### D. Proposed Route Changes (`Back/app/routers/department.py`)

Replace the facade endpoints and update the user listing route:

```python
# Back/app/routers/department.py
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from typing import Optional

@router.get("/department/users")
def get_department_users(
    id: Optional[str] = Query(None), # Filter by department ID
    pageSize: int = Query(10),
    pageIndex: int = Query(1),
    db: Session = Depends(get_db)
):
    query = db.query(models.User)
    if id:
        query = query.filter(models.User.department_id == id)
    
    users = query.all()
    total = len(users)
    
    start = (pageIndex - 1) * pageSize
    end = start + pageSize
    paginated = users[start:end]
    
    user_list = []
    for u in paginated:
        user_list.append({
            "id": str(u.id),
            "username": u.username,
            "account": u.username,
            "email": u.email or f"{u.username}@example.com",
            "createTime": u.create_time
        })
        
    return {
        "code": 0,
        "data": {
            "total": total,
            "list": user_list
        }
    }

@router.post("/department/user/save")
def department_user_save(user_in: schemas.DepartmentUserSave, db: Session = Depends(get_db)):
    crud.save_department_user(db, user_in)
    return {
        "code": 0,
        "data": "success"
    }

@router.post("/department/user/delete")
def department_user_delete(body: dict = Body(...), db: Session = Depends(get_db)):
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "请选择需要删除的数据"}
    
    # Standardize string/number IDs list to integer IDs
    if isinstance(ids, (int, str)):
        int_ids = [int(ids)]
    else:
        int_ids = [int(i) for i in ids]
        
    crud.delete_department_users(db, int_ids)
    return {
        "code": 0,
        "data": "success"
    }
```

---

## 5. Verification Method

To verify the proposed implementation:

1. **Verify Database Records**:
   After triggering the `/department/user/save` endpoint, execute the following sqlite command to verify that the user's `department_id` is successfully persisted in `Back/erp.db`:
   ```bash
   sqlite3 Back/erp.db "SELECT id, username, department_id FROM users WHERE username = 'test_user_dep';"
   ```
2. **Interactive Testing via curl**:
   - **Create / Map User**:
     ```bash
     curl -X POST http://localhost:8000/department/user/save \
       -H "Content-Type: application/json" \
       -d '{"username": "test_user_dep", "department": {"id": "DEPT-HQ"}}'
     ```
     Verify that the database responds with a code of `0` and a new record has been created with `department_id = 'DEPT-HQ'`.
   
   - **Retrieve Users Filtered by Department**:
     ```bash
     curl "http://localhost:8000/department/users?id=DEPT-HQ"
     ```
     Verify that the returned user list contains the user `test_user_dep` and only maps users in `DEPT-HQ`.

   - **Delete User**:
     Get the numeric ID of `test_user_dep` and send a POST request to delete it:
     ```bash
     curl -X POST http://localhost:8000/department/user/delete \
       -H "Content-Type: application/json" \
       -d '{"ids": [ID]}'
     ```
     Verify that the record is removed from the database and the table.
