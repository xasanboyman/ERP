import os
import uuid
import shutil
from fastapi import APIRouter, Depends, Query, Body, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.routers.activity import log_activity

router = APIRouter()

@router.get("/product/list")
def get_product_list(
    productName: str = Query(None),
    category: str = Query(None),
    shtrix_code: str = Query(None),
    brand_name: str = Query(None),
    pageIndex: int = Query(1),
    pageSize: int = Query(10),
    db: Session = Depends(get_db)
):
    products = crud.get_products(db)

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
def get_product_by_barcode(code: str, db: Session = Depends(get_db)):
    clean_code = code.strip()
    prod = db.query(models.Product).filter(
        (models.Product.shtrix_code == clean_code) |
        (models.Product.SKU == clean_code) |
        (models.Product.id == clean_code) |
        (models.Product.mxik_code == clean_code)
    ).first()

    selected_pkg = None
    if not prod:
        pkg = db.query(models.ProductPackaging).filter(models.ProductPackaging.shtrix_code == clean_code).first()
        if pkg:
            prod = db.query(models.Product).filter(models.Product.id == pkg.product_id).first()
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
def get_product_detail(id: str = Query(...), db: Session = Depends(get_db)):
    prod = db.query(models.Product).filter(models.Product.id == id).first()
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
def product_save(prod_in: schemas.ProductCreate, db: Session = Depends(get_db)):
    prod_id = getattr(prod_in, "id", None)
    shtrix = getattr(prod_in, "shtrix_code", None)
    classifier_id = getattr(prod_in, "classifier_id", None)
    sku = getattr(prod_in, "SKU", None)

    existing = None
    if prod_id:
        existing = db.query(models.Product).filter(models.Product.id == prod_id).first()
    if not existing and shtrix and shtrix.strip():
        existing = db.query(models.Product).filter(models.Product.shtrix_code == shtrix.strip()).first()
    if not existing and classifier_id:
        existing = db.query(models.Product).filter(models.Product.classifier_id == classifier_id).first()
    if not existing and sku and sku.strip():
        existing = db.query(models.Product).filter(models.Product.SKU == sku.strip()).first()

    is_existing = (existing is not None) and (not prod_id)
    action = "updated" if existing else "created"

    product = crud.create_product(db, prod_in)

    log_activity(
        db,
        actor="admin",
        action=action,
        entity="product",
        entity_id=getattr(product, "id", None) or prod_id,
        entity_name=prod_in.productName,
    )
    return {
        "code": 0,
        "data": "success",
        "is_existing": is_existing,
        "total_stock": getattr(product, "quantityInStock", 0),
        "added_qty": prod_in.quantityInStock or 1,
        "product_name": getattr(product, "productName", prod_in.productName)
    }


@router.post("/product/delete")
def product_delete(body: dict = Body(...), db: Session = Depends(get_db)):
    ids = body.get("ids")
    if not ids:
        return {"code": 500, "message": "Iltimos, o'chirish uchun ma'lumotni tanlang"}

    if isinstance(ids, str):
        ids = [ids]

    for i in ids:
        product = db.query(models.Product).filter(models.Product.id == i).first()
        name = product.productName if product else i
        crud.delete_product(db, i)
        log_activity(db, actor="admin", action="deleted", entity="product", entity_id=i, entity_name=name)

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
