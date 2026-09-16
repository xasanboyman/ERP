import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(String, default="comp-default", index=True)
    actor = Column(String, default="admin")          # who did it
    action = Column(String)                          # created | updated | deleted
    entity = Column(String)                          # worker | product | salary | department
    entity_id = Column(String, nullable=True)        # the affected record id
    entity_name = Column(String, nullable=True)      # human-readable name of record
    timestamp = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class Company(Base):
    __tablename__ = "companies"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    code = Column(String, unique=True, index=True)
    plan = Column(String, default="basic", index=True)  # basic | pro
    billing_cycle = Column(String, default="monthly")   # monthly | yearly
    subscription_expires_at = Column(String, nullable=True)
    status = Column(Integer, default=1)                 # 1 = active, 0 = inactive/suspended
    max_users = Column(Integer, default=10)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    features = Column(JSON, default=lambda: {"ai": False, "upcoming": False})
    created_at = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)          # e.g. "Alibek Hasanov"
    role = Column(String, default="worker")
    roleId = Column(String, default="2")
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    department_id = Column(String, nullable=True)
    avatar = Column(Text, nullable=True)               # base64 data-URI or external URL
    create_time = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    permissions = Column(JSON, default=list)

    company = relationship("Company", foreign_keys=[company_id])

class Role(Base):
    __tablename__ = "roles"
    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, default="comp-default", index=True)
    roleName = Column(String, unique=True)
    status = Column(Integer, default=1)  # 1 = enable, 0 = disable
    remark = Column(Text, nullable=True)
    createTime = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    permissions = Column(JSON, default=list)

class Department(Base):
    __tablename__ = "departments"
    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, default="comp-default", index=True)
    departmentName = Column(String)
    parentId = Column(String, nullable=True)
    status = Column(Integer, default=1)  # 1 = active, 0 = inactive
    remark = Column(Text, nullable=True)
    createTime = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class Branch(Base):
    __tablename__ = "branches"
    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, default="comp-default", index=True)
    name = Column(String, index=True)
    code = Column(String, unique=True, index=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class ProductPackaging(Base):
    __tablename__ = "product_packagings"
    id = Column(String, primary_key=True, index=True)
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"), index=True)
    unit_name = Column(String, nullable=False)
    conversion_factor = Column(Float, nullable=False, default=1.0)
    price = Column(Float, nullable=False, default=0.0)
    cost = Column(Float, default=0.0)
    shtrix_code = Column(String, unique=True, index=True, nullable=True)
    is_base_unit = Column(Boolean, default=False)

    product = relationship("Product", back_populates="packagings")


class Product(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("companies.id", ondelete="CASCADE"), default="comp-default", index=True)
    productName = Column(String, index=True)
    SKU = Column(String, index=True)
    category = Column(String, index=True)
    price = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)
    quantityInStock = Column(Float, default=0.0)
    status = Column(Integer, default=1)  # 1 = in stock, 0 = out of stock
    classifier_id = Column(String, nullable=True)
    shtrix_code = Column(String, index=True, nullable=True)
    mxik_code = Column(String, index=True, nullable=True)
    brand_name = Column(String, index=True, nullable=True)
    attribute_name = Column(String, nullable=True)
    unit = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    expiration_date = Column(String, nullable=True, index=True)
    remark = Column(Text, nullable=True)
    createTime = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    packagings = relationship("ProductPackaging", back_populates="product", cascade="all, delete-orphan")
    company = relationship("Company", foreign_keys=[company_id])



class Worker(Base):
    __tablename__ = "workers"
    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("companies.id", ondelete="CASCADE"), default="comp-default", index=True)
    name = Column(String, index=True)
    account = Column(String, unique=True, index=True)
    employee_code = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    role = Column(String, nullable=True)
    departmentId = Column(String, nullable=True)
    hireDate = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d"))
    status = Column(Integer, default=1)  # 1 = active, 0 = suspended
    baseSalary = Column(Float, default=0.0)
    remark = Column(Text, nullable=True)
    avatar = Column(Text, nullable=True)               # base64 data-URI or external URL

class Salary(Base):
    __tablename__ = "salaries"
    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, default="comp-default", index=True)
    workerId = Column(String, ForeignKey("workers.id", ondelete="CASCADE"))
    baseSalary = Column(Float, default=0.0)
    allowance = Column(Float, default=0.0)
    deduction = Column(Float, default=0.0)
    netSalary = Column(Float, default=0.0)
    payDate = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d"))
    status = Column(String, default="pending")  # paid, pending, processing
    remark = Column(Text, nullable=True)
    
    worker = relationship("Worker")

class Menu(Base):
    __tablename__ = "menus"
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String)
    name = Column(String)
    component = Column(String)
    redirect = Column(String, nullable=True)
    parentId = Column(Integer, nullable=True)
    title = Column(String)
    meta_title = Column(String)
    meta_icon = Column(String, nullable=True)
    status = Column(Integer, default=1)
    type = Column(Integer, default=1)  # 0 = dir, 1 = menu

