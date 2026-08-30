#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for ERP System.
Provides AI agents with structured, secure access to ERP database, business logic,
inventory, sales, HR/payroll, production cutting orders, CRM, and analytics.

Includes Role-Based Access Control (RBAC) security checks and Activity Logging.
"""

import sys
import os
import uuid
import json
import datetime
from typing import Optional, List, Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastmcp import FastMCP
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func
from app.database import SessionLocal
from app import models

# Initialize FastMCP Server
mcp = FastMCP(
    "ERP_AI_Server",
    instructions="Comprehensive and secure Model Context Protocol (MCP) Server for Knit ERP. Exposes inventory, sales/POS, HR/payroll, cutting production, CRM, and analytics to AI models with RBAC authorization."
)

def get_db_session() -> Session:
    """Helper to acquire a database session."""
    return SessionLocal()


# =====================================================================
# SECURITY & ACTIVITY LOGGING HELPERS
# =====================================================================

PERMISSION_RESOURCE_MAP = {
    # Workers / Employees
    "create_worker": ("hr.sotrudniki", "create"),
    "update_worker": ("hr.sotrudniki", "update"),
    "delete_worker": ("hr.sotrudniki", "delete"),
    "list_workers": ("hr.sotrudniki", "view"),
    "get_worker": ("hr.sotrudniki", "view"),

    # Products & Stock
    "create_product": ("products.spisok_tovarov", "create"),
    "update_product": ("products.spisok_tovarov", "update"),
    "delete_product": ("products.spisok_tovarov", "delete"),
    "add_product_stock": ("products.spisok_tovarov", "create"),
    "list_products": ("products.spisok_tovarov", "view"),
    "get_product": ("products.spisok_tovarov", "view"),

    # Departments & Positions
    "create_department": ("hr.otdel", "create"),
    "list_departments": ("hr.otdel", "view"),
    "create_position": ("hr.dolzhnosti", "create"),
    "list_positions": ("hr.dolzhnosti", "view"),

    # Timesheets & Output & Adjustments
    "create_timesheet": ("hr.tabel", "create"),
    "list_timesheets": ("hr.tabel", "view"),
    "create_staff_output": ("hr.vyrabotka", "create"),
    "list_staff_outputs": ("hr.vyrabotka", "view"),
    "create_staff_adjustment": ("hr.korrektirovki", "create"),
    "list_staff_adjustments": ("hr.korrektirovki", "view"),

    # Salaries & Payroll
    "create_salary": ("hr.vedomost", "create"),
    "list_salaries": ("hr.vedomost", "view"),
    "bulk_salary_payout": ("hr.vedomost", "create"),

    # Sales & POS & Debtors
    "create_sale": ("sales.istoriya_prodazh", "create"),
    "list_sales": ("sales.istoriya_prodazh", "view"),
    "get_sale_receipt": ("sales.istoriya_prodazh", "view"),
    "list_debtors": ("sales.istoriya_prodazh", "view"),
    "record_debt_payment": ("sales.istoriya_prodazh", "create"),

    # Cutting Orders & Production
    "create_cutting_order": ("cutting.raskroi", "create"),
    "list_cutting_orders": ("cutting.raskroi", "view"),
    "get_cutting_order": ("cutting.raskroi", "view"),
    "start_cutting_production": ("cutting.raskroi", "update"),
    "update_cutting_task_status": ("cutting.raskroi", "update"),
    "create_cutting_execution": ("cutting.raskroi", "create"),

    # QR Codes
    "generate_qr_code": ("qr_codes.print", "create"),
    "list_qr_codes": ("qr_codes.print", "view"),

    # Users & Roles
    "list_users": ("staff.users", "view"),
    "create_role": ("staff.roles", "create"),
    "list_roles": ("staff.roles", "view"),
}

def verify_permission(db: Session, username: Optional[str], action: str) -> bool:
    """Check if the requesting user is authorized to perform action."""
    if not username or username in ["admin", "system", "Super Administrator"]:
        return True
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return False
    
    if user.role == "admin" or str(user.roleId) == "1" or "*.*.*" in (user.permissions or []):
        return True

    perm_spec = PERMISSION_RESOURCE_MAP.get(action)
    if not perm_spec:
        return True

    res, act = perm_spec
    user_perms = set(user.permissions or [])
    if user.roleId:
        role = db.query(models.Role).filter(models.Role.id == str(user.roleId)).first()
        if role and role.permissions:
            user_perms.update(role.permissions)

    req_exact = f"{res}:{act}"
    req_wildcard = f"{res}:*"
    return (
        "*.*.*" in user_perms
        or "*:*" in user_perms
        or req_exact in user_perms
        or req_wildcard in user_perms
    )

def log_activity(db: Session, actor: str, action: str, entity: str, entity_id: str, entity_name: str):
    """Record an audit trail entry in activity_logs."""
    try:
        log = models.ActivityLog(
            actor=actor or "mcp_agent",
            action=action,
            entity=entity,
            entity_id=str(entity_id) if entity_id else None,
            entity_name=str(entity_name) if entity_name else None
        )
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[MCP Log Warning] {e}")


# =====================================================================
# 1. PRODUCTS, INVENTORY & CLASSIFIER TOOLS
# =====================================================================

@mcp.tool(
    name="list_products",
    description="Query product catalog and inventory with optional keyword, category, or pagination filters."
)
def list_products(query: str = "", category: str = "", limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
    """List products with stock quantities, prices, categories, and barcodes."""
    db = get_db_session()
    try:
        q = db.query(models.Product)
        if query:
            search = f"%{query}%"
            q = q.filter(
                or_(
                    models.Product.productName.ilike(search),
                    models.Product.SKU.ilike(search),
                    models.Product.shtrix_code.ilike(search),
                    models.Product.brand_name.ilike(search)
                )
            )
        if category:
            q = q.filter(models.Product.category == category)
        
        products = q.offset(skip).limit(min(limit, 100)).all()
        return [
            {
                "id": p.id,
                "name": p.productName,
                "sku": p.SKU,
                "category": p.category,
                "price": p.price,
                "cost": p.cost,
                "quantity_in_stock": p.quantityInStock,
                "unit": p.unit or "dona",
                "barcode": p.shtrix_code or "",
                "status": "in_stock" if p.quantityInStock > 0 else "out_of_stock",
                "brand": p.brand_name or "",
                "created_at": p.createTime
            }
            for p in products
        ]
    finally:
        db.close()


@mcp.tool(
    name="get_product",
    description="Retrieve detailed product record by ID, SKU code, or Barcode."
)
def get_product(identifier: str) -> Dict[str, Any]:
    """Get single product details."""
    db = get_db_session()
    try:
        p = db.query(models.Product).filter(
            or_(
                models.Product.id == identifier,
                models.Product.SKU == identifier,
                models.Product.shtrix_code == identifier
            )
        ).first()
        if not p:
            return {"error": f"Product '{identifier}' not found."}
        
        packagings = [
            {
                "id": pkg.id,
                "unit_name": pkg.unit_name,
                "conversion_factor": pkg.conversion_factor,
                "price": pkg.price,
                "barcode": pkg.shtrix_code or ""
            }
            for pkg in p.packagings
        ]

        return {
            "id": p.id,
            "name": p.productName,
            "sku": p.SKU,
            "category": p.category,
            "price": p.price,
            "cost": p.cost,
            "quantity_in_stock": p.quantityInStock,
            "unit": p.unit or "dona",
            "barcode": p.shtrix_code or "",
            "mxik_code": p.mxik_code or "",
            "brand": p.brand_name or "",
            "remark": p.remark or "",
            "packagings": packagings,
            "created_at": p.createTime
        }
    finally:
        db.close()


@mcp.tool(
    name="create_product",
    description="Create a new product item in ERP inventory. Secure with RBAC."
)
def create_product(
    name: str,
    sku: str = "",
    category: str = "Umumiy",
    price: float = 0.0,
    cost: float = 0.0,
    quantity: float = 0.0,
    unit: str = "dona",
    barcode: str = "",
    brand: str = "",
    remark: str = "",
    auth_user: str = "admin"
) -> Dict[str, Any]:
    """Add a new product to inventory."""
    db = get_db_session()
    try:
        if not verify_permission(db, auth_user, "create_product"):
            return {"error": "Ruxsat etilmagan: Mahsulot yaratish huquqi yo'q."}

        product_id = str(uuid.uuid4())[:8]
        if not sku:
            sku = f"SKU-{datetime.datetime.now().strftime('%m%d')}-{product_id[:4].upper()}"

        existing = db.query(models.Product).filter(models.Product.SKU == sku).first()
        if existing:
            return {"error": f"Product with SKU '{sku}' already exists."}

        new_prod = models.Product(
            id=product_id,
            productName=name,
            SKU=sku,
            category=category,
            price=price,
            cost=cost,
            quantityInStock=quantity,
            status=1 if quantity > 0 else 0,
            unit=unit,
            shtrix_code=barcode,
            brand_name=brand,
            remark=remark
        )
        db.add(new_prod)
        db.commit()
        db.refresh(new_prod)

        log_activity(db, auth_user, "created", "product", new_prod.id, new_prod.productName)

        return {
            "success": True,
            "message": f"Product '{name}' created successfully.",
            "product_id": new_prod.id,
            "sku": new_prod.SKU,
            "quantity": new_prod.quantityInStock
        }
    finally:
        db.close()


@mcp.tool(
    name="update_product",
    description="Update an existing product's details, pricing, or quantity."
)
def update_product(
    product_id: str,
    name: Optional[str] = None,
    price: Optional[float] = None,
    cost: Optional[float] = None,
    quantity: Optional[float] = None,
    category: Optional[str] = None,
    barcode: Optional[str] = None,
    auth_user: str = "admin"
) -> Dict[str, Any]:
    """Update product information."""
    db = get_db_session()
    try:
        if not verify_permission(db, auth_user, "update_product"):
            return {"error": "Ruxsat etilmagan: Mahsulotni yangilash huquqi yo'q."}

        p = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not p:
            return {"error": f"Product with id '{product_id}' not found."}

        if name is not None:
            p.productName = name
        if price is not None:
            p.price = price
        if cost is not None:
            p.cost = cost
        if quantity is not None:
            p.quantityInStock = quantity
            p.status = 1 if quantity > 0 else 0
        if category is not None:
            p.category = category
        if barcode is not None:
            p.shtrix_code = barcode

        db.commit()
        db.refresh(p)
        log_activity(db, auth_user, "updated", "product", p.id, p.productName)

        return {
            "success": True,
            "product_id": p.id,
            "name": p.productName,
            "price": p.price,
            "quantity": p.quantityInStock
        }
    finally:
        db.close()


@mcp.tool(
    name="delete_product",
    description="Delete a product from the catalog. Requires delete permission."
)
def delete_product(product_id: str, auth_user: str = "admin") -> Dict[str, Any]:
    """Delete a product."""
    db = get_db_session()
    try:
        if not verify_permission(db, auth_user, "delete_product"):
            return {"error": "Ruxsat etilmagan: Mahsulotni o'chirish huquqi yo'q."}

        p = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not p:
            return {"error": f"Product '{product_id}' not found."}

        name = p.productName
        db.delete(p)
        db.commit()
        log_activity(db, auth_user, "deleted", "product", product_id, name)

        return {"success": True, "message": f"Product '{name}' ({product_id}) successfully deleted."}
    finally:
        db.close()


@mcp.tool(
    name="add_product_stock",
    description=(
        "Smart product stock intake: First searches local products by name/barcode/SKU. "
        "If found, increments stock quantity and updates optional price/cost. "
        "If NOT found, searches national 411K+ classifier database for official MXIK code, brand & unit, "
        "and auto-creates the product in warehouse with the requested initial stock. "
        "Required: name. Optional: quantity (default 1.0), price, cost, brand_name, expiration_date, barcode, unit."
    )
)
def add_product_stock(
    name: str,
    quantity: float = 1.0,
    price: Optional[float] = None,
    cost: Optional[float] = None,
    brand_name: Optional[str] = None,
    category: Optional[str] = None,
    barcode: Optional[str] = None,
    unit: Optional[str] = None,
    expiration_date: Optional[str] = None,
    comment: str = "",
    auth_user: str = "admin"
) -> Dict[str, Any]:
    """Smart restock or auto-create product from classifier."""
    db = get_db_session()
    try:
        if not verify_permission(db, auth_user, "add_product_stock"):
            return {"error": "Ruxsat etilmagan: Zaxira kiritish huquqi yo'q."}

        clean_name = name.strip()
        search_pattern = f"%{clean_name}%"

        # 1. Search existing product in local inventory
        p = db.query(models.Product).filter(
            or_(
                models.Product.productName.ilike(search_pattern),
                models.Product.SKU == clean_name,
                models.Product.shtrix_code == clean_name,
                models.Product.id == clean_name
            )
        ).first()

        if p:
            old_qty = p.quantityInStock or 0.0
            p.quantityInStock = max(0.0, old_qty + quantity)
            p.status = 1 if p.quantityInStock > 0 else 0
            if price is not None and price > 0:
                p.price = price
            if cost is not None and cost > 0:
                p.cost = cost
            if expiration_date:
                p.expiration_date = expiration_date
            if brand_name and not p.brand_name:
                p.brand_name = brand_name
            if barcode and not p.shtrix_code:
                p.shtrix_code = barcode

            db.commit()
            db.refresh(p)
            log_activity(db, auth_user, "updated", "product_stock", p.id, f"{p.productName} (+{quantity})")

            return {
                "success": True,
                "action_type": "existing_stock_updated",
                "message": f"Ombordagi '{p.productName}' mahsulotiga +{quantity} dona qo'shildi (Eski: {old_qty}, Yangi: {p.quantityInStock}).",
                "product_id": p.id,
                "name": p.productName,
                "sku": p.SKU,
                "previous_quantity": old_qty,
                "added_quantity": quantity,
                "current_quantity": p.quantityInStock,
                "price": p.price,
                "cost": p.cost,
                "brand": p.brand_name or "",
                "expiration_date": p.expiration_date or ""
            }

        # 2. Not found in local inventory -> Search 411K+ National Classifier database
        classifier_match = db.query(models.ClassifierItem).filter(
            or_(
                models.ClassifierItem.mxik_name.ilike(search_pattern),
                models.ClassifierItem.brand_name.ilike(search_pattern),
                models.ClassifierItem.shtrix_code == clean_name,
                models.ClassifierItem.mxik_code == clean_name
            )
        ).first()

        # Fallback to first brand word (e.g. "Coca Cola 1.5L" -> "Coca")
        if not classifier_match:
            first_term = clean_name.split()[0]
            if len(first_term) >= 3:
                classifier_match = db.query(models.ClassifierItem).filter(
                    or_(
                        models.ClassifierItem.brand_name.ilike(f"%{first_term}%"),
                        models.ClassifierItem.mxik_name.ilike(f"%{first_term}%")
                    )
                ).first()

        product_id = str(uuid.uuid4())[:8]
        if classifier_match:
            final_brand = brand_name or classifier_match.brand_name or clean_name.split()[0].upper()
            final_unit = unit or classifier_match.unit or "dona"
            final_category = category or classifier_match.group_name or classifier_match.class_name or "Ichimliklar"
            final_barcode = barcode or classifier_match.shtrix_code or ""
            final_mxik = classifier_match.mxik_code or ""
            final_sku = f"SKU-{final_barcode}" if final_barcode else (f"SKU-{final_mxik}" if final_mxik else f"SKU-{datetime.datetime.now().strftime('%m%d')}-{product_id[:4].upper()}")
            classifier_id = classifier_match.id

            new_prod = models.Product(
                id=product_id,
                productName=clean_name,
                SKU=final_sku,
                category=final_category,
                price=price or 0.0,
                cost=cost or 0.0,
                quantityInStock=quantity,
                status=1 if quantity > 0 else 0,
                unit=final_unit,
                shtrix_code=final_barcode,
                mxik_code=final_mxik,
                brand_name=final_brand,
                classifier_id=classifier_id,
                expiration_date=expiration_date,
                remark=comment or "Avtomatik milliy klassifikatordan yaratildi"
            )
            db.add(new_prod)
            db.commit()
            db.refresh(new_prod)

            log_activity(db, auth_user, "created", "product", new_prod.id, f"{new_prod.productName} (via Classifier MXIK: {final_mxik})")

            return {
                "success": True,
                "action_type": "created_from_classifier",
                "message": f"'{clean_name}' omborda yo'q edi. Milliy klassifikatordan topildi (MXIK: {final_mxik}, Brend: {final_brand}) va omborga +{quantity} dona bilan yangi kiritildi.",
                "product_id": new_prod.id,
                "name": new_prod.productName,
                "sku": new_prod.SKU,
                "quantity": new_prod.quantityInStock,
                "price": new_prod.price,
                "cost": new_prod.cost,
                "mxik_code": new_prod.mxik_code,
                "brand": new_prod.brand_name,
                "unit": new_prod.unit
            }

        # 3. Not found in classifier -> Create standard custom product
        fallback_sku = f"SKU-{datetime.datetime.now().strftime('%m%d')}-{product_id[:4].upper()}"
        fallback_brand = brand_name or clean_name.split()[0].upper()

        new_prod = models.Product(
            id=product_id,
            productName=clean_name,
            SKU=fallback_sku,
            category=category or "Umumiy",
            price=price or 0.0,
            cost=cost or 0.0,
            quantityInStock=quantity,
            status=1 if quantity > 0 else 0,
            unit=unit or "dona",
            shtrix_code=barcode or "",
            brand_name=fallback_brand,
            expiration_date=expiration_date,
            remark=comment or "AI orqali yangi yaratildi"
        )
        db.add(new_prod)
        db.commit()
        db.refresh(new_prod)

        log_activity(db, auth_user, "created", "product", new_prod.id, new_prod.productName)

        return {
            "success": True,
            "action_type": "created_custom",
            "message": f"'{clean_name}' omborda va klassifikatorda mavjud emas edi, yangi mahsulot sifatida +{quantity} dona bilan omborga kiritildi.",
            "product_id": new_prod.id,
            "name": new_prod.productName,
            "sku": new_prod.SKU,
            "quantity": new_prod.quantityInStock,
            "price": new_prod.price,
            "cost": new_prod.cost,
            "brand": new_prod.brand_name
        }
    finally:
        db.close()


@mcp.tool(
    name="get_low_stock_products",
    description="List all products whose inventory quantity is below the given threshold."
)
def get_low_stock_products(threshold: float = 5.0) -> List[Dict[str, Any]]:
    """Get items running low in stock."""
    db = get_db_session()
    try:
        low_items = db.query(models.Product).filter(
            models.Product.quantityInStock <= threshold
        ).order_by(models.Product.quantityInStock.asc()).all()

        return [
            {
                "id": p.id,
                "name": p.productName,
                "sku": p.SKU,
                "quantity_in_stock": p.quantityInStock,
                "category": p.category,
                "price": p.price,
                "cost": p.cost
            }
            for p in low_items
        ]
    finally:
        db.close()


@mcp.tool(
    name="search_product_classifier",
    description="Search Uzbek MXIK product classifiers by keyword, brand, or mxik code."
)
def search_product_classifier(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Search national classifier database."""
    db = get_db_session()
    try:
        search = f"%{query}%"
        items = db.query(models.ClassifierItem).filter(
            or_(
                models.ClassifierItem.mxik_name.ilike(search),
                models.ClassifierItem.mxik_code.ilike(search),
                models.ClassifierItem.brand_name.ilike(search),
                models.ClassifierItem.class_name.ilike(search)
            )
        ).limit(min(limit, 50)).all()

        return [
            {
                "id": c.id,
                "mxik_code": c.mxik_code,
                "mxik_name": c.mxik_name,
                "brand_name": c.brand_name or "",
                "unit": c.unit or "",
                "class_name": c.class_name or ""
            }
            for c in items
        ]
    finally:
        db.close()


