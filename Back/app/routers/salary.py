import datetime
from fastapi import APIRouter, Depends, Query, Body, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.routers.activity import log_activity
from app.cache import invalidate_analytics
from app.auth import get_user_company_id, get_current_user_from_header, check_user_access

router = APIRouter()

@router.get("/salary/list")
def get_salary_list(
    workerId: str = Query(None),
    status: str = Query(None),
    pageIndex: int = Query(1),
    pageSize: int = Query(10),
    company_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    current_user = get_current_user_from_header(authorization, db)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tizimga kirilmagan yoki sessiya yaroqsiz"
        )
    check_user_access(current_user, ["salary:view", "salary", "/hr/salary"], db)

    target_company = get_user_company_id(authorization, db, company_id)
    salaries = crud.get_salaries(db, company_id=target_company)

    if workerId:
        salaries = [s for s in salaries if s.workerId == workerId]
    if status:
        salaries = [s for s in salaries if s.status.lower() == status.lower()]

    total = len(salaries)
    start = (pageIndex - 1) * pageSize
    end = start + pageSize
    paged = salaries[start:end]

    workers = {w.id: w for w in crud.get_workers(db, company_id=target_company)}
    depts = {d.id: d.departmentName for d in crud.get_departments(db, company_id=target_company)}

    list_data = []
    for s in paged:
        w = workers.get(s.workerId)
        list_data.append({
            "id": s.id,
            "company_id": getattr(s, "company_id", "comp-default"),
            "workerId": s.workerId,
            "workerName": w.name if w else "Noma'lum",
            "departmentName": depts.get(w.departmentId, "—") if w else "—",
            "baseSalary": s.baseSalary,
            "allowance": s.allowance,
            "deduction": s.deduction,
            "netSalary": s.netSalary,
            "status": s.status,
            "payDate": s.payDate,
            "remark": s.remark
        })

    return {
        "code": 0,
        "data": {
            "total": total,
            "list": list_data
        }
    }

