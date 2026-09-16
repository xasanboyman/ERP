import uuid
import datetime
import secrets
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from passlib.context import CryptContext
from . import models, schemas


import hashlib

def verify_password(plain_password, hashed_password):
    if not hashed_password or not plain_password:
        return False
    if ":" in hashed_password:
        salt, h_pass = hashed_password.split(":", 1)
        return hashlib.sha256((salt + plain_password).encode()).hexdigest() == h_pass
    if hashed_password.startswith("$2a$") or hashed_password.startswith("$2b$") or hashed_password.startswith("$2y$"):
        try:
            import bcrypt
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            pass
    # fallback for raw SHA-256 or matching plain
    if hashed_password == plain_password:
         return True
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def get_password_hash(password):
    salt = "erpsalt"
    h_pass = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{h_pass}"


# User CRUD
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed,
        full_name=getattr(user, 'full_name', None),
        role=user.role,
        roleId=user.roleId,
        email=user.email,
        phone=getattr(user, 'phone', None),
        department_id=user.department_id,
        company_id=getattr(user, 'company_id', None) or 'comp-default',
        permissions=user.permissions,
        avatar=getattr(user, 'avatar', None)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def seed_default_roles_for_company(db: Session, company_id: str):
    if not company_id or company_id == "comp-default":
        return []
    # Fetch template roles from comp-default (excluding Super Administrator)
    templates = db.query(models.Role).filter(
        (models.Role.company_id == "comp-default") &
        (~models.Role.roleName.ilike("%super%")) &
        (models.Role.id != "1")
    ).all()
    created = []
    if not templates:
        templates_data = [
            ("Administrator", "Tashkilot administratori", ["/dashboard", "/dashboard/analysis", "/dashboard/workplace", "/product", "/product/list", "/sales", "/sales/pos", "/sales/debtors", "/hr", "/hr/workers", "/hr/timesheets", "/hr/outputs", "/hr/adjustments", "/hr/salary", "/authorization", "/authorization/department", "/authorization/role"]),
            ("Oddiy xodim", "Oddiy xodim", ["/dashboard", "/dashboard/workplace", "/product", "/product/list"]),
            ("Cashier", "Kassir roli", ["/dashboard", "/sales", "/sales/pos", "pos:sell", "pos:nasiya"])
        ]
        for name, remark, perms in templates_data:
            r = models.Role(
                id=str(uuid.uuid4()),
                company_id=company_id,
                roleName=name,
                status=1,
                remark=remark,
                permissions=perms
            )
            db.add(r)
            created.append(r)
    else:
        for t in templates:
            r = models.Role(
                id=str(uuid.uuid4()),
                company_id=company_id,
                roleName=t.roleName,
                status=1,
                remark=t.remark,
                permissions=list(t.permissions or [])
            )
            db.add(r)
            created.append(r)
    db.commit()
    for r in created:
        db.refresh(r)
    return created

# Role CRUD
def get_roles(db: Session, company_id: Optional[str] = None):
    query = db.query(models.Role)
    if company_id:
        if company_id == "comp-default":
            return query.filter((models.Role.company_id == "comp-default") | (models.Role.company_id == None)).all()
        else:
            company_roles = query.filter(models.Role.company_id == company_id).all()
            if not company_roles:
                comp_obj = db.query(models.Company).filter(models.Company.id == company_id).first()
                if comp_obj and isinstance(comp_obj.features, dict) and comp_obj.features.get("roles_initialized"):
                    return []
                company_roles = seed_default_roles_for_company(db, company_id)
                if comp_obj:
                    feats = dict(comp_obj.features or {})
                    feats["roles_initialized"] = True
                    comp_obj.features = feats
                    db.commit()
            return company_roles
    return query.all()

def create_role(db: Session, role: schemas.RoleCreate, company_id: Optional[str] = None):
    db_role = db.query(models.Role).filter(models.Role.id == role.id).first()
    comp = company_id or getattr(role, "company_id", None) or "comp-default"
    if db_role:
        # Update
        db_role.roleName = role.roleName
        db_role.status = role.status
        db_role.remark = role.remark
        db_role.permissions = role.permissions
        if company_id and (not db_role.company_id or db_role.company_id == "comp-default"):
            db_role.company_id = company_id
    else:
        # Create
        db_role = models.Role(
            id=role.id or str(uuid.uuid4()),
            company_id=comp,
            roleName=role.roleName,
            status=role.status,
            remark=role.remark,
            permissions=role.permissions
        )
        db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

# Department CRUD
def get_departments(db: Session, company_id: Optional[str] = None):
    query = db.query(models.Department)
    if company_id:
        query = query.filter(models.Department.company_id == company_id)
    return query.all()

def create_department(db: Session, dept: schemas.DepartmentCreate, company_id: Optional[str] = None):
    dept_id = dept.id
    db_dept = None
    if dept_id:
        db_dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    
    comp = company_id or getattr(dept, "company_id", None) or "comp-default"
    if db_dept:
        db_dept.departmentName = dept.departmentName
        db_dept.parentId = dept.parentId
        db_dept.status = dept.status
        db_dept.remark = dept.remark
        if company_id and (not db_dept.company_id or db_dept.company_id == "comp-default"):
            db_dept.company_id = company_id
    else:
        db_dept = models.Department(
            id=dept_id or str(uuid.uuid4())[:8],
            company_id=comp,
            departmentName=dept.departmentName,
            parentId=dept.parentId,
            status=dept.status,
            remark=dept.remark
        )
        db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept

def delete_department(db: Session, dept_id: str):
    # Clean up any child departments pointing to this parent
    children = db.query(models.Department).filter(models.Department.parentId == str(dept_id)).all()
    for child in children:
        db.delete(child)
    db_dept = db.query(models.Department).filter(models.Department.id == str(dept_id)).first()
    if db_dept:
        db.delete(db_dept)
        db.commit()
        return True
    db.commit()
    return False

# Product CRUD
def get_products(db: Session, company_id: Optional[str] = None):
    q = db.query(models.Product)
    if company_id:
        q = q.filter(models.Product.company_id == company_id)
    return q.all()

