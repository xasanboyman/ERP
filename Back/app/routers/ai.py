from fastapi import APIRouter, Depends, Query, Body, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.routers.activity import log_activity
import os
import uuid
import datetime

router = APIRouter()

PERMISSION_MAP = {
    # Workers / Employees
    "create_worker": {"resource": "hr.sotrudniki", "action": "create", "legacy": ["worker:create", "hr:create"]},
    "update_worker": {"resource": "hr.sotrudniki", "action": "update", "legacy": ["worker:edit", "hr:edit"]},
    "delete_worker": {"resource": "hr.sotrudniki", "action": "delete", "legacy": ["worker:delete", "hr:delete"]},
    "list_workers": {"resource": "hr.sotrudniki", "action": "view", "legacy": ["worker:view", "hr:view"]},

    # Products & Stock
    "create_product": {"resource": "products.spisok_tovarov", "action": "create", "legacy": ["product:create", "products:create"]},
    "add_product_stock": {"resource": "products.spisok_tovarov", "action": "create", "legacy": ["product:create", "product:edit", "pos:sell"]},
    "update_product": {"resource": "products.spisok_tovarov", "action": "update", "legacy": ["product:edit", "products:edit"]},
    "delete_product": {"resource": "products.spisok_tovarov", "action": "delete", "legacy": ["product:delete", "products:delete"]},
    "list_products": {"resource": "products.spisok_tovarov", "action": "view", "legacy": ["product:view", "products:view", "pos:sell", "pos:history"]},
    "search_product": {"resource": "products.spisok_tovarov", "action": "view", "legacy": ["product:view", "products:view", "pos:sell", "pos:history"]},

    # Departments
    "create_department": {"resource": "hr.otdel", "action": "create", "legacy": ["department:create", "hr:create"]},
    "update_department": {"resource": "hr.otdel", "action": "update", "legacy": ["department:edit", "hr:edit"]},
    "delete_department": {"resource": "hr.otdel", "action": "delete", "legacy": ["department:delete", "hr:delete"]},
    "list_departments": {"resource": "hr.otdel", "action": "view", "legacy": ["department:view", "hr:view"]},

    # Positions
    "create_position": {"resource": "hr.dolzhnosti", "action": "create", "legacy": ["position:create", "hr:create"]},
    "update_position": {"resource": "hr.dolzhnosti", "action": "update", "legacy": ["position:edit", "hr:edit"]},
    "delete_position": {"resource": "hr.dolzhnosti", "action": "delete", "legacy": ["position:delete", "hr:delete"]},
    "list_positions": {"resource": "hr.dolzhnosti", "action": "view", "legacy": ["position:view", "hr:view"]},

    # Timesheets & Attendance
    "create_timesheet": {"resource": "hr.tabel", "action": "create", "legacy": ["timesheet:create", "timesheet:view", "hr:view"]},
    "delete_timesheet": {"resource": "hr.tabel", "action": "delete", "legacy": ["timesheet:delete", "hr:delete"]},
    "list_timesheets": {"resource": "hr.tabel", "action": "view", "legacy": ["timesheet:view", "hr:view"]},

    # Staff Output & Adjustments
    "create_staff_output": {"resource": "hr.vyrabotka", "action": "create", "legacy": ["output:create", "hr:create"]},
    "delete_staff_output": {"resource": "hr.vyrabotka", "action": "delete", "legacy": ["output:delete", "hr:delete"]},
    "list_staff_outputs": {"resource": "hr.vyrabotka", "action": "view", "legacy": ["output:view", "hr:view"]},

    "create_staff_adjustment": {"resource": "hr.korrektirovki", "action": "create", "legacy": ["adjustment:create", "hr:create"]},
    "delete_staff_adjustment": {"resource": "hr.korrektirovki", "action": "delete", "legacy": ["adjustment:delete", "hr:delete"]},
    "list_staff_adjustments": {"resource": "hr.korrektirovki", "action": "view", "legacy": ["adjustment:view", "hr:view"]},

    # Salaries & Payroll
    "create_salary": {"resource": "hr.vedomost", "action": "create", "legacy": ["salary:create", "payroll:create"]},
    "list_salaries": {"resource": "hr.vedomost", "action": "view", "legacy": ["salary:view", "payroll:view"]},
    "salary_payout": {"resource": "hr.vedomost", "action": "create", "legacy": ["salary:payout", "payroll:payout"]},

    # Sales & POS & Debtors
    "list_sales": {"resource": "sales.istoriya_prodazh", "action": "view", "legacy": ["pos:history", "sales:view", "pos:sell"]},
    "get_sale_receipt": {"resource": "sales.istoriya_prodazh", "action": "view", "legacy": ["pos:history", "sales:view", "pos:sell"]},
    "list_debtors": {"resource": "sales.istoriya_prodazh", "action": "view", "legacy": ["pos:nasiya", "pos:history", "sales:view", "debtors:view"]},
    "repay_debt": {"resource": "sales.istoriya_prodazh", "action": "create", "legacy": ["pos:nasiya", "pos:sell", "sales:create", "debtors:repay"]},

    # Branches
    "list_branches": {"resource": "products.spisok_tovarov", "action": "view", "legacy": ["branch:view", "branch:list"]},
    "create_branch": {"resource": "products.spisok_tovarov", "action": "create", "legacy": ["branch:create"]},

    # Cutting Orders & Production
    "create_cutting_order": {"resource": "cutting.raskroi", "action": "create", "legacy": ["cutting:create"]},
    "delete_cutting_order": {"resource": "cutting.raskroi", "action": "delete", "legacy": ["cutting:delete"]},
    "list_cutting_orders": {"resource": "cutting.raskroi", "action": "view", "legacy": ["cutting:view"]},
    "start_production": {"resource": "cutting.raskroi", "action": "update", "legacy": ["cutting:edit"]},
    "create_cutting_stage": {"resource": "cutting.raskroi", "action": "create", "legacy": ["cutting:create"]},
    "delete_cutting_stage": {"resource": "cutting.raskroi", "action": "delete", "legacy": ["cutting:delete"]},
    "list_cutting_stages": {"resource": "cutting.raskroi", "action": "view", "legacy": ["cutting:view"]},
    "create_cutting_process": {"resource": "cutting.raskroi", "action": "create", "legacy": ["cutting:create"]},
    "delete_cutting_process": {"resource": "cutting.raskroi", "action": "delete", "legacy": ["cutting:delete"]},
    "list_cutting_processes": {"resource": "cutting.raskroi", "action": "view", "legacy": ["cutting:view"]},
    "list_cutting_tasks": {"resource": "cutting.raskroi", "action": "view", "legacy": ["cutting:view"]},
    "update_task_status": {"resource": "cutting.raskroi", "action": "update", "legacy": ["cutting:edit"]},
    "create_cutting_execution": {"resource": "cutting.raskroi", "action": "create", "legacy": ["cutting:create"]},
    "list_cutting_executions": {"resource": "cutting.raskroi", "action": "view", "legacy": ["cutting:view"]},

    # QR Codes
    "generate_qr_code": {"resource": "qr_codes.print", "action": "create", "legacy": ["qr:create"]},
    "list_qr_codes": {"resource": "qr_codes.print", "action": "view", "legacy": ["qr:view"]},
    "delete_qr_code": {"resource": "qr_codes.print", "action": "delete", "legacy": ["qr:delete"]},

    # Users & Roles
    "list_users": {"resource": "staff.users", "action": "view", "legacy": ["user:view", "staff:view"]},
    "create_role": {"resource": "staff.roles", "action": "create", "legacy": ["role:create", "staff:create"]},
    "delete_role": {"resource": "staff.roles", "action": "delete", "legacy": ["role:delete", "staff:delete"]},
    "list_roles": {"resource": "staff.roles", "action": "view", "legacy": ["role:view", "staff:view"]},
}