# =====================================================================
# 2. SALES, POS & DEBT MANAGEMENT TOOLS
# =====================================================================

@mcp.tool(
    name="list_sales",
    description="List recent sales transactions and receipts with optional payment method filter."
)
def list_sales(limit: int = 50, payment_method: str = "") -> List[Dict[str, Any]]:
    """Retrieve recent sales list."""
    db = get_db_session()
    try:
        q = db.query(models.Sale).order_by(desc(models.Sale.created_at))
        if payment_method:
            q = q.filter(models.Sale.payment_method == payment_method)
        sales = q.limit(min(limit, 100)).all()

        return [
            {
                "id": s.id,
                "receipt_number": s.receipt_number,
                "cashier": s.cashier_name,
                "customer": s.customer_name or "Noma'lum",
                "payment_method": s.payment_method,
                "total_amount": s.total_amount,
                "paid_amount": s.paid_amount,
                "debt_amount": s.debt_amount,
                "items_count": s.total_items,
                "created_at": s.created_at
            }
            for s in sales
        ]
    finally:
        db.close()


@mcp.tool(
    name="get_sale_receipt",
    description="Fetch full receipt details including purchased line items."
)
def get_sale_receipt(receipt_number_or_id: str) -> Dict[str, Any]:
    """Get complete sale receipt."""
    db = get_db_session()
    try:
        s = db.query(models.Sale).filter(
            or_(
                models.Sale.id == receipt_number_or_id,
                models.Sale.receipt_number == receipt_number_or_id
            )
        ).first()
        if not s:
            return {"error": f"Sale receipt '{receipt_number_or_id}' not found."}

        items = [
            {
                "id": item.id,
                "product_name": item.product_name,
                "quantity": item.quantity,
                "unit": item.unit_name or "dona",
                "price": item.price,
                "total": item.total
            }
            for item in s.items
        ]

        return {
            "id": s.id,
            "receipt_number": s.receipt_number,
            "cashier": s.cashier_name,
            "customer_name": s.customer_name,
            "customer_phone": s.customer_phone,
            "payment_method": s.payment_method,
            "total_amount": s.total_amount,
            "paid_amount": s.paid_amount,
            "debt_amount": s.debt_amount,
            "discount": s.discount,
            "created_at": s.created_at,
            "items": items
        }
    finally:
        db.close()


