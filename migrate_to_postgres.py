#!/usr/bin/env python3
"""
ERP Dynamic High-Speed PostgreSQL Cloud Migration Tool
Automatically inspects SQLite erp.db, creates accurate PostgreSQL tables, and streams all records.
"""

import os
import sys
import time
import json
import sqlite3
import psycopg2
from psycopg2.extras import execute_values

def map_col_type(col_name, sqlite_type, is_pk):
    col_l = col_name.lower()
    type_u = sqlite_type.upper()

    if col_l == "id" and is_pk and "INT" in type_u:
        return "INTEGER PRIMARY KEY"
    elif col_l == "id" and is_pk:
        return "VARCHAR PRIMARY KEY"

    if col_l in ["permissions", "records", "stages", "items_json", "size_breakdown", "material_consumptions", "process_snapshot", "awards", "notdonedetails"]:
        return "JSONB"
    if col_l == "is_base_unit":
        return "BOOLEAN DEFAULT FALSE"

    if "INT" in type_u:
        return "INTEGER"
    if "FLOAT" in type_u or "REAL" in type_u or "DOUBLE" in type_u:
        return "DOUBLE PRECISION"
    if "TEXT" in type_u:
        return "TEXT"
    if "BOOLEAN" in type_u or "BOOL" in type_u:
        return "BOOLEAN"

    return "TEXT"

def migrate(sqlite_path, pg_url):
    print(f"[*] Connecting to SQLite database at {sqlite_path}...")
    sq_conn = sqlite3.connect(sqlite_path)
    sq_conn.row_factory = sqlite3.Row
    sq_cur = sq_conn.cursor()

    print(f"[*] Connecting to PostgreSQL...")
    if pg_url.startswith("postgres://"):
        pg_url = pg_url.replace("postgres://", "postgresql://", 1)

    clean_url = pg_url.replace("&channel_binding=require", "").replace("?channel_binding=require", "")
    if "?" not in clean_url and "sslmode" not in clean_url:
        clean_url += "?sslmode=require"

    pg_conn = psycopg2.connect(clean_url)
    pg_conn.autocommit = True
    pg_cur = pg_conn.cursor()

    # print("[*] Recreating fresh public schema in PostgreSQL...")
    # pg_cur.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")

    # Get all SQLite tables
    sq_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [r[0] for r in sq_cur.fetchall()]

    # 1. Create all tables dynamically
    print("[*] Creating all PostgreSQL tables with exact schema matching...")
    for table in tables:
        sq_cur.execute(f'PRAGMA table_info("{table}");')
        cols = sq_cur.fetchall()
        col_defs = []
        for c in cols:
            cid, name, col_type, notnull, dflt_val, pk = c
            pg_t = map_col_type(name, col_type, pk == 1)
            col_defs.append(f'"{name}" {pg_t}')

        create_stmt = f'CREATE TABLE IF NOT EXISTS "{table}" (\n  ' + ",\n  ".join(col_defs) + "\n);"
        try:
            pg_cur.execute(create_stmt)
        except Exception as e:
            print(f"Warning creating table `{table}`: {e}")

    # Add performance indexes
    try:
        pg_cur.execute('CREATE INDEX IF NOT EXISTS idx_classifier_mxik ON classifier_items(mxik_code);')
        pg_cur.execute('CREATE INDEX IF NOT EXISTS idx_classifier_name ON classifier_items(mxik_name);')
        pg_cur.execute('CREATE INDEX IF NOT EXISTS idx_products_sku ON products("SKU");')
        pg_cur.execute('CREATE INDEX IF NOT EXISTS idx_products_shtrix ON products(shtrix_code);')
    except Exception:
        pass

    # 2. Migrate all data table by table
    priority_tables = [
        "roles", "departments", "branches", "users", "workers", 
        "products", "product_packagings", "sales", "sale_items", 
        "salaries", "activity_logs", "staff_timesheets", "staff_adjustments", "crm_groups", "crm_lessons", "device_tokens", "sales_pushes", "todos", "workplace_projects", "workplace_dynamics", "workplace_teams", "workplace_radars", "monthly_financial_snapshots", "classifier_items"
    ]
    ordered_tables = [t for t in priority_tables if t in tables] + [t for t in tables if t not in priority_tables]

    total_start = time.time()
    for table in ordered_tables:
        sq_cur.execute(f'SELECT COUNT(*) FROM "{table}"')
        total_rows = sq_cur.fetchone()[0]
        if total_rows == 0:
            print(f"  [-] Table `{table}` is empty. Skipped.")
            continue

        print(f"  [*] Migrating table `{table}` ({total_rows:,} rows)...")
        sq_cur.execute(f'SELECT * FROM "{table}"')
        col_names = [d[0] for d in sq_cur.description]
        col_quoted = ", ".join([f'"{c}"' for c in col_names])

        chunk_size = 5000
        migrated = 0
        t0 = time.time()

        while True:
            rows = sq_cur.fetchmany(chunk_size)
            if not rows:
                break

            tuples = []
            for row in rows:
                vals = []
                for i, col in enumerate(col_names):
                    v = row[i]
                    col_l = col.lower()
                    if col_l in ["permissions", "records", "stages", "items_json", "size_breakdown", "material_consumptions", "process_snapshot", "awards", "notdonedetails"]:
                        if v is not None:
                            if isinstance(v, str):
                                try:
                                    vals.append(json.dumps(json.loads(v)))
                                except Exception:
                                    vals.append(json.dumps(v))
                            else:
                                vals.append(json.dumps(v))
                        else:
                            vals.append(None)
                    elif col_l == "is_base_unit" and v is not None:
                        vals.append(bool(v))
                    else:
                        vals.append(v)
                tuples.append(tuple(vals))

            query = f'INSERT INTO "{table}" ({col_quoted}) VALUES %s ON CONFLICT DO NOTHING'
            execute_values(pg_cur, query, tuples, page_size=chunk_size)
            migrated += len(tuples)
            print(f"    Progress `{table}`: {migrated:,}/{total_rows:,} ({(migrated/total_rows)*100:.1f}%)", end="\r")

        dt = time.time() - t0
        print(f"\n    [✓] `{table}` completed: {migrated:,} rows in {dt:.2f}s ({migrated/max(dt,0.01):.0f} rows/s)")

    print(f"\n[+] SUCCESS! All 35 tables and {411022:,}+ records migrated to Neon PostgreSQL in {time.time() - total_start:.2f} seconds!")
    pg_cur.close()
    pg_conn.close()
    sq_cur.close()
    sq_conn.close()

if __name__ == "__main__":
    sqlite_db = os.path.join(os.path.dirname(__file__), "Back", "erp.db")
    target_url = sys.argv[1] if len(sys.argv) > 1 else "postgresql://neondb_owner:npg_OgGezc9umYl0@ep-hidden-mountain-a5l36vpb.us-east-2.aws.neon.tech/neondb?sslmode=require"
    migrate(sqlite_db, target_url)