def create_product(db: Session, prod: schemas.ProductCreate, company_id: Optional[str] = None):
    prod_id = getattr(prod, 'id', None)
    shtrix = getattr(prod, 'shtrix_code', None)
    raw_classifier = getattr(prod, 'classifier_id', None)
    mxik_code = getattr(prod, 'mxik_code', None)
    sku = getattr(prod, 'SKU', None)
    target_company_id = company_id or getattr(prod, 'company_id', None) or 'comp-default'

    # Cluster Database Synchronization:
    # If the added item does not exist in the shared cluster catalog (classifier_items), add it!
    clean_shtrix = str(shtrix).strip() if shtrix else None
    clean_mxik = str(mxik_code).strip() if mxik_code else None
    clean_name = str(prod.productName).strip() if prod.productName else None

    cluster_item = None
    if clean_shtrix:
        cluster_item = db.query(models.ClassifierItem).filter(models.ClassifierItem.shtrix_code == clean_shtrix).first()
    if not cluster_item and clean_mxik:
        cluster_item = db.query(models.ClassifierItem).filter(models.ClassifierItem.mxik_code == clean_mxik).first()
    if not cluster_item and raw_classifier:
        cluster_item = db.query(models.ClassifierItem).filter(models.ClassifierItem.id == str(raw_classifier)).first()

    if not cluster_item and (clean_name or clean_shtrix or clean_mxik):
        new_cls_id = str(raw_classifier) if raw_classifier else f"cls_{uuid.uuid4().hex[:10]}"
        try:
            cluster_item = models.ClassifierItem(
                id=new_cls_id,
                group_name=prod.category or "Boshqalar",
                class_name=prod.category or "Boshqalar",
                position_name=prod.productName or "Yangi Mahsulot",
                subposition_name=prod.productName or "Yangi Mahsulot",
                brand_name=getattr(prod, 'brand_name', None) or "",
                attribute_name=getattr(prod, 'attribute_name', None) or "",
                mxik_code=clean_mxik or "",
                mxik_name=prod.productName or "",
                shtrix_code=clean_shtrix or "",
                unit=getattr(prod, 'unit', None) or "dona"
            )
            db.add(cluster_item)
            db.flush()
        except Exception as cls_err:
            db.rollback()
            cluster_item = None

    safe_classifier_id = str(cluster_item.id) if cluster_item else (str(raw_classifier) if raw_classifier else None)

    # Consolidate duplicate checks strictly isolated to this company
    conditions = []
    if prod_id:
        conditions.append(models.Product.id == prod_id)
    else:
        if clean_shtrix:
            conditions.append(models.Product.shtrix_code == clean_shtrix)
        if clean_mxik:
            conditions.append(models.Product.mxik_code == clean_mxik)
        if sku and str(sku).strip():
            conditions.append(models.Product.SKU == str(sku).strip())

    db_prod = None
    if conditions:
        query = db.query(models.Product).filter(or_(*conditions))
        if target_company_id:
            query = query.filter(models.Product.company_id == target_company_id)
        db_prod = query.first()

    is_existing = (db_prod is not None) and (not prod_id)

    if db_prod:
        # If adding new stock for an existing product (no explicit ID passed from openAddDialog)
        if not prod_id:
            db_prod.quantityInStock = (db_prod.quantityInStock or 0) + (prod.quantityInStock or 1)
        else:
            db_prod.quantityInStock = prod.quantityInStock

        db_prod.productName = prod.productName or db_prod.productName
        if sku:
            db_prod.SKU = sku
        db_prod.category = prod.category or db_prod.category
        if prod.price is not None and prod.price > 0:
            db_prod.price = prod.price
        if prod.cost is not None and prod.cost > 0:
            db_prod.cost = prod.cost
        db_prod.status = 1
        if safe_classifier_id is not None:
            db_prod.classifier_id = safe_classifier_id
        if clean_shtrix:
            db_prod.shtrix_code = clean_shtrix
        if clean_mxik:
            db_prod.mxik_code = clean_mxik
        if getattr(prod, 'brand_name', None):
            db_prod.brand_name = prod.brand_name
        if getattr(prod, 'attribute_name', None):
            db_prod.attribute_name = prod.attribute_name
        if getattr(prod, 'unit', None):
            db_prod.unit = prod.unit
        if getattr(prod, 'image_url', None):
            db_prod.image_url = prod.image_url
        if getattr(prod, 'expiration_date', None):
            db_prod.expiration_date = prod.expiration_date
        if prod.remark:
            db_prod.remark = prod.remark
        db_prod.company_id = target_company_id
    else:
        new_sku = sku or f"SKU-{str(uuid.uuid4().int)[:6]}"
        db_prod = models.Product(
            id=prod_id or ("PROD-" + str(uuid.uuid4().int)[:6]),
            company_id=target_company_id,
            productName=prod.productName,
            SKU=new_sku,
            category=prod.category or "Boshqalar",
            price=prod.price or 0.0,
            cost=prod.cost or 0.0,
            quantityInStock=prod.quantityInStock or 1,
            status=1,
            classifier_id=safe_classifier_id,
            shtrix_code=clean_shtrix,
            mxik_code=clean_mxik,
            brand_name=getattr(prod, 'brand_name', None),
            attribute_name=getattr(prod, 'attribute_name', None),
            unit=getattr(prod, 'unit', None) or 'dona',
            image_url=getattr(prod, 'image_url', None),
            expiration_date=getattr(prod, 'expiration_date', None),
            remark=prod.remark
        )
        db.add(db_prod)

    if hasattr(prod, 'packagings') and prod.packagings is not None:
        db.query(models.ProductPackaging).filter(models.ProductPackaging.product_id == db_prod.id).delete()
        for pkg_in in prod.packagings:
            pkg_obj = models.ProductPackaging(
                id=pkg_in.id or f"PKG-{uuid.uuid4().hex[:8]}",
                product_id=db_prod.id,
                unit_name=pkg_in.unit_name,
                conversion_factor=pkg_in.conversion_factor,
                price=pkg_in.price,
                cost=getattr(pkg_in, 'cost', 0.0) or 0.0,
                shtrix_code=getattr(pkg_in, 'shtrix_code', None),
                is_base_unit=getattr(pkg_in, 'is_base_unit', False)
            )
            db.add(pkg_obj)

    # Single commit, no redundant network round-trip refresh
    db.commit()
    db_prod.is_existing_record = is_existing
    return db_prod



def delete_product(db: Session, prod_id: str):
    db_prod = db.query(models.Product).filter(models.Product.id == prod_id).first()
    if db_prod:
        db.delete(db_prod)
        db.commit()
        return True
    return False

# Worker CRUD
def get_workers(db: Session, company_id: Optional[str] = None):
    query = db.query(models.Worker)
    if company_id:
        query = query.filter(models.Worker.company_id == company_id)
    return query.all()