@mcp.tool(
    name="list_debtors",
    description="List customers who have outstanding debts (nasiya) and their unpaid balances."
)
def list_debtors(limit: int = 50) -> List[Dict[str, Any]]:
    """List debtors with pending balance."""
    db = get_db_session()
    try:
        debt_sales = db.query(models.Sale).filter(
            models.Sale.debt_amount > 0
        ).order_by(desc(models.Sale.debt_amount)).limit(min(limit, 100)).all()

        return [
            {
                "sale_id": s.id,
                "receipt_number": s.receipt_number,
                "customer_name": s.customer_name or "Noma'lum",
                "customer_phone": s.customer_phone or "",
                "total_sale": s.total_amount,
                "paid_amount": s.paid_amount,
                "debt_balance": s.debt_amount,
                "date": s.created_at
            }
            for s in debt_sales
        ]
    finally:
        db.close()


@mcp.tool(
    name="record_debt_payment",
    description="Record customer debt repayment transaction."
)
def record_debt_payment(
    customer_name: str,
    amount: float,
    payment_method: str = "naqd",
    cashier_name: str = "admin",
    customer_phone: str = "",
    remark: str = "",
    auth_user: str = "admin"
) -> Dict[str, Any]:
    """Record customer repayment of debt."""
    db = get_db_session()
    try:
        if not verify_permission(db, auth_user, "record_debt_payment"):
            return {"error": "Ruxsat etilmagan: Qarz so'ndirish huquqi yo'q."}

        payment_id = str(uuid.uuid4())[:8]
        receipt_no = f"PAY-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        payment = models.DebtPayment(
            id=payment_id,
            receipt_number=receipt_no,
            customer_name=customer_name,
            customer_phone=customer_phone,
            amount=amount,
            payment_method=payment_method,
            cashier_name=cashier_name,
            remark=remark
        )
        db.add(payment)

        # Also update debt amount on open sales if matching
        sales = db.query(models.Sale).filter(
            models.Sale.customer_name == customer_name,
            models.Sale.debt_amount > 0
        ).order_by(models.Sale.created_at.asc()).all()

        rem_amount = amount
        for s in sales:
            if rem_amount <= 0:
                break
            deduct = min(s.debt_amount, rem_amount)
            s.debt_amount -= deduct
            s.paid_amount += deduct
            rem_amount -= deduct

        db.commit()
        log_activity(db, auth_user, "created", "debt_payment", payment_id, f"{customer_name} ({amount})")

        return {
            "success": True,
            "receipt_number": receipt_no,
            "customer_name": customer_name,
            "amount_paid": amount,
            "remaining_unallocated": rem_amount
        }
    finally:
        db.close()


