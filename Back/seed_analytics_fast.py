import datetime
import random
import uuid
from app.database import SessionLocal
from app import models
from sqlalchemy import text

def fast_seed_sales():
    db = SessionLocal()
    try:
        print("Clearing old sales and items...")
        db.execute(text("DELETE FROM sale_items;"))
        db.execute(text("DELETE FROM sales;"))
        db.commit()

        products = db.query(models.Product).all()
        if not products:
            print("No products found! Please check products table.")
            return

        customers = [
            ("Olimjon Rahimov", "+998901234567"),
            ("Ziyoda Karimova", "+998912345678"),
            ("Textile Trade MCHJ", "+998712001122"),
            ("Shohruh Mirzayev", "+998933331122"),
            ("Nodira Yusupova", "+998944445566"),
            ("Moda Dunyosi Savdo", "+998977771100"),
            ("Bekzod To'rayev", "+998909876543"),
            ("Shahnoza Ergasheva", "+998918765432"),
            ("Silk Road Textile", "+998712998877"),
            ("Hamidulla Umarov", "+998951112233"),
            ("Farida Alimova", "+998935558899"),
            ("Bobur Ismoilov", "+998903337711")
        ]

        payment_methods = ["naqd", "naqd", "karta", "karta", "otkazma", "nasiya"]

        sales_distribution = {
            "2025-10": (8, 31),
            "2025-11": (9, 30),
            "2025-12": (14, 31),
            "2026-01": (10, 31),
            "2026-02": (12, 28),
            "2026-03": (16, 31),
            "2026-04": (18, 30),
            "2026-05": (22, 31),
            "2026-06": (25, 30),
            "2026-07": (28, 31),
            "2026-08": (38, 31),
            "2026-09": (26, 11),  # September up to Sep 11
        }

        sales_records = []
        items_records = []
        receipt_counter = 1001

        for month, (count, max_day) in sales_distribution.items():
            for i in range(count):
                day = min(max_day, 1 + int((i / max(1, count - 1)) * (max_day - 1))) if count > 1 else 1
                hour = random.randint(9, 19)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                dt_str = f"{month}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

                cust_name, cust_phone = random.choice(customers)
                pay_method = random.choice(payment_methods)

                sale_id = f"SALE-{month.replace('-', '')}-{receipt_counter}"
                receipt_no = f"CHK-{month.replace('-', '')}-{receipt_counter:04d}"
                receipt_counter += 1

                sample_prods = random.sample(products, random.randint(1, 3))
                sale_total = 0.0
                curr_sale_items = []

                for p in sample_prods:
                    qty = float(random.randint(2, 10))
                    p_price = float(p.price)
                    p_cost = float(p.cost)
                    line_total = round(p_price * qty, 2)
                    sale_total += line_total

                    curr_sale_items.append({
                        "id": f"ITEM-{uuid.uuid4().hex[:8]}",
                        "sale_id": sale_id,
                        "product_id": p.id,
                        "product_name": p.productName,
                        "shtrix_code": p.shtrix_code,
                        "price": p_price,
                        "cost": p_cost,
                        "quantity": qty,
                        "unit_name": "dona",
                        "conversion_factor": 1.0,
                        "total": line_total
                    })

                sale_total = round(sale_total, 2)
                paid = sale_total
                debt = 0.0
                if pay_method == "nasiya":
                    paid = round(sale_total * 0.3, 2)
                    debt = round(sale_total - paid, 2)

                sales_records.append({
                    "id": sale_id,
                    "receipt_number": receipt_no,
                    "cashier_name": "admin",
                    "customer_name": cust_name,
                    "customer_phone": cust_phone,
                    "payment_method": pay_method,
                    "total_amount": sale_total,
                    "paid_amount": paid,
                    "debt_amount": debt,
                    "total_items": len(curr_sale_items),
                    "discount": 0.0,
                    "remark": f"Savdo cheki #{receipt_no}",
                    "created_at": dt_str
                })
                items_records.extend(curr_sale_items)

        print(f"Bulk inserting {len(sales_records)} sales...")
        db.bulk_insert_mappings(models.Sale, sales_records)
        db.commit()

        print(f"Bulk inserting {len(items_records)} sale items...")
        db.bulk_insert_mappings(models.SaleItem, items_records)
        db.commit()

        print("--- Seeding Historical Financial Snapshots ---")
        db.query(models.MonthlyFinancialSnapshot).delete()
        db.commit()

        # Calculate exact numbers for 2026-06
        sales_06 = db.query(models.Sale).filter(models.Sale.created_at.like("2026-06%")).all()
        rev_06 = sum(s.total_amount for s in sales_06)
        cogs_06 = sum(sum(it.cost * it.quantity for it in s.items) for s in sales_06)
        sal_06 = sum(s.netSalary for s in db.query(models.Salary).filter(models.Salary.payDate.like("2026-06%")).all())
        out_06 = sum(o.amount for o in db.query(models.StaffOutput).filter(models.StaffOutput.createTime.like("2026-06%")).all())
        exp_06 = round(cogs_06 + sal_06 + out_06, 2)
        profit_06 = round(rev_06 - exp_06, 2)
        margin_06 = round((profit_06 / rev_06 * 100), 1) if rev_06 > 0 else 0.0

        snap_06 = models.MonthlyFinancialSnapshot(
            id="MFS-2026-06",
            period_month="2026-06",
            revenue=round(rev_06, 2),
            cogs=round(cogs_06, 2),
            staff_salaries=round(sal_06, 2),
            short_term_outputs=round(out_06, 2),
            total_expenses=exp_06,
            net_profit=profit_06,
            profit_margin=margin_06,
            sales_count=len(sales_06),
            status="closed",
            remark="2026-06 oyi yakuniy moliyaviy hisoboti (Yopildi)",
            closed_by="admin",
            created_at=datetime.datetime(2026, 7, 1, 10, 0, 0)
        )
        db.add(snap_06)

        # Calculate exact numbers for 2026-07
        sales_07 = db.query(models.Sale).filter(models.Sale.created_at.like("2026-07%")).all()
        rev_07 = sum(s.total_amount for s in sales_07)
        cogs_07 = sum(sum(it.cost * it.quantity for it in s.items) for s in sales_07)
        sal_07 = sum(s.netSalary for s in db.query(models.Salary).filter(models.Salary.payDate.like("2026-07%")).all())
        out_07 = sum(o.amount for o in db.query(models.StaffOutput).filter(models.StaffOutput.createTime.like("2026-07%")).all())
        exp_07 = round(cogs_07 + sal_07 + out_07, 2)
        profit_07 = round(rev_07 - exp_07, 2)
        margin_07 = round((profit_07 / rev_07 * 100), 1) if rev_07 > 0 else 0.0

        snap_07 = models.MonthlyFinancialSnapshot(
            id="MFS-2026-07",
            period_month="2026-07",
            revenue=round(rev_07, 2),
            cogs=round(cogs_07, 2),
            staff_salaries=round(sal_07, 2),
            short_term_outputs=round(out_07, 2),
            total_expenses=exp_07,
            net_profit=profit_07,
            profit_margin=margin_07,
            sales_count=len(sales_07),
            status="closed",
            remark="2026-07 oyi yakuniy moliyaviy hisoboti (Yopildi)",
            closed_by="admin",
            created_at=datetime.datetime(2026, 8, 1, 10, 0, 0)
        )
        db.add(snap_07)

        db.commit()
        print("Seeded historical snapshots for 2026-06 and 2026-07.")
        print(f"SUCCESS: Total sales: {db.query(models.Sale).count()}, Total items: {db.query(models.SaleItem).count()}")

    except Exception as e:
        db.rollback()
        print("Error during fast sales seed:", e)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fast_seed_sales()
