import os
import glob
import re
import sqlite3
import openpyxl

DB_PATH = os.path.join(os.path.dirname(__file__), "erp.db")

def clean_brand(val):
    if not val:
        return None
    val = str(val).strip()
    if val == "---" or "---" in val:
        return None
    m = re.match(r"^\d+-(.+)$", val)
    if m:
        brand = m.group(1).strip()
        return brand if brand and brand != "---" else None
    return val if val != "---" else None

def clean_str(val):
    if not val:
        return None
    val = str(val).strip()
    return None if (val == "---" or val == "") else val

def import_all_classifiers():
    print("=========================================")
    print("Starting Classifier Excel Files Import...")
    print("=========================================")
    
    files = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "classifier*.xlsx")))
    if not files:
        # Also check Downloads folder if not in Back folder
        files = sorted(glob.glob("/home/xasanboy/Downloads/classifier*.xlsx"))

    print(f"Found {len(files)} classifier files to process:")
    for f in files:
        print(f"  - {os.path.basename(f)}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classifier_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT,
            class_name TEXT,
            position_name TEXT,
            subposition_name TEXT,
            brand_name TEXT,
            attribute_name TEXT,
            mxik_code TEXT,
            mxik_name TEXT,
            shtrix_code TEXT,
            unit_group TEXT,
            unit TEXT,
            package_unit TEXT,
            source_file TEXT
        )
    """)

    # Create indexes for fast search
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_classifier_mxik ON classifier_items (mxik_code)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_classifier_shtrix ON classifier_items (shtrix_code)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_classifier_brand ON classifier_items (brand_name)")

    # Clear existing data before re-seeding classifier items
    cursor.execute("DELETE FROM classifier_items")
    conn.commit()

    total_inserted = 0
    batch_size = 10000

    for file_path in files:
        file_name = os.path.basename(file_path)
        print(f"\nProcessing file: {file_name} ...")
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        sheet = wb.active

        batch = []
        file_count = 0

        for i, row in enumerate(sheet.iter_rows(values_only=True)):
            if i < 2:  # Skip headers (Row 1 & Row 2)
                continue

            group_name = clean_str(row[0] if len(row) > 0 else None)
            class_name = clean_str(row[1] if len(row) > 1 else None)
            position_name = clean_str(row[2] if len(row) > 2 else None)
            subposition_name = clean_str(row[3] if len(row) > 3 else None)
            brand_name = clean_brand(row[4] if len(row) > 4 else None)
            attribute_name = clean_str(row[5] if len(row) > 5 else None)
            mxik_code = clean_str(row[6] if len(row) > 6 else None)
            mxik_name = clean_str(row[7] if len(row) > 7 else None)
            shtrix_code = clean_str(row[8] if len(row) > 8 else None)
            unit_group = clean_str(row[9] if len(row) > 9 else None)
            unit = clean_str(row[10] if len(row) > 10 else None)
            package_unit = clean_str(row[11] if len(row) > 11 else None)

            batch.append((
                group_name,
                class_name,
                position_name,
                subposition_name,
                brand_name,
                attribute_name,
                mxik_code,
                mxik_name,
                shtrix_code,
                unit_group,
                unit,
                package_unit,
                file_name
            ))

            file_count += 1

            if len(batch) >= batch_size:
                cursor.executemany("""
                    INSERT INTO classifier_items (
                        group_name, class_name, position_name, subposition_name,
                        brand_name, attribute_name, mxik_code, mxik_name,
                        shtrix_code, unit_group, unit, package_unit, source_file
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, batch)
                conn.commit()
                batch.clear()

        if batch:
            cursor.executemany("""
                INSERT INTO classifier_items (
                    group_name, class_name, position_name, subposition_name,
                    brand_name, attribute_name, mxik_code, mxik_name,
                    shtrix_code, unit_group, unit, package_unit, source_file
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch)
            conn.commit()
            batch.clear()

        total_inserted += file_count
        print(f"  -> Imported {file_count} items from {file_name}")

    conn.close()
    print("=========================================")
    print(f"Classifier Import Complete! Total Records: {total_inserted}")
    print("=========================================")

if __name__ == "__main__":
    import_all_classifiers()
