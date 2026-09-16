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