def generate_unique_employee_code(db: Session) -> str:
    import random
    code = "".join(random.choices("0123456789", k=6))
    exists = db.query(models.Worker.id).filter(models.Worker.employee_code == code).first()
    if not exists:
        return code
    return str(random.randint(100000, 999999))

def create_worker(db: Session, worker: schemas.WorkerCreate, company_id: Optional[str] = None):
    import datetime
    w_id = worker.id
    comp = company_id or getattr(worker, "company_id", None) or "comp-default"
    db_w = None
    if w_id:
        db_w = db.query(models.Worker).filter(models.Worker.id == w_id).first()
        
    if db_w:
        db_w.name = worker.name
        db_w.account = worker.account
        if comp and (not db_w.company_id or db_w.company_id == "comp-default"):
            db_w.company_id = comp
        if not db_w.employee_code:
            db_w.employee_code = worker.employee_code or generate_unique_employee_code(db)
        elif worker.employee_code:
            db_w.employee_code = worker.employee_code
        db_w.email = worker.email
        db_w.phone = worker.phone
        db_w.role = worker.role
        db_w.departmentId = worker.departmentId
        if worker.hireDate:
            db_w.hireDate = worker.hireDate
        db_w.status = worker.status
        db_w.baseSalary = worker.baseSalary
        db_w.remark = worker.remark
        if worker.avatar is not None:
            db_w.avatar = worker.avatar
    else:
        db_w = models.Worker(
            id=w_id or "W" + str(uuid.uuid4().int)[:6],
            company_id=comp,
            name=worker.name,
            account=worker.account,
            employee_code=worker.employee_code or generate_unique_employee_code(db),
            email=worker.email,
            phone=worker.phone,
            role=worker.role,
            departmentId=worker.departmentId,
            hireDate=worker.hireDate or datetime.date.today().strftime("%Y-%m-%d"),
            status=worker.status,
            baseSalary=worker.baseSalary,
            remark=worker.remark,
            avatar=worker.avatar
        )
        db.add(db_w)
        
    db_user = db.query(models.User).filter(models.User.username == worker.account).first()
    w_role_name = (worker.role or "Cashier").strip()
    db_role_match = db.query(models.Role).filter(
        (models.Role.roleName.ilike(w_role_name)) |
        (models.Role.id == w_role_name)
    ).first()
    
    if db_role_match:
        role_str = db_role_match.roleName
        role_id = db_role_match.id
        role_perms = db_role_match.permissions or []
    else:
        role_str = w_role_name
        role_id = "7972a496-a501-48f4-b2f8-5774dc2bd9c4" if "cashier" in w_role_name.lower() or "kassir" in w_role_name.lower() else "3"
        role_perms = []

    if db_user:
        db_user.full_name = worker.name
        db_user.email = worker.email
        db_user.phone = worker.phone
        db_user.role = role_str
        db_user.roleId = role_id
        if comp and not db_user.company_id:
            db_user.company_id = comp
        if role_perms:
            db_user.permissions = role_perms
        if worker.password:
            db_user.hashed_password = get_password_hash(worker.password)
    else:
        pwd = worker.password if worker.password else "123456"
        db_user = models.User(
            username=worker.account,
            company_id=comp,
            hashed_password=get_password_hash(pwd),
            full_name=worker.name,
            role=role_str,
            roleId=role_id,
            email=worker.email,
            phone=worker.phone,
            permissions=role_perms
        )
        db.add(db_user)
            
    db.commit()
    return db_w

def delete_worker(db: Session, worker_id: str):
    db_w = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
    if db_w:
        db.delete(db_w)
        db.commit()
        return True
    return False

# Salary CRUD
def get_salaries(db: Session, company_id: Optional[str] = None):
    query = db.query(models.Salary)
    if company_id:
        query = query.join(models.Worker, models.Salary.workerId == models.Worker.id).filter(models.Worker.company_id == company_id)
    return query.order_by(models.Salary.payDate.desc(), models.Salary.id.desc()).all()

def create_salary(db: Session, sal: schemas.SalaryCreate, company_id: Optional[str] = None):
    sal_id = sal.id
    comp = company_id or getattr(sal, "company_id", None) or "comp-default"
    db_sal = None
    if sal_id:
        db_sal = db.query(models.Salary).filter(models.Salary.id == sal_id).first()
        
    net = max(0.0, float(sal.baseSalary or 0.0) + float(sal.allowance or 0.0) - float(sal.deduction or 0.0))
    if db_sal:
        db_sal.workerId = sal.workerId
        db_sal.baseSalary = sal.baseSalary
        db_sal.allowance = sal.allowance
        db_sal.deduction = sal.deduction
        db_sal.netSalary = net
        if sal.payDate:
            db_sal.payDate = sal.payDate
        db_sal.status = sal.status
        db_sal.remark = sal.remark
        if comp and hasattr(db_sal, "company_id"):
            db_sal.company_id = comp
    else:
        db_sal = models.Salary(
            id=sal_id or "S" + str(uuid.uuid4().int)[:6],
            company_id=comp,
            workerId=sal.workerId,
            baseSalary=sal.baseSalary,
            allowance=sal.allowance,
            deduction=sal.deduction,
            netSalary=net,
            payDate=sal.payDate or datetime.date.today().strftime("%Y-%m-%d"),
            status=sal.status,
            remark=sal.remark
        )
        db.add(db_sal)
    db.commit()
    return db_sal

def delete_salary(db: Session, sal_id: str):
    db_sal = db.query(models.Salary).filter(models.Salary.id == sal_id).first()
    if db_sal:
        db.delete(db_sal)
        db.commit()
        return True
    return False


# Position CRUD
def get_positions(db: Session, company_id: Optional[str] = None):
    query = db.query(models.Position)
    if company_id:
        if company_id == "comp-default":
            query = query.filter((models.Position.company_id == "comp-default") | (models.Position.company_id == None))
        else:
            query = query.filter(models.Position.company_id == company_id)
    return query.all()

def create_position(db: Session, pos: schemas.PositionCreate, company_id: Optional[str] = None):
    pos_id = pos.id
    comp = company_id or getattr(pos, "company_id", None) or "comp-default"
    db_pos = None
    if pos_id:
        db_pos = db.query(models.Position).filter(models.Position.id == pos_id).first()

    if db_pos:
        db_pos.positionName = pos.positionName
        db_pos.departmentId = pos.departmentId
        db_pos.baseSalary = pos.baseSalary
        db_pos.status = pos.status
        db_pos.remark = pos.remark
        if comp and hasattr(db_pos, "company_id"):
            db_pos.company_id = comp
    else:
        db_pos = models.Position(
            id=pos_id or "P" + str(uuid.uuid4().int)[:6],
            company_id=comp,
            positionName=pos.positionName,
            departmentId=pos.departmentId,
            baseSalary=pos.baseSalary,
            status=pos.status,
            remark=pos.remark
        )
        db.add(db_pos)
    db.commit()
    db.refresh(db_pos)
    return db_pos