@mcp.tool(
    name="get_monthly_financials",
    description="Fetch monthly financial snapshots (Revenue, COGS, Net Profit, Staff Salaries)."
)
def get_monthly_financials(period_month: str = "") -> Dict[str, Any]:
    """Get financial performance report."""
    db = get_db_session()
    try:
        if not period_month:
            period_month = datetime.datetime.now().strftime("%Y-%m")

        snap = db.query(models.MonthlyFinancialSnapshot).filter(
            models.MonthlyFinancialSnapshot.period_month == period_month
        ).first()

        if snap:
            return {
                "period": snap.period_month,
                "revenue": snap.revenue,
                "cogs": snap.cogs,
                "staff_salaries": snap.staff_salaries,
                "total_expenses": snap.total_expenses,
                "net_profit": snap.net_profit,
                "profit_margin": snap.profit_margin,
                "sales_count": snap.sales_count,
                "status": snap.status
            }

        # Calculate live if snapshot not yet finalized
        sales = db.query(models.Sale).filter(models.Sale.created_at.startswith(period_month)).all()
        rev = sum(s.total_amount for s in sales)
        salaries = db.query(models.Salary).filter(models.Salary.payDate.startswith(period_month)).all()
        sal_total = sum(sal.netSalary for sal in salaries)

        return {
            "period": period_month,
            "revenue": rev,
            "staff_salaries": sal_total,
            "sales_count": len(sales),
            "status": "live_unfinalized"
        }
    finally:
        db.close()


