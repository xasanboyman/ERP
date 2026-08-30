import datetime
import jwt
from fastapi import Header, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, crud
from app.config import settings

def decode_access_token(token: str):
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except Exception:
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
