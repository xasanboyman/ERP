from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.routers.activity import log_activity
import datetime

router = APIRouter()

# ----------------- Cutting Stage -----------------
@router.get("/cutting/stage/list")
def get_stage_list(db: Session = Depends(get_db)):
    stages = crud.get_cutting_stages(db)
    return {
        "code": 0,
        "data": {
            "total": len(stages),
            "list": [
                {
                    "id": s.id,
                    "name": s.name,
                    "is_system": s.is_system,
                    "price": s.price,
                    "duration": s.duration,
                    "createTime": s.createTime
                }
                for s in stages
            ]
        }
    }

@router.post("/cutting/stage/save")
def save_stage(stage_in: schemas.CuttingStageCreate, db: Session = Depends(get_db)):
    existing = db.query(models.CuttingStage).filter(models.CuttingStage.id == stage_in.id).first() if stage_in.id else None
    action = "updated" if existing else "created"
    stage = crud.create_cutting_stage(db, stage_in)
    log_activity(
        db,
        actor="admin",
        action=action,
        entity="cutting_stage",
        entity_id=stage.id,
        entity_name=stage.name
    )
    return {"code": 0, "data": "success"}

@router.post("/cutting/stage/delete")
def delete_stage(body: dict = Body(...), db: Session = Depends(get_db)):
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "No IDs provided"}
    if isinstance(ids, str):
        ids = [ids]
    for i in ids:
        stage = db.query(models.CuttingStage).filter(models.CuttingStage.id == i).first()
        name = stage.name if stage else i
        crud.delete_cutting_stage(db, i)
        log_activity(db, actor="admin", action="deleted", entity="cutting_stage", entity_id=i, entity_name=name)
    return {"code": 0, "data": "success"}


# ----------------- Cutting Process -----------------
@router.get("/cutting/process/list")
def get_process_list(db: Session = Depends(get_db)):
    processes = crud.get_cutting_processes(db)
    return {
        "code": 0,
        "data": {
            "total": len(processes),
            "list": [
                {
                    "id": p.id,
                    "name": p.name,
                    "remark": p.remark,
                    "stages": p.stages,
                    "createTime": p.createTime
                }
                for p in processes
            ]
        }
    }

@router.post("/cutting/process/save")
def save_process(proc_in: schemas.CuttingProcessCreate, db: Session = Depends(get_db)):
    existing = db.query(models.CuttingProcess).filter(models.CuttingProcess.id == proc_in.id).first() if proc_in.id else None
    action = "updated" if existing else "created"
    proc = crud.create_cutting_process(db, proc_in)
    log_activity(
        db,
        actor="admin",
        action=action,
        entity="cutting_process",
        entity_id=proc.id,
        entity_name=proc.name
    )
    return {"code": 0, "data": "success"}

@router.post("/cutting/process/delete")
def delete_process(body: dict = Body(...), db: Session = Depends(get_db)):
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "No IDs provided"}
    if isinstance(ids, str):
        ids = [ids]
    for i in ids:
        proc = db.query(models.CuttingProcess).filter(models.CuttingProcess.id == i).first()
        name = proc.name if proc else i
        crud.delete_cutting_process(db, i)
        log_activity(db, actor="admin", action="deleted", entity="cutting_process", entity_id=i, entity_name=name)
    return {"code": 0, "data": "success"}


# ----------------- Cutting Order -----------------
@router.get("/cutting/order/list")
def get_order_list(db: Session = Depends(get_db)):
    orders = crud.get_cutting_orders(db)
    list_data = []
    
    # Pre-load workers and products to reduce queries
    prods = {p.id: p for p in db.query(models.Product).all()}
    procs = {pr.id: pr for pr in db.query(models.CuttingProcess).all()}
    
    for o in orders:
        items_data = []
        for item in o.items:
            prod = prods.get(item.productId)
            proc = procs.get(item.cuttingProcessId)
            items_data.append({
                "id": item.id,
                "productId": item.productId,
                "productName": prod.productName if prod else "Unknown Product",
                "category": item.category,
                "color": item.color,
                "code": item.code,
                "cuttingProcessId": item.cuttingProcessId,
                "cuttingProcessName": proc.name if proc else "—",
                "quantity": item.quantity,
                "size_breakdown": item.size_breakdown,
                "material_consumptions": item.material_consumptions,
                "process_snapshot": item.process_snapshot
            })
            
        list_data.append({
            "id": o.id,
            "order_number": o.order_number,
            "project": o.project,
            "order_name": o.order_name,
            "document_date": o.document_date,
            "responsible_user_ids": o.responsible_user_ids,
            "status": o.status,
            "total_quantity": o.total_quantity,
            "createTime": o.createTime,
            "items": items_data
        })
        
    return {
        "code": 0,
        "data": {
            "total": len(orders),
            "list": list_data
        }
    }

@router.post("/cutting/order/save")
def save_order(order_in: schemas.CuttingOrderCreate, db: Session = Depends(get_db)):
    responsible = order_in.responsible_user_ids or []
    deduped = list(dict.fromkeys(responsible))
    if deduped:
        existing_users = db.query(models.User).filter(models.User.username.in_(deduped)).all()
        existing_usernames = {u.username for u in existing_users}
        for u in deduped:
            if u not in existing_usernames:
                return JSONResponse(
                    status_code=400,
                    content={"code": 400, "message": f"User '{u}' does not exist"}
                )
    order_in.responsible_user_ids = deduped

    existing = db.query(models.CuttingOrder).filter(models.CuttingOrder.id == order_in.id).first() if order_in.id else None
    action = "updated" if existing else "created"
    order = crud.create_cutting_order(db, order_in)
    log_activity(
        db,
        actor="admin",
        action=action,
        entity="cutting_order",
        entity_id=order.id,
        entity_name=order.order_number
    )
    return {"code": 0, "data": "success"}

