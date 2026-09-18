import copy
from typing import Optional
from fastapi import APIRouter, Depends, Query, Body, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, models
from app.auth import decode_access_token, get_current_user_from_header, check_user_access

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

COMPANY_MANAGEMENT_ROUTE = {
    "path": "/company",
    "component": "#",
    "redirect": "/company/list",
    "name": "CompanyRoot",
    "meta": {
        "title": "router.companyManagement",
        "icon": "vi-ep:office-building",
        "alwaysShow": True
    },
    "children": [
        {
            "path": "list",
            "component": "views/Company/CompanyManagement",
            "name": "CompanyManagement",
            "meta": {
                "title": "router.companyManagement",
                "icon": "vi-ep:office-building",
                "noCache": True
            }
        }
    ]
}


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

COMPANY_USER_ROUTES = [
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

@router.get("/role/list")
def get_role_menu_list(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tizimga kirilmagan yoki sessiya yaroqsiz"
        )

    user = get_current_user_from_header(authorization, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tizimga kirilmagan yoki sessiya yaroqsiz"
        )

    comp_id = getattr(user, "company_id", None) or "comp-default"
    role_str = (user.role or "").lower()
    is_super_admin = False
    if user.username in ["admin", "anvars"]:
        is_super_admin = True
    elif comp_id == "comp-default":
        if "super" in role_str or getattr(user, "is_super_admin", False) is True:
            is_super_admin = True

    if is_super_admin:
        routes = list(DEFAULT_ADMIN_ROUTES)
        routes.insert(1, COMPANY_MANAGEMENT_ROUTE)
        return {"code": 0, "data": routes}

    # For Company Admins (and users with wildcard *.*.* permissions):
    is_admin = "admin" in role_str or "administrator" in role_str
    user_perms = list(user.permissions or [])
    if not user_perms:
        role_obj = None
        if user.roleId:
            role_obj = db.query(models.Role).filter(models.Role.id == str(user.roleId)).first()
        if not role_obj and user.role:
            role_obj = db.query(models.Role).filter(
                models.Role.roleName.ilike(user.role),
                (models.Role.company_id == comp_id) | (models.Role.company_id == "comp-default") | (models.Role.company_id == None)
            ).first()
        if role_obj and role_obj.permissions:
            user_perms = list(role_obj.permissions)

    user_perms_lower = set(str(p).lower().strip() for p in user_perms)
    if "*.*.*" in user_perms_lower or "*" in user_perms_lower or is_admin:
        return {"code": 0, "data": COMPANY_USER_ROUTES}

    # Strict Cashier restriction: cashiers must ONLY see POS (/sales/pos) and Products (/product/list)
    is_cashier = "cashier" in role_str or "kassir" in role_str
    if is_cashier:
        cashier_routes = []
        for parent in COMPANY_USER_ROUTES:
            if parent.get("path") == "/sales":
                parent_copy = copy.deepcopy(parent)
                parent_copy["children"] = [c for c in parent.get("children", []) if c.get("path") == "pos"]
                parent_copy["redirect"] = "/sales/pos"
                cashier_routes.append(parent_copy)
            elif parent.get("path") == "/product":
                parent_copy = copy.deepcopy(parent)
                parent_copy["children"] = [c for c in parent.get("children", []) if c.get("path") == "list"]
                parent_copy["redirect"] = "/product/list"
                cashier_routes.append(parent_copy)
        return {"code": 0, "data": cashier_routes}

    # Filter COMPANY_USER_ROUTES strictly based on user's specific permissions:
    ROUTE_PERMISSION_MAP = {
        "/dashboard/analysis": ["analysis:view", "dashboard:analysis", "dashboard:view"],
        "/dashboard/workplace": ["workplace:view", "dashboard:workplace"],
        "/product/list": ["product:view", "product:create", "product:edit", "product:delete", "product", "list", "/product/list"],
        "/sales/pos": ["sales:pos:view", "sales:pos:checkout", "sales:pos", "pos:sell", "pos:view", "pos:discount", "pos:nasiya", "pos:history", "pos", "/sales/pos"],
        "/sales/debtors": ["debtors:view", "debtors:manage", "debtors:repay", "debtors:history", "debtors:export", "debtors", "/sales/debtors"],
        "/hr/workers": ["worker:view", "worker:create", "worker:edit", "worker:delete", "worker", "workers", "hr:workers", "/hr/workers"],
        "/hr/timesheets": ["timesheet:view", "timesheets", "/hr/timesheets"],
        "/hr/outputs": ["output:view", "outputs", "/hr/outputs"],
        "/hr/adjustments": ["adjustment:view", "adjustments", "/hr/adjustments"],
        "/hr/salary": ["salary:view", "salary", "/hr/salary"],
        "/authorization/department": ["department:manage", "department", "/authorization/department"],
        "/authorization/role": ["role:manage", "role", "/authorization/role"]
    }

    allowed_routes = []
    for parent in COMPANY_USER_ROUTES:
        parent_path = parent.get("path", "")
        children = parent.get("children", [])

        allowed_children = []
        for child in children:
            child_path = child.get("path", "")
            full_child_path = f"{parent_path}/{child_path}" if not child_path.startswith("/") else child_path
            req_keys = ROUTE_PERMISSION_MAP.get(full_child_path, [full_child_path, child_path])
            if any(k.lower() in user_perms_lower for k in req_keys):
                allowed_children.append(copy.deepcopy(child))

        if allowed_children:
            parent_copy = copy.deepcopy(parent)
            parent_copy["children"] = allowed_children
            first_child_path = allowed_children[0].get("path", "")
            parent_copy["redirect"] = f"{parent_path}/{first_child_path}" if not first_child_path.startswith("/") else first_child_path
            allowed_routes.append(parent_copy)

    return {"code": 0, "data": allowed_routes}

@router.get("/role/list2")
def get_role_list2(
    authorization: str = Header(None),
    roleName: str = Query("admin"),
    db: Session = Depends(get_db)
):
    if authorization:
        user = get_current_user_from_header(authorization, db)
        if user:
            role_str = (user.role or "").lower()
            if "admin" in role_str or user.username in ["admin", "anvars"]:
                return {"code": 0, "data": ["*.*.*"]}
            perms = list(user.permissions or [])
            if user.roleId:
                role_obj = db.query(models.Role).filter(models.Role.id == str(user.roleId)).first()
                if role_obj and role_obj.permissions:
                    perms.extend(role_obj.permissions)
            return {"code": 0, "data": list(set(perms))}

    if "admin" in roleName.lower():
        permissions = ["*.*.*"]
    elif "student" in roleName.lower():
        permissions = ["crm:student:view"]
    else:
        permissions = ["sales:pos:view", "sales:pos:checkout", "product:view"]
    return {
        "code": 0,
        "data": permissions
    }


@router.get("/role/table")
def get_roles_table(
    authorization: str = Header(None),
    company_id: str = Query(None),
    db: Session = Depends(get_db)
):
    current_user = get_current_user_from_header(authorization, db)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tizimga kirilmagan yoki sessiya yaroqsiz"
        )
    check_user_access(current_user, ["role:manage", "role", "/authorization/role"], db)

    from app.auth import get_user_company_id
    target_company = get_user_company_id(authorization, db, company_id)
    roles = crud.get_roles(db, company_id=target_company)
    return {
        "code": 0,
        "data": {
            "list": [
                {
                    "id": r.id,
                    "company_id": getattr(r, "company_id", "comp-default"),
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
                        {"label": "Bo'limlarni boshqarish", "value": "department:manage", "icon": "vi-ep:folder"}
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
                            "title": "Bo'limlar",
                            "icon": "vi-ep:folder",
                            "meta": {
                                "title": "Bo'limlar",
                                "noCache": True,
                                "permission": []
                            },
                            "permissionList": [
                                {"label": "Bo'limlarni boshqarish", "value": "department:manage", "icon": "vi-ep:folder"}
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
def role_save(
    role_in: schemas.RoleCreate,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    from app.auth import get_user_company_id
    current_user = get_current_user_from_header(authorization, db)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tizimga kirilmagan yoki sessiya yaroqsiz")
    check_user_access(current_user, ["role:manage", "role", "/authorization/role"], db)

    target_company = get_user_company_id(authorization, db, getattr(role_in, "company_id", None))
    r = crud.create_role(db, role_in, company_id=target_company)

    # Sync users in target_company with this role
    user_query = db.query(models.User).filter(
        (models.User.roleId == r.id) | (models.User.role.ilike(r.roleName))
    )
    if target_company and target_company != "comp-default":
        user_query = user_query.filter(models.User.company_id == target_company)
    users_with_role = user_query.all()
    for u in users_with_role:
        u.permissions = r.permissions or []
        u.role = r.roleName
        u.roleId = r.id

    # Also sync workers in target_company
    worker_query = db.query(models.Worker).filter(models.Worker.role.ilike(r.roleName))
    if target_company and target_company != "comp-default":
        worker_query = worker_query.filter(models.Worker.company_id == target_company)
    workers_with_role = worker_query.all()
    for w in workers_with_role:
        w.role = r.roleName
    db.commit()

    from app.routers.activity import log_activity
    log_activity(
        db=db,
        actor=current_user.username if current_user else "admin",
        action="saved",
        entity="role",
        entity_id=r.id,
        entity_name=r.roleName,
        company_id=target_company
    )

    return {"code": 0, "data": r.id}

@router.post("/role/delete")
def role_delete(
    body: dict = Body(...),
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    from app.auth import get_user_company_id
    current_user = get_current_user_from_header(authorization, db)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tizimga kirilmagan yoki sessiya yaroqsiz")
    check_user_access(current_user, ["role:manage", "role", "/authorization/role"], db)

    target_company = get_user_company_id(authorization, db)
    role_id = body.get("id")
    if not role_id:
        return {"code": 500, "message": "ID is required"}

    role = db.query(models.Role).filter(models.Role.id == str(role_id)).first()
    if not role:
        return {"code": 500, "message": "Role not found"}

    # Base system roles cannot be deleted
    if str(role.id) in ["1", "2", "3"] or (role.company_id == "comp-default" and target_company != "comp-default"):
        return {"code": 403, "message": "Tizim asosiy rollarini o'chirib bo'lmaydi!"}

    if target_company and target_company != "comp-default" and role.company_id != target_company:
        return {"code": 403, "message": "Siz faqat o'z tashkilotingiz rollarini o'chira olasiz!"}

    role_name = role.roleName
    db.delete(role)
    db.commit()
    from app.routers.activity import log_activity
    log_activity(
        db=db,
        actor=current_user.username if current_user else "admin",
        action="deleted",
        entity="role",
        entity_id=str(role_id),
        entity_name=role_name,
        company_id=target_company
    )
    return {"code": 0, "data": True}
