from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from .routers import auth, role, department, branch, product, worker, salary, analytics, activity, cutting, qr, staff_hr, ai, classifier, sales, device, ws, company

import datetime
import os

from .database import is_sqlite, SessionLocal
from . import models

if is_sqlite:
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print("Database init notice:", e)


def seed_initial_roles_and_users():
    from .database import SessionLocal
    from . import models, crud
    db = SessionLocal()
    try:
        # 1. Ensure Cashier Role exists
        cashier_role = db.query(models.Role).filter(
            (models.Role.id == '7972a496-a501-48f4-b2f8-5774dc2bd9c4') |
            (models.Role.roleName.ilike('Cashier'))
        ).first()
        cashier_perms = ['/dashboard', 'workplace:view', 'workplace', 'product:view', 'product:create', 'product:edit', 'product:delete', '/product', 'list', 'pos:sell', 'pos:nasiya', 'pos:history', '/sales', 'pos']
        if not cashier_role:
            cashier_role = models.Role(
                id='7972a496-a501-48f4-b2f8-5774dc2bd9c4',
                roleName='Cashier',
                status=1,
                remark='Kassir roli',
                permissions=cashier_perms
            )
            db.add(cashier_role)
            db.commit()
            db.refresh(cashier_role)

        # 2. Ensure Super Administrator Role exists
        admin_role = db.query(models.Role).filter(models.Role.id == '1').first()
        if not admin_role:
            admin_role = models.Role(
                id='1',
                roleName='Super Administrator',
                status=1,
                remark='Super administrator',
                permissions=['*.*.*']
            )
            db.add(admin_role)
            db.commit()

        # 3. Synchronize Cashier Users
        cashier_id = cashier_role.id
        for username in ['dilshodk', 'jasura', 'kassir', 'emp_test_200_123']:
            u = db.query(models.User).filter(models.User.username == username).first()
            if u:
                u.role = 'Cashier'
                u.roleId = cashier_id
                u.permissions = cashier_role.permissions or cashier_perms

            w = db.query(models.Worker).filter(models.Worker.account == username).first()
            if w:
                w.role = 'Cashier'

        # 4. Synchronize Super Admin Users
        for username in ['admin', 'anvars']:
            u = db.query(models.User).filter(models.User.username == username).first()
            if u:
                u.role = 'Super Administrator'
                u.roleId = '1'
                u.permissions = ['*.*.*']

        db.commit()
    except Exception as e:
        print('Seed warning:', e)
    finally:
        db.close()

app = FastAPI(title="ERP System Backend", version="1.0.0")

# Serve uploaded product images
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
uploads_dir = os.path.join(base_dir, "uploads")
try:
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir, exist_ok=True)
    if os.path.exists(uploads_dir):
        app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
except Exception as err:
    print("Uploads mount notice:", err)

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400,
        content={"code": 400, "message": "Database integrity constraint violation: " + str(exc)}
    )

app.add_middleware(GZipMiddleware, minimum_size=500)

# Setup CORS to allow request redirects from frontend port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def token_expiration_middleware(request: Request, call_next):
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
    if auth_header and request.url.path not in ["/user/login", "/user/loginOut", "/v1/status", "/docs", "/openapi.json"]:
        payload = auth.decode_access_token(auth_header)
        if isinstance(payload, dict) and "error" in payload:
            return JSONResponse(
                status_code=401,
                content={"code": 401, "message": "Sessiya muddati tugadi (12 soat). Iltimos, qayta tizimga kiring."}
            )
        if isinstance(payload, dict) and "sub" in payload and payload["sub"] not in ["admin", "anvars"]:
            db = SessionLocal()
            try:
                user = db.query(models.User).filter(models.User.username == payload["sub"]).first()
                if user and user.company_id and user.company_id != "comp-default":
                    comp = db.query(models.Company).filter(models.Company.id == user.company_id).first()
                    if comp and comp.status == 0:
                        return JSONResponse(
                            status_code=403,
                            content={
                                "code": 403,
                                "message": f"'{comp.name}' kompaniyasi hisobi oylik to'lov amalga oshirilmaganligi sababli to'xtatilgan. Iltimos, administratorga murojaat qiling."
                            }
                        )
            finally:
                db.close()
    return await call_next(request)

# Register routes (both directly and with /api prefix for serverless compatibility)
all_routers = [
    (auth.router, ["Authentication"]),
    (role.router, ["Role & Routing"]),
    (department.router, ["Department Management"]),
    (branch.router, ["Branch Management"]),
    (product.router, ["Product & Inventory"]),
    (worker.router, ["Worker Management"]),
    (salary.router, ["Salary & Payroll"]),
    (analytics.router, ["Analytics & Dashboard"]),
    (activity.router, ["Activity Log"]),
    (cutting.router, ["Cutting Management"]),
    (qr.router, ["QR Code Management"]),
    (staff_hr.router, ["Staff HR Extensions"]),
    (ai.router, ["AI Voice Assistant"]),
    (classifier.router, ["Classifier Management"]),
    (sales.router, ["Sales & POS Terminal"]),
    (device.router, ["Device Management"]),
    (ws.router, ["Real-Time WebSockets"]),
    (company.router, ["Company Management"]),
]

for router_obj, router_tags in all_routers:
    app.include_router(router_obj, tags=router_tags)
    app.include_router(router_obj, prefix="/api", tags=router_tags)

@app.on_event("startup")
async def on_startup():
    try:
        seed_initial_roles_and_users()
    except Exception as e:
        print("Startup seed notice:", e)

    from .websocket_manager import manager
    import asyncio
    try:
        manager.set_loop(asyncio.get_running_loop())
    except Exception as e:
        print("WS loop bind notice:", e)

    import threading
    from .routers.analytics import warm_up_analytics_cache
    threading.Thread(target=warm_up_analytics_cache, daemon=True).start()




@app.get("/")
def read_root():
    return {"message": "ERP API is running and healthy", "status": "ok"}

@app.get("/v1/status")
def get_v1_status():
    return {
        "status": "online",
        "version": "1.0.0",
        "app": app.title,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }

@app.post("/v1/qr/scan")
async def post_v1_qr_scan(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    
    qr_code = body.get("qr_code")
    
    return JSONResponse(
        status_code=501,
        content={
            "success": False,
            "message": "QR scan endpoint is not enabled yet.",
            "next_step": "Configure device authentication before enabling external scan requests.",
            "data": {
                "received_at": datetime.datetime.utcnow().isoformat() + "Z",
                "qr_code": qr_code
            }
        }
    )

