from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from .. import crud, schemas
from import_classifiers import import_all_classifiers

router = APIRouter(prefix="/classifier", tags=["Classifier"])

@router.get("/list", response_model=schemas.ClassifierListResponse)
def list_classifier_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    brand: Optional[str] = None,
    mxik_code: Optional[str] = None,
    shtrix_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    items, total = crud.get_classifier_items(
        db,
        page=page,
        page_size=page_size,
        search=search,
        brand=brand,
        mxik_code=mxik_code,
        shtrix_code=shtrix_code
    )
    return {
        "code": 0,
        "message": "success",
        "data": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/by-barcode/{shtrix_code}")
def get_classifier_by_barcode(shtrix_code: str, db: Session = Depends(get_db)):
    item = crud.get_classifier_by_barcode(db, shtrix_code)
    if not item:
        return {"code": 0, "message": "not_found", "data": None}
    return {"code": 0, "message": "success", "data": item}

@router.get("/by-mxik/{mxik_code}")
def get_classifier_by_mxik(mxik_code: str, db: Session = Depends(get_db)):
    item = crud.get_classifier_by_mxik(db, mxik_code)
    if not item:
        return {"code": 0, "message": "not_found", "data": None}
    return {"code": 0, "message": "success", "data": item}

@router.get("/{item_id}")
def get_classifier_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_classifier_by_id(db, item_id)
    if not item:
        return {"code": 0, "message": "not_found", "data": None}
    return {"code": 0, "message": "success", "data": item}


@router.post("/import")
def trigger_classifier_import():
    try:
        import_all_classifiers()
        return {"code": 0, "message": "Classifier re-import completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