class WorkplaceProject(Base):
    __tablename__ = "workplace_projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    icon = Column(String)
    message = Column(String)
    personal = Column(String)
    time = Column(String)

class WorkplaceDynamic(Base):
    __tablename__ = "workplace_dynamics"
    id = Column(Integer, primary_key=True, index=True)
    keys = Column(JSON)  # e.g., ["workplace.push", "Github"]
    time = Column(String)

class WorkplaceTeam(Base):
    __tablename__ = "workplace_teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    icon = Column(String)

class WorkplaceRadar(Base):
    __tablename__ = "workplace_radars"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    max = Column(Integer)
    personal = Column(Integer)
    team = Column(Integer)

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    completed = Column(Integer, default=0)  # 0 = pending, 1 = completed


class Position(Base):
    __tablename__ = "positions"
    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, default="comp-default", index=True)
    positionName = Column(String, index=True)
    departmentId = Column(String, nullable=True)
    baseSalary = Column(Float, default=0.0)
    status = Column(Integer, default=1)  # 1 = active, 0 = inactive
    remark = Column(Text, nullable=True)
    createTime = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class CuttingStage(Base):
    __tablename__ = "cutting_stages"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    is_system = Column(Integer, default=0)  # 0 = custom, 1 = system
    price = Column(Float, default=0.0)
    duration = Column(Integer, default=0)  # seconds
    createTime = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class CuttingProcess(Base):
    __tablename__ = "cutting_processes"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    remark = Column(Text, nullable=True)
    stages = Column(JSON, default=list)  # list of stage objects or IDs
    createTime = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class CuttingOrder(Base):
    __tablename__ = "cutting_orders"
    id = Column(String, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    project = Column(String, nullable=True)
    order_name = Column(String, nullable=True)
    document_date = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d"))
    responsible_user_ids = Column(JSON, default=list)
    status = Column(String, default="created")  # created, in_production, in_progress, completed, cancelled, partially_shipped, shipped
    total_quantity = Column(Integer, default=0)
    createTime = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    items = relationship("CuttingOrderItem", backref="order", cascade="all, delete-orphan")


class CuttingOrderItem(Base):
    __tablename__ = "cutting_order_items"
    id = Column(String, primary_key=True, index=True)
    orderId = Column(String, ForeignKey("cutting_orders.id", ondelete="CASCADE"))
    productId = Column(String, ForeignKey("products.id", ondelete="CASCADE"))
    category = Column(String, nullable=True)
    color = Column(String, nullable=True)
    code = Column(String, nullable=True)
    cuttingProcessId = Column(String, ForeignKey("cutting_processes.id", ondelete="SET NULL"), nullable=True)
    quantity = Column(Integer, default=0)
    size_breakdown = Column(JSON, default=dict)
    material_consumptions = Column(JSON, default=list)
    process_snapshot = Column(JSON, default=list)

    product = relationship("Product")
    cutting_process = relationship("CuttingProcess")


class CuttingTask(Base):
    __tablename__ = "cutting_tasks"
    id = Column(String, primary_key=True, index=True)
    orderId = Column(String, ForeignKey("cutting_orders.id", ondelete="CASCADE"))
    orderItemId = Column(String, ForeignKey("cutting_order_items.id", ondelete="CASCADE"))
    stageId = Column(String, ForeignKey("cutting_stages.id", ondelete="SET NULL"), nullable=True)
    position = Column(Integer, default=0)
    quantity = Column(Integer, default=0)
    status = Column(String, default="created")  # created, in_progress, completed
    order_number_snapshot = Column(String, nullable=True)
    order_name_snapshot = Column(String, nullable=True)
    process_name_snapshot = Column(String, nullable=True)
    stage_name_snapshot = Column(String, nullable=True)
    product_name_snapshot = Column(String, nullable=True)
    createTime = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    order = relationship("CuttingOrder")
    order_item = relationship("CuttingOrderItem")
    stage = relationship("CuttingStage")


class CuttingTaskExecution(Base):
    __tablename__ = "cutting_task_executions"
    id = Column(String, primary_key=True, index=True)
    taskId = Column(String, ForeignKey("cutting_tasks.id", ondelete="CASCADE"))
    workerId = Column(String, ForeignKey("workers.id", ondelete="CASCADE"))
    quantity = Column(Integer, default=0)
    period_month = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m"))
    comment = Column(Text, nullable=True)
    createTime = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    task = relationship("CuttingTask")
    worker = relationship("Worker")


class QrCode(Base):
    __tablename__ = "qr_codes"
    id = Column(String, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    taskId = Column(String, ForeignKey("cutting_tasks.id", ondelete="CASCADE"))
    quantity = Column(Integer, default=0)
    status = Column(String, default="created")
    workerId = Column(String, ForeignKey("workers.id", ondelete="SET NULL"), nullable=True)
    createTime = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    task = relationship("CuttingTask")
    worker = relationship("Worker")


class StaffAdjustment(Base):
    __tablename__ = "staff_adjustments"
    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, default="comp-default", index=True)
    workerId = Column(String, ForeignKey("workers.id", ondelete="CASCADE"))
    document_type = Column(String)  # bonus, fine, advance
    amount = Column(Float, default=0.0)
    period_month = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m"))
    description = Column(Text, nullable=True)
    createTime = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    worker = relationship("Worker")


class StaffTimesheet(Base):
    __tablename__ = "staff_timesheets"
    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, default="comp-default", index=True)
    date = Column(String, index=True)  # YYYY-MM-DD
    status = Column(String, default="active")  # active, archived
    records = Column(JSON, default=list)  # list of worker attendance (workerId, status, hours)
    createTime = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class StaffOutput(Base):
    __tablename__ = "staff_outputs"
    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, default="comp-default", index=True)
    workerId = Column(String, nullable=True)
    workerName = Column(String, nullable=True)
    name = Column(String)  # operation name / task description
    amount = Column(Float, default=0.0)
    period_month = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d"))
    comment = Column(Text, nullable=True)
    createTime = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))



