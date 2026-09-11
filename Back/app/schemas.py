from pydantic import BaseModel, Field
from typing import List, Optional, Any, Union
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# User Schemas
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = "worker"
    roleId: Optional[str] = "2"
    email: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[str] = None
    permissions: Optional[List[str]] = []
    avatar: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    role: str
    roleId: str
    email: Optional[str] = None
    department_id: Optional[str] = None
    create_time: str
    permissions: List[str]
    avatar: Optional[str] = None

    class Config:
        from_attributes = True

# Role Schemas
class RoleCreate(BaseModel):
    id: str
    roleName: str
    status: Optional[int] = 1
    remark: Optional[str] = None
    permissions: Optional[List[Any]] = []

class RoleResponse(BaseModel):
    id: str
    roleName: str
    status: int
    remark: Optional[str] = None
    createTime: str
    permissions: List[Any]

    class Config:
        from_attributes = True

# Department Schemas
class DepartmentCreate(BaseModel):
    id: Optional[str] = None
    departmentName: str
    parentId: Optional[str] = None
    status: Optional[int] = 1
    remark: Optional[str] = None

class DepartmentResponse(BaseModel):
    id: str
    departmentName: str
    parentId: Optional[str] = None
    status: int
    remark: Optional[str] = None
    createTime: str

    class Config:
        from_attributes = True

class DepartmentUserDept(BaseModel):
    id: Optional[Union[str, int]] = None
    departmentName: Optional[str] = None

class DepartmentUserSave(BaseModel):
    id: Optional[int] = None
    username: str
    password: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    roleId: Optional[Union[str, int]] = None
    department: Optional[Union[DepartmentUserDept, dict, str, int]] = None
    department_id: Optional[str] = None
    departmentId: Optional[str] = None


class ProductPackagingCreate(BaseModel):
    id: Optional[str] = None
    unit_name: str
    conversion_factor: float
    price: float
    cost: Optional[float] = 0.0
    shtrix_code: Optional[str] = None
    is_base_unit: Optional[bool] = False

class ProductPackagingResponse(BaseModel):
    id: str
    product_id: str
    unit_name: str
    conversion_factor: float
    price: float
    cost: float
    shtrix_code: Optional[str] = None
    is_base_unit: bool

    class Config:
        from_attributes = True

# Product Schemas
class ProductCreate(BaseModel):
    id: Optional[str] = None
    productName: str
    SKU: str
    category: str
    price: float
    cost: float
    quantityInStock: float
    status: Optional[int] = 1
    classifier_id: Optional[int] = None
    shtrix_code: Optional[str] = None
    mxik_code: Optional[str] = None
    brand_name: Optional[str] = None
    attribute_name: Optional[str] = None
    unit: Optional[str] = None
    image_url: Optional[str] = None
    expiration_date: Optional[str] = None
    remark: Optional[str] = None
    packagings: Optional[List[ProductPackagingCreate]] = None

class ProductResponse(BaseModel):
    id: str
    productName: str
    SKU: str
    category: str
    price: float
    cost: float
    quantityInStock: float
    status: int
    classifier_id: Optional[int] = None
    shtrix_code: Optional[str] = None
    mxik_code: Optional[str] = None
    brand_name: Optional[str] = None
    attribute_name: Optional[str] = None
    unit: Optional[str] = None
    image_url: Optional[str] = None
    expiration_date: Optional[str] = None
    remark: Optional[str] = None
    createTime: str
    packagings: Optional[List[ProductPackagingResponse]] = []

    class Config:
        from_attributes = True



# Worker Schemas
class WorkerCreate(BaseModel):
    id: Optional[str] = None
    name: str
    account: str
    employee_code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    departmentId: Optional[str] = None
    hireDate: Optional[str] = None
    status: Optional[int] = 1
    baseSalary: Optional[float] = 0.0
    remark: Optional[str] = None
    avatar: Optional[str] = None
    password: Optional[str] = None
    adminPassword: Optional[str] = None

