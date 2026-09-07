from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from .. import crud, schemas
from import_classifiers import import_all_classifiers

import urllib.request
import urllib.parse
import json

def fetch_tasnif_elasticsearch(query: str, page: int = 1, page_size: int = 20, lang: str = "uz_latn"):
    try:
        p_zero = max(0, page - 1)
        url = f"https://tasnif.soliq.uz/api/cls-api/elasticsearch/search?lang={urllib.parse.quote(lang)}&search={urllib.parse.quote(query)}&size={page_size}&page={p_zero}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 ERP/1.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and data.get("success") and isinstance(data.get("data"), list):
                mapped = []
                for idx, it in enumerate(data.get("data", [])):
                    code_id = 0
                    if it.get("mxikCode") and it.get("mxikCode")[-8:].isdigit():
                        code_id = int(it.get("mxikCode")[-8:])
                    else:
                        code_id = (page * 100) + idx
                    mapped.append(schemas.ClassifierItemResponse(
                        id=code_id,
                        mxik_code=it.get("mxikCode") or "",
                        mxik_name=it.get("name") or "",
                        brand_name=it.get("brandName") or "",
                        attribute_name=it.get("attributeName") or "",
                        shtrix_code=it.get("internationalCode") or "",
                        unit=it.get("unitsName") or "dona",
                        group_name=it.get("groupName") or "",
                        class_name=it.get("className") or "",
                        position_name=it.get("positionName") or "",
                        subposition_name=it.get("subPositionName") or ""
                    ))
                return mapped, data.get("recordTotal", len(mapped))
    except Exception:
        pass
    return None, 0

router = APIRouter(prefix="/classifier", tags=["Classifier"])

@router.get("/list", response_model=schemas.ClassifierListResponse)
def list_classifier_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    brand: Optional[str] = None,
    mxik_code: Optional[str] = None,
    shtrix_code: Optional[str] = None,
    mode: Optional[str] = "extended",
    db: Session = Depends(get_db)
):
    # Try Tasnif Soliq Elasticsearch extended search first if searching
    if search and mode != "local":
        es_items, es_total = fetch_tasnif_elasticsearch(search.strip(), page=page, page_size=page_size)
        if es_items and len(es_items) > 0:
            return {
                "code": 0,
                "message": "success",
                "data": es_items,
                "total": es_total,
                "page": page,
                "page_size": page_size
            }

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
    if not item and shtrix_code:
        es_items, _ = fetch_tasnif_elasticsearch(shtrix_code.strip(), page=1, page_size=1)
        if es_items and len(es_items) > 0:
            return {"code": 0, "message": "success", "data": es_items[0]}
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
