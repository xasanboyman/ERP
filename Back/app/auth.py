import datetime
from fastapi import Header, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, crud
from app.routers.crm import get_current_user_required
from app.routers.auth import create_access_token, decode_access_token


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
