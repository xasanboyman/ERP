import jwt
import datetime
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models

router = APIRouter()

SECRET_KEY = "super-secret-key-that-is-hard-to-guess"
ALGORITHM = "HS256"

def create_access_token(username: str):
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    to_encode = {"sub": username, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        if not isinstance(token, str):
            return None
        while token.startswith("Bearer ") or token.startswith("bearer "):
            token = token[7:].strip()
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "token_expired"}
    except jwt.PyJWTError:
        return {"error": "token_invalid"}
    except Exception:
        return None

def _user_initials(user) -> str:
    """Compute two-letter initials from full_name, falling back to username."""
    source = getattr(user, "full_name", None) or getattr(user, "name", None) or getattr(user, "username", None) or getattr(user, "account", "?")
    source = str(source).strip()
    parts = source.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return source[:2].upper()

def _user_dict(user, db: Session = None, include_password: str | None = None) -> dict:
    """Serialise a User ORM object to a response dict."""
    user_role = getattr(user, "role", "worker") or "worker"
    user_role_id = getattr(user, "roleId", "2") or "2"
    username = getattr(user, "username", None) or getattr(user, "account", "user")

    is_super = False
    db_role = None
    if db:
        if user_role_id:
            db_role = db.query(models.Role).filter(models.Role.id == str(user_role_id)).first()
        if not db_role and user_role:
            db_role = db.query(models.Role).filter(models.Role.roleName.ilike(user_role)).first()
    
    if db_role and db_role.permissions:
        perms_list = db_role.permissions if isinstance(db_role.permissions, list) else []
        flat_perms = []
        for p in perms_list:
            if isinstance(p, str):
                flat_perms.append(p)
            elif isinstance(p, dict) and 'path' in p:
                flat_perms.append(p['path'])
        clean_perms = flat_perms if flat_perms else []
    else:
        clean_perms = []
    
    comp_id = getattr(user, "company_id", None) or "comp-default"

    # Super Administrator is strictly reserved for the root company's super admins
    is_super = False
    if comp_id == 'comp-default':
        if username in ['admin', 'anvars']:
            is_super = True
        elif getattr(user, 'is_super_admin', False) is True or (user_role and user_role.lower() in ['super administrator', 'superadmin']):
            is_super = True
        elif db_role and db_role.roleName == 'Super Administrator':
            is_super = True
    
    if is_super:
        clean_perms = ['*.*.*']
    company = None
    if db:
        company = db.query(models.Company).filter(models.Company.id == comp_id).first()
        if not company:
            company = db.query(models.Company).filter(models.Company.id == "comp-default").first()

    company_name = company.name if company else "Bosh Korxona"
    company_plan = company.plan if company else ("pro" if is_super else "basic")
    company_features = company.features if (company and company.features) else {}
    if is_super:
        company_plan = "pro"
        company_features = {"ai": True, "upcoming": True}

    token = f"Bearer {create_access_token(username)}"
    return {
        "id": getattr(user, "id", 1),
        "username": username,
        "full_name": getattr(user, "full_name", None) or getattr(user, "name", username),
        "initials": _user_initials(user),
        "avatar": getattr(user, "avatar", "") or "",
        "role": user_role,
        "roleId": user_role_id,
        "email": getattr(user, "email", "") or "",
        "department_id": getattr(user, "department_id", "") or getattr(user, "departmentId", "") or "",
        "company_id": comp_id,
        "company_name": company_name,
        "company_plan": company_plan,
        "company_features": company_features,
        "is_super_admin": is_super,
        "permissions": clean_perms,
        "token": token,
        **({"password": include_password} if include_password is not None else {}),
    }