def delete_position(db: Session, pos_id: str):
    db_pos = db.query(models.Position).filter(models.Position.id == pos_id).first()
    if db_pos:
        db.delete(db_pos)
        db.commit()
        return True
    return False


# Cutting Stage CRUD
def get_cutting_stages(db: Session):
    return db.query(models.CuttingStage).all()

def create_cutting_stage(db: Session, stage: schemas.CuttingStageCreate):
    stage_id = stage.id
    db_stage = None
    if stage_id:
        db_stage = db.query(models.CuttingStage).filter(models.CuttingStage.id == stage_id).first()

    if db_stage:
        db_stage.name = stage.name
        db_stage.is_system = stage.is_system
        db_stage.price = stage.price
        db_stage.duration = stage.duration
    else:
        db_stage = models.CuttingStage(
            id=stage_id or "CS" + str(uuid.uuid4().int)[:6],
            name=stage.name,
            is_system=stage.is_system,
            price=stage.price,
            duration=stage.duration
        )
        db.add(db_stage)
    db.commit()
    db.refresh(db_stage)
    return db_stage

def delete_cutting_stage(db: Session, stage_id: str):
    db_stage = db.query(models.CuttingStage).filter(models.CuttingStage.id == stage_id).first()
    if db_stage:
        db.delete(db_stage)
        db.commit()
        return True
    return False


# Cutting Process CRUD
def get_cutting_processes(db: Session):
    return db.query(models.CuttingProcess).all()

def create_cutting_process(db: Session, proc: schemas.CuttingProcessCreate):
    proc_id = proc.id
    db_proc = None
    if proc_id:
        db_proc = db.query(models.CuttingProcess).filter(models.CuttingProcess.id == proc_id).first()

    if db_proc:
        db_proc.name = proc.name
        db_proc.remark = proc.remark
        db_proc.stages = proc.stages
    else:
        db_proc = models.CuttingProcess(
            id=proc_id or "CP" + str(uuid.uuid4().int)[:6],
            name=proc.name,
            remark=proc.remark,
            stages=proc.stages
        )
        db.add(db_proc)
    db.commit()
    db.refresh(db_proc)
    return db_proc

def delete_cutting_process(db: Session, proc_id: str):
    db_proc = db.query(models.CuttingProcess).filter(models.CuttingProcess.id == proc_id).first()
    if db_proc:
        db.delete(db_proc)
        db.commit()
        return True
    return False


# Cutting Order & Order Items CRUD
def get_cutting_orders(db: Session):
    return db.query(models.CuttingOrder).all()

def get_cutting_order(db: Session, order_id: str):
    return db.query(models.CuttingOrder).filter(models.CuttingOrder.id == order_id).first()

def create_cutting_order(db: Session, order: schemas.CuttingOrderCreate):
    order_id = order.id
    db_order = None
    if order_id:
        db_order = db.query(models.CuttingOrder).filter(models.CuttingOrder.id == order_id).first()

    total_qty = sum(item.quantity for item in order.items)

    if db_order:
        db_order.order_number = order.order_number
        db_order.project = order.project
        db_order.order_name = order.order_name
        if order.document_date:
            db_order.document_date = order.document_date
        db_order.responsible_user_ids = order.responsible_user_ids
        db_order.status = order.status
        db_order.total_quantity = total_qty
        
        # Delete old items and rewrite
        db.query(models.CuttingOrderItem).filter(models.CuttingOrderItem.orderId == db_order.id).delete()
    else:
        db_order = models.CuttingOrder(
            id=order_id or "CO" + str(uuid.uuid4().int)[:6],
            order_number=order.order_number,
            project=order.project,
            order_name=order.order_name,
            document_date=order.document_date or datetime.date.today().strftime("%Y-%m-%d"),
            responsible_user_ids=order.responsible_user_ids,
            status=order.status,
            total_quantity=total_qty
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)

    # Save new items
    for item in order.items:
        db_item = models.CuttingOrderItem(
            id=item.id or "CI" + str(uuid.uuid4().int)[:6],
            orderId=db_order.id,
            productId=item.productId,
            category=item.category,
            color=item.color,
            code=item.code,
            cuttingProcessId=item.cuttingProcessId,
            quantity=item.quantity,
            size_breakdown=item.size_breakdown,
            material_consumptions=item.material_consumptions,
            process_snapshot=item.process_snapshot
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_order)
    return db_order

def delete_cutting_order(db: Session, order_id: str):
    db_order = db.query(models.CuttingOrder).filter(models.CuttingOrder.id == order_id).first()
    if db_order:
        db.delete(db_order)
        db.commit()
        return True
    return False

def start_production_for_order(db: Session, order_id: str):
    db_order = db.query(models.CuttingOrder).filter(models.CuttingOrder.id == order_id).first()
    if not db_order:
        return False
    
    db_order.status = "in_production"
    
    # Generate CuttingTasks for each item and each stage in its technical process
    for item in db_order.items:
        stages_list = []
        if item.process_snapshot:
            stages_list = item.process_snapshot
        elif item.cutting_process and item.cutting_process.stages:
            stages_list = item.cutting_process.stages
        
        for idx, stage_data in enumerate(stages_list):
            if isinstance(stage_data, str):
                stage_id = stage_data
                raise ValueError(f"Invalid stage item structure: {stage_data}. Stages must be dictionaries.")
            elif isinstance(stage_data, dict):
                stage_id = stage_data.get("id") or stage_data.get("stageId")
            else:
                stage_id = None
            if not stage_id:
                continue
            
            db_stage = db.query(models.CuttingStage).filter(models.CuttingStage.id == stage_id).first()
            stage_name = db_stage.name if db_stage else "Unknown Stage"
            
            task_id = f"CT-{db_order.order_number}-{item.productId[:4]}-{stage_id[:4]}"
            # check if exists
            exists = db.query(models.CuttingTask).filter(models.CuttingTask.id == task_id).first()
            if not exists:
                db_task = models.CuttingTask(
                    id=task_id,
                    orderId=db_order.id,
                    orderItemId=item.id,
                    stageId=stage_id,
                    position=idx + 1,
                    quantity=item.quantity,
                    status="created",
                    order_number_snapshot=db_order.order_number,
                    order_name_snapshot=db_order.order_name,
                    process_name_snapshot=item.cutting_process.name if item.cutting_process else "Default",
                    stage_name_snapshot=stage_name,
                    product_name_snapshot=item.product.productName if item.product else "Product"
                )
                db.add(db_task)
    
    db.commit()
    db.refresh(db_order)
    return db_order