@router.post("/salary/save")
def salary_save(
    sal_in: schemas.SalaryCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    current_user = get_current_user_from_header(authorization, db)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tizimga kirilmagan yoki sessiya yaroqsiz")
    check_user_access(current_user, ["salary:edit", "salary:view", "salary", "/hr/salary"], db)

    target_company = get_user_company_id(authorization, db, getattr(sal_in, "company_id", None))
    
    worker = db.query(models.Worker).filter(models.Worker.id == sal_in.workerId).first()
    if target_company and target_company != "comp-default" and worker and worker.company_id != target_company:
        return {"code": 403, "message": "Siz faqat o'z tashkilotingiz xodimlari maoshini saqlay olasiz"}

    salary = crud.create_salary(db, sal_in, company_id=target_company)
    log_activity(
        db,
        actor=current_user.username if current_user else "admin",
        action="created",
        entity="salary",
        entity_id=getattr(salary, "id", None),
        entity_name=worker.name if worker else sal_in.workerId,
        company_id=target_company
    )
    invalidate_analytics()
    return {"code": 0, "data": "success"}

@router.post("/salary/delete")
def salary_delete(
    body: dict = Body(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    current_user = get_current_user_from_header(authorization, db)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tizimga kirilmagan yoki sessiya yaroqsiz")
    check_user_access(current_user, ["salary:delete", "salary", "/hr/salary"], db)

    target_company = get_user_company_id(authorization, db)
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "Iltimos, o'chirish uchun ma'lumotni tanlang"}

    if isinstance(ids, str):
        ids = [ids]

    query = db.query(models.Salary).filter(models.Salary.id.in_(ids))
    if target_company and target_company != "comp-default":
        query = query.join(models.Worker, models.Salary.workerId == models.Worker.id).filter(models.Worker.company_id == target_company)
    salaries = query.all()
    worker_ids = [s.workerId for s in salaries if s.workerId]
    workers = {w.id: w.name for w in db.query(models.Worker).filter(models.Worker.id.in_(worker_ids)).all()} if worker_ids else {}

    for s in salaries:
        db.delete(s)

    for s in salaries:
        name = workers.get(s.workerId, s.id)
        log_activity(db, actor=current_user.username if current_user else "admin", action="deleted", entity="salary", entity_id=s.id, entity_name=name, commit=False, company_id=target_company)

    db.commit()
    invalidate_analytics()
    return {"code": 0, "data": "success"}

@router.post("/salary/payout")
def salary_payout(
    payout: schemas.SalaryPayout,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    current_user = get_current_user_from_header(authorization, db)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tizimga kirilmagan yoki sessiya yaroqsiz")
    check_user_access(current_user, ["salary:payout", "salary:edit", "salary", "/hr/salary"], db)

    target_company = get_user_company_id(authorization, db)
    today = datetime.date.today().strftime("%Y-%m-%d")
    target_month = payout.period_month or datetime.date.today().strftime("%Y-%m")
    pay_count = 0

    if payout.items and len(payout.items) > 0:
        for item in payout.items:
            query = db.query(models.Worker).filter(models.Worker.id == item.workerId)
            if target_company and target_company != "comp-default":
                query = query.filter(models.Worker.company_id == target_company)
            w = query.first()
            if not w:
                continue
            base = item.baseSalary if item.baseSalary is not None and item.baseSalary > 0 else (w.baseSalary or 0.0)
            item_month = item.period_month or target_month
            salary = crud.create_salary(db, schemas.SalaryCreate(
                workerId=w.id,
                baseSalary=base,
                allowance=float(item.allowance or 0.0),
                deduction=float(item.deduction or 0.0),
                payDate=today,
                status="paid",
                remark=item.remark or payout.remark or f"{item_month} oyi maosh to'lovi"
            ), company_id=target_company)
            log_activity(
                db,
                actor=current_user.username if current_user else "admin",
                action="payout",
                entity="salary",
                entity_id=getattr(salary, "id", None),
                entity_name=w.name,
                company_id=target_company
            )
            pay_count += 1
    else:
        target_ids = payout.workerIds or []
        query = db.query(models.Worker).filter(models.Worker.id.in_(target_ids))
        if target_company and target_company != "comp-default":
            query = query.filter(models.Worker.company_id == target_company)
        workers = query.all()
        for w in workers:
            adjustments = db.query(models.StaffAdjustment).filter(
                models.StaffAdjustment.workerId == w.id,
                models.StaffAdjustment.period_month == target_month
            ).all()
            if not adjustments:
                adjustments = db.query(models.StaffAdjustment).filter(models.StaffAdjustment.workerId == w.id).all()

            worker_bonus = sum(a.amount for a in adjustments if a.document_type in ["bonus", "mukofot", "reward"])
            worker_deduction = sum(a.amount for a in adjustments if a.document_type in ["penalty", "fine", "advance", "shtraf", "jarima", "avans"])

            if payout.allowance and payout.allowance > 0 and worker_bonus == 0:
                worker_bonus = payout.allowance
            if payout.deduction and payout.deduction > 0 and worker_deduction == 0:
                worker_deduction = payout.deduction

            salary = crud.create_salary(db, schemas.SalaryCreate(
                workerId=w.id,
                baseSalary=float(w.baseSalary or 0.0),
                allowance=float(worker_bonus),
                deduction=float(worker_deduction),
                payDate=today,
                status="paid",
                remark=payout.remark or f"{target_month} oyi maosh to'lovi"
            ), company_id=target_company)
            log_activity(
                db,
                actor=current_user.username if current_user else "admin",
                action="payout",
                entity="salary",
                entity_id=getattr(salary, "id", None),
                entity_name=w.name,
                company_id=target_company
            )
            pay_count += 1

    invalidate_analytics()
    return {
        "code": 0,
        "data": f"{pay_count} ta xodimga ish haqi muvaffaqiyatli tarqatildi va hisobga olindi"
    }
