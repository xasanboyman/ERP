import jwt
from fastapi import APIRouter, Depends, Query, Body, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models

SECRET_KEY = "super-secret-key-that-is-hard-to-guess"
ALGORITHM = "HS256"

def decode_access_token(token: str):
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def get_current_user_from_header(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        return None
    payload = decode_access_token(authorization)
    if not payload or "sub" not in payload:
        return None
    return db.query(models.User).filter(models.User.username == payload["sub"]).first()

router = APIRouter()

DEFAULT_ADMIN_ROUTES = [
    {
        "path": "/dashboard",
        "component": "#",
        "redirect": "/dashboard/analysis",
        "name": "Dashboard",
        "meta": {
            "title": "router.dashboard",
            "icon": "vi-ant-design:dashboard-filled",
            "alwaysShow": True
        },
        "children": [
            {
                "path": "analysis",
                "component": "views/Dashboard/Analysis",
                "name": "Analysis",
                "meta": {
                    "title": "router.analysis",
                    "noCache": True
                }
            },
            {
                "path": "workplace",
                "component": "views/Dashboard/Workplace",
                "name": "Workplace",
                "meta": {
                    "title": "router.workplace",
                    "noCache": True
                }
            }
        ]
    },
    {
        "path": "/product",
        "component": "#",
        "redirect": "/product/list",
        "name": "ProductRoot",
        "meta": {
            "title": "router.product",
            "icon": "vi-ep:goods",
            "alwaysShow": True
        },
        "children": [
            {
                "path": "list",
                "component": "views/Product/Product",
                "name": "ProductManagement",
                "meta": {
                    "title": "router.product",
                    "noCache": True
                }
            }
        ]
    },
    {
        "path": "/sales",
        "component": "#",
        "redirect": "/sales/pos",
        "name": "SalesRoot",
        "meta": {
            "title": "router.sales",
            "icon": "vi-ep:shopping-cart-full",
            "alwaysShow": True
        },
        "children": [
            {
                "path": "pos",
                "component": "views/Sales/Pos",
                "name": "SalesPos",
                "meta": {
                    "title": "router.pos",
                    "icon": "vi-ep:sell",
                    "noCache": True
                }
            },
            {
                "path": "debtors",
                "component": "views/Sales/Debtors",
                "name": "SalesDebtors",
                "meta": {
                    "title": "router.debtors",
                    "icon": "vi-ep:credit-card",
                    "noCache": True
                }
            }
        ]
    },

    {
        "path": "/hr",

        "component": "#",
        "redirect": "/hr/workers",
        "name": "HRRoot",
        "meta": {
            "title": "router.worker",
            "icon": "vi-ep:avatar",
            "alwaysShow": True
        },
        "children": [
            {
                "path": "workers",
                "component": "views/Worker/Worker",
                "name": "WorkerManagement",
                "meta": {
                    "title": "router.worker",
                    "noCache": True
                }
            },
            {
                "path": "timesheets",
                "component": "views/StaffHR/Timesheet",
                "name": "TimesheetManagement",
                "meta": {
                    "title": "router.timesheet",
                    "noCache": True
                }
            },
            {
                "path": "outputs",
                "component": "views/StaffHR/Output",
                "name": "OutputManagement",
                "meta": {
                    "title": "router.output",
                    "noCache": True
                }
            },
            {
                "path": "adjustments",
                "component": "views/StaffHR/Adjustment",
                "name": "AdjustmentManagement",
                "meta": {
                    "title": "Korrektirovka (Bonus/Shtraf)",
                    "noCache": True
                }
            },
            {
                "path": "salary",
                "component": "views/Salary/Salary",
                "name": "SalaryManagement",
                "meta": {
                    "title": "Ish haqi",
                    "noCache": True
                }
            }
        ]
    },
    {
        "path": "/authorization",
        "component": "#",
        "redirect": "/authorization/department",
        "name": "Authorization",
        "meta": {
            "title": "router.authorization",
            "icon": "vi-eos-icons:role-binding",
            "alwaysShow": True
        },
        "children": [
            {
                "path": "department",
                "component": "views/Authorization/Department/Department",
                "name": "Department",
                "meta": {
                    "title": "router.department",
                    "noCache": True
                }
            },
            {
                "path": "role",
                "component": "views/Authorization/Role/Role",
                "name": "Role",
                "meta": {
                    "title": "Rollar",
                    "noCache": True
                }
            }
        ]
    }
]


# For student portal, restrict access to student portal routes only
DEFAULT_STUDENT_ROUTES = [
    {
        "path": "/crm",
        "component": "#",
        "redirect": "/crm/student-lessons",
        "name": "CRMStudentPortal",
        "meta": {
            "title": "Talaba Portali",
            "icon": "vi-ep:reading",
            "alwaysShow": True
        },
        "children": [
            {
                "path": "student-lessons",
                "component": "views/CRM/StudentLessons",
                "name": "CRMStudentLessons",
                "meta": {
                    "title": "Mening darslarim",
                    "noCache": True
                }
            },
            {
                "path": "student-coupons",
                "component": "views/CRM/StudentCoupons",
                "name": "CRMStudentCoupons",
                "meta": {
                    "title": "Mening kuponlarim",
                    "noCache": True
                }
            }
        ]
    }
]

# For test user, we can restrict access to just workplace, products and analytics
DEFAULT_TEST_ROUTES = [
    {
        "path": "/dashboard",
        "component": "#",
        "redirect": "/dashboard/workplace",
        "name": "Dashboard",
        "meta": {
            "title": "router.dashboard",
            "icon": "vi-ant-design:dashboard-filled",
            "alwaysShow": True
        },
        "children": [
            {
                "path": "workplace",
                "component": "views/Dashboard/Workplace",
                "name": "Workplace",
                "meta": {
                    "title": "router.workplace",
                    "noCache": True,
                    "affix": True
                }
            }
        ]
    },
    {
        "path": "/product",
        "component": "#",
        "redirect": "/product/list",
        "name": "ProductRoot",
        "meta": {
            "title": "Products",
            "icon": "vi-ep:goods",
            "alwaysShow": True
        },
        "children": [
            {
                "path": "list",
                "component": "views/Product/Product",
                "name": "ProductManagement",
                "meta": {
                    "title": "router.product",
                    "noCache": True
                }
            }
        ]
    }
]

MODULE_ACTION_MAP = {
    "/dashboard/analysis": ["dashboard:view", "dashboard:export", "analysis:view", "analysis"],
    "/dashboard/workplace": ["workplace:view", "workplace"],
    "/product/list": ["product:view", "product:create", "product:edit", "product:delete", "product", "list"],
    "/sales/pos": ["pos:sell", "pos:discount", "pos:nasiya", "pos:history", "pos"],
    "/sales/debtors": ["pos:nasiya", "debtors"],
    "/hr/workers": ["worker:view", "worker:create", "worker:edit", "worker:delete", "worker", "workers"],
    "/hr/positions": ["position:view", "positions"],
    "/hr/timesheets": ["timesheet:view", "timesheets"],
    "/hr/outputs": ["output:view", "outputs"],
    "/hr/adjustments": ["adjustment:view", "adjustments"],
    "/hr/salary": ["salary:view", "salary"],
    "/authorization/department": ["department:manage", "department"],
    "/authorization/role": ["role:manage", "role"]
}

@router.get("/role/list")
def get_role_menu_list(
    roleName: str = Query("admin"),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == roleName).first()
    if not user:
        worker = db.query(models.Worker).filter(
            (models.Worker.account == roleName) |
            (models.Worker.name == roleName) |
            (models.Worker.employee_code == roleName)
        ).first()
        if worker:
            user = db.query(models.User).filter(
                (models.User.username == worker.account) |
                (models.User.full_name == worker.name)
            ).first()

    if not user:
        return {"code": 0, "data": []}

    db_role = None
    if user.roleId:
        db_role = db.query(models.Role).filter(models.Role.id == str(user.roleId)).first()
    if not db_role and user.role:
        db_role = db.query(models.Role).filter(
            (models.Role.roleName.ilike(user.role)) |
            (models.Role.id == str(user.role))
        ).first()

    is_super_admin = (user.role and user.role.lower() in ["super administrator", "superadmin", "admin"])
    if not is_super_admin and db_role and db_role.permissions:
        role_perms = db_role.permissions if isinstance(db_role.permissions, list) else []
        for p in role_perms:
            if isinstance(p, str) and p in ['*.*.*', '*']:
                is_super_admin = True
                break

    if is_super_admin:
        return {"code": 0, "data": DEFAULT_ADMIN_ROUTES}

    raw_permissions = []
    if db_role and db_role.permissions:
        raw_permissions = db_role.permissions
    elif user.permissions:
        raw_permissions = user.permissions

    if isinstance(raw_permissions, str):
        try:
            import json
            raw_permissions = json.loads(raw_permissions)
        except Exception:
            raw_permissions = [raw_permissions]

    if "*.*.*" in raw_permissions and is_super_admin:
        return {"code": 0, "data": DEFAULT_ADMIN_ROUTES}

    perm_set = set()
    for p in raw_permissions:
        if isinstance(p, str):
            perm_set.add(p.lower())
        elif isinstance(p, dict):
            if "path" in p:
                perm_set.add(p["path"].lower())
            if "children" in p and isinstance(p["children"], list):
                for c in p["children"]:
                    if isinstance(c, dict) and "path" in c:
                        perm_set.add(c["path"].lower())
                    elif isinstance(c, str):
                        perm_set.add(c.lower())

    filtered_routes = []
    for route in DEFAULT_ADMIN_ROUTES:
        r_path = route["path"].lower()
        r_clean = r_path.replace("/", "")

        filtered_children = []
        if "children" in route:
            for child in route["children"]:
                c_path = child["path"].lower()
                full_path = f"{r_path}/{c_path}".lower()
                r_clean_child = f"{r_clean}:{c_path}"

                action_triggers = MODULE_ACTION_MAP.get(full_path, [c_path, full_path, r_clean_child])

                allowed = (
                    full_path in perm_set or
                    r_clean_child in perm_set or
                    r_path in perm_set or
                    any(act in perm_set for act in action_triggers) or
                    any(
                        p == full_path or
                        p == f"/{c_path}" or
                        p == r_clean_child or
                        p.endswith(f":{c_path}") or
                        p.endswith(f"/{c_path}")
                        for p in perm_set if isinstance(p, str)
                    )
                )
                if allowed:
                    filtered_children.append(child)

        parent_explicit = r_path in perm_set or r_clean in perm_set
        if filtered_children or parent_explicit:
            new_route = dict(route)
            if "children" in route:
                new_route["children"] = filtered_children
                if filtered_children:
                    first_child = filtered_children[0]["path"]
                    new_route["redirect"] = f"{r_path}/{first_child}".replace("//", "/")
            
            if "children" not in route or len(new_route.get("children", [])) > 0:
                filtered_routes.append(new_route)

    return {
        "code": 0,
        "data": filtered_routes
    }

@router.get("/role/list2")
def get_role_list2(roleName: str = Query("admin")):
    if "admin" in roleName.lower():
        permissions = ["*.*.*"]
    elif "student" in roleName.lower():
        permissions = ["crm:student:view"]
    else:
        permissions = ["example:dialog:create", "example:dialog:delete"]
    return {
        "code": 0,
        "data": permissions
    }


@router.get("/role/table")
def get_roles_table(db: Session = Depends(get_db)):
    roles = crud.get_roles(db)
    return {
        "code": 0,
        "data": {
            "list": [
                {
                    "id": r.id,
                    "roleName": r.roleName,
                    "status": r.status,
                    "remark": r.remark,
                    "createTime": r.createTime,
                    "permissions": r.permissions or []
                }
                for r in roles
            ],
            "total": len(roles)
        }
    }

@router.get("/menu/list")
def get_menu_list():
    return {
        "code": 0,
        "data": {
            "list": [
                {
                    "path": "/dashboard",
                    "component": "#",
                    "redirect": "/dashboard/analysis",
                    "name": "Dashboard",
                    "status": 1,
                    "id": 1,
                    "type": 0,
                    "parentId": None,
                    "title": "Boshqaruv paneli (Dashboard)",
                    "icon": "vi-ant-design:dashboard-filled",
                    "meta": {
                        "title": "Boshqaruv paneli (Dashboard)",
                        "icon": "vi-ant-design:dashboard-filled",
                        "alwaysShow": True,
                        "permission": []
                    },
                    "permissionList": [
                        {"label": "Statistikalarni ko'rish", "value": "dashboard:view", "icon": "vi-ep:view"},
                        {"label": "Hisobotlarni yuklash", "value": "dashboard:export", "icon": "vi-ep:download"}
                    ],
                    "children": [
                        {
                            "path": "analysis",
                            "component": "views/Dashboard/Analysis",
                            "name": "Analysis",
                            "status": 1,
                            "id": 2,
                            "type": 1,
                            "parentId": 1,
                            "title": "Tahlil va Grafika",
                            "icon": "vi-ep:data-analysis",
                            "meta": {
                                "title": "Tahlil va Grafika",
                                "noCache": True,
                                "permission": []
                            },
                            "permissionList": [
                                {"label": "Ko'rish ruxsati", "value": "analysis:view", "icon": "vi-ep:view"}
                            ]
                        },
                        {
                            "path": "workplace",
                            "component": "views/Dashboard/Workplace",
                            "name": "Workplace",
                            "status": 1,
                            "id": 3,
                            "type": 1,
                            "parentId": 1,
                            "title": "Ish joyi paneli",
                            "icon": "vi-ep:monitor",
                            "meta": {
                                "title": "Ish joyi paneli",
                                "noCache": True,
                                "permission": []
                            },
                            "permissionList": [
                                {"label": "Ko'rish ruxsati", "value": "workplace:view", "icon": "vi-ep:view"}
                            ]
                        }
                    ]
                },
                {
                    "path": "/product",
                    "component": "#",
                    "redirect": "/product/list",
                    "name": "ProductRoot",
                    "status": 1,
                    "id": 50,
                    "type": 0,
                    "parentId": None,
                    "title": "Omborxona (Mahsulotlar)",
                    "icon": "vi-ep:goods",
                    "meta": {
                        "title": "Omborxona (Mahsulotlar)",
                        "icon": "vi-ep:goods",
                        "alwaysShow": True,
                        "permission": []
                    },
                    "permissionList": [
                        {"label": "Mahsulotlarni ko'rish", "value": "product:view", "icon": "vi-ep:view"},
                        {"label": "Yangi mahsulot qo'shish", "value": "product:create", "icon": "vi-ep:plus"},
                        {"label": "Narx/Sonini tahrirlash", "value": "product:edit", "icon": "vi-ep:edit"},
                        {"label": "Mahsulotni o'chirish", "value": "product:delete", "icon": "vi-ep:delete"}
                    ],
                    "children": [
                        {
                            "path": "list",
                            "component": "views/Product/Product",
                            "name": "ProductManagement",
                            "status": 1,
                            "id": 51,
                            "type": 1,
                            "parentId": 50,
                            "title": "Ombor Mahsulotlari Ro'yxati",
                            "icon": "vi-ep:list",
                            "meta": {
                                "title": "Ombor Mahsulotlari Ro'yxati",
                                "noCache": True,
                                "permission": []
                            },
                            "permissionList": [
                                {"label": "Mahsulotlarni ko'rish", "value": "product:view", "icon": "vi-ep:view"},
                                {"label": "Yangi mahsulot qo'shish", "value": "product:create", "icon": "vi-ep:plus"},
                                {"label": "Tahrirlash ruxsati", "value": "product:edit", "icon": "vi-ep:edit"},
                                {"label": "O'chirish ruxsati", "value": "product:delete", "icon": "vi-ep:delete"}
                            ]
                        }
                    ]
                },
                {
                    "path": "/sales",
                    "component": "#",
                    "redirect": "/sales/pos",
                    "name": "SalesRoot",
                    "status": 1,
                    "id": 60,
                    "type": 0,
                    "parentId": None,
                    "title": "Sotuvlar (POS Kassa)",
                    "icon": "vi-ep:shopping-cart-full",
                    "meta": {
                        "title": "Sotuvlar (POS Kassa)",
                        "icon": "vi-ep:shopping-cart-full",
                        "alwaysShow": False,
                        "permission": []
                    },
                    "permissionList": [
                        {"label": "Sotuvni rasmiylashtirish va chek urish", "value": "pos:sell", "icon": "vi-ep:sell"},
                        {"label": "Chegirma berish ruxsati", "value": "pos:discount", "icon": "vi-ep:discount"},
                        {"label": "Nasiya / qarzga sotish ruxsati", "value": "pos:nasiya", "icon": "vi-ep:document"},
                        {"label": "Sotuvlar tarixini ko'rish", "value": "pos:history", "icon": "vi-ep:clock"}
                    ],
                    "children": [
                        {
                            "path": "pos",
                            "component": "views/Sales/Pos",
                            "name": "SalesPos",
                            "status": 1,
                            "id": 61,
                            "type": 1,
                            "parentId": 60,
                            "title": "POS Terminal Kassa",
                            "icon": "vi-ep:goods-filled",
                            "meta": {
                                "title": "POS Terminal Kassa",
                                "noCache": True,
                                "permission": []
                            },
                            "permissionList": [
                                {"label": "Sotuvni rasmiylashtirish", "value": "pos:sell", "icon": "vi-ep:sell"},
                                {"label": "Chegirma berish ruxsati", "value": "pos:discount", "icon": "vi-ep:discount"},
                                {"label": "Nasiya / qarzga sotish", "value": "pos:nasiya", "icon": "vi-ep:document"}
                            ]
                        }
                    ]
                },
                {
                    "path": "/hr",
                    "component": "#",
                    "redirect": "/hr/workers",
                    "name": "HRRoot",
                    "status": 1,
                    "id": 100,
                    "type": 0,
                    "parentId": None,
                    "title": "Xodimlar (Employees)",
                    "icon": "vi-ep:avatar",
                    "meta": {
                        "title": "Xodimlar (Employees)",
                        "icon": "vi-ep:avatar",
                        "alwaysShow": True,
                        "permission": []
                    },
                    "permissionList": [
                        {"label": "Xodimlarni ko'rish", "value": "worker:view", "icon": "vi-ep:view"},
                        {"label": "Yangi xodim qo'shish", "value": "worker:create", "icon": "vi-ep:plus"},
                        {"label": "Xodim ma'lumotlarini tahrirlash", "value": "worker:edit", "icon": "vi-ep:edit"},
                        {"label": "Xodimni bo'shatish / o'chirish", "value": "worker:delete", "icon": "vi-ep:delete"}
                    ],
                    "children": [
                        {
                            "path": "workers",
                            "component": "views/Worker/Worker",
                            "name": "WorkerManagement",
                            "status": 1,
                            "id": 101,
                            "type": 1,
                            "parentId": 100,
                            "title": "router.worker",
                            "icon": "vi-ep:user",
                            "meta": {
                                "title": "router.worker",
                                "noCache": True,
                                "permission": []
                            },
                            "permissionList": [
                                {"label": "Xodimlarni ko'rish", "value": "worker:view", "icon": "vi-ep:view"},
                                {"label": "Yangi xodim qo'shish", "value": "worker:create", "icon": "vi-ep:plus"},
                                {"label": "Tahrirlash ruxsati", "value": "worker:edit", "icon": "vi-ep:edit"},
                                {"label": "O'chirish ruxsati", "value": "worker:delete", "icon": "vi-ep:delete"}
                            ]
                        },
                        {
                            "path": "timesheets",
                            "component": "views/StaffHR/Timesheet",
                            "name": "TimesheetManagement",
                            "status": 1,
                            "id": 103,
                            "type": 1,
                            "parentId": 100,
                            "title": "router.timesheet",
                            "icon": "vi-ep:calendar",
                            "meta": {
                                "title": "router.timesheet",
                                "noCache": True,
                                "permission": []
                            },
                            "permissionList": [
                                {"label": "Tabel davomatini ko'rish", "value": "timesheet:view", "icon": "vi-ep:view"}
                            ]
                        },
                        {
                            "path": "outputs",
                            "component": "views/StaffHR/Output",
                            "name": "OutputManagement",
                            "status": 1,
                            "id": 104,
                            "type": 1,
                            "parentId": 100,
                            "title": "Vyrabotka (Bajarilgan ishlar)",
                            "icon": "vi-ep:trend-charts",
                            "meta": {
                                "title": "Vyrabotka (Bajarilgan ishlar)",
                                "noCache": True,
                                "permission": []
                            },
                            "permissionList": [
                                {"label": "Vyrabotkani ko'rish", "value": "output:view", "icon": "vi-ep:view"}
                            ]
                        },
                        {
                            "path": "adjustments",
                            "component": "views/StaffHR/Adjustment",
                            "name": "AdjustmentManagement",
                            "status": 1,
                            "id": 105,
                            "type": 1,
                            "parentId": 100,
                            "title": "Korrektirovka (Bonus/Shtraf)",
                            "icon": "vi-ep:setting",
                            "meta": {
                                "title": "Korrektirovka (Bonus/Shtraf)",
                                "noCache": True,
                                "permission": []
                            },
                            "permissionList": [
                                {"label": "Korrektirovkalarni ko'rish", "value": "adjustment:view", "icon": "vi-ep:view"}
                            ]
                        },
                        {
                            "path": "salary",
                            "component": "views/Salary/Salary",
                            "name": "SalaryManagement",
                            "status": 1,
                            "id": 106,
                            "type": 1,
                            "parentId": 100,
                            "title": "Ish haqi",
                            "icon": "vi-ep:money",
                            "meta": {
                                "title": "Ish haqi",
                                "noCache": True,
                                "permission": []
                            },
                            "permissionList": [
                                {"label": "Ish haqini ko'rish", "value": "salary:view", "icon": "vi-ep:view"}
                            ]
                        }
                    ]
                },
                {
                    "path": "/authorization",
                    "component": "#",
                    "redirect": "/authorization/role",
                    "name": "Authorization",
                    "status": 1,
                    "id": 200,
                    "type": 0,
                    "parentId": None,
                    "title": "router.authorization",
                    "icon": "vi-eos-icons:role-binding",
                    "meta": {
                        "title": "router.authorization",
                        "icon": "vi-eos-icons:role-binding",
                        "alwaysShow": True,
                        "permission": []
                    },
                    "permissionList": [
                        {"label": "Rollar va ruxsatlarni boshqarish", "value": "role:manage", "icon": "vi-ep:lock"},
                        {"label": "Do'kon filiallarini boshqarish", "value": "branch:manage", "icon": "vi-ep:office-building"}
                    ],
                    "children": [
                        {
                            "path": "department",
                            "component": "views/Authorization/Department/Department",
                            "name": "Department",
                            "status": 1,
                            "id": 201,
                            "type": 1,
                            "parentId": 200,
                            "title": "Bo'limlar & Filiallar",
                            "icon": "vi-ep:office-building",
                            "meta": {
                                "title": "Bo'limlar & Filiallar",
                                "noCache": True,
                                "permission": []
                            },
                            "permissionList": [
                                {"label": "Bo'limlar va filiallarni boshqarish", "value": "branch:manage", "icon": "vi-ep:office-building"}
                            ]
                        },
                        {
                            "path": "role",
                            "component": "views/Authorization/Role/Role",
                            "name": "Role",
                            "status": 1,
                            "id": 204,
                            "type": 1,
                            "parentId": 200,
                            "title": "Rollar (Ruxsatlar)",
                            "icon": "vi-eos-icons:role-binding",
                            "meta": {
                                "title": "Rollar (Ruxsatlar)",
                                "noCache": True,
                                "permission": []
                            },
                            "permissionList": [
                                {"label": "Rollar va ruxsatlarni boshqarish", "value": "role:manage", "icon": "vi-ep:lock"}
                            ]
                        }
                    ]
                }
            ]
        }
    }

@router.post("/role/save")
def role_save(role_in: schemas.RoleCreate, db: Session = Depends(get_db)):
    r = crud.create_role(db, role_in)
    # Sync ALL users with this role
    users_with_role = db.query(models.User).filter(
        (models.User.roleId == r.id) | (models.User.role.ilike(r.roleName))
    ).all()
    for u in users_with_role:
        u.permissions = r.permissions or []
        u.role = r.roleName
        u.roleId = r.id
    # Also sync workers
    workers_with_role = db.query(models.Worker).filter(
        models.Worker.role.ilike(r.roleName)
    ).all()
    for w in workers_with_role:
        w.role = r.roleName
    db.commit()

    from app.routers.activity import log_activity
    log_activity(
        db=db,
        actor="admin",
        action="saved",
        entity="role",
        entity_id=r.id,
        entity_name=r.roleName
    )

    return {"code": 0, "data": r.id}

@router.post("/role/delete")
def role_delete(body: dict = Body(...), db: Session = Depends(get_db)):
    role_id = body.get("id")
    if not role_id:
        return {"code": 500, "message": "ID is required"}
    role = db.query(models.Role).filter(models.Role.id == str(role_id)).first()
    if role:
        role_name = role.roleName
        db.delete(role)
        db.commit()
        from app.routers.activity import log_activity
        log_activity(
            db=db,
            actor="admin",
            action="deleted",
            entity="role",
            entity_id=str(role_id),
            entity_name=role_name
        )
        return {"code": 0, "data": True}
    return {"code": 500, "message": "Role not found"}