# =====================================================================
# 3. HR, EMPLOYEES, PAYROLL, POSITIONS & ATTENDANCE
# =====================================================================

@mcp.tool(
    name="list_workers",
    description="List company employees/workers with department, position, status, and base salary."
)
def list_workers(department_id: str = "", status: int = 1) -> List[Dict[str, Any]]:
    """List workers/employees."""
    db = get_db_session()
    try:
        q = db.query(models.Worker)
        if status is not None:
            q = q.filter(models.Worker.status == status)
        if department_id:
            q = q.filter(models.Worker.departmentId == department_id)
        
        workers = q.all()
        return [
            {
                "id": w.id,
                "name": w.name,
                "employee_code": w.employee_code or "",
                "role": w.role or "",
                "department_id": w.departmentId or "",
                "phone": w.phone or "",
                "email": w.email or "",
                "base_salary": w.baseSalary,
                "hire_date": w.hireDate,
                "status": "active" if w.status == 1 else "inactive"
            }
            for w in workers
        ]
    finally:
        db.close()


@mcp.tool(
    name="get_worker",
    description="Get detailed worker record by ID or employee code."
)
def get_worker(identifier: str) -> Dict[str, Any]:
    """Get single worker details."""
    db = get_db_session()
    try:
        w = db.query(models.Worker).filter(
            or_(
                models.Worker.id == identifier,
                models.Worker.employee_code == identifier,
                models.Worker.name.ilike(f"%{identifier}%")
            )
        ).first()
        if not w:
            return {"error": f"Worker '{identifier}' not found."}

        return {
            "id": w.id,
            "name": w.name,
            "employee_code": w.employee_code or "",
            "phone": w.phone or "",
            "email": w.email or "",
            "role": w.role or "",
            "department_id": w.departmentId or "",
            "base_salary": w.baseSalary,
            "hire_date": w.hireDate,
            "status": "active" if w.status == 1 else "inactive",
            "remark": w.remark or ""
        }
    finally:
        db.close()


@mcp.tool(
    name="create_worker",
    description="Register a new employee/worker in ERP HR system. Secure with RBAC."
)
def create_worker(
    name: str,
    phone: str = "",
    role: str = "Xodim",
    department_id: str = "",
    base_salary: float = 0.0,
    employee_code: str = "",
    remark: str = "",
    auth_user: str = "admin"
) -> Dict[str, Any]:
    """Register employee."""
    db = get_db_session()
    try:
        if not verify_permission(db, auth_user, "create_worker"):
            return {"error": "Ruxsat etilmagan: Xodim yaratish huquqi yo'q."}

        worker_id = str(uuid.uuid4())[:8]
        if not employee_code:
            employee_code = f"EMP-{datetime.datetime.now().strftime('%y%m')}-{worker_id[:4].upper()}"

        new_worker = models.Worker(
            id=worker_id,
            name=name,
            account=worker_id,
            employee_code=employee_code,
            phone=phone,
            role=role,
            departmentId=department_id,
            baseSalary=base_salary,
            status=1,
            remark=remark
        )
        db.add(new_worker)
        db.commit()
        db.refresh(new_worker)

        log_activity(db, auth_user, "created", "worker", new_worker.id, new_worker.name)

        return {
            "success": True,
            "worker_id": new_worker.id,
            "name": new_worker.name,
            "employee_code": new_worker.employee_code,
            "base_salary": new_worker.baseSalary
        }
    finally:
        db.close()


@mcp.tool(
    name="update_worker",
    description="Update employee details (role, phone, department, salary, status)."
)
def update_worker(
    worker_id: str,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    role: Optional[str] = None,
    department_id: Optional[str] = None,
    base_salary: Optional[float] = None,
    status: Optional[int] = None,
    remark: Optional[str] = None,
    auth_user: str = "admin"
) -> Dict[str, Any]:
    """Update employee details."""
    db = get_db_session()
    try:
        if not verify_permission(db, auth_user, "update_worker"):
            return {"error": "Ruxsat etilmagan: Xodim ma'lumotlarini yangilash huquqi yo'q."}

        w = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
        if not w:
            return {"error": f"Worker with id '{worker_id}' not found."}

        if name is not None:
            w.name = name
        if phone is not None:
            w.phone = phone
        if role is not None:
            w.role = role
        if department_id is not None:
            w.departmentId = department_id
        if base_salary is not None:
            w.baseSalary = base_salary
        if status is not None:
            w.status = status
        if remark is not None:
            w.remark = remark

        db.commit()
        db.refresh(w)
        log_activity(db, auth_user, "updated", "worker", w.id, w.name)

        return {
            "success": True,
            "worker_id": w.id,
            "name": w.name,
            "role": w.role,
            "base_salary": w.baseSalary
        }
    finally:
        db.close()


@mcp.tool(
    name="delete_worker",
    description="Delete or suspend worker record from HR system."
)
def delete_worker(worker_id: str, auth_user: str = "admin") -> Dict[str, Any]:
    """Delete a worker."""
    db = get_db_session()
    try:
        if not verify_permission(db, auth_user, "delete_worker"):
            return {"error": "Ruxsat etilmagan: Xodimni o'chirish huquqi yo'q."}

        w = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
        if not w:
            return {"error": f"Worker '{worker_id}' not found."}

        name = w.name
        db.delete(w)
        db.commit()
        log_activity(db, auth_user, "deleted", "worker", worker_id, name)

        return {"success": True, "message": f"Worker '{name}' ({worker_id}) deleted."}
    finally:
        db.close()


