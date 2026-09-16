from fastapi import APIRouter, Depends, Query, Body, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.routers.activity import log_activity
from app.cache import invalidate_analytics
from app.auth import get_user_company_id, get_current_user_optional

router = APIRouter()

# ----------------- Job Position -----------------
@router.get("/hr/position/list")
def get_position_list(
    company_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, company_id)
    positions = crud.get_positions(db, company_id=target_company)
    depts = {d.id: d.departmentName for d in crud.get_departments(db, company_id=target_company)}
    return {
        "code": 0,
        "data": {
            "total": len(positions),
            "list": [
                {
                    "id": p.id,
                    "company_id": getattr(p, "company_id", "comp-default"),
                    "positionName": p.positionName,
                    "departmentId": p.departmentId,
                    "departmentName": depts.get(p.departmentId, "—"),
                    "baseSalary": p.baseSalary,
                    "status": p.status,
                    "remark": p.remark,
                    "createTime": p.createTime
                }
                for p in positions
            ]
        }
    }

@router.post("/hr/position/save")
def save_position(
    pos_in: schemas.PositionCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, getattr(pos_in, "company_id", None))
    current_user = get_current_user_optional(authorization, db)
    existing = db.query(models.Position).filter(models.Position.id == pos_in.id).first() if pos_in.id else None
    action = "updated" if existing else "created"
    pos = crud.create_position(db, pos_in, company_id=target_company)
    log_activity(
        db,
        actor=current_user.username if current_user else "admin",
        action=action,
        entity="position",
        entity_id=pos.id,
        entity_name=pos.positionName,
        company_id=target_company
    )
    return {"code": 0, "data": "success"}

@router.post("/hr/position/delete")
def delete_position(
    body: dict = Body(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db)
    current_user = get_current_user_optional(authorization, db)
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "No IDs provided"}
    if isinstance(ids, str):
        ids = [ids]
    for i in ids:
        query = db.query(models.Position).filter(models.Position.id == i)
        if target_company and target_company != "comp-default":
            query = query.filter(models.Position.company_id == target_company)
        pos = query.first()
        if pos:
            name = pos.positionName
            crud.delete_position(db, i)
            log_activity(db, actor=current_user.username if current_user else "admin", action="deleted", entity="position", entity_id=i, entity_name=name, company_id=target_company)
    return {"code": 0, "data": "success"}


# ----------------- Staff Adjustment -----------------
@router.get("/hr/adjustment/list")
def get_adjustment_list(
    company_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, company_id)
    adjustments = crud.get_staff_adjustments(db, company_id=target_company)
    workers = {w.id: w for w in crud.get_workers(db, company_id=target_company)}
    
    return {
        "code": 0,
        "data": {
            "total": len(adjustments),
            "list": [
                {
                    "id": a.id,
                    "company_id": getattr(a, "company_id", "comp-default"),
                    "workerId": a.workerId,
                    "workerName": workers[a.workerId].name if a.workerId in workers else "Unknown Worker",
                    "document_type": a.document_type,
                    "amount": a.amount,
                    "period_month": a.period_month,
                    "description": a.description,
                    "createTime": a.createTime
                }
                for a in adjustments
            ]
        }
    }

@router.post("/hr/adjustment/save")
def save_adjustment(
    adj_in: schemas.StaffAdjustmentCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, getattr(adj_in, "company_id", None))
    current_user = get_current_user_optional(authorization, db)
    existing = db.query(models.StaffAdjustment).filter(models.StaffAdjustment.id == adj_in.id).first() if adj_in.id else None
    action = "updated" if existing else "created"
    adj = crud.create_staff_adjustment(db, adj_in, company_id=target_company)
    log_activity(
        db,
        actor=current_user.username if current_user else "admin",
        action=action,
        entity="staff_adjustment",
        entity_id=adj.id,
        entity_name=f"{adj.document_type} - {adj.amount}",
        company_id=target_company
    )
    return {"code": 0, "data": "success"}

@router.post("/hr/adjustment/delete")
def delete_adjustment(
    body: dict = Body(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db)
    current_user = get_current_user_optional(authorization, db)
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "No IDs provided"}
    if isinstance(ids, str):
        ids = [ids]
    for i in ids:
        query = db.query(models.StaffAdjustment).filter(models.StaffAdjustment.id == i)
        if target_company and target_company != "comp-default":
            query = query.filter(models.StaffAdjustment.company_id == target_company)
        adj = query.first()
        if adj:
            name = f"{adj.document_type} - {adj.amount}"
            crud.delete_staff_adjustment(db, i)
            log_activity(db, actor=current_user.username if current_user else "admin", action="deleted", entity="staff_adjustment", entity_id=i, entity_name=name, company_id=target_company)
    return {"code": 0, "data": "success"}