@router.post("/user/login")
def login(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    # 1. Try matching User by username
    db_user = crud.get_user_by_username(db, username=user_in.username)

    # 2. If not found in User table, search Worker table by account, name, or employee_code
    if not db_user:
        db_worker = db.query(models.Worker).filter(
            (models.Worker.account == user_in.username) |
            (models.Worker.employee_code == user_in.username) |
            (models.Worker.name == user_in.username)
        ).first()

        if db_worker:
            acc_name = db_worker.account or f"worker_{db_worker.id}"
            db_user = db.query(models.User).filter(models.User.username == acc_name).first()
            w_role = db_worker.role or "Cashier"
            # Look up from Role table
            db_role_match = db.query(models.Role).filter(
                (models.Role.roleName.ilike(w_role)) |
                (models.Role.id == w_role)
            ).first()
            w_role_id = db_role_match.id if db_role_match else "3"
            w_perms = db_role_match.permissions if db_role_match and db_role_match.permissions else []
            # Flatten permissions if they contain route objects
            flat_perms = []
            for p in w_perms:
                if isinstance(p, str):
                    flat_perms.append(p)
                elif isinstance(p, dict) and 'path' in p:
                    flat_perms.append(p['path'])
            w_perms = flat_perms
            if not db_user:
                db_user = crud.create_user(db, schemas.UserCreate(
                    username=acc_name,
                    password=user_in.password or "123456",
                    full_name=db_worker.name,
                    role=w_role,
                    roleId=w_role_id,
                    avatar=db_worker.avatar,
                    company_id=getattr(db_worker, "company_id", None) or "comp-default",
                    permissions=w_perms
                ))
            else:
                db_user.full_name = db_worker.name
                if db_worker.avatar:
                    db_user.avatar = db_worker.avatar
                db.commit()

    if not db_user:
        # Only auto-create admin account
        if user_in.username == "admin":
            db_user = crud.create_user(db, schemas.UserCreate(
                username="admin",
                password=user_in.password or "admin",
                full_name="Administrator",
                role="Super Administrator",
                roleId="1",
                permissions=["*.*.*"]
            ))
        else:
            return {"code": 500, "message": "Xodim topilmadi yoki parol noto'g'ri"}
    else:
        # Check password if set
        if db_user.hashed_password:
            valid_pass = crud.verify_password(user_in.password, db_user.hashed_password)
            if not valid_pass:
                return {"code": 500, "message": "Xodim paroli noto'g'ri"}

    return {
        "code": 0,
        "data": _user_dict(db_user, db=db, include_password=user_in.password)
    }

@router.get("/user/employees")
def get_auth_employees(db: Session = Depends(get_db)):
    """List all active employees / users for employee authentication & cashier switching."""
    workers = db.query(models.Worker).filter(models.Worker.status == 1).all()
    users = db.query(models.User).all()

    emp_list = []
    seen = set()

    for w in workers:
        acc = w.account or f"emp_{w.id}"
        seen.add(acc)
        emp_list.append({
            "id": w.id,
            "username": acc,
            "full_name": w.name,
            "role": w.role or "Kassir",
            "avatar": w.avatar or "",
            "phone": w.phone or "",
            "initials": _user_initials(w)
        })

    for u in users:
        if u.username not in seen:
            emp_list.append({
                "id": f"u_{u.id}",
                "username": u.username,
                "full_name": u.full_name or u.username,
                "role": u.role or "Admin",
                "avatar": u.avatar or "",
                "phone": u.phone or "",
                "initials": _user_initials(u)
            })

    return {
        "code": 0,
        "data": emp_list
    }

@router.get("/user/loginOut")
def logout():
    return {"code": 0, "data": None}

@router.get("/user/list")
def user_list(
    username: str = Query(None),
    pageIndex: int = Query(1),
    pageSize: int = Query(10),
    db: Session = Depends(get_db)
):
    users = db.query(models.User).all()
    if username:
        users = [u for u in users if username.lower() in u.username.lower()]

    total = len(users)
    start = (pageIndex - 1) * pageSize
    end = start + pageSize
    paginated = users[start:end]

    return {
        "code": 0,
        "data": {
            "total": total,
            "list": [_user_dict(u, db=db, include_password="••••••") for u in paginated]
        }
    }

@router.post("/user/avatar")
def update_user_avatar(body: dict = Body(...), db: Session = Depends(get_db)):
    username = body.get("username")
    avatar   = body.get("avatar")
    full_name = body.get("full_name")

    if not username:
        return {"code": 500, "message": "username is required"}

    db_user = crud.get_user_by_username(db, username)
    if not db_user:
        return {"code": 404, "message": "User not found"}

    if avatar is not None:
        db_user.avatar = avatar
    if full_name is not None:
        db_user.full_name = full_name

    db.commit()
    db.refresh(db_user)
    return {"code": 0, "data": _user_dict(db_user, db=db)}

@router.post("/user/save")
def save_user(body: dict = Body(...), db: Session = Depends(get_db)):
    user_id  = body.get("id")
    username = body.get("username")
    password = body.get("password")
    full_name = body.get("full_name")
    avatar   = body.get("avatar")
    role     = body.get("role", "worker")
    role_id  = body.get("roleId", "2")
    email    = body.get("email")
    dept_id  = body.get("department_id")
    perms    = body.get("permissions", [])

    if not username:
        return {"code": 500, "message": "username is required"}

    db_user = None
    if user_id:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        db_user = crud.get_user_by_username(db, username)

    if db_user:
        db_user.username  = username
        if password:
            db_user.hashed_password = crud.get_password_hash(password)
        if full_name is not None:
            db_user.full_name = full_name
        if avatar is not None:
            db_user.avatar = avatar
        db_user.role          = role
        db_user.roleId        = role_id
        db_user.email         = email
        db_user.department_id = dept_id
        db_user.permissions   = perms
    else:
        db_user = crud.create_user(db, schemas.UserCreate(
            username=username,
            password=password or "123456",
            full_name=full_name,
            role=role,
            roleId=role_id,
            email=email,
            department_id=dept_id,
            permissions=perms,
            avatar=avatar
        ))

    db.commit()
    db.refresh(db_user)
    return {"code": 0, "data": _user_dict(db_user, db=db)}