@mcp.tool(
    name="list_departments",
    description="List all organization departments."
)
def list_departments() -> List[Dict[str, Any]]:
    """List departments."""
    db = get_db_session()
    try:
        depts = db.query(models.Department).all()
        return [
            {
                "id": d.id,
                "name": d.departmentName,
                "parent_id": d.parentId,
                "status": "active" if d.status == 1 else "inactive",
                "remark": d.remark or ""
            }
            for d in depts
        ]
    finally:
        db.close()


@mcp.tool(
    name="create_department",
    description="Create a new department in the company structure."
)
def create_department(name: str, parent_id: str = "", remark: str = "", auth_user: str = "admin") -> Dict[str, Any]:
    """Create department."""
    db = get_db_session()
    try:
        if not verify_permission(db, auth_user, "create_department"):
            return {"error": "Ruxsat etilmagan: Bo'lim yaratish huquqi yo'q."}

        dept_id = str(uuid.uuid4())[:8]
        new_dept = models.Department(
            id=dept_id,
            departmentName=name,
            parentId=parent_id or None,
            status=1,
            remark=remark
        )
        db.add(new_dept)
        db.commit()
        db.refresh(new_dept)

        log_activity(db, auth_user, "created", "department", new_dept.id, new_dept.departmentName)

        return {
            "success": True,
            "department_id": new_dept.id,
            "name": new_dept.departmentName
        }
    finally:
        db.close()


@mcp.tool(
    name="list_positions",
    description="List all organizational job positions."
)
def list_positions(department_id: str = "") -> List[Dict[str, Any]]:
    """List positions."""
    db = get_db_session()
    try:
        q = db.query(models.Position)
        if department_id:
            q = q.filter(models.Position.departmentId == department_id)
        pos_list = q.all()
        return [
            {
                "id": p.id,
                "name": p.positionName,
                "department_id": p.departmentId or "",
                "base_salary": p.baseSalary,
                "status": "active" if p.status == 1 else "inactive"
            }
            for p in pos_list
        ]
    finally:
        db.close()


@mcp.tool(
    name="create_position",
    description="Create a new position / job title."
)
def create_position(
    position_name: str,
    department_id: str = "",
    base_salary: float = 0.0,
    remark: str = "",
    auth_user: str = "admin"
) -> Dict[str, Any]:
    """Create position."""
    db = get_db_session()
    try:
        if not verify_permission(db, auth_user, "create_position"):
            return {"error": "Ruxsat etilmagan: Lavozim yaratish huquqi yo'q."}

        pos_id = str(uuid.uuid4())[:8]
        new_pos = models.Position(
            id=pos_id,
            positionName=position_name,
            departmentId=department_id or None,
            baseSalary=base_salary,
            status=1,
            remark=remark
        )
        db.add(new_pos)
        db.commit()
        db.refresh(new_pos)

        log_activity(db, auth_user, "created", "position", new_pos.id, new_pos.positionName)

        return {
            "success": True,
            "position_id": new_pos.id,
            "name": new_pos.positionName,
            "base_salary": new_pos.baseSalary
        }
    finally:
        db.close()


@mcp.tool(
    name="list_salaries",
    description="List salary payroll records for employees with optional month or payment status filter."
)
def list_salaries(period_month: str = "", status: str = "") -> List[Dict[str, Any]]:
    """List employee salaries and payouts."""
    db = get_db_session()
    try:
        q = db.query(models.Salary)
        if status:
            q = q.filter(models.Salary.status == status)
        if period_month:
            q = q.filter(models.Salary.payDate.startswith(period_month))
        
        salaries = q.order_by(desc(models.Salary.payDate)).limit(100).all()
        return [
            {
                "id": sal.id,
                "worker_id": sal.workerId,
                "worker_name": sal.worker.name if sal.worker else "Noma'lum",
                "base_salary": sal.baseSalary,
                "allowance": sal.allowance,
                "deduction": sal.deduction,
                "net_salary": sal.netSalary,
                "pay_date": sal.payDate,
                "status": sal.status,
                "remark": sal.remark or ""
            }
            for sal in salaries
        ]
    finally:
        db.close()


@mcp.tool(
    name="create_salary_record",
    description="Create a salary payroll entry for a worker."
)
def create_salary_record(
    worker_id: str,
    base_salary: float,
    allowance: float = 0.0,
    deduction: float = 0.0,
    pay_date: str = "",
    remark: str = "",
    auth_user: str = "admin"
) -> Dict[str, Any]:
    """Create salary payroll record."""
    db = get_db_session()
    try:
        if not verify_permission(db, auth_user, "create_salary"):
            return {"error": "Ruxsat etilmagan: Oylik vedomost yaratish huquqi yo'q."}

        w = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
        if not w:
            return {"error": f"Worker with id '{worker_id}' not found."}

        if not pay_date:
            pay_date = datetime.datetime.now().strftime("%Y-%m-%d")

        net = max(0.0, base_salary + allowance - deduction)
        sal_id = str(uuid.uuid4())[:8]

        sal = models.Salary(
            id=sal_id,
            workerId=worker_id,
            baseSalary=base_salary,
            allowance=allowance,
            deduction=deduction,
            netSalary=net,
            payDate=pay_date,
            status="pending",
            remark=remark
        )
        db.add(sal)
        db.commit()
        db.refresh(sal)

        log_activity(db, auth_user, "created", "salary", sal.id, f"{w.name} ({net})")

        return {
            "success": True,
            "salary_id": sal.id,
            "worker_name": w.name,
            "net_salary": sal.netSalary,
            "pay_date": sal.payDate
        }
    finally:
        db.close()


@mcp.tool(
    name="record_staff_adjustment",
    description="Record a bonus, fine, or salary advance for a worker."
)
def record_staff_adjustment(
    worker_id: str,
    document_type: str,
    amount: float,
    period_month: str = "",
    description: str = "",
    auth_user: str = "admin"
) -> Dict[str, Any]:
    """Record bonus/fine/advance adjustment."""
    db = get_db_session()
    try:
        if not verify_permission(db, auth_user, "create_staff_adjustment"):
            return {"error": "Ruxsat etilmagan: Korrektirovka kiritish huquqi yo'q."}

        w = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
        if not w:
            return {"error": f"Worker with id '{worker_id}' not found."}

        if not period_month:
            period_month = datetime.datetime.now().strftime("%Y-%m")

        adj_id = str(uuid.uuid4())[:8]
        adj = models.StaffAdjustment(
            id=adj_id,
            workerId=worker_id,
            document_type=document_type,
            amount=amount,
            period_month=period_month,
            description=description
        )
        db.add(adj)
        db.commit()

        log_activity(db, auth_user, "created", "staff_adjustment", adj.id, f"{w.name} ({document_type}: {amount})")

        return {
            "success": True,
            "adjustment_id": adj.id,
            "worker_name": w.name,
            "type": document_type,
            "amount": amount,
            "period": period_month
        }
    finally:
        db.close()


