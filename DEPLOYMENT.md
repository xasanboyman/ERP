# Apex ERP Production Deployment Guide (Vercel & Cloud SQL)

This repository is configured for full-stack deployment on **Vercel** with **Cloud PostgreSQL** (Neon / Supabase / Vercel Postgres / Railway).

---

## 1. Architecture Overview

- **Frontend**: Vue 3 + Vite + Element Plus (Edge CDN on Vercel)
- **Backend**: FastAPI Python Serverless Function (`api/index.py` & `Back/`)
- **Database**: Cloud PostgreSQL (Neon, Supabase, Vercel Postgres, or Railway)
- **Classifiers & Catalog**: 411,022+ national MXIK commodity items and system users pre-configured.

---

## 2. Deploy to Vercel via GitHub (Recommended)

### Step 1: Push Repository to GitHub
Run the following command in terminal:
```bash
gh repo create ERP --private --source=. --remote=origin --push
```
*(Or push to your existing GitHub account `AbdulkhaevHasanboy`).*

### Step 2: Import into Vercel
1. Go to [vercel.com/new](https://vercel.com/new) and select the `ERP` repository.
2. Vercel will automatically detect `vite` and the settings from [`vercel.json`](file:///home/xasanboy/ERP/vercel.json).
3. Under **Environment Variables**, add:
   - `DATABASE_URL`: `postgresql://<user>:<password>@<host>/<database>` (From Neon, Supabase, or Vercel Postgres)
   - `SECRET_KEY`: `<your-secure-random-key>`

---

## 3. Database Migration & Cloud SQL Setup

### Option A: Direct 1-Click Migration (Fastest)
Get your connection string from **Neon.tech**, **Supabase.com**, or **Vercel Postgres**, then run:
```bash
python3 migrate_to_postgres.py --target-url="postgresql://user:password@ep-host.region.neon.tech/neondb?sslmode=require"
```
This automatically:
- Creates all relational tables & indexes
- Migrates all 411,022 classifier items
- Migrates all users, roles, workers, and settings in ~15 seconds.

### Option B: Import SQL Dump
- SQL Dump file: [`erp_database_dump.sql`](file:///home/xasanboy/ERP/erp_database_dump.sql) (or compressed [`erp_database_dump.sql.gz`](file:///home/xasanboy/ERP/erp_database_dump.sql.gz))
- Import into Postgres via CLI:
  ```bash
  psql "<DATABASE_URL>" < erp_database_dump.sql
  ```

---

## 4. Local Testing & Production Verification

- **Build Frontend**: `pnpm run build` (Outputs to `Front/dist`)
- **Run Backend**: `uvicorn app.main:app --reload --port 8000` (in `Back/`)
- **Run Full Vercel Simulation**: `npx vercel dev`