# Cutting Task CRUD
def get_cutting_tasks(db: Session):
    return db.query(models.CuttingTask).all()

def update_cutting_task_status(db: Session, task_id: str, status: str):
    db_task = db.query(models.CuttingTask).filter(models.CuttingTask.id == task_id).first()
    if db_task:
        db_task.status = status
        db.commit()
        db.refresh(db_task)
        return db_task
    return None


# Cutting Task Execution CRUD
def get_cutting_task_executions(db: Session):
    return db.query(models.CuttingTaskExecution).all()

def create_cutting_task_execution(db: Session, exe: schemas.CuttingTaskExecutionCreate):
    db_exe = models.CuttingTaskExecution(
        id="CTE" + str(uuid.uuid4().int)[:6],
        taskId=exe.taskId,
        workerId=exe.workerId,
        quantity=exe.quantity,
        period_month=exe.period_month or datetime.datetime.now().strftime("%Y-%m"),
        comment=exe.comment
    )
    db.add(db_exe)
    
    # Update task status to in_progress or completed
    db_task = db.query(models.CuttingTask).filter(models.CuttingTask.id == exe.taskId).first()
    if db_task:
        total_executed = db.query(models.CuttingTaskExecution).filter(models.CuttingTaskExecution.taskId == exe.taskId).all()
        executed_qty = sum(e.quantity for e in total_executed) + exe.quantity
        if executed_qty >= db_task.quantity:
            db_task.status = "completed"
        else:
            db_task.status = "in_progress"
        
        # Cascade to order status
        if db_task.orderId:
            all_tasks = db.query(models.CuttingTask).filter(models.CuttingTask.orderId == db_task.orderId).all()
            if all_tasks:
                if all(t.status == "completed" for t in all_tasks):
                    db_task.order.status = "completed"
                elif any(t.status in ("in_progress", "completed") for t in all_tasks):
                    db_task.order.status = "in_progress"
            
    db.commit()
    db.refresh(db_exe)
    return db_exe

def delete_cutting_task_execution(db: Session, exe_id: str):
    db_exe = db.query(models.CuttingTaskExecution).filter(models.CuttingTaskExecution.id == exe_id).first()
    if db_exe:
        db.delete(db_exe)
        db.commit()
        return True
    return False


# QR Code CRUD
def get_qr_codes(db: Session):
    return db.query(models.QrCode).all()

def generate_ulid() -> str:
    import time
    import random
    encoding = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    timestamp = int(time.time() * 1000)
    ts_chars = []
    for _ in range(10):
        ts_chars.append(encoding[timestamp % 32])
        timestamp //= 32
    ts_chars.reverse()
    rand_chars = [random.choice(encoding) for _ in range(16)]
    return "".join(ts_chars) + "".join(rand_chars)

def generate_qr_code_for_task(db: Session, qr: schemas.QrCodeCreate):
    code_str = generate_ulid()
    db_qr = models.QrCode(
        id="QR" + str(uuid.uuid4().int)[:6],
        code=code_str,
        taskId=qr.taskId,
        quantity=qr.quantity,
        status=qr.status or "created",
        workerId=qr.workerId
    )
    db.add(db_qr)
    db.commit()
    db.refresh(db_qr)
    return db_qr

def delete_qr_code(db: Session, qr_id: str):
    db_qr = db.query(models.QrCode).filter(models.QrCode.id == qr_id).first()
    if db_qr:
        db.delete(db_qr)
        db.commit()
        return True
    return False


# Staff Adjustment CRUD
def get_staff_adjustments(db: Session, company_id: Optional[str] = None):
    query = db.query(models.StaffAdjustment)
    if company_id:
        query = query.filter(models.StaffAdjustment.company_id == company_id)
    return query.all()

def create_staff_adjustment(db: Session, adj: schemas.StaffAdjustmentCreate, company_id: Optional[str] = None):
    adj_id = adj.id
    comp = company_id or getattr(adj, "company_id", None) or "comp-default"
    db_adj = None
    if adj_id:
        db_adj = db.query(models.StaffAdjustment).filter(models.StaffAdjustment.id == adj_id).first()

    if db_adj:
        db_adj.workerId = adj.workerId
        db_adj.document_type = adj.document_type
        db_adj.amount = adj.amount
        db_adj.period_month = adj.period_month
        db_adj.description = adj.description
        if comp and hasattr(db_adj, "company_id"):
            db_adj.company_id = comp
    else:
        db_adj = models.StaffAdjustment(
            id=adj_id or "ADJ" + str(uuid.uuid4().int)[:6],
            company_id=comp,
            workerId=adj.workerId,
            document_type=adj.document_type,
            amount=adj.amount,
            period_month=adj.period_month or datetime.datetime.now().strftime("%Y-%m"),
            description=adj.description
        )
        db.add(db_adj)
    db.commit()
    db.refresh(db_adj)
    return db_adj

def delete_staff_adjustment(db: Session, adj_id: str):
    db_adj = db.query(models.StaffAdjustment).filter(models.StaffAdjustment.id == adj_id).first()
    if db_adj:
        db.delete(db_adj)
        db.commit()
        return True
    return False


# Staff Timesheet CRUD
def get_staff_timesheets(db: Session, company_id: Optional[str] = None):
    query = db.query(models.StaffTimesheet)
    if company_id:
        query = query.filter(models.StaffTimesheet.company_id == company_id)
    return query.all()

def create_staff_timesheet(db: Session, ts: schemas.StaffTimesheetCreate, company_id: Optional[str] = None):
    ts_id = ts.id
    comp = company_id or getattr(ts, "company_id", None) or "comp-default"
    db_ts = None
    if ts_id:
        db_ts = db.query(models.StaffTimesheet).filter(models.StaffTimesheet.id == ts_id).first()

    if db_ts:
        db_ts.date = ts.date
        db_ts.status = ts.status
        db_ts.records = ts.records
        if comp and hasattr(db_ts, "company_id"):
            db_ts.company_id = comp
    else:
        db_ts = models.StaffTimesheet(
            id=ts_id or "TS" + str(uuid.uuid4().int)[:6],
            company_id=comp,
            date=ts.date,
            status=ts.status,
            records=ts.records
        )
        db.add(db_ts)
    db.commit()
    db.refresh(db_ts)
    return db_ts