@mcp.tool(
    name="record_staff_output",
    description="Record piecework production output (vyrabotka) for a worker or contractor."
)
def record_staff_output(
    name: str,
    amount: float,
    worker_id: str = "",
    worker_name: str = "",
    period_month: str = "",
    comment: str = "",
    auth_user: str = "admin"
) -> Dict[str, Any]:
    """Record piecework output."""
    db = get_db_session()
    try:
        if not verify_permission(db, auth_user, "create_staff_output"):
            return {"error": "Ruxsat etilmagan: Vyrabotka kiritish huquqi yo'q."}

        if not period_month:
            period_month = datetime.datetime.now().strftime("%Y-%m-%d")

        output_id = str(uuid.uuid4())[:8]
        out_rec = models.StaffOutput(
            id=output_id,
            workerId=worker_id or None,
            workerName=worker_name or None,
            name=name,
            amount=amount,
            period_month=period_month,
            comment=comment
        )
        db.add(out_rec)
        db.commit()

        log_activity(db, auth_user, "created", "staff_output", out_rec.id, f"{name} ({amount})")

        return {
            "success": True,
            "output_id": out_rec.id,
            "operation": name,
            "amount": amount,
            "worker": worker_name or worker_id
        }
    finally:
        db.close()


# =====================================================================
# 4. PRODUCTION & CUTTING ORDERS (RASKROY) TOOLS
# =====================================================================

@mcp.tool(
    name="list_cutting_orders",
    description="List production cutting orders (raskroy) with project, status, and total quantity."
)
def list_cutting_orders(status: str = "", limit: int = 50) -> List[Dict[str, Any]]:
    """List cutting orders."""
    db = get_db_session()
    try:
        q = db.query(models.CuttingOrder)
        if status:
            q = q.filter(models.CuttingOrder.status == status)
        orders = q.order_by(desc(models.CuttingOrder.createTime)).limit(min(limit, 100)).all()

        return [
            {
                "id": o.id,
                "order_number": o.order_number,
                "project": o.project or "",
                "order_name": o.order_name or "",
                "status": o.status,
                "total_quantity": o.total_quantity,
                "items_count": len(o.items),
                "created_at": o.createTime
            }
            for o in orders
        ]
    finally:
        db.close()


@mcp.tool(
    name="get_cutting_order",
    description="Get complete cutting order details including order items and process breakdown."
)
def get_cutting_order(order_id_or_number: str) -> Dict[str, Any]:
    """Get single cutting order."""
    db = get_db_session()
    try:
        o = db.query(models.CuttingOrder).filter(
            or_(
                models.CuttingOrder.id == order_id_or_number,
                models.CuttingOrder.order_number == order_id_or_number
            )
        ).first()
        if not o:
            return {"error": f"Cutting order '{order_id_or_number}' not found."}

        items = [
            {
                "id": item.id,
                "product_id": item.productId,
                "product_name": item.product.productName if item.product else "",
                "quantity": item.quantity,
                "color": item.color or "",
                "code": item.code or ""
            }
            for item in o.items
        ]

        return {
            "id": o.id,
            "order_number": o.order_number,
            "project": o.project or "",
            "order_name": o.order_name or "",
            "status": o.status,
            "total_quantity": o.total_quantity,
            "items": items,
            "created_at": o.createTime
        }
    finally:
        db.close()


@mcp.tool(
    name="create_cutting_order",
    description="Create a new cutting production order (raskroy buyurtmasi)."
)
def create_cutting_order(
    order_number: str,
    project: str = "",
    order_name: str = "",
    total_quantity: int = 0,
    auth_user: str = "admin"
) -> Dict[str, Any]:
    """Create cutting order."""
    db = get_db_session()
    try:
        if not verify_permission(db, auth_user, "create_cutting_order"):
            return {"error": "Ruxsat etilmagan: Raskroy buyurtmasi yaratish huquqi yo'q."}

        order_id = str(uuid.uuid4())[:8]
        order = models.CuttingOrder(
            id=order_id,
            order_number=order_number,
            project=project,
            order_name=order_name,
            total_quantity=total_quantity,
            status="created"
        )
        db.add(order)
        db.commit()
        db.refresh(order)

        log_activity(db, auth_user, "created", "cutting_order", order.id, order.order_number)

        return {
            "success": True,
            "order_id": order.id,
            "order_number": order.order_number,
            "status": order.status
        }
    finally:
        db.close()


@mcp.tool(
    name="start_cutting_production",
    description="Move a cutting order into active production ('in_production' status)."
)
def start_cutting_production(order_id: str, auth_user: str = "admin") -> Dict[str, Any]:
    """Start production on cutting order."""
    db = get_db_session()
    try:
        if not verify_permission(db, auth_user, "start_cutting_production"):
            return {"error": "Ruxsat etilmagan: Ishlab chiqarishni boshlash huquqi yo'q."}

        order = db.query(models.CuttingOrder).filter(models.CuttingOrder.id == order_id).first()
        if not order:
            return {"error": f"Cutting order '{order_id}' not found."}

        order.status = "in_production"
        db.commit()
        log_activity(db, auth_user, "updated", "cutting_order", order.id, f"{order.order_number} -> in_production")

        return {
            "success": True,
            "order_id": order.id,
            "order_number": order.order_number,
            "status": "in_production"
        }
    finally:
        db.close()


# =====================================================================
# 5. CRM (GROUPS, STUDENTS, LESSONS) TOOLS
# =====================================================================

@mcp.tool(
    name="list_crm_groups",
    description="List all student / training groups in CRM module."
)
def list_crm_groups() -> List[Dict[str, Any]]:
    """List CRM groups."""
    db = get_db_session()
    try:
        groups = db.query(models.CRMGroup).all()
        return [
            {
                "id": g.id,
                "name": g.groupName,
                "teacher": g.teacherName or "",
                "start_time": g.startTime or "",
                "end_time": g.endTime or "",
                "status": "active" if g.status == 1 else "inactive"
            }
            for g in groups
        ]
    finally:
        db.close()


