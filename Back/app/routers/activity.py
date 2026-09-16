import datetime
from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.auth import get_user_company_id

router = APIRouter()


def log_activity(
    db: Session,
    actor: str,
    action: str,
    entity: str,
    entity_id: str = None,
    entity_name: str = None,
    commit: bool = True,
    company_id: str = None,
):
    """Helper called by all routers to record an activity and broadcast real-time sync."""
    entry = models.ActivityLog(
        company_id=company_id or "comp-default",
        actor=actor,
        action=action,
        entity=entity,
        entity_id=entity_id,
        entity_name=entity_name,
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    db.add(entry)
    if commit:
        db.commit()

    try:
        from app.websocket_manager import manager
        manager.broadcast_sync(
            entity=entity,
            action=action,
            entity_id=entity_id,
            data={"entity_name": entity_name, "actor": actor, "company_id": company_id},
            actor=actor
        )
    except Exception as ws_err:
        pass


@router.get("/activity/list")
def get_activity_list(
    pageIndex: int = Query(1),
    pageSize: int = Query(20),
    company_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    target_company = get_user_company_id(authorization, db, company_id)
    query = db.query(models.ActivityLog)
    if target_company and target_company != "comp-default":
        query = query.filter(models.ActivityLog.company_id == target_company)

    logs = query.order_by(models.ActivityLog.id.desc()).all()

    total = len(logs)
    start = (pageIndex - 1) * pageSize
    end = start + pageSize
    paginated = logs[start:end]

    return {
        "code": 0,
        "data": {
            "total": total,
            "list": [
                {
                    "id": log.id,
                    "company_id": getattr(log, "company_id", "comp-default"),
                    "actor": log.actor,
                    "action": log.action,
                    "entity": log.entity,
                    "entityId": log.entity_id,
                    "entityName": log.entity_name,
                    "timestamp": log.timestamp,
                }
                for log in paginated
            ],
        },
    }
