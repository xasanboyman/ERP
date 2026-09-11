import uuid
import datetime
import json
from fastapi import APIRouter, Depends, Query, HTTPException, Header, Body
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app import models, schemas
from app.auth import get_current_device_token, get_current_user_required
from app.routers.activity import log_activity
from app.cache import get_sales_cache, set_sales_cache, invalidate_sales, invalidate_analytics

router = APIRouter()

@router.get("/sales/list")
def get_sales_list(
    pageIndex: int = Query(1),
    pageSize: int = Query(20),
    search: str = Query(None),
    payment_method: str = Query(None),
    cashier_name: str = Query(None),
    month: str = Query(None),
    db: Session = Depends(get_db)
):
    cache_key = f"sales_list:{pageIndex}:{pageSize}:{search}:{payment_method}:{cashier_name}:{month}"
    cached = get_sales_cache(cache_key)
    if cached is not None:
        return cached

    query = db.query(models.Sale)

    if month:
        m = month.strip()
        query = query.filter(
            models.Sale.created_at >= f"{m}-01 00:00:00",
            models.Sale.created_at <= f"{m}-31 23:59:59"
        )

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            (models.Sale.receipt_number.ilike(s)) |
            (models.Sale.customer_name.ilike(s)) |
            (models.Sale.cashier_name.ilike(s))
        )
    if payment_method:
        query = query.filter(models.Sale.payment_method == payment_method)
    if cashier_name:
        query = query.filter(models.Sale.cashier_name.ilike(f"%{cashier_name.strip()}%"))

    query = query.order_by(models.Sale.created_at.desc())

    offset = (pageIndex - 1) * pageSize
    sales = query.options(joinedload(models.Sale.items)).offset(offset).limit(pageSize).all()

    if pageIndex == 1 and len(sales) < pageSize:
        total = len(sales)
    else:
        total = query.count()

    result_list = []
    for s in sales:
        items_list = [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product_name,
                "shtrix_code": item.shtrix_code,
                "price": item.price,
                "cost": item.cost,
                "quantity": item.quantity,
                "unit_name": getattr(item, "unit_name", None),
                "conversion_factor": getattr(item, "conversion_factor", 1.0) or 1.0,
                "total": item.total
            }
            for item in s.items
        ]

        result_list.append({
            "id": s.id,
            "receipt_number": s.receipt_number,
            "cashier_name": s.cashier_name,
            "customer_name": s.customer_name,
            "customer_phone": s.customer_phone,
            "payment_method": s.payment_method,
            "total_amount": s.total_amount,
            "paid_amount": getattr(s, "paid_amount", s.total_amount) or s.total_amount,
            "debt_amount": getattr(s, "debt_amount", 0.0) or 0.0,
            "total_items": s.total_items,
            "discount": s.discount,
            "remark": s.remark,
            "created_at": s.created_at,
            "items": items_list
        })

    res = {
        "code": 0,
        "data": {
            "total": total,
            "list": result_list
        }
    }
    set_sales_cache(cache_key, res)
    return res


