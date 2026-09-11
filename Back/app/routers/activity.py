import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter()


def log_activity(
    db: Session,
    actor: str,
    action: str,
    entity: str,
    entity_id: str = None,
    entity_name: str = None,
    commit: bool = True,
):
    """Helper called by all routers to record an activity and broadcast real-time sync."""
    entry = models.ActivityLog(
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
            data={"entity_name": entity_name, "actor": actor},
            actor=actor
        )
    except Exception as ws_err:
        pass


@router.get("/activity/list")
def get_activity_list(
    pageIndex: int = Query(1),
    pageSize: int = Query(20),
    db: Session = Depends(get_db),
):
    logs = (
        db.query(models.ActivityLog)
        .order_by(models.ActivityLog.id.desc())
        .all()
    )

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