class ClassifierItem(Base):
    __tablename__ = "classifier_items"
    id = Column(String, primary_key=True, index=True)
    group_name = Column(String, nullable=True, index=True)
    class_name = Column(String, nullable=True, index=True)
    position_name = Column(String, nullable=True, index=True)
    subposition_name = Column(String, nullable=True, index=True)
    brand_name = Column(String, nullable=True, index=True)
    attribute_name = Column(String, nullable=True, index=True)
    mxik_code = Column(String, nullable=True, index=True)
    mxik_name = Column(Text, nullable=True)
    shtrix_code = Column(String, nullable=True, index=True)
    unit_group = Column(String, nullable=True)
    unit = Column(String, nullable=True)
    package_unit = Column(String, nullable=True)
    source_file = Column(String, nullable=True)
    image_url = Column(String, nullable=True)


class Sale(Base):
    __tablename__ = "sales"
    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("companies.id", ondelete="CASCADE"), default="comp-default", index=True)
    receipt_number = Column(String, unique=True, index=True)
    cashier_name = Column(String, index=True, default="admin")
    customer_name = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    payment_method = Column(String, default="naqd")  # naqd, karta, otkazma, nasiya
    total_amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    debt_amount = Column(Float, default=0.0)
    total_items = Column(Integer, default=0)
    discount = Column(Float, default=0.0)
    remark = Column(Text, nullable=True)
    created_at = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    company = relationship("Company", foreign_keys=[company_id])



class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(String, primary_key=True, index=True)
    sale_id = Column(String, ForeignKey("sales.id", ondelete="CASCADE"), index=True)
    product_id = Column(String, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    product_name = Column(String)
    shtrix_code = Column(String, nullable=True)
    price = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)
    quantity = Column(Float, default=1.0)
    unit_name = Column(String, nullable=True)
    conversion_factor = Column(Float, default=1.0)
    total = Column(Float, default=0.0)

    sale = relationship("Sale", back_populates="items")



class DebtPayment(Base):
    __tablename__ = "debt_payments"
    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, default="comp-default", index=True)
    receipt_number = Column(String, unique=True, index=True)
    customer_name = Column(String, index=True)
    customer_phone = Column(String, nullable=True)
    amount = Column(Float, default=0.0)
    payment_method = Column(String, default="naqd")  # naqd, karta, otkazma
    cashier_name = Column(String, default="admin")
    remark = Column(Text, nullable=True)
    created_at = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class DeviceToken(Base):
    __tablename__ = "device_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    device_name = Column(String, nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    pair_code = Column(String, nullable=True)
    status = Column(String, default="active", nullable=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    user = relationship("User", backref="device_tokens")


class SalesPush(Base):
    __tablename__ = "sales_pushes"

    id = Column(String, primary_key=True, index=True)
    device_token = Column(String, nullable=False, index=True)
    pc_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    device_name = Column(String, nullable=True)
    items_json = Column(Text, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending, accepted, declined
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    pc_user = relationship("User", backref="sales_pushes")


class MonthlyFinancialSnapshot(Base):
    __tablename__ = "monthly_financial_snapshots"

    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, default="comp-default", index=True)
    period_month = Column(String, index=True, nullable=False)  # e.g. "2026-07"
    revenue = Column(Float, default=0.0)
    cogs = Column(Float, default=0.0)
    staff_salaries = Column(Float, default=0.0)
    short_term_outputs = Column(Float, default=0.0)
    total_expenses = Column(Float, default=0.0)
    net_profit = Column(Float, default=0.0)
    profit_margin = Column(Float, default=0.0)
    sales_count = Column(Integer, default=0)
    status = Column(String, default="closed")  # "closed", "draft"
    remark = Column(Text, nullable=True)
    closed_by = Column(String, default="admin")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
