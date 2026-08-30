import uuid
import datetime
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()

@router.get("/branch/list")
def get_branch_list(db: Session = Depends(get_db)):
    branches = db.query(models.Branch).order_by(models.Branch.created_at.asc()).all()
    list_data = [
        {
            "id": b.id,
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
def save_branch(body: dict = Body(...), db: Session = Depends(get_db)):
    b_id = body.get("id")
    name = body.get("name")
    code = body.get("code")
    address = body.get("address")
    phone = body.get("phone")

    if not name:
        raise HTTPException(status_code=400, detail="Filial nomi kiritilishi shart")

    branch = None
    if b_id:
        branch = db.query(models.Branch).filter(models.Branch.id == b_id).first()

    if branch:
        branch.name = name
        if code:
            branch.code = code
        branch.address = address
        branch.phone = phone
    else:
        new_id = f"BR-{uuid.uuid4().hex[:6].upper()}"
        new_code = code or f"FIL-{uuid.uuid4().hex[:4].upper()}"
        branch = models.Branch(
            id=new_id,
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
        actor="admin",
        action="updated" if b_id else "created",
        entity="branch",
        entity_id=branch.id,
        entity_name=branch.name
    )

    return {
        "code": 0,
        "message": "Filial muvaffaqiyatli saqlandi",
        "data": {
            "id": branch.id,
            "name": branch.name,
            "code": branch.code,
            "address": branch.address,
            "phone": branch.phone
        }
    }

@router.post("/branch/delete")
def delete_branch(body: dict = Body(...), db: Session = Depends(get_db)):
    b_id = body.get("id")
    if not b_id:
        raise HTTPException(status_code=400, detail="Filial ID topilmadi")
    branch = db.query(models.Branch).filter(models.Branch.id == b_id).first()
    if branch:
        branch_name = branch.name
        db.delete(branch)
        db.commit()
        from app.routers.activity import log_activity
        log_activity(
            db=db,
            actor="admin",
            action="deleted",
            entity="branch",
            entity_id=b_id,
            entity_name=branch_name
        )
    return {"code": 0, "message": "Filial o'chirildi"}
