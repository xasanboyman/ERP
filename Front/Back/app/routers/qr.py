from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.routers.activity import log_activity

router = APIRouter()

@router.get("/qr/list")
def get_qr_list(db: Session = Depends(get_db)):
    codes = crud.get_qr_codes(db)
    list_data = []
    
    for q in codes:
        list_data.append({
            "id": q.id,
            "code": q.code,
            "taskId": q.taskId,
            "quantity": q.quantity,
            "status": q.status,
            "workerId": q.workerId,
            "createTime": q.createTime,
            "task_details": {
                "order_number": q.task.order_number_snapshot if q.task else "",
                "stage_name": q.task.stage_name_snapshot if q.task else "",
                "product_name": q.task.product_name_snapshot if q.task else ""
            } if q.task else None
        })
        
    return {
        "code": 0,
        "data": {
            "total": len(codes),
            "list": list_data
        }
    }

@router.post("/qr/save")
def save_qr(qr_in: schemas.QrCodeCreate, db: Session = Depends(get_db)):
    task = db.query(models.CuttingTask).filter(models.CuttingTask.id == qr_in.taskId).first()
    if not task:
        return {"code": 404, "message": "Task not found"}
    if qr_in.quantity > task.quantity:
        return JSONResponse(
            status_code=400,
            content={"code": 400, "message": "QR Code quantity exceeds task quantity"}
        )
    qr = crud.generate_qr_code_for_task(db, qr_in)
    log_activity(
        db,
        actor="admin",
        action="generated",
        entity="qr_code",
        entity_id=qr.id,
        entity_name=qr.code
    )
    return {"code": 0, "data": qr.code}

@router.post("/qr/assign-worker")
def assign_worker(body: dict = Body(...), db: Session = Depends(get_db)):
    qr_id = body.get("qrId")
    code = body.get("code")
    worker_id = body.get("workerId")
    if not worker_id:
        return {"code": 500, "message": "workerId is required"}
    
    qr = None
    if qr_id:
        qr = db.query(models.QrCode).filter(models.QrCode.id == qr_id).first()
    elif code:
        qr = db.query(models.QrCode).filter(models.QrCode.code == code).first()
        
    if not qr:
        return {"code": 404, "message": "QR Code not found"}
        
    if qr.status == "scanned":
        return JSONResponse(
            status_code=400,
            content={"code": 400, "message": "QR Code has already been scanned"}
        )
        
    worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
    if not worker:
        return {"code": 404, "message": "Worker not found"}
        
    qr.workerId = worker_id
    qr.status = "scanned"
    
    if qr.taskId:
        crud.create_cutting_task_execution(
            db,
            schemas.CuttingTaskExecutionCreate(
                taskId=qr.taskId,
                workerId=worker_id,
                quantity=qr.quantity,
                comment=f"Auto-executed via QR code scan: {qr.code}"
            )
        )
        
    db.commit()
    db.refresh(qr)
    
    log_activity(
        db,
        actor="admin",
        action="assigned_worker",
        entity="qr_code",
        entity_id=qr.id,
        entity_name=f"Assigned worker {worker.name} to QR {qr.code}"
    )
    
    return {"code": 0, "data": "success"}

@router.post("/qr/update-status")
def update_qr_status(body: dict = Body(...), db: Session = Depends(get_db)):
    qr_id = body.get("qrId")
    code = body.get("code")
    status = body.get("status")
    if not status:
        return {"code": 500, "message": "status is required"}
        
    qr = None
    if qr_id:
        qr = db.query(models.QrCode).filter(models.QrCode.id == qr_id).first()
    elif code:
        qr = db.query(models.QrCode).filter(models.QrCode.code == code).first()
        
    if not qr:
        return {"code": 404, "message": "QR Code not found"}
        
    qr.status = status
    db.commit()
    db.refresh(qr)
    
    log_activity(
        db,
        actor="admin",
        action="updated_status",
        entity="qr_code",
        entity_id=qr.id,
        entity_name=f"Updated status of QR {qr.code} to {status}"
    )
    
    return {"code": 0, "data": "success"}

@router.post("/qr/delete")
def delete_qr(body: dict = Body(...), db: Session = Depends(get_db)):
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "No IDs provided"}
    if isinstance(ids, str):
        ids = [ids]
    for i in ids:
        qr = db.query(models.QrCode).filter(models.QrCode.id == i).first()
        name = qr.code if qr else i
        crud.delete_qr_code(db, i)
        log_activity(db, actor="admin", action="deleted", entity="qr_code", entity_id=i, entity_name=name)
    return {"code": 0, "data": "success"}