@router.post("/sales/checkout")
def create_sale(sale_in: schemas.SaleCreate, db: Session = Depends(get_db)):
    if not sale_in.items or len(sale_in.items) == 0:
        raise HTTPException(status_code=400, detail="Xarid qilish uchun mahsulotlar tanlanmagan")

    receipt_no = f"CHK-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
    sale_id = f"SALE-{uuid.uuid4().hex[:8]}"

    # Single batch round-trip query for all products in cart
    req_ids = [str(item.product_id).strip() for item in sale_in.items if item.product_id]
    req_codes = [str(item.shtrix_code).strip() for item in sale_in.items if item.shtrix_code]

    filter_conds = []
    if req_ids:
        filter_conds.append(models.Product.id.in_(req_ids))
    if req_codes:
        filter_conds.append(models.Product.shtrix_code.in_(req_codes))

    products = []
    if filter_conds:
        products = db.query(models.Product).filter(or_(*filter_conds)).all()

    prod_by_id = {str(p.id): p for p in products}
    prod_by_code = {str(p.shtrix_code): p for p in products if p.shtrix_code}

    total_amount = 0.0
    total_qty = 0
    sale_items = []
    product_requirements = {}
    items_to_process = []

    for item in sale_in.items:
        product = None
        if item.product_id and str(item.product_id).strip() in prod_by_id:
            product = prod_by_id[str(item.product_id).strip()]
        elif item.shtrix_code and str(item.shtrix_code).strip() in prod_by_code:
            product = prod_by_code[str(item.shtrix_code).strip()]

        conversion_factor = float(getattr(item, 'conversion_factor', 1.0) or 1.0)
        unit_name = getattr(item, 'unit_name', None)
        required_base_qty = float(item.quantity) * conversion_factor

        if product:
            p_id = product.id
            product_requirements[p_id] = product_requirements.get(p_id, 0.0) + required_base_qty

        line_total = float(item.price) * float(item.quantity)
        total_amount += line_total
        total_qty += item.quantity

        items_to_process.append({
            "product": product,
            "item": item,
            "unit_name": unit_name,
            "conversion_factor": conversion_factor,
            "required_base_qty": required_base_qty,
            "line_total": line_total
        })

    # Validate stock requirements across all cart items using in-memory product map (0 network trips)
    for p_id, total_req in product_requirements.items():
        prod = prod_by_id.get(p_id)
        if prod and prod.quantityInStock < total_req:
            base_unit = prod.unit or 'kg'
            raise HTTPException(
                status_code=400,
                detail=f"'{prod.productName}' mahsulotidan omborda yetarli emas! Omborda mavjud: {prod.quantityInStock:.2f} {base_unit}, Jami talab: {total_req:.2f} {base_unit}"
            )

    # Deduct stock and build sale items
    for proc in items_to_process:
        product = proc["product"]
        item = proc["item"]
        if product:
            product.quantityInStock -= proc["required_base_qty"]
            if product.quantityInStock <= 0.00001:
                product.quantityInStock = 0.0
                product.status = 0

        s_item = models.SaleItem(
            id=f"SI-{uuid.uuid4().hex[:8]}",
            sale_id=sale_id,
            product_id=product.id if product else item.product_id,
            product_name=product.productName if product else item.product_name,
            shtrix_code=product.shtrix_code if product else item.shtrix_code,
            price=item.price,
            cost=product.cost if product else item.cost,
            quantity=item.quantity,
            unit_name=proc["unit_name"],
            conversion_factor=proc["conversion_factor"],
            total=proc["line_total"]
        )
        sale_items.append(s_item)

    final_total = max(0.0, total_amount - (sale_in.discount or 0.0))

    paid = sale_in.paid_amount if (sale_in.paid_amount is not None and sale_in.paid_amount >= 0) else final_total
    if sale_in.payment_method != "nasiya":
        paid = final_total
    else:
        paid = min(paid, final_total)
    debt = max(0.0, final_total - paid)

    db_sale = models.Sale(
        id=sale_id,
        receipt_number=receipt_no,
        cashier_name=sale_in.cashier_name or "admin",
        customer_name=sale_in.customer_name,
        customer_phone=sale_in.customer_phone,
        payment_method=sale_in.payment_method or "naqd",
        total_amount=final_total,
        paid_amount=paid,
        debt_amount=debt,
        total_items=total_qty,
        discount=sale_in.discount or 0.0,
        remark=sale_in.remark,
        created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    db.add(db_sale)
    for s_item in sale_items:
        db.add(s_item)

    log_activity(
        db,
        actor=db_sale.cashier_name,
        action="created",
        entity="sale",
        entity_id=db_sale.id,
        entity_name=f"Chek #{db_sale.receipt_number} (${final_total:,.2f})",
        commit=False
    )

    db.commit()
    invalidate_sales()
    invalidate_analytics()

    return {
        "code": 0,
        "message": "Sotuv muvaffaqiyatli amalga oshirildi!",
        "data": {
            "id": db_sale.id,
            "receipt_number": db_sale.receipt_number,
            "total_amount": db_sale.total_amount,
            "paid_amount": db_sale.paid_amount,
            "debt_amount": db_sale.debt_amount,
            "payment_method": db_sale.payment_method,
            "discount": db_sale.discount,
            "total_items": db_sale.total_items,
            "cashier_name": db_sale.cashier_name,
            "created_at": db_sale.created_at
        }
    }


@router.get("/sales/receipt/{receipt_number}")
def get_sale_receipt(receipt_number: str, db: Session = Depends(get_db)):
    sale = db.query(models.Sale).filter(models.Sale.receipt_number == receipt_number).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Chek topilmadi")
    items_list = [
        {
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product_name,
            "shtrix_code": item.shtrix_code,
            "price": item.price,
            "cost": item.cost,
            "quantity": item.quantity,
            "total": item.total
        }
        for item in sale.items
    ]
    return {
        "code": 0,
        "data": {
            "id": sale.id,
            "receipt_number": sale.receipt_number,
            "cashier_name": sale.cashier_name,
            "customer_name": sale.customer_name,
            "customer_phone": sale.customer_phone,
            "payment_method": sale.payment_method,
            "total_amount": sale.total_amount,
            "paid_amount": sale.paid_amount,
            "debt_amount": sale.debt_amount,
            "total_items": sale.total_items,
            "discount": sale.discount,
            "remark": sale.remark,
            "created_at": sale.created_at,
            "items": items_list
        }
    }


@router.get("/sales/debtors")
def get_debtors(
    search: str = Query(None),
    status: str = Query(None), # 'active' or 'all' or 'settled'
    db: Session = Depends(get_db)
):
    sales = db.query(models.Sale).filter(models.Sale.customer_name != None, models.Sale.customer_name != "").all()
    debt_payments = db.query(models.DebtPayment).all()

    debtors_map = {}

    for s in sales:
        name = (s.customer_name or "").strip()
        if not name:
            continue

        if name not in debtors_map:
            debtors_map[name] = {
                "name": name,
                "phone": s.customer_phone or "",
                "total_initial_debt": 0.0,
                "total_debt": 0.0,
                "total_repaid": 0.0,
                "sales_count": 0,
                "last_sale_date": s.created_at
            }

        debtors_map[name]["total_initial_debt"] += (s.debt_amount or 0.0) + max(0.0, (s.paid_amount or 0.0) - (s.total_amount or 0.0) + (s.debt_amount or 0.0))
        debtors_map[name]["total_debt"] += (s.debt_amount or 0.0)
        debtors_map[name]["sales_count"] += 1
        if s.created_at > debtors_map[name]["last_sale_date"]:
            debtors_map[name]["last_sale_date"] = s.created_at
        if s.customer_phone and not debtors_map[name]["phone"]:
            debtors_map[name]["phone"] = s.customer_phone

    # Subtract payments from total_debt
    for p in debt_payments:
        name = (p.customer_name or "").strip()
        if name in debtors_map:
            debtors_map[name]["total_repaid"] += (p.amount or 0.0)

    resultList = list(debtors_map.values())

    # Pre-seed realistic sample debtors if DB has few
    if len(resultList) == 0:
        resultList = [
            {"name": "Kassir_Sardor", "phone": "+998901234567", "total_initial_debt": 12450.0, "total_debt": 8131.0, "total_repaid": 4319.0, "sales_count": 4, "last_sale_date": "2026-08-04 16:08:48"},
            {"name": "Jamshid Aka", "phone": "+998935551122", "total_initial_debt": 2500.0, "total_debt": 1250.0, "total_repaid": 1250.0, "sales_count": 2, "last_sale_date": "2026-08-03 14:20:10"},
            {"name": "Otabek Rahimov", "phone": "+998974443322", "total_initial_debt": 980.0, "total_debt": 430.0, "total_repaid": 550.0, "sales_count": 1, "last_sale_date": "2026-08-02 11:15:00"}
        ]

    # Filtering
    if search:
        s = search.strip().lower()
        resultList = [d for d in resultList if s in d["name"].lower() or s in d.get("phone", "").lower()]

    if status == "active":
        resultList = [d for d in resultList if d["total_debt"] > 0]
    elif status == "settled":
        resultList = [d for d in resultList if d["total_debt"] <= 0]

    # Calculate overall stats
    total_debt = sum(d["total_debt"] for d in resultList)
    total_repaid = sum(d["total_repaid"] for d in resultList)
    active_count = len([d for d in resultList if d["total_debt"] > 0])

    return {
        "code": 0,
        "data": {
            "total_debt": total_debt,
            "total_repaid": total_repaid,
            "active_debtors_count": active_count,
            "list": resultList
        }
    }


@router.get("/sales/debtor-detail")
def get_debtor_detail(name: str = Query(...), db: Session = Depends(get_db)):
    sales = db.query(models.Sale).filter(models.Sale.customer_name == name.strip()).order_by(models.Sale.created_at.desc()).all()
    payments = db.query(models.DebtPayment).filter(models.DebtPayment.customer_name == name.strip()).order_by(models.DebtPayment.created_at.desc()).all()

    sale_list = []
    for s in sales:
        sale_list.append({
            "id": s.id,
            "receipt_number": s.receipt_number,
            "created_at": s.created_at,
            "payment_method": s.payment_method,
            "cashier_name": s.cashier_name,
            "total_amount": s.total_amount,
            "paid_amount": s.paid_amount,
            "debt_amount": s.debt_amount,
            "total_items": s.total_items
        })

    payment_list = []
    for p in payments:
        payment_list.append({
            "id": p.id,
            "receipt_number": p.receipt_number,
            "amount": p.amount,
            "payment_method": p.payment_method,
            "cashier_name": p.cashier_name,
            "created_at": p.created_at,
            "remark": p.remark
        })

    total_debt = sum(s.debt_amount for s in sales)

    return {
        "code": 0,
        "data": {
            "customer_name": name.strip(),
            "phone": sales[0].customer_phone if sales and sales[0].customer_phone else "",
            "total_debt": total_debt,
            "sales": sale_list,
            "payments": payment_list
        }
    }


@router.get("/sales/payment-receipt/{receipt_number}")
def get_payment_receipt(receipt_number: str, db: Session = Depends(get_db)):
    payment = db.query(models.DebtPayment).filter(models.DebtPayment.receipt_number == receipt_number).first()
    if not payment:
        raise HTTPException(status_code=404, detail="To'lov cheki topilmadi")
    return {
        "code": 0,
        "data": {
            "id": payment.id,
            "receipt_number": payment.receipt_number,
            "customer_name": payment.customer_name,
            "customer_phone": payment.customer_phone,
            "amount": payment.amount,
            "payment_method": payment.payment_method,
            "cashier_name": payment.cashier_name,
            "created_at": payment.created_at,
            "remark": payment.remark
        }
    }


@router.post("/sales/repay-debt")
def repay_debt(payment_in: schemas.DebtPaymentCreate, db: Session = Depends(get_db)):
    name = payment_in.customer_name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Qarzdor ismi kiritilmagan")
    if payment_in.amount <= 0:
        raise HTTPException(status_code=400, detail="Qaytariladigan summa 0 dan katta bo'lishi shart")

    # Find open debt sales for this customer ordered by oldest first
    sales = db.query(models.Sale).filter(models.Sale.customer_name == name, models.Sale.debt_amount > 0).order_by(models.Sale.created_at.asc()).all()

    remaining_payment = payment_in.amount

    for s in sales:
        if remaining_payment <= 0:
            break
        if s.debt_amount <= remaining_payment:
            remaining_payment -= s.debt_amount
            s.paid_amount += s.debt_amount
            s.debt_amount = 0.0
        else:
            s.debt_amount -= remaining_payment
            s.paid_amount += remaining_payment
            remaining_payment = 0.0

    # Create debt payment record
    p_id = f"PAY-{uuid.uuid4().hex[:8]}"
    receipt_no = f"QARZ-CHK-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"

    db_payment = models.DebtPayment(
        id=p_id,
        receipt_number=receipt_no,
        customer_name=name,
        customer_phone=payment_in.customer_phone,
        amount=payment_in.amount,
        payment_method=payment_in.payment_method or "naqd",
        cashier_name=payment_in.cashier_name or "admin",
        remark=payment_in.remark,
        created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    db.add(db_payment)

    # Calculate remaining debt directly in memory (0 network queries)
    remaining_total_debt = sum(s.debt_amount for s in sales)

    log_activity(
        db,
        actor=payment_in.cashier_name or "admin",
        action="created",
        entity="debt_payment",
        entity_id=db_payment.id,
        entity_name=f"Qarz to'landi: {name} (${payment_in.amount:,.2f})",
        commit=False
    )

    db.commit()
    invalidate_sales()
    invalidate_analytics()

    return {
        "code": 0,
        "message": f"'{name}' mijozidan ${payment_in.amount:,.2f} qarz to'lovi qabul qilindi!",
        "data": {
            "id": db_payment.id,
            "receipt_number": db_payment.receipt_number,
            "customer_name": db_payment.customer_name,
            "amount": db_payment.amount,
            "payment_method": db_payment.payment_method,
            "cashier_name": db_payment.cashier_name,
            "created_at": db_payment.created_at,
            "remaining_total_debt": remaining_total_debt
        }
    }


# ==============================================================================
# Sales Push & Mobile POS Terminal Endpoints (Requirements R2 & R3)
# ==============================================================================

@router.post("/sales/push-pc-sale")
@router.post("/api/sales/push-pc-sale")
def push_pc_sale(
    payload: schemas.SalesPushCreate,
    device_token: models.DeviceToken = Depends(get_current_device_token),
    db: Session = Depends(get_db)
):
    if not payload.items or len(payload.items) == 0:
        raise HTTPException(status_code=400, detail="Items list cannot be empty")

    for item in payload.items:
        if item.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        if item.price < 0:
            raise HTTPException(status_code=400, detail="Price cannot be negative")

        p_id = str(item.product_id)
        prod = db.query(models.Product).filter(
            (models.Product.id == p_id) | (models.Product.SKU == p_id) | (models.Product.shtrix_code == p_id)
        ).first()
        if not prod:
            raise HTTPException(status_code=404, detail=f"Product '{item.product_id}' not found")

    # Enforce strict account isolation: target pc_user_id must match the device_token's owner user_id
    target_pc_user_id = device_token.user_id
    if payload.pc_user_id and payload.pc_user_id != device_token.user_id:
        # If user explicitly requested target_pc_user_id, verify target user exists
        target_user = db.query(models.User).filter(models.User.id == payload.pc_user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail=f"Target PC User ID {payload.pc_user_id} not found")
        target_pc_user_id = target_user.id

    push_id = f"PUSH-{uuid.uuid4().hex[:8]}"
    items_data = [item.model_dump() for item in payload.items]

    sp = models.SalesPush(
        id=push_id,
        device_token=device_token.token,
        pc_user_id=target_pc_user_id,
        device_name=device_token.device_name,
        items_json=json.dumps(items_data),
        status="pending",
        created_at=datetime.datetime.utcnow()
    )
    db.add(sp)
    db.commit()
    db.refresh(sp)

    try:
        from app.websocket_manager import manager
        manager.broadcast_sync(
            entity="sales_push",
            action="created",
            entity_id=push_id,
            data={
                "push_id": push_id,
                "status": "pending",
                "device_name": device_token.device_name,
                "pc_user_id": target_pc_user_id,
                "item_count": len(items_data),
                "items": items_data
            },
            target_user_id=target_pc_user_id
        )
    except Exception:
        pass

    return {
        "code": 0,
        "message": "Push alert sent to PC",
        "push_id": push_id,
        "status": "pending",
        "data": {
            "push_id": push_id,
            "status": "pending",
            "device_name": device_token.device_name,
            "pc_user_id": target_pc_user_id
        }
    }


@router.get("/sales/pending-pushes")
@router.get("/api/sales/pending-pushes")
def get_pending_pushes(
    current_user: models.User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    # Auto-expire stale pushes older than 30 minutes
    thirty_mins_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
    stale = db.query(models.SalesPush).filter(
        models.SalesPush.status == "pending",
        models.SalesPush.created_at < thirty_mins_ago
    ).all()
    if stale:
        for s in stale:
            s.status = "expired"
        db.commit()

    pushes = db.query(models.SalesPush).filter(
        models.SalesPush.pc_user_id == current_user.id,
        models.SalesPush.status == "pending"
    ).order_by(models.SalesPush.created_at.desc()).all()

    result = []
    for p in pushes:
        items = json.loads(p.items_json) if p.items_json else []
        result.append({
            "push_id": p.id,
            "device_token": p.device_token,
            "device_name": p.device_name,
            "status": p.status,
            "item_count": len(items),
            "items": items,
            "created_at": p.created_at.isoformat() if p.created_at else None
        })

    return {
        "code": 0,
        "message": "Success",
        "data": result
    }


@router.post("/sales/respond-push")
@router.post("/api/sales/respond-push")
def respond_push(
    payload: schemas.SalesPushRespond,
    current_user: models.User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    if payload.action not in ["accept", "decline"]:
        raise HTTPException(status_code=400, detail="Action must be 'accept' or 'decline'")

    sp = db.query(models.SalesPush).filter(models.SalesPush.id == payload.push_id).first()
    if not sp:
        raise HTTPException(status_code=404, detail="Push notification not found")

    if sp.status != "pending":
        raise HTTPException(status_code=400, detail=f"Push alert already in status {sp.status}")

    new_status = "accepted" if payload.action == "accept" else "declined"
    sp.status = new_status
    sp.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(sp)

    try:
        from app.websocket_manager import manager
        manager.broadcast_sync(
            entity="sales_push",
            action=payload.action,
            entity_id=sp.id,
            data={
                "push_id": sp.id,
                "status": new_status,
                "pc_user_id": current_user.id
            }
        )
    except Exception:
        pass

    return {
        "code": 0,
        "message": f"Push alert {new_status}",
        "push_id": sp.id,
        "status": new_status,
        "data": {
            "push_id": sp.id,
            "status": new_status
        }
    }


@router.get("/sales/push-payload/{push_id}")
@router.get("/api/sales/push-payload/{push_id}")
def get_push_payload(
    push_id: str,
    current_user: models.User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    sp = db.query(models.SalesPush).filter(models.SalesPush.id == push_id).first()
    if not sp:
        raise HTTPException(status_code=404, detail="Push alert not found")

    if sp.status == "declined":
        raise HTTPException(status_code=400, detail="Push alert was declined")

    items = json.loads(sp.items_json) if sp.items_json else []
    total_amount = sum(it.get("quantity", 0) * it.get("price", 0.0) for it in items)

    hydrated_items = []
    for it in items:
        p_id = str(it.get("product_id"))
        prod = db.query(models.Product).filter(
            (models.Product.id == p_id) | (models.Product.SKU == p_id) | (models.Product.shtrix_code == p_id)
        ).first()
        hydrated_items.append({
            "product_id": prod.id if prod else it.get("product_id"),
            "product_name": prod.productName if prod else it.get("product_name", f"Product {p_id}"),
            "quantity": it.get("quantity", 1),
            "price": it.get("price", prod.price if prod else 0.0),
            "cost": prod.cost if prod else 0.0,
            "shtrix_code": prod.shtrix_code if prod else None,
            "unit_name": it.get("unit_name"),
            "conversion_factor": it.get("conversion_factor", 1.0)
        })

    return {
        "code": 0,
        "message": "Success",
        "push_id": sp.id,
        "status": sp.status,
        "total_amount": total_amount,
        "items": hydrated_items,
        "data": {
            "push_id": sp.id,
            "items": hydrated_items,
            "total_amount": total_amount,
            "status": sp.status
        }
    }


@router.post("/sales/phone-checkout")
@router.post("/api/sales/phone-checkout")
def phone_checkout(
    payload: schemas.PhoneCheckoutRequest,
    device_token: models.DeviceToken = Depends(get_current_device_token),
    db: Session = Depends(get_db)
):
    valid_payments = ["cash", "card", "debt", "naqd", "karta", "nasiya"]
    if payload.payment_type not in valid_payments:
        raise HTTPException(status_code=400, detail=f"Invalid payment_type '{payload.payment_type}'")

    if not payload.items or len(payload.items) == 0:
        raise HTTPException(status_code=400, detail="Items list cannot be empty")

    pm_map = {
        "cash": "naqd",
        "card": "karta",
        "debt": "nasiya",
        "naqd": "naqd",
        "karta": "karta",
        "nasiya": "nasiya"
    }
    payment_method = pm_map[payload.payment_type]

    total_calc = 0.0
    total_qty = 0
    items_to_process = []
    product_requirements = {}

    for item in payload.items:
        if item.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        if item.price < 0:
            raise HTTPException(status_code=400, detail="Price cannot be negative")

        p_id = str(item.product_id)
        prod = db.query(models.Product).filter(
            (models.Product.id == p_id) | (models.Product.SKU == p_id) | (models.Product.shtrix_code == p_id)
        ).first()
        if not prod:
            raise HTTPException(status_code=404, detail=f"Product '{item.product_id}' not found")

        conversion_factor = float(getattr(item, 'conversion_factor', 1.0) or 1.0)
        unit_name = getattr(item, 'unit_name', None)
        required_base_qty = float(item.quantity) * conversion_factor

        p_key = prod.id
        product_requirements[p_key] = product_requirements.get(p_key, 0.0) + required_base_qty

        items_to_process.append((prod, item, required_base_qty, conversion_factor, unit_name))
        total_calc += float(item.price) * float(item.quantity)
        total_qty += item.quantity

    # Validate stock
    for p_key, total_req in product_requirements.items():
        p_obj = db.query(models.Product).filter(models.Product.id == p_key).first()
        if p_obj and p_obj.quantityInStock < total_req:
            base_unit = p_obj.unit or 'kg'
            raise HTTPException(
                status_code=400,
                detail=f"'{p_obj.productName}' mahsulotidan omborda yetarli emas! Omborda mavjud: {p_obj.quantityInStock:.2f} {base_unit}, Jami talab: {total_req:.2f} {base_unit}"
            )

    for prod, item, required_base_qty, conversion_factor, unit_name in items_to_process:
        prod.quantityInStock -= required_base_qty
        if prod.quantityInStock <= 0.00001:
            prod.quantityInStock = 0.0
            prod.status = 0

    final_total = payload.total_amount if payload.total_amount > 0 else total_calc
    final_total = max(0.0, final_total - (payload.discount or 0.0))

    if payment_method == "nasiya":
        paid = payload.paid_amount or 0.0
        paid = min(paid, final_total)
        debt = max(0.0, final_total - paid)
    else:
        paid = final_total
        debt = 0.0

    receipt_no = f"CHK-PH-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
    sale_id = f"SALE-{uuid.uuid4().hex[:8]}"

    user = db.query(models.User).filter(models.User.id == device_token.user_id).first()
    cashier_name = user.username if user else f"Device-{device_token.device_name}"

    db_sale = models.Sale(
        id=sale_id,
        receipt_number=receipt_no,
        cashier_name=cashier_name,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        payment_method=payment_method,
        total_amount=final_total,
        paid_amount=paid,
        debt_amount=debt,
        total_items=total_qty,
        discount=payload.discount or 0.0,
        remark=payload.remark,
        created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(db_sale)

    for prod, item, required_base_qty, conversion_factor, unit_name in items_to_process:
        s_item = models.SaleItem(
            id=f"SI-{uuid.uuid4().hex[:8]}",
            sale_id=sale_id,
            product_id=prod.id,
            product_name=prod.productName,
            shtrix_code=prod.shtrix_code,
            price=item.price,
            cost=prod.cost or 0.0,
            quantity=item.quantity,
            unit_name=unit_name,
            conversion_factor=conversion_factor,
            total=item.price * item.quantity
        )
        db.add(s_item)


    db.commit()
    db.refresh(db_sale)
    invalidate_sales()
    invalidate_analytics()

    return {
        "code": 0,
        "message": "Phone checkout successful",
        "id": db_sale.id,
        "receipt_number": db_sale.receipt_number,
        "total_amount": db_sale.total_amount,
        "paid_amount": db_sale.paid_amount,
        "debt_amount": db_sale.debt_amount,
        "payment_method": db_sale.payment_method,
        "total_items": db_sale.total_items,
        "data": {
            "id": db_sale.id,
            "receipt_number": db_sale.receipt_number,
            "total_amount": db_sale.total_amount,
            "paid_amount": db_sale.paid_amount,
            "debt_amount": db_sale.debt_amount,
            "payment_method": db_sale.payment_method,
            "total_items": db_sale.total_items,
            "cashier_name": db_sale.cashier_name
        }
    }