@mcp.tool(
    name="list_crm_students",
    description="List students registered in CRM or filter by group."
)
def list_crm_students(group_id: str = "") -> List[Dict[str, Any]]:
    """List CRM students."""
    db = get_db_session()
    try:
        q = db.query(models.CRMStudent)
        if group_id:
            q = q.filter(models.CRMStudent.groupId == group_id)
        students = q.all()
        return [
            {
                "id": s.id,
                "name": s.studentName,
                "group_id": s.groupId or "",
                "group_name": s.group.groupName if s.group else ""
            }
            for s in students
        ]
    finally:
        db.close()


# =====================================================================
# 6. QR CODES, BRANCHES & DEVICES
# =====================================================================

@mcp.tool(
    name="list_qr_codes",
    description="List generated production QR codes for task tracking."
)
def list_qr_codes(task_id: str = "", limit: int = 50) -> List[Dict[str, Any]]:
    """List QR codes."""
    db = get_db_session()
    try:
        q = db.query(models.QrCode)
        if task_id:
            q = q.filter(models.QrCode.taskId == task_id)
        codes = q.limit(min(limit, 100)).all()
        return [
            {
                "id": c.id,
                "code": c.code,
                "task_id": c.taskId,
                "quantity": c.quantity,
                "status": c.status,
                "worker_id": c.workerId or ""
            }
            for c in codes
        ]
    finally:
        db.close()


@mcp.tool(
    name="list_branches",
    description="List all company branches / store locations."
)
def list_branches() -> List[Dict[str, Any]]:
    """List branches."""
    db = get_db_session()
    try:
        branches = db.query(models.Branch).all()
        return [
            {
                "id": b.id,
                "name": b.name,
                "code": b.code,
                "address": b.address or "",
                "phone": b.phone or "",
                "is_active": bool(b.is_active)
            }
            for b in branches
        ]
    finally:
        db.close()


@mcp.tool(
    name="list_users",
    description="List system operator user accounts with their assigned roles."
)
def list_users(auth_user: str = "admin") -> List[Dict[str, Any]]:
    """List users."""
    db = get_db_session()
    try:
        if not verify_permission(db, auth_user, "list_users"):
            return [{"error": "Ruxsat etilmagan: Foydalanuvchilarni ko'rish huquqi yo'q."}]

        users = db.query(models.User).all()
        return [
            {
                "id": u.id,
                "username": u.username,
                "full_name": u.full_name or "",
                "role": u.role or "",
                "role_id": u.roleId or "",
                "email": u.email or "",
                "phone": u.phone or ""
            }
            for u in users
        ]
    finally:
        db.close()


# =====================================================================
# 7. MCP RESOURCES & CONTEXT PROVIDERS
# =====================================================================

@mcp.resource("erp://summary/dashboard")
def get_dashboard_summary() -> str:
    """Real-time ERP dashboard overview for AI context."""
    db = get_db_session()
    try:
        total_products = db.query(models.Product).count()
        low_stock = db.query(models.Product).filter(models.Product.quantityInStock <= 5).count()
        total_workers = db.query(models.Worker).filter(models.Worker.status == 1).count()
        total_sales_count = db.query(models.Sale).count()
        total_revenue = db.query(func.sum(models.Sale.total_amount)).scalar() or 0.0
        total_debt = db.query(func.sum(models.Sale.debt_amount)).scalar() or 0.0
        open_cutting = db.query(models.CuttingOrder).filter(
            models.CuttingOrder.status.in_(["created", "in_production", "in_progress"])
        ).count()

        data = {
            "system": "Antigravity ERP System",
            "snapshot_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "inventory": {
                "total_unique_products": total_products,
                "low_stock_alerts": low_stock
            },
            "sales_and_finance": {
                "total_sales_transactions": total_sales_count,
                "total_gross_revenue": total_revenue,
                "total_outstanding_debt": total_debt
            },
            "human_resources": {
                "active_employees": total_workers
            },
            "production": {
                "active_cutting_orders": open_cutting
            }
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
    finally:
        db.close()


@mcp.resource("erp://inventory/status")
def get_inventory_status() -> str:
    """Current inventory status including top stocked and low stocked items."""
    db = get_db_session()
    try:
        low_stock = db.query(models.Product).filter(models.Product.quantityInStock <= 5).all()
        items = [
            {
                "sku": p.SKU,
                "name": p.productName,
                "quantity": p.quantityInStock,
                "price": p.price
            }
            for p in low_stock[:25]
        ]
        return json.dumps({"low_stock_items": items}, indent=2, ensure_ascii=False)
    finally:
        db.close()


# =====================================================================
# 8. MCP PROMPT TEMPLATES
# =====================================================================

@mcp.prompt(name="daily_summary_report")
def prompt_daily_summary() -> str:
    """Executive daily briefing on sales, warehouse inventory, and production status."""
    return (
        "Siz ERP tizimining boshqaruv tahlilchisi sifatida harakat qilasiz. "
        "`erp://summary/dashboard` resursini o'qing va bugungi kun bo'yicha: "
        "1. Sotuvlar va tushumlar, "
        "2. Nasiya (qarzdorlik) holati, "
        "3. Kam qolgan tovarlar bo'yicha ogohlantirishlar, "
        "4. Ishlab chiqarish va xodimlar bo'yicha qisqa xulosa tayyorlab bering."
    )


@mcp.prompt(name="stock_reorder_advisor")
def prompt_stock_reorder() -> str:
    """Inventory advisor to identify out-of-stock and low-stock items for replenishment."""
    return (
        "`get_low_stock_products` vositasidan foydalanib, zaxirasi 5 tadan kam qolgan tovarlar "
        "ro'yxatini oling va omborni to'ldirish bo'yicha xaridlarni rejalashtirish jadvalini taqdim eting."
    )


# =====================================================================
# SERVER RUNNER (CLI & STDIO)
# =====================================================================

if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    if transport == "sse":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8001
        print(f"Starting ERP MCP Server over SSE on port {port}...")
        mcp.run(transport="sse", port=port)
    else:
        # Default to stdio for Claude Desktop / Antigravity / Cursor
        mcp.run(transport="stdio")
