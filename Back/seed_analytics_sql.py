import datetime
import random
import uuid
from app.database import SessionLocal
from sqlalchemy import text

def insert_items_and_snapshots():
    db = SessionLocal()
    try:
        # 1. Fetch pure tuples
        sale_ids = [row[0] for row in db.execute(text("SELECT id FROM sales")).fetchall()]
        print(f"Found {len(sale_ids)} sales.")
        if not sale_ids:
            print("No sales in DB!")
            return

        products = db.execute(text("SELECT id, \"productName\", price, cost, shtrix_code FROM products")).fetchall()
        print(f"Found {len(products)} products.")

        # 2. Clear old sale_items
        db.execute(text("DELETE FROM sale_items;"))
        db.commit()

        # 3. Generate multi-row SQL values
        values_sql = []
        for s_id in sale_ids:
            sample_prods = random.sample(products, random.randint(1, 3))
            for p_id, p_name, price, cost, barcode in sample_prods:
                qty = float(random.randint(2, 8))
                price = float(price or 25.0)
                cost = float(cost or 12.0)
                line_total = round(price * qty, 2)
                item_id = f"ITEM-{uuid.uuid4().hex[:10]}"
                clean_name = str(p_name).replace("'", "''")
                clean_barcode = str(barcode or '')
                values_sql.append(
                    f"('{item_id}', '{s_id}', '{p_id}', '{clean_name}', '{clean_barcode}', {price}, {cost}, {qty}, 'dona', 1.0, {line_total})"
                )

        print(f"Generated {len(values_sql)} sale items. Executing multi-row SQL INSERT...")
        chunk_size = 150
        for i in range(0, len(values_sql), chunk_size):
            chunk = values_sql[i:i + chunk_size]
            sql = (
                "INSERT INTO sale_items (id, sale_id, product_id, product_name, shtrix_code, price, cost, quantity, unit_name, conversion_factor, total) VALUES "
                + ", ".join(chunk)
                + ";"
            )
            db.execute(text(sql))
            db.commit()
            print(f"Inserted chunk {i} to {i + len(chunk)}...")

        # 4. Snapshots for 2026-06 and 2026-07
        print("Seeding Snapshots...")
        db.execute(text("DELETE FROM monthly_financial_snapshots;"))
        db.commit()

        snap_06_sql = """
        INSERT INTO monthly_financial_snapshots (
            id, period_month, revenue, cogs, staff_salaries, short_term_outputs, total_expenses, net_profit, profit_margin, sales_count, status, remark, closed_by, created_at, updated_at
        ) VALUES (
            'MFS-2026-06', '2026-06', 22450.00, 11225.00, 4800.00, 1850.00, 17875.00, 4575.00, 20.4, 25, 'closed', '2026-06 oyi yakuniy moliyaviy hisoboti (Yopildi)', 'admin', '2026-07-01 10:00:00', '2026-07-01 10:00:00'
        );
        """
        db.execute(text(snap_06_sql))

        snap_07_sql = """
        INSERT INTO monthly_financial_snapshots (
            id, period_month, revenue, cogs, staff_salaries, short_term_outputs, total_expenses, net_profit, profit_margin, sales_count, status, remark, closed_by, created_at, updated_at
        ) VALUES (
            'MFS-2026-07', '2026-07', 25800.00, 12900.00, 4800.00, 2100.00, 19800.00, 6000.00, 23.3, 28, 'closed', '2026-07 oyi yakuniy moliyaviy hisoboti (Yopildi)', 'admin', '2026-08-01 10:00:00', '2026-08-01 10:00:00'
        );
        """
        db.execute(text(snap_07_sql))
        db.commit()

        total_sales = db.execute(text("SELECT count(*) FROM sales")).scalar()
        total_items = db.execute(text("SELECT count(*) FROM sale_items")).scalar()
        total_snaps = db.execute(text("SELECT count(*) FROM monthly_financial_snapshots")).scalar()
        print("=== COMPLETED IN UNDER 2 SECONDS! ===")
        print(f"Total Sales: {total_sales}")
        print(f"Total Sale Items: {total_items}")
        print(f"Total Snapshots: {total_snaps}")

    except Exception as e:
        db.rollback()
        print("Error during fast SQL insert:", e)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    insert_items_and_snapshots()
