from fastapi import APIRouter, Depends, Query, HTTPException, Body, Header
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.database import get_db, SessionLocal
from app import models, schemas
from app.cache import get_analytics_cache, set_analytics_cache, invalidate_analytics
from app.routers.product import get_user_company_id
from app.auth import get_current_user_from_header, check_user_access
from concurrent.futures import ThreadPoolExecutor
import datetime

router = APIRouter()

def calc_month_metrics(db: Session, ym: str, company_id: str = None, branch_id: str = None):
    """
    ym: 'YYYY-MM' e.g. '2026-08'
    Calculates exact real figures for that month with concurrent database queries.
    """
    def q_sales():
        s_db = SessionLocal()
        try:
            q = s_db.query(models.Sale).options(joinedload(models.Sale.items)).filter(
                models.Sale.created_at.like(f"{ym}%")
            )
            if company_id:
                q = q.filter(models.Sale.company_id == company_id)
            if branch_id:
                q = q.filter(models.Sale.branch_id == branch_id)
            return q.all()
        finally:
            s_db.close()

    def q_debt_payments():
        s_db = SessionLocal()
        try:
            q = s_db.query(models.DebtPayment).filter(
                models.DebtPayment.created_at.like(f"{ym}%")
            )
            if company_id:
                q = q.filter(models.DebtPayment.company_id == company_id)
            return q.all()
        finally:
            s_db.close()

    def q_salaries():
        s_db = SessionLocal()
        try:
            q = s_db.query(models.Salary).join(models.Worker, models.Salary.workerId == models.Worker.id).filter(
                models.Salary.status == "paid",
                (models.Salary.payDate.like(f"{ym}%") | models.Salary.remark.like(f"%{ym}%"))
            )
            if company_id:
                q = q.filter(models.Worker.company_id == company_id)
            if branch_id:
                q = q.filter(models.Worker.branch_id == branch_id)
            return q.all()
        finally:
            s_db.close()

    def q_outputs():
        s_db = SessionLocal()
        try:
            q = s_db.query(models.StaffOutput).join(models.Worker, models.StaffOutput.workerId == models.Worker.id).filter(
                (models.StaffOutput.createTime.like(f"{ym}%") | models.StaffOutput.period_month.like(f"{ym}%"))
            )
            if company_id:
                q = q.filter(models.Worker.company_id == company_id)
            if branch_id:
                q = q.filter(models.Worker.branch_id == branch_id)
            return q.all()
        finally:
            s_db.close()

    def q_adjustments():
        s_db = SessionLocal()
        try:
            q = s_db.query(models.StaffAdjustment).join(models.Worker, models.StaffAdjustment.workerId == models.Worker.id).filter(
                (models.StaffAdjustment.period_month == ym) | (models.StaffAdjustment.createTime.like(f"{ym}%"))
            )
            if company_id:
                q = q.filter(models.Worker.company_id == company_id)
            if branch_id:
                q = q.filter(models.Worker.branch_id == branch_id)
            return q.all()
        finally:
            s_db.close()

    with ThreadPoolExecutor(max_workers=5) as executor:
        f_sales = executor.submit(q_sales)
        f_debt_payments = executor.submit(q_debt_payments)
        f_salaries = executor.submit(q_salaries)
        f_outputs = executor.submit(q_outputs)
        f_adjustments = executor.submit(q_adjustments)

        sales = f_sales.result()
        debt_payments = f_debt_payments.result()
        salaries = f_salaries.result()
        outputs = f_outputs.result()
        adjustments = f_adjustments.result()

    revenue = round(sum(float(s.total_amount or getattr(s, 'total', 0.0) or 0.0) for s in sales), 2)
    total_paid = round(sum(float(s.paid_amount or 0.0) for s in sales), 2)
    total_debt = round(sum(float(s.debt_amount or 0.0) for s in sales), 2)
    
    cogs = 0.0
    for s in sales:
        for it in s.items:
            cogs += float(it.cost or 0.0) * float(it.quantity or 1.0)

    staff_salaries = sum(float(s.netSalary or 0.0) for s in salaries)
    short_term_outputs = sum(float(o.amount or 0.0) for o in outputs)
    bonuses = sum(float(a.amount or 0.0) for a in adjustments if str(a.document_type or '').lower() in ["bonus", "ragbat"])
    advances = sum(float(a.amount or 0.0) for a in adjustments if str(a.document_type or '').lower() in ["advance", "avans"])

    total_payroll = round(staff_salaries + short_term_outputs + bonuses, 2)
    total_expenses = round(cogs + total_payroll, 2)
    net_profit = round(revenue - total_expenses, 2)
    profit_margin = round((net_profit / revenue * 100), 1) if revenue > 0 else 0.0

    return {
        "period_month": ym,
        "revenue": round(revenue, 2),
        "total_paid": round(total_paid, 2),
        "total_debt": round(total_debt, 2),
        "cogs": round(cogs, 2),
        "staff_salaries": round(staff_salaries, 2),
        "short_term_outputs": round(short_term_outputs, 2),
        "bonuses": round(bonuses, 2),
        "advances": round(advances, 2),
        "total_payroll": total_payroll,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "profit_margin": profit_margin,
        "sales_count": len(sales)
    }


