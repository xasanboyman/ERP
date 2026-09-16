import uuid
import datetime
from fastapi import APIRouter, Depends, Query, Body, Header, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.auth import get_user_company_id, get_current_user_optional

router = APIRouter()

@router.get("/branch/list")
def get_branch_list(
    authorization: str = Header(None),
    company_id: str = Query(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, company_id)
    query = db.query(models.Branch)
    if target_company:
        query = query.filter(models.Branch.company_id == target_company)
    branches = query.order_by(models.Branch.created_at.asc()).all()

    # Auto-seed initial branch for new company tenant if none exists
    if not branches and target_company and target_company != "comp-default":
        default_branch = models.Branch(
            id=f"BR-{uuid.uuid4().hex[:6].upper()}",
            company_id=target_company,
            name="Asosiy filial",
            code=f"FIL-{uuid.uuid4().hex[:4].upper()}",
            address="",
            phone="",
            is_active=1,
            created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        db.add(default_branch)
        db.commit()
        branches = [default_branch]

    list_data = [
        {
            "id": b.id,
            "company_id": getattr(b, "company_id", "comp-default"),
            "name": b.name,
            "code": b.code,
            "address": b.address or "",
            "phone": b.phone or "",
            "is_active": b.is_active
        }
        for b in branches
    ]
    return {"code": 0, "data": list_data}

@router.post("/branch/save")
def save_branch(
    body: dict = Body(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, body.get("company_id"))
    current_user = get_current_user_optional(authorization, db)
    b_id = body.get("id")
    name = body.get("name")
    code = body.get("code")
    address = body.get("address")
    phone = body.get("phone")

    if not name:
        raise HTTPException(status_code=400, detail="Filial nomi kiritilishi shart")

    branch = None
    if b_id:
        query = db.query(models.Branch).filter(models.Branch.id == b_id)
        if target_company and target_company != "comp-default":
            query = query.filter(models.Branch.company_id == target_company)
        branch = query.first()

    if branch:
        branch.name = name
        if code:
            branch.code = code
        branch.address = address
        branch.phone = phone
        if target_company:
            branch.company_id = target_company
    else:
        new_id = f"BR-{uuid.uuid4().hex[:6].upper()}"
        new_code = code or f"FIL-{uuid.uuid4().hex[:4].upper()}"
        branch = models.Branch(
            id=new_id,
            company_id=target_company or "comp-default",
            name=name,
            code=new_code,
            address=address,
            phone=phone,
            is_active=1,
            created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        db.add(branch)

    db.commit()
    db.refresh(branch)

    from app.routers.activity import log_activity
    log_activity(
        db=db,
        actor=current_user.username if current_user else "admin",
        action="updated" if b_id else "created",
        entity="branch",
        entity_id=branch.id,
        entity_name=branch.name,
        company_id=target_company
    )

    return {
        "code": 0,
        "message": "Filial muvaffaqiyatli saqlandi",
        "data": {
            "id": branch.id,
            "company_id": branch.company_id,
            "name": branch.name,
            "code": branch.code,
            "address": branch.address,
            "phone": branch.phone
        }
    }

@router.post("/branch/delete")
def delete_branch(
    body: dict = Body(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db)
    current_user = get_current_user_optional(authorization, db)
    b_id = body.get("id")
    if not b_id:
        raise HTTPException(status_code=400, detail="Filial ID topilmadi")

    query = db.query(models.Branch).filter(models.Branch.id == b_id)
    if target_company and target_company != "comp-default":
        query = query.filter(models.Branch.company_id == target_company)
    branch = query.first()

    if branch:
        branch_name = branch.name
        db.delete(branch)
        db.commit()
        from app.routers.activity import log_activity
        log_activity(
            db=db,
            actor=current_user.username if current_user else "admin",
            action="deleted",
            entity="branch",
            entity_id=b_id,
            entity_name=branch_name,
            company_id=target_company
        )
    return {"code": 0, "message": "Filial o'chirildi"}


@router.get("/branch/statistics")
def get_branch_statistics(
    branch_id: str = Query(None),
    company_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, company_id)
    b_query = db.query(models.Branch)
    if target_company:
        b_query = b_query.filter(models.Branch.company_id == target_company)
    if branch_id:
        b_query = b_query.filter(models.Branch.id == branch_id)
    branches = b_query.order_by(models.Branch.created_at.asc()).all()

    # Auto-seed primary branch for new tenant company if none exists
    if not branches and target_company and target_company != "comp-default":
        default_branch = models.Branch(
            id=f"BR-{uuid.uuid4().hex[:6].upper()}",
            company_id=target_company,
            name="Asosiy filial",
            code=f"FIL-{uuid.uuid4().hex[:4].upper()}",
            address="",
            phone="",
            is_active=1,
            created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        db.add(default_branch)
        db.commit()
        db.refresh(default_branch)
        branches = [default_branch]

    primary_branch_id = branches[0].id if branches else None

    # Fetch company-scoped items
    workers_q = db.query(models.Worker)
    products_q = db.query(models.Product)
    sales_q = db.query(models.Sale)
    if target_company:
        workers_q = workers_q.filter(models.Worker.company_id == target_company)
        products_q = products_q.filter(models.Product.company_id == target_company)
        sales_q = sales_q.filter(models.Sale.company_id == target_company)

    all_workers = workers_q.all()
    all_products = products_q.all()
    all_sales = sales_q.order_by(models.Sale.created_at.desc()).all()

    result = []
    for b in branches:
        # Match workers for this branch
        b_workers = [
            w for w in all_workers
            if w.branch_id == b.id or (not w.branch_id and b.id == primary_branch_id)
        ]
        active_workers = [w for w in b_workers if w.status == 1]
        total_salary = sum(w.baseSalary or 0.0 for w in active_workers)

        # Match products for this branch
        b_products = [
            p for p in all_products
            if p.branch_id == b.id or (not p.branch_id and b.id == primary_branch_id)
        ]
        total_qty = sum(p.quantityInStock or 0.0 for p in b_products)
        inventory_value = sum((p.price or 0.0) * (p.quantityInStock or 0.0) for p in b_products)
        low_stock_count = sum(1 for p in b_products if (p.quantityInStock or 0.0) <= 5)

        # Match sales for this branch
        b_sales = [
            s for s in all_sales
            if s.branch_id == b.id or (not s.branch_id and b.id == primary_branch_id)
        ]
        total_revenue = sum(s.total_amount or 0.0 for s in b_sales)
        total_paid = sum(s.paid_amount or 0.0 for s in b_sales)
        total_debt = sum(s.debt_amount or 0.0 for s in b_sales)
        avg_check = round(total_revenue / len(b_sales), 2) if b_sales else 0.0

        result.append({
            "id": b.id,
            "company_id": getattr(b, "company_id", target_company or "comp-default"),
            "name": b.name,
            "code": b.code,
            "address": b.address or "",
            "phone": b.phone or "",
            "is_active": b.is_active,
            "statistics": {
                "employees": {
                    "count": len(b_workers),
                    "active_count": len(active_workers),
                    "total_salary": round(total_salary, 2),
                    "list": [
                        {
                            "id": w.id,
                            "name": w.name,
                            "role": w.role or "Xodim",
                            "phone": w.phone or "",
                            "baseSalary": w.baseSalary or 0.0,
                            "status": w.status
                        }
                        for w in b_workers[:15]
                    ]
                },
                "products": {
                    "count": len(b_products),
                    "total_quantity": round(total_qty, 2),
                    "total_inventory_value": round(inventory_value, 2),
                    "low_stock_count": low_stock_count,
                    "list": [
                        {
                            "id": p.id,
                            "productName": p.productName,
                            "category": p.category,
                            "price": p.price or 0.0,
                            "quantityInStock": p.quantityInStock or 0.0,
                            "unit": p.unit or "dona"
                        }
                        for p in b_products[:15]
                    ]
                },
                "income": {
                    "total_revenue": round(total_revenue, 2),
                    "total_sales_count": len(b_sales),
                    "total_paid": round(total_paid, 2),
                    "total_debt": round(total_debt, 2),
                    "average_check": avg_check,
                    "recent_sales": [
                        {
                            "id": s.id,
                            "receipt_number": s.receipt_number,
                            "total_amount": s.total_amount or 0.0,
                            "payment_method": s.payment_method,
                            "created_at": s.created_at
                        }
                        for s in b_sales[:5]
                    ]
                }
            }
        })

    return {"code": 0, "data": result}