class WorkerResponse(BaseModel):
    id: str
    name: str
    account: str
    employee_code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    departmentId: Optional[str] = None
    hireDate: str
    status: int
    baseSalary: float
    remark: Optional[str] = None
    avatar: Optional[str] = None

    class Config:
        from_attributes = True

# Salary Schemas
class SalaryCreate(BaseModel):
    id: Optional[str] = None
    workerId: str
    baseSalary: float
    allowance: Optional[float] = 0.0
    deduction: Optional[float] = 0.0
    payDate: Optional[str] = None
    status: Optional[str] = "pending"
    remark: Optional[str] = None

class SalaryResponse(BaseModel):
    id: str
    workerId: str
    baseSalary: float
    allowance: float
    deduction: float
    netSalary: float
    payDate: str
    status: str
    remark: Optional[str] = None
    worker: Optional[WorkerResponse] = None

    class Config:
        from_attributes = True

class SalaryWorkerPayoutItem(BaseModel):
    workerId: str
    baseSalary: Optional[float] = 0.0
    allowance: Optional[float] = 0.0
    deduction: Optional[float] = 0.0
    period_month: Optional[str] = None
    remark: Optional[str] = None

class SalaryPayout(BaseModel):
    workerIds: Optional[List[str]] = []
    items: Optional[List[SalaryWorkerPayoutItem]] = []
    period_month: Optional[str] = None
    allowance: Optional[float] = 0.0
    deduction: Optional[float] = 0.0
    remark: Optional[str] = None


# Position Schemas
class PositionCreate(BaseModel):
    id: Optional[str] = None
    positionName: str
    departmentId: Optional[str] = None
    baseSalary: Optional[float] = 0.0
    status: Optional[int] = 1
    remark: Optional[str] = None

class PositionResponse(BaseModel):
    id: str
    positionName: str
    departmentId: Optional[str] = None
    baseSalary: float
    status: int
    remark: Optional[str] = None
    createTime: str

    class Config:
        from_attributes = True


# Cutting Stage Schemas
class CuttingStageCreate(BaseModel):
    id: Optional[str] = None
    name: str
    is_system: Optional[int] = 0
    price: Optional[float] = 0.0
    duration: Optional[int] = 0

class CuttingStageResponse(BaseModel):
    id: str
    name: str
    is_system: int
    price: float
    duration: int
    createTime: str

    class Config:
        from_attributes = True


# Cutting Process Schemas
class CuttingProcessCreate(BaseModel):
    id: Optional[str] = None
    name: str
    remark: Optional[str] = None
    stages: Optional[List[Any]] = []

class CuttingProcessResponse(BaseModel):
    id: str
    name: str
    remark: Optional[str] = None
    stages: List[Any]
    createTime: str

    class Config:
        from_attributes = True


# Cutting Order Item Schemas
class CuttingOrderItemCreate(BaseModel):
    id: Optional[str] = None
    productId: str
    category: Optional[str] = None
    color: Optional[str] = None
    code: Optional[str] = None
    cuttingProcessId: Optional[str] = None
    quantity: int = Field(..., gt=0)
    size_breakdown: Optional[dict] = {}
    material_consumptions: Optional[List[Any]] = []
    process_snapshot: Optional[List[Any]] = []

class CuttingOrderItemResponse(BaseModel):
    id: str
    orderId: str
    productId: str
    category: Optional[str] = None
    color: Optional[str] = None
    code: Optional[str] = None
    cuttingProcessId: Optional[str] = None
    quantity: int
    size_breakdown: dict
    material_consumptions: List[Any]
    process_snapshot: List[Any]
    product: Optional[ProductResponse] = None
    cutting_process: Optional[CuttingProcessResponse] = None

    class Config:
        from_attributes = True


# Cutting Order Schemas
class CuttingOrderCreate(BaseModel):
    id: Optional[str] = None
    order_number: str
    project: Optional[str] = None
    order_name: Optional[str] = None
    document_date: Optional[str] = None
    responsible_user_ids: Optional[List[str]] = []
    status: Optional[str] = "created"
    items: List[CuttingOrderItemCreate]

