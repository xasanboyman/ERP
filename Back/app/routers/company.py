import datetime
import time
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Header, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import crud, schemas, models
from app.routers.auth import decode_access_token
from app.routers.activity import log_activity

router = APIRouter(prefix="/company", tags=["Company Management"])

def get_current_user_from_header(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        return None
    payload = decode_access_token(authorization)
    if not payload or "sub" not in payload or "error" in payload:
        return None
    return db.query(models.User).filter(models.User.username == payload["sub"]).first()

def require_super_admin(authorization: str = Header(None), db: Session = Depends(get_db)):
    user = get_current_user_from_header(authorization, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autentifikatsiyadan o'tilmagan. Iltimos, qayta tizimga kiring."
        )
    role_str = (user.role or "").lower()
    is_super = (
        getattr(user, "is_super_admin", False) is True
        or "super" in role_str
        or user.username in ["admin", "anvars"]
    )
    if not is_super:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kompaniyalarni boshqarish faqat Super Administrator uchun ruxsat etilgan."
        )
    return user


@router.get("/list")
def list_companies(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    require_super_admin(authorization, db)
    data = crud.get_companies(db)
    return {
        "code": 0,
        "message": "success",
        "data": {
            "total": len(data),
            "list": data
        }
    }


@router.get("/current")
def get_current_company(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_header(authorization, db)
    if not user:
        raise HTTPException(status_code=401, detail="Sessiya yaroqsiz")

    role_str = (user.role or "").lower()
    is_super = "super" in role_str or user.username in ["admin", "anvars"]

    company_id = getattr(user, "company_id", None) or "comp-default"
    company = crud.get_company_by_id(db, company_id)

    if not company:
        company = crud.get_company_by_id(db, "comp-default")

    plan = getattr(company, "plan", "basic") if company else ("pro" if is_super else "basic")
    features = getattr(company, "features", {}) if company else {}
    if is_super:
        plan = "pro"
        features = {"ai": True, "upcoming": True, "advanced_analytics": True}

    return {
        "code": 0,
        "data": {
            "company_id": getattr(company, "id", "comp-default"),
            "name": getattr(company, "name", "Bosh Korxona"),
            "code": getattr(company, "code", "default"),
            "plan": plan,
            "billing_cycle": getattr(company, "billing_cycle", "monthly"),
            "subscription_expires_at": getattr(company, "subscription_expires_at", None),
            "status": getattr(company, "status", 1),
            "features": features,
            "is_super_admin": is_super
        }
    }


@router.get("/detail/{company_id}")
def get_company_detail(
    company_id: str,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    require_super_admin(authorization, db)
    comp = crud.get_company_by_id(db, company_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Kompaniya topilmadi")

    # Query Workers & Users
    workers = db.query(models.Worker).filter(models.Worker.company_id == comp.id).order_by(models.Worker.id.desc()).all()
    users = db.query(models.User).filter(models.User.company_id == comp.id).order_by(models.User.id.desc()).all()

    # Query Sales & Financials
    sales = db.query(models.Sale).filter(models.Sale.company_id == comp.id).order_by(models.Sale.id.desc()).all()
    total_sales_count = len(sales)
    total_revenue = sum(float(s.paid_amount or 0.0) for s in sales)
    total_sales_amount = sum(float(s.total_amount or 0.0) for s in sales)
    total_debt = sum(float(s.debt_amount or 0.0) for s in sales)
    debtors_count = len([s for s in sales if float(s.debt_amount or 0.0) > 0])

    # Query Products & Inventory
    products = db.query(models.Product).filter(models.Product.company_id == comp.id).order_by(models.Product.id.desc()).all()
    products_count = len(products)
    total_stock = sum(float(getattr(p, 'quantityInStock', None) or 0.0) for p in products)
    inventory_value = sum(float(getattr(p, 'quantityInStock', None) or 0.0) * float(p.price or 0.0) for p in products)

    # Expiry Check
    now_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    is_expired = False
    if comp.subscription_expires_at:
        is_expired = comp.subscription_expires_at < now_str

    total_employees = len(workers) + len(users)
    max_users = comp.max_users or 10
    usage_percent = min(100, int((total_employees / max_users) * 100)) if max_users > 0 else 0

    admin_u = None
    for u in users:
        if u.username != 'admin':
            admin_u = u
            break
    if not admin_u and comp.id == 'comp-default':
        admin_u = db.query(models.User).filter(models.User.username == 'admin').first()
    elif not admin_u and users:
        admin_u = users[0]

    admin_info = {
        "id": admin_u.id,
        "username": admin_u.username,
        "full_name": admin_u.full_name or admin_u.username,
        "role": admin_u.role or "Administrator",
        "email": admin_u.email or "",
        "phone": getattr(admin_u, "phone", "") or ""
    } if admin_u else None

    return {
        "code": 0,
        "data": {
            "id": comp.id,
            "name": comp.name,
            "code": comp.code,
            "plan": comp.plan or "basic",
            "billing_cycle": comp.billing_cycle or "monthly",
            "subscription_expires_at": comp.subscription_expires_at,
            "status": comp.status if comp.status is not None else 1,
            "max_users": max_users,
            "usage_percent": usage_percent,
            "phone": comp.phone,
            "email": comp.email,
            "address": comp.address,
            "features": comp.features or {},
            "created_at": comp.created_at,
            "is_expired": is_expired,
            "admin_user": admin_info,
            "admin_username": admin_info["username"] if admin_info else "",
            "admin_full_name": admin_info["full_name"] if admin_info else "",
            "stats": {
                "employees_count": total_employees,
                "workers_count": len(workers),
                "users_count": len(users),
                "max_users": max_users,
                "usage_percent": usage_percent,
                "products_count": products_count,
                "total_stock": total_stock,
                "inventory_value": inventory_value,
                "total_sales_count": total_sales_count,
                "total_revenue": total_revenue,
                "total_sales_amount": total_sales_amount,
                "total_debt": total_debt,
                "debtors_count": debtors_count
            },
            "workers": [
                {
                    "id": w.id,
                    "name": w.name or "",
                    "role": w.role or "Xodim",
                    "phone": w.phone or "",
                    "account": w.account or "",
                    "employee_code": w.employee_code or "",
                    "department": w.departmentId or "",
                    "hireDate": w.hireDate or "",
                    "status": w.status if w.status is not None else 1,
                    "baseSalary": float(w.baseSalary or 0.0),
                    "company_id": w.company_id
                }
                for w in workers
            ],
            "users": [
                {
                    "id": u.id,
                    "username": u.username,
                    "full_name": u.full_name or u.username,
                    "role": u.role or "Foydalanuvchi",
                    "email": u.email or "",
                    "phone": u.phone or "",
                    "company_id": u.company_id
                }
                for u in users
            ],
            "recent_sales": [
                {
                    "id": s.id,
                    "customer_name": s.customer_name or "Xaridor",
                    "customer_phone": s.customer_phone or "",
                    "total_amount": float(s.total_amount or 0.0),
                    "paid_amount": float(s.paid_amount or 0.0),
                    "debt_amount": float(s.debt_amount or 0.0),
                    "createTime": getattr(s, "createTime", None) or ""
                }
                for s in sales[:10]
            ],
            "top_products": [
                {
                    "id": p.id,
                    "productName": p.productName or "",
                    "category": p.category or "",
                    "price": float(p.price or 0.0),
                    "stock": float(getattr(p, 'quantityInStock', None) or 0.0),
                    "unit": p.unit or "dona"
                }
                for p in products[:10]
            ]
        }
    }


@router.post("/save")
def save_company(
    comp_in: schemas.CompanyCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    admin_user = require_super_admin(authorization, db)
    is_new = not bool(comp_in.id)
    comp = crud.create_or_update_company(db, comp_in)

    log_activity(
        db,
        actor=admin_user.username,
        action="created" if is_new else "updated",
        entity="company",
        entity_id=comp.id,
        entity_name=comp.name
    )

    return {
        "code": 0,
        "message": "Kompaniya muvaffaqiyatli saqlandi",
        "data": {
            "id": comp.id,
            "name": comp.name,
            "code": comp.code,
            "plan": comp.plan,
            "billing_cycle": comp.billing_cycle,
            "subscription_expires_at": comp.subscription_expires_at,
            "status": comp.status
        }
    }


@router.post("/tier")
def update_tier(
    tier_in: schemas.CompanyTierUpdate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    admin_user = require_super_admin(authorization, db)
    comp = crud.update_company_tier(db, tier_in)
    if not comp:
        raise HTTPException(status_code=404, detail="Kompaniya topilmadi")

    log_activity(
        db,
        actor=admin_user.username,
        action="tier_updated",
        entity="company",
        entity_id=comp.id,
        entity_name=f"{comp.name} -> {comp.plan.upper()}"
    )

    return {
        "code": 0,
        "message": f"Kompaniya tarifi '{comp.plan.upper()}' ga o'zgartirildi",
        "data": {
            "id": comp.id,
            "name": comp.name,
            "plan": comp.plan,
            "billing_cycle": comp.billing_cycle,
            "subscription_expires_at": comp.subscription_expires_at,
            "features": comp.features
        }
    }


@router.post("/delete")
def delete_company_endpoint(
    body: dict = Body(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    admin_user = require_super_admin(authorization, db)
    comp_id = body.get("id") or body.get("company_id")
    if not comp_id:
        raise HTTPException(status_code=400, detail="Kompaniya ID ko'rsatilmadi")

    if comp_id == "comp-default":
        raise HTTPException(status_code=400, detail="Asosiy bosh korxonani o'chirib bo'lmaydi")

    admin_password = body.get("admin_password")
    if not admin_password or not str(admin_password).strip():
        raise HTTPException(status_code=400, detail="Kompaniyani o'chirish uchun Super Admin parolini kiritish shart!")

    if not crud.verify_password(str(admin_password).strip(), admin_user.hashed_password):
        raise HTTPException(status_code=400, detail="Super Admin paroli noto'g'ri!")

    comp = crud.get_company_by_id(db, comp_id)
    comp_name = comp.name if comp else comp_id

    success = crud.delete_company(db, comp_id)
    if not success:
        raise HTTPException(status_code=404, detail="Kompaniya topilmadi")

    log_activity(
        db,
        actor=admin_user.username,
        action="deleted",
        entity="company",
        entity_id=comp_id,
        entity_name=comp_name
    )

    return {"code": 0, "message": f"'{comp_name}' kompaniyasi va uning barcha ma'lumotlari muvaffaqiyatli o'chirildi"}


@router.post("/status")
def toggle_company_status(
    body: dict = Body(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    admin_user = require_super_admin(authorization, db)
    comp_id = body.get("company_id") or body.get("id")
    if not comp_id:
        raise HTTPException(status_code=400, detail="Kompaniya ID ko'rsatilmadi")
    status_val = int(body.get("status", 1))

    comp = crud.get_company_by_id(db, comp_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Kompaniya topilmadi")

    comp.status = status_val
    db.commit()
    db.refresh(comp)

    log_activity(
        db,
        actor=admin_user.username,
        action="status_updated",
        entity="company",
        entity_id=comp.id,
        entity_name=f"{comp.name} -> {'Faol' if status_val == 1 else 'To\'xtatilgan'}"
    )

    return {
        "code": 0,
        "message": f"Kompaniya holati {'faollashtirildi' if status_val == 1 else 'to\'xtatildi'}",
        "data": {"id": comp.id, "status": comp.status}
    }


@router.post("/employee/save")
def save_company_employee(
    data: dict = Body(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    admin_user = require_super_admin(authorization, db)
    company_id = data.get("company_id")
    if not company_id:
        raise HTTPException(status_code=400, detail="Kompaniya ID ko'rsatilmadi")

    comp = crud.get_company_by_id(db, company_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Kompaniya topilmadi")

    emp_id = data.get("id")
    if not emp_id:
        w_cnt = db.query(models.Worker).filter(models.Worker.company_id == company_id).count()
        u_cnt = db.query(models.User).filter(models.User.company_id == company_id).count()
        if comp.max_users and (w_cnt + u_cnt) >= comp.max_users:
            raise HTTPException(
                status_code=400,
                detail=f"Xodimlar limiti to'lgan ({w_cnt + u_cnt}/{comp.max_users}). Iltimos, tarifni yoki limitni oshiring."
            )

    worker = None
    if emp_id:
        worker = db.query(models.Worker).filter(models.Worker.id == str(emp_id)).first()

    now_ts = int(time.time() * 1000)
    if not worker:
        auto_id = f"w_{now_ts}"
        worker = models.Worker(id=auto_id, company_id=company_id)
        db.add(worker)

    worker.name = data.get("name") or worker.name or "Nomsiz xodim"
    worker.role = data.get("role") or worker.role or "Mutaxassis"
    worker.phone = data.get("phone") or worker.phone or ""
    worker.account = data.get("account") or worker.account or f"usr_{now_ts % 10000}"
    worker.employee_code = data.get("employee_code") or worker.employee_code or f"EMP-{now_ts % 100000}"
    worker.departmentId = data.get("department") or data.get("departmentId") or worker.departmentId or ""
    worker.status = int(data.get("status", 1))
    if data.get("hireDate"):
        worker.hireDate = data.get("hireDate")
    if data.get("baseSalary"):
        worker.baseSalary = float(data.get("baseSalary"))

    db.commit()
    db.refresh(worker)

    log_activity(
        db,
        actor=admin_user.username,
        action="saved_employee",
        entity="worker",
        entity_id=worker.id,
        entity_name=f"{worker.name} ({comp.name})"
    )

    return {
        "code": 0,
        "message": "Xodim muvaffaqiyatli saqlandi",
        "data": {
            "id": worker.id,
            "name": worker.name,
            "role": worker.role,
            "phone": worker.phone,
            "account": worker.account,
            "status": worker.status,
            "company_id": worker.company_id
        }
    }


@router.post("/employee/delete")
def delete_company_employee(
    data: dict = Body(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    admin_user = require_super_admin(authorization, db)
    emp_id = data.get("id")
    if not emp_id:
        raise HTTPException(status_code=400, detail="Xodim ID ko'rsatilmadi")

    worker = db.query(models.Worker).filter(models.Worker.id == str(emp_id)).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Xodim topilmadi")

    w_name = worker.name
    db.delete(worker)
    db.commit()

    log_activity(
        db,
        actor=admin_user.username,
        action="deleted_employee",
        entity="worker",
        entity_id=str(emp_id),
        entity_name=w_name
    )

    return {"code": 0, "message": "Xodim muvaffaqiyatli o'chirildi"}


@router.get("/main-account")
def get_main_account(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    admin_user = require_super_admin(authorization, db)
    main_comp = crud.get_company_by_id(db, "comp-default")
    if not main_comp:
        main_comp = db.query(models.Company).first()

    return {
        "code": 0,
        "data": {
            "super_admin": {
                "id": admin_user.id,
                "username": admin_user.username,
                "full_name": admin_user.full_name or "Administrator",
                "email": admin_user.email or "",
                "phone": getattr(admin_user, "phone", "") or ""
            },
            "main_company": {
                "id": main_comp.id if main_comp else "comp-default",
                "name": main_comp.name if main_comp else "Bosh Korxona",
                "code": main_comp.code if main_comp else "default",
                "plan": getattr(main_comp, "plan", "pro"),
                "billing_cycle": getattr(main_comp, "billing_cycle", "monthly"),
                "max_users": getattr(main_comp, "max_users", 50),
                "phone": getattr(main_comp, "phone", "") or "",
                "email": getattr(main_comp, "email", "") or "",
                "address": getattr(main_comp, "address", "") or ""
            }
        }
    }


@router.post("/main-account")
def update_main_account(
    data: dict = Body(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    admin_user = require_super_admin(authorization, db)
    main_comp = crud.get_company_by_id(db, "comp-default")
    if not main_comp:
        main_comp = db.query(models.Company).first()

    # Update main company fields
    if main_comp:
        if "company_name" in data and data["company_name"]:
            main_comp.name = str(data["company_name"]).strip()
        if "company_code" in data and data["company_code"]:
            main_comp.code = str(data["company_code"]).strip()
        if "company_phone" in data:
            main_comp.phone = data["company_phone"]
        if "company_email" in data:
            main_comp.email = data["company_email"]
        if "company_address" in data:
            main_comp.address = data["company_address"]

    # Update super admin user credentials
    if "admin_username" in data and data["admin_username"]:
        new_username = str(data["admin_username"]).strip()
        if new_username != admin_user.username:
            existing = db.query(models.User).filter(models.User.username == new_username).first()
            if existing and existing.id != admin_user.id:
                raise HTTPException(status_code=400, detail="Ushbu login band, boshqa login tanlang")
            admin_user.username = new_username

    if "admin_password" in data and data["admin_password"] and str(data["admin_password"]).strip():
        admin_user.hashed_password = crud.get_password_hash(str(data["admin_password"]).strip())

    if "admin_full_name" in data:
        admin_user.full_name = data["admin_full_name"]
    if "admin_email" in data:
        admin_user.email = data["admin_email"]
    if "admin_phone" in data:
        admin_user.phone = data["admin_phone"]

    db.commit()
    if main_comp:
        db.refresh(main_comp)
    db.refresh(admin_user)

    log_activity(
        db,
        actor=admin_user.username,
        action="updated_main_account",
        entity="super_admin",
        entity_id=str(admin_user.id),
        entity_name=f"{admin_user.username} / {main_comp.name if main_comp else 'Bosh Korxona'}"
    )

    return {
        "code": 0,
        "message": "Bosh korxona va Super Administrator ma'lumotlari muvaffaqiyatli saqlandi",
        "data": {
            "username": admin_user.username,
            "full_name": admin_user.full_name,
            "company_name": main_comp.name if main_comp else "Bosh Korxona"
        }
    }


@router.post("/account/reset-password")
def reset_company_account_password(
    body: dict = Body(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    admin_user = require_super_admin(authorization, db)
    comp_id = body.get("company_id")
    new_password = body.get("new_password")
    new_username = body.get("username")
    full_name = body.get("full_name")

    if not comp_id:
        raise HTTPException(status_code=400, detail="Kompaniya ID ko'rsatilmadi")
    if not new_password or not str(new_password).strip():
        raise HTTPException(status_code=400, detail="Yangi parol kiritilmadi")

    comp = crud.get_company_by_id(db, comp_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Kompaniya topilmadi")

    u = db.query(models.User).filter(
        models.User.company_id == comp_id,
        models.User.username != 'admin'
    ).order_by(models.User.id.asc()).first()

    hashed = crud.get_password_hash(str(new_password).strip())

    if u:
        old_u = u.username
        if new_username and str(new_username).strip():
            clean_u = str(new_username).strip().lower()
            existing = db.query(models.User).filter(models.User.username == clean_u, models.User.id != u.id).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"'{clean_u}' loginli foydalanuvchi allaqachon mavjud")
            u.username = clean_u
            wk = db.query(models.Worker).filter(models.Worker.company_id == comp_id, models.Worker.account == old_u).first()
            if wk:
                wk.account = clean_u

        u.hashed_password = hashed
        if full_name:
            u.full_name = str(full_name).strip()
            wk = db.query(models.Worker).filter(models.Worker.company_id == comp_id, models.Worker.account == u.username).first()
            if wk:
                wk.name = str(full_name).strip()

        db.commit()
        assigned_username = u.username
    else:
        clean_u = (new_username or f"admin_{comp.code}").strip().lower()
        new_u = models.User(
            username=clean_u,
            hashed_password=hashed,
            full_name=full_name or f"{comp.name} Administrator",
            role="Administrator",
            roleId="10",
            company_id=comp_id,
            permissions=[
                "/dashboard", "/dashboard/analysis", "/dashboard/workplace",
                "/product", "/product/list",
                "/sales", "/sales/pos", "/sales/debtors",
                "/hr", "/hr/workers", "/hr/timesheets", "/hr/outputs", "/hr/adjustments", "/hr/salary"
            ],
            create_time=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        )
        db.add(new_u)
        db.commit()
        assigned_username = clean_u

    log_activity(
        db,
        actor=admin_user.username,
        action="password_reset",
        entity="company_account",
        entity_id=comp_id,
        entity_name=f"{comp.name} ({assigned_username})"
    )

    return {
        "code": 0,
        "message": f"'{comp.name}' kompaniyasi admin paroli muvaffaqiyatli yangilandi",
        "data": {
            "company_id": comp_id,
            "username": assigned_username
        }
    }