def check_user_permission(action: str, user_perms: list, is_super: bool) -> bool:
    if is_super:
        return True
    if not user_perms:
        return False
    if "*.*.*" in user_perms or "*:*" in user_perms:
        return True
    perm_entry = PERMISSION_MAP.get(action)
    if not perm_entry:
        return False

    resource = perm_entry["resource"]
    act = perm_entry["action"]

    req_str = f"{resource}:{act}"
    req_star = f"{resource}:*"

    if req_str in user_perms or req_star in user_perms:
        return True

    for leg in perm_entry.get("legacy", []):
        if leg in user_perms:
            return True

    return False

@router.get("/ai/config")
def ai_config(username: str = Query(None), db: Session = Depends(get_db)):
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        for env_path in [".env", "Back/.env", "../.env", "../../.env"]:
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    for line in f:
                        if line.startswith("GEMINI_API_KEY="):
                            gemini_key = line.split("=")[1].strip().strip('"').strip("'")
                            break
            if gemini_key:
                break

    user_name = "Mehmon"
    role_name = "Cheklangan Foydalanuvchi"
    is_super = False
    user_permissions = []

    if username:
        db_user = db.query(models.User).filter(models.User.username == username).first()
        if db_user:
            user_name = db_user.username
            role_name = db_user.role or "Foydalanuvchi"
            is_super = (db_user.role == "admin" or str(db_user.roleId) == "1" or "*.*.*" in (db_user.permissions or []))
            
            db_role = db.query(models.Role).filter(models.Role.id == str(db_user.roleId)).first()
            role_perms = db_role.permissions if db_role and db_role.permissions else []
            user_perms_raw = db_user.permissions or []
            user_permissions = list(set(role_perms + user_perms_raw))
            if is_super:
                user_permissions = ["*.*.*"]

    # Filter allowed tools
    allowed_tools = []
    permissions_dict = {}
    for action_name, perm_info in PERMISSION_MAP.items():
        if check_user_permission(action_name, user_permissions, is_super):
            allowed_tools.append(action_name)
            res = perm_info["resource"]
            act = perm_info["action"]
            if res not in permissions_dict:
                permissions_dict[res] = []
            if act not in permissions_dict[res]:
                permissions_dict[res].append(act)

    ALL_UI = [
        {"resource": "products.spisok_tovarov", "title": "Omborxona", "actions": ["view", "create", "update", "delete"]},
        {"resource": "sales.istoriya_prodazh", "title": "Sotuvlar / POS", "actions": ["view", "create"]},
        {"resource": "hr.sotrudniki", "title": "Xodimlar", "actions": ["view", "create", "update", "delete", "print"]},
        {"resource": "hr.otdel", "title": "Bo'limlar", "actions": ["view", "create", "update", "delete"]},
        {"resource": "hr.dolzhnosti", "title": "Lavozimlar", "actions": ["view", "create", "update", "delete"]},
        {"resource": "hr.tabel", "title": "Tabel davomati", "actions": ["view", "create", "update", "delete"]},
        {"resource": "hr.vyrabotka", "title": "Ishlab chiqarish (vyrabotka)", "actions": ["view", "create", "update", "delete"]},
        {"resource": "hr.korrektirovki", "title": "Korrektirovkalar", "actions": ["view", "create", "update", "delete"]},
        {"resource": "hr.vedomost", "title": "Ish haqi vedomosti", "actions": ["view", "create", "print"]},
        {"resource": "staff.users", "title": "Foydalanuvchilar", "actions": ["view", "create", "update", "delete"]},
        {"resource": "staff.roles", "title": "Rollar", "actions": ["view", "create", "update", "delete"]},
        {"resource": "cutting.raskroi", "title": "Raskroy / Kesish", "actions": ["view", "create", "update", "delete", "print"]},
        {"resource": "qr_codes.print", "title": "QR kodlar", "actions": ["view", "create"]}
    ]

    accessible_ui = []
    for ui in ALL_UI:
        if is_super or ui["resource"] in permissions_dict:
            acts = permissions_dict.get(ui["resource"], ui["actions"] if is_super else [])
            accessible_ui.append({"resource": ui["resource"], "title": ui["title"], "actions": acts})

    roles_list = []
    if is_super or "staff.roles:view" in user_permissions or "role:view" in user_permissions:
        roles = db.query(models.Role).all()
        for r in roles:
            roles_list.append({
                "id": r.id,
                "name": r.roleName,
                "slug": r.roleName.lower().replace(" ", "_")
            })

    return {
        "code": 0,
        "data": {
            "user": {
                "id": 1,
                "name": user_name,
                "role": role_name,
                "is_super": is_super
            },
            "roles": roles_list,
            "permissions": permissions_dict,
            "allowed_tools": allowed_tools,
            "accessible_ui": accessible_ui,
            "gemini_api_key": gemini_key or "",
            "mcp": {
                "server_name": "ERP_AI_Server",
                "endpoint": "/mcp",
                "protocol_version": "2024-11-05",
                "supported_transports": ["stdio", "sse", "http"]
            }
        }
    }