class CuttingOrderResponse(BaseModel):
    id: str
    order_number: str
    project: Optional[str] = None
    order_name: Optional[str] = None
    document_date: str
    responsible_user_ids: List[str]
    status: str
    total_quantity: int
    createTime: str
    items: Optional[List[CuttingOrderItemResponse]] = []

    class Config:
        from_attributes = True


# Cutting Task Schemas
class CuttingTaskResponse(BaseModel):
    id: str
    orderId: str
    orderItemId: str
    stageId: str
    position: int
    quantity: int
    status: str
    order_number_snapshot: Optional[str] = None
    order_name_snapshot: Optional[str] = None
    process_name_snapshot: Optional[str] = None
    stage_name_snapshot: Optional[str] = None
    product_name_snapshot: Optional[str] = None
    createTime: str
    order: Optional[CuttingOrderResponse] = None
    stage: Optional[CuttingStageResponse] = None

    class Config:
        from_attributes = True


# Cutting Task Execution Schemas
class CuttingTaskExecutionCreate(BaseModel):
    taskId: str
    workerId: str
    quantity: int
    period_month: Optional[str] = None
    comment: Optional[str] = None

class CuttingTaskExecutionResponse(BaseModel):
    id: str
    taskId: str
    workerId: str
    quantity: int
    period_month: str
    comment: Optional[str] = None
    createTime: str
    task: Optional[CuttingTaskResponse] = None
    worker: Optional[WorkerResponse] = None

    class Config:
        from_attributes = True


# QR Code Schemas
class QrCodeCreate(BaseModel):
    taskId: str
    quantity: int = Field(..., gt=0)
    status: Optional[str] = "created"
    workerId: Optional[str] = None

class QrCodeResponse(BaseModel):
    id: str
    code: str
    taskId: str
    quantity: int
    status: Optional[str] = "created"
    workerId: Optional[str] = None
    createTime: str
    task: Optional[CuttingTaskResponse] = None

    class Config:
        from_attributes = True


# Staff Adjustment Schemas
class StaffAdjustmentCreate(BaseModel):
    id: Optional[str] = None
    workerId: str
    document_type: str
    amount: float
    period_month: Optional[str] = None
    description: Optional[str] = None

class StaffAdjustmentResponse(BaseModel):
    id: str
    workerId: str
    document_type: str
    amount: float
    period_month: str
    description: Optional[str] = None
    createTime: str
    worker: Optional[WorkerResponse] = None

    class Config:
        from_attributes = True


# Staff Timesheet Schemas
class StaffTimesheetCreate(BaseModel):
    id: Optional[str] = None
    date: str
    status: Optional[str] = "active"
    records: List[Any]

class StaffTimesheetResponse(BaseModel):
    id: str
    date: str
    status: str
    records: List[Any]
    createTime: str

    class Config:
        from_attributes = True


# Staff Output Schemas
class StaffOutputCreate(BaseModel):
    id: Optional[str] = None
    workerId: Optional[str] = None
    workerName: Optional[str] = None
    name: str
    amount: float
    period_month: Optional[str] = None
    comment: Optional[str] = None

class StaffOutputResponse(BaseModel):
    id: str
    workerId: Optional[str] = None
    workerName: Optional[str] = None
    name: str
    amount: float
    period_month: Optional[str] = None
    comment: Optional[str] = None
    createTime: str
    worker: Optional[WorkerResponse] = None

    class Config:
        from_attributes = True




# Classifier Schemas
class ClassifierItemCreate(BaseModel):
    group_name: Optional[str] = None
    class_name: Optional[str] = None
    position_name: Optional[str] = None
    subposition_name: Optional[str] = None
    brand_name: Optional[str] = None
    attribute_name: Optional[str] = None
    mxik_code: Optional[str] = None
    mxik_name: Optional[str] = None
    shtrix_code: Optional[str] = None
    unit_group: Optional[str] = None
    unit: Optional[str] = None
    package_unit: Optional[str] = None
    source_file: Optional[str] = None

