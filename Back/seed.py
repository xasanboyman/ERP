import datetime
from app.database import SessionLocal, Base, engine
from app import models, crud, schemas
from import_classifiers import import_all_classifiers


def seed_database():
    print("Initializing database tables...")
    Base.metadata.drop_all(bind=engine)  # Fresh start
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Seeding Users...")
        admin_user = crud.create_user(db, schemas.UserCreate(
            username="admin",
            password="admin",
            role="admin",
            roleId="1",
            department_id="DEPT-HQ",
            permissions=["*.*.*"]
        ))
        test_user = crud.create_user(db, schemas.UserCreate(
            username="test",
            password="test",
            role="test",
            roleId="2",
            department_id="DEPT-RD",
            permissions=["example:dialog:create", "example:dialog:delete"]
        ))
        test_user_dept = crud.create_user(db, schemas.UserCreate(
            username="test_dept_user",
            password="password123",
            role="worker",
            roleId="2",
            department_id="DEPT-RD",
            permissions=["example:dialog:create"]
        ))
        
        print("Seeding Roles...")
        crud.create_role(db, schemas.RoleCreate(
            id="1",
            roleName="Super Administrator",
            status=1,
            remark="Tizimning barcha boshqaruv huquqlariga ega",
            permissions=["*.*.*"]
        ))
        crud.create_role(db, schemas.RoleCreate(
            id="2",
            roleName="Administrator",
            status=1,
            remark="Oddiy administrator",
            permissions=["*.*.*"]
        ))
        crud.create_role(db, schemas.RoleCreate(
            id="3",
            roleName="Oddiy xodim",
            status=1,
            remark="Faqat ish joyi, kassa (POS) va mahsulotlar bilan ishlash huquqiga ega",
            permissions=[
                "/dashboard",
                "/dashboard/workplace",
                "dashboard:workplace",
                "/product",
                "/product/list",
                "product:view",
                "/sales",
                "/sales/pos",
                "sales:pos",
                "sales:view",
                "sales:create"
            ]
        ))

        print("Seeding Departments...")
        hq = crud.create_department(db, schemas.DepartmentCreate(
            id="DEPT-HQ",
            departmentName="Bosh Ofis",
            parentId=None,
            status=1,
            remark="Kompaniyaning bosh qarorgohi"
        ))
        bj = crud.create_department(db, schemas.DepartmentCreate(
            id="DEPT-BJ",
            departmentName="Toshkent filiali",
            parentId=None,
            status=1,
            remark="Toshkent shahridagi texnik va savdo markazi"
        ))
        rd = crud.create_department(db, schemas.DepartmentCreate(
            id="DEPT-RD",
            departmentName="Tadqiqot va ishlanmalar (R&D)",
            parentId="DEPT-HQ",
            status=1,
            remark="Dasturiy ta'minotni ishlab chiqish bo'limi"
        ))
        prod = crud.create_department(db, schemas.DepartmentCreate(
            id="DEPT-PD",
            departmentName="Mahsulotlar bo'limi",
            parentId="DEPT-HQ",
            status=1,
            remark="Tizim talablarini tahlil qilish va rejalashtirish"
        ))
        sales = crud.create_department(db, schemas.DepartmentCreate(
            id="DEPT-SL",
            departmentName="Sotuvlar bo'limi",
            parentId="DEPT-BJ",
            status=1,
            remark="Yangi shartnomalar tuzish va mijozlar bilan ishlash"
        ))

        print("Seeding Products... (Clean slate for real textile inventory)")
        # Clean slate: No mock electronic products seeded.


        print("Seeding Workers...")
        w1 = crud.create_worker(db, schemas.WorkerCreate(
            id="WORK-001",
            name="Anvar Soliyev",
            account="anvars",
            email="anvar.soliyev@example.com",
            phone="+998901234567",
            role="Katta dasturchi",
            departmentId="DEPT-RD",
            hireDate="2024-03-01",
            status=1,
            baseSalary=8500.00,
            remark="Backend mikroxizmatlar arxitekturasini rivojlantirish uchun mas'ul"
        ))
        w2 = crud.create_worker(db, schemas.WorkerCreate(
            id="WORK-002",
            name="Dilshod Karimov",
            account="dilshodk",
            email="dilshod.karimov@example.com",
            phone="+998907654321",
            role="Mahsulot direktori",
            departmentId="DEPT-PD",
            hireDate="2023-05-15",
            status=1,
            baseSalary=9800.00,
            remark="ERP tizimining yo'nalishlarini loyihalashni muvofiqlashtirish"
        ))
        w3 = crud.create_worker(db, schemas.WorkerCreate(
            id="WORK-003",
            name="Jasur Alimov",
            account="jasura",
            email="jasur.alimov@example.com",
            phone="+998935554433",
            role="Katta mijoz menedjeri",
            departmentId="DEPT-SL",
            hireDate="2025-01-10",
            status=1,
            baseSalary=6000.00,
            remark="Yirik korporativ mijozlar bilan aloqalarni o'rnatish"
        ))

        print("Seeding Salaries...")
        # Previous Month Salaries (June 2026)
        crud.create_salary(db, schemas.SalaryCreate(
            workerId="WORK-001",
            baseSalary=8500.00,
            allowance=500.00,
            deduction=200.00,
            payDate="2026-06-15",
            status="paid",
            remark="2026-yil Iyun oyi uchun oylik maosh hisobi"
        ))
        crud.create_salary(db, schemas.SalaryCreate(
            workerId="WORK-002",
            baseSalary=9800.00,
            allowance=800.00,
            deduction=100.00,
            payDate="2026-06-15",
            status="paid",
            remark="2026-yil Iyun oyi uchun oylik maosh hisobi"
        ))
        crud.create_salary(db, schemas.SalaryCreate(
            workerId="WORK-003",
            baseSalary=6000.00,
            allowance=1200.00,
            deduction=150.00,
            payDate="2026-06-15",
            status="paid",
            remark="2026-yil Iyun oyi uchun oylik maosh va mukofot puli"
        ))

        print("Seeding Workplace Dashboard Data...")
        # Projects
        db.add_all([
            models.WorkplaceProject(name="FastAPI", icon="logos:fastapi-icon", message="workplace.introduction", personal="ERP Team", time="2026-07-06"),
            models.WorkplaceProject(name="Vue 3", icon="logos:vue", message="workplace.introduction", personal="Admin Team", time="2026-07-06"),
            models.WorkplaceProject(name="Element Plus", icon="logos:element-ui", message="workplace.introduction", personal="Design Team", time="2026-07-06"),
            models.WorkplaceProject(name="SQLite", icon="logos:sqlite", message="workplace.introduction", personal="Database Team", time="2026-07-06"),
            models.WorkplaceProject(name="Webpack", icon="logos:webpack", message="workplace.introduction", personal="Build Team", time="2026-07-06"),
            models.WorkplaceProject(name="Vite", icon="vscode-icons:file-type-vite", message="workplace.introduction", personal="Core Team", time="2026-07-06")
        ])
        
        # Teams
        db.add_all([
            models.WorkplaceTeam(name="Github", icon="akar-icons:github-fill"),
            models.WorkplaceTeam(name="Vue", icon="logos:vue"),
            models.WorkplaceTeam(name="Angular", icon="logos:angular-icon"),
            models.WorkplaceTeam(name="React", icon="logos:react"),
            models.WorkplaceTeam(name="Webpack", icon="logos:webpack"),
            models.WorkplaceTeam(name="Vite", icon="vscode-icons:file-type-vite")
        ])

        # Dynamics
        db.add_all([
            models.WorkplaceDynamic(keys=["workplace.push", "Github"], time="2026-07-06 14:00:00"),
            models.WorkplaceDynamic(keys=["workplace.push", "Github"], time="2026-07-06 13:30:00"),
            models.WorkplaceDynamic(keys=["workplace.push", "Github"], time="2026-07-06 13:00:00"),
            models.WorkplaceDynamic(keys=["workplace.push", "Github"], time="2026-07-06 12:30:00"),
            models.WorkplaceDynamic(keys=["workplace.push", "Github"], time="2026-07-06 12:00:00")
        ])

        # Radar Indices
        db.add_all([
            models.WorkplaceRadar(name="workplace.quote", max=65, personal=42, team=50),
            models.WorkplaceRadar(name="workplace.contribution", max=160, personal=30, team=140),
            models.WorkplaceRadar(name="workplace.hot", max=300, personal=20, team=28),
            models.WorkplaceRadar(name="workplace.yield", max=130, personal=35, team=35),
            models.WorkplaceRadar(name="workplace.follow", max=100, personal=80, team=90)
        ])

        # Todos
        db.add_all([
            models.Todo(title="Mahsulotlar katalogini tahlil qilish", completed=0),
            models.Todo(title="Xodimlar oylik maoshlarini hisoblash", completed=1),
            models.Todo(title="FastAPI backend tekshiruvlarini yakunlash", completed=0),
            models.Todo(title="Uzbek tili mahalliylashtirishini tasdiqlash", completed=1),
            models.Todo(title="Boshqaruv paneli grafikalarini sozlash", completed=0),
            models.Todo(title="Foydalanuvchi ma'lumotlarini tahrirlash", completed=0),
            models.Todo(title="ECharts interfeysini sozlash", completed=0),
            models.Todo(title="Xodimlar ro'yxatini yuklash", completed=1),
            models.Todo(title="To'lov tizimini integratsiya qilish", completed=0),
            models.Todo(title="Tizim keshini tozalash", completed=1)
        ])

        db.commit()

        print("Seeding Classifier Excel items...")
        import_all_classifiers()

        print("Database seeding completed successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

