#!/usr/bin/env python3
"""
ERP Database Migration & Cloud Export Tool
Migrates all tables, schemas, and records (including 411k+ classifier items)
from local SQLite (erp.db) to Cloud PostgreSQL (Neon, Supabase, Vercel Postgres, Railway).
"""

import os
import sys
import time
import json
import sqlite3
import argparse

def get_sqlite_conn(sqlite_path):
    if not os.path.exists(sqlite_path):
        raise FileNotFoundError(f"SQLite database not found at {sqlite_path}")
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    return conn

def export_to_sql_file(sqlite_path, output_sql_path):
    """Generate a clean PostgreSQL compatible SQL dump file."""
    print(f"[*] Exporting SQLite DB ({sqlite_path}) -> PostgreSQL Dump ({output_sql_path})...")
    conn = get_sqlite_conn(sqlite_path)
    cursor = conn.cursor()

    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [r[0] for r in cursor.fetchall()]

    with open(output_sql_path, "w", encoding="utf-8") as f:
        f.write("-- ERP PostgreSQL Production Dump\n")
        f.write("-- Generated for Cloud SQL / Vercel Postgres / Supabase / Neon\n\n")
        f.write("SET statement_timeout = 0;\n")
        f.write("SET lock_timeout = 0;\n")
        f.write("SET client_encoding = 'UTF8';\n")
        f.write("SET standard_conforming_strings = on;\n\n")

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM \"{table}\"")
            count = cursor.fetchone()[0]
            print(f"  Exporting table `{table}` ({count:,} rows)...")

            cursor.execute(f"SELECT * FROM \"{table}\"")
            rows = cursor.fetchall()
            if not rows:
                continue

            col_names = [d[0] for d in cursor.description]
            col_list_str = ", ".join([f'"{c}"' for c in col_names])

            # Write inserts in chunks of 500
            chunk_size = 500
            for i in range(0, len(rows), chunk_size):
                chunk = rows[i:i + chunk_size]
                values_list = []
                for row in chunk:
                    val_strs = []
                    for val in row:
                        if val is None:
                            val_strs.append("NULL")
                        elif isinstance(val, (int, float)):
                            val_strs.append(str(val))
                        elif isinstance(val, (dict, list)):
                            s = json.dumps(val).replace("'", "''")
                            val_strs.append(f"'{s}'")
                        elif isinstance(val, bytes):
                            val_strs.append(f"decode('{val.hex()}', 'hex')")
                        else:
                            s = str(val).replace("'", "''")
                            val_strs.append(f"'{s}'")
                    values_list.append(f"({', '.join(val_strs)})")

                insert_sql = f'INSERT INTO "{table}" ({col_list_str}) VALUES\n' + ",\n".join(values_list) + ";\n"
                f.write(insert_sql)

    print(f"[+] SQL dump successfully exported to {output_sql_path}!")

def direct_migrate_to_postgres(sqlite_path, postgres_url):
    """Directly stream all data from SQLite into target PostgreSQL database."""
    try:
        from app.database import Base
        import app.models
        from sqlalchemy import create_engine, text
    except ImportError:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Back"))
        from app.database import Base
        import app.models
        from sqlalchemy import create_engine, text

    if postgres_url.startswith("postgres://"):
        postgres_url = postgres_url.replace("postgres://", "postgresql://", 1)

    print(f"[*] Connecting to PostgreSQL target...")
    pg_engine = create_engine(postgres_url, pool_pre_ping=True)

    print("[*] Creating all database tables in PostgreSQL if not present...")
    Base.metadata.create_all(bind=pg_engine)

    sqlite_conn = get_sqlite_conn(sqlite_path)
    sq_cursor = sqlite_conn.cursor()

    sq_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [r[0] for r in sq_cursor.fetchall()]

    priority_tables = [
        "roles", "departments", "branches", "users", "workers", 
        "classifier_items", "products", "product_packagings", "sales", "sale_items"
    ]
    ordered_tables = [t for t in priority_tables if t in tables] + [t for t in tables if t not in priority_tables]

    total_start = time.time()
    for table in ordered_tables:
        sq_cursor.execute(f"SELECT COUNT(*) FROM \"{table}\"")
        total_rows = sq_cursor.fetchone()[0]
        if total_rows == 0:
            print(f"  [-] Table `{table}` is empty. Skipping.")
            continue

        print(f"  [*] Migrating table `{table}`: {total_rows:,} rows...")
        sq_cursor.execute(f"SELECT * FROM \"{table}\"")
        col_names = [d[0] for d in sq_cursor.description]
        col_quoted = ", ".join([f'"{c}"' for c in col_names])
        param_placeholders = ", ".join([f":{c}" for c in col_names])

        insert_query = text(f'INSERT INTO "{table}" ({col_quoted}) VALUES ({param_placeholders}) ON CONFLICT DO NOTHING')

        chunk_size = 2000
        migrated = 0
        t0 = time.time()
        with pg_engine.begin() as conn:
            while True:
                rows = sq_cursor.fetchmany(chunk_size)
                if not rows:
                    break
                
                dicts = []
                for row in rows:
                    d = dict(zip(col_names, row))
                    dicts.append(d)
                
                conn.execute(insert_query, dicts)
                migrated += len(dicts)
                print(f"    Progress `{table}`: {migrated:,}/{total_rows:,} ({(migrated/total_rows)*100:.1f}%)", end="\r")

        dt = time.time() - t0
        print(f"\n    [✓] Finished `{table}`: {migrated:,} rows in {dt:.2f}s ({migrated/max(dt,0.01):.0f} rows/s)")

    print(f"\n[+] Full database migration to Cloud PostgreSQL completed in {time.time() - total_start:.2f}s!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ERP Database Migration & Export Tool")
    parser.add_argument("--sqlite", default=os.path.join(os.path.dirname(__file__), "Back", "erp.db"), help="Path to SQLite erp.db")
    parser.add_argument("--export-sql", help="Export to PostgreSQL SQL file (e.g. dump.sql)")
    parser.add_argument("--target-url", help="PostgreSQL connection string (e.g. postgresql://user:pass@host/db)")

    args = parser.parse_args()

    if args.export_sql:
        export_to_sql_file(args.sqlite, args.export_sql)
    elif args.target_url:
        direct_migrate_to_postgres(args.sqlite, args.target_url)
    else:
        default_out = os.path.join(os.path.dirname(__file__), "erp_database_dump.sql")
        export_to_sql_file(args.sqlite, default_out)