@router.post("/ai/execute")
def ai_execute(body: dict = Body(...), db: Session = Depends(get_db)):
    action = body.get("action")
    params = body.get("params", {})
    username = body.get("username")

    if not action:
        return {"code": 500, "message": "Action parameter is required."}

    try:
        # Strict authorization check for all users
        is_super = False
        user_permissions = []
        if username:
            db_user = db.query(models.User).filter(models.User.username == username).first()
            if db_user:
                is_super = (db_user.role == "admin" or str(db_user.roleId) == "1" or "*.*.*" in (db_user.permissions or []))
                db_role = db.query(models.Role).filter(models.Role.id == str(db_user.roleId)).first()
                role_perms = db_role.permissions if db_role and db_role.permissions else []
                user_permissions = list(set(role_perms + (db_user.permissions or [])))
                if is_super:
                    user_permissions = ["*.*.*"]

        if not check_user_permission(action, user_permissions, is_super):
            return {
                "code": 403,
                "message": "Xavfsizlik ogohlantirishi: Sizda ushbu amalni bajarish yoki ma'lumotni olish uchun ruxsat yo'q."
            }
                            
        if action == "create_worker":
            # Map first_name, last_name, phone, department, position, salary
            name = f"{params.get('first_name', '')} {params.get('last_name', '')}".strip()
            if not name:
                name = params.get("name", "New Worker")
                
            account = params.get("account") or name.lower().replace(" ", "_")[:12]
            
            # Resolve departmentId
            dept_name = params.get("department", "")
            dept_id = None
            if dept_name:
                dept = db.query(models.Department).filter(models.Department.departmentName.like(f"%{dept_name}%")).first()
                if dept:
                    dept_id = dept.id
                    
            worker_in = schemas.WorkerCreate(
                name=name,
                account=account,
                email=params.get("email"),
                phone=params.get("phone", "+998900000000"),
                role=params.get("position", "Worker"),
                departmentId=dept_id,
                baseSalary=params.get("salary", 0.0),
                remark=params.get("description", "Created via AI voice assistant")
            )
            worker = crud.create_worker(db, worker_in)
            return {"code": 0, "message": f"Worker '{worker.name}' created successfully.", "data": {"id": worker.id, "name": worker.name}}
            
        elif action == "update_worker":
            worker_id = params.get("worker_id")
            if not worker_id:
                return {"code": 500, "message": "worker_id is required."}
            worker = db.query(models.Worker).filter(models.Worker.id == str(worker_id)).first()
            if not worker:
                return {"code": 500, "message": "Worker not found."}
                
            if "first_name" in params or "last_name" in params:
                first = params.get("first_name", worker.name.split()[0] if worker.name else "")
                last = params.get("last_name", worker.name.split()[1] if len(worker.name.split()) > 1 else "")
                worker.name = f"{first} {last}".strip()
            if "phone" in params:
                worker.phone = params["phone"]
            if "salary" in params:
                worker.baseSalary = params["salary"]
            if "position" in params:
                worker.role = params["position"]
                
            db.commit()
            return {"code": 0, "message": f"Worker '{worker.name}' updated successfully."}
            
        elif action == "delete_worker":
            worker_id = params.get("worker_id")
            if not worker_id:
                return {"code": 500, "message": "worker_id is required."}
            res = crud.delete_worker(db, str(worker_id))
            if res:
                return {"code": 0, "message": f"Worker {worker_id} deleted successfully."}
            return {"code": 500, "message": "Worker not found."}
            
        elif action == "create_product":
            product_in = schemas.ProductCreate(
                productName=params.get("name", "New Product"),
                SKU=params.get("article") or "SKU-" + str(uuid.uuid4().int)[:6],
                category=params.get("category", "Dasturiy ta'minot"),
                price=params.get("price", 0.0),
                cost=params.get("cost", 0.0),
                quantityInStock=params.get("quantity", 0),
                remark=params.get("description", "Created via AI voice assistant")
            )
            prod = crud.create_product(db, product_in)
            return {"code": 0, "message": f"Product '{prod.productName}' created successfully.", "data": {"id": prod.id, "name": prod.productName}}
            
        elif action == "update_product":
            product_id = params.get("product_id")
            if not product_id:
                return {"code": 500, "message": "product_id is required."}
            prod = db.query(models.Product).filter(models.Product.id == str(product_id)).first()
            if not prod:
                return {"code": 500, "message": "Product not found."}
            if "name" in params:
                prod.productName = params["name"]
            if "price" in params:
                prod.price = params["price"]
            if "quantity" in params:
                prod.quantityInStock = params["quantity"]
            db.commit()
            return {"code": 0, "message": f"Product '{prod.productName}' updated successfully."}
            
        elif action == "delete_product":
            product_id = params.get("product_id")
            if not product_id:
                return {"code": 500, "message": "product_id is required."}
            res = crud.delete_product(db, str(product_id))
            if res:
                return {"code": 0, "message": f"Product {product_id} deleted successfully."}
            return {"code": 500, "message": "Product not found."}
            
        elif action == "list_products":
            prods = db.query(models.Product).all()
            return {
                "code": 0,
                "data": [{"id": p.id, "name": p.productName, "SKU": p.SKU, "price": p.price, "quantity": p.quantityInStock} for p in prods]
            }
            
        elif action == "list_workers":
            workers = db.query(models.Worker).all()
            return {
                "code": 0,
                "data": [{"id": w.id, "name": w.name, "role": w.role, "phone": w.phone} for w in workers]
            }
            
        elif action == "list_users":
            users = db.query(models.User).all()
            return {
                "code": 0,
                "data": [{"id": u.id, "username": u.username, "role": u.role} for u in users]
            }
            
        elif action == "list_departments":
            depts = db.query(models.Department).all()
            return {
                "code": 0,
                "data": [{"id": d.id, "name": d.departmentName} for d in depts]
            }
            
        elif action == "list_positions":
            positions = db.query(models.Position).all()
            return {
                "code": 0,
                "data": [{"id": p.id, "name": p.positionName, "departmentId": p.departmentId, "salary": p.baseSalary} for p in positions]
            }
            
        elif action == "create_department":
            dept_in = schemas.DepartmentCreate(
                departmentName=params.get("name", "New Department"),
                remark=params.get("description")
            )
            dept = crud.create_department(db, dept_in)
            return {"code": 0, "message": f"Department '{dept.departmentName}' created successfully.", "data": {"id": dept.id, "name": dept.departmentName}}
            
        elif action == "create_position":
            pos_in = schemas.PositionCreate(
                positionName=params.get("name", "New Position"),
                baseSalary=params.get("salary", 0.0),
                remark=params.get("description")
            )
            pos = crud.create_position(db, pos_in)
            return {"code": 0, "message": f"Position '{pos.positionName}' created successfully.", "data": {"id": pos.id, "name": pos.positionName}}
            
        elif action == "create_timesheet":
            ts_in = schemas.StaffTimesheetCreate(
                date=params.get("date") or datetime.date.today().strftime("%Y-%m-%d"),
                records=params.get("records", [])
            )
            ts = crud.create_staff_timesheet(db, ts_in)
            return {"code": 0, "message": f"Timesheet for date '{ts.date}' created successfully."}
            
        elif action == "create_staff_output":
            out_in = schemas.StaffOutputCreate(
                workerId=str(params.get("worker_id")),
                name=params.get("name", "Operation Output"),
                amount=params.get("amount", 0.0),
                period_month=params.get("period_month"),
                comment=params.get("comment")
            )
            out = crud.create_staff_output(db, out_in)
            return {"code": 0, "message": "Staff output recorded successfully."}
            
        elif action == "create_staff_adjustment":
            adj_in = schemas.StaffAdjustmentCreate(
                workerId=str(params.get("worker_id")),
                document_type=params.get("document_type", "bonus"),
                amount=params.get("amount", 0.0),
                period_month=params.get("period_month"),
                description=params.get("description")
            )
            adj = crud.create_staff_adjustment(db, adj_in)
            return {"code": 0, "message": f"Staff adjustment '{adj.document_type}' recorded successfully."}
            
        elif action == "list_staff_outputs":
            outputs = db.query(models.StaffOutput).all()
            workers = {w.id: w.name for w in db.query(models.Worker).all()}
            return {
                "code": 0,
                "data": [{"id": o.id, "workerId": o.workerId, "workerName": workers.get(o.workerId, "?"), "name": o.name, "amount": o.amount, "period_month": o.period_month} for o in outputs]
            }

        elif action == "delete_staff_output":
            ids = params.get("ids", [params.get("id")])
            if isinstance(ids, str): ids = [ids]
            for i in ids:
                crud.delete_staff_output(db, str(i))
            return {"code": 0, "message": "Staff output deleted successfully."}

        elif action == "list_staff_adjustments":
            adjs = db.query(models.StaffAdjustment).all()
            workers = {w.id: w.name for w in db.query(models.Worker).all()}
            return {
                "code": 0,
                "data": [{"id": a.id, "workerId": a.workerId, "workerName": workers.get(a.workerId, "?"), "type": a.document_type, "amount": a.amount, "period_month": a.period_month} for a in adjs]
            }

        elif action == "delete_staff_adjustment":
            ids = params.get("ids", [params.get("id")])
            if isinstance(ids, str): ids = [ids]
            for i in ids:
                crud.delete_staff_adjustment(db, str(i))
            return {"code": 0, "message": "Staff adjustment deleted successfully."}

        elif action == "update_department":
            dept_id = params.get("department_id")
            if not dept_id:
                return {"code": 500, "message": "department_id is required."}
            dept = db.query(models.Department).filter(models.Department.id == str(dept_id)).first()
            if not dept:
                return {"code": 500, "message": "Department not found."}
            if "name" in params: dept.departmentName = params["name"]
            if "remark" in params: dept.remark = params["remark"]
            db.commit()
            return {"code": 0, "message": f"Department '{dept.departmentName}' updated successfully."}

        elif action == "delete_department":
            dept_id = params.get("department_id")
            if not dept_id:
                return {"code": 500, "message": "department_id is required."}
            dept = db.query(models.Department).filter(models.Department.id == str(dept_id)).first()
            if dept:
                db.delete(dept)
                db.commit()
                return {"code": 0, "message": f"Department deleted successfully."}
            return {"code": 500, "message": "Department not found."}

        elif action == "update_position":
            pos_id = params.get("position_id")
            if not pos_id:
                return {"code": 500, "message": "position_id is required."}
            pos = db.query(models.Position).filter(models.Position.id == str(pos_id)).first()
            if not pos:
                return {"code": 500, "message": "Position not found."}
            if "name" in params: pos.positionName = params["name"]
            if "salary" in params: pos.baseSalary = params["salary"]
            if "department_id" in params: pos.departmentId = params["department_id"]
            db.commit()
            return {"code": 0, "message": f"Position '{pos.positionName}' updated successfully."}

        elif action == "delete_position":
            pos_id = params.get("position_id")
            if not pos_id:
                return {"code": 500, "message": "position_id is required."}
            crud.delete_position(db, str(pos_id))
            return {"code": 0, "message": f"Position deleted successfully."}

        elif action == "list_timesheets":
            timesheets = db.query(models.StaffTimesheet).all()
            return {
                "code": 0,
                "data": [{"id": t.id, "date": t.date, "status": t.status} for t in timesheets]
            }

        elif action == "delete_timesheet":
            ids = params.get("ids", [params.get("id")])
            if isinstance(ids, str): ids = [ids]
            for i in ids:
                crud.delete_staff_timesheet(db, str(i))
            return {"code": 0, "message": "Timesheet deleted successfully."}

        elif action == "list_salaries":
            salaries = db.query(models.Salary).all()
            workers = {w.id: w.name for w in db.query(models.Worker).all()}
            return {
                "code": 0,
                "data": [{"id": s.id, "workerId": s.workerId, "workerName": workers.get(s.workerId, "?"), "netSalary": s.netSalary, "payDate": s.payDate, "status": s.status} for s in salaries]
            }

        elif action == "create_salary":
            sal_in = schemas.SalaryCreate(
                workerId=str(params.get("worker_id")),
                baseSalary=params.get("base_salary", 0.0),
                allowance=params.get("allowance", 0.0),
                deduction=params.get("deduction", 0.0),
                payDate=params.get("pay_date") or datetime.date.today().strftime("%Y-%m-%d"),
                status=params.get("status", "paid"),
                remark=params.get("remark", "AI orqali yaratildi")
            )
            s = crud.create_salary(db, sal_in)
            return {"code": 0, "message": "Salary record created successfully.", "data": {"id": s.id}}

        elif action == "salary_payout":
            worker_ids = params.get("worker_ids", [])
            if isinstance(worker_ids, str): worker_ids = [worker_ids]
            today = datetime.date.today().strftime("%Y-%m-%d")
            count = 0
            for wid in worker_ids:
                w = db.query(models.Worker).filter(models.Worker.id == str(wid)).first()
                if w:
                    crud.create_salary(db, schemas.SalaryCreate(
                        workerId=w.id, baseSalary=w.baseSalary,
                        allowance=params.get("allowance", 0.0),
                        deduction=params.get("deduction", 0.0),
                        payDate=today, status="paid",
                        remark=params.get("remark", "AI orqali ish haqi to'lovi")
                    ))
                    count += 1
            return {"code": 0, "message": f"{count} ta xodimga ish haqi to'landi."}

        elif action == "list_cutting_orders":
            orders = crud.get_cutting_orders(db)
            return {
                "code": 0,
                "data": [{"id": o.id, "order_number": o.order_number, "project": o.project, "status": o.status, "total_quantity": o.total_quantity} for o in orders]
            }

        elif action == "create_cutting_order":
            from app.schemas import CuttingOrderCreate
            order_in = CuttingOrderCreate(
                order_number=params.get("order_number", "ORD-" + str(uuid.uuid4().int)[:6]),
                project=params.get("project", ""),
                order_name=params.get("order_name", ""),
                document_date=params.get("document_date") or datetime.date.today().strftime("%Y-%m-%d"),
                responsible_user_ids=params.get("responsible_user_ids", []),
                items=params.get("items", [])
            )
            o = crud.create_cutting_order(db, order_in)
            return {"code": 0, "message": f"Cutting order '{o.order_number}' created.", "data": {"id": o.id, "order_number": o.order_number}}

        elif action == "delete_cutting_order":
            ids = params.get("ids", [params.get("id")])
            if isinstance(ids, str): ids = [ids]
            for i in ids:
                crud.delete_cutting_order(db, str(i))
            return {"code": 0, "message": "Cutting order deleted successfully."}

        elif action == "start_production":
            order_id = params.get("order_id")
            if not order_id:
                return {"code": 500, "message": "order_id is required."}
            o = crud.start_production_for_order(db, str(order_id))
            if o:
                return {"code": 0, "message": f"Production started for order {order_id}."}
            return {"code": 500, "message": "Order not found."}

        elif action == "list_cutting_stages":
            stages = crud.get_cutting_stages(db)
            return {"code": 0, "data": [{"id": s.id, "name": s.name, "price": s.price} for s in stages]}

        elif action == "create_cutting_stage":
            from app.schemas import CuttingStageCreate
            s_in = CuttingStageCreate(
                name=params.get("name", "New Stage"),
                is_system=params.get("is_system", False),
                price=params.get("price", 0.0),
                duration=params.get("duration", 0.0)
            )
            s = crud.create_cutting_stage(db, s_in)
            return {"code": 0, "message": f"Cutting stage '{s.name}' created.", "data": {"id": s.id}}

        elif action == "delete_cutting_stage":
            ids = params.get("ids", [params.get("id")])
            if isinstance(ids, str): ids = [ids]
            for i in ids:
                crud.delete_cutting_stage(db, str(i))
            return {"code": 0, "message": "Cutting stage deleted."}

        elif action == "list_cutting_processes":
            processes = crud.get_cutting_processes(db)
            return {"code": 0, "data": [{"id": p.id, "name": p.name, "remark": p.remark} for p in processes]}

        elif action == "create_cutting_process":
            from app.schemas import CuttingProcessCreate
            p_in = CuttingProcessCreate(
                name=params.get("name", "New Process"),
                remark=params.get("remark"),
                stages=params.get("stages", [])
            )
            p = crud.create_cutting_process(db, p_in)
            return {"code": 0, "message": f"Cutting process '{p.name}' created.", "data": {"id": p.id}}

        elif action == "delete_cutting_process":
            ids = params.get("ids", [params.get("id")])
            if isinstance(ids, str): ids = [ids]
            for i in ids:
                crud.delete_cutting_process(db, str(i))
            return {"code": 0, "message": "Cutting process deleted."}

        elif action == "list_cutting_tasks":
            tasks = crud.get_cutting_tasks(db)
            return {
                "code": 0,
                "data": [{"id": t.id, "orderId": t.orderId, "stageId": t.stageId, "quantity": t.quantity, "status": t.status, "order_number": t.order_number_snapshot, "stage_name": t.stage_name_snapshot} for t in tasks]
            }

        elif action == "update_task_status":
            task_id = params.get("task_id")
            status = params.get("status")
            if not task_id or not status:
                return {"code": 500, "message": "task_id and status are required."}
            t = crud.update_cutting_task_status(db, str(task_id), status)
            if t:
                return {"code": 0, "message": f"Task status updated to '{status}'."}
            return {"code": 500, "message": "Task not found."}

        elif action == "list_cutting_executions":
            exes = crud.get_cutting_task_executions(db)
            workers = {w.id: w.name for w in db.query(models.Worker).all()}
            return {
                "code": 0,
                "data": [{"id": e.id, "taskId": e.taskId, "workerId": e.workerId, "workerName": workers.get(e.workerId, "?"), "quantity": e.quantity} for e in exes]
            }

        elif action == "create_cutting_execution":
            from app.schemas import CuttingTaskExecutionCreate
            exe_in = CuttingTaskExecutionCreate(
                taskId=str(params.get("task_id")),
                workerId=str(params.get("worker_id")),
                quantity=params.get("quantity", 0),
                period_month=params.get("period_month"),
                comment=params.get("comment")
            )
            e = crud.create_cutting_task_execution(db, exe_in)
            return {"code": 0, "message": "Cutting execution recorded.", "data": {"id": e.id}}

        elif action == "list_qr_codes":
            codes = crud.get_qr_codes(db)
            return {"code": 0, "data": [{"id": q.id, "code": q.code, "taskId": q.taskId, "quantity": q.quantity} for q in codes]}

        elif action == "generate_qr_code":
            from app.schemas import QrCodeCreate
            qr_in = QrCodeCreate(
                taskId=str(params.get("task_id")),
                quantity=params.get("quantity", 1)
            )
            q = crud.generate_qr_code_for_task(db, qr_in)
            return {"code": 0, "message": f"QR code generated: {q.code}", "data": {"id": q.id, "code": q.code}}

        elif action == "delete_qr_code":
            ids = params.get("ids", [params.get("id")])
            if isinstance(ids, str): ids = [ids]
            for i in ids:
                crud.delete_qr_code(db, str(i))
            return {"code": 0, "message": "QR code deleted."}

        elif action == "create_role":
            role_in = schemas.RoleCreate(
                id=params.get("role_id") or "ROLE-" + str(uuid.uuid4().int)[:6],
                roleName=params.get("name", "New Role"),
                status=params.get("status", 1),
                remark=params.get("remark", "Created via AI voice assistant"),
                permissions=params.get("permissions", [])
            )
            r = crud.create_role(db, role_in)
            return {"code": 0, "message": f"Role '{r.roleName}' created successfully.", "data": {"id": r.id, "name": r.roleName}}

        elif action == "delete_role":
            role_id = params.get("role_id")
            if not role_id:
                return {"code": 500, "message": "role_id is required."}
            role = db.query(models.Role).filter(models.Role.id == str(role_id)).first()
            if role:
                db.delete(role)
                db.commit()
                return {"code": 0, "message": f"Role {role_id} deleted successfully."}
            return {"code": 500, "message": "Role not found."}

        elif action == "list_roles":
            roles = db.query(models.Role).all()
            if not roles:
                roles_list = [
                    {"id": "1", "name": "Super Admin", "remark": "All permissions"},
                    {"id": "2", "name": "Manager", "remark": "Normal manager"},
                ]
            else:
                roles_list = [{"id": r.id, "name": r.roleName, "remark": r.remark} for r in roles]
            return {"code": 0, "data": roles_list}

        elif action == "list_sales":
            sales = db.query(models.Sale).order_by(models.Sale.id.desc()).limit(30).all()
            return {
                "code": 0,
                "data": [
                    {
                        "id": s.id,
                        "receipt_number": s.receipt_number,
                        "created_at": s.created_at,
                        "total_amount": s.total_amount,
                        "payment_method": s.payment_method,
                        "customer_name": s.customer_name,
                        "debt_amount": s.debt_amount
                    }
                    for s in sales
                ]
            }

        elif action == "get_sale_receipt":
            rec = params.get("receipt_number")
            sale = db.query(models.Sale).filter(models.Sale.receipt_number == rec).first()
            if sale:
                return {
                    "code": 0,
                    "data": {
                        "id": sale.id,
                        "receipt_number": sale.receipt_number,
                        "total_amount": sale.total_amount,
                        "paid_amount": sale.paid_amount,
                        "debt_amount": sale.debt_amount,
                        "payment_method": sale.payment_method,
                        "customer_name": sale.customer_name,
                        "items": sale.items
                    }
                }
            return {"code": 404, "message": "Chek topilmadi."}

        elif action == "list_debtors":
            sales_with_debt = db.query(models.Sale).filter(models.Sale.debt_amount > 0).all()
            debtors_map = {}
            for s in sales_with_debt:
                c_name = s.customer_name or "Noma'lum Mijoz"
                if c_name not in debtors_map:
                    debtors_map[c_name] = {"name": c_name, "phone": s.customer_phone or "", "total_debt": 0, "sales_count": 0}
                debtors_map[c_name]["total_debt"] += (s.debt_amount or 0)
                debtors_map[c_name]["sales_count"] += 1
            return {"code": 0, "data": list(debtors_map.values())}

        elif action == "repay_debt":
            c_name = params.get("customer_name")
            amt = float(params.get("amount", 0))
            if not c_name or amt <= 0:
                return {"code": 400, "message": "Mijoz ismi va to'lov summasi kiritilishi shart."}
            sales = db.query(models.Sale).filter(models.Sale.customer_name == c_name, models.Sale.debt_amount > 0).order_by(models.Sale.id.asc()).all()
            remaining_repay = amt
            for s in sales:
                if remaining_repay <= 0:
                    break
                current_debt = s.debt_amount or 0
                pay_for_this = min(remaining_repay, current_debt)
                s.debt_amount = current_debt - pay_for_this
                s.paid_amount = (s.paid_amount or 0) + pay_for_this
                remaining_repay -= pay_for_this
            db.commit()
            return {"code": 0, "message": f"{c_name} uchun ${amt} qarz to'lovi qabul qilindi."}

        elif action == "list_branches":
            branches = db.query(models.Branch).all()
            return {
                "code": 0,
                "data": [{"id": b.id, "name": b.name, "code": b.code, "address": b.address, "phone": b.phone} for b in branches]
            }

        elif action == "create_branch":
            b_in = schemas.BranchCreate(
                name=params.get("name", "Yangi Filial"),
                code=params.get("code", "BR-" + str(uuid.uuid4().int)[:4]),
                address=params.get("address", ""),
                phone=params.get("phone", "")
            )
            b = crud.create_branch(db, b_in)
            return {"code": 0, "message": f"Filial '{b.name}' yaratildi.", "data": {"id": b.id, "name": b.name}}

        elif action == "search_product":
            q = params.get("name") or params.get("query") or ""
            prods = db.query(models.Product).filter(models.Product.productName.like(f"%{q}%")).all()
            return {
                "code": 0,
                "data": [{"id": p.id, "name": p.productName, "SKU": p.SKU, "price": p.price, "quantity": p.quantityInStock} for p in prods]
            }

        elif action == "add_product_stock":
            name = params.get("name") or "Yangi Mahsulot"
            qty = float(params.get("added_quantity", params.get("quantity", 1)))
            prod = db.query(models.Product).filter(models.Product.productName.like(f"%{name}%")).first()
            if prod:
                prod.quantityInStock = (prod.quantityInStock or 0) + qty
                db.commit()
                return {"code": 0, "message": f"'{prod.productName}' ombor qoldig'iga +{qty} qo'shildi (Jami: {prod.quantityInStock})."}
            else:
                prod_in = schemas.ProductCreate(
                    productName=name,
                    SKU="SKU-" + str(uuid.uuid4().int)[:6],
                    category=params.get("category", "Umumiy"),
                    price=float(params.get("price", 0.0)),
                    cost=float(params.get("cost", 0.0)),
                    quantityInStock=qty,
                    remark="AI orqali qo'shildi"
                )
                p = crud.create_product(db, prod_in)
                return {"code": 0, "message": f"Yangi mahsulot '{p.productName}' ({qty} dona) omborga kiritildi.", "data": {"id": p.id}}

        else:
            return {"code": 500, "message": f"Unknown action '{action}'."}

    except Exception as e:
        return {"code": 500, "message": str(e)}
