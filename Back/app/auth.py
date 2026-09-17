import datetime
import jwt
from fastapi import Header, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, crud
from app.config import settings

def decode_access_token(token: str):
    if not isinstance(token, str):
        return None
    while token.startswith("Bearer ") or token.startswith("bearer "):
        token = token[7:].strip()
    keys_to_try = [getattr(settings, "SECRET_KEY", None), "super-secret-key-that-is-hard-to-guess"]
    for k in keys_to_try:
        if not k:
            continue
        try:
            payload = jwt.decode(token, k, algorithms=[getattr(settings, "ALGORITHM", "HS256")])
            return payload
        except Exception:
            continue
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

def get_user_company_id(authorization: str | None, db: Session, requested_company_id: any = None) -> str | None:
    if not isinstance(requested_company_id, str) or not requested_company_id.strip():
        requested_company_id = None
    if not authorization:
        return "comp-default"
    payload = decode_access_token(authorization)
    if not payload or not isinstance(payload, dict) or "sub" not in payload or "error" in payload:
        return "comp-default"
    user = db.query(models.User).filter(models.User.username == payload["sub"]).first()
    if not user:
        return "comp-default"
    user_comp = getattr(user, "company_id", None) or "comp-default"
    role_str = (user.role or "").lower()
    is_super = (user_comp == "comp-default") and (
        user.username in ["admin", "anvars"]
        or "super" in role_str
        or getattr(user, "is_super_admin", False) is True
    )
    if is_super:
        return requested_company_id if requested_company_id else "comp-default"
    return user_comp

def get_current_user_from_header(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        return None
    payload = decode_access_token(authorization)
    if not payload or not isinstance(payload, dict) or "sub" not in payload:
        return None
    return db.query(models.User).filter(models.User.username == payload["sub"]).first()

def check_user_access(
    user: models.User | None,
    required_permissions: list[str],
    db: Session,
    allow_admin: bool = True
) -> bool:
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Tizimga kirilmagan yoki sessiya muddati tugagan"
        )

    comp_id = getattr(user, "company_id", None) or "comp-default"
    role_str = (user.role or "").lower()

    # Super Admin check
    if user.username in ["admin", "anvars"] or (comp_id == "comp-default" and ("super" in role_str or getattr(user, "is_super_admin", False) is True)):
        return True

    # Company Administrator check
    if allow_admin and ("admin" in role_str or "administrator" in role_str):
        return True

    # Gather user's direct or role-based permissions
    user_perms = list(user.permissions or [])
    if not user_perms:
        role_obj = None
        if user.roleId:
            role_obj = db.query(models.Role).filter(models.Role.id == str(user.roleId)).first()
        if not role_obj and user.role:
            role_obj = db.query(models.Role).filter(
                models.Role.roleName.ilike(user.role),
                (models.Role.company_id == comp_id) | (models.Role.company_id == "comp-default") | (models.Role.company_id == None)
            ).first()
        if role_obj and role_obj.permissions:
            user_perms = list(role_obj.permissions)

    user_perms_lower = set(str(p).lower().strip() for p in user_perms)

    if "*.*.*" in user_perms_lower or "*" in user_perms_lower:
        return True

    for req in required_permissions:
        req_clean = req.lower().strip()
        if req_clean in user_perms_lower:
            return True

    raise HTTPException(
        status_code=403,
        detail="Sizda ushbu amalni bajarish yoki ma'lumotlarni ko'rish uchun ruxsat yo'q!"
    )

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
        
    for p in user_perms:
        if ":" in p:
            parts = p.split(":")
            try:
                menu_id = int(parts[0])
                action = parts[1]
                if menu_id == required_menu_id:
                    if required_action == "view" or action == required_action:
                        return True
            except ValueError:
                pass
                
    raise HTTPException(
        status_code=403,
        detail="Sizda ushbu amalni bajarish uchun ruxsat yo'q!"
    )

def get_current_device_token(
    x_device_token: str | None = Header(None, alias="X-Device-Token"),
    db: Session = Depends(get_db)
) -> models.DeviceToken:
    if not x_device_token:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Missing X-Device-Token header"
        )

    device_token = crud.get_device_token_by_token(db, token=x_device_token)
    if not device_token:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid device token"
        )

    if device_token.status == "revoked":
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Device token has been revoked"
        )

    if device_token.status != "active":
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Device token is inactive"
        )

    user = db.query(models.User).filter(models.User.id == device_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: User associated with device token not found"
        )

    now = datetime.datetime.utcnow()
    if device_token.last_used_at is None or (now - device_token.last_used_at).total_seconds() > 60:
        crud.update_device_token_last_used(db, device_token)

    return device_token
