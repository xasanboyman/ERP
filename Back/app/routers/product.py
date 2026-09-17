import os
import uuid
import shutil
from fastapi import APIRouter, Depends, Query, Body, UploadFile, File, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.routers.activity import log_activity
from app.cache import invalidate_analytics, invalidate_sales
from app.auth import decode_access_token, get_current_user_from_header, check_user_access

router = APIRouter()

def get_user_company_id(authorization: str, db: Session, requested_company_id: any = None) -> str | None:
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
        return requested_company_id
    return user_comp

@router.get("/product/list")
def get_product_list(
    productName: str = Query(None),
    category: str = Query(None),
    shtrix_code: str = Query(None),
    brand_name: str = Query(None),
    company_id: str = Query(None),
    pageIndex: int = Query(1),
    pageSize: int = Query(10),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, company_id)
    products = crud.get_products(db, company_id=target_company)

    if productName:
        term = productName.lower()
        products = [
            p for p in products 
            if term in (p.productName or "").lower() 
            or term in (p.SKU or "").lower()
            or term in (p.brand_name or "").lower()
            or term in (p.shtrix_code or "").lower()
            or term in (p.mxik_code or "").lower()
        ]
    if category:
        products = [p for p in products if category.lower() in (p.category or "").lower()]
    if shtrix_code:
        products = [p for p in products if p.shtrix_code == shtrix_code.strip()]
    if brand_name:
        products = [p for p in products if brand_name.lower() in (p.brand_name or "").lower()]

    total = len(products)
    start = (pageIndex - 1) * pageSize
    end = start + pageSize
    paginated = products[start:end]

    def serialize_packagings(p):
        if not hasattr(p, "packagings") or not p.packagings:
            return []
        return [
            {
                "id": pkg.id,
                "unit_name": pkg.unit_name,
                "conversion_factor": pkg.conversion_factor,
                "price": pkg.price,
                "cost": pkg.cost,
                "shtrix_code": pkg.shtrix_code,
                "is_base_unit": pkg.is_base_unit
            }
            for pkg in p.packagings
        ]

    return {
        "code": 0,
        "data": {
            "total": total,
            "list": [
                {
                    "id": p.id,
                    "productName": p.productName,
                    "SKU": p.SKU,
                    "category": p.category,
                    "price": p.price,
                    "cost": p.cost,
                    "quantityInStock": p.quantityInStock,
                    "status": p.status,
                    "classifier_id": p.classifier_id,
                    "shtrix_code": p.shtrix_code,
                    "mxik_code": p.mxik_code,
                    "brand_name": p.brand_name,
                    "attribute_name": p.attribute_name,
                    "unit": p.unit,
                    "image_url": getattr(p, "image_url", None),
                    "expiration_date": getattr(p, "expiration_date", None),
                    "branch_id": getattr(p, "branch_id", None),
                    "remark": p.remark,
                    "createTime": p.createTime,
                    "packagings": serialize_packagings(p)
                }
                for p in paginated
            ]
        }
    }

