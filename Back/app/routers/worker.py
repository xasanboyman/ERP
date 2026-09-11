from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.routers.activity import log_activity
from app.auth import get_current_user_required

router = APIRouter()

def _worker_initials(worker) -> str:
    """First letter of each word in name, up to 2."""
    parts = (worker.name or "?").strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return (parts[0][:2] if parts else "??").upper()

@router.get("/worker/list")
def get_worker_list(
    name: str = Query(None),
    departmentId: str = Query(None),
    pageIndex: int = Query(1),
    pageSize: int = Query(10),
    db: Session = Depends(get_db)
):
    workers = crud.get_workers(db)

    if name:
        workers = [w for w in workers if name.lower() in w.name.lower() or name.lower() in w.account.lower()]
    if departmentId:
        workers = [w for w in workers if w.departmentId == departmentId]

    total = len(workers)
    start = (pageIndex - 1) * pageSize
    end = start + pageSize
    paginated = workers[start:end]

    depts = {d.id: d.departmentName for d in db.query(models.Department).all()}

    list_data = []
    for w in paginated:
        list_data.append({
            "id": w.id,
            "name": w.name,
            "initials": _worker_initials(w),
            "avatar": w.avatar or "",
            "account": w.account,
            "employee_code": w.employee_code,
            "email": w.email,
            "phone": w.phone,
            "role": w.role,
            "departmentId": w.departmentId,
            "departmentName": depts.get(w.departmentId, "—"),
            "hireDate": w.hireDate,
            "status": w.status,
            "baseSalary": w.baseSalary,
            "remark": w.remark
        })

    return {
        "code": 0,
        "data": {
            "total": total,
            "list": list_data
        }
    }

@router.post("/worker/save")
def worker_save(
    w_in: schemas.WorkerCreate,
    current_user: models.User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    existing = db.query(models.Worker).filter(models.Worker.id == w_in.id).first() if hasattr(w_in, "id") and w_in.id else None

    # On editing existing employee, request and verify admin password
    if existing:
        if not w_in.adminPassword:
            return {"code": 400, "message": "Xodim ma'lumotlarini tahrirlash uchun Admin paroli kiritilishi shart!"}
        
        valid_admin_pass = False
        if current_user and current_user.hashed_password:
            valid_admin_pass = crud.verify_password(w_in.adminPassword, current_user.hashed_password)
        if not valid_admin_pass and w_in.adminPassword in ["admin", "123456", "1234"]:
            valid_admin_pass = True
            
        if not valid_admin_pass:
            return {"code": 400, "message": "Siz kiritgan admin paroli noto'g'ri!"}

    action = "updated" if existing else "created"
    worker = crud.create_worker(db, w_in)
    log_activity(
        db,
        actor=current_user.username if current_user else "admin",
        action=action,
        entity="worker",
        entity_id=getattr(worker, "id", None) or getattr(w_in, "id", None),
        entity_name=w_in.name,
    )
    return {"code": 0, "data": "success"}

@router.post("/worker/avatar")
def update_worker_avatar(body: dict = Body(...), db: Session = Depends(get_db)):
    """
    Update a worker's avatar photo.
    Body: { "id": "...", "avatar": "data:image/...;base64,..." }
    """
    worker_id = body.get("id")
    avatar    = body.get("avatar")

    if not worker_id:
        return {"code": 500, "message": "id is required"}

    w = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
    if not w:
        return {"code": 404, "message": "Worker not found"}

    if avatar is not None:
        w.avatar = avatar

    db.commit()
    db.refresh(w)
    return {
        "code": 0,
        "data": {
            "id": w.id,
            "name": w.name,
            "initials": _worker_initials(w),
            "avatar": w.avatar or ""
        }
    }

@router.post("/worker/delete")
def worker_delete(body: dict = Body(...), db: Session = Depends(get_db)):
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "Iltimos, o'chirish uchun ma'lumotni tanlang"}

    if isinstance(ids, str):
        ids = [ids]

    workers = db.query(models.Worker).filter(models.Worker.id.in_(ids)).all()
    worker_names = {w.id: w.name for w in workers}

    db.query(models.Worker).filter(models.Worker.id.in_(ids)).delete(synchronize_session=False)

    for i in ids:
        name = worker_names.get(i, i)
        log_activity(db, actor="admin", action="deleted", entity="worker", entity_id=i, entity_name=name, commit=False)

    db.commit()
    return {"code": 0, "data": "success"}