def delete_staff_timesheet(db: Session, ts_id: str):
    db_ts = db.query(models.StaffTimesheet).filter(models.StaffTimesheet.id == ts_id).first()
    if db_ts:
        db.delete(db_ts)
        db.commit()
        return True
    return False


# Staff Output CRUD
def get_staff_outputs(db: Session, company_id: Optional[str] = None):
    query = db.query(models.StaffOutput)
    if company_id:
        query = query.filter(models.StaffOutput.company_id == company_id)
    return query.all()

def create_staff_output(db: Session, out: schemas.StaffOutputCreate, company_id: Optional[str] = None):
    out_id = out.id
    comp = company_id or getattr(out, "company_id", None) or "comp-default"
    db_out = None
    if out_id:
        db_out = db.query(models.StaffOutput).filter(models.StaffOutput.id == out_id).first()

    worker_name = out.workerName or out.workerId

    if db_out:
        db_out.workerId = out.workerId or worker_name
        db_out.workerName = worker_name
        db_out.name = out.name
        db_out.amount = out.amount
        db_out.period_month = out.period_month
        db_out.comment = out.comment
        if comp and hasattr(db_out, "company_id"):
            db_out.company_id = comp
    else:
        db_out = models.StaffOutput(
            id=out_id or "OUT" + str(uuid.uuid4().int)[:6],
            company_id=comp,
            workerId=out.workerId or worker_name,
            workerName=worker_name,
            name=out.name,
            amount=out.amount,
            period_month=out.period_month or datetime.datetime.now().strftime("%Y-%m-%d"),
            comment=out.comment
        )
        db.add(db_out)
    db.commit()
    db.refresh(db_out)
    return db_out

def delete_staff_output(db: Session, out_id: str):
    db_out = db.query(models.StaffOutput).filter(models.StaffOutput.id == out_id).first()
    if db_out:
        db.delete(db_out)
        db.commit()
        return True
    return False

def save_department_user(db: Session, user_data: schemas.DepartmentUserSave):
    # Resolve the department ID from the request
    dept_id = None
    dept = user_data.department
    if dept is not None:
        if isinstance(dept, (str, int)):
            dept_id = str(dept)
        elif isinstance(dept, dict):
            for k in ['id', 'department_id', 'departmentId']:
                if k in dept and dept[k] is not None:
                    dept_id = str(dept[k])
                    break
        elif hasattr(dept, 'id') and getattr(dept, 'id') is not None:
            dept_id = str(getattr(dept, 'id'))
            
    if dept_id is None:
        for field in ['department_id', 'departmentId']:
            val = getattr(user_data, field, None)
            if val is not None:
                dept_id = str(val)
                break

    # Resolve role names/IDs dynamically from the Role table
    role_id_str = str(user_data.roleId) if user_data.roleId is not None else None
    role_str = user_data.role

    db_role_match = None
    if role_id_str:
        db_role_match = db.query(models.Role).filter(models.Role.id == role_id_str).first()
    if not db_role_match and role_str:
        db_role_match = db.query(models.Role).filter(
            (models.Role.roleName.ilike(role_str)) |
            (models.Role.id == role_str)
        ).first()

    if db_role_match:
        resolved_role_id = db_role_match.id
        resolved_role = db_role_match.roleName
    else:
        resolved_role_id = role_id_str or "3"
        resolved_role = role_str or "worker"

    # Query if the user exists by id.
    db_user = None
    if user_data.id is not None:
        db_user = db.query(models.User).filter(models.User.id == user_data.id).first()

    if db_user:
        # If they do, update their username, email, department_id, role, and roleId.
        db_user.username = user_data.username
        db_user.email = user_data.email
        db_user.department_id = dept_id
        db_user.role = resolved_role
        db_user.roleId = resolved_role_id
        if user_data.password:
            db_user.hashed_password = get_password_hash(user_data.password)
    else:
        # If the user does not exist, create a new user in the database.
        pwd = user_data.password if user_data.password else "123456"
        hashed_password = get_password_hash(pwd)
        
        user_kwargs = {
            "username": user_data.username,
            "hashed_password": hashed_password,
            "role": resolved_role,
            "roleId": resolved_role_id,
            "email": user_data.email,
            "department_id": dept_id,
            "permissions": []
        }
        if user_data.id is not None:
            user_kwargs["id"] = user_data.id
            
        db_user = models.User(**user_kwargs)
        db.add(db_user)
        
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_department_users(db: Session, user_ids: list):
    db.query(models.User).filter(models.User.id.in_(user_ids)).delete(synchronize_session=False)
    db.commit()


# Classifier CRUD & High Performance Caching
_classifier_cache = {}

def get_classifier_items(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search: str = None,
    brand: str = None,
    mxik_code: str = None,
    shtrix_code: str = None
):
    cache_key = (search, brand, mxik_code, shtrix_code, page, page_size)
    if cache_key in _classifier_cache:
        cached_ids, cached_total = _classifier_cache[cache_key]
        if cached_ids:
            items = db.query(models.ClassifierItem).filter(models.ClassifierItem.id.in_(cached_ids)).all()
            # Preserve cached ID order
            item_map = {it.id: it for it in items}
            ordered = [item_map[i] for i in cached_ids if i in item_map]
            return ordered, cached_total
        return [], cached_total

    query = db.query(models.ClassifierItem)
    if search:
        s = search.strip()
        if s.isdigit():
            # Super-fast index prefix match for barcodes/MXIK codes
            query = query.filter(
                or_(
                    models.ClassifierItem.shtrix_code.startswith(s),
                    models.ClassifierItem.mxik_code.startswith(s)
                )
            )
        else:
            tokens = [t.lower() for t in s.split() if t]
            if len(tokens) == 1:
                # Fast indexed single word match
                tok = tokens[0]
                pat = f"%{tok}%"
                query = query.filter(
                    or_(
                        models.ClassifierItem.brand_name.ilike(pat),
                        models.ClassifierItem.position_name.ilike(pat),
                        models.ClassifierItem.attribute_name.ilike(pat),
                        models.ClassifierItem.mxik_name.ilike(pat)
                    )
                )
            else:
                for token in tokens:
                    t_dot = token.replace(',', '.')
                    t_comma = token.replace('.', ',')
                    conds = []
                    for t in set([token, t_dot, t_comma]):
                        pat = f"%{t}%"
                        conds.append(models.ClassifierItem.brand_name.ilike(pat))
                        conds.append(models.ClassifierItem.position_name.ilike(pat))
                        conds.append(models.ClassifierItem.attribute_name.ilike(pat))
                        conds.append(models.ClassifierItem.mxik_name.ilike(pat))
                    query = query.filter(or_(*conds))

    if brand:
        query = query.filter(models.ClassifierItem.brand_name.ilike(f"%{brand.strip()}%"))
    if mxik_code:
        query = query.filter(models.ClassifierItem.mxik_code == mxik_code.strip())
    if shtrix_code:
        query = query.filter(models.ClassifierItem.shtrix_code == shtrix_code.strip())

    # Fast fetch without expensive count over 411k rows when page is 1
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    total = len(items) if len(items) < page_size and page == 1 else 100

    item_ids = [it.id for it in items]
    if len(_classifier_cache) > 4096:
        _classifier_cache.clear()
    _classifier_cache[cache_key] = (item_ids, total)

    return items, total


