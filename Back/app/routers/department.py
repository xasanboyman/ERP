import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models

router = APIRouter()

@router.get("/department/list")
def get_department_list(db: Session = Depends(get_db)):
    depts = crud.get_departments(db)
    
    dept_map = {d.id: d for d in depts}
    top_level = [d for d in depts if not d.parentId or d.parentId not in dept_map]
    children = [d for d in depts if d.parentId and d.parentId in dept_map]
    
    tree = []
    for top in top_level:
        node = {
            "id": top.id,
            "departmentName": top.departmentName,
            "parentId": top.parentId,
            "status": top.status,
            "remark": top.remark,
            "createTime": top.createTime,
            "children": []
        }
        for child in children:
            if child.parentId == top.id:
                node["children"].append({
                    "id": child.id,
                    "departmentName": child.departmentName,
                    "parentId": child.parentId,
                    "status": child.status,
                    "remark": child.remark,
                    "createTime": child.createTime
                })
        tree.append(node)
        
    return {
        "code": 0,
        "data": {
            "list": tree
        }
    }

@router.get("/department/table/list")
def get_department_table_list(db: Session = Depends(get_db)):
    # Simple list is expected or tree
    res = get_department_list(db)
    return {
        "code": 0,
        "data": {
            "list": res["data"]["list"],
            "total": len(res["data"]["list"])
        }
    }

@router.get("/department/users")
def get_department_users(
    id: Optional[str] = Query(None),
    pageSize: int = Query(10),
    pageIndex: int = Query(1),
    db: Session = Depends(get_db)
):
    query = db.query(models.User)
    if id:
        query = query.filter(models.User.department_id == id)
        
    total = query.count()
    
    start = (pageIndex - 1) * pageSize
    end = start + pageSize
    paginated = query.offset(start).limit(pageSize).all()
    
    user_list = []
    for u in paginated:
        user_list.append({
            "id": str(u.id),
            "username": u.username,
            "account": u.username,
            "email": u.email or f"{u.username}@example.com",
            "createTime": u.create_time,
            "role": u.role,
            "roleId": u.roleId,
            "department_id": u.department_id
        })
        
    return {
        "code": 0,
        "data": {
            "total": total,
            "list": user_list
        }
    }

@router.post("/department/user/save")
def department_user_save(user_data: schemas.DepartmentUserSave, db: Session = Depends(get_db)):
    crud.save_department_user(db, user_data)
    from app.routers.activity import log_activity
    log_activity(
        db=db,
        actor="admin",
        action="saved",
        entity="department_user",
        entity_name=user_data.username
    )
    return {
        "code": 0,
        "data": "success"
    }

@router.post("/department/user/delete")
def department_user_delete(body: dict = Body(...), db: Session = Depends(get_db)):
    ids = body.get("ids")
    if ids is None:
        return {"code": 500, "message": "请选择需要删除的数据"}
    
    # Parse ids into a list of integers
    user_ids = []
    if isinstance(ids, list):
        for item in ids:
            try:
                user_ids.append(int(item))
            except (ValueError, TypeError):
                pass
    elif isinstance(ids, (int, str)):
        if isinstance(ids, str) and "," in ids:
            for item in ids.split(","):
                try:
                    user_ids.append(int(item.strip()))
                except (ValueError, TypeError):
                    pass
        else:
            try:
                user_ids.append(int(ids))
            except (ValueError, TypeError):
                pass
                
    if not user_ids:
        return {"code": 500, "message": "请选择需要删除的数据"}
        
    crud.delete_department_users(db, user_ids)
    from app.routers.activity import log_activity
    for uid in user_ids:
        log_activity(
            db=db,
            actor="admin",
            action="deleted",
            entity="department_user",
            entity_id=str(uid)
        )
    return {
        "code": 0,
        "data": "success"
    }

@router.post("/department/save")
def department_save(dept_in: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    crud.create_department(db, dept_in)
    from app.routers.activity import log_activity
    log_activity(
        db=db,
        actor="admin",
        action="created",
        entity="department",
        entity_id=dept_in.id,
        entity_name=dept_in.departmentName
    )
    return {
        "code": 0,
        "data": "success"
    }

@router.post("/department/delete")
def department_delete(body: dict = Body(...), db: Session = Depends(get_db)):
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "Iltimos, o'chirish uchun ma'lumotni tanlang"}
    
    # Support string ids or list of ids
    if isinstance(ids, str):
        ids = [ids]
        
    from app.routers.activity import log_activity
    db.query(models.Department).filter(models.Department.id.in_(ids)).delete(synchronize_session=False)
    for i in ids:
        log_activity(
            db=db,
            actor="admin",
            action="deleted",
            entity="department",
            entity_id=str(i),
            commit=False
        )
    db.commit()
        
    return {
        "code": 0,
        "data": "success"
    }