@router.post("/cutting/order/delete")
def delete_order(body: dict = Body(...), db: Session = Depends(get_db)):
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "No IDs provided"}
    if isinstance(ids, str):
        ids = [ids]
    for i in ids:
        order = db.query(models.CuttingOrder).filter(models.CuttingOrder.id == i).first()
        name = order.order_number if order else i
        crud.delete_cutting_order(db, i)
        log_activity(db, actor="admin", action="deleted", entity="cutting_order", entity_id=i, entity_name=name)
    return {"code": 0, "data": "success"}

@router.post("/cutting/order/start-production")
def start_production(body: dict = Body(...), db: Session = Depends(get_db)):
    order_id = body.get("orderId")
    if not order_id:
        return {"code": 500, "message": "orderId is required"}
    
    order = db.query(models.CuttingOrder).filter(models.CuttingOrder.id == order_id).first()
    if not order:
        return {"code": 404, "message": "Order not found"}
    if not order.items:
        return JSONResponse(
            status_code=400,
            content={"code": 400, "message": "Order contains no items"}
        )
        
    try:
        order = crud.start_production_for_order(db, order_id)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"code": 400, "message": str(e)}
        )
        
    if not order:
        return {"code": 404, "message": "Order not found"}
        
    log_activity(
        db,
        actor="admin",
        action="started_production",
        entity="cutting_order",
        entity_id=order.id,
        entity_name=order.order_number
    )
    return {"code": 0, "data": "success"}


# ----------------- Cutting Task -----------------
@router.get("/cutting/task/list")
def get_task_list(db: Session = Depends(get_db)):
    tasks = crud.get_cutting_tasks(db)
    return {
        "code": 0,
        "data": {
            "total": len(tasks),
            "list": [
                {
                    "id": t.id,
                    "orderId": t.orderId,
                    "orderItemId": t.orderItemId,
                    "stageId": t.stageId,
                    "position": t.position,
                    "quantity": t.quantity,
                    "status": t.status,
                    "order_number_snapshot": t.order_number_snapshot,
                    "order_name_snapshot": t.order_name_snapshot,
                    "process_name_snapshot": t.process_name_snapshot,
                    "stage_name_snapshot": t.stage_name_snapshot,
                    "product_name_snapshot": t.product_name_snapshot,
                    "createTime": t.createTime
                }
                for t in tasks
            ]
        }
    }

@router.post("/cutting/task/update-status")
def update_task_status(body: dict = Body(...), db: Session = Depends(get_db)):
    task_id = body.get("taskId")
    status = body.get("status")
    if not task_id or not status:
        return {"code": 500, "message": "taskId and status are required"}
    
    task = crud.update_cutting_task_status(db, task_id, status)
    if not task:
        return {"code": 404, "message": "Task not found"}
        
    log_activity(
        db,
        actor="admin",
        action="updated_status",
        entity="cutting_task",
        entity_id=task.id,
        entity_name=f"{task.order_number_snapshot} - {task.stage_name_snapshot}"
    )
    return {"code": 0, "data": "success"}


# ----------------- Cutting Task Execution -----------------
@router.get("/cutting/task/execution/list")
def get_execution_list(db: Session = Depends(get_db)):
    executions = crud.get_cutting_task_executions(db)
    workers = {w.id: w for w in db.query(models.Worker).all()}
    
    list_data = []
    for e in executions:
        worker = workers.get(e.workerId)
        list_data.append({
            "id": e.id,
            "taskId": e.taskId,
            "workerId": e.workerId,
            "workerName": worker.name if worker else "Unknown Worker",
            "quantity": e.quantity,
            "period_month": e.period_month,
            "comment": e.comment,
            "createTime": e.createTime,
            "task_details": {
                "order_number": e.task.order_number_snapshot if e.task else "",
                "stage_name": e.task.stage_name_snapshot if e.task else "",
                "product_name": e.task.product_name_snapshot if e.task else ""
            } if e.task else None
        })
        
    return {
        "code": 0,
        "data": {
            "total": len(executions),
            "list": list_data
        }
    }

@router.post("/cutting/task/execution/save")
def save_execution(exe_in: schemas.CuttingTaskExecutionCreate, db: Session = Depends(get_db)):
    exe = crud.create_cutting_task_execution(db, exe_in)
    log_activity(
        db,
        actor="admin",
        action="created",
        entity="cutting_execution",
        entity_id=exe.id,
        entity_name=f"Execution of qty {exe.quantity} for task {exe.taskId}"
    )
    return {"code": 0, "data": "success"}

@router.post("/cutting/task/execution/delete")
def delete_execution(body: dict = Body(...), db: Session = Depends(get_db)):
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "No IDs provided"}
    if isinstance(ids, str):
        ids = [ids]
    for i in ids:
        crud.delete_cutting_task_execution(db, i)
        log_activity(db, actor="admin", action="deleted", entity="cutting_execution", entity_id=i, entity_name=i)
    return {"code": 0, "data": "success"}