@router.get("/product/by-barcode/{code}")
@router.get("/api/product/by-barcode/{code}")
def get_product_by_barcode(
    code: str,
    company_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    clean_code = code.strip()
    target_company = get_user_company_id(authorization, db, company_id)

    query = db.query(models.Product).filter(
        (models.Product.shtrix_code == clean_code) |
        (models.Product.SKU == clean_code) |
        (models.Product.id == clean_code) |
        (models.Product.mxik_code == clean_code)
    )
    if target_company:
        query = query.filter(models.Product.company_id == target_company)
    prod = query.first()

    selected_pkg = None
    if not prod:
        pkg_query = db.query(models.ProductPackaging).join(models.Product).filter(models.ProductPackaging.shtrix_code == clean_code)
        if target_company:
            pkg_query = pkg_query.filter(models.Product.company_id == target_company)
        pkg = pkg_query.first()
        if pkg:
            p_query = db.query(models.Product).filter(models.Product.id == pkg.product_id)
            if target_company:
                p_query = p_query.filter(models.Product.company_id == target_company)
            prod = p_query.first()
            if prod:
                selected_pkg = {
                    "id": pkg.id,
                    "unit_name": pkg.unit_name,
                    "conversion_factor": pkg.conversion_factor,
                    "price": pkg.price,
                    "cost": pkg.cost,
                    "shtrix_code": pkg.shtrix_code
                }

    if prod:
        packagings_list = [
            {
                "id": p.id,
                "unit_name": p.unit_name,
                "conversion_factor": p.conversion_factor,
                "price": p.price,
                "cost": p.cost,
                "shtrix_code": p.shtrix_code,
                "is_base_unit": p.is_base_unit
            }
            for p in (prod.packagings or [])
        ]
        return {
            "code": 0,
            "message": "Product found",
            "data": {
                "id": prod.id,
                "product_id": prod.id,
                "productName": prod.productName,
                "product_name": prod.productName,
                "price": selected_pkg["price"] if selected_pkg else prod.price,
                "cost": selected_pkg["cost"] if selected_pkg else prod.cost,
                "shtrix_code": prod.shtrix_code or clean_code,
                "mxik_code": prod.mxik_code,
                "brand_name": prod.brand_name,
                "image_url": getattr(prod, "image_url", None),
                "expiration_date": getattr(prod, "expiration_date", None),
                "quantityInStock": prod.quantityInStock,
                "unit": prod.unit,
                "packagings": packagings_list,
                "selected_packaging": selected_pkg
            }
        }

    return {
        "code": 404,
        "message": "Product not found",
        "data": None
    }


@router.get("/product/detail")
@router.get("/api/product/detail")
def get_product_detail(
    id: str = Query(...),
    company_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, company_id)
    q = db.query(models.Product).filter(models.Product.id == id)
    if target_company:
        q = q.filter(models.Product.company_id == target_company)
    prod = q.first()
    if not prod:
        return {"code": 404, "message": "Product not found"}

    packagings_list = [
        {
            "id": p.id,
            "unit_name": p.unit_name,
            "conversion_factor": p.conversion_factor,
            "price": p.price,
            "cost": p.cost,
            "shtrix_code": p.shtrix_code,
            "is_base_unit": p.is_base_unit
        }
        for p in (prod.packagings or [])
    ]

    return {
        "code": 0,
        "data": {
            "id": prod.id,
            "productName": prod.productName,
            "SKU": prod.SKU,
            "category": prod.category,
            "price": prod.price,
            "cost": prod.cost,
            "quantityInStock": prod.quantityInStock,
            "status": prod.status,
            "classifier_id": prod.classifier_id,
            "shtrix_code": prod.shtrix_code,
            "mxik_code": prod.mxik_code,
            "brand_name": prod.brand_name,
            "attribute_name": prod.attribute_name,
            "unit": prod.unit,
            "image_url": getattr(prod, "image_url", None),
            "remark": prod.remark,
            "createTime": prod.createTime,
            "packagings": packagings_list
        }
    }



@router.post("/product/save")
def product_save(
    prod_in: schemas.ProductCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    current_user = get_current_user_from_header(authorization, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Tizimga kirilmagan yoki sessiya yaroqsiz")
    check_user_access(current_user, ["product:create", "product:edit", "product"], db)

    prod_id = getattr(prod_in, "id", None)
    target_company = get_user_company_id(authorization, db, getattr(prod_in, "company_id", None))
    if prod_id and target_company:
        existing_check = db.query(models.Product).filter(models.Product.id == prod_id).first()
        if existing_check and existing_check.company_id != target_company:
            raise HTTPException(status_code=403, detail="Boshqa kompaniyaning mahsulotini tahrirlash taqiqlangan")
    product = crud.create_product(db, prod_in, company_id=target_company)
    is_existing = getattr(product, "is_existing_record", False)
    action = "updated" if (is_existing or prod_id) else "created"

    log_activity(
        db,
        actor="admin",
        action=action,
        entity="product",
        entity_id=getattr(product, "id", None) or prod_id,
        entity_name=prod_in.productName,
    )
    invalidate_analytics()
    invalidate_sales()

    return {
        "code": 0,
        "data": "success",
        "is_existing": is_existing,
        "total_stock": getattr(product, "quantityInStock", 0),
        "added_qty": prod_in.quantityInStock or 1,
        "product_name": getattr(product, "productName", prod_in.productName)
    }


@router.post("/product/delete")
def product_delete(
    body: dict = Body(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    current_user = get_current_user_from_header(authorization, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Tizimga kirilmagan yoki sessiya yaroqsiz")
    check_user_access(current_user, ["product:delete", "product"], db)

    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "Iltimos, o'chirish uchun ma'lumotni tanlang"}

    if isinstance(ids, str):
        ids = [ids]

    target_company = get_user_company_id(authorization, db, body.get("company_id"))
    query = db.query(models.Product).filter(models.Product.id.in_(ids))
    if target_company:
        query = query.filter(models.Product.company_id == target_company)
    products = query.all()
    allowed_ids = [p.id for p in products]

    if not allowed_ids:
        return {"code": 404, "message": "O'chirish uchun mahsulotlar topilmadi"}

    prod_dict = {p.id: p.productName for p in products}

    db.query(models.ProductPackaging).filter(models.ProductPackaging.product_id.in_(allowed_ids)).delete(synchronize_session=False)
    db.query(models.Product).filter(models.Product.id.in_(allowed_ids)).delete(synchronize_session=False)

    for i in allowed_ids:
        name = prod_dict.get(i, i)
        log_activity(db, actor="admin", action="deleted", entity="product", entity_id=i, entity_name=name, commit=False)

    db.commit()
    invalidate_analytics()
    invalidate_sales()

    return {"code": 0, "data": "success"}

@router.post("/product/upload-image")
def upload_product_image(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Fayl tanlanmagan")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"]:
        ext = ".png"

    from app.storage import upload_file_bytes
    file_bytes = file.file.read()
    content_type = file.content_type or "image/png"
    url = upload_file_bytes(file_bytes, file.filename, content_type=content_type)

    return {"code": 0, "message": "success", "data": {"url": url}}
