import uuid
import calendar
import datetime
import jwt
from fastapi import APIRouter, Depends, Query, Body, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, crud

router = APIRouter()

SECRET_KEY = "super-secret-key-that-is-hard-to-guess"
ALGORITHM = "HS256"

def decode_access_token(token: str):
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def get_current_user_optional(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        return None
    payload = decode_access_token(authorization)
    if not payload or "sub" not in payload:
        return None
    return db.query(models.User).filter(models.User.username == payload["sub"]).first()

def get_current_user_required(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized: Missing token")
    payload = decode_access_token(authorization)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid token")
    user = db.query(models.User).filter(models.User.username == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized: User not found")
    return user


def check_permission(user: models.User, required_menu_id: int, required_action: str = "view", db: Session = None):
    user_perms = list(user.permissions or [])
    if not user_perms and db and user.roleId:
        role_ids = [r.strip() for r in str(user.roleId).split(",") if r.strip()]
        roles = db.query(models.Role).filter(models.Role.id.in_(role_ids)).all()
        for r in roles:
            if r.permissions:
                user_perms.extend(r.permissions)
        user_perms = list(set(user_perms))
        
    if "*.*.*" in user_perms:
        return True
        
    allowed = False
    for p in user_perms:
        if ":" in p:
            parts = p.split(":")
            try:
                menu_id = int(parts[0])
                action = parts[1]
                if menu_id == required_menu_id:
                    if required_action == "view" or action == required_action:
                        allowed = True
                        break
            except ValueError:
                # String permissions (like "crm:student:view")
                prefix = parts[0].lower()
                sub = parts[1].lower()
                if required_menu_id == 10 and prefix == "crm":
                    allowed = True
                elif required_menu_id == 12 and prefix == "crm" and sub == "student":
                    allowed = True
                elif required_menu_id == 11 and prefix == "crm" and sub == "groups":
                    allowed = True
                elif required_menu_id == 13 and prefix == "crm" and sub == "teachers":
                    allowed = True
                    
    if not allowed:
        raise HTTPException(
            status_code=403,
            detail="Sizda ushbu amalni bajarish uchun ruxsat yo'q!"
        )
    return True

# --- Groups ---

@router.get("/crm/group/list")
def get_group_list(
    user: models.User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    query = db.query(models.CRMGroup)
    if user and user.role and user.role.lower() == "teacher":
        teacher_name = user.full_name if user.full_name else user.username
        query = query.filter(models.CRMGroup.teacherName == teacher_name)
    groups = query.all()
    return {
        "code": 0,
        "data": {
            "list": [
                {
                    "id": g.id,
                    "groupName": g.groupName,
                    "scheduleDays": g.scheduleDays or [],
                    "status": g.status,
                    "duration": g.duration or 1.5,
                    "teacherName": g.teacherName,
                    "startTime": g.startTime,
                    "endTime": g.endTime,
                    "awards": g.awards or ["Award"],
                    "createTime": g.createTime
                }
                for g in groups
            ],
            "total": len(groups)
        }
    }

@router.post("/crm/group/save")
def save_group(
    group_in: schemas.CRMGroupCreate,
    user: models.User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    check_permission(user, 11, "create" if not group_in.id else "edit", db)
    db_group = None
    if group_in.id:
        db_group = db.query(models.CRMGroup).filter(models.CRMGroup.id == group_in.id).first()
    
    current_month_str = datetime.datetime.now().strftime("%Y-%m")
    parts = current_month_str.split('-')
    year_val = int(parts[0])
    month_val = int(parts[1])

    # 1. Validate Start Time and End Time order
    if group_in.startTime and group_in.endTime and group_in.startTime >= group_in.endTime:
        return {"code": 400, "message": "Dars boshlanish vaqti tugash vaqtidan oldin bo'lishi kerak!"}

    # 2. Check for scheduling conflict with other groups taught by the same teacher
    if group_in.teacherName and group_in.startTime and group_in.endTime:
        query = db.query(models.CRMGroup).filter(
            models.CRMGroup.teacherName == group_in.teacherName
        )
        if group_in.id:
            query = query.filter(models.CRMGroup.id != group_in.id)
        for other in query.all():
            # Check overlap in scheduled days
            common_days = set(group_in.scheduleDays or []) & set(other.scheduleDays or [])
            if common_days:
                # Check overlap in time interval [startTime, endTime]
                t_start = max(group_in.startTime, other.startTime)
                t_end = min(group_in.endTime, other.endTime)
                if t_start < t_end:
                    days_str = ", ".join(common_days)
                    return {
                        "code": 400,
                        "message": f"Dars vaqti mos kelmadi! {group_in.teacherName} ushbu vaqtda band (Guruh: '{other.groupName}', Kunlar: {days_str}, Vaqt: {other.startTime} - {other.endTime})"
                    }
    
    if db_group:
        # Check if schedule, duration, teacher or times changed
        schedule_changed = (
            db_group.scheduleDays != group_in.scheduleDays 
            or db_group.duration != group_in.duration
            or db_group.teacherName != group_in.teacherName
            or db_group.startTime != group_in.startTime
            or db_group.endTime != group_in.endTime
        )
        db_group.groupName = group_in.groupName
        db_group.scheduleDays = group_in.scheduleDays
        db_group.status = group_in.status
        db_group.duration = group_in.duration or 1.5
        db_group.teacherName = group_in.teacherName
        db_group.startTime = group_in.startTime
        db_group.endTime = group_in.endTime
        db_group.awards = group_in.awards or ["Award"]
        db.commit()
        db.refresh(db_group)
        
        if schedule_changed:
            # Sync/Regenerate current month lessons automatically!
            generate_lessons_helper(db, db_group, year_val, month_val)
    else:
        db_group = models.CRMGroup(
            id=group_in.id or str(uuid.uuid4())[:8],
            groupName=group_in.groupName,
            scheduleDays=group_in.scheduleDays,
            status=group_in.status,
            duration=group_in.duration or 1.5,
            teacherName=group_in.teacherName,
            startTime=group_in.startTime,
            endTime=group_in.endTime,
            awards=group_in.awards or ["Award"]
        )
        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        
        # Auto generate lessons for the new group for the current month!
        generate_lessons_helper(db, db_group, year_val, month_val)
        
    from app.routers.activity import log_activity
    log_activity(
        db=db,
        actor=user.username if user else "admin",
        action="saved",
        entity="crm_group",
        entity_id=db_group.id,
        entity_name=db_group.groupName
    )
    return {"code": 0, "data": db_group.id}

@router.post("/crm/group/delete")
def delete_group(
    body: dict = Body(...),
    user: models.User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    check_permission(user, 11, "delete", db)
    group_ids = body.get("ids", [])
    if not group_ids and body.get("id"):
        group_ids = [body.get("id")]
        
    from app.routers.activity import log_activity
    for g_id in group_ids:
        db_group = db.query(models.CRMGroup).filter(models.CRMGroup.id == str(g_id)).first()
        if db_group:
            g_name = db_group.groupName
            db.delete(db_group)
            log_activity(
                db=db,
                actor=user.username,
                action="deleted",
                entity="crm_group",
                entity_id=str(g_id),
                entity_name=g_name
            )
    db.commit()
    return {"code": 0, "data": True}


# --- Lessons ---

@router.get("/crm/lesson/list")
def get_lesson_list(groupId: str = Query(None), month: str = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.CRMLesson)
    if groupId:
        query = query.filter(models.CRMLesson.groupId == groupId)
    if month:
        query = query.filter(models.CRMLesson.date.like(f"{month}%"))
    
    lessons = query.order_by(models.CRMLesson.date.asc()).all()
    
    # Pre-fetch group names
    groups = {g.id: g.groupName for g in db.query(models.CRMGroup).all()}
    
    return {
        "code": 0,
        "data": {
            "list": [
                {
                    "id": l.id,
                    "groupId": l.groupId,
                    "groupName": groups.get(l.groupId, "Unknown Group"),
                    "date": l.date,
                    "dayOfWeek": l.dayOfWeek,
                    "lessonType": l.lessonType,
                    "duration": l.duration,
                    "title": l.title,
                    "createTime": l.createTime
                }
                for l in lessons
            ],
            "total": len(lessons)
        }
    }

def generate_lessons_helper(db: Session, group: models.CRMGroup, year: int, month: int):
    target_month_prefix = f"{year}-{month:02d}"
    
    # Calculate days in the target month
    import calendar
    import datetime
    num_days = calendar.monthrange(year, month)[1]
    target_dates = []
    for day in range(1, num_days + 1):
        dt = datetime.date(year, month, day)
        day_name = dt.strftime("%A")
        is_scheduled = any(sd.lower() == day_name.lower() for sd in (group.scheduleDays or []))
        if is_scheduled:
            target_dates.append((dt.strftime("%Y-%m-%d"), day_name))
            
    # Get existing lessons for this group & month
    existing_lessons = db.query(models.CRMLesson).filter(
        models.CRMLesson.groupId == group.id,
        models.CRMLesson.date.like(f"{target_month_prefix}%")
    ).all()
    
    existing_dates = {l.date: l for l in existing_lessons}
    target_dates_set = {d[0] for d in target_dates}
    
    # Delete lessons that are no longer in the schedule (only if they are Regular)
    for d, l in list(existing_dates.items()):
        if d not in target_dates_set and l.lessonType == "Regular":
            db.delete(l)
            
    # Add new lessons
    lessons_created = 0
    for date_str, day_name in target_dates:
        if date_str not in existing_dates:
            title = f"{group.groupName} - Regular Lesson"
            db_lesson = models.CRMLesson(
                id=str(uuid.uuid4())[:8] + f"-{date_str}",
                groupId=group.id,
                date=date_str,
                dayOfWeek=day_name,
                lessonType="Regular",
                duration=group.duration or 1.5,
                title=title
            )
            db.add(db_lesson)
            lessons_created += 1
        else:
            # Update duration/title of existing lesson if needed
            l = existing_dates[date_str]
            l.duration = group.duration or 1.5
            l.title = f"{group.groupName} - Regular Lesson"
            
    db.commit()
    return lessons_created

@router.post("/crm/lesson/generate")
def generate_lessons(query: schemas.CRMLessonGenerate, db: Session = Depends(get_db)):
    group = db.query(models.CRMGroup).filter(models.CRMGroup.id == query.groupId).first()
    if not group:
        return {"code": 500, "message": "Group not found"}
    lessons_created = generate_lessons_helper(db, group, query.year, query.month)
    return {"code": 0, "data": {"lessons_created": lessons_created}}

@router.post("/crm/lesson/save")
def save_lesson(lesson_in: schemas.CRMLessonCreate, db: Session = Depends(get_db)):
    db_lesson = None
    if lesson_in.id:
        db_lesson = db.query(models.CRMLesson).filter(models.CRMLesson.id == lesson_in.id).first()
        
    if db_lesson:
        db_lesson.date = lesson_in.date
        db_lesson.dayOfWeek = lesson_in.dayOfWeek
        db_lesson.lessonType = lesson_in.lessonType
        db_lesson.duration = lesson_in.duration
        db_lesson.title = lesson_in.title
    else:
        db_lesson = models.CRMLesson(
            id=lesson_in.id or str(uuid.uuid4())[:8],
            groupId=lesson_in.groupId,
            date=lesson_in.date,
            dayOfWeek=lesson_in.dayOfWeek,
            lessonType=lesson_in.lessonType or "Regular",
            duration=lesson_in.duration or 1.5,
            title=lesson_in.title
        )
        db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    from app.routers.activity import log_activity
    log_activity(
        db=db,
        actor="admin",
        action="saved",
        entity="crm_lesson",
        entity_id=db_lesson.id,
        entity_name=db_lesson.title or db_lesson.date
    )
    return {"code": 0, "data": db_lesson.id}

@router.post("/crm/lesson/delete")
def delete_lesson(body: dict = Body(...), db: Session = Depends(get_db)):
    lesson_ids = body.get("ids", [])
    if not lesson_ids and body.get("id"):
        lesson_ids = [body.get("id")]
        
    from app.routers.activity import log_activity
    for l_id in lesson_ids:
        db_lesson = db.query(models.CRMLesson).filter(models.CRMLesson.id == str(l_id)).first()
        if db_lesson:
            l_name = db_lesson.title or db_lesson.date
            db.delete(db_lesson)
            log_activity(
                db=db,
                actor="admin",
                action="deleted",
                entity="crm_lesson",
                entity_id=str(l_id),
                entity_name=l_name
            )
    db.commit()
    return {"code": 0, "data": True}


# --- Students ---

@router.get("/crm/student/list")
def get_student_list(
    month: str = Query(None),
    user: models.User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    if not month:
        month = datetime.datetime.now().strftime("%Y-%m")
        
    if user and user.role and user.role.lower() == "teacher":
        teacher_name = user.full_name if user.full_name else user.username
        teacher_groups = db.query(models.CRMGroup).filter(models.CRMGroup.teacherName == teacher_name).all()
        teacher_group_ids = [g.id for g in teacher_groups]
        if not teacher_group_ids:
            return {
                "code": 0,
                "data": {
                    "total": 0,
                    "list": []
                }
            }
        students = db.query(models.CRMStudent).filter(models.CRMStudent.groupId.in_(teacher_group_ids)).all()
    else:
        students = db.query(models.CRMStudent).all()
        
    # Get group objects mapping
    group_map = {g.id: g for g in db.query(models.CRMGroup).all()}
    
    # Pre-fetch user details
    users = {u.id: u.username for u in db.query(models.User).all()}
    
    # Pre-fetch coupon records for the selected month
    coupons = {}
    for c in db.query(models.CRMCoupon).filter(models.CRMCoupon.month == month).all():
        coupons[c.studentId] = (c.count, c.discount)
        
    # Calculate the max date string for the selected month (e.g. "2026-07-31")
    import calendar
    try:
        parts = month.split('-')
        y, m = int(parts[0]), int(parts[1])
        last_day = calendar.monthrange(y, m)[1]
        max_date_str = f"{y:04d}-{m:02d}-{last_day:02d}"
    except Exception:
        max_date_str = "9999-12-31"

    res_list = []
    for s in students:
        c_count, c_disc = coupons.get(s.id, (0, 0.0))
        
        # Calculate award totals up to the end of the selected month
        award_totals = {}
        group_obj = group_map.get(s.groupId) if s.groupId else None
        
        # Determine the awards we need to count (based on their assigned group)
        awards_list = group_obj.awards if (group_obj and group_obj.awards) else ["Award"]
        
        for award in awards_list:
            cnt = db.query(models.CRMHomework).join(models.CRMLesson).filter(
                models.CRMHomework.studentId == s.id,
                models.CRMHomework.reward == award,
                models.CRMLesson.date <= max_date_str
            ).count()
            award_totals[award] = cnt
            
        res_list.append({
            "id": s.id,
            "studentName": s.studentName,
            "groupId": s.groupId,
            "groupName": group_obj.groupName if group_obj else "No Group Assigned",
            "userId": s.userId,
            "username": users.get(s.userId, ""),
            "couponsCount": c_count,
            "discount": c_disc,
            "awardTotals": award_totals,
            "createTime": s.createTime
        })
        
    return {
        "code": 0,
        "data": {
            "list": res_list,
            "total": len(res_list)
        }
    }

@router.post("/crm/student/save")
def save_student(
    student_in: schemas.CRMStudentCreate,
    user: models.User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    check_permission(user, 12, "create" if not student_in.id else "edit", db)
    db_student = None
    if student_in.id:
        db_student = db.query(models.CRMStudent).filter(models.CRMStudent.id == student_in.id).first()
        
    # User linkage logic
    user_id = None
    resolved_username = student_in.username
    if not resolved_username and student_in.studentName:
        clean_name = "".join(c for c in student_in.studentName.lower() if c.isalnum() or c == ' ').replace(' ', '_')
        resolved_username = f"std_{clean_name}_{str(uuid.uuid4().int)[:4]}"
        
    if resolved_username:
        db_user = db.query(models.User).filter(models.User.username == resolved_username).first()
        if not db_user:
            db_user = crud.create_user(db, schemas.UserCreate(
                username=resolved_username,
                password=student_in.password or "123456",
                role="student",
                roleId="3",
                permissions=["crm:student:view"],
                email=student_in.email,
                phone=student_in.phone
            ))
        else:
            if student_in.password:
                db_user.hashed_password = crud.get_password_hash(student_in.password)
            if student_in.email:
                db_user.email = student_in.email
            if student_in.phone:
                db_user.phone = student_in.phone
            db.commit()
        user_id = db_user.id

    if db_student:
        db_student.studentName = student_in.studentName
        db_student.groupId = student_in.groupId
        if user_id:
            db_student.userId = user_id
    else:
        db_student = models.CRMStudent(
            id=student_in.id or str(uuid.uuid4())[:8],
            studentName=student_in.studentName,
            groupId=student_in.groupId,
            userId=user_id
        )
        db.add(db_student)
        
    db.commit()
    db.refresh(db_student)
    from app.routers.activity import log_activity
    log_activity(
        db=db,
        actor=user.username if user else "admin",
        action="saved",
        entity="crm_student",
        entity_id=db_student.id,
        entity_name=db_student.studentName
    )
    return {"code": 0, "data": db_student.id}

@router.post("/crm/student/delete")
def delete_student(
    body: dict = Body(...),
    user: models.User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    check_permission(user, 12, "delete", db)
    student_ids = body.get("ids", [])
    if not student_ids and body.get("id"):
        student_ids = [body.get("id")]
        
    from app.routers.activity import log_activity
    for s_id in student_ids:
        db_student = db.query(models.CRMStudent).filter(models.CRMStudent.id == str(s_id)).first()
        if db_student:
            s_name = db_student.studentName
            # Optional: delete associated student user account
            if db_student.userId:
                db_user = db.query(models.User).filter(models.User.id == db_student.userId).first()
                if db_user:
                    db.delete(db_user)
            db.delete(db_student)
            log_activity(
                db=db,
                actor=user.username,
                action="deleted",
                entity="crm_student",
                entity_id=str(s_id),
                entity_name=s_name
            )
    db.commit()
    return {"code": 0, "data": True}


@router.post("/crm/student/reassign-group")
def reassign_group(body: dict = Body(...), db: Session = Depends(get_db)):
    student_ids = body.get("studentIds", [])
    group_id = body.get("groupId")
    if not group_id:
        return {"code": 400, "message": "Guruh tanlanishi shart"}
    
    # Check if group exists
    group = db.query(models.CRMGroup).filter(models.CRMGroup.id == group_id).first()
    if not group:
        return {"code": 404, "message": "Guruh topilmadi"}

    for s_id in student_ids:
        student = db.query(models.CRMStudent).filter(models.CRMStudent.id == s_id).first()
        if student:
            student.groupId = group_id
    db.commit()
    return {"code": 0, "data": True}


# --- Coupon Management ---

@router.post("/crm/student/update-coupons")
def update_coupons(body: dict = Body(...), db: Session = Depends(get_db)):
    student_id = body.get("studentId")
    month = body.get("month")  # YYYY-MM
    count = body.get("count", 0)
    
    if not student_id or not month:
        return {"code": 500, "message": "studentId and month are required"}
        
    coupon = db.query(models.CRMCoupon).filter(
        models.CRMCoupon.studentId == student_id,
        models.CRMCoupon.month == month
    ).first()
    
    if coupon:
        coupon.count = count
    else:
        coupon = models.CRMCoupon(
            id=str(uuid.uuid4())[:8],
            studentId=student_id,
            month=month,
            count=count,
            discount=0.0
        )
        db.add(coupon)
        
    db.commit()
    return {"code": 0, "data": True}

@router.post("/crm/student/award-discount")
def award_discount(
    body: dict = Body(...),
    user: models.User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    check_permission(user, 12, "edit", db)
    group_id = body.get("groupId")
    month = body.get("month")  # YYYY-MM
    
    if not month:
        return {"code": 500, "message": "month is required"}
        
    # Get students in the group
    students_query = db.query(models.CRMStudent)
    if group_id:
        students_query = students_query.filter(models.CRMStudent.groupId == group_id)
    students = students_query.all()
    student_ids = [s.id for s in students]
    
    if not student_ids:
        return {"code": 0, "message": "No students found in the group", "data": []}
        
    # Retrieve coupons for these students in this month
    coupon_records = db.query(models.CRMCoupon).filter(
        models.CRMCoupon.studentId.in_(student_ids),
        models.CRMCoupon.month == month
    ).all()
    
    coupon_map = {c.studentId: c for c in coupon_records}
    
    # Find the maximum coupon count
    max_count = -1
    for s_id in student_ids:
        c_record = coupon_map.get(s_id)
        c_count = c_record.count if c_record else 0
        if c_count > max_count:
            max_count = c_count
            
    winners = []
    # If max coupon count is 0 or less, no discount is awarded
    if max_count > 0:
        for s_id in student_ids:
            c_record = coupon_map.get(s_id)
            c_count = c_record.count if c_record else 0
            
            # If a coupon record doesn't exist, create it
            if not c_record:
                c_record = models.CRMCoupon(
                    id=str(uuid.uuid4())[:8],
                    studentId=s_id,
                    month=month,
                    count=0,
                    discount=0.0
                )
                db.add(c_record)
                
            if c_count == max_count:
                c_record.discount = 50.0
                winners.append(s_id)
            else:
                c_record.discount = 0.0
    else:
        # Reset everyone to 0 discount
        for s_id in student_ids:
            c_record = coupon_map.get(s_id)
            if c_record:
                c_record.discount = 0.0
                
    db.commit()
    return {
        "code": 0,
        "message": f"Successfully calculated. Highest coupon count was {max(max_count, 0)}.",
        "data": {
            "winners": winners,
            "max_count": max(max_count, 0)
        }
    }


# --- Homework Management ---

@router.get("/crm/homework/list")
def get_homework_list(lessonId: str = Query(None), db: Session = Depends(get_db)):
    if not lessonId:
        return {"code": 500, "message": "lessonId is required"}
        
    lesson = db.query(models.CRMLesson).filter(models.CRMLesson.id == lessonId).first()
    if not lesson:
        return {"code": 500, "message": "Lesson not found"}
        
    # Get students in the group of the lesson
    students = db.query(models.CRMStudent).filter(models.CRMStudent.groupId == lesson.groupId).all()
    student_ids = [s.id for s in students]
    
    # Pre-fetch existing homework entries
    homework_records = db.query(models.CRMHomework).filter(
        models.CRMHomework.lessonId == lessonId,
        models.CRMHomework.studentId.in_(student_ids) if student_ids else False
    ).all()
    
    homework_map = {hw.studentId: hw for hw in homework_records}
    
    res_list = []
    for s in students:
        hw = homework_map.get(s.id)
        res_list.append({
            "id": hw.id if hw else None,
            "lessonId": lessonId,
            "studentId": s.id,
            "studentName": s.studentName,
            "completed": hw.completed if hw else 1,  # 1 = Completed (default)
            "notDoneDetails": hw.notDoneDetails if hw else "",
            "attendance": hw.attendance if hw else "present",
            "reward": hw.reward if hw else "none",
            "submittedOnTime": hw.submittedOnTime if hw else True
        })
        
    return {
        "code": 0,
        "data": {
            "list": res_list,
            "total": len(res_list)
        }
    }

@router.post("/crm/homework/save")
def save_homework(homework_in: schemas.CRMHomeworkCreate, db: Session = Depends(get_db)):
    hw = db.query(models.CRMHomework).filter(
        models.CRMHomework.lessonId == homework_in.lessonId,
        models.CRMHomework.studentId == homework_in.studentId
    ).first()
    
    if hw:
        hw.completed = homework_in.completed
        hw.notDoneDetails = homework_in.notDoneDetails
        hw.attendance = homework_in.attendance
        hw.reward = homework_in.reward
        hw.submittedOnTime = homework_in.submittedOnTime
    else:
        hw = models.CRMHomework(
            id=str(uuid.uuid4())[:8],
            lessonId=homework_in.lessonId,
            studentId=homework_in.studentId,
            completed=homework_in.completed,
            notDoneDetails=homework_in.notDoneDetails,
            attendance=homework_in.attendance,
            reward=homework_in.reward,
            submittedOnTime=homework_in.submittedOnTime
        )
        db.add(hw)
        
    db.commit()
    db.refresh(hw)
    from app.routers.activity import log_activity
    log_activity(
        db=db,
        actor="admin",
        action="saved",
        entity="crm_homework",
        entity_id=hw.id,
        entity_name=f"Homework for student {homework_in.studentId}"
    )
    return {"code": 0, "data": hw.id}


# --- Student Portal Endpoints ---

def get_student_by_username(username: str, db: Session):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    student = db.query(models.CRMStudent).filter(models.CRMStudent.userId == user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student

@router.get("/crm/student/my-info")
def get_my_info(username: str = Query(...), month: str = Query(None), db: Session = Depends(get_db)):
    student = get_student_by_username(username, db)
    if not month:
        month = datetime.datetime.now().strftime("%Y-%m")
        
    group_name = "No Group Assigned"
    if student.groupId:
        g = db.query(models.CRMGroup).filter(models.CRMGroup.id == student.groupId).first()
        if g:
            group_name = g.groupName
            
    # Get coupon count and discount
    coupon = db.query(models.CRMCoupon).filter(
        models.CRMCoupon.studentId == student.id,
        models.CRMCoupon.month == month
    ).first()
    
    return {
        "code": 0,
        "data": {
            "id": student.id,
            "studentName": student.studentName,
            "groupId": student.groupId,
            "groupName": group_name,
            "couponsCount": coupon.count if coupon else 0,
            "discount": coupon.discount if coupon else 0.0,
            "month": month
        }
    }

@router.get("/crm/student/my-lessons")
def get_my_lessons(username: str = Query(...), month: str = Query(None), db: Session = Depends(get_db)):
    student = get_student_by_username(username, db)
    if not student.groupId:
        return {"code": 0, "data": {"list": [], "total": 0}}
        
    query = db.query(models.CRMLesson).filter(models.CRMLesson.groupId == student.groupId)
    if month:
        query = query.filter(models.CRMLesson.date.like(f"{month}%"))
    lessons = query.order_by(models.CRMLesson.date.asc()).all()
    
    # Get all homework logs for this student
    homeworks = db.query(models.CRMHomework).filter(
        models.CRMHomework.studentId == student.id
    ).all()
    hw_map = {hw.lessonId: hw for hw in homeworks}
    
    res_list = []
    for l in lessons:
        hw = hw_map.get(l.id)
        res_list.append({
            "id": l.id,
            "date": l.date,
            "dayOfWeek": l.dayOfWeek,
            "lessonType": l.lessonType,
            "duration": l.duration,
            "title": l.title,
            "homework": {
                "completed": hw.completed if hw else -1,  # -1 means pending / not set
                "notDoneDetails": hw.notDoneDetails if hw else "",
                "attendance": hw.attendance if hw else "present",
                "reward": hw.reward if hw else "none",
                "submittedOnTime": hw.submittedOnTime if hw else True
            }
        })
        
    return {
        "code": 0,
        "data": {
            "list": res_list,
            "total": len(res_list)
        }
    }

@router.get("/crm/student/my-homeworks")
def get_my_homeworks(username: str = Query(...), db: Session = Depends(get_db)):
    student = get_student_by_username(username, db)
    homeworks = db.query(models.CRMHomework).filter(models.CRMHomework.studentId == student.id).all()
    
    # Pre-fetch lessons details
    lessons = {l.id: l for l in db.query(models.CRMLesson).all()}
    
    res_list = []
    for hw in homeworks:
        l = lessons.get(hw.lessonId)
        res_list.append({
            "id": hw.id,
            "lessonId": hw.lessonId,
            "lessonTitle": l.title if l else "Unknown Lesson",
            "lessonDate": l.date if l else "",
            "completed": hw.completed,
            "notDoneDetails": hw.notDoneDetails,
            "attendance": hw.attendance,
            "reward": hw.reward,
            "submittedOnTime": hw.submittedOnTime
        })
        
    return {
        "code": 0,
        "data": {
            "list": res_list,
            "total": len(res_list)
        }
    }


@router.get("/crm/homework/grid")
def get_homework_grid(groupId: str = Query(...), month: str = Query(...), db: Session = Depends(get_db)):
    group = db.query(models.CRMGroup).filter(models.CRMGroup.id == groupId).first()
    if not group:
        return {"code": 500, "message": "Group not found"}

    # Auto sync/generate lessons for this group & month automatically
    parts = month.split('-')
    year_val = int(parts[0])
    month_val = int(parts[1])
    generate_lessons_helper(db, group, year_val, month_val)

    # Fetch lessons in group for month
    lessons = db.query(models.CRMLesson).filter(
        models.CRMLesson.groupId == groupId,
        models.CRMLesson.date.like(f"{month}%")
    ).order_by(models.CRMLesson.date.asc()).all()
        
    lesson_ids = [l.id for l in lessons]

    # Fetch students in group
    students = db.query(models.CRMStudent).filter(models.CRMStudent.groupId == groupId).all()
    student_ids = [s.id for s in students]

    # Fetch all homework/attendance records
    records = db.query(models.CRMHomework).filter(
        models.CRMHomework.lessonId.in_(lesson_ids) if lesson_ids else False,
        models.CRMHomework.studentId.in_(student_ids) if student_ids else False
    ).all()

    # Map records by (studentId, lessonId)
    grid_map = {(r.studentId, r.lessonId): r for r in records}

    # Format the grid
    list_data = []
    for s in students:
        history = []
        present_count = 0
        total_marked = 0
        
        for l in lessons:
            r = grid_map.get((s.id, l.id))
            if r:
                history.append({
                    "id": r.id,
                    "lessonId": l.id,
                    "studentId": s.id,
                    "completed": r.completed,
                    "notDoneDetails": r.notDoneDetails or "",
                    "attendance": r.attendance or "unset",
                    "reward": r.reward or "none",
                    "submittedOnTime": r.submittedOnTime if r.submittedOnTime is not None else True
                })
                if r.attendance in ["present", "late", "absent"]:
                    total_marked += 1
                    if r.attendance in ["present", "late"]:
                        present_count += 1
            else:
                # Default empty
                history.append({
                    "id": None,
                    "lessonId": l.id,
                    "studentId": s.id,
                    "completed": -1, # Future/Not set
                    "notDoneDetails": "",
                    "attendance": "unset",
                    "reward": "none",
                    "submittedOnTime": True
                })
        
        attendance_rate = int(round((present_count / total_marked) * 100)) if total_marked > 0 else 100

        list_data.append({
            "studentId": s.id,
            "studentName": s.studentName,
            "presentCount": present_count,
            "totalMarked": total_marked,
            "attendanceRate": attendance_rate,
            "history": history
        })

    return {
        "code": 0,
        "data": {
            "lessons": [{
                "id": l.id,
                "date": l.date,
                "dayOfWeek": l.dayOfWeek,
                "title": l.title
            } for l in lessons],
            "grid": list_data
        }
    }