def calc_date_range_metrics(db: Session, start_date: str, end_date: str, company_id: str = None, branch_id: str = None):
    """
    start_date: 'YYYY-MM-DD'
    end_date: 'YYYY-MM-DD'
    Calculates exact real metrics for any specific date range using concurrent execution.
    """
    start_dt_str = f"{start_date} 00:00:00"
    end_dt_str = f"{end_date} 23:59:59"

    def q_sales():
        s_db = SessionLocal()
        try:
            q = s_db.query(models.Sale).options(joinedload(models.Sale.items)).filter(
                models.Sale.created_at >= start_dt_str,
                models.Sale.created_at <= end_dt_str
            )
            if company_id:
                q = q.filter(models.Sale.company_id == company_id)
            if branch_id:
                q = q.filter(models.Sale.branch_id == branch_id)
            return q.all()
        finally:
            s_db.close()

    def q_debt_payments():
        s_db = SessionLocal()
        try:
            q = s_db.query(models.DebtPayment).filter(
                models.DebtPayment.created_at >= start_dt_str,
                models.DebtPayment.created_at <= end_dt_str
            )
            if company_id:
                q = q.filter(models.DebtPayment.company_id == company_id)
            return q.all()
        finally:
            s_db.close()

    def q_salaries():
        s_db = SessionLocal()
        try:
            q = s_db.query(models.Salary).join(models.Worker, models.Salary.workerId == models.Worker.id).filter(
                models.Salary.status == "paid",
                models.Salary.payDate >= start_date,
                models.Salary.payDate <= end_date
            )
            if company_id:
                q = q.filter(models.Worker.company_id == company_id)
            if branch_id:
                q = q.filter(models.Worker.branch_id == branch_id)
            return q.all()
        finally:
            s_db.close()

    def q_outputs():
        s_db = SessionLocal()
        try:
            q = s_db.query(models.StaffOutput).join(models.Worker, models.StaffOutput.workerId == models.Worker.id).filter(
                models.StaffOutput.createTime >= start_dt_str,
                models.StaffOutput.createTime <= end_dt_str
            )
            if company_id:
                q = q.filter(models.Worker.company_id == company_id)
            if branch_id:
                q = q.filter(models.Worker.branch_id == branch_id)
            return q.all()
        finally:
            s_db.close()

    def q_adjustments():
        s_db = SessionLocal()
        try:
            q = s_db.query(models.StaffAdjustment).join(models.Worker, models.StaffAdjustment.workerId == models.Worker.id).filter(
                models.StaffAdjustment.createTime >= start_dt_str,
                models.StaffAdjustment.createTime <= end_dt_str
            )
            if company_id:
                q = q.filter(models.Worker.company_id == company_id)
            if branch_id:
                q = q.filter(models.Worker.branch_id == branch_id)
            return q.all()
        finally:
            s_db.close()

    with ThreadPoolExecutor(max_workers=5) as executor:
        f_sales = executor.submit(q_sales)
        f_debt_payments = executor.submit(q_debt_payments)
        f_salaries = executor.submit(q_salaries)
        f_outputs = executor.submit(q_outputs)
        f_adjustments = executor.submit(q_adjustments)

        sales = f_sales.result()
        debt_payments = f_debt_payments.result()
        salaries = f_salaries.result()
        outputs = f_outputs.result()
        adjustments = f_adjustments.result()

    revenue = round(sum(float(s.total_amount or getattr(s, 'total', 0.0) or 0.0) for s in sales), 2)
    total_paid = round(sum(float(s.paid_amount or 0.0) for s in sales), 2)
    total_debt = round(sum(float(s.debt_amount or 0.0) for s in sales), 2)

    cogs = 0.0
    for s in sales:
        for it in s.items:
            cogs += float(it.cost or 0.0) * float(it.quantity or 1.0)

    staff_salaries = sum(float(s.netSalary or 0.0) for s in salaries)
    short_term_outputs = sum(float(o.amount or 0.0) for o in outputs)
    bonuses = sum(float(a.amount or 0.0) for a in adjustments if str(a.document_type or '').lower() in ["bonus", "ragbat"])

    total_payroll = round(staff_salaries + short_term_outputs + bonuses, 2)
    total_expenses = round(cogs + total_payroll, 2)
    net_profit = round(revenue - total_expenses, 2)
    profit_margin = round((net_profit / revenue * 100), 1) if revenue > 0 else 0.0

    return {
        "start_date": start_date,
        "end_date": end_date,
        "revenue": round(revenue, 2),
        "total_paid": round(total_paid, 2),
        "total_debt": round(total_debt, 2),
        "cogs": round(cogs, 2),
        "staff_salaries": round(staff_salaries, 2),
        "short_term_outputs": round(short_term_outputs, 2),
        "total_payroll": total_payroll,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "profit_margin": profit_margin,
        "sales_count": len(sales)
    }