def get_classifier_by_id(db: Session, item_id: int):
    return db.query(models.ClassifierItem).filter(models.ClassifierItem.id == item_id).first()

def get_classifier_by_barcode(db: Session, shtrix_code: str):
    code = shtrix_code.strip()
    item = db.query(models.ClassifierItem).filter(models.ClassifierItem.shtrix_code == code).first()
    if not item:
        item = db.query(models.ClassifierItem).filter(models.ClassifierItem.mxik_code == code).first()
    return item

def get_classifier_by_mxik(db: Session, mxik_code: str):
    return db.query(models.ClassifierItem).filter(models.ClassifierItem.mxik_code == mxik_code.strip()).first()


# Device Token CRUD
def create_device_token(db: Session, user_id: int, device_name: str) -> models.DeviceToken:
    token_str = f"devtok_{secrets.token_urlsafe(32)}"
    pair_code = f"PAIR-{secrets.randbelow(900000) + 100000}"
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    db_obj = models.DeviceToken(
        user_id=user_id,
        device_name=device_name,
        token=token_str,
        pair_code=pair_code,
        expires_at=expires_at,
        status="active",
        created_at=datetime.datetime.utcnow()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_user_device_tokens(db: Session, user_id: int, status: str | None = None) -> list[models.DeviceToken]:
    query = db.query(models.DeviceToken).filter(models.DeviceToken.user_id == user_id)
    if status is not None:
        query = query.filter(models.DeviceToken.status == status)
    return query.all()

def get_device_token_by_token(db: Session, token: str) -> models.DeviceToken | None:
    clean_token = token.strip()
    clean_pair = clean_token.replace("PAIR-", "").replace("pair-", "")
    return db.query(models.DeviceToken).filter(
        (models.DeviceToken.token == clean_token) |
        (models.DeviceToken.pair_code == clean_token) |
        (models.DeviceToken.pair_code == f"PAIR-{clean_pair}") |
        (models.DeviceToken.pair_code == clean_pair)
    ).first()

def get_device_token_by_id(db: Session, device_id: int, user_id: int | None = None) -> models.DeviceToken | None:
    query = db.query(models.DeviceToken).filter(models.DeviceToken.id == device_id)
    if user_id is not None:
        query = query.filter(models.DeviceToken.user_id == user_id)
    return query.first()

def revoke_device_token(db: Session, device_id: int, user_id: int | None = None) -> models.DeviceToken | None:
    db_obj = get_device_token_by_id(db, device_id=device_id, user_id=user_id)
    if db_obj:
        db_obj.status = "revoked"
        db.commit()
        db.refresh(db_obj)
    return db_obj

def update_device_token_last_used(db: Session, device_token: models.DeviceToken):
    device_token.last_used_at = datetime.datetime.utcnow()
    db.commit()

# =========================================================
# Company & Multi-Tenancy CRUD
# =========================================================

def get_companies(db: Session):
    companies = db.query(models.Company).order_by(models.Company.created_at.desc()).all()
    results = []
    now_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    for c in companies:
        u_count = db.query(models.User).filter(models.User.company_id == c.id).count()
        w_count = db.query(models.Worker).filter(models.Worker.company_id == c.id).count()
        p_count = db.query(models.Product).filter(models.Product.company_id == c.id).count()
        s_count = db.query(models.Sale).filter(models.Sale.company_id == c.id).count()
        revenue = db.query(func.coalesce(func.sum(models.Sale.paid_amount), 0.0)).filter(models.Sale.company_id == c.id).scalar() or 0.0
        
        is_expired = False
        if c.subscription_expires_at:
            is_expired = c.subscription_expires_at < now_str

        # Default features per plan
        base_features = {"ai": True, "upcoming": True, "advanced_analytics": True} if c.plan == "pro" else {"ai": False, "upcoming": False, "advanced_analytics": False}
        merged_features = {**base_features, **(c.features or {})}

        admin_u = db.query(models.User).filter(
            models.User.company_id == c.id,
            models.User.username != 'admin'
        ).order_by(models.User.id.asc()).first()
        if not admin_u and c.id == 'comp-default':
            admin_u = db.query(models.User).filter(models.User.username == 'admin').first()

        results.append({
            "id": c.id,
            "name": c.name,
            "code": c.code,
            "plan": c.plan or "basic",
            "billing_cycle": c.billing_cycle or "monthly",
            "subscription_expires_at": c.subscription_expires_at,
            "status": c.status if c.status is not None else 1,
            "max_users": c.max_users or 10,
            "phone": c.phone,
            "email": c.email,
            "address": c.address,
            "features": merged_features,
            "created_at": c.created_at,
            "admin_username": admin_u.username if admin_u else "",
            "admin_full_name": (admin_u.full_name or admin_u.username) if admin_u else "",
            "admin_id": admin_u.id if admin_u else None,
            "employees_count": w_count + u_count,
            "workers_count": w_count,
            "users_count": u_count,
            "products_count": p_count,
            "total_sales_count": s_count,
            "total_revenue": float(revenue),
            "is_expired": is_expired
        })
    return results

def get_company_by_id(db: Session, company_id: str):
    return db.query(models.Company).filter(models.Company.id == company_id).first()

def get_company_by_code(db: Session, code: str):
    return db.query(models.Company).filter(models.Company.code == code).first()

def create_or_update_company(db: Session, comp_in: schemas.CompanyCreate):
    comp_id = getattr(comp_in, "id", None)
    db_comp = None
    if comp_id:
        db_comp = db.query(models.Company).filter(models.Company.id == comp_id).first()
    if not db_comp and comp_in.code:
        db_comp = db.query(models.Company).filter(models.Company.code == comp_in.code.strip()).first()

    now = datetime.datetime.utcnow()
    # Default expires: 1 month or 1 year
    if not comp_in.subscription_expires_at:
        if comp_in.billing_cycle == "yearly":
            default_exp = (now + datetime.timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            default_exp = (now + datetime.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    else:
        default_exp = comp_in.subscription_expires_at

    plan_features = {"ai": True, "upcoming": True} if comp_in.plan == "pro" else {"ai": False, "upcoming": False}
    final_features = {**plan_features, **(comp_in.features or {})}

    if db_comp:
        db_comp.name = comp_in.name
        db_comp.code = comp_in.code.strip()
        db_comp.plan = comp_in.plan or db_comp.plan
        db_comp.billing_cycle = comp_in.billing_cycle or db_comp.billing_cycle
        if comp_in.subscription_expires_at:
            db_comp.subscription_expires_at = comp_in.subscription_expires_at
        if comp_in.status is not None:
            db_comp.status = comp_in.status
        if comp_in.max_users:
            db_comp.max_users = comp_in.max_users
        if comp_in.phone is not None:
            db_comp.phone = comp_in.phone
        if comp_in.email is not None:
            db_comp.email = comp_in.email
        if comp_in.address is not None:
            db_comp.address = comp_in.address
        if comp_in.features is not None:
            db_comp.features = final_features
        db.commit()
        db.refresh(db_comp)
    else:
        new_id = comp_id or f"comp-{uuid.uuid4().hex[:8]}"
        db_comp = models.Company(
            id=new_id,
            name=comp_in.name,
            code=comp_in.code.strip(),
            plan=comp_in.plan or "basic",
            billing_cycle=comp_in.billing_cycle or "monthly",
            subscription_expires_at=default_exp,
            status=comp_in.status if comp_in.status is not None else 1,
            max_users=comp_in.max_users or 10,
            phone=comp_in.phone,
            email=comp_in.email,
            address=comp_in.address,
            features=final_features,
            created_at=now.strftime("%Y-%m-%d %H:%M:%S")
        )
        db.add(db_comp)
        db.commit()
        db.refresh(db_comp)

        # Seed isolated default roles for this new company
        seed_default_roles_for_company(db, new_id)
        if isinstance(db_comp.features, dict):
            db_comp.features["roles_initialized"] = True
            db.commit()

    # Optional initial company admin user creation or password update
    if comp_in.admin_username and comp_in.admin_password:
        clean_user = comp_in.admin_username.strip().lower()
        existing_u = db.query(models.User).filter(models.User.username == clean_user).first()
        hashed = get_password_hash(comp_in.admin_password)
        company_permissions = [
            "/dashboard", "/dashboard/analysis", "/dashboard/workplace",
            "/product", "/product/list",
            "/sales", "/sales/pos", "/sales/debtors",
            "/hr", "/hr/workers", "/hr/timesheets", "/hr/outputs", "/hr/adjustments", "/hr/salary"
        ]
        if not existing_u:
            new_u = models.User(
                username=clean_user,
                hashed_password=hashed,
                full_name=comp_in.admin_full_name or f"{comp_in.name} Administrator",
                role="Administrator",
                roleId="10",
                company_id=db_comp.id,
                permissions=company_permissions,
                create_time=now.strftime("%Y-%m-%d %H:%M:%S")
            )
            db.add(new_u)
            db.commit()
        else:
            existing_u.company_id = db_comp.id
            existing_u.hashed_password = hashed
            if comp_in.admin_full_name:
                existing_u.full_name = comp_in.admin_full_name
            db.commit()

    return db_comp

def update_company_tier(db: Session, tier_in: schemas.CompanyTierUpdate):
    comp = db.query(models.Company).filter(models.Company.id == tier_in.company_id).first()
    if not comp:
        return None

    now = datetime.datetime.utcnow()
    comp.plan = tier_in.plan
    if tier_in.billing_cycle:
        comp.billing_cycle = tier_in.billing_cycle

    if tier_in.max_users is not None:
        comp.max_users = tier_in.max_users

    # Features: grant AI + upcoming to Pro, remove from Basic unless overridden
    plan_features = {"ai": True, "upcoming": True} if tier_in.plan == "pro" else {"ai": False, "upcoming": False}
    comp.features = {**plan_features, **(tier_in.features or {})}

    # Adjust expiration
    if tier_in.subscription_expires_at:
        comp.subscription_expires_at = tier_in.subscription_expires_at
    elif tier_in.duration_months:
        # If currently active, extend from current expiration; otherwise extend from now
        base_date = now
        if comp.subscription_expires_at:
            try:
                parsed = datetime.datetime.strptime(comp.subscription_expires_at, "%Y-%m-%d %H:%M:%S")
                if parsed > now:
                    base_date = parsed
            except Exception:
                base_date = now
        days = int(tier_in.duration_months * 30.5)
        comp.subscription_expires_at = (base_date + datetime.timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

    db.commit()
    db.refresh(comp)
    return comp

def delete_company(db: Session, company_id: str):
    comp = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not comp:
        return False

    # Detach or delete associated records
    db.query(models.ProductPackaging).filter(models.ProductPackaging.product_id.in_(
        db.query(models.Product.id).filter(models.Product.company_id == company_id)
    )).delete(synchronize_session=False)

    db.query(models.SaleItem).filter(models.SaleItem.sale_id.in_(
        db.query(models.Sale.id).filter(models.Sale.company_id == company_id)
    )).delete(synchronize_session=False)

    db.query(models.Product).filter(models.Product.company_id == company_id).delete(synchronize_session=False)
    db.query(models.Sale).filter(models.Sale.company_id == company_id).delete(synchronize_session=False)
    db.query(models.Worker).filter(models.Worker.company_id == company_id).delete(synchronize_session=False)
    db.query(models.Department).filter(models.Department.company_id == company_id).delete(synchronize_session=False)
    db.query(models.Branch).filter(models.Branch.company_id == company_id).delete(synchronize_session=False)
    db.query(models.User).filter(models.User.company_id == company_id).delete(synchronize_session=False)

    db.delete(comp)
    db.commit()
    return True

    db.refresh(device_token)
    return device_token