class ClassifierItemResponse(BaseModel):
    id: int
    group_name: Optional[str] = None
    class_name: Optional[str] = None
    position_name: Optional[str] = None
    subposition_name: Optional[str] = None
    brand_name: Optional[str] = None
    attribute_name: Optional[str] = None
    mxik_code: Optional[str] = None
    mxik_name: Optional[str] = None
    shtrix_code: Optional[str] = None
    unit_group: Optional[str] = None
    unit: Optional[str] = None
    package_unit: Optional[str] = None
    source_file: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class ClassifierListResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: List[ClassifierItemResponse]
    total: int
    page: int
    page_size: int

# Sales Schemas
class SaleItemCreate(BaseModel):
    product_id: str
    product_name: Optional[str] = None
    shtrix_code: Optional[str] = None
    price: float
    cost: Optional[float] = 0.0
    quantity: float
    unit_name: Optional[str] = None
    conversion_factor: Optional[float] = 1.0

class SaleCreate(BaseModel):
    cashier_name: Optional[str] = "admin"
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    payment_method: Optional[str] = "naqd"
    paid_amount: Optional[float] = None
    debt_amount: Optional[float] = None
    discount: Optional[float] = 0.0
    remark: Optional[str] = None
    items: List[SaleItemCreate]


class DebtPaymentCreate(BaseModel):
    customer_name: str
    customer_phone: Optional[str] = None
    amount: float
    payment_method: Optional[str] = "naqd"
    cashier_name: Optional[str] = "admin"
    remark: Optional[str] = None


# Device Token Schemas
class DevicePairRequest(BaseModel):
    user_id: Optional[int] = None
    device_name: str

class DevicePairTokenResponse(BaseModel):
    pair_code: str
    token: str
    expires_at: datetime
    device_name: str
    user_id: int
    qr_payload: Optional[str] = None
    created_at: Optional[datetime] = None

class DeviceTokenOut(BaseModel):
    id: int
    user_id: int
    device_name: str
    token: str
    pair_code: Optional[str] = None
    status: str
    expires_at: Optional[datetime] = None
    created_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DeviceTokenListResponse(BaseModel):
    total: int
    list: List[DeviceTokenOut]


# Sales Push & Phone POS Schemas
class SalesPushItem(BaseModel):
    product_id: Union[int, str]
    quantity: float
    price: float
    product_name: Optional[str] = None
    cost: Optional[float] = None
    shtrix_code: Optional[str] = None
    unit_name: Optional[str] = None
    conversion_factor: Optional[float] = 1.0


class SalesPushCreate(BaseModel):
    device_token: Optional[str] = None
    items: List[SalesPushItem]
    pc_user_id: int

class SalesPushRespond(BaseModel):
    push_id: str
    action: str  # "accept" or "decline"

class PhoneCheckoutRequest(BaseModel):
    device_token: Optional[str] = None
    items: List[SalesPushItem]
    payment_type: str  # "cash", "card", "debt"
    total_amount: float
    paid_amount: Optional[float] = 0.0
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    discount: Optional[float] = 0.0
    remark: Optional[str] = None


class MonthlyFinancialSnapshotClose(BaseModel):
    period_month: str  # e.g. "2026-07"
    remark: Optional[str] = None
    override_revenue: Optional[float] = None
    override_cogs: Optional[float] = None
    override_staff_salaries: Optional[float] = None
    override_short_term: Optional[float] = None


class MonthlyFinancialSnapshotResponse(BaseModel):
    id: str
    period_month: str
    revenue: float
    cogs: float
    staff_salaries: float
    short_term_outputs: float
    total_expenses: float
    net_profit: float
    profit_margin: float
    sales_count: int
    status: str
    remark: Optional[str] = None
    closed_by: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PeriodCompareRequest(BaseModel):
    period1_start: Optional[str] = None
    period1_end: Optional[str] = None
    period2_start: Optional[str] = None
    period2_end: Optional[str] = None