# ----------------- Staff Timesheet -----------------
@router.get("/hr/timesheet/list")
def get_timesheet_list(
    company_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, company_id)
    timesheets = crud.get_staff_timesheets(db, company_id=target_company)
    return {
        "code": 0,
        "data": {
            "total": len(timesheets),
            "list": [
                {
                    "id": t.id,
                    "company_id": getattr(t, "company_id", "comp-default"),
                    "date": t.date,
                    "status": t.status,
                    "records": t.records,
                    "createTime": t.createTime
                }
                for t in timesheets
            ]
        }
    }

@router.post("/hr/timesheet/save")
def save_timesheet(
    ts_in: schemas.StaffTimesheetCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, getattr(ts_in, "company_id", None))
    current_user = get_current_user_optional(authorization, db)
    existing = db.query(models.StaffTimesheet).filter(models.StaffTimesheet.id == ts_in.id).first() if ts_in.id else None
    action = "updated" if existing else "created"
    ts = crud.create_staff_timesheet(db, ts_in, company_id=target_company)
    log_activity(
        db,
        actor=current_user.username if current_user else "admin",
        action=action,
        entity="staff_timesheet",
        entity_id=ts.id,
        entity_name=ts.date,
        company_id=target_company
    )
    return {"code": 0, "data": "success"}

@router.post("/hr/timesheet/delete")
def delete_timesheet(
    body: dict = Body(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db)
    current_user = get_current_user_optional(authorization, db)
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "No IDs provided"}
    if isinstance(ids, str):
        ids = [ids]
    for i in ids:
        query = db.query(models.StaffTimesheet).filter(models.StaffTimesheet.id == i)
        if target_company and target_company != "comp-default":
            query = query.filter(models.StaffTimesheet.company_id == target_company)
        ts = query.first()
        if ts:
            name = ts.date
            crud.delete_staff_timesheet(db, i)
            log_activity(db, actor=current_user.username if current_user else "admin", action="deleted", entity="staff_timesheet", entity_id=i, entity_name=name, company_id=target_company)
    return {"code": 0, "data": "success"}


# ----------------- Staff Output -----------------
@router.get("/hr/output/list")
def get_output_list(
    company_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, company_id)
    outputs = crud.get_staff_outputs(db, company_id=target_company)
    workers = {w.id: w.name for w in crud.get_workers(db, company_id=target_company)}
    
    return {
        "code": 0,
        "data": {
            "total": len(outputs),
            "list": [
                {
                    "id": o.id,
                    "company_id": getattr(o, "company_id", "comp-default"),
                    "workerId": o.workerId,
                    "workerName": getattr(o, 'workerName', None) or (workers.get(o.workerId) if o.workerId else None) or o.workerId or "Vaqtinchalik Ishchi",
                    "name": o.name,
                    "amount": o.amount,
                    "period_month": o.period_month,
                    "comment": o.comment,
                    "createTime": o.createTime
                }
                for o in outputs
            ]
        }
    }

@router.post("/hr/output/save")
def save_output(
    out_in: schemas.StaffOutputCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, getattr(out_in, "company_id", None))
    current_user = get_current_user_optional(authorization, db)
    existing = db.query(models.StaffOutput).filter(models.StaffOutput.id == out_in.id).first() if out_in.id else None
    action = "updated" if existing else "created"
    out = crud.create_staff_output(db, out_in, company_id=target_company)
    invalidate_analytics()
    log_activity(
        db,
        actor=current_user.username if current_user else "admin",
        action=action,
        entity="staff_output",
        entity_id=out.id,
        entity_name=f"{out.name} - {out.amount}",
        company_id=target_company
    )
    return {"code": 0, "data": "success"}

@router.post("/hr/output/delete")
def delete_output(
    body: dict = Body(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db)
    current_user = get_current_user_optional(authorization, db)
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "No IDs provided"}
    if isinstance(ids, str):
        ids = [ids]
    for i in ids:
        query = db.query(models.StaffOutput).filter(models.StaffOutput.id == i)
        if target_company and target_company != "comp-default":
            query = query.filter(models.StaffOutput.company_id == target_company)
        out = query.first()
        if out:
            name = out.name
            crud.delete_staff_output(db, i)
            log_activity(db, actor=current_user.username if current_user else "admin", action="deleted", entity="staff_output", entity_id=i, entity_name=name, company_id=target_company)
    invalidate_analytics()
    return {"code": 0, "data": "success"}
