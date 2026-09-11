import datetime
import random
import uuid
from app.database import SessionLocal
from app import models

def generate_dump():
    db = SessionLocal()
    try:
        print("--- Seeding Products ---")
        products_data = [
            # Erkaklar kiyimlari
            ("PROD-001", "Klassik Paxtali Erkaklar Ko'ylagi", "MSHIRT-001", "Erkaklar kiyimlari", 28.0, 14.0, 180.0, "8601001"),
            ("PROD-002", "Erkaklar Slim-Fit Jinsi Shimi", "MPANTS-002", "Erkaklar kiyimlari", 38.0, 19.0, 140.0, "8601002"),
            ("PROD-003", "Premium Trikotaj Polo Futbolka", "MPOLO-003", "Erkaklar kiyimlari", 22.0, 10.0, 220.0, "8601003"),
            ("PROD-004", "Kuzgi Bomber Kurtka", "MJACKET-004", "Erkaklar kiyimlari", 65.0, 32.0, 90.0, "8601004"),
            # Ayollar kiyimlari
            ("PROD-005", "Elegant Ipak Ko'ylak", "WDRESS-005", "Ayollar kiyimlari", 55.0, 26.0, 110.0, "8601005"),
            ("PROD-006", "Ayollar Yumshoq Kardigani", "WCARD-006", "Ayollar kiyimlari", 36.0, 17.0, 130.0, "8601006"),
            ("PROD-007", "Klassik Ofis Yubkasi", "WSKIRT-007", "Ayollar kiyimlari", 26.0, 12.0, 150.0, "8601007"),
            ("PROD-008", "Paxtali Kundalik Bluzka", "WBLOUSE-008", "Ayollar kiyimlari", 24.0, 11.0, 170.0, "8601008"),
            # Bolalar kiyimlari
            ("PROD-009", "Bolalar Sport Kostyumi", "KTRACK-009", "Bolalar kiyimlari", 30.0, 14.0, 160.0, "8601009"),
            ("PROD-010", "Rang-barang Bolalar Futbolkasi", "KTSHIRT-010", "Bolalar kiyimlari", 12.0, 5.5, 280.0, "8601010"),
            # Uy to'qimachiligi
            ("PROD-011", "Premium Satin Yotoq To'plami", "HBED-011", "Uy to'qimachiligi", 75.0, 36.0, 85.0, "8601011"),
            ("PROD-012", "Maxrovy Sochiqlar To'plami", "HTOWEL-012", "Uy to'qimachiligi", 22.0, 9.5, 210.0, "8601012"),
            # Aksessuarlar
            ("PROD-013", "Tabiiy Jun Sharf va Shapka", "ASCARF-013", "Aksessuarlar", 18.0, 8.0, 200.0, "8601013"),
            ("PROD-014", "Klassik Charm Kamar", "ABELT-014", "Aksessuarlar", 16.0, 7.0, 240.0, "8601014"),
        ]

        products_map = {}
        for pid, name, sku, cat, price, cost, qty, barcode in products_data:
            prod = db.query(models.Product).filter(models.Product.id == pid).first()
            if not prod:
                prod = models.Product(
                    id=pid,
                    productName=name,
                    SKU=sku,
                    category=cat,
                    price=price,
                    cost=cost,
                    quantityInStock=qty,
                    status=1,
                    shtrix_code=barcode,
                    unit="dona",
                    createTime="2025-09-01 10:00:00"
                )
                db.add(prod)
            else:
                prod.productName = name
                prod.category = cat
                prod.price = price
                prod.cost = cost
                prod.quantityInStock = qty
            products_map[pid] = prod
        db.commit()
        print(f"Seeded/Updated {len(products_data)} products.")

        print("--- Seeding Additional Workers ---")
        workers_data = [
            ("WORK-004", "Shahlo Karimova", "shahlok", "shahlo@example.com", "+998901112233", "Bichuv va tikuv ustasi", "DEPT-PD", "2024-01-10", 3200.0),
            ("WORK-005", "Muzaffar Jo'rayev", "muzaffarj", "muzaffar@example.com", "+998912223344", "Katta Bichuvchi", "DEPT-PD", "2024-02-15", 2800.0),
            ("WORK-006", "Nodira Qosimova", "nodiraq", "nodira@example.com", "+998933334455", "Sifat Nazoratchisi", "DEPT-PD", "2024-03-01", 2200.0),
            ("WORK-007", "Rustam Mahmudov", "rustamm", "rustam@example.com", "+998944445566", "Omborxona Mudiri", "DEPT-HQ", "2023-11-20", 2500.0),
            ("WORK-008", "Fotima Umarova", "fotimau", "fotima@example.com", "+998955556677", "Tikuvchi", "DEPT-PD", "2024-04-05", 2400.0),
            ("WORK-009", "Ulug'bek Nazarov", "ulugbekn", "ulugbek@example.com", "+998977778899", "Kassa va Sotuv Menedjeri", "DEPT-SL", "2024-01-05", 2600.0),
        ]
        all_workers = db.query(models.Worker).all()
        existing_wids = {w.id for w in all_workers}
        for wid, name, acc, email, phone, role, dept, hire, salary in workers_data:
            if wid not in existing_wids:
                w = models.Worker(
                    id=wid,
                    name=name,
                    account=acc,
                    email=email,
                    phone=phone,
                    role=role,
                    departmentId=dept,
                    hireDate=hire,
                    status=1,
                    baseSalary=salary,
                    remark="Malakali xodim"
                )
                db.add(w)
                all_workers.append(w)
        db.commit()
        print(f"Total active workers: {len(all_workers)}")

        # Months to seed data for: Oct 2025 through Sep 2026
        months_list = [
            "2025-10", "2025-11", "2025-12",
            "2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06",
            "2026-07", "2026-08", "2026-09"
        ]

        print("--- Seeding Paid Salaries ---")
        db.query(models.Salary).delete()
        db.commit()

        salary_count = 0
        for m in months_list:
            pay_day = f"{m}-05"
            for w in all_workers:
                base = w.baseSalary or 2500.0
                allowance = 150.0 if random.random() > 0.5 else 0.0
                deduction = 50.0 if random.random() > 0.7 else 0.0
                net = base + allowance - deduction
                sal = models.Salary(
                    id=f"SAL-{m}-{w.id}",
                    workerId=w.id,
                    baseSalary=base,
                    allowance=allowance,
                    deduction=deduction,
                    netSalary=net,
                    payDate=pay_day,
                    status="paid",
                    remark=f"{m} oyi maoshi ({w.name})"
                )
                db.add(sal)
                salary_count += 1
        db.commit()
        print(f"Seeded {salary_count} salary records across {len(months_list)} months.")

        print("--- Seeding Staff Outputs (Piecework / Vyrabotka) ---")
        db.query(models.StaffOutput).delete()
        db.commit()

        output_tasks = [
            ("Ko'ylak bichish va andaza tayyorlash", 320.0),
            ("Shim detallarini yig'ish va tikish", 450.0),
            ("Trikotaj yoqalarini tikish", 280.0),
            ("Tugma qadash va tugma ilmog'i ochish", 190.0),
            ("Dazmollash va qadoqlash", 240.0),
            ("Maxsus kashta tikish ishlari", 380.0),
            ("Sifat nazorati va saralash", 210.0),
        ]

        output_count = 0
        for m in months_list:
            for task_name, base_amount in output_tasks:
                amt = base_amount * random.uniform(0.85, 1.25)
                out_date = f"{m}-{random.randint(10, 25):02d}"
                so = models.StaffOutput(
                    id=f"OUT-{uuid.uuid4().hex[:8]}",
                    workerId="WORK-004",
                    workerName="Shahlo Karimova",
                    name=task_name,
                    amount=round(amt, 2),
                    period_month=out_date,
                    comment=f"{m} oylik reja bo'yicha ishlab chiqarish topshirig'i",
                    createTime=f"{out_date} 15:30:00"
                )
                db.add(so)
                output_count += 1
        db.commit()
        print(f"Seeded {output_count} staff outputs across {len(months_list)} months.")

        print("--- Seeding Staff Adjustments (Advances & Bonuses) ---")
        db.query(models.StaffAdjustment).delete()
        db.commit()

        adj_count = 0
        for m in months_list:
            db.add(models.StaffAdjustment(
                id=f"ADJ-ADV-{m}",
                workerId="WORK-005",
                document_type="advance",
                amount=350.0,
                period_month=m,
                description=f"{m} oyi avans to'lovi",
                createTime=f"{m}-15 11:00:00"
            ))
            db.add(models.StaffAdjustment(
                id=f"ADJ-BON-{m}",
                workerId="WORK-006",
                document_type="bonus",
                amount=200.0,
                period_month=m,
                description=f"{m} oyi samarali mehnat bonusi",
                createTime=f"{m}-25 17:00:00"
            ))
            adj_count += 2
        db.commit()
        print(f"Seeded {adj_count} staff adjustments.")

        print("--- Seeding Sales & SaleItems ---")
        db.query(models.SaleItem).delete()
        db.query(models.Sale).delete()
        db.commit()

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

        all_prod_list = list(products_map.values())
        total_sales_created = 0
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

                sample_prods = random.sample(all_prod_list, random.randint(1, 3))
                sale_total = 0.0
                sale_items = []

                for p in sample_prods:
                    qty = random.randint(2, 10)
                    p_price = p.price
                    p_cost = p.cost
                    line_total = round(p_price * qty, 2)
                    sale_total += line_total

                    item = models.SaleItem(
                        id=f"ITEM-{uuid.uuid4().hex[:8]}",
                        sale_id=sale_id,
                        product_id=p.id,
                        product_name=p.productName,
                        shtrix_code=p.shtrix_code,
                        price=p_price,
                        cost=p_cost,
                        quantity=qty,
                        unit_name="dona",
                        conversion_factor=1.0,
                        total=line_total
                    )
                    sale_items.append(item)

                sale_total = round(sale_total, 2)
                paid = sale_total
                debt = 0.0
                if pay_method == "nasiya":
                    paid = round(sale_total * 0.3, 2)
                    debt = round(sale_total - paid, 2)

                sale = models.Sale(
                    id=sale_id,
                    receipt_number=receipt_no,
                    cashier_name="admin",
                    customer_name=cust_name,
                    customer_phone=cust_phone,
                    payment_method=pay_method,
                    total_amount=sale_total,
                    paid_amount=paid,
                    debt_amount=debt,
                    total_items=len(sale_items),
                    discount=0.0,
                    remark=f"Savdo cheki #{receipt_no}",
                    created_at=dt_str
                )
                sale.items = sale_items
                db.add(sale)
                total_sales_created += 1

        db.commit()
        print(f"Seeded {total_sales_created} sales with full item breakdowns!")

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

        print("=== Dump Data Generation Completed Successfully! ===")

    except Exception as e:
        db.rollback()
        print(f"Error during dump generation: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    generate_dump()