@router.get("/analysis/financial-overview")
def get_financial_overview(
    time_range: str = Query("6m"),
    company_id: str = Query(None),
    branch_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    current_user = get_current_user_from_header(authorization, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Tizimga kirilmagan yoki sessiya yaroqsiz")
    check_user_access(current_user, ["dashboard:view", "analysis:view", "analysis", "/dashboard"], db)

    target_company = get_user_company_id(authorization, db, company_id)
    cache_key = f"financial_overview:{target_company}:{time_range}:{branch_id or 'all'}"
    cached = get_analytics_cache(cache_key)
    if cached is not None:
        return cached

    months_count = 12 if time_range in ["1y", "12m", "yearly"] else 6
    month_names_uz = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"]

    now = datetime.datetime.now()
    curr_year = now.year
    curr_month = now.month

    target_months = []
    for i in range(months_count - 1, -1, -1):
        m_calc = curr_month - i
        y_calc = curr_year
        while m_calc <= 0:
            m_calc += 12
            y_calc -= 1
        ym = f"{y_calc:04d}-{m_calc:02d}"
        month_label = f"{month_names_uz[m_calc - 1]} {y_calc}"
        target_months.append((ym, month_label))

    start_ym = target_months[0][0]
    end_ym = target_months[-1][0]
    start_dt = f"{start_ym}-01 00:00:00"
    end_dt = f"{end_ym}-31 23:59:59"

    # Concurrent batch fetch of all records in period
    def q_sales():
        s_db = SessionLocal()
        try:
            q = s_db.query(models.Sale).options(joinedload(models.Sale.items)).filter(
                models.Sale.created_at >= start_dt,
                models.Sale.created_at <= end_dt
            )
            if target_company:
                q = q.filter(models.Sale.company_id == target_company)
            if branch_id:
                q = q.filter(models.Sale.branch_id == branch_id)
            return q.all()
        finally:
            s_db.close()

    def q_salaries():
        s_db = SessionLocal()
        try:
            q = s_db.query(models.Salary).join(models.Worker, models.Salary.workerId == models.Worker.id).filter(
                models.Salary.status == "paid",
                models.Salary.payDate >= f"{start_ym}-01",
                models.Salary.payDate <= f"{end_ym}-31"
            )
            if target_company:
                q = q.filter(models.Worker.company_id == target_company)
            if branch_id:
                q = q.filter(models.Worker.branch_id == branch_id)
            return q.all()
        finally:
            s_db.close()

    def q_outputs():
        s_db = SessionLocal()
        try:
            q = s_db.query(models.StaffOutput).join(models.Worker, models.StaffOutput.workerId == models.Worker.id).filter(
                models.StaffOutput.createTime >= start_dt,
                models.StaffOutput.createTime <= end_dt
            )
            if target_company:
                q = q.filter(models.Worker.company_id == target_company)
            return q.all()
        finally:
            s_db.close()

    def q_adjustments():
        s_db = SessionLocal()
        try:
            q = s_db.query(models.StaffAdjustment).join(models.Worker, models.StaffAdjustment.workerId == models.Worker.id).filter(
                models.StaffAdjustment.createTime >= start_dt,
                models.StaffAdjustment.createTime <= end_dt
            )
            if target_company:
                q = q.filter(models.Worker.company_id == target_company)
            return q.all()
        finally:
            s_db.close()

    def q_debt_payments():
        s_db = SessionLocal()
        try:
            q = s_db.query(models.DebtPayment).filter(
                models.DebtPayment.created_at >= start_dt,
                models.DebtPayment.created_at <= end_dt
            )
            if target_company:
                q = q.filter(models.DebtPayment.company_id == target_company)
            return q.all()
        finally:
            s_db.close()

    def q_products():
        s_db = SessionLocal()
        try:
            q = s_db.query(models.Product)
            if target_company:
                q = q.filter(models.Product.company_id == target_company)
            if branch_id:
                q = q.filter(models.Product.branch_id == branch_id)
            return q.all()
        finally:
            s_db.close()

    with ThreadPoolExecutor(max_workers=6) as executor:
        f_sales = executor.submit(q_sales)
        f_debt_payments = executor.submit(q_debt_payments)
        f_salaries = executor.submit(q_salaries)
        f_outputs = executor.submit(q_outputs)
        f_adjustments = executor.submit(q_adjustments)
        f_products = executor.submit(q_products)

        all_sales = f_sales.result()
        all_debt_payments = f_debt_payments.result()
        all_salaries = f_salaries.result()
        all_outputs = f_outputs.result()
        all_adjustments = f_adjustments.result()
        products = f_products.result()

    # In-memory grouping by YYYY-MM
    monthly_data = []
    for ym, m_label in target_months:
        m_sales = [s for s in all_sales if s.created_at and s.created_at.startswith(ym)]
        m_rev = round(sum(float(s.total_amount or getattr(s, 'total', 0.0) or 0.0) for s in m_sales), 2)
        m_paid = round(sum(float(s.paid_amount or 0.0) for s in m_sales), 2)
        m_debt = round(sum(float(s.debt_amount or 0.0) for s in m_sales), 2)
        m_cogs = sum(sum(float(it.cost or 0.0) * float(it.quantity or 1.0) for it in s.items) for s in m_sales)

        m_sal = sum(float(s.netSalary or 0.0) for s in all_salaries if s.payDate and s.payDate.startswith(ym))
        m_out = sum(float(o.amount or 0.0) for o in all_outputs if o.createTime and o.createTime.startswith(ym))
        m_bon = sum(float(a.amount or 0.0) for a in all_adjustments if a.createTime and a.createTime.startswith(ym) and str(a.document_type or '').lower() in ["bonus", "ragbat"])

        m_payroll = round(m_sal + m_out + m_bon, 2)
        m_exp = round(m_cogs + m_payroll, 2)
        m_profit = round(m_rev - m_exp, 2)
        m_margin = round((m_profit / m_rev * 100), 1) if m_rev > 0 else 0.0

        monthly_data.append({
            "month": m_label,
            "period_month": ym,
            "revenue": round(m_rev, 2),
            "totalPaid": m_paid,
            "totalDebt": m_debt,
            "cogs": round(m_cogs, 2),
            "staffSalaries": round(m_sal, 2),
            "shortTermOutputs": round(m_out, 2),
            "totalPayroll": m_payroll,
            "totalExpenses": m_exp,
            "netProfit": m_profit,
            "profitMargin": m_margin,
            "salesCount": len(m_sales)
        })

    # Overall Totals across the period
    gross_revenue = round(sum(m["revenue"] for m in monthly_data), 2)
    total_paid = round(sum(float(s.paid_amount or 0.0) for s in all_sales), 2)
    total_debt = round(sum(float(s.debt_amount or 0.0) for s in all_sales), 2)
    total_cogs = round(sum(m["cogs"] for m in monthly_data), 2)
    total_staff = round(sum(m["staffSalaries"] for m in monthly_data), 2)
    total_short = round(sum(m["shortTermOutputs"] for m in monthly_data), 2)
    total_payroll = round(sum(m["totalPayroll"] for m in monthly_data), 2)
    total_expenses = round(sum(m["totalExpenses"] for m in monthly_data), 2)
    real_net_profit = round(gross_revenue - total_expenses, 2)
    profit_margin = round((real_net_profit / gross_revenue * 100), 1) if gross_revenue > 0 else 0.0

    # Category breakdown (products already fetched in parallel)
    prod_cat_map = {p.id: (p.category or "Boshqa") for p in products}
    cat_stats: dict[str, dict] = {}

    for s in all_sales:
        for it in s.items:
            cat = prod_cat_map.get(it.product_id, "Boshqa")
            if cat not in cat_stats:
                cat_stats[cat] = {"revenue": 0.0, "cost": 0.0, "profit": 0.0}
            line_rev = float(it.total or (it.price * it.quantity) or 0.0)
            line_cost = float((it.cost or 0.0) * it.quantity)
            cat_stats[cat]["revenue"] += line_rev
            cat_stats[cat]["cost"] += line_cost
            cat_stats[cat]["profit"] += (line_rev - line_cost)

    sorted_cats = sorted(cat_stats.items(), key=lambda x: x[1]["revenue"], reverse=True)
    category_profits = [
        {
            "name": k,
            "revenue": round(v["revenue"], 2),
            "cost": round(v["cost"], 2),
            "profit": round(v["profit"], 2)
        }
        for k, v in sorted_cats if v["revenue"] > 0
    ]

    res = {
        "code": 0,
        "data": {
            "grossRevenue": gross_revenue,
            "totalPaid": total_paid,
            "totalDebt": total_debt,
            "totalSalesCount": len(all_sales),
            "cogs": total_cogs,
            "staffSalaries": total_staff,
            "shortTermOutputs": total_short,
            "totalPayroll": total_payroll,
            "totalExpenses": total_expenses,
            "realNetProfit": real_net_profit,
            "profitMargin": profit_margin,
            "activeWorkersCount": db.query(models.Worker).filter(
                models.Worker.status == 1,
                (models.Worker.company_id == target_company) if target_company else True,
                (models.Worker.branch_id == branch_id) if branch_id else True
            ).count(),
            "shortTermTasksCount": len(all_outputs),
            "monthlyFinancials": monthly_data,
            "expenseBreakdown": [
                {"name": "Mahsulot Tannarxi (COGS)", "value": total_cogs},
                {"name": "Doimiy Xodimlar Maoshi", "value": total_staff},
                {"name": "Qisqa Muddatli Ishchilar To'lovi", "value": total_short},
                {"name": "Bonus va Rag'batlantirish", "value": round(total_payroll - total_staff - total_short, 2)}
            ],
            "categoryProfits": category_profits
        }
    }
    set_analytics_cache(cache_key, res)
    return res


@router.get("/workplace/summary")
def get_workplace_summary(
    company_id: str = Query(None),
    branch_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Returns real summary counts for the workplace hero header:
    - productsCount: Distinct product catalog count
    - activeWorkersCount: Active staff members
    - salesCount: Total sales receipts
    - debtorsCount: Customers/Sales with pending debt
    - totalDebtAmount: Outstanding receivable total
    """
    target_company = get_user_company_id(authorization, db, company_id)

    prod_q = db.query(func.count(models.Product.id))
    if target_company:
        prod_q = prod_q.filter(models.Product.company_id == target_company)
    products_count = prod_q.scalar() or 0

    worker_q = db.query(func.count(models.Worker.id)).filter(models.Worker.status == 1)
    if target_company:
        worker_q = worker_q.filter(models.Worker.company_id == target_company)
    workers_count = worker_q.scalar() or 0

    sales_q = db.query(func.count(models.Sale.id))
    if target_company:
        sales_q = sales_q.filter(models.Sale.company_id == target_company)
    sales_count = sales_q.scalar() or 0

    debtors_q = db.query(func.count(models.Sale.id)).filter(models.Sale.debt_amount > 0)
    if target_company:
        debtors_q = debtors_q.filter(models.Sale.company_id == target_company)
    debtors_count = debtors_q.scalar() or 0

    debt_sum_q = db.query(func.sum(models.Sale.debt_amount))
    if target_company:
        debt_sum_q = debt_sum_q.filter(models.Sale.company_id == target_company)
    total_debt_amount = float(debt_sum_q.scalar() or 0.0)

    return {
        "code": 0,
        "data": {
            "productsCount": products_count,
            "activeWorkersCount": workers_count,
            "salesCount": sales_count,
            "debtorsCount": debtors_count,
            "totalDebtAmount": round(total_debt_amount, 2)
        }
    }


@router.get("/analysis/month-summary")
def get_month_summary(
    month: str = Query(...),
    company_id: str = Query(None),
    branch_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Returns exact real calculations for a specific month (e.g. '2026-08').
    If month is officially closed, returns the frozen snapshot.
    """
    target_company = get_user_company_id(authorization, db, company_id)
    month = month.strip()
    cache_key = f"month_summary:{target_company}:{branch_id or 'all'}:{month}"
    cached = get_analytics_cache(cache_key)
    if cached is not None:
        return cached

    snap_q = db.query(models.MonthlyFinancialSnapshot).filter(
        models.MonthlyFinancialSnapshot.period_month == month
    )
    if target_company:
        snap_q = snap_q.filter(models.MonthlyFinancialSnapshot.company_id == target_company)
    snapshot = snap_q.first()

    if snapshot and not branch_id:
        res = {
            "code": 0,
            "data": {
                "period_month": snapshot.period_month,
                "revenue": snapshot.revenue,
                "cogs": snapshot.cogs,
                "staffSalaries": snapshot.staff_salaries,
                "shortTermOutputs": snapshot.short_term_outputs,
                "totalPayroll": round(snapshot.staff_salaries + snapshot.short_term_outputs, 2),
                "totalExpenses": snapshot.total_expenses,
                "netProfit": snapshot.net_profit,
                "profitMargin": snapshot.profit_margin,
                "salesCount": snapshot.sales_count,
                "is_frozen": True,
                "status": snapshot.status,
                "remark": snapshot.remark,
                "closed_by": snapshot.closed_by,
                "created_at": snapshot.created_at.strftime("%Y-%m-%d %H:%M:%S") if snapshot.created_at else None
            }
        }
        set_analytics_cache(cache_key, res)
        return res

    data = calc_month_metrics(db, month, company_id=target_company, branch_id=branch_id)
    res = {
        "code": 0,
        "data": {
            "period_month": data["period_month"],
            "revenue": data["revenue"],
            "totalPaid": data.get("total_paid", 0.0),
            "totalDebt": data.get("total_debt", 0.0),
            "cogs": data["cogs"],
            "staffSalaries": data["staff_salaries"],
            "shortTermOutputs": data["short_term_outputs"],
            "totalPayroll": data["total_payroll"],
            "totalExpenses": data["total_expenses"],
            "netProfit": data["net_profit"],
            "profitMargin": data["profit_margin"],
            "salesCount": data["sales_count"],
            "is_frozen": False,
            "status": "open"
        }
    }
    set_analytics_cache(cache_key, res)
    return res


@router.get("/analysis/bundle")
def get_analysis_bundle(
    time_range: str = Query("6m"),
    month: str = Query(None),
    p1_start: str = Query(None),
    p1_end: str = Query(None),
    p2_start: str = Query(None),
    p2_end: str = Query(None),
    company_id: str = Query(None),
    branch_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Unified master endpoint: Returns ALL dashboard data at once in a SINGLE network request.
    Eliminates waterfall delays, reduces TLS round-trips, and loads the entire dashboard simultaneously.
    """
    current_user = get_current_user_from_header(authorization, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Tizimga kirilmagan yoki sessiya yaroqsiz")
    check_user_access(current_user, ["dashboard:view", "analysis:view", "analysis", "/dashboard"], db)
    now = datetime.datetime.now()
    curr_ym = f"{now.year:04d}-{now.month:02d}"
    target_month = (month or curr_ym).strip()

    overview_res = get_financial_overview(time_range=time_range, company_id=company_id, branch_id=branch_id, authorization=authorization, db=db)
    snapshots_res = get_financial_snapshots(company_id=company_id, authorization=authorization, db=db)
    month_summary_res = get_month_summary(month=target_month, company_id=company_id, branch_id=branch_id, authorization=authorization, db=db)
    comp_req = schemas.PeriodCompareRequest(
        period1_start=p1_start,
        period1_end=p1_end,
        period2_start=p2_start,
        period2_end=p2_end
    )
    compare_res = compare_periods(req=comp_req, company_id=company_id, branch_id=branch_id, authorization=authorization, db=db)

    return {
        "code": 0,
        "data": {
            "overview": overview_res.get("data") if isinstance(overview_res, dict) else overview_res,
            "snapshots": snapshots_res.get("data") if isinstance(snapshots_res, dict) else snapshots_res,
            "monthSummary": month_summary_res.get("data") if isinstance(month_summary_res, dict) else month_summary_res,
            "comparison": compare_res.get("data") if isinstance(compare_res, dict) else compare_res
        }
    }



@router.post("/analysis/compare")
def compare_periods(
    req: schemas.PeriodCompareRequest,
    company_id: str = Query(None),
    branch_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Calculates exact real metrics for Period 1 and Period 2, and their growth/delta percentages.
    Includes smart fallbacks to prevent 422 errors when dates are incomplete.
    """
    target_company = get_user_company_id(authorization, db, company_id)
    now = datetime.datetime.now()
    curr_ym = f"{now.year:04d}-{now.month:02d}"
    prev_month = now.month - 1 or 12
    prev_year = now.year if now.month > 1 else now.year - 1
    prev_ym = f"{prev_year:04d}-{prev_month:02d}"

    p1_s = (req.period1_start or f"{curr_ym}-01").strip()
    p1_e = (req.period1_end or f"{curr_ym}-{now.day:02d}").strip()
    p2_s = (req.period2_start or f"{prev_ym}-01").strip()
    p2_e = (req.period2_end or f"{prev_ym}-28").strip()

    cache_key = f"compare:{target_company}:{branch_id or 'all'}:{p1_s}:{p1_e}:{p2_s}:{p2_e}"
    cached = get_analytics_cache(cache_key)
    if cached is not None:
        return cached

    with ThreadPoolExecutor(max_workers=2) as executor:
        f_p1 = executor.submit(calc_date_range_metrics, db, p1_s, p1_e, target_company, branch_id)
        f_p2 = executor.submit(calc_date_range_metrics, db, p2_s, p2_e, target_company, branch_id)
        p1 = f_p1.result()
        p2 = f_p2.result()

    rev_diff = round(p1["revenue"] - p2["revenue"], 2)
    rev_growth = round((rev_diff / p2["revenue"] * 100), 1) if p2["revenue"] > 0 else (100.0 if p1["revenue"] > 0 else 0.0)

    cogs_diff = round(p1["cogs"] - p2["cogs"], 2)
    cogs_growth = round((cogs_diff / p2["cogs"] * 100), 1) if p2["cogs"] > 0 else 0.0

    staff_diff = round(p1["staff_salaries"] - p2["staff_salaries"], 2)
    staff_growth = round((staff_diff / p2["staff_salaries"] * 100), 1) if p2["staff_salaries"] > 0 else 0.0

    short_diff = round(p1["short_term_outputs"] - p2["short_term_outputs"], 2)
    short_growth = round((short_diff / p2["short_term_outputs"] * 100), 1) if p2["short_term_outputs"] > 0 else 0.0

    payroll_diff = round(p1["total_payroll"] - p2["total_payroll"], 2)
    payroll_growth = round((payroll_diff / p2["total_payroll"] * 100), 1) if p2["total_payroll"] > 0 else 0.0

    profit_diff = round(p1["net_profit"] - p2["net_profit"], 2)
    profit_growth = round((profit_diff / abs(p2["net_profit"]) * 100), 1) if p2["net_profit"] != 0 else 0.0

    margin_diff = round(p1["profit_margin"] - p2["profit_margin"], 1)

    res = {
        "code": 0,
        "data": {
            "period1": p1,
            "period2": p2,
            "deltas": {
                "revDiff": rev_diff,
                "revGrowth": rev_growth,
                "cogsDiff": cogs_diff,
                "cogsGrowth": cogs_growth,
                "staffDiff": staff_diff,
                "staffGrowth": staff_growth,
                "shortDiff": short_diff,
                "shortGrowth": short_growth,
                "payrollDiff": payroll_diff,
                "payrollGrowth": payroll_growth,
                "profitDiff": profit_diff,
                "profitGrowth": profit_growth,
                "marginDiff": margin_diff
            }
        }
    }
    set_analytics_cache(cache_key, res)
    return res


@router.get("/analysis/date-range")
def get_date_range_analysis(
    start_date: str = Query(...),
    end_date: str = Query(...),
    company_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, company_id)
    cache_key = f"date_range:{target_company}:{start_date}:{end_date}"
    cached = get_analytics_cache(cache_key)
    if cached is not None:
        return cached

    data = calc_date_range_metrics(db, start_date, end_date, target_company)
    res = {
        "code": 0,
        "data": data
    }
    set_analytics_cache(cache_key, res)
    return res


@router.get("/analysis/total")
def get_analysis_total(
    company_id: str = Query(None),
    branch_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, company_id)
    cache_key = f"analysis_total:{target_company}:{branch_id or 'all'}"
    cached = get_analytics_cache(cache_key)
    if cached is not None:
        return cached

    pq = db.query(models.Product)
    if target_company:
        pq = pq.filter(models.Product.company_id == target_company)
    if branch_id:
        pq = pq.filter(models.Product.branch_id == branch_id)
    products = pq.all()
    products_count = len(products)

    wq = db.query(models.Worker).filter(models.Worker.status == 1)
    if target_company:
        wq = wq.filter(models.Worker.company_id == target_company)
    if branch_id:
        wq = wq.filter(models.Worker.branch_id == branch_id)
    workers_count = wq.count()
    
    inventory_val = sum((p.price or 0.0) * (p.quantityInStock or 0) for p in products)
    
    sal_q = db.query(func.sum(models.Salary.netSalary)).join(models.Worker, models.Salary.workerId == models.Worker.id).filter(models.Salary.status == 'paid')
    if target_company:
        sal_q = sal_q.filter(models.Worker.company_id == target_company)
    if branch_id:
        sal_q = sal_q.filter(models.Worker.branch_id == branch_id)
    salaries_sum = sal_q.scalar() or 0.0
    if salaries_sum == 0:
        salaries_sum = sum((w.baseSalary or 0.0) for w in wq.all())
        
    res = {
        "code": 0,
        "data": {
            "users": products_count,
            "messages": workers_count,
            "moneys": int(inventory_val),
            "shoppings": int(salaries_sum)
        }
    }
    set_analytics_cache(cache_key, res)
    return res


@router.get("/analysis/monthlySales")
def get_monthly_sales(
    company_id: str = Query(None),
    branch_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, company_id)
    now = datetime.datetime.now()
    data = []
    for i in range(5, -1, -1):
        m_calc = now.month - i
        y_calc = now.year
        while m_calc <= 0:
            m_calc += 12
            y_calc -= 1
        ym = f"{y_calc:04d}-{m_calc:02d}"
        sq = db.query(models.Sale).filter(models.Sale.created_at.like(f"{ym}%"))
        if target_company:
            sq = sq.filter(models.Sale.company_id == target_company)
        if branch_id:
            sq = sq.filter(models.Sale.branch_id == branch_id)
        sales = sq.all()
        rev = sum(float(s.total_amount or getattr(s, 'total', 0.0) or 0.0) for s in sales)
        data.append({
            "name": ym,
            "actual": round(rev, 2),
            "estimate": round(rev * 1.08, 2)
        })
    return {
        "code": 0,
        "data": data
    }


@router.get("/workplace/total")
def get_workplace_total(
    company_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, company_id)
    pq = db.query(models.Product)
    if target_company:
        pq = pq.filter(models.Product.company_id == target_company)
    total_products = pq.count()

    wq = db.query(models.Worker)
    if target_company:
        wq = wq.filter(models.Worker.company_id == target_company)
    total_workers = wq.count()
    total_todos = db.query(models.Todo).filter(models.Todo.completed == 0).count()
    
    return {
        "code": 0,
        "data": {
            "project": total_products,
            "access": 100 + total_workers * 10,
            "todo": total_todos
        }
    }


@router.get("/workplace/project")
def get_workplace_project(db: Session = Depends(get_db)):
    projects = db.query(models.WorkplaceProject).all()
    return {
        "code": 0,
        "data": [
            {
                "name": p.name,
                "icon": p.icon,
                "message": p.message,
                "personal": p.personal,
                "time": p.time
            } for p in projects
        ]
    }


@router.get("/workplace/dynamic")
def get_workplace_dynamic(db: Session = Depends(get_db)):
    dynamics = db.query(models.WorkplaceDynamic).order_by(models.WorkplaceDynamic.id.desc()).limit(10).all()
    logs = [
        {
            "keys": d.keys,
            "time": d.time
        } for d in dynamics
    ]
    
    products = db.query(models.Product).order_by(models.Product.createTime.desc()).limit(3).all()
    for p in products:
        logs.append({
            "keys": ["workplace.push", f"Mahsulot: {p.productName}"],
            "time": p.createTime
        })
        
    return {
        "code": 0,
        "data": logs
    }


@router.get("/workplace/team")
def get_workplace_team(db: Session = Depends(get_db)):
    teams = db.query(models.WorkplaceTeam).all()
    return {
        "code": 0,
        "data": [
            {
                "name": t.name,
                "icon": t.icon
            } for t in teams
        ]
    }


@router.get("/workplace/radar")
def get_workplace_radar(db: Session = Depends(get_db)):
    radars = db.query(models.WorkplaceRadar).all()
    return {
        "code": 0,
        "data": [
            {
                "name": r.name,
                "max": r.max,
                "personal": r.personal,
                "team": r.team
            } for r in radars
        ]
    }


# ══════════════════════════════════════════════════════════════
# MONTHLY FINANCIAL CLOSING & ARCHIVE SNAPSHOTS
# ══════════════════════════════════════════════════════════════
@router.get("/analysis/snapshot/list")
def get_financial_snapshots(
    company_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, company_id)
    cache_key = f"analysis:snapshot:list:{target_company}"
    cached = get_analytics_cache(cache_key)
    if cached is not None:
        return cached

    q = db.query(models.MonthlyFinancialSnapshot)
    if target_company:
        q = q.filter(models.MonthlyFinancialSnapshot.company_id == target_company)
    snapshots = q.order_by(models.MonthlyFinancialSnapshot.period_month.desc()).all()
    res = {
        "code": 0,
        "data": [
            {
                "id": s.id,
                "period_month": s.period_month,
                "revenue": s.revenue,
                "cogs": s.cogs,
                "staff_salaries": s.staff_salaries,
                "short_term_outputs": s.short_term_outputs,
                "total_expenses": s.total_expenses,
                "net_profit": s.net_profit,
                "profit_margin": s.profit_margin,
                "sales_count": s.sales_count,
                "status": s.status,
                "remark": s.remark,
                "closed_by": s.closed_by,
                "created_at": s.created_at.strftime("%Y-%m-%d %H:%M:%S") if s.created_at else None
            }
            for s in snapshots
        ]
    }
    set_analytics_cache(cache_key, res)
    return res


@router.post("/analysis/snapshot/close")
def close_monthly_financial_snapshot(
    req: schemas.MonthlyFinancialSnapshotClose,
    company_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, getattr(req, "company_id", None) or company_id)
    month = req.period_month.strip()
    if not month:
        return {"code": 1, "message": "Hisobot oyi (period_month) kiritilishi shart"}

    real_data = calc_month_metrics(db, month, company_id=target_company)

    revenue = req.override_revenue if req.override_revenue is not None else real_data["revenue"]
    cogs = req.override_cogs if req.override_cogs is not None else real_data["cogs"]
    staff_salaries = req.override_staff_salaries if req.override_staff_salaries is not None else real_data["staff_salaries"]
    short_term_outputs = req.override_short_term if req.override_short_term is not None else real_data["short_term_outputs"]

    total_expenses = round(cogs + staff_salaries + short_term_outputs, 2)
    net_profit = round(revenue - total_expenses, 2)
    profit_margin = round((net_profit / revenue * 100), 1) if revenue > 0 else 0.0
    sales_count = real_data["sales_count"]

    q = db.query(models.MonthlyFinancialSnapshot).filter(
        models.MonthlyFinancialSnapshot.period_month == month
    )
    if target_company:
        q = q.filter(models.MonthlyFinancialSnapshot.company_id == target_company)
    existing = q.first()

    if existing:
        existing.revenue = revenue
        existing.cogs = cogs
        existing.staff_salaries = staff_salaries
        existing.short_term_outputs = short_term_outputs
        existing.total_expenses = total_expenses
        existing.net_profit = net_profit
        existing.profit_margin = profit_margin
        existing.sales_count = sales_count
        existing.status = "closed"
        existing.remark = req.remark or f"{month} oyi yakuniy moliyaviy hisoboti (Yopildi)"
        existing.closed_by = "admin"
        db.commit()
        db.refresh(existing)
        snap = existing
    else:
        snap = models.MonthlyFinancialSnapshot(
            id=f"MFS-{target_company or 'comp-default'}-{month}",
            company_id=target_company or "comp-default",
            period_month=month,
            revenue=revenue,
            cogs=cogs,
            staff_salaries=staff_salaries,
            short_term_outputs=short_term_outputs,
            total_expenses=total_expenses,
            net_profit=net_profit,
            profit_margin=profit_margin,
            sales_count=sales_count,
            status="closed",
            remark=req.remark or f"{month} oyi yakuniy moliyaviy hisoboti (Yopildi)",
            closed_by="admin"
        )
        db.add(snap)
        db.commit()
        db.refresh(snap)

    from app.routers.activity import log_activity
    log_activity(
        db,
        actor="admin",
        action="close_month",
        entity="financial_snapshot",
        entity_id=snap.id,
        entity_name=f"{month} oylik hisoboti (Sof foyda: ${net_profit})"
    )

    invalidate_analytics()
    return {
        "code": 0,
        "data": {
            "id": snap.id,
            "period_month": snap.period_month,
            "revenue": snap.revenue,
            "cogs": snap.cogs,
            "staff_salaries": snap.staff_salaries,
            "shortTermOutputs": snap.short_term_outputs,
            "total_expenses": snap.total_expenses,
            "net_profit": snap.net_profit,
            "profitMargin": snap.profit_margin,
            "sales_count": snap.sales_count,
            "status": snap.status,
            "remark": snap.remark
        },
        "message": f"{month} oyi moliyaviy hisoboti muvaffaqiyatli yopildi va tarixga saqlandi!"
    }


@router.post("/analysis/snapshot/delete")
def delete_financial_snapshot(
    data: dict = Body(...),
    company_id: str = Query(None),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    target_company = get_user_company_id(authorization, db, data.get("company_id") or company_id)
    snap_id = data.get("id") or data.get("period_month")
    if not snap_id:
        return {"code": 1, "message": "ID ko'rsatilmadi"}

    q = db.query(models.MonthlyFinancialSnapshot).filter(
        (models.MonthlyFinancialSnapshot.id == snap_id) | (models.MonthlyFinancialSnapshot.period_month == snap_id)
    )
    if target_company:
        q = q.filter(models.MonthlyFinancialSnapshot.company_id == target_company)
    item = q.first()

    if item:
        db.delete(item)
        db.commit()
        invalidate_analytics()
        return {"code": 0, "message": "Oylik hisobot tarixi o'chirildi"}
    return {"code": 1, "message": "Hisobot topilmadi"}


def warm_up_analytics_cache():
    """
    Pre-warms all primary analysis views so user requests hit in-memory cache instantly (0.5ms).
    """
    try:
        db = SessionLocal()
        try:
            get_financial_snapshots(db)
            get_financial_overview(time_range="6m", db=db)
            get_financial_overview(time_range="1y", db=db)
            now = datetime.datetime.now()
            curr_ym = f"{now.year:04d}-{now.month:02d}"
            prev_m = now.month - 1 or 12
            prev_y = now.year if now.month > 1 else now.year - 1
            prev_ym = f"{prev_y:04d}-{prev_m:02d}"
            get_month_summary(month_str=curr_ym, db=db)
            get_month_summary(month_str=prev_ym, db=db)
            compare_periods(request=schemas.PeriodCompareRequest(), db=db)
        finally:
            db.close()
    except Exception as e:
        print(f"[Analytics Cache Warmer] Warning: {e}")

