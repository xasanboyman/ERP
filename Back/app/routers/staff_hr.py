from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.routers.activity import log_activity
from app.cache import invalidate_analytics

router = APIRouter()

# ----------------- Job Position -----------------
@router.get("/hr/position/list")
def get_position_list(db: Session = Depends(get_db)):
    positions = crud.get_positions(db)
    depts = {d.id: d.departmentName for d in db.query(models.Department).all()}
    return {
        "code": 0,
        "data": {
            "total": len(positions),
            "list": [
                {
                    "id": p.id,
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
def save_position(pos_in: schemas.PositionCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Position).filter(models.Position.id == pos_in.id).first() if pos_in.id else None
    action = "updated" if existing else "created"
    pos = crud.create_position(db, pos_in)
    log_activity(
        db,
        actor="admin",
        action=action,
        entity="position",
        entity_id=pos.id,
        entity_name=pos.positionName
    )
    return {"code": 0, "data": "success"}

@router.post("/hr/position/delete")
def delete_position(body: dict = Body(...), db: Session = Depends(get_db)):
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "No IDs provided"}
    if isinstance(ids, str):
        ids = [ids]
    for i in ids:
        pos = db.query(models.Position).filter(models.Position.id == i).first()
        name = pos.positionName if pos else i
        crud.delete_position(db, i)
        log_activity(db, actor="admin", action="deleted", entity="position", entity_id=i, entity_name=name)
    return {"code": 0, "data": "success"}


# ----------------- Staff Adjustment -----------------
@router.get("/hr/adjustment/list")
def get_adjustment_list(db: Session = Depends(get_db)):
    adjustments = crud.get_staff_adjustments(db)
    workers = {w.id: w for w in db.query(models.Worker).all()}
    
    return {
        "code": 0,
        "data": {
            "total": len(adjustments),
            "list": [
                {
                    "id": a.id,
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
def save_adjustment(adj_in: schemas.StaffAdjustmentCreate, db: Session = Depends(get_db)):
    existing = db.query(models.StaffAdjustment).filter(models.StaffAdjustment.id == adj_in.id).first() if adj_in.id else None
    action = "updated" if existing else "created"
    adj = crud.create_staff_adjustment(db, adj_in)
    log_activity(
        db,
        actor="admin",
        action=action,
        entity="staff_adjustment",
        entity_id=adj.id,
        entity_name=f"{adj.document_type} - {adj.amount}"
    )
    return {"code": 0, "data": "success"}

@router.post("/hr/adjustment/delete")
def delete_adjustment(body: dict = Body(...), db: Session = Depends(get_db)):
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "No IDs provided"}
    if isinstance(ids, str):
        ids = [ids]
    for i in ids:
        adj = db.query(models.StaffAdjustment).filter(models.StaffAdjustment.id == i).first()
        name = f"{adj.document_type} - {adj.amount}" if adj else i
        crud.delete_staff_adjustment(db, i)
        log_activity(db, actor="admin", action="deleted", entity="staff_adjustment", entity_id=i, entity_name=name)
    return {"code": 0, "data": "success"}


# ----------------- Staff Timesheet -----------------
@router.get("/hr/timesheet/list")
def get_timesheet_list(db: Session = Depends(get_db)):
    timesheets = crud.get_staff_timesheets(db)
    return {
        "code": 0,
        "data": {
            "total": len(timesheets),
            "list": [
                {
                    "id": t.id,
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
def save_timesheet(ts_in: schemas.StaffTimesheetCreate, db: Session = Depends(get_db)):
    existing = db.query(models.StaffTimesheet).filter(models.StaffTimesheet.id == ts_in.id).first() if ts_in.id else None
    action = "updated" if existing else "created"
    ts = crud.create_staff_timesheet(db, ts_in)
    log_activity(
        db,
        actor="admin",
        action=action,
        entity="staff_timesheet",
        entity_id=ts.id,
        entity_name=ts.date
    )
    return {"code": 0, "data": "success"}

@router.post("/hr/timesheet/delete")
def delete_timesheet(body: dict = Body(...), db: Session = Depends(get_db)):
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "No IDs provided"}
    if isinstance(ids, str):
        ids = [ids]
    for i in ids:
        ts = db.query(models.StaffTimesheet).filter(models.StaffTimesheet.id == i).first()
        name = ts.date if ts else i
        crud.delete_staff_timesheet(db, i)
        log_activity(db, actor="admin", action="deleted", entity="staff_timesheet", entity_id=i, entity_name=name)
    return {"code": 0, "data": "success"}


# ----------------- Staff Output -----------------
@router.get("/hr/output/list")
def get_output_list(db: Session = Depends(get_db)):
    outputs = crud.get_staff_outputs(db)
    workers = {w.id: w.name for w in db.query(models.Worker).all()}
    
    return {
        "code": 0,
        "data": {
            "total": len(outputs),
            "list": [
                {
                    "id": o.id,
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
def save_output(out_in: schemas.StaffOutputCreate, db: Session = Depends(get_db)):
    existing = db.query(models.StaffOutput).filter(models.StaffOutput.id == out_in.id).first() if out_in.id else None
    action = "updated" if existing else "created"
    out = crud.create_staff_output(db, out_in)
    invalidate_analytics()
    log_activity(
        db,
        actor="admin",
        action=action,
        entity="staff_output",
        entity_id=out.id,
        entity_name=f"{out.name} - {out.amount}"
    )
    return {"code": 0, "data": "success"}

@router.post("/hr/output/delete")
def delete_output(body: dict = Body(...), db: Session = Depends(get_db)):
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "No IDs provided"}
    if isinstance(ids, str):
        ids = [ids]
    for i in ids:
        out = db.query(models.StaffOutput).filter(models.StaffOutput.id == i).first()
        name = out.name if out else i
        crud.delete_staff_output(db, i)
        log_activity(db, actor="admin", action="deleted", entity="staff_output", entity_id=i, entity_name=name)
    invalidate_analytics()
    return {"code": 0, "data": "success"}
