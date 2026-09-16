import { neon } from '@neondatabase/serverless';
import jwt from 'jsonwebtoken';
import fs from 'fs';
import pathModule from 'path';

let classifierSeedData = null;
function getClassifierSeedData() {
  if (!classifierSeedData) {
    try {
      const candidates = [
        pathModule.join(process.cwd(), 'api', 'classifier_seed.json'),
        pathModule.join(process.cwd(), 'classifier_seed.json')
      ];
      for (const p of candidates) {
        if (fs.existsSync(p)) {
          classifierSeedData = JSON.parse(fs.readFileSync(p, 'utf8'));
          break;
        }
      }
    } catch (e) {
      console.warn('Failed to load classifier_seed.json:', e);
    }
  }
  return classifierSeedData || [];
}

const DATABASE_URL = process.env.DATABASE_URL || 'postgresql://neondb_owner:npg_ArFp1ORwLbX6@ep-sparkling-fog-axd0fzvc-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require';
const SECRET_KEY = process.env.SECRET_KEY || 'super-secret-key-that-is-hard-to-guess';

let sqlClient;
function getSql() {
  if (!sqlClient) {
    let connStr = DATABASE_URL;
    if (connStr.startsWith('postgres://')) {
      connStr = connStr.replace('postgres://', 'postgresql://');
    }
    connStr = connStr.replace('&channel_binding=require', '').replace('?channel_binding=require', '');
    sqlClient = neon(connStr);
  }
  return sqlClient;
}

let schemaInitialized = false;
async function ensureSchema(sql) {
  if (schemaInitialized) return;
  try {
    await sql`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR UNIQUE NOT NULL,
        password VARCHAR NOT NULL,
        full_name VARCHAR,
        initials VARCHAR,
        avatar TEXT,
        role VARCHAR,
        "roleId" VARCHAR,
        email VARCHAR,
        department_id VARCHAR,
        permissions JSONB,
        created_at TIMESTAMP DEFAULT NOW()
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS roles (
        id VARCHAR PRIMARY KEY,
        "roleName" VARCHAR NOT NULL,
        status INTEGER DEFAULT 1,
        permissions JSONB,
        remark TEXT,
        "createTime" VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS departments (
        id VARCHAR PRIMARY KEY,
        name VARCHAR NOT NULL,
        status INTEGER DEFAULT 1,
        remark TEXT,
        "createTime" VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS branches (
        id VARCHAR PRIMARY KEY,
        name VARCHAR NOT NULL,
        status INTEGER DEFAULT 1,
        remark TEXT,
        "createTime" VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS workers (
        id VARCHAR PRIMARY KEY,
        worker_id VARCHAR,
        name VARCHAR NOT NULL,
        username VARCHAR,
        department_id VARCHAR,
        "departmentId" VARCHAR,
        role VARCHAR,
        email VARCHAR,
        phone VARCHAR,
        status INTEGER DEFAULT 1,
        "baseSalary" DOUBLE PRECISION DEFAULT 0,
        base_salary DOUBLE PRECISION DEFAULT 0,
        entry_date VARCHAR,
        notes TEXT,
        avatar TEXT,
        "createTime" VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS products (
        id VARCHAR PRIMARY KEY,
        "productName" VARCHAR NOT NULL,
        "SKU" VARCHAR,
        category VARCHAR,
        price DOUBLE PRECISION DEFAULT 0,
        cost DOUBLE PRECISION DEFAULT 0,
        "quantityInStock" INTEGER DEFAULT 0,
        status INTEGER DEFAULT 1,
        shtrix_code VARCHAR,
        mxik_code VARCHAR,
        brand_name VARCHAR,
        image_url TEXT,
        unit VARCHAR,
        remark TEXT,
        min_stock INTEGER DEFAULT 10,
        expiration_date VARCHAR,
        "createTime" VARCHAR
      );
    `;
    await sql`
      ALTER TABLE products ADD COLUMN IF NOT EXISTS min_stock INTEGER DEFAULT 10;
    `;
    await sql`
      ALTER TABLE products ADD COLUMN IF NOT EXISTS expiration_date VARCHAR;
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS product_packagings (
        id SERIAL PRIMARY KEY,
        product_id VARCHAR,
        name VARCHAR,
        coefficient DOUBLE PRECISION DEFAULT 1,
        barcode VARCHAR,
        is_base_unit BOOLEAN DEFAULT FALSE
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS classifier_items (
        id INTEGER PRIMARY KEY,
        group_name VARCHAR,
        class_name VARCHAR,
        position_name VARCHAR,
        subposition_name VARCHAR,
        brand_name VARCHAR,
        attribute_name VARCHAR,
        mxik_code VARCHAR,
        mxik_name TEXT,
        shtrix_code VARCHAR,
        unit VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS sales (
        id VARCHAR PRIMARY KEY,
        items JSONB,
        total DOUBLE PRECISION DEFAULT 0,
        total_amount DOUBLE PRECISION DEFAULT 0,
        payment_method VARCHAR,
        status VARCHAR,
        customer_name VARCHAR,
        customer_phone VARCHAR,
        debt_amount DOUBLE PRECISION DEFAULT 0,
        debt_due_date VARCHAR,
        user_id VARCHAR,
        "createTime" VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS sale_items (
        id SERIAL PRIMARY KEY,
        sale_id VARCHAR,
        product_id VARCHAR,
        product_name VARCHAR,
        quantity DOUBLE PRECISION,
        price DOUBLE PRECISION,
        total DOUBLE PRECISION
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS salaries (
        id VARCHAR PRIMARY KEY,
        "workerId" VARCHAR,
        "baseSalary" DOUBLE PRECISION DEFAULT 0,
        allowance DOUBLE PRECISION DEFAULT 0,
        deduction DOUBLE PRECISION DEFAULT 0,
        "netSalary" DOUBLE PRECISION DEFAULT 0,
        "payDate" VARCHAR,
        status VARCHAR,
        remark TEXT,
        "createTime" VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS positions (
        id VARCHAR PRIMARY KEY,
        name VARCHAR,
        department_id VARCHAR,
        base_salary DOUBLE PRECISION DEFAULT 0,
        status INTEGER DEFAULT 1,
        description TEXT,
        "createTime" VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS staff_timesheets (
        id VARCHAR PRIMARY KEY,
        date VARCHAR,
        status VARCHAR,
        records JSONB,
        "createTime" VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS staff_outputs (
        id VARCHAR PRIMARY KEY,
        "workerId" VARCHAR,
        "workerName" VARCHAR,
        name VARCHAR,
        amount DOUBLE PRECISION DEFAULT 0,
        period_month VARCHAR,
        comment TEXT,
        "createTime" VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS staff_adjustments (
        id VARCHAR PRIMARY KEY,
        "workerId" VARCHAR,
        document_type VARCHAR,
        amount DOUBLE PRECISION DEFAULT 0,
        period_month VARCHAR,
        description TEXT,
        "createTime" VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS monthly_financial_snapshots (
        id SERIAL PRIMARY KEY,
        period_month VARCHAR UNIQUE NOT NULL,
        revenue DOUBLE PRECISION DEFAULT 0,
        cogs DOUBLE PRECISION DEFAULT 0,
        staff_salaries DOUBLE PRECISION DEFAULT 0,
        short_term_outputs DOUBLE PRECISION DEFAULT 0,
        total_expenses DOUBLE PRECISION DEFAULT 0,
        net_profit DOUBLE PRECISION DEFAULT 0,
        profit_margin DOUBLE PRECISION DEFAULT 0,
        sales_count INTEGER DEFAULT 0,
        closed_by VARCHAR,
        closed_at VARCHAR,
        remark TEXT
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS device_tokens (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        device_name VARCHAR,
        token VARCHAR UNIQUE,
        pair_code VARCHAR,
        status VARCHAR DEFAULT 'active',
        expires_at VARCHAR,
        created_at VARCHAR,
        last_used_at VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS sales_pushes (
        id VARCHAR PRIMARY KEY,
        device_token VARCHAR,
        pc_user_id INTEGER,
        device_name VARCHAR,
        items_json JSONB,
        status VARCHAR DEFAULT 'pending',
        created_at VARCHAR,
        updated_at VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS qr_codes (
        id VARCHAR PRIMARY KEY,
        task_id VARCHAR,
        code VARCHAR,
        quantity INTEGER DEFAULT 1,
        status VARCHAR DEFAULT 'active',
        "createTime" VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS cutting_stages (
        id VARCHAR PRIMARY KEY,
        name VARCHAR NOT NULL,
        code VARCHAR,
        sequence INTEGER DEFAULT 1,
        description TEXT,
        status INTEGER DEFAULT 1,
        "createTime" VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS cutting_processes (
        id VARCHAR PRIMARY KEY,
        name VARCHAR NOT NULL,
        stage_id VARCHAR,
        description TEXT,
        status INTEGER DEFAULT 1,
        "createTime" VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS cutting_orders (
        id VARCHAR PRIMARY KEY,
        order_no VARCHAR,
        product_name VARCHAR,
        quantity INTEGER DEFAULT 1,
        status VARCHAR DEFAULT 'pending',
        remark TEXT,
        "createTime" VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS cutting_tasks (
        id VARCHAR PRIMARY KEY,
        order_id VARCHAR,
        task_name VARCHAR,
        status VARCHAR DEFAULT 'pending',
        assigned_to VARCHAR,
        "createTime" VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS cutting_task_executions (
        id VARCHAR PRIMARY KEY,
        task_id VARCHAR,
        worker_id VARCHAR,
        worker_name VARCHAR,
        quantity INTEGER DEFAULT 1,
        status VARCHAR DEFAULT 'completed',
        remark TEXT,
        "createTime" VARCHAR
      );
    `;
    await sql`
      CREATE TABLE IF NOT EXISTS debt_payments (
        id VARCHAR(64) PRIMARY KEY,
        receipt_number VARCHAR(64),
        customer_name VARCHAR(255),
        customer_phone VARCHAR(64),
        amount NUMERIC(15, 2) DEFAULT 0,
        payment_method VARCHAR(64) DEFAULT 'naqd',
        cashier_name VARCHAR(255),
        remark TEXT,
        created_at VARCHAR(64)
      );
    `;

    // Seed default roles if empty
    await sql`
      INSERT INTO roles (id, "roleName", status, permissions, remark, "createTime")
      VALUES 
        ('1', 'Super Administrator', 1, '["*.*.*"]'::jsonb, 'Tizimning barcha boshqaruv huquqlariga ega', to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS')),
        ('2', 'Administrator', 1, '["/dashboard", "/dashboard/analysis", "/dashboard/workplace", "/product", "/product/list", "/sales", "/sales/pos", "/sales/debtors", "/hr", "/hr/workers", "/hr/timesheets", "/hr/outputs", "/hr/adjustments", "/hr/salary"]'::jsonb, 'Oddiy administrator', to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS')),
        ('3', 'Oddiy xodim', 1, '["/dashboard", "/dashboard/workplace", "/product", "/product/list", "/sales", "/sales/pos"]'::jsonb, 'Faqat ish joyi, kassa (POS) va mahsulotlar bilan ishlash huquqiga ega', to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
      ON CONFLICT (id) DO NOTHING;
    `;

    // Seed default department if empty
    await sql`
      INSERT INTO departments (id, name, status, remark, "createTime")
      VALUES ('DEPT-HQ', 'Boshqaruv', 1, 'Bosh ofis va ma''muriyat', to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
      ON CONFLICT (id) DO NOTHING;
    `;

    // Seed default branch if empty
    await sql`
      INSERT INTO branches (id, name, status, remark, "createTime")
      VALUES ('BR-01', 'Asosiy filial', 1, 'Bosh savdo filiali', to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
      ON CONFLICT (id) DO NOTHING;
    `;

    // Seed default admin user if empty
    await sql`
      INSERT INTO users (id, username, password, full_name, role, "roleId", permissions, create_time)
      VALUES (1, 'admin', 'admin', 'Administrator', 'Super Administrator', '1', '["*.*.*"]'::jsonb, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
      ON CONFLICT (id) DO NOTHING;
    `;

    // Ensure companies table and multi-tenancy columns
    await sql`
      CREATE TABLE IF NOT EXISTS companies (
        id VARCHAR(50) PRIMARY KEY,
        name VARCHAR(150) NOT NULL,
        code VARCHAR(50) UNIQUE NOT NULL,
        plan VARCHAR(20) DEFAULT 'pro',
        billing_cycle VARCHAR(20) DEFAULT 'monthly',
        subscription_expires_at TIMESTAMP,
        status VARCHAR(20) DEFAULT 'active',
        max_users INTEGER DEFAULT 10,
        features JSONB DEFAULT '{"ai_assistant": true, "advanced_analytics": true, "multi_branch": true, "cutting_module": true, "upcoming_features": true}'::jsonb,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      );
    `;
    await sql`ALTER TABLE products ADD COLUMN IF NOT EXISTS company_id VARCHAR(50) DEFAULT 'comp-default';`;
    await sql`ALTER TABLE sales ADD COLUMN IF NOT EXISTS company_id VARCHAR(50) DEFAULT 'comp-default';`;
    await sql`ALTER TABLE users ADD COLUMN IF NOT EXISTS company_id VARCHAR(50) DEFAULT 'comp-default';`;
    await sql`ALTER TABLE workers ADD COLUMN IF NOT EXISTS company_id VARCHAR(50) DEFAULT 'comp-default';`;
    try {
      await sql`ALTER TABLE products ALTER COLUMN classifier_id TYPE VARCHAR USING classifier_id::varchar;`;
    } catch(e) {}
    await sql`
      INSERT INTO companies (id, name, code, plan, billing_cycle, status, max_users)
      VALUES ('comp-default', 'Bosh Korxona', 'DEFAULT', 'pro', 'yearly', 'active', 50)
      ON CONFLICT (id) DO NOTHING;
    `;

    schemaInitialized = true;
  } catch (err) {
    console.warn('ensureSchema warning:', err);
  }
}

const defaultAdminRoutes = [
  {
    path: '/dashboard',
    component: '#',
    redirect: '/dashboard/workplace',
    name: 'Dashboard',
    meta: {
      title: 'router.dashboard',
      icon: 'vi-ant-design:dashboard-filled',
      alwaysShow: true
    },
    children: [
      {
        path: 'analysis',
        component: 'views/Dashboard/Analysis',
        name: 'Analysis',
        meta: {
          title: 'router.analysis',
          noCache: true
        }
      },
      {
        path: 'workplace',
        component: 'views/Dashboard/Workplace',
        name: 'Workplace',
        meta: {
          title: 'router.workplace',
          noCache: true,
          affix: true
        }
      }
    ]
  },
  {
    path: '/company',
    component: '#',
    redirect: '/company/list',
    name: 'CompanyRoot',
    meta: {
      title: 'Korxonalar Boshqaruvi',
      icon: 'vi-ep:office-building',
      alwaysShow: true
    },
    children: [
      {
        path: 'list',
        component: 'views/Company/CompanyManagement',
        name: 'CompanyManagement',
        meta: {
          title: 'Kompaniyalar va Tariflar',
          noCache: true
        }
      }
    ]
  },
  {
    path: '/product',
    component: '#',
    redirect: '/product/list',
    name: 'ProductRoot',
    meta: {
      title: 'Omborxona',
      icon: 'vi-ep:goods',
      alwaysShow: true
    },
    children: [
      {
        path: 'list',
        component: 'views/Product/Product',
        name: 'ProductManagement',
        meta: {
          title: 'Ombor Mahsulotlari',
          noCache: true
        }
      }
    ]
  }
];

const defaultRoleKeys = [
  '/dashboard',
  '/dashboard/analysis',
  '/dashboard/workplace',
  '/company',
  '/company/list',
  '/product',
  '/product/list'
];

const defaultWorkerPermissions = [
  '/dashboard',
  '/dashboard/workplace',
  'dashboard:workplace',
  '/product',
  '/product/list',
  'product:view',
  '/sales',
  '/sales/pos',
  'sales:pos',
  'sales:view',
  'sales:create'
];

function filterRoutesByRole(permissions) {
  if (!Array.isArray(permissions) || permissions.includes('*.*.*') || permissions.includes('*') || permissions.includes('all')) {
    return defaultAdminRoutes;
  }

  const pSet = new Set(permissions.map((p) => String(p).toLowerCase().trim()));

  const filtered = [];
  for (const parent of defaultAdminRoutes) {
    const parentPath = parent.path.toLowerCase();
    const parentName = (parent.name || '').toLowerCase();

    // Check children
    const validChildren = [];
    if (parent.children && parent.children.length > 0) {
      for (const child of parent.children) {
        const childPath = child.path.toLowerCase();
        const fullPath = `${parentPath}/${childPath}`.replace(/\/+/g, '/').toLowerCase();
        const childName = (child.name || '').toLowerCase();

        const hasMatch =
          pSet.has(fullPath) ||
          pSet.has(childPath) ||
          pSet.has(childName) ||
          pSet.has(parentPath) ||
          Array.from(pSet).some(
            (p) => p.includes(childPath) || (childPath.length > 2 && p.endsWith(childPath))
          );

        if (hasMatch) {
          validChildren.push(child);
        }
      }
    }

    if (validChildren.length > 0) {
      filtered.push({
        ...parent,
        children: validChildren
      });
    } else if (pSet.has(parentPath) || pSet.has(parentName)) {
      filtered.push({
        ...parent,
        children: []
      });
    }
  }

  if (filtered.length > 0) return filtered;
  if (permissions.includes('*.*.*') || permissions.includes('*')) return defaultAdminRoutes;

  // Safe fallback for unprivileged/unassigned users:
  return [
    {
      path: '/dashboard',
      component: '#',
      redirect: '/dashboard/workplace',
      name: 'Dashboard',
      meta: {
        title: 'router.dashboard',
        icon: 'vi-ant-design:dashboard-filled',
        alwaysShow: true
      },
      children: [
        {
          path: 'workplace',
          component: 'views/Dashboard/Workplace',
          name: 'Workplace',
          meta: {
            title: 'router.workplace',
            noCache: true
          }
        }
      ]
    }
  ];
}

function filterRoleKeysByRole(permissions) {
  if (!Array.isArray(permissions) || permissions.includes('*.*.*') || permissions.includes('*') || permissions.includes('all')) {
    return defaultRoleKeys;
  }

  const pSet = new Set(permissions.map((p) => String(p).toLowerCase().trim()));
  const keys = defaultRoleKeys.filter((k) => {
    const lk = k.toLowerCase();
    const parts = lk.split('/').filter(Boolean);
    const lastPart = parts[parts.length - 1];
    return (
      pSet.has(lk) ||
      pSet.has(lastPart) ||
      Array.from(pSet).some((p) => p.includes(lastPart) || lk.includes(p))
    );
  });

  return keys.length > 0 ? keys : ['/dashboard', '/dashboard/workplace'];
}

function getReqCompanyId(req, payload = null) {
  let qCompany = null;
  try {
    const urlObj = new URL(req.url, 'http://localhost');
    qCompany = req?.query?.company_id || urlObj.searchParams.get('company_id');
  } catch (e) {
    qCompany = req?.query?.company_id;
  }
  if (qCompany) return qCompany;
  if (payload) {
    if (payload.is_super_admin && !qCompany) return null;
    if (payload.company_id) return payload.company_id;
  }
  return 'comp-default';
}

function authenticate(req, res) {
  const authHeader = req?.headers?.authorization || req?.headers?.Authorization;
  if (!authHeader) {
    res.status(401).json({
      code: 401,
      message: 'Avtorizatsiya talab qilinadi. Yaroqli JWT token taqdim eting.'
    });
    return null;
  }

  let token = String(authHeader).trim();
  if (token.startsWith('Bearer ') || token.startsWith('bearer ')) {
    token = token.slice(7).trim();
  }

  if (!token) {
    res.status(401).json({
      code: 401,
      message: 'Token topilmadi. Qaytadan tizimga kiring.'
    });
    return null;
  }

  try {
    const payload = jwt.verify(token, SECRET_KEY);
    if (!payload || (!payload.id && !payload.username)) {
      res.status(401).json({
        code: 401,
        message: 'Yaroqsiz token strukturasi.'
      });
      return null;
    }
    return payload;
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      res.status(401).json({
        code: 401,
        message: 'Sessiya muddati tugadi (Token Expired). Iltimos, qaytadan tizimga kiring.'
      });
    } else {
      res.status(401).json({
        code: 401,
        message: 'Yaroqsiz token: ' + err.message
      });
    }
    return null;
  }
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'SAMEORIGIN');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Parse path
  let rawUrl = req.url || '';
  const [pathname, search] = rawUrl.split('?');
  const path = pathname.replace(/^(\/?(api|mock)\/?)+/i, '').replace(/\/+$/g, '');
  const urlSearchParams = new URLSearchParams(search || '');
  const sql = getSql();
  await ensureSchema(sql);

  try {
    // 1. POST /api/user/login (Public)
    if (path === 'user/login' && req.method === 'POST') {
      const { username, password } = req.body || {};
      const userRows = await sql`SELECT * FROM users WHERE username = ${username}`;
      let user = userRows[0];

      if (!user) {
        try {
          const workerRows = await sql`
            SELECT * FROM workers WHERE username = ${username} OR worker_id = ${username} OR name = ${username} LIMIT 1
          `;
          const worker = workerRows[0];
          if (worker) {
            user = {
              id: worker.id,
              username: worker.username || worker.worker_id || `worker_${worker.id}`,
              full_name: worker.name,
              role: worker.role || 'Oddiy xodim',
              roleId: '3',
              avatar: worker.avatar || '',
              permissions: []
            };
          }
        } catch (wErr) {
          console.warn('Worker lookup error:', wErr.message);
        }
      }

      if (!user) {
        if (username === 'admin') {
          try {
            const ins = await sql`
              INSERT INTO users (id, username, full_name, role, "roleId", permissions) 
              VALUES (1, 'admin', 'Administrator', 'Super Administrator', '1', '["*.*.*"]'::jsonb) 
              ON CONFLICT (id) DO UPDATE SET role = 'Super Administrator'
              RETURNING *
            `;
            user = ins[0];
          } catch (insErr) {
            user = {
              id: 1,
              username: 'admin',
              full_name: 'Administrator',
              role: 'Super Administrator',
              roleId: '1',
              permissions: ['*.*.*']
            };
          }
        } else {
          return res.status(200).json({ code: 500, message: "Xodim topilmadi yoki parol noto'g'ri" });
        }
      }

      // Ensure user has a valid role and roleId:
      if (!user.role) {
        user.role = user.username === 'admin' ? 'Super Administrator' : 'Oddiy xodim';
        user.roleId = user.username === 'admin' ? '1' : '3';
      }

      const isSuper = (user.role || '').toLowerCase().includes('super') || user.username === 'admin';
      const companyId = user.company_id || 'comp-default';
      let company = null;
      try {
        const compRows = await sql`SELECT * FROM companies WHERE id = ${companyId} LIMIT 1`;
        company = compRows[0];
      } catch (e) {}

      const token = 'Bearer ' + jwt.sign({
        sub: user.username,
        id: user.id,
        company_id: companyId,
        is_super_admin: isSuper
      }, SECRET_KEY, { expiresIn: '8h' });
      let permissions = user.permissions;
      if (typeof permissions === 'string') {
        try { permissions = JSON.parse(permissions); } catch (e) { permissions = []; }
      }
      if (!Array.isArray(permissions) || permissions.length === 0) {
        if (user.role === 'Super Administrator' || user.username === 'admin') {
          permissions = ['*.*.*'];
        } else {
          const rRows = await sql`SELECT * FROM roles WHERE "roleName" = ${user.role} OR id = ${user.roleId || user.role} LIMIT 1`;
          if (rRows[0] && rRows[0].permissions) {
            permissions = typeof rRows[0].permissions === 'string' ? JSON.parse(rRows[0].permissions) : rRows[0].permissions;
          }
          if (!Array.isArray(permissions) || permissions.length === 0) {
            permissions = defaultWorkerPermissions;
          }
        }
      }

      return res.status(200).json({
        code: 0,
        data: {
          id: user.id || 1,
          username: user.username || username,
          full_name: user.full_name || user.username || 'admin',
          initials: (user.full_name || user.username || 'AD').substring(0, 2).toUpperCase(),
          avatar: user.avatar || '',
          role: user.role,
          roleId: user.roleId || (user.role === 'Super Administrator' ? '1' : '3'),
          email: user.email || '',
          department_id: user.department_id || 'DEPT-HQ',
          company_id: companyId,
          company_name: company ? company.name : 'Bosh Korxona',
          company_plan: company ? (company.plan || 'pro') : 'pro',
          company_features: company ? (company.features || {}) : {},
          is_super_admin: isSuper,
          permissions: permissions,
          token: token,
          password: password
        }
      });
    }

    // 2. GET /api/user/employees (Public - for login screen cashier chooser)
    if (path === 'user/employees') {
      const rows = await sql`SELECT * FROM workers WHERE status = 1`;
      return res.status(200).json({ code: 0, data: rows });
    }

    // Public & Device endpoints exempt from strict JWT auth
    const isPublicOrDeviceRoute = 
      path === 'user/login' ||
      path === 'user/employees' ||
      path.startsWith('classifier/') ||
      path === 'menu/list' ||
      path.startsWith('dict/') ||
      path.startsWith('device/') ||
      path.startsWith('sales/phone-checkout') ||
      path.startsWith('sales/push-pc-sale') ||
      path.startsWith('sales/pending-pushes') ||
      path.startsWith('sales/push-payload') ||
      path.startsWith('sales/respond-push') ||
      path.startsWith('analysis/');

    let authUser = null;
    if (!isPublicOrDeviceRoute) {
      authUser = authenticate(req, res);
      if (!authUser) return;
    }

    // User Profile Save & Update
    if (path === 'user/save' && req.method === 'POST') {
      const { id, username, password, full_name, phone, email, avatar, role, roleId } = req.body || {};
      if (password) {
        await sql`
          UPDATE users 
          SET hashed_password = ${password}, full_name = ${full_name || username}, phone = ${phone || null}, email = ${email || null}, avatar = ${avatar || ''}
          WHERE username = ${username} OR id = ${id}
        `;
      } else {
        await sql`
          UPDATE users 
          SET full_name = ${full_name || username}, phone = ${phone || null}, email = ${email || null}, avatar = ${avatar || ''}
          WHERE username = ${username} OR id = ${id}
        `;
      }
      const userRows = await sql`SELECT * FROM users WHERE username = ${username} OR id = ${id}`;
      return res.status(200).json({ code: 0, data: userRows[0] || req.body, message: 'Saqlandi' });
    }

    if ((path === 'user/avatar' || path === 'user/updateAvatar') && req.method === 'POST') {
      const { username, avatar, full_name } = req.body || {};
      const targetUser = username || authUser?.username || authUser?.sub || 'admin';
      if (full_name) {
        await sql`UPDATE users SET avatar = ${avatar || ''}, full_name = ${full_name} WHERE username = ${targetUser}`;
      } else {
        await sql`UPDATE users SET avatar = ${avatar || ''} WHERE username = ${targetUser}`;
      }
      const userRows = await sql`SELECT * FROM users WHERE username = ${targetUser}`;
      return res.status(200).json({ code: 0, data: userRows[0] || { username: targetUser, avatar }, message: 'Avatar saqlandi' });
    }

    if (path === 'user/list') {
      const pageIndex = parseInt(req.query?.pageIndex || urlSearchParams.get('pageIndex') || 1, 10);
      const pageSize = parseInt(req.query?.pageSize || urlSearchParams.get('pageSize') || 10, 10);
      const username = (req.query?.username || urlSearchParams.get('username') || '').trim().toLowerCase();
      const offset = (pageIndex - 1) * pageSize;

      let allUsers = await sql`SELECT id, username, full_name, role, "roleId", email, phone, avatar, created_at, create_time FROM users ORDER BY id ASC`;
      if (username) {
        allUsers = allUsers.filter(u => (u.username || '').toLowerCase().includes(username) || (u.full_name || '').toLowerCase().includes(username));
      }
      const total = allUsers.length;
      const list = allUsers.slice(offset, offset + pageSize);
      return res.status(200).json({ code: 0, data: { list, total } });
    }

    if (path === 'user/delete' && req.method === 'POST') {
      let ids = req.body?.ids;
      if (!ids && req.body?.id) ids = [req.body.id];
      if (Array.isArray(ids) && ids.length > 0) {
        await sql`DELETE FROM users WHERE id = ANY(${ids}) AND username != 'admin'`;
        return res.status(200).json({ code: 0, message: 'Foydalanuvchi o\'chirildi' });
      }
      return res.status(200).json({ code: 400, message: 'ID ko\'rsatilmadi' });
    }

    if (path === 'user/loginOut') {
      return res.status(200).json({ code: 0, data: null, message: 'Tizimdan chiqildi' });
    }

    // 3. GET /api/workplace/total
    if (path === 'workplace/total') {
      const [pCount, wCount, tCount] = await Promise.all([
        sql`SELECT count(*) FROM products`,
        sql`SELECT count(*) FROM workers`,
        sql`SELECT count(*) FROM todos WHERE completed = 0`
      ]);
      return res.status(200).json({
        code: 0,
        data: {
          project: parseInt(pCount[0].count, 10),
          access: 100 + parseInt(wCount[0].count, 10) * 10,
          todo: parseInt(tCount[0].count, 10)
        }
      });
    }

    // 4. GET /api/workplace/project
    if (path === 'workplace/project') {
      const rows = await sql`SELECT * FROM workplace_projects ORDER BY id ASC`;
      return res.status(200).json({ code: 0, data: rows });
    }

    // 5. GET /api/workplace/dynamic
    if (path === 'workplace/dynamic') {
      const rows = await sql`SELECT * FROM workplace_dynamics ORDER BY id DESC LIMIT 10`;
      const logs = rows.map(r => {
        let keys = r.keys;
        if (typeof keys === 'string') {
          try { keys = JSON.parse(keys); } catch(e) { keys = [keys]; }
        }
        return { keys, time: r.time };
      });
      return res.status(200).json({ code: 0, data: logs });
    }

    // 6. GET /api/workplace/team
    if (path === 'workplace/team') {
      const rows = await sql`SELECT * FROM workplace_teams ORDER BY id ASC`;
      return res.status(200).json({ code: 0, data: rows });
    }

    // 7. GET /api/workplace/radar
    if (path === 'workplace/radar') {
      const rows = await sql`SELECT * FROM workplace_radars ORDER BY id ASC`;
      return res.status(200).json({ code: 0, data: rows });
    }

    // 8. GET /api/product/list
    if (path === 'product/list') {
      const pageIndex = parseInt(req.query?.pageIndex || urlSearchParams.get('pageIndex') || 1, 10);
      const pageSize = parseInt(req.query?.pageSize || urlSearchParams.get('pageSize') || 20, 10);
      const productName = (req.query?.productName || urlSearchParams.get('productName') || '').trim().toLowerCase();
      const category = (req.query?.category || urlSearchParams.get('category') || '').trim();
      const offset = (pageIndex - 1) * pageSize;
      const targetCompany = req.query?.company_id || urlSearchParams.get('company_id') || getReqCompanyId(req, authUser);

      let allRows;
      if (targetCompany) {
        allRows = await sql`SELECT * FROM products WHERE company_id = ${targetCompany} ORDER BY id DESC`;
      } else {
        allRows = await sql`SELECT * FROM products ORDER BY id DESC`;
      }
      if (productName) {
        const normalizeTokens = (str) => {
          let s = (str || '').toLowerCase();
          s = s.replace(/([0-9]+),([0-9]+)/g, '$1.$2');
          s = s.replace(/([0-9]+(\.[0-9]+)?)\s*(l|litr|kg|g|gr|ml)\b/gi, '$1 ');
          s = s.replace(/(?<=\d)\.(?=\d)/g, '___DEC___');
          s = s.replace(/[^a-z0-9_]/gi, ' ');
          s = s.replace(/___DEC___/g, '.');
          return s.split(/\s+/).filter(Boolean).map(w => {
            if (/^[0-9]+(\.[0-9]+)?$/.test(w)) return String(parseFloat(w));
            return w;
          });
        };
        const queryTokens = normalizeTokens(productName);
        allRows = allRows.filter(p => {
          const targetStr = `${p.productName || ''} ${p.brand_name || ''} ${p.attribute_name || ''} ${p.shtrix_code || ''} ${p.SKU || ''} ${p.mxik_code || ''} ${p.remark || ''}`;
          if (targetStr.toLowerCase().includes(productName)) return true;
          const targetTokens = normalizeTokens(targetStr);
          return queryTokens.length > 0 && queryTokens.every(q => targetTokens.includes(q));
        });
      }
      if (category) {
        allRows = allRows.filter(p => p.category === category);
      }

      const total = allRows.length;
      const paginated = allRows.slice(offset, offset + pageSize);
      return res.status(200).json({
        code: 0,
        data: {
          total,
          list: paginated
        }
      });
    }

    // GET /api/product/check-existing
    if (path === 'product/check-existing') {
      try {
        const barcode = (req.query?.barcode || urlSearchParams.get('barcode') || req.body?.barcode || '').trim();
        const sku = (req.query?.sku || urlSearchParams.get('sku') || req.body?.sku || '').trim();
        const name = (req.query?.name || urlSearchParams.get('name') || req.body?.name || '').trim();
        const rawClsId = req.query?.classifier_id || urlSearchParams.get('classifier_id') || req.body?.classifier_id;
        const classifierIdStr = rawClsId !== undefined && rawClsId !== null ? String(rawClsId).trim() : '';

        let rows = [];
        if (barcode) {
          rows = await sql`SELECT * FROM products WHERE shtrix_code = ${barcode} LIMIT 1`;
        }
        if (rows.length === 0 && sku) {
          rows = await sql`SELECT * FROM products WHERE LOWER("SKU") = LOWER(${sku}) LIMIT 1`;
        }
        if (rows.length === 0 && classifierIdStr) {
          rows = await sql`SELECT * FROM products WHERE classifier_id::text = ${classifierIdStr} OR mxik_code = ${classifierIdStr} LIMIT 1`;
        }
        if (rows.length === 0 && name) {
          rows = await sql`SELECT * FROM products WHERE LOWER("productName") = LOWER(${name}) LIMIT 1`;
        }
        if (rows.length === 0 && name && name.length >= 2) {
          const normalizeTokens = (str) => {
            let s = (str || '').toLowerCase();
            s = s.replace(/([0-9]+),([0-9]+)/g, '$1.$2');
            s = s.replace(/([0-9]+(\.[0-9]+)?)\s*(l|litr|kg|g|gr|ml)\b/gi, '$1 ');
            s = s.replace(/(?<=\d)\.(?=\d)/g, '___DEC___');
            s = s.replace(/[^a-z0-9_]/gi, ' ');
            s = s.replace(/___DEC___/g, '.');
            return s.split(/\s+/).filter(Boolean).map(w => {
              if (/^[0-9]+(\.[0-9]+)?$/.test(w)) return String(parseFloat(w));
              return w;
            });
          };
          const queryTokens = normalizeTokens(name);
          const allProducts = await sql`SELECT * FROM products LIMIT 500`;
          const matched = allProducts.find(p => {
            const targetStr = `${p.productName || ''} ${p.brand_name || ''} ${p.attribute_name || ''} ${p.shtrix_code || ''} ${p.SKU || ''} ${p.mxik_code || ''} ${p.remark || ''}`;
            if (targetStr.toLowerCase().includes(name.toLowerCase())) return true;
            const targetTokens = normalizeTokens(targetStr);
            return queryTokens.length > 0 && queryTokens.every(q => targetTokens.includes(q));
          });
          if (matched) {
            rows = [matched];
          }
        }

        if (rows.length > 0) {
          return res.status(200).json({ code: 0, exists: true, data: rows[0] });
        }
        return res.status(200).json({ code: 0, exists: false, data: null });
      } catch (err) {
        console.error('check-existing error:', err);
        return res.status(200).json({ code: 0, exists: false, data: null });
      }
    }

    // GET /api/product/by-barcode/:barcode
    if (path.startsWith('product/by-barcode/')) {
      const barcode = decodeURIComponent(path.replace('product/by-barcode/', '')).trim();
      const rows = await sql`SELECT * FROM products WHERE shtrix_code = ${barcode} LIMIT 1`;
      if (rows[0]) {
        return res.status(200).json({ code: 0, data: rows[0] });
      }
      return res.status(200).json({ code: 404, message: 'Mahsulot topilmadi' });
    }

    // POST /api/product/save (Add, update, or replenish existing stock)
    if (path === 'product/save' && req.method === 'POST') {
      try {
        const {
          id,
          productName,
          SKU,
          category,
          price,
          cost,
          quantityInStock,
          status,
          shtrix_code,
          mxik_code,
          brand_name,
          attribute_name,
          image_url,
          unit,
          remark,
          expiration_date,
          min_stock,
          classifier_id,
          additional_qty,
          is_replenish,
          packagings
        } = req.body || {};

        const targetCompany = req.body?.company_id || getReqCompanyId(req, authUser);

        let existing = null;
        if (id) {
          const rows = targetCompany
            ? await sql`SELECT * FROM products WHERE id = ${id} AND company_id = ${targetCompany} LIMIT 1`
            : await sql`SELECT * FROM products WHERE id = ${id} LIMIT 1`;
          if (rows[0]) existing = rows[0];
        }
        if (!existing && shtrix_code) {
          const rows = targetCompany
            ? await sql`SELECT * FROM products WHERE shtrix_code = ${shtrix_code.trim()} AND company_id = ${targetCompany} LIMIT 1`
            : await sql`SELECT * FROM products WHERE shtrix_code = ${shtrix_code.trim()} LIMIT 1`;
          if (rows[0]) existing = rows[0];
        }
        if (!existing && SKU) {
          const rows = targetCompany
            ? await sql`SELECT * FROM products WHERE LOWER("SKU") = LOWER(${SKU.trim()}) AND company_id = ${targetCompany} LIMIT 1`
            : await sql`SELECT * FROM products WHERE LOWER("SKU") = LOWER(${SKU.trim()}) LIMIT 1`;
          if (rows[0]) existing = rows[0];
        }

        const clsId = classifier_id !== undefined && classifier_id !== null && String(classifier_id).trim() !== '' ? String(classifier_id).trim() : (existing ? existing.classifier_id : null);
        const minStk = min_stock !== undefined && min_stock !== null && min_stock !== '' ? parseInt(min_stock, 10) : (existing && existing.min_stock !== undefined ? existing.min_stock : 10);

        if (existing) {
          // Product exists in warehouse: add stock
          const oldStock = existing.quantityInStock || 0;
          let added = 0;
          let newStock = oldStock;

          if (additional_qty !== undefined && additional_qty !== null) {
            added = parseInt(additional_qty, 10) || 0;
            newStock = oldStock + added;
          } else if (is_replenish) {
            added = parseInt(quantityInStock, 10) || 0;
            newStock = oldStock + added;
          } else {
            newStock = parseInt(quantityInStock, 10) || 0;
            added = newStock - oldStock;
          }

          const pr = price !== undefined && price !== null ? parseFloat(price) : existing.price;
          const cst = cost !== undefined && cost !== null ? parseFloat(cost) : existing.cost;
          const stat = status !== undefined ? parseInt(status, 10) : existing.status;

          const updated = await sql`
            UPDATE products
            SET "productName" = ${productName || existing.productName},
                "SKU" = ${SKU || existing.SKU},
                category = ${category || existing.category},
                price = ${pr},
                cost = ${cst},
                "quantityInStock" = ${newStock},
                status = ${stat},
                shtrix_code = ${shtrix_code || existing.shtrix_code},
                mxik_code = ${mxik_code || existing.mxik_code},
                brand_name = ${brand_name || existing.brand_name},
                attribute_name = ${attribute_name || existing.attribute_name},
                image_url = ${image_url !== undefined ? image_url : existing.image_url},
                unit = ${unit || existing.unit},
                remark = ${remark !== undefined ? remark : existing.remark},
                expiration_date = ${expiration_date !== undefined ? expiration_date : existing.expiration_date},
                classifier_id = ${clsId},
                min_stock = ${minStk}
            WHERE id = ${existing.id}
            RETURNING *
          `;

          if (Array.isArray(packagings)) {
            await sql`DELETE FROM product_packagings WHERE product_id = ${existing.id}`;
            for (const pkg of packagings) {
              await sql`
                INSERT INTO product_packagings (product_id, name, coefficient, barcode, is_base_unit)
                VALUES (${existing.id}, ${pkg.unit_name || pkg.name}, ${pkg.conversion_factor || pkg.coefficient || 1}, ${pkg.shtrix_code || pkg.barcode || null}, ${!!pkg.is_base_unit})
              `;
            }
          }

          try {
            await sql`
              INSERT INTO activity_logs (user_id, username, action, details, "createTime")
              VALUES (${authUser?.id || 1}, ${authUser?.sub || 'admin'}, 'STOCK_REPLENISH', ${`"${productName || existing.productName}" qoldig'iga +${added} qo'shildi. Yangi qoldiq: ${newStock}`}, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
            `;
          } catch (actErr) {}

          return res.status(200).json({
            code: 0,
            is_existing: true,
            old_stock: oldStock,
            added_qty: added,
            total_stock: newStock,
            product_name: productName || existing.productName,
            data: updated[0],
            message: `"${productName || existing.productName}" omborda mavjud bo'lgani sababli qoldig'i +${added} ga oshirildi. Yangi umumiy qoldiq: ${newStock}!`
          });
        } else {
          // Insert brand new product
          const newId = id || ('PROD-' + Date.now().toString().slice(-6) + '-' + Math.floor(Math.random() * 900 + 100));
          const newSKU = SKU || `SKU-${Date.now().toString().slice(-6)}`;
          const stock = parseInt(quantityInStock, 10) || 0;
          const pr = parseFloat(price) || 0;
          const cst = parseFloat(cost) || 0;
          const stat = status !== undefined ? parseInt(status, 10) : 1;

          // Cluster Database Sync: If not in classifier_items, add it to shared cluster database
          try {
            let inCluster = false;
            if (shtrix_code) {
              const cCheck = await sql`SELECT id FROM classifier_items WHERE shtrix_code = ${shtrix_code.trim()} LIMIT 1`;
              if (cCheck.length > 0) inCluster = true;
            }
            if (!inCluster && mxik_code) {
              const mCheck = await sql`SELECT id FROM classifier_items WHERE mxik_code = ${mxik_code.trim()} LIMIT 1`;
              if (mCheck.length > 0) inCluster = true;
            }
            if (!inCluster) {
              const maxIdRes = await sql`SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM classifier_items`;
              const nextId = parseInt(maxIdRes[0].next_id, 10) || Math.floor(Date.now() / 1000);
              await sql`
                INSERT INTO classifier_items (
                  id, group_name, class_name, position_name, brand_name,
                  attribute_name, mxik_code, mxik_name, shtrix_code, unit
                )
                VALUES (
                  ${nextId},
                  ${category || 'Boshqa tovarlar'},
                  ${category || 'Boshqa tovarlar'},
                  ${productName || 'Yangi mahsulot'},
                  ${brand_name || null},
                  ${attribute_name || null},
                  ${mxik_code || null},
                  ${productName || 'Yangi tovar'},
                  ${shtrix_code || null},
                  ${unit || 'dona'}
                )
                ON CONFLICT (id) DO NOTHING
              `;
            }
          } catch (clsErr) {
            console.warn('Cluster database sync warning:', clsErr.message);
          }

          const inserted = await sql`
            INSERT INTO products (
              id, company_id, "productName", "SKU", category, price, cost, "quantityInStock", status,
              shtrix_code, mxik_code, brand_name, attribute_name, image_url, unit, remark,
              expiration_date, classifier_id, min_stock, "createTime"
            )
            VALUES (
              ${newId}, ${targetCompany}, ${productName || 'Yangi Mahsulot'}, ${newSKU}, ${category || 'Ichimliklar va suvlar'},
              ${pr}, ${cst}, ${stock}, ${stat}, ${shtrix_code || null}, ${mxik_code || null},
              ${brand_name || null}, ${attribute_name || null}, ${image_url || null}, ${unit || 'dona'},
              ${remark || null}, ${expiration_date || null}, ${clsId}, ${minStk}, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS')
            )
            RETURNING *
          `;

          if (Array.isArray(packagings)) {
            for (const pkg of packagings) {
              await sql`
                INSERT INTO product_packagings (product_id, name, coefficient, barcode, is_base_unit)
                VALUES (${newId}, ${pkg.unit_name || pkg.name}, ${pkg.conversion_factor || pkg.coefficient || 1}, ${pkg.shtrix_code || pkg.barcode || null}, ${!!pkg.is_base_unit})
              `;
            }
          }

          try {
            await sql`
              INSERT INTO activity_logs (user_id, username, action, details, "createTime")
              VALUES (${authUser?.id || 1}, ${authUser?.sub || 'admin'}, 'PRODUCT_CREATE', ${`Yangi mahsulot yaratildi: "${productName}" (${stock} dona)`}, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
            `;
          } catch (actErr) {}

          return res.status(200).json({
            code: 0,
            is_existing: false,
            data: inserted[0],
            message: 'Yangi mahsulot omborga muvaffaqiyatli qo\'shildi'
          });
        }
      } catch (err) {
        console.error('product/save error:', err);
        return res.status(500).json({ code: 500, message: 'Mahsulotni saqlashda xatolik: ' + err.message });
      }
    }

    // POST /api/product/delete
    if (path === 'product/delete' && req.method === 'POST') {
      let ids = req.body?.ids;
      if (!ids && req.body?.id) ids = [req.body.id];
      const targetCompany = req.body?.company_id || getReqCompanyId(req, authUser);
      if (Array.isArray(ids) && ids.length > 0) {
        await sql`DELETE FROM product_packagings WHERE product_id = ANY(${ids})`;
        if (targetCompany) {
          await sql`DELETE FROM products WHERE id = ANY(${ids}) AND company_id = ${targetCompany}`;
        } else {
          await sql`DELETE FROM products WHERE id = ANY(${ids})`;
        }
        try {
          await sql`
            INSERT INTO activity_logs (user_id, username, action, details, "createTime")
            VALUES (${authUser?.id || 1}, ${authUser?.sub || 'admin'}, 'PRODUCT_DELETE', ${`${ids.length} ta mahsulot o'chirildi: ${ids.join(', ')}`}, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
          `;
        } catch (actErr) {}
        return res.status(200).json({ code: 0, message: 'Mahsulotlar muvaffaqiyatli o\'chirildi', data: { deleted: ids.length } });
      }
      return res.status(200).json({ code: 400, message: 'O\'chirish uchun ID ko\'rsatilmadi' });
    }

    // POST /api/product/upload-image
    if (path === 'product/upload-image' && req.method === 'POST') {
      const imgUrl = req.body?.url || req.body?.image || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400';
      return res.status(200).json({ code: 0, data: { url: imgUrl } });
    }

    // ══════════════════════════════════════════════════════════════
    // COMPANY MANAGEMENT ENDPOINTS (Multi-Tenancy & Subscriptions)
    // ══════════════════════════════════════════════════════════════
    if (path === 'company/list') {
      const pageIndex = parseInt(req.query?.pageIndex || urlSearchParams.get('pageIndex') || 1, 10);
      const pageSize = parseInt(req.query?.pageSize || urlSearchParams.get('pageSize') || 20, 10);
      const name = (req.query?.name || urlSearchParams.get('name') || '').trim().toLowerCase();
      const plan = (req.query?.plan || urlSearchParams.get('plan') || '').trim().toLowerCase();
      const offset = (pageIndex - 1) * pageSize;

      let allCompanies = await sql`SELECT * FROM companies ORDER BY created_at DESC`;
      if (name) {
        allCompanies = allCompanies.filter(c => (c.name || '').toLowerCase().includes(name) || (c.code || '').toLowerCase().includes(name));
      }
      if (plan) {
        allCompanies = allCompanies.filter(c => (c.plan || '').toLowerCase() === plan);
      }

      const total = allCompanies.length;
      const paginated = allCompanies.slice(offset, offset + pageSize);

      return res.status(200).json({
        code: 0,
        data: {
          total,
          list: paginated
        }
      });
    }

    if (path === 'company/current') {
      const compId = getReqCompanyId(req, authUser) || 'comp-default';
      const rows = await sql`SELECT * FROM companies WHERE id = ${compId} LIMIT 1`;
      return res.status(200).json({
        code: 0,
        data: rows[0] || {
          id: 'comp-default',
          name: 'Bosh Korxona',
          code: 'DEFAULT',
          plan: 'pro',
          billing_cycle: 'yearly',
          status: 'active'
        }
      });
    }

    if (path === 'company/save' && req.method === 'POST') {
      const { id, name, code, plan, billing_cycle, status, max_users, features } = req.body || {};
      if (!name || !code) {
        return res.status(200).json({ code: 400, message: "Kompaniya nomi va kodi kiritilishi shart" });
      }
      const p = (plan || 'basic').toLowerCase();
      const defaultFeatures = p === 'pro'
        ? { ai_assistant: true, advanced_analytics: true, multi_branch: true, cutting_module: true, upcoming_features: true }
        : { ai_assistant: false, advanced_analytics: false, multi_branch: false, cutting_module: false, upcoming_features: false };
      const feats = features ? JSON.stringify(features) : JSON.stringify(defaultFeatures);

      let saved;
      if (id) {
        const rows = await sql`
          UPDATE companies
          SET name = ${name},
              code = ${code},
              plan = ${p},
              billing_cycle = ${billing_cycle || 'monthly'},
              status = ${status || 'active'},
              max_users = ${parseInt(max_users, 10) || 10},
              features = ${feats}::jsonb,
              updated_at = NOW()
          WHERE id = ${id}
          RETURNING *
        `;
        saved = rows[0];
      } else {
        const newId = 'comp-' + Date.now().toString(36) + '-' + Math.floor(100 + Math.random() * 900);
        const rows = await sql`
          INSERT INTO companies (id, name, code, plan, billing_cycle, status, max_users, features, created_at, updated_at)
          VALUES (${newId}, ${name}, ${code}, ${p}, ${billing_cycle || 'monthly'}, ${status || 'active'}, ${parseInt(max_users, 10) || 10}, ${feats}::jsonb, NOW(), NOW())
          RETURNING *
        `;
        saved = rows[0];
      }

      return res.status(200).json({
        code: 0,
        message: id ? "Kompaniya ma'lumotlari muvaffaqiyatli yangilandi" : "Yangi korxona muvaffaqiyatli ro'yxatga olindi",
        data: saved
      });
    }

    if (path === 'company/tier' && req.method === 'POST') {
      const { company_id, plan, billing_cycle, features } = req.body || {};
      if (!company_id || !plan) {
        return res.status(200).json({ code: 400, message: "company_id va plan kiritilishi shart" });
      }
      const p = plan.toLowerCase();
      const pFeatures = features
        ? JSON.stringify(features)
        : (p === 'pro'
          ? JSON.stringify({ ai_assistant: true, advanced_analytics: true, multi_branch: true, cutting_module: true, upcoming_features: true })
          : JSON.stringify({ ai_assistant: false, advanced_analytics: false, multi_branch: false, cutting_module: false, upcoming_features: false })
        );

      const rows = await sql`
        UPDATE companies
        SET plan = ${p},
            billing_cycle = ${billing_cycle || 'monthly'},
            features = ${pFeatures}::jsonb,
            updated_at = NOW()
        WHERE id = ${company_id}
        RETURNING *
      `;
      if (!rows[0]) {
        return res.status(200).json({ code: 404, message: "Kompaniya topilmadi" });
      }
      return res.status(200).json({
        code: 0,
        message: `Tarif muvaffaqiyatli ${p.toUpperCase()} ga o'zgartirildi`,
        data: rows[0]
      });
    }

    if (path === 'company/delete' && req.method === 'POST') {
      const { id } = req.body || {};
      if (!id) {
        return res.status(200).json({ code: 400, message: "O'chirish uchun id ko'rsatilmadi" });
      }
      if (id === 'comp-default') {
        return res.status(200).json({ code: 400, message: "Asosiy bosh korxonani o'chirish taqiqlangan" });
      }
      await sql`DELETE FROM companies WHERE id = ${id}`;
      return res.status(200).json({
        code: 0,
        message: "Kompaniya muvaffaqiyatli o'chirildi"
      });
    }

    // 9. Worker Endpoints
    if (path === 'worker/list') {
      const pageIndex = parseInt(req.query?.pageIndex || urlSearchParams.get('pageIndex') || 1, 10);
      const pageSize = parseInt(req.query?.pageSize || urlSearchParams.get('pageSize') || 20, 10);
      const name = (req.query?.name || urlSearchParams.get('name') || '').trim();
      const departmentId = (req.query?.departmentId || urlSearchParams.get('departmentId') || '').trim();
      const role = (req.query?.role || urlSearchParams.get('role') || '').trim();
      const offset = (pageIndex - 1) * pageSize;

      let allRows = await sql`SELECT * FROM workers ORDER BY id DESC`;
      if (name) {
        const ln = name.toLowerCase();
        allRows = allRows.filter(w => (w.name || '').toLowerCase().includes(ln) || (w.account || '').toLowerCase().includes(ln) || (w.id || '').toLowerCase().includes(ln));
      }
      if (departmentId) {
        allRows = allRows.filter(w => w.departmentId === departmentId || w.department_id === departmentId);
      }
      if (role) {
        allRows = allRows.filter(w => (w.role || 'Oddiy xodim') === role);
      }

      const total = allRows.length;
      const paginated = allRows.slice(offset, offset + pageSize).map(w => ({
        ...w,
        role: w.role || 'Oddiy xodim'
      }));

      return res.status(200).json({
        code: 0,
        data: {
          total,
          list: paginated
        }
      });
    }

    if (path === 'worker/save' && req.method === 'POST') {
      const { id, name, account, email, phone, role, departmentId, hireDate, status, baseSalary, remark } = req.body || {};
      const effectiveRole = role || 'Oddiy xodim';
      const effectiveStatus = status !== undefined ? parseInt(status, 10) : 1;
      const effectiveSalary = baseSalary !== undefined ? parseFloat(baseSalary) : 0;

      if (id) {
        await sql`
          UPDATE workers 
          SET name = ${name}, 
              account = ${account || null}, 
              email = ${email || null}, 
              phone = ${phone || null}, 
              role = ${effectiveRole}, 
              "departmentId" = ${departmentId || null}, 
              "hireDate" = ${hireDate || null}, 
              status = ${effectiveStatus}, 
              "baseSalary" = ${effectiveSalary}, 
              remark = ${remark || null}
          WHERE id = ${id}
        `;
      } else {
        const newId = 'WORK-' + Math.floor(100 + Math.random() * 900);
        await sql`
          INSERT INTO workers (id, name, account, email, phone, role, "departmentId", "hireDate", status, "baseSalary", remark)
          VALUES (${newId}, ${name}, ${account || null}, ${email || null}, ${phone || null}, ${effectiveRole}, ${departmentId || null}, ${hireDate || null}, ${effectiveStatus}, ${effectiveSalary}, ${remark || null})
        `;
      }
      return res.status(200).json({ code: 0, data: 'success', message: 'Xodim ma\'lumotlari muvaffaqiyatli saqlandi' });
    }

    if (path === 'worker/delete' && req.method === 'POST') {
      const { ids } = req.body || {};
      if (Array.isArray(ids) && ids.length > 0) {
        await sql`DELETE FROM workers WHERE id = ANY(${ids})`;
      }
      return res.status(200).json({ code: 0, data: 'success', message: "Xodimlar muvaffaqiyatli bo'shatildi" });
    }

    if (path === 'worker/avatar' && req.method === 'POST') {
      const { id, avatar } = req.body || {};
      if (id && avatar) {
        await sql`UPDATE workers SET avatar = ${avatar} WHERE id = ${id}`;
      }
      return res.status(200).json({ code: 0, data: { id, avatar } });
    }

    // 10. Roles Endpoints
    if (path === 'role/list') {
      if (!authUser) {
        return res.status(401).json({ code: 401, message: 'Tizimga kirilmagan yoki sessiya yaroqsiz' });
      }
      const isSuper = authUser.sub === 'admin' || authUser.role === 'Super Administrator' || authUser.is_super_admin === true;
      if (isSuper) {
        return res.status(200).json({ code: 0, data: filterRoutesByRole(['*.*.*']) });
      }
      return res.status(200).json({ code: 0, data: filterRoutesByRole(['dashboard:*', 'product:*', 'sales:*', 'hr:*']) });
    }

    if (path === 'role/list2') {
      const roleName = req.query?.roleName || urlSearchParams.get('roleName') || authUser?.role || authUser?.sub;
      let permissions = ['*.*.*'];
      if (roleName && roleName !== 'Super Administrator' && roleName !== 'admin') {
        const rRows = await sql`SELECT * FROM roles WHERE "roleName" = ${roleName} OR id = ${roleName} LIMIT 1`;
        if (rRows[0] && rRows[0].permissions) {
          permissions = typeof rRows[0].permissions === 'string' ? JSON.parse(rRows[0].permissions) : rRows[0].permissions;
        } else {
          const uRows = await sql`SELECT u.*, r.permissions as role_perms FROM users u LEFT JOIN roles r ON u."roleId" = r.id WHERE u.username = ${roleName} LIMIT 1`;
          if (uRows[0]) {
            permissions = uRows[0].role_perms || uRows[0].permissions || [];
            if (typeof permissions === 'string') {
              try { permissions = JSON.parse(permissions); } catch (e) {}
            }
          } else {
            const wRows = await sql`SELECT w.*, r.permissions as role_perms FROM workers w LEFT JOIN roles r ON w.role = r."roleName" WHERE w.account = ${roleName} LIMIT 1`;
            if (wRows[0]) {
              permissions = wRows[0].role_perms || [];
              if (typeof permissions === 'string') {
                try { permissions = JSON.parse(permissions); } catch (e) {}
              }
            }
          }
        }
      }
      if (!Array.isArray(permissions) || permissions.length === 0) {
        permissions = defaultWorkerPermissions;
      }
      return res.status(200).json({ code: 0, data: filterRoleKeysByRole(permissions) });
    }

    if (path === 'role/table') {
      const rows = await sql`SELECT * FROM roles ORDER BY id ASC`;
      return res.status(200).json({ code: 0, data: { total: rows.length, list: rows } });
    }

    if (path === 'role/save' && req.method === 'POST') {
      const isSuper = authUser?.role === 'Super Administrator' || authUser?.sub === 'admin';
      if (!isSuper) {
        return res.status(403).json({ code: 403, message: 'Kechirasiz, rollarni tahrirlash uchun Administrator huquqi talab qilinadi.' });
      }
      const { id, roleName, status, remark, permissions } = req.body || {};
      if (id) {
        await sql`
          UPDATE roles 
          SET "roleName" = ${roleName}, status = ${status !== undefined ? status : 1}, remark = ${remark || null}, permissions = ${JSON.stringify(permissions || [])}
          WHERE id = ${id}
        `;
      } else {
        const newId = 'role_' + Date.now().toString(36);
        await sql`
          INSERT INTO roles (id, "roleName", status, remark, permissions, "createTime")
          VALUES (${newId}, ${roleName}, ${status !== undefined ? status : 1}, ${remark || null}, ${JSON.stringify(permissions || [])}, NOW())
        `;
      }
      return res.status(200).json({ code: 0, message: 'Saqlandi' });
    }

    if (path === 'role/delete' && req.method === 'POST') {
      const isSuper = authUser?.role === 'Super Administrator' || authUser?.sub === 'admin';
      if (!isSuper) {
        return res.status(403).json({ code: 403, message: "Kechirasiz, rollarni o'chirish uchun Administrator huquqi talab qilinadi." });
      }
      const { id } = req.body || {};
      if (id === '1') {
        return res.status(400).json({ code: 400, message: "Super Administrator rolini o'chirib bo'lmaydi!" });
      }
      if (id) {
        await sql`DELETE FROM roles WHERE id = ${id}`;
      }
      return res.status(200).json({ code: 0, message: "O'chirildi" });
    }

    // 11. Departments Endpoints
    if (path === 'department/table/list' || path === 'department/list') {
      const rows = await sql`SELECT * FROM departments ORDER BY id ASC`;
      return res.status(200).json({
        code: 0,
        data: {
          total: rows.length,
          list: rows
        }
      });
    }

    if (path === 'department/save' && req.method === 'POST') {
      const isSuper = authUser?.role === 'Super Administrator' || authUser?.sub === 'admin';
      if (!isSuper) {
        return res.status(403).json({ code: 403, message: "Kechirasiz, bo'limlarni boshqarish uchun Administrator huquqi talab qilinadi." });
      }
      const { id, departmentName, name, parentId, status, remark } = req.body || {};
      const deptTitle = departmentName || name || 'Bo\'lim';
      if (id) {
        await sql`
          UPDATE departments 
          SET name = ${deptTitle}, status = ${status !== undefined ? status : 1}, remark = ${remark || null}
          WHERE id = ${id}
        `;
      } else {
        const newId = 'dept_' + Date.now().toString(36);
        await sql`
          INSERT INTO departments (id, name, status, remark, "createTime")
          VALUES (${newId}, ${deptTitle}, ${status !== undefined ? status : 1}, ${remark || null}, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
        `;
      }
      return res.status(200).json({ code: 0, message: 'Saqlandi' });
    }

    if (path === 'department/delete' && req.method === 'POST') {
      const { ids } = req.body || {};
      if (Array.isArray(ids) && ids.length > 0) {
        await sql`DELETE FROM departments WHERE id = ANY(${ids})`;
      }
      return res.status(200).json({ code: 0, message: "O'chirildi" });
    }

    if (path === 'department/users') {
      const deptId = req.query?.id || urlSearchParams.get('id');
      const rows = await sql`SELECT * FROM workers WHERE department_id = ${deptId} OR "departmentId" = ${deptId}`;
      const userList = rows.map(w => ({
        id: w.id,
        username: w.name,
        account: w.account || w.employee_code,
        email: w.email || '',
        createTime: w.createTime || '',
        role: w.role || 'Staff',
        department: { id: deptId, departmentName: '' }
      }));
      return res.status(200).json({ code: 0, data: { list: userList, total: userList.length } });
    }

    if (path === 'department/user/save' && req.method === 'POST') {
      const { id, departmentId, department_id, name, account, email, phone, role } = req.body || {};
      const deptId = departmentId || department_id || 'DEPT-HQ';
      if (id) {
        await sql`UPDATE workers SET "departmentId" = ${deptId}, department_id = ${deptId} WHERE id = ${id}`;
      } else {
        const newId = 'WORK-' + Math.floor(100 + Math.random() * 900);
        await sql`
          INSERT INTO workers (id, name, account, email, phone, role, "departmentId", department_id, status, "createTime")
          VALUES (${newId}, ${name || 'Yangi xodim'}, ${account || null}, ${email || null}, ${phone || null}, ${role || 'Oddiy xodim'}, ${deptId}, ${deptId}, 1, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
        `;
      }
      return res.status(200).json({ code: 0, data: 'success', message: "Xodim bo'limga biriktirildi" });
    }

    // ==========================================
    // 12. SaaS Company Management Endpoints
    // ==========================================
    if (path === 'company/list') {
      const companies = await sql`SELECT * FROM companies ORDER BY created_at DESC`;
      const enriched = [];
      const now = new Date();

      for (const c of companies) {
        const [wRes] = await sql`SELECT COUNT(*)::int as count FROM workers WHERE company_id = ${c.id}`;
        const [uRes] = await sql`SELECT COUNT(*)::int as count FROM users WHERE company_id = ${c.id}`;
        const [pRes] = await sql`SELECT COUNT(*)::int as count FROM products WHERE company_id = ${c.id}`;
        const [sRes] = await sql`SELECT COUNT(*)::int as count, COALESCE(SUM(paid_amount), 0)::float as revenue FROM sales WHERE company_id = ${c.id}`;

        const wCount = wRes?.count || 0;
        const uCount = uRes?.count || 0;
        const pCount = pRes?.count || 0;
        const sCount = sRes?.count || 0;
        const rev = sRes?.revenue || 0.0;

        let isExpired = false;
        if (c.subscription_expires_at) {
          isExpired = new Date(c.subscription_expires_at) < now;
        }

        const baseFeatures = c.plan === 'pro'
          ? { ai: true, upcoming: true, advanced_analytics: true }
          : { ai: false, upcoming: false, advanced_analytics: false };
        const mergedFeatures = { ...baseFeatures, ...(c.features || {}) };

        enriched.push({
          id: c.id,
          name: c.name,
          code: c.code,
          plan: c.plan || 'basic',
          billing_cycle: c.billing_cycle || 'monthly',
          subscription_expires_at: c.subscription_expires_at ? new Date(c.subscription_expires_at).toISOString().replace('T', ' ').slice(0, 19) : null,
          status: c.status === 'suspended' || c.status === 0 ? 0 : 1,
          max_users: c.max_users || 10,
          phone: c.phone || '',
          email: c.email || '',
          address: c.address || '',
          features: mergedFeatures,
          created_at: c.created_at,
          employees_count: wCount + uCount,
          workers_count: wCount,
          users_count: uCount,
          products_count: pCount,
          total_sales_count: sCount,
          total_revenue: rev,
          is_expired: isExpired
        });
      }

      return res.status(200).json({
        code: 0,
        message: 'success',
        data: {
          total: enriched.length,
          list: enriched
        }
      });
    }

    if (path === 'company/current') {
      const isSuper = authUser?.role === 'Super Administrator' || authUser?.sub === 'admin';
      const compId = authUser?.company_id || 'comp-default';
      const [comp] = await sql`SELECT * FROM companies WHERE id = ${compId} LIMIT 1`;
      const targetComp = comp || { id: 'comp-default', name: 'Bosh Korxona', code: 'default', plan: 'pro', billing_cycle: 'monthly', status: 1 };
      return res.status(200).json({
        code: 0,
        data: {
          company_id: targetComp.id,
          name: targetComp.name,
          code: targetComp.code,
          plan: isSuper ? 'pro' : (targetComp.plan || 'basic'),
          billing_cycle: targetComp.billing_cycle || 'monthly',
          subscription_expires_at: targetComp.subscription_expires_at,
          status: targetComp.status === 'suspended' || targetComp.status === 0 ? 0 : 1,
          features: isSuper ? { ai: true, upcoming: true, advanced_analytics: true } : (targetComp.features || {}),
          is_super_admin: isSuper
        }
      });
    }

    if (path.startsWith('company/detail')) {
      let compId = req.query?.id || urlSearchParams.get('id');
      if (!compId) {
        const parts = path.split('/');
        if (parts.length > 2) compId = parts[2];
      }
      if (!compId) compId = 'comp-default';

      const [c] = await sql`SELECT * FROM companies WHERE id = ${compId} LIMIT 1`;
      if (!c) {
        return res.status(404).json({ code: 404, message: 'Kompaniya topilmadi' });
      }

      const workers = await sql`SELECT * FROM workers WHERE company_id = ${c.id} ORDER BY id DESC`;
      const users = await sql`SELECT id, username, full_name, role, email, phone, company_id FROM users WHERE company_id = ${c.id} ORDER BY id DESC`;
      const sales = await sql`SELECT id, customer_name, customer_phone, total_amount, paid_amount, debt_amount, "createTime" FROM sales WHERE company_id = ${c.id} ORDER BY id DESC`;
      const products = await sql`SELECT id, "productName", category, price, "quantityInStock" as stock FROM products WHERE company_id = ${c.id} ORDER BY id DESC`;

      const totalEmployees = workers.length + users.length;
      const maxUsers = c.max_users || 10;
      const usagePercent = Math.min(100, Math.round((totalEmployees / maxUsers) * 100));

      const totalRevenue = sales.reduce((acc, s) => acc + (parseFloat(s.paid_amount) || 0), 0);
      const totalSalesAmount = sales.reduce((acc, s) => acc + (parseFloat(s.total_amount) || 0), 0);
      const totalDebt = sales.reduce((acc, s) => acc + (parseFloat(s.debt_amount) || 0), 0);
      const debtorsCount = sales.filter(s => (parseFloat(s.debt_amount) || 0) > 0).length;

      const totalStock = products.reduce((acc, p) => acc + (parseFloat(p.stock) || 0), 0);
      const inventoryVal = products.reduce((acc, p) => acc + ((parseFloat(p.stock) || 0) * (parseFloat(p.price) || 0)), 0);

      const now = new Date();
      const isExpired = c.subscription_expires_at ? new Date(c.subscription_expires_at) < now : false;

      return res.status(200).json({
        code: 0,
        data: {
          id: c.id,
          name: c.name,
          code: c.code,
          plan: c.plan || 'basic',
          billing_cycle: c.billing_cycle || 'monthly',
          subscription_expires_at: c.subscription_expires_at ? new Date(c.subscription_expires_at).toISOString().replace('T', ' ').slice(0, 19) : null,
          status: c.status === 'suspended' || c.status === 0 ? 0 : 1,
          max_users: maxUsers,
          usage_percent: usagePercent,
          phone: c.phone || '',
          email: c.email || '',
          address: c.address || '',
          features: c.features || {},
          created_at: c.created_at,
          is_expired: isExpired,
          stats: {
            employees_count: totalEmployees,
            workers_count: workers.length,
            users_count: users.length,
            max_users: maxUsers,
            usage_percent: usagePercent,
            products_count: products.length,
            total_stock: totalStock,
            inventory_value: inventoryVal,
            total_sales_count: sales.length,
            total_revenue: totalRevenue,
            total_sales_amount: totalSalesAmount,
            total_debt: totalDebt,
            debtors_count: debtorsCount
          },
          workers: workers.map(w => ({
            id: w.id,
            name: w.name || '',
            role: w.role || 'Xodim',
            phone: w.phone || '',
            account: w.account || w.employee_code || '',
            employee_code: w.employee_code || '',
            department: w.departmentId || w.department_id || '',
            hireDate: w.entry_date || '',
            status: w.status !== 0 ? 1 : 0,
            baseSalary: parseFloat(w.baseSalary || w.base_salary || 0),
            company_id: w.company_id
          })),
          users: users,
          recent_sales: sales.slice(0, 10),
          top_products: products.slice(0, 10)
        }
      });
    }

    if (path === 'company/save' && req.method === 'POST') {
      const { id, name, code, plan, billing_cycle, subscription_expires_at, status, max_users, phone, email, address, features, admin_username, admin_password } = req.body || {};
      if (!name) return res.status(400).json({ code: 400, message: 'Kompaniya nomi majburiy' });

      let compId = id;
      const cleanCode = (code || `comp_${Date.now().toString(36)}`).trim();

      if (compId) {
        await sql`
          UPDATE companies
          SET name = ${name}, code = ${cleanCode}, plan = ${plan || 'basic'}, billing_cycle = ${billing_cycle || 'monthly'},
              subscription_expires_at = ${subscription_expires_at || null}, status = ${status !== undefined ? String(status) : '1'},
              max_users = ${max_users || 10}, phone = ${phone || null}, email = ${email || null}, address = ${address || null},
              features = ${JSON.stringify(features || {})}, updated_at = NOW()
          WHERE id = ${compId}
        `;
      } else {
        compId = `comp_${Date.now().toString(36)}`;
        await sql`
          INSERT INTO companies (id, name, code, plan, billing_cycle, subscription_expires_at, status, max_users, phone, email, address, features, created_at, updated_at)
          VALUES (${compId}, ${name}, ${cleanCode}, ${plan || 'basic'}, ${billing_cycle || 'monthly'}, ${subscription_expires_at || null},
                  ${status !== undefined ? String(status) : '1'}, ${max_users || 10}, ${phone || null}, ${email || null}, ${address || null},
                  ${JSON.stringify(features || {})}, NOW(), NOW())
        `;
      }

      if (admin_username && admin_password) {
        const [existing] = await sql`SELECT id FROM users WHERE username = ${admin_username} LIMIT 1`;
        if (!existing) {
          await sql`
            INSERT INTO users (username, password, full_name, role, "roleId", company_id, permissions)
            VALUES (${admin_username}, ${admin_password}, ${name + ' Admin'}, 'Administrator', '2', ${compId}, '["*.*.*"]'::jsonb)
          `;
        }
      }

      return res.status(200).json({ code: 0, message: 'Kompaniya saqlandi', data: { id: compId } });
    }

    if (path === 'company/tier' && req.method === 'POST') {
      const { company_id, plan, billing_cycle, duration_months, subscription_expires_at, max_users, features } = req.body || {};
      if (!company_id) return res.status(400).json({ code: 400, message: 'Kompaniya ID ko\'rsatilmadi' });

      let expDate = subscription_expires_at;
      if (!expDate && duration_months) {
        const d = new Date();
        d.setDate(d.getDate() + Math.round(duration_months * 30.5));
        expDate = d.toISOString();
      }

      const planFeatures = plan === 'pro' ? { ai: true, upcoming: true } : { ai: false, upcoming: false };
      const finalFeatures = { ...planFeatures, ...(features || {}) };

      await sql`
        UPDATE companies
        SET plan = ${plan || 'basic'}, billing_cycle = ${billing_cycle || 'monthly'},
            subscription_expires_at = ${expDate || null}, max_users = COALESCE(${max_users || null}, max_users),
            features = ${JSON.stringify(finalFeatures)}, updated_at = NOW()
        WHERE id = ${company_id}
      `;

      return res.status(200).json({ code: 0, message: 'Tarif muvaffaqiyatli yangilandi' });
    }

    if (path === 'company/status' && req.method === 'POST') {
      const { company_id, id, status } = req.body || {};
      const targetId = company_id || id;
      if (!targetId) return res.status(400).json({ code: 400, message: 'Kompaniya ID ko\'rsatilmadi' });

      const statusStr = String(status);
      await sql`UPDATE companies SET status = ${statusStr}, updated_at = NOW() WHERE id = ${targetId}`;
      return res.status(200).json({ code: 0, message: 'Kompaniya holati yangilandi', data: { id: targetId, status } });
    }

    if (path === 'company/delete' && req.method === 'POST') {
      const { id, company_id } = req.body || {};
      const targetId = id || company_id;
      if (!targetId) return res.status(400).json({ code: 400, message: 'Kompaniya ID ko\'rsatilmadi' });
      if (targetId === 'comp-default') return res.status(400).json({ code: 400, message: 'Bosh korxonani o\'chirib bo\'lmaydi' });

      await sql`DELETE FROM sale_items WHERE sale_id IN (SELECT id FROM sales WHERE company_id = ${targetId})`;
      await sql`DELETE FROM sales WHERE company_id = ${targetId}`;
      await sql`DELETE FROM products WHERE company_id = ${targetId}`;
      await sql`DELETE FROM workers WHERE company_id = ${targetId}`;
      await sql`DELETE FROM users WHERE company_id = ${targetId}`;
      await sql`DELETE FROM companies WHERE id = ${targetId}`;

      return res.status(200).json({ code: 0, message: 'Kompaniya o\'chirildi' });
    }

    if (path === 'company/employee/save' && req.method === 'POST') {
      const { id, company_id, name, role, phone, account, employee_code, department, status, baseSalary, hireDate } = req.body || {};
      if (!company_id) return res.status(400).json({ code: 400, message: 'Kompaniya ID ko\'rsatilmadi' });
      if (!name) return res.status(400).json({ code: 400, message: 'Xodim ismi majburiy' });

      let empId = id;
      if (empId) {
        await sql`
          UPDATE workers
          SET name = ${name}, role = ${role || 'Xodim'}, phone = ${phone || null},
              account = ${account || null}, employee_code = ${employee_code || null},
              "departmentId" = ${department || null}, department_id = ${department || null},
              status = ${status !== undefined ? status : 1}, "baseSalary" = ${baseSalary || 0},
              entry_date = ${hireDate || null}
          WHERE id = ${empId}
        `;
      } else {
        empId = `w_${Date.now().toString(36)}`;
        await sql`
          INSERT INTO workers (id, name, role, phone, account, employee_code, "departmentId", department_id, status, "baseSalary", entry_date, company_id, "createTime")
          VALUES (${empId}, ${name}, ${role || 'Xodim'}, ${phone || null}, ${account || null}, ${employee_code || null},
                  ${department || null}, ${department || null}, ${status !== undefined ? status : 1}, ${baseSalary || 0},
                  ${hireDate || null}, ${company_id}, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
        `;
      }

      return res.status(200).json({ code: 0, message: 'Xodim saqlandi', data: { id: empId, name } });
    }

    if (path === 'company/employee/delete' && req.method === 'POST') {
      const { id } = req.body || {};
      if (!id) return res.status(400).json({ code: 400, message: 'Xodim ID ko\'rsatilmadi' });
      await sql`DELETE FROM workers WHERE id = ${id}`;
      return res.status(200).json({ code: 0, message: 'Xodim o\'chirildi' });
    }

    if (path === 'department/user/delete' && req.method === 'POST') {
      let ids = req.body?.ids;
      if (!ids && req.body?.id) ids = [req.body.id];
      if (Array.isArray(ids) && ids.length > 0) {
        await sql`UPDATE workers SET "departmentId" = NULL, department_id = NULL WHERE id = ANY(${ids})`;
        return res.status(200).json({ code: 0, data: 'success', message: "Xodim bo'limdan chiqarildi" });
      }
      return res.status(200).json({ code: 400, message: "ID ko'rsatilmadi" });
    }

    // 12. GET /api/salary/list
    if (path === 'salary/list') {
      const pageIndex = parseInt(req.query?.pageIndex || urlSearchParams.get('pageIndex') || 1, 10);
      const pageSize = parseInt(req.query?.pageSize || urlSearchParams.get('pageSize') || 500, 10);
      const offset = (pageIndex - 1) * pageSize;
      const [countRes, rows] = await Promise.all([
        sql`SELECT count(*) FROM salaries`,
        sql`SELECT * FROM salaries ORDER BY id DESC LIMIT ${pageSize} OFFSET ${offset}`
      ]);
      return res.status(200).json({
        code: 0,
        data: {
          total: parseInt(countRes[0].count, 10),
          list: rows
        }
      });
    }

    // POST /api/salary/delete
    if (path === 'salary/delete' && req.method === 'POST') {
      const { ids } = req.body || {};
      if (Array.isArray(ids) && ids.length > 0) {
        await sql`DELETE FROM salaries WHERE id = ANY(${ids})`;
      } else {
        await sql`DELETE FROM salaries`;
      }
      return res.status(200).json({ code: 0, message: "O'chirildi" });
    }

    // POST /api/salary/clear
    if (path === 'salary/clear' && req.method === 'POST') {
      await sql`DELETE FROM salaries`;
      return res.status(200).json({ code: 0, message: "Barcha maoshlar tozalandi" });
    }

    // POST /api/salary/save
    if (path === 'salary/save' && req.method === 'POST') {
      const { id, workerId, baseSalary, allowance, deduction, netSalary, payDate, status, remark } = req.body || {};
      const calculatedNet = parseFloat(netSalary) || ((parseFloat(baseSalary) || 0) + (parseFloat(allowance) || 0) - (parseFloat(deduction) || 0));
      if (id) {
        await sql`
          UPDATE salaries 
          SET "workerId" = ${workerId}, "baseSalary" = ${parseFloat(baseSalary) || 0}, allowance = ${parseFloat(allowance) || 0}, deduction = ${parseFloat(deduction) || 0}, "netSalary" = ${calculatedNet}, "payDate" = ${payDate}, status = ${status || 'paid'}, remark = ${remark}
          WHERE id = ${id}
        `;
      } else {
        const newId = 'S' + Math.floor(100000 + Math.random() * 900000);
        await sql`
          INSERT INTO salaries (id, "workerId", "baseSalary", allowance, deduction, "netSalary", "payDate", status, remark)
          VALUES (${newId}, ${workerId}, ${parseFloat(baseSalary) || 0}, ${parseFloat(allowance) || 0}, ${parseFloat(deduction) || 0}, ${calculatedNet}, ${payDate || to_char(NOW(), 'YYYY-MM-DD')}, ${status || 'paid'}, ${remark})
        `;
      }
      return res.status(200).json({ code: 0, message: 'Saqlandi' });
    }

    // POST /api/salary/payout
    if (path === 'salary/payout' && req.method === 'POST') {
      const { items, period_month, remark } = req.body || {};
      if (Array.isArray(items) && items.length > 0) {
        for (const item of items) {
          const newId = 'S' + Math.floor(100000 + Math.random() * 900000);
          const base = parseFloat(item.baseSalary) || 0;
          const allow = parseFloat(item.allowance) || 0;
          const ded = parseFloat(item.deduction) || 0;
          const net = base + allow - ded;
          await sql`
            INSERT INTO salaries (id, "workerId", "baseSalary", allowance, deduction, "netSalary", "payDate", status, remark)
            VALUES (${newId}, ${item.workerId}, ${base}, ${allow}, ${ded}, ${net}, to_char(NOW(), 'YYYY-MM-DD'), 'paid', ${remark || (period_month ? period_month + ' oylik maoshi' : 'Oylik maosh')})
          `;
        }
      }
      return res.status(200).json({ code: 0, message: 'Maoshlar muvaffaqiyatli tarqatildi' });
    }

    // 13. GET /api/sales/list
    if (path === 'sales/list') {
      const pageIndex = parseInt(req.query?.pageIndex || urlSearchParams.get('pageIndex') || 1, 10);
      const pageSize = parseInt(req.query?.pageSize || urlSearchParams.get('pageSize') || 500, 10);
      const offset = (pageIndex - 1) * pageSize;
      const targetCompany = req.query?.company_id || urlSearchParams.get('company_id') || getReqCompanyId(req, authUser);

      const [statsRes, rows] = await Promise.all([
        targetCompany
          ? sql`
              SELECT 
                count(*) as all_time_count,
                COALESCE(SUM(total_amount), 0) as all_time_revenue,
                COALESCE(SUM(total_items), 0) as all_time_items,
                COUNT(*) FILTER (WHERE substring(created_at from 1 for 10) = to_char(NOW() AT TIME ZONE 'Asia/Tashkent', 'YYYY-MM-DD')) as today_count,
                COALESCE(SUM(total_amount) FILTER (WHERE substring(created_at from 1 for 10) = to_char(NOW() AT TIME ZONE 'Asia/Tashkent', 'YYYY-MM-DD')), 0) as today_revenue,
                COALESCE(SUM(total_items) FILTER (WHERE substring(created_at from 1 for 10) = to_char(NOW() AT TIME ZONE 'Asia/Tashkent', 'YYYY-MM-DD')), 0) as today_items
              FROM sales
              WHERE company_id = ${targetCompany}
            `
          : sql`
              SELECT 
                count(*) as all_time_count,
                COALESCE(SUM(total_amount), 0) as all_time_revenue,
                COALESCE(SUM(total_items), 0) as all_time_items,
                COUNT(*) FILTER (WHERE substring(created_at from 1 for 10) = to_char(NOW() AT TIME ZONE 'Asia/Tashkent', 'YYYY-MM-DD')) as today_count,
                COALESCE(SUM(total_amount) FILTER (WHERE substring(created_at from 1 for 10) = to_char(NOW() AT TIME ZONE 'Asia/Tashkent', 'YYYY-MM-DD')), 0) as today_revenue,
                COALESCE(SUM(total_items) FILTER (WHERE substring(created_at from 1 for 10) = to_char(NOW() AT TIME ZONE 'Asia/Tashkent', 'YYYY-MM-DD')), 0) as today_items
              FROM sales
            `,
        targetCompany
          ? sql`SELECT * FROM sales WHERE company_id = ${targetCompany} ORDER BY id DESC LIMIT ${pageSize} OFFSET ${offset}`
          : sql`SELECT * FROM sales ORDER BY id DESC LIMIT ${pageSize} OFFSET ${offset}`
      ]);

      const statsRow = statsRes[0] || {};
      const summary = {
        todayCount: parseInt(statsRow.today_count, 10) || 0,
        todayRevenue: parseFloat(statsRow.today_revenue) || 0,
        todayItems: parseInt(statsRow.today_items, 10) || 0,
        allTimeCount: parseInt(statsRow.all_time_count, 10) || 0,
        allTimeRevenue: parseFloat(statsRow.all_time_revenue) || 0,
        allTimeItems: parseInt(statsRow.all_time_items, 10) || 0
      };

      const saleIds = rows.map(r => r.id).filter(Boolean);
      const itemsMap = {};
      if (saleIds.length > 0) {
        try {
          const items = await sql`SELECT * FROM sale_items WHERE sale_id = ANY(${saleIds}) ORDER BY id ASC`;
          for (const it of items) {
            if (!itemsMap[it.sale_id]) {
              itemsMap[it.sale_id] = [];
            }
            itemsMap[it.sale_id].push({
              ...it,
              price: parseFloat(it.price) || 0,
              cost: parseFloat(it.cost) || 0,
              quantity: parseFloat(it.quantity) || 1,
              total: parseFloat(it.total) || ((parseFloat(it.price) || 0) * (parseFloat(it.quantity) || 1))
            });
          }
        } catch (e) {
          console.warn('Batch sale_items error:', e.message);
        }
      }

      const listWithItems = rows.map(r => {
        let its = itemsMap[r.id] || [];
        if (its.length === 0 && parseFloat(r.total_amount) > 0) {
          its = [{
            id: 'ITEM-' + r.id,
            sale_id: r.id,
            product_name: r.remark || 'Ombor mahsuloti',
            shtrix_code: 'CHK-' + (r.receipt_number || '').slice(-4),
            price: parseFloat(r.total_amount) / (parseInt(r.total_items, 10) || 1),
            cost: (parseFloat(r.total_amount) * 0.7) / (parseInt(r.total_items, 10) || 1),
            quantity: parseInt(r.total_items, 10) || 1,
            unit_name: 'dona',
            total: parseFloat(r.total_amount)
          }];
        }
        return {
          ...r,
          total_amount: parseFloat(r.total_amount) || 0,
          paid_amount: parseFloat(r.paid_amount) || 0,
          debt_amount: parseFloat(r.debt_amount) || 0,
          items: its
        };
      });

      return res.status(200).json({
        code: 0,
        data: {
          total: summary.allTimeCount,
          list: listWithItems,
          summary
        }
      });
    }

    // GET /api/sales/debtors
    if (path === 'sales/debtors') {
      try {
        const search = (req.query?.search || urlSearchParams.get('search') || '').toLowerCase().trim();
        const statusFilter = req.query?.status || urlSearchParams.get('status');

        let debtSales = [];
        let payments = [];

        try {
          debtSales = await sql`SELECT * FROM sales WHERE payment_method = 'nasiya' OR (debt_amount IS NOT NULL AND debt_amount > 0) ORDER BY created_at DESC`;
        } catch (sErr) {
          console.warn('debtSales query warning:', sErr.message);
          debtSales = [];
        }

        try {
          payments = await sql`SELECT * FROM debt_payments ORDER BY created_at DESC`;
        } catch (pErr) {
          console.warn('payments query warning:', pErr.message);
          payments = [];
        }

        const debtorMap = {};

        for (const s of debtSales) {
          const name = s.customer_name?.trim() || ('Qarzdor (' + (s.receipt_number || '').slice(-4) + ')');
          if (!debtorMap[name]) {
            debtorMap[name] = {
              name: name,
              phone: s.customer_phone || '',
              total_initial_debt: 0,
              total_repaid: 0,
              total_debt: 0,
              status: 'active',
              deals_count: 0,
              last_sale_date: s.created_at || ''
            };
          }
          const debtVal = parseFloat(s.debt_amount || (s.total_amount - (s.paid_amount || 0)) || 0);
          debtorMap[name].total_initial_debt += debtVal;
          debtorMap[name].deals_count += 1;
          if (!debtorMap[name].phone && s.customer_phone) {
            debtorMap[name].phone = s.customer_phone;
          }
          if (s.created_at && (!debtorMap[name].last_sale_date || s.created_at > debtorMap[name].last_sale_date)) {
            debtorMap[name].last_sale_date = s.created_at;
          }
        }

        for (const p of payments) {
          const name = p.customer_name?.trim();
          if (name && debtorMap[name]) {
            debtorMap[name].total_repaid += parseFloat(p.amount || 0);
          }
        }

        let list = Object.values(debtorMap).map(d => {
          const currentDebt = Math.max(0, d.total_initial_debt - d.total_repaid);
          return {
            name: d.name,
            phone: d.phone,
            total_initial_debt: d.total_initial_debt,
            total_repaid: d.total_repaid,
            total_debt: currentDebt,
            current_balance: currentDebt,
            status: currentDebt <= 0 ? 'settled' : 'active',
            sales_count: d.deals_count,
            deals_count: d.deals_count,
            last_sale_date: d.last_sale_date
          };
        });

        if (search) {
          list = list.filter(d => d.name.toLowerCase().includes(search) || (d.phone && d.phone.includes(search)));
        }

        if (statusFilter && statusFilter !== 'all') {
          list = list.filter(d => d.status === statusFilter);
        }

        const total_debt = list.reduce((acc, d) => acc + d.total_debt, 0);
        const total_repaid = list.reduce((acc, d) => acc + d.total_repaid, 0);
        const active_debtors_count = list.filter(d => d.total_debt > 0).length;

        return res.status(200).json({
          code: 0,
          data: {
            list,
            total_debt,
            total_repaid,
            active_debtors_count,
            total: list.length
          }
        });
      } catch (err) {
        console.error('sales/debtors error:', err);
        return res.status(200).json({
          code: 0,
          data: {
            list: [],
            total_debt: 0,
            total_repaid: 0,
            active_debtors_count: 0,
            total: 0
          }
        });
      }
    }

    // GET /api/sales/debtor-detail
    if (path === 'sales/debtor-detail') {
      try {
        const name = req.query?.name || urlSearchParams.get('name');
        if (!name) {
          return res.status(200).json({ code: 0, data: null });
        }

        let debtSales = [];
        let payments = [];

        try {
          debtSales = await sql`
            SELECT * FROM sales 
            WHERE (customer_name = ${name} OR receipt_number LIKE ${'%' + name + '%'}) 
              AND (payment_method = 'nasiya' OR (debt_amount IS NOT NULL AND debt_amount > 0))
            ORDER BY created_at DESC
          `;
        } catch (sErr) {
          console.warn('debtor-detail debtSales error:', sErr.message);
          debtSales = [];
        }

        try {
          payments = await sql`
            SELECT * FROM debt_payments 
            WHERE customer_name = ${name}
            ORDER BY created_at DESC
          `;
        } catch (pErr) {
          console.warn('debtor-detail payments error:', pErr.message);
          payments = [];
        }

        const phone = debtSales[0]?.customer_phone || payments[0]?.customer_phone || '';
        const total_debt = debtSales.reduce((acc, s) => acc + parseFloat(s.debt_amount || (s.total_amount - (s.paid_amount || 0)) || 0), 0);
        const total_repaid = payments.reduce((acc, p) => acc + parseFloat(p.amount || 0), 0);
        const current_balance = Math.max(0, total_debt - total_repaid);

        return res.status(200).json({
          code: 0,
          data: {
            customer_name: name,
            phone: phone,
            total_debt: current_balance,
            total_repaid: total_repaid,
            initial_debt: total_debt,
            status: current_balance <= 0 ? 'settled' : 'active',
            sales: debtSales,
            payments: payments
          }
        });
      } catch (err) {
        console.error('sales/debtor-detail error:', err);
        return res.status(200).json({ code: 0, data: null });
      }
    }

    // POST /api/sales/repay-debt
    if (path === 'sales/repay-debt' && req.method === 'POST') {
      try {
        const { customer_name, customer_phone, amount, payment_method, cashier_name, remark } = req.body || {};
        const numAmount = parseFloat(amount) || 0;
        const receipt_number = 'PAY-' + Date.now().toString(36).toUpperCase() + '-' + Math.floor(1000 + Math.random() * 9000);
        const paymentId = 'PMT-' + Date.now().toString(36);
        const nowStr = new Date().toISOString().replace('T', ' ').substring(0, 19);

        try {
          await sql`
            INSERT INTO debt_payments (id, receipt_number, customer_name, customer_phone, amount, payment_method, cashier_name, remark, created_at)
            VALUES (${paymentId}, ${receipt_number}, ${customer_name}, ${customer_phone || null}, ${numAmount}, ${payment_method || 'naqd'}, ${cashier_name || 'admin'}, ${remark || null}, ${nowStr})
          `;
        } catch (insErr) {
          console.warn('repay-debt insert warning:', insErr.message);
        }

        let debtSales = [];
        let allPayments = [];

        try {
          debtSales = await sql`
            SELECT * FROM sales 
            WHERE (customer_name = ${customer_name}) 
              AND (payment_method = 'nasiya' OR (debt_amount IS NOT NULL AND debt_amount > 0))
          `;
          allPayments = await sql`SELECT * FROM debt_payments WHERE customer_name = ${customer_name}`;
        } catch (qErr) {
          console.warn('repay-debt recalculate warning:', qErr.message);
        }

        const totalInitial = debtSales.reduce((acc, s) => acc + parseFloat(s.debt_amount || (s.total_amount - (s.paid_amount || 0)) || 0), 0);
        const totalPaid = allPayments.reduce((acc, p) => acc + parseFloat(p.amount || 0), 0);
        const remaining_debt = Math.max(0, totalInitial - totalPaid);

        return res.status(200).json({
          code: 0,
          data: {
            id: paymentId,
            receipt_number: receipt_number,
            customer_name: customer_name,
            customer_phone: customer_phone,
            amount: numAmount,
            payment_method: payment_method || 'naqd',
            cashier_name: cashier_name || 'admin',
            remark: remark,
            created_at: nowStr,
            remaining_debt: remaining_debt
          },
          message: "Qarz to'lovi muvaffaqiyatli qabul qilindi"
        });
      } catch (err) {
        console.error('sales/repay-debt error:', err);
        return res.status(500).json({ code: 500, message: "Qarz to'lovini saqlashda xatolik yuz berdi" });
      }
    }

    // POST /api/sales/checkout
    if (path === 'sales/checkout' && req.method === 'POST') {
      const {
        receipt_number,
        cashier_name,
        customer_name,
        customer_phone,
        payment_method,
        total_amount,
        paid_amount,
        debt_amount,
        total_items,
        discount,
        remark,
        items
      } = req.body || {};

      const saleId = 'SALE-' + Date.now().toString(36) + '-' + Math.floor(100 + Math.random() * 900);
      const recNo = receipt_number || ('CHK-' + Date.now().toString(36).toUpperCase());
      const nowStr = new Date().toISOString().replace('T', ' ').substring(0, 19);

      let tAmount = parseFloat(total_amount);
      if (isNaN(tAmount) || tAmount <= 0) {
        if (Array.isArray(items) && items.length > 0) {
          tAmount = items.reduce((acc, it) => acc + (parseFloat(it.total) || (parseFloat(it.price) || 0) * (parseFloat(it.quantity) || 1)), 0);
        } else {
          tAmount = 0;
        }
      }

      const pAmount = parseFloat(paid_amount) || 0;
      const dAmount = parseFloat(debt_amount) || (payment_method === 'nasiya' ? Math.max(0, tAmount - pAmount) : 0);
      const targetCompany = req.body?.company_id || getReqCompanyId(req, authUser);

      await sql`
        INSERT INTO sales (
          id, company_id, receipt_number, cashier_name, customer_name, customer_phone,
          payment_method, total_amount, paid_amount, debt_amount, total_items,
          discount, remark, created_at
        ) VALUES (
          ${saleId}, ${targetCompany}, ${recNo}, ${cashier_name || 'admin'}, ${customer_name || null}, ${customer_phone || null},
          ${payment_method || 'naqd'}, ${tAmount}, ${pAmount}, ${dAmount}, ${parseInt(total_items || (items ? items.length : 1), 10)},
          ${parseFloat(discount) || 0}, ${remark || null}, ${nowStr}
        )
      `;

      if (Array.isArray(items) && items.length > 0) {
        for (const item of items) {
          const itemId = 'SITEM-' + Date.now().toString(36) + '-' + Math.floor(1000 + Math.random() * 9000);
          await sql`
            INSERT INTO sale_items (
              id, sale_id, product_id, product_name, shtrix_code,
              price, cost, quantity, unit_name, total
            ) VALUES (
              ${itemId}, ${saleId}, ${item.product_id || item.id}, ${item.product_name || item.productName}, ${item.shtrix_code || item.SKU || null},
              ${parseFloat(item.price) || 0}, ${parseFloat(item.cost) || 0}, ${parseInt(item.quantity || 1, 10)}, ${item.unit_name || item.unit || 'dona'}, ${parseFloat(item.total || (item.price * (item.quantity || 1))) || 0}
            )
          `;
          if (item.product_id || item.id) {
            await sql`
              UPDATE products 
              SET "quantityInStock" = GREATEST(0, "quantityInStock" - ${parseInt(item.quantity || 1, 10)})
              WHERE id = ${item.product_id || item.id}
            `;
          }
        }
      }

      return res.status(200).json({
        code: 0,
        data: {
          id: saleId,
          receipt_number: recNo,
          total_amount: tAmount,
          paid_amount: pAmount,
          debt_amount: dAmount,
          payment_method: payment_method || 'naqd',
          cashier_name: cashier_name || 'admin',
          customer_name: customer_name,
          created_at: nowStr
        },
        message: 'Sotuv muvaffaqiyatli amalga oshirildi'
      });
    }

    // GET /api/sales/receipt/:no
    if (path.startsWith('sales/receipt/')) {
      const receiptNo = path.replace('sales/receipt/', '');
      const salesRows = await sql`SELECT * FROM sales WHERE receipt_number = ${receiptNo} OR id = ${receiptNo}`;
      const sale = salesRows[0];
      if (!sale) {
        return res.status(200).json({ code: 0, data: null });
      }
      let items = await sql`SELECT * FROM sale_items WHERE sale_id = ${sale.id}`;

      // Fallback for older seeded sales that don't have separate sale_items entries
      if ((!items || items.length === 0) && parseFloat(sale.total_amount) > 0) {
        items = [{
          id: 'ITEM-' + sale.id,
          sale_id: sale.id,
          product_name: sale.remark || 'Ombor mahsulotlari to\'plami',
          shtrix_code: 'ERP-CHK-' + (sale.receipt_number || '').slice(-4),
          price: parseFloat(sale.total_amount) / (parseInt(sale.total_items) || 1),
          cost: parseFloat(sale.total_amount) * 0.7 / (parseInt(sale.total_items) || 1),
          quantity: parseInt(sale.total_items) || 1,
          unit_name: 'dona',
          total: parseFloat(sale.total_amount)
        }];
      }

      let totalAmount = parseFloat(sale.total_amount) || 0;
      if (totalAmount === 0 && items && items.length > 0) {
        totalAmount = items.reduce((sum, it) => sum + (parseFloat(it.total) || (parseFloat(it.price) || 0) * (parseFloat(it.quantity) || 1)), 0);
      }

      return res.status(200).json({
        code: 0,
        data: {
          ...sale,
          total_amount: totalAmount,
          items: items || []
        }
      });
    }

    // GET /api/sales/top-selling
    if (path === 'sales/top-selling') {
      const topItems = await sql`
        SELECT 
          product_name, 
          SUM(quantity) as total_qty, 
          SUM(total) as total_revenue,
          COUNT(DISTINCT sale_id) as orders_count
        FROM sale_items 
        GROUP BY product_name 
        ORDER BY total_qty DESC 
        LIMIT 10
      `;
      return res.status(200).json({
        code: 0,
        data: topItems.map(it => ({
          name: it.product_name,
          quantity: parseInt(it.total_qty || 0, 10),
          revenue: parseFloat(it.total_revenue || 0),
          orders_count: parseInt(it.orders_count || 0, 10)
        }))
      });
    }

    // GET /api/sales/analytics
    if (path === 'sales/analytics') {
      const [totalsRes, topRes, pmRes] = await Promise.all([
        sql`SELECT COUNT(*) as count, SUM(total_amount) as total_revenue, SUM(paid_amount) as total_paid, SUM(debt_amount) as total_debt FROM sales`,
        sql`SELECT product_name, SUM(quantity) as total_qty, SUM(total) as total_revenue FROM sale_items GROUP BY product_name ORDER BY total_qty DESC LIMIT 5`,
        sql`SELECT payment_method, COUNT(*) as count, SUM(total_amount) as revenue FROM sales GROUP BY payment_method`
      ]);
      return res.status(200).json({
        code: 0,
        data: {
          total_sales: parseInt(totalsRes[0]?.count || 0, 10),
          total_revenue: parseFloat(totalsRes[0]?.total_revenue || 0),
          total_paid: parseFloat(totalsRes[0]?.total_paid || 0),
          total_debt: parseFloat(totalsRes[0]?.total_debt || 0),
          top_products: topRes.map(it => ({
            name: it.product_name,
            quantity: parseInt(it.total_qty || 0, 10),
            revenue: parseFloat(it.total_revenue || 0)
          })),
          payment_methods: pmRes.map(it => ({
            method: it.payment_method,
            count: parseInt(it.count || 0, 10),
            revenue: parseFloat(it.revenue || 0)
          }))
        }
      });
    }

    // GET /api/analysis/bundle or /api/analysis/financial-overview
    if (path === 'analysis/bundle' || path === 'analysis/financial-overview') {
      const selMonth = urlSearchParams.get('month') || new Date().toISOString().slice(0, 7);

      const months = [];
      const d = new Date();
      for (let i = 5; i >= 0; i--) {
        const past = new Date(d.getFullYear(), d.getMonth() - i, 1);
        months.push(past.toISOString().slice(0, 7));
      }

      const targetCompany = req.query?.company_id || urlSearchParams.get('company_id') || getReqCompanyId(req, authUser);

      const [sales, saleItems, salaries, outputs, debtors, products] = await Promise.all([
        targetCompany
          ? sql`SELECT id, total_amount, paid_amount, debt_amount, created_at FROM sales WHERE company_id = ${targetCompany}`
          : sql`SELECT id, total_amount, paid_amount, debt_amount, created_at FROM sales`,
        targetCompany
          ? sql`SELECT si.sale_id, si.product_id, si.quantity, si.cost, si.total, si.price FROM sale_items si JOIN sales s ON s.id = si.sale_id WHERE s.company_id = ${targetCompany}`
          : sql`SELECT sale_id, product_id, quantity, cost, total, price FROM sale_items`,
        sql`SELECT "netSalary", status, "payDate", remark FROM salaries`,
        sql`SELECT amount, "createTime", period_month FROM staff_outputs`,
        targetCompany
          ? sql`SELECT COUNT(DISTINCT customer_name) as debtor_count, SUM(debt_amount) as total_debt FROM sales WHERE debt_amount > 0 AND company_id = ${targetCompany}`
          : sql`SELECT COUNT(DISTINCT customer_name) as debtor_count, SUM(debt_amount) as total_debt FROM sales WHERE debt_amount > 0`,
        targetCompany
          ? sql`SELECT id, category FROM products WHERE company_id = ${targetCompany}`
          : sql`SELECT id, category FROM products`
      ]);

      const costBySale = {};
      for (const it of saleItems) {
        costBySale[it.sale_id] = (costBySale[it.sale_id] || 0) + (parseFloat(it.cost || 0) * parseFloat(it.quantity || 1));
      }

      const prodCatMap = {};
      for (const p of (products || [])) {
        prodCatMap[String(p.id)] = p.category || 'Boshqa';
      }
      const catStats = {};
      for (const it of saleItems) {
        const cat = prodCatMap[String(it.product_id)] || 'Boshqa';
        if (!catStats[cat]) {
          catStats[cat] = { revenue: 0, cost: 0, profit: 0 };
        }
        const rev = parseFloat(it.total || (parseFloat(it.price || 0) * parseFloat(it.quantity || 1)) || 0);
        let cost = parseFloat(it.cost || 0) * parseFloat(it.quantity || 1);
        if (cost === 0 && rev > 0) cost = rev * 0.55;
        catStats[cat].revenue += rev;
        catStats[cat].cost += cost;
        catStats[cat].profit += (rev - cost);
      }
      let categoryProfits = Object.entries(catStats)
        .map(([name, stat]) => ({
          name,
          revenue: Math.round(stat.revenue * 100) / 100,
          cost: Math.round(stat.cost * 100) / 100,
          profit: Math.round(stat.profit * 100) / 100
        }))
        .filter(c => c.revenue > 0)
        .sort((a, b) => b.revenue - a.revenue);

      const calcMonth = (ym) => {
        const mSales = sales.filter(s => (s.created_at || '').startsWith(ym));
        const rev = mSales.reduce((acc, s) => acc + parseFloat(s.total_amount || 0), 0);
        let cogs = mSales.reduce((acc, s) => acc + (costBySale[s.id] || 0), 0);
        if (cogs === 0 && rev > 0) cogs = rev * 0.55;

        const mSalaries = salaries.filter(s => String(s.status).toLowerCase() === 'paid' && ((s.payDate || '').startsWith(ym) || (s.remark || '').includes(ym)));
        const salTotal = mSalaries.reduce((acc, s) => acc + parseFloat(s.netSalary || 0), 0);

        const mOutputs = outputs.filter(o => (o.createTime || '').startsWith(ym) || (o.period_month || '') === ym);
        const outTotal = mOutputs.reduce((acc, o) => acc + parseFloat(o.amount || 0), 0);

        const payroll = salTotal + outTotal;
        const expenses = cogs + payroll;
        const netProfit = rev - expenses;
        const margin = rev > 0 ? (netProfit / rev) * 100 : 0;

        return {
          month: ym,
          period_month: ym,
          revenue: Math.round(rev * 100) / 100,
          cogs: Math.round(cogs * 100) / 100,
          staff_salaries: Math.round(salTotal * 100) / 100,
          staffSalaries: Math.round(salTotal * 100) / 100,
          short_term_outputs: Math.round(outTotal * 100) / 100,
          shortTermOutputs: Math.round(outTotal * 100) / 100,
          total_payroll: Math.round(payroll * 100) / 100,
          totalPayroll: Math.round(payroll * 100) / 100,
          total_expenses: Math.round(expenses * 100) / 100,
          totalExpenses: Math.round(expenses * 100) / 100,
          net_profit: Math.round(netProfit * 100) / 100,
          netProfit: Math.round(netProfit * 100) / 100,
          profit_margin: Math.round(margin * 10) / 10,
          profitMargin: Math.round(margin * 10) / 10,
          margin: Math.round(margin * 10) / 10,
          sales_count: mSales.length,
          salesCount: mSales.length
        };
      };

      const snapshots = months.map(calcMonth);
      const currMonthData = calcMonth(selMonth);

      const totalRev = snapshots.reduce((acc, s) => acc + s.revenue, 0);
      const totalCogs = snapshots.reduce((acc, s) => acc + s.cogs, 0);
      const totalSal = snapshots.reduce((acc, s) => acc + s.staff_salaries, 0);
      const totalOut = snapshots.reduce((acc, s) => acc + s.short_term_outputs, 0);
      const totalPayroll = snapshots.reduce((acc, s) => acc + s.total_payroll, 0);
      const totalExp = snapshots.reduce((acc, s) => acc + s.total_expenses, 0);
      const totalNet = snapshots.reduce((acc, s) => acc + s.net_profit, 0);
      const avgMargin = totalRev > 0 ? (totalNet / totalRev) * 100 : 0;

      if (categoryProfits.length === 0) {
        categoryProfits = [
          { name: 'Ichimliklar va suvlar', revenue: Math.round(totalRev * 0.45 * 100) / 100, cost: Math.round(totalCogs * 0.45 * 100) / 100, profit: Math.round(totalNet * 0.45 * 100) / 100 },
          { name: 'Oziq-ovqat mahsulotlari', revenue: Math.round(totalRev * 0.35 * 100) / 100, cost: Math.round(totalCogs * 0.35 * 100) / 100, profit: Math.round(totalNet * 0.35 * 100) / 100 },
          { name: 'Xo\'jalik mollari', revenue: Math.round(totalRev * 0.20 * 100) / 100, cost: Math.round(totalCogs * 0.20 * 100) / 100, profit: Math.round(totalNet * 0.20 * 100) / 100 }
        ];
      }

      const monthlyFinancials = snapshots.map(s => ({
        month: s.period_month,
        period_month: s.period_month,
        revenue: s.revenue,
        cogs: s.cogs,
        staffSalaries: s.staff_salaries,
        staff_salaries: s.staff_salaries,
        shortTermOutputs: s.short_term_outputs,
        short_term_outputs: s.short_term_outputs,
        totalPayroll: s.total_payroll,
        total_payroll: s.total_payroll,
        totalExpenses: s.total_expenses,
        total_expenses: s.total_expenses,
        netProfit: s.net_profit,
        net_profit: s.net_profit,
        profitMargin: s.profit_margin,
        profit_margin: s.profit_margin,
        margin: s.profit_margin,
        salesCount: s.sales_count,
        sales_count: s.sales_count
      }));

      const expenseBreakdown = [
        { name: 'Mahsulot Tannarxi (COGS)', value: Math.round(totalCogs * 100) / 100 },
        { name: 'Doimiy Xodimlar Maoshi', value: Math.round(totalSal * 100) / 100 },
        { name: 'Qisqa Muddatli Ishchilar To\'lovi', value: Math.round(totalOut * 100) / 100 },
        { name: 'Boshqa Xarajatlar', value: 0 }
      ];

      const overview = {
        grossRevenue: Math.round(totalRev * 100) / 100,
        cogs: Math.round(totalCogs * 100) / 100,
        staffSalaries: Math.round(totalSal * 100) / 100,
        shortTermOutputs: Math.round(totalOut * 100) / 100,
        totalPayroll: Math.round(totalPayroll * 100) / 100,
        totalExpenses: Math.round(totalExp * 100) / 100,
        realNetProfit: Math.round(totalNet * 100) / 100,
        profitMargin: Math.round(avgMargin * 10) / 10,
        revenueGrowth: 12.5,
        profitGrowth: 8.3,
        debtCollected: 0,
        activeDebtorsCount: parseInt(debtors[0]?.debtor_count || 0, 10),
        totalOutstandingDebt: parseFloat(debtors[0]?.total_debt || 0),
        monthlyFinancials,
        expenseBreakdown,
        categoryProfits
      };

      const monthSummary = {
        currentMonth: selMonth,
        salesTotal: currMonthData.revenue,
        expenseTotal: currMonthData.total_expenses,
        netProfit: currMonthData.net_profit,
        salesCount: currMonthData.sales_count,
        salesGrowth: 5.2,
        avgCheck: currMonthData.sales_count > 0 ? Math.round((currMonthData.revenue / currMonthData.sales_count) * 100) / 100 : 0
      };

      const p1 = snapshots[snapshots.length - 2] || currMonthData;
      const p2 = snapshots[snapshots.length - 1] || currMonthData;
      const calcGrowth = (a, b) => {
        if (b === 0) return a === 0 ? 0 : 100;
        return Math.round(((a - b) / Math.abs(b)) * 1000) / 10;
      };

      const revDiff = Math.round((p1.revenue - p2.revenue) * 100) / 100;
      const revGrowth = calcGrowth(p1.revenue, p2.revenue);
      const cogsDiff = Math.round((p1.cogs - p2.cogs) * 100) / 100;
      const cogsGrowth = calcGrowth(p1.cogs, p2.cogs);
      const staffDiff = Math.round((p1.staff_salaries - p2.staff_salaries) * 100) / 100;
      const staffGrowth = calcGrowth(p1.staff_salaries, p2.staff_salaries);
      const shortDiff = Math.round((p1.short_term_outputs - p2.short_term_outputs) * 100) / 100;
      const shortGrowth = calcGrowth(p1.short_term_outputs, p2.short_term_outputs);
      const payrollDiff = Math.round((p1.total_payroll - p2.total_payroll) * 100) / 100;
      const payrollGrowth = calcGrowth(p1.total_payroll, p2.total_payroll);
      const profitDiff = Math.round((p1.net_profit - p2.net_profit) * 100) / 100;
      const profitGrowth = calcGrowth(p1.net_profit, p2.net_profit);
      const marginDiff = Math.round((p1.profit_margin - p2.profit_margin) * 10) / 10;

      const deltas = {
        revDiff,
        revGrowth,
        cogsDiff,
        cogsGrowth,
        staffDiff,
        staffGrowth,
        shortDiff,
        shortGrowth,
        payrollDiff,
        payrollGrowth,
        profitDiff,
        profitGrowth,
        marginDiff
      };

      const comparison = {
        period1: p1,
        period2: p2,
        deltas,
        revenueGrowth: revGrowth,
        profitGrowth: profitGrowth,
        payrollGrowth: payrollGrowth,
        cogsGrowth: cogsGrowth
      };

      if (path === 'analysis/financial-overview') {
        return res.status(200).json({ code: 0, data: overview });
      }

      return res.status(200).json({
        code: 0,
        data: {
          overview,
          snapshots,
          monthSummary,
          comparison
        }
      });
    }

    // GET /api/analysis/snapshot/list
    if (path === 'analysis/snapshot/list') {
      const d = new Date();
      const months = [];
      for (let i = 5; i >= 0; i--) {
        const past = new Date(d.getFullYear(), d.getMonth() - i, 1);
        months.push(past.toISOString().slice(0, 7));
      }
      const [sales, saleItems, salaries, outputs] = await Promise.all([
        sql`SELECT id, total_amount, created_at FROM sales`,
        sql`SELECT sale_id, quantity, cost FROM sale_items`,
        sql`SELECT "netSalary", status, "payDate", remark FROM salaries`,
        sql`SELECT amount, "createTime", period_month FROM staff_outputs`
      ]);
      const costBySale = {};
      for (const it of saleItems) {
        costBySale[it.sale_id] = (costBySale[it.sale_id] || 0) + (parseFloat(it.cost || 0) * parseFloat(it.quantity || 1));
      }
      const snapshots = months.map(ym => {
        const mSales = sales.filter(s => (s.created_at || '').startsWith(ym));
        const rev = mSales.reduce((acc, s) => acc + parseFloat(s.total_amount || 0), 0);
        let cogs = mSales.reduce((acc, s) => acc + (costBySale[s.id] || 0), 0);
        if (cogs === 0 && rev > 0) cogs = rev * 0.55;
        const mSal = salaries.filter(s => String(s.status).toLowerCase() === 'paid' && ((s.payDate || '').startsWith(ym) || (s.remark || '').includes(ym)));
        const sal = mSal.reduce((acc, s) => acc + parseFloat(s.netSalary || 0), 0);
        const mOut = outputs.filter(o => (o.createTime || '').startsWith(ym) || (o.period_month || '') === ym);
        const out = mOut.reduce((acc, o) => acc + parseFloat(o.amount || 0), 0);
        const pay = sal + out;
        const exp = cogs + pay;
        const net = rev - exp;
        return {
          period_month: ym,
          revenue: Math.round(rev * 100) / 100,
          cogs: Math.round(cogs * 100) / 100,
          staff_salaries: Math.round(sal * 100) / 100,
          short_term_outputs: Math.round(out * 100) / 100,
          total_payroll: Math.round(pay * 100) / 100,
          total_expenses: Math.round(exp * 100) / 100,
          net_profit: Math.round(net * 100) / 100,
          profit_margin: rev > 0 ? Math.round((net / rev) * 1000) / 10 : 0
        };
      });
      return res.status(200).json({ code: 0, data: snapshots });
    }

    // POST /api/analysis/compare
    if (path === 'analysis/compare' && (req.method === 'POST' || req.method === 'GET')) {
      const body = req.body || {};
      const query = req.query || {};
      const p1_start = (body.period1_start || query.period1_start || '').trim();
      const p1_end = (body.period1_end || query.period1_end || '').trim();
      const p2_start = (body.period2_start || query.period2_start || '').trim();
      const p2_end = (body.period2_end || query.period2_end || '').trim();
      const p1_month = (body.period1_month || query.period1_month || '').trim();
      const p2_month = (body.period2_month || query.period2_month || '').trim();

      const now = new Date();
      const currYm = now.toISOString().slice(0, 7);
      const prevDate = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const prevYm = prevDate.toISOString().slice(0, 7);

      const m1 = p1_month || (p1_start ? p1_start.slice(0, 7) : currYm);
      const m2 = p2_month || (p2_start ? p2_start.slice(0, 7) : prevYm);

      const [sales, saleItems, salaries, outputs] = await Promise.all([
        sql`SELECT id, total_amount, created_at FROM sales`,
        sql`SELECT sale_id, quantity, cost FROM sale_items`,
        sql`SELECT "netSalary", status, "payDate", remark FROM salaries`,
        sql`SELECT amount, "createTime", period_month FROM staff_outputs`
      ]);
      const costBySale = {};
      for (const it of saleItems) {
        costBySale[it.sale_id] = (costBySale[it.sale_id] || 0) + (parseFloat(it.cost || 0) * parseFloat(it.quantity || 1));
      }
      const calcP = (ym, start, end) => {
        let mSales, mSal, mOut;
        if (start && end) {
          const sDate = start.length === 10 ? `${start} 00:00:00` : start;
          const eDate = end.length === 10 ? `${end} 23:59:59` : end;
          mSales = sales.filter(s => s.created_at && s.created_at >= sDate && s.created_at <= eDate);
          mSal = salaries.filter(s => String(s.status).toLowerCase() === 'paid' && s.payDate && s.payDate >= start.slice(0, 10) && s.payDate <= end.slice(0, 10));
          mOut = outputs.filter(o => o.createTime && o.createTime >= sDate && o.createTime <= eDate);
        } else {
          mSales = sales.filter(s => (s.created_at || '').startsWith(ym));
          mSal = salaries.filter(s => String(s.status).toLowerCase() === 'paid' && ((s.payDate || '').startsWith(ym) || (s.remark || '').includes(ym)));
          mOut = outputs.filter(o => (o.createTime || '').startsWith(ym) || (o.period_month || '') === ym);
        }

        const rev = mSales.reduce((acc, s) => acc + parseFloat(s.total_amount || 0), 0);
        let cogs = mSales.reduce((acc, s) => acc + (costBySale[s.id] || 0), 0);
        if (cogs === 0 && rev > 0) cogs = rev * 0.55;
        const sal = mSal.reduce((acc, s) => acc + parseFloat(s.netSalary || 0), 0);
        const out = mOut.reduce((acc, o) => acc + parseFloat(o.amount || 0), 0);
        const pay = sal + out;
        const exp = cogs + pay;
        const net = rev - exp;
        const margin = rev > 0 ? (net / rev) * 100 : 0;
        return {
          start_date: start || `${ym}-01`,
          end_date: end || `${ym}-31`,
          period_month: ym,
          revenue: Math.round(rev * 100) / 100,
          cogs: Math.round(cogs * 100) / 100,
          staff_salaries: Math.round(sal * 100) / 100,
          staffSalaries: Math.round(sal * 100) / 100,
          short_term_outputs: Math.round(out * 100) / 100,
          shortTermOutputs: Math.round(out * 100) / 100,
          total_payroll: Math.round(pay * 100) / 100,
          totalPayroll: Math.round(pay * 100) / 100,
          total_expenses: Math.round(exp * 100) / 100,
          totalExpenses: Math.round(exp * 100) / 100,
          net_profit: Math.round(net * 100) / 100,
          netProfit: Math.round(net * 100) / 100,
          profit_margin: Math.round(margin * 10) / 10,
          profitMargin: Math.round(margin * 10) / 10,
          margin: Math.round(margin * 10) / 10,
          sales_count: mSales.length,
          salesCount: mSales.length
        };
      };
      const p1Data = calcP(m1, p1_start, p1_end);
      const p2Data = calcP(m2, p2_start, p2_end);

      const calcGrowth = (a, b) => {
        if (b === 0) return a === 0 ? 0 : 100;
        return Math.round(((a - b) / Math.abs(b)) * 1000) / 10;
      };

      const revDiff = Math.round((p1Data.revenue - p2Data.revenue) * 100) / 100;
      const revGrowth = calcGrowth(p1Data.revenue, p2Data.revenue);
      const cogsDiff = Math.round((p1Data.cogs - p2Data.cogs) * 100) / 100;
      const cogsGrowth = calcGrowth(p1Data.cogs, p2Data.cogs);
      const staffDiff = Math.round((p1Data.staff_salaries - p2Data.staff_salaries) * 100) / 100;
      const staffGrowth = calcGrowth(p1Data.staff_salaries, p2Data.staff_salaries);
      const shortDiff = Math.round((p1Data.short_term_outputs - p2Data.short_term_outputs) * 100) / 100;
      const shortGrowth = calcGrowth(p1Data.short_term_outputs, p2Data.short_term_outputs);
      const payrollDiff = Math.round((p1Data.total_payroll - p2Data.total_payroll) * 100) / 100;
      const payrollGrowth = calcGrowth(p1Data.total_payroll, p2Data.total_payroll);
      const profitDiff = Math.round((p1Data.net_profit - p2Data.net_profit) * 100) / 100;
      const profitGrowth = calcGrowth(p1Data.net_profit, p2Data.net_profit);
      const marginDiff = Math.round((p1Data.profit_margin - p2Data.profit_margin) * 10) / 10;

      const deltas = {
        revDiff,
        revGrowth,
        cogsDiff,
        cogsGrowth,
        staffDiff,
        staffGrowth,
        shortDiff,
        shortGrowth,
        payrollDiff,
        payrollGrowth,
        profitDiff,
        profitGrowth,
        marginDiff
      };

      return res.status(200).json({
        code: 0,
        data: {
          period1: p1Data,
          period2: p2Data,
          deltas,
          revenueGrowth: revGrowth,
          profitGrowth: profitGrowth,
          payrollGrowth: payrollGrowth,
          cogsGrowth: cogsGrowth
        }
      });
    }

    // GET /api/analysis/month-summary
    if (path === 'analysis/month-summary') {
      const m = urlSearchParams.get('month') || new Date().toISOString().slice(0, 7);
      const [sales, saleItems, salaries, outputs] = await Promise.all([
        sql`SELECT id, total_amount, created_at FROM sales WHERE created_at LIKE ${m + '%'}`,
        sql`SELECT sale_id, quantity, cost FROM sale_items`,
        sql`SELECT "netSalary", status, "payDate", remark FROM salaries`,
        sql`SELECT amount, "createTime", period_month FROM staff_outputs`
      ]);
      const costBySale = {};
      for (const it of saleItems) {
        costBySale[it.sale_id] = (costBySale[it.sale_id] || 0) + (parseFloat(it.cost || 0) * parseFloat(it.quantity || 1));
      }
      const rev = sales.reduce((acc, s) => acc + parseFloat(s.total_amount || 0), 0);
      let cogs = sales.reduce((acc, s) => acc + (costBySale[s.id] || 0), 0);
      if (cogs === 0 && rev > 0) cogs = rev * 0.55;
      const mSal = salaries.filter(s => String(s.status).toLowerCase() === 'paid' && ((s.payDate || '').startsWith(m) || (s.remark || '').includes(m)));
      const sal = mSal.reduce((acc, s) => acc + parseFloat(s.netSalary || 0), 0);
      const mOut = outputs.filter(o => (o.createTime || '').startsWith(m) || (o.period_month || '') === m);
      const out = mOut.reduce((acc, o) => acc + parseFloat(o.amount || 0), 0);
      const pay = sal + out;
      const exp = cogs + pay;
      const net = rev - exp;
      return res.status(200).json({
        code: 0,
        data: {
          currentMonth: m,
          salesTotal: Math.round(rev * 100) / 100,
          expenseTotal: Math.round(exp * 100) / 100,
          netProfit: Math.round(net * 100) / 100,
          salesCount: sales.length,
          salesGrowth: 5.0,
          avgCheck: sales.length > 0 ? Math.round((rev / sales.length) * 100) / 100 : 0
        }
      });
    }

    // GET /api/menu/list or /api/mock/menu/list
    if (path === 'menu/list' || path === 'mock/menu/list' || path === 'menu/tree') {
      const menuList = [
        {
          id: 1,
          path: '/dashboard',
          name: 'Dashboard',
          title: 'Boshqaruv Paneli (Dashboard)',
          meta: { title: 'Boshqaruv Paneli', icon: 'vi-ant-design:dashboard-filled' },
          children: [
            {
              id: 2,
              parentId: 1,
              path: 'analysis',
              name: 'Analysis',
              title: 'Tahlil va Statistika',
              meta: { title: 'Tahlil va Statistika', permission: ['dashboard:view', 'analysis:export'] },
              permissionList: [
                { id: 1, label: 'Ko‘rish', value: 'dashboard:view' },
                { id: 2, label: 'Eksport (Excel)', value: 'analysis:export' }
              ]
            },
            {
              id: 3,
              parentId: 1,
              path: 'workplace',
              name: 'Workplace',
              title: 'Ish Joyi (Workplace)',
              meta: { title: 'Ish Joyi', permission: ['workplace:view'] },
              permissionList: [
                { id: 1, label: 'Ko‘rish', value: 'workplace:view' }
              ]
            }
          ]
        },
        {
          id: 4,
          path: '/product',
          name: 'ProductRoot',
          title: 'Omborxona (Mahsulotlar)',
          meta: { title: 'Omborxona', icon: 'vi-ep:goods' },
          children: [
            {
              id: 5,
              parentId: 4,
              path: 'list',
              name: 'ProductManagement',
              title: 'Ombor Mahsulotlari',
              meta: { title: 'Ombor Mahsulotlari', permission: ['product:view', 'product:create', 'product:edit', 'product:delete', 'product:export'] },
              permissionList: [
                { id: 1, label: 'Ko‘rish', value: 'product:view' },
                { id: 2, label: 'Qo‘shish', value: 'product:create' },
                { id: 3, label: 'Tahrirlash', value: 'product:edit' },
                { id: 4, label: 'O‘chirish', value: 'product:delete' },
                { id: 5, label: 'Eksport', value: 'product:export' }
              ]
            }
          ]
        },
        {
          id: 6,
          path: '/sales',
          name: 'SalesRoot',
          title: 'Sotuvlar & POS Kassa',
          meta: { title: 'Sotuvlar (POS)', icon: 'vi-ep:shopping-cart-full' },
          children: [
            {
              id: 7,
              parentId: 6,
              path: 'pos',
              name: 'SalesPos',
              title: 'Sotuvlar (POS)',
              meta: { title: 'Sotuvlar (POS)', permission: ['pos:view', 'pos:sell', 'pos:nasiya', 'pos:discount', 'pos:receipt'] },
              permissionList: [
                { id: 1, label: 'Ko‘rish', value: 'pos:view' },
                { id: 2, label: 'Sotuv amalga oshirish', value: 'pos:sell' },
                { id: 3, label: 'Nasiyaga sotish', value: 'pos:nasiya' },
                { id: 4, label: 'Chegirma berish', value: 'pos:discount' },
                { id: 5, label: 'Chek chop etish', value: 'pos:receipt' }
              ]
            },
            {
              id: 8,
              parentId: 6,
              path: 'debtors',
              name: 'SalesDebtors',
              title: 'Nasiyalar (Qarzlar)',
              meta: { title: 'Nasiyalar (Qarzlar)', permission: ['debtors:view', 'debtors:repay', 'debtors:history', 'debtors:export'] },
              permissionList: [
                { id: 1, label: 'Ko‘rish', value: 'debtors:view' },
                { id: 2, label: 'Qarzni qaytarish', value: 'debtors:repay' },
                { id: 3, label: 'Tarixni ko‘rish', value: 'debtors:history' },
                { id: 4, label: 'Eksport', value: 'debtors:export' }
              ]
            }
          ]
        },
        {
          id: 9,
          path: '/hr',
          name: 'HRRoot',
          title: 'Xodimlar (HR)',
          meta: { title: 'Xodimlar (HR)', icon: 'vi-ep:avatar' },
          children: [
            {
              id: 10,
              parentId: 9,
              path: 'workers',
              name: 'WorkerManagement',
              title: 'Xodimlar Ro‘yxati',
              meta: { title: 'Xodimlar Ro‘yxati', permission: ['workers:view', 'workers:create', 'workers:edit', 'workers:delete'] },
              permissionList: [
                { id: 1, label: 'Ko‘rish', value: 'workers:view' },
                { id: 2, label: 'Qo‘shish', value: 'workers:create' },
                { id: 3, label: 'Tahrirlash', value: 'workers:edit' },
                { id: 4, label: 'O‘chirish', value: 'workers:delete' }
              ]
            },
            {
              id: 11,
              parentId: 9,
              path: 'timesheets',
              name: 'TimesheetManagement',
              title: 'Davomat (Ish Vaqti)',
              meta: { title: 'Davomat', permission: ['timesheet:view', 'timesheet:edit'] },
              permissionList: [
                { id: 1, label: 'Ko‘rish', value: 'timesheet:view' },
                { id: 2, label: 'Belgilash', value: 'timesheet:edit' }
              ]
            },
            {
              id: 12,
              parentId: 9,
              path: 'outputs',
              name: 'OutputManagement',
              title: 'Kunlik Ishbay Ishlab Chiqarish',
              meta: { title: 'Ishbay Chiqarish', permission: ['output:view', 'output:create', 'output:delete'] },
              permissionList: [
                { id: 1, label: 'Ko‘rish', value: 'output:view' },
                { id: 2, label: 'Qo‘shish', value: 'output:create' },
                { id: 3, label: 'O‘chirish', value: 'output:delete' }
              ]
            },
            {
              id: 13,
              parentId: 9,
              path: 'adjustments',
              name: 'AdjustmentManagement',
              title: 'Mukofot va Jarimalar',
              meta: { title: 'Korrektirovkalar', permission: ['adjustments:view', 'adjustments:create', 'adjustments:delete'] },
              permissionList: [
                { id: 1, label: 'Ko‘rish', value: 'adjustments:view' },
                { id: 2, label: 'Qo‘shish', value: 'adjustments:create' },
                { id: 3, label: 'O‘chirish', value: 'adjustments:delete' }
              ]
            },
            {
              id: 14,
              parentId: 9,
              path: 'salary',
              name: 'SalaryManagement',
              title: 'Oylik Maoshlar',
              meta: { title: 'Oylik Maoshlar', permission: ['salary:view', 'salary:create', 'salary:payout'] },
              permissionList: [
                { id: 1, label: 'Ko‘rish', value: 'salary:view' },
                { id: 2, label: 'Hisoblash', value: 'salary:create' },
                { id: 3, label: 'To‘lash', value: 'salary:payout' }
              ]
            }
          ]
        },
        {
          id: 15,
          path: '/cutting',
          name: 'CuttingRoot',
          title: 'Ishlab Chiqarish & Raskroy',
          meta: { title: 'Raskroy', icon: 'vi-ep:scissors' },
          children: [
            {
              id: 16,
              parentId: 15,
              path: 'order',
              name: 'CuttingOrder',
              title: 'Raskroy Buyurtmalari',
              meta: { title: 'Buyurtmalar', permission: ['cutting:view', 'cutting:create', 'cutting:delete'] },
              permissionList: [
                { id: 1, label: 'Ko‘rish', value: 'cutting:view' },
                { id: 2, label: 'Yaratish', value: 'cutting:create' },
                { id: 3, label: 'O‘chirish', value: 'cutting:delete' }
              ]
            },
            {
              id: 17,
              parentId: 15,
              path: 'task',
              name: 'CuttingTask',
              title: 'Ishlab Chiqarish Vazifalari',
              meta: { title: 'Vazifalar', permission: ['cutting_task:view', 'cutting_task:update'] },
              permissionList: [
                { id: 1, label: 'Ko‘rish', value: 'cutting_task:view' },
                { id: 2, label: 'Statusni yangilash', value: 'cutting_task:update' }
              ]
            }
          ]
        },
        {
          id: 18,
          path: '/qr_codes',
          name: 'QRCodesRoot',
          title: 'QR Kodlar',
          meta: { title: 'QR Kodlar', icon: 'vi-ep:camera' },
          children: [
            {
              id: 19,
              parentId: 18,
              path: 'print',
              name: 'QRPrint',
              title: 'QR Kod Chop Etish',
              meta: { title: 'Chop Etish', permission: ['qr:view', 'qr:print'] },
              permissionList: [
                { id: 1, label: 'Ko‘rish', value: 'qr:view' },
                { id: 2, label: 'Chop etish', value: 'qr:print' }
              ]
            }
          ]
        },
        {
          id: 20,
          path: '/authorization',
          name: 'AuthorizationRoot',
          title: 'Huquqlar & Sozlamalar',
          meta: { title: 'Huquqlar & Sozlamalar', icon: 'vi-eos-icons:role-binding' },
          children: [
            {
              id: 21,
              parentId: 20,
              path: 'department',
              name: 'Department',
              title: 'Bo‘limlar',
              meta: { title: 'Bo‘limlar', permission: ['department:view', 'department:create', 'department:edit', 'department:delete'] },
              permissionList: [
                { id: 1, label: 'Ko‘rish', value: 'department:view' },
                { id: 2, label: 'Qo‘shish', value: 'department:create' },
                { id: 3, label: 'Tahrirlash', value: 'department:edit' },
                { id: 4, label: 'O‘chirish', value: 'department:delete' }
              ]
            },
            {
              id: 22,
              parentId: 20,
              path: 'role',
              name: 'Role',
              title: 'Rollar & Huquqlar',
              meta: { title: 'Rollar', permission: ['role:view', 'role:create', 'role:edit', 'role:delete'] },
              permissionList: [
                { id: 1, label: 'Ko‘rish', value: 'role:view' },
                { id: 2, label: 'Qo‘shish', value: 'role:create' },
                { id: 3, label: 'Tahrirlash', value: 'role:edit' },
                { id: 4, label: 'O‘chirish', value: 'role:delete' }
              ]
            }
          ]
        }
      ];

      return res.status(200).json({
        code: 0,
        data: {
          list: menuList,
          total: menuList.length
        }
      });
    }

    // GET /api/sales/payment-receipt/:no
    if (path.startsWith('sales/payment-receipt/')) {
      const receiptNo = path.replace('sales/payment-receipt/', '');
      const payRows = await sql`SELECT * FROM debt_payments WHERE receipt_number = ${receiptNo} OR id = ${receiptNo}`;
      return res.status(200).json({
        code: 0,
        data: payRows[0] || null
      });
    }

    // 14. GET /api/device/list
    if (path === 'device/list') {
      const rows = await sql`SELECT * FROM device_tokens ORDER BY id DESC`;
      return res.status(200).json({ code: 0, data: { total: rows.length, list: rows } });
    }

    // 15. GET /api/activity/list
    if (path === 'activity/list') {
      const pageIndex = parseInt(req.query?.pageIndex || urlSearchParams.get('pageIndex') || 1, 10);
      const pageSize = parseInt(req.query?.pageSize || urlSearchParams.get('pageSize') || 20, 10);
      const offset = (pageIndex - 1) * pageSize;
      const [countRes, rows] = await Promise.all([
        sql`SELECT count(*) FROM activity_logs`,
        sql`SELECT * FROM activity_logs ORDER BY id DESC LIMIT ${pageSize} OFFSET ${offset}`
      ]);
      return res.status(200).json({
        code: 0,
        data: {
          total: parseInt(countRes[0].count, 10),
          list: rows
        }
      });
    }

    // 16. Staff HR Endpoints
    if (path === 'hr/position/list') {
      const rows = await sql`SELECT * FROM positions ORDER BY id ASC`;
      return res.status(200).json({ code: 0, data: { total: rows.length, list: rows } });
    }

    if (path === 'hr/position/save' && req.method === 'POST') {
      const { id, name, department_id, base_salary, status, description } = req.body || {};
      if (id) {
        await sql`
          UPDATE positions 
          SET name = ${name}, department_id = ${department_id || null}, base_salary = ${parseFloat(base_salary) || 0}, status = ${status !== undefined ? status : 1}, description = ${description || null}
          WHERE id = ${id}
        `;
      } else {
        const newId = 'pos_' + Date.now().toString(36);
        await sql`
          INSERT INTO positions (id, name, department_id, base_salary, status, description, "createTime")
          VALUES (${newId}, ${name}, ${department_id || null}, ${parseFloat(base_salary) || 0}, ${status !== undefined ? status : 1}, ${description || null}, NOW())
        `;
      }
      return res.status(200).json({ code: 0, message: 'Saqlandi' });
    }

    if (path === 'hr/position/delete' && req.method === 'POST') {
      const { ids } = req.body || {};
      if (Array.isArray(ids) && ids.length > 0) {
        await sql`DELETE FROM positions WHERE id = ANY(${ids})`;
      }
      return res.status(200).json({ code: 0, message: "O'chirildi" });
    }

    if (path === 'hr/timesheet/list') {
      const rows = await sql`SELECT * FROM staff_timesheets ORDER BY id DESC`;
      return res.status(200).json({ code: 0, data: { total: rows.length, list: rows } });
    }

    if (path === 'hr/timesheet/save' && req.method === 'POST') {
      const { id, date, status, records } = req.body || {};
      const recordsJson = typeof records === 'string' ? records : JSON.stringify(records || []);
      if (id) {
        await sql`
          UPDATE staff_timesheets 
          SET date = ${date}, status = ${status || 'active'}, records = ${recordsJson}::jsonb
          WHERE id = ${id}
        `;
      } else {
        const newId = 'TS' + Math.floor(100000 + Math.random() * 900000);
        await sql`
          INSERT INTO staff_timesheets (id, date, status, records, "createTime")
          VALUES (${newId}, ${date}, ${status || 'active'}, ${recordsJson}::jsonb, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
        `;
      }
      return res.status(200).json({ code: 0, message: 'Saqlandi' });
    }

    if (path === 'hr/timesheet/delete' && req.method === 'POST') {
      const { ids } = req.body || {};
      if (Array.isArray(ids) && ids.length > 0) {
        await sql`DELETE FROM staff_timesheets WHERE id = ANY(${ids})`;
      }
      return res.status(200).json({ code: 0, message: "O'chirildi" });
    }

    if (path === 'hr/output/list') {
      const rows = await sql`
        SELECT o.*, COALESCE(o."workerName", w.name, o."workerId") as "workerName" 
        FROM staff_outputs o 
        LEFT JOIN workers w ON o."workerId" = w.id OR o."workerId" = w.employee_code
        ORDER BY o.id DESC
      `;
      return res.status(200).json({ code: 0, data: { total: rows.length, list: rows } });
    }

    if (path === 'hr/output/save' && req.method === 'POST') {
      const { id, workerId, workerName, name, amount, period_month, comment } = req.body || {};
      if (id) {
        await sql`
          UPDATE staff_outputs 
          SET "workerId" = ${workerId}, "workerName" = ${workerName}, name = ${name}, amount = ${parseFloat(amount) || 0}, period_month = ${period_month}, comment = ${comment}
          WHERE id = ${id}
        `;
      } else {
        const newId = 'OUT' + Math.floor(100000 + Math.random() * 900000);
        await sql`
          INSERT INTO staff_outputs (id, "workerId", "workerName", name, amount, period_month, comment, "createTime")
          VALUES (${newId}, ${workerId}, ${workerName}, ${name}, ${parseFloat(amount) || 0}, ${period_month}, ${comment}, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
        `;
      }
      return res.status(200).json({ code: 0, message: 'Saqlandi' });
    }

    if (path === 'hr/output/delete' && req.method === 'POST') {
      const { ids } = req.body || {};
      if (Array.isArray(ids) && ids.length > 0) {
        await sql`DELETE FROM staff_outputs WHERE id = ANY(${ids})`;
      }
      return res.status(200).json({ code: 0, message: "O'chirildi" });
    }

    if (path === 'hr/adjustment/list') {
      const rows = await sql`
        SELECT a.*, COALESCE(w.name, a."workerId") as "workerName" 
        FROM staff_adjustments a 
        LEFT JOIN workers w ON a."workerId" = w.id OR a."workerId" = w.employee_code
        ORDER BY a.id DESC
      `;
      return res.status(200).json({ code: 0, data: { total: rows.length, list: rows } });
    }

    if (path === 'hr/adjustment/save' && req.method === 'POST') {
      const { id, workerId, document_type, amount, period_month, description } = req.body || {};
      if (id) {
        await sql`
          UPDATE staff_adjustments 
          SET "workerId" = ${workerId}, document_type = ${document_type}, amount = ${parseFloat(amount) || 0}, period_month = ${period_month}, description = ${description}
          WHERE id = ${id}
        `;
      } else {
        const newId = 'ADJ' + Math.floor(100000 + Math.random() * 900000);
        await sql`
          INSERT INTO staff_adjustments (id, "workerId", document_type, amount, period_month, description, "createTime")
          VALUES (${newId}, ${workerId}, ${document_type}, ${parseFloat(amount) || 0}, ${period_month}, ${description}, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
        `;
      }
      return res.status(200).json({ code: 0, message: 'Saqlandi' });
    }

    if (path === 'hr/adjustment/delete' && req.method === 'POST') {
      const { ids } = req.body || {};
      if (Array.isArray(ids) && ids.length > 0) {
        await sql`DELETE FROM staff_adjustments WHERE id = ANY(${ids})`;
      }
      return res.status(200).json({ code: 0, message: "O'chirildi" });
    }

    // 17. GET /api/analysis/snapshot/list
    if (path === 'analysis/snapshot/list') {
      const rows = await sql`SELECT * FROM monthly_financial_snapshots ORDER BY period_month DESC`;
      return res.status(200).json({ code: 0, data: rows });
    }

    if (path === 'analysis/snapshot/close' && req.method === 'POST') {
      const { period_month, remark } = req.body || {};
      const period = period_month || new Date().toISOString().slice(0, 7);
      const salesRows = await sql`SELECT * FROM sales WHERE "createTime" LIKE ${period + '%'}`;
      const revenue = salesRows.reduce((acc, s) => acc + (parseFloat(s.total || s.total_amount || 0)), 0);
      const salesCount = salesRows.length;
      const salaryRows = await sql`SELECT * FROM salaries WHERE "payDate" LIKE ${period + '%'}`;
      const salaries = salaryRows.reduce((acc, s) => acc + (parseFloat(s.netSalary || s.baseSalary || 0)), 0);
      const cogs = Math.round(revenue * 0.65);
      const netProfit = Math.round(revenue - cogs - salaries);
      const profitMargin = revenue > 0 ? Math.round((netProfit / revenue) * 100) : 0;

      await sql`
        INSERT INTO monthly_financial_snapshots (
          period_month, revenue, cogs, staff_salaries, total_expenses, net_profit, profit_margin, sales_count, closed_by, closed_at, remark
        )
        VALUES (
          ${period}, ${revenue}, ${cogs}, ${salaries}, ${cogs + salaries}, ${netProfit}, ${profitMargin}, ${salesCount}, ${authUser?.sub || 'admin'}, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'), ${remark || 'Oylik moliyaviy hisobot yopildi'}
        )
        ON CONFLICT (period_month) DO UPDATE SET
          revenue = EXCLUDED.revenue,
          cogs = EXCLUDED.cogs,
          staff_salaries = EXCLUDED.staff_salaries,
          total_expenses = EXCLUDED.total_expenses,
          net_profit = EXCLUDED.net_profit,
          profit_margin = EXCLUDED.profit_margin,
          sales_count = EXCLUDED.sales_count,
          closed_by = EXCLUDED.closed_by,
          closed_at = EXCLUDED.closed_at,
          remark = EXCLUDED.remark
      `;

      return res.status(200).json({ code: 0, message: `${period} oylik hisoboti muvaffaqiyatli yopildi` });
    }

    if (path === 'analysis/snapshot/delete' && req.method === 'POST') {
      const { id, period_month } = req.body || {};
      if (id) {
        await sql`DELETE FROM monthly_financial_snapshots WHERE id = ${id}`;
      } else if (period_month) {
        await sql`DELETE FROM monthly_financial_snapshots WHERE period_month = ${period_month}`;
      }
      return res.status(200).json({ code: 0, message: 'Hisobot o\'chirildi' });
    }

    // 18. Branch Endpoints
    if (path === 'branch/list') {
      const rows = await sql`SELECT * FROM branches ORDER BY id ASC`;
      return res.status(200).json({ code: 0, data: rows, list: rows, total: rows.length });
    }

    if (path === 'branch/save' && req.method === 'POST') {
      const { id, name, code, address, phone, is_active, status, remark } = req.body || {};
      const branchStatus = status !== undefined ? parseInt(status, 10) : (is_active !== undefined ? parseInt(is_active, 10) : 1);
      if (id) {
        const updated = await sql`
          UPDATE branches 
          SET name = ${name}, status = ${branchStatus}, remark = ${remark || address || null}
          WHERE id = ${id}
          RETURNING *
        `;
        return res.status(200).json({ code: 0, message: 'Filial yangilandi', data: updated[0] || req.body });
      } else {
        const newId = 'BR-' + Math.floor(10 + Math.random() * 90);
        const inserted = await sql`
          INSERT INTO branches (id, name, status, remark, "createTime")
          VALUES (${newId}, ${name}, ${branchStatus}, ${remark || address || null}, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
          RETURNING *
        `;
        return res.status(200).json({ code: 0, message: 'Yangi filial yaratildi', data: inserted[0] });
      }
    }

    if (path === 'branch/delete' && req.method === 'POST') {
      let ids = req.body?.ids;
      if (!ids && req.body?.id) ids = [req.body.id];
      if (Array.isArray(ids) && ids.length > 0) {
        await sql`DELETE FROM branches WHERE id = ANY(${ids})`;
        return res.status(200).json({ code: 0, message: 'Filial o\'chirildi' });
      }
      return res.status(200).json({ code: 400, message: 'ID ko\'rsatilmadi' });
    }

    // 19. GET /api/classifier/list
    if (path === 'classifier/list') {
      const search = (req.query?.search || urlSearchParams.get('search') || req.query?.q || urlSearchParams.get('q') || '').trim();
      const page = parseInt(req.query?.page || urlSearchParams.get('page') || req.query?.pageIndex || urlSearchParams.get('pageIndex') || 1, 10);
      const pageSize = parseInt(req.query?.page_size || urlSearchParams.get('page_size') || req.query?.pageSize || urlSearchParams.get('pageSize') || 20, 10);
      const mode = (req.query?.mode || urlSearchParams.get('mode') || 'extended').trim().toLowerCase();
      const lang = (req.query?.lang || urlSearchParams.get('lang') || 'uz_latn').trim();
      const offset = (page - 1) * pageSize;

      let list = [];
      let total = 0;

      // 1. If searching and mode is extended (default), query Tasnif Soliq's Elasticsearch API
      // ("Matn bo'yicha kengaytirilgan qidiruv" across all 440,000+ national classifier items)
      if (search && mode !== 'local' && mode !== 'simple') {
        try {
          const pZero = Math.max(0, page - 1);
          const targetUrl = `https://tasnif.soliq.uz/api/cls-api/elasticsearch/search?lang=${encodeURIComponent(lang)}&search=${encodeURIComponent(search)}&size=${pageSize}&page=${pZero}`;
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 12000);

          const esResp = await fetch(targetUrl, {
            signal: controller.signal,
            headers: {
              'Accept': 'application/json',
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            }
          });
          clearTimeout(timeoutId);

          if (esResp.ok) {
            const esJson = await esResp.json();
            if (esJson && Array.isArray(esJson.data) && esJson.data.length > 0) {
              list = esJson.data.map((item, idx) => ({
                id: item.mxikCode || (item.internationalCode ? `bar_${item.internationalCode}` : `ext_${page}_${idx}`),
                mxik_code: item.mxikCode || '',
                mxik_name: item.name || '',
                brand_name: item.brandName || '',
                attribute_name: item.attributeName || '',
                shtrix_code: item.internationalCode || '',
                unit: item.unitsName || 'dona',
                group_name: item.groupName || '',
                group_code: item.groupCode || '',
                class_name: item.className || '',
                position_name: item.positionName || '',
                subposition_name: item.subPositionName || '',
                category_name: item.categoryName || '',
                search_mode: 'extended'
              }));
              total = esJson.recordTotal || list.length;
            }
          }
        } catch (esErr) {
          console.warn('Tasnif Soliq Elasticsearch extended search failed, falling back to local:', esErr.message);
        }
      }

      // 1b. If mode is explicitly simple ("Matn bo'yicha qidirish"), try Tasnif Soliq's by-params endpoint
      if (search && mode === 'simple' && list.length === 0) {
        try {
          const pZero = Math.max(0, page - 1);
          const targetUrl = `https://tasnif.soliq.uz/api/cls-api/mxik/search/by-params?text=${encodeURIComponent(search)}&size=${pageSize}&page=${pZero}`;
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 12000);

          const paramsResp = await fetch(targetUrl, { signal: controller.signal });
          clearTimeout(timeoutId);

          if (paramsResp.ok) {
            const pJson = await paramsResp.json();
            const content = pJson?.data?.content;
            if (Array.isArray(content) && content.length > 0) {
              list = content.map((item, idx) => ({
                id: item.mxikCode || `simple_${page}_${idx}`,
                mxik_code: item.mxikCode || '',
                mxik_name: item.subPositionName || item.positionName || item.className || item.groupName || search,
                brand_name: item.brandName || '',
                attribute_name: item.attributeName || '',
                shtrix_code: item.internationalCode || '',
                unit: 'dona',
                group_name: item.groupName || '',
                class_name: item.className || '',
                position_name: item.positionName || '',
                subposition_name: item.subPositionName || '',
                search_mode: 'simple'
              }));
              total = pJson?.data?.totalElements || list.length;
            }
          }
        } catch (pErr) {
          console.warn('Tasnif Soliq by-params search failed:', pErr.message);
        }
      }

      // 2. Local Database Search (Neon PostgreSQL) fallback or when no search query
      if (list.length === 0) {
        try {
          if (search) {
            const sLower = search.toLowerCase();
            const sParam = `%${sLower}%`;
            const [countRes, rows] = await Promise.all([
              sql`SELECT count(*) FROM classifier_items 
                  WHERE LOWER(mxik_name) LIKE ${sParam} 
                     OR LOWER(brand_name) LIKE ${sParam} 
                     OR LOWER(attribute_name) LIKE ${sParam} 
                     OR LOWER(group_name) LIKE ${sParam} 
                     OR shtrix_code LIKE ${sParam} 
                     OR mxik_code LIKE ${sParam}`,
              sql`SELECT * FROM classifier_items 
                  WHERE LOWER(mxik_name) LIKE ${sParam} 
                     OR LOWER(brand_name) LIKE ${sParam} 
                     OR LOWER(attribute_name) LIKE ${sParam} 
                     OR LOWER(group_name) LIKE ${sParam} 
                     OR shtrix_code LIKE ${sParam} 
                     OR mxik_code LIKE ${sParam} 
                  ORDER BY id ASC LIMIT ${pageSize} OFFSET ${offset}`
            ]);
            total = parseInt(countRes[0]?.count || 0, 10);
            list = rows;
          } else {
            const [countRes, rows] = await Promise.all([
              sql`SELECT count(*) FROM classifier_items`,
              sql`SELECT * FROM classifier_items ORDER BY id ASC LIMIT ${pageSize} OFFSET ${offset}`
            ]);
            total = parseInt(countRes[0]?.count || 0, 10);
            list = rows;
          }
        } catch (dbErr) {
          console.error('Database classifier query error:', dbErr);
        }
      }

      // 3. Fallback to bundled classifier seed JSON
      if (list.length === 0 && total === 0) {
        const seedItems = getClassifierSeedData();
        if (seedItems && seedItems.length > 0) {
          let filtered = seedItems;
          if (search) {
            const sLower = search.toLowerCase();
            const tokens = sLower.split(/\s+/).filter(Boolean);
            filtered = filtered.filter(item => {
              const fullText = `${item.mxik_name || ''} ${item.brand_name || ''} ${item.attribute_name || ''} ${item.group_name || ''} ${item.shtrix_code || ''} ${item.mxik_code || ''}`.toLowerCase();
              return tokens.every(tok => fullText.includes(tok)) || (item.shtrix_code && item.shtrix_code.includes(sLower));
            });
          }
          total = filtered.length;
          list = filtered.slice(offset, offset + pageSize);
        }
      }

      return res.status(200).json({
        code: 0,
        data: {
          total,
          list
        },
        list,
        total
      });
    }

    // 19b. GET /api/classifier/by-barcode/:barcode
    if (path.startsWith('classifier/by-barcode/')) {
      const barcode = path.replace('classifier/by-barcode/', '').trim();
      let item = null;
      try {
        const rows = await sql`SELECT * FROM classifier_items WHERE shtrix_code = ${barcode} LIMIT 1`;
        if (rows && rows.length > 0) item = rows[0];
      } catch (e) {}

      // If not in local DB, query live Tasnif Soliq Elasticsearch
      if (!item && barcode) {
        try {
          const targetUrl = `https://tasnif.soliq.uz/api/cls-api/elasticsearch/search?lang=uz_latn&search=${encodeURIComponent(barcode)}&size=5&page=0`;
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 12000);
          const esResp = await fetch(targetUrl, { signal: controller.signal });
          clearTimeout(timeoutId);
          if (esResp.ok) {
            const esJson = await esResp.json();
            if (esJson && Array.isArray(esJson.data) && esJson.data.length > 0) {
              const exact = esJson.data.find(d => d.internationalCode === barcode) || esJson.data[0];
              item = {
                id: exact.mxikCode || (exact.internationalCode ? `bar_${exact.internationalCode}` : barcode),
                mxik_code: exact.mxikCode || '',
                mxik_name: exact.name || '',
                brand_name: exact.brandName || '',
                attribute_name: exact.attributeName || '',
                shtrix_code: exact.internationalCode || barcode,
                unit: exact.unitsName || 'dona',
                group_name: exact.groupName || '',
                class_name: exact.className || '',
                position_name: exact.positionName || '',
                subposition_name: exact.subPositionName || '',
                source: 'tasnif_elasticsearch'
              };
            }
          }
        } catch (esErr) {
          console.warn('Barcode lookup via Tasnif Elasticsearch failed:', esErr.message);
        }
      }

      if (!item) {
        const seedItems = getClassifierSeedData();
        item = seedItems.find(i => i.shtrix_code === barcode) || null;
      }
      return res.status(200).json({ code: 0, data: item });
    }

    if (path === 'classifier/sync' && req.method === 'POST') {
      const seedItems = getClassifierSeedData();
      let inserted = 0;
      if (seedItems && seedItems.length > 0) {
        // Insert in small batches of 100
        const batchSize = 100;
        const toInsert = seedItems.slice(0, 1000);
        for (let i = 0; i < toInsert.length; i += batchSize) {
          const chunk = toInsert.slice(i, i + batchSize);
          for (const item of chunk) {
            await sql`
              INSERT INTO classifier_items (id, group_name, class_name, position_name, subposition_name, brand_name, attribute_name, mxik_code, mxik_name, shtrix_code, unit)
              VALUES (${item.id}, ${item.group_name}, ${item.class_name}, ${item.position_name}, ${item.subposition_name}, ${item.brand_name}, ${item.attribute_name}, ${item.mxik_code}, ${item.mxik_name}, ${item.shtrix_code}, ${item.unit})
              ON CONFLICT (id) DO NOTHING
            `;
            inserted++;
          }
        }
      }
      return res.status(200).json({ code: 0, message: `${inserted} ta klassifikator elementi sinxronlashtirildi` });
    }

    // 20. GET /api/analysis/financial-overview
    if (path === 'analysis/financial-overview') {
      const [salesRows, products, workers, salariesPaid] = await Promise.all([
        sql`SELECT sum(total) as sales_total FROM sales`,
        sql`SELECT * FROM products`,
        sql`SELECT * FROM workers WHERE status = 1`,
        sql`SELECT sum(netSalary) as salaries_paid FROM salaries WHERE status = 'paid'`
      ]);

      const salesTotal = parseFloat(salesRows[0]?.sales_total || 0);
      const totalInventoryRetail = products.reduce((acc, p) => acc + (parseFloat(p.price || 0) * (parseInt(p.quantityInStock || 0, 10))), 0);
      const totalInventoryCost = products.reduce((acc, p) => acc + (parseFloat(p.cost || 0) * (parseInt(p.quantityInStock || 0, 10))), 0);
      const costRatio = totalInventoryRetail > 0 ? (totalInventoryCost / totalInventoryRetail) : 0.65;

      const grossRevenue = salesTotal > 0 ? salesTotal : totalInventoryRetail;
      const cogs = salesTotal > 0 ? (grossRevenue * costRatio) : totalInventoryCost;

      let staffSalaries = parseFloat(salariesPaid[0]?.salaries_paid || 0);
      if (staffSalaries === 0) {
        staffSalaries = workers.reduce((acc, w) => acc + parseFloat(w.baseSalary || 0), 0);
      }

      const totalExpenses = cogs + staffSalaries;
      const realNetProfit = grossRevenue - totalExpenses;
      const profitMargin = grossRevenue > 0 ? ((realNetProfit / grossRevenue) * 100) : 0;

      return res.status(200).json({
        code: 0,
        data: {
          grossRevenue: Math.round(grossRevenue * 100) / 100,
          cogs: Math.round(cogs * 100) / 100,
          staffSalaries: Math.round(staffSalaries * 100) / 100,
          shortTermOutputs: 0,
          totalPayroll: Math.round(staffSalaries * 100) / 100,
          totalExpenses: Math.round(totalExpenses * 100) / 100,
          realNetProfit: Math.round(realNetProfit * 100) / 100,
          profitMargin: Math.round(profitMargin * 10) / 10,
          activeWorkersCount: workers.length,
          shortTermTasksCount: 0,
          monthlyFinancials: [],
          expenseBreakdown: [
            { name: "Mahsulot Tannarxi (COGS)", value: Math.round(cogs * 100) / 100 },
            { name: "Doimiy Xodimlar Maoshi", value: Math.round(staffSalaries * 100) / 100 }
          ]
        }
      });
    }

    // 21. GET /api/analysis/total
    if (path === 'analysis/total') {
      const [pRes, wRes] = await Promise.all([
        sql`SELECT count(*) as count, sum(price * quantityInStock) as total_price FROM products`,
        sql`SELECT count(*) as count, sum(baseSalary) as total_salary FROM workers WHERE status = 1`
      ]);

      return res.status(200).json({
        code: 0,
        data: {
          users: parseInt(pRes[0]?.count || 0, 10),
          messages: parseInt(wRes[0]?.count || 0, 10),
          moneys: parseFloat(pRes[0]?.total_price || 0),
          shoppings: parseFloat(wRes[0]?.total_salary || 0)
        }
      });
    }

    // Analysis charts
    if (path === 'analysis/monthlySales') {
      const months = [
        'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december'
      ];
      const curYear = new Date().getFullYear();
      const salesRows = await sql`SELECT "createTime", total, total_amount FROM sales WHERE "createTime" LIKE ${curYear + '%'}`;
      const monthTotals = {};
      salesRows.forEach(s => {
        const m = parseInt((s.createTime || '').slice(5, 7), 10);
        if (m >= 1 && m <= 12) {
          monthTotals[m] = (monthTotals[m] || 0) + parseFloat(s.total || s.total_amount || 0);
        }
      });

      const data = months.map((mName, idx) => {
        const mNum = idx + 1;
        const actual = Math.round(monthTotals[mNum] || (80 + Math.sin(idx) * 40));
        const estimate = Math.round(actual * 1.15 + 10);
        return {
          estimate,
          actual,
          name: `analysis.${mName}`
        };
      });
      return res.status(200).json({ code: 0, data });
    }

    if (path === 'analysis/userAccessSource') {
      return res.status(200).json({
        code: 0,
        data: [
          { value: 1000, name: 'analysis.directAccess' },
          { value: 310, name: 'analysis.mailMarketing' },
          { value: 234, name: 'analysis.allianceAdvertising' },
          { value: 135, name: 'analysis.videoAdvertising' },
          { value: 1548, name: 'analysis.searchEngines' }
        ]
      });
    }

    if (path === 'analysis/weeklyUserActivity') {
      return res.status(200).json({
        code: 0,
        data: [
          { value: 13253, name: 'analysis.monday' },
          { value: 34235, name: 'analysis.tuesday' },
          { value: 26321, name: 'analysis.wednesday' },
          { value: 12340, name: 'analysis.thursday' },
          { value: 24643, name: 'analysis.friday' },
          { value: 1322, name: 'analysis.saturday' },
          { value: 1324, name: 'analysis.sunday' }
        ]
      });
    }

    // Dictionaries
    if (path === 'dict/list') {
      return res.status(200).json({
        code: 0,
        data: {
          importance: [
            { value: 0, label: 'Oddiy' },
            { value: 1, label: 'Yaxshi' },
            { value: 2, label: 'Muhim' }
          ]
        }
      });
    }

    if (path === 'dict/one') {
      return res.status(200).json({
        code: 0,
        data: [
          { label: 'test1', value: 0 },
          { label: 'test2', value: 1 },
          { label: 'test3', value: 2 }
        ]
      });
    }

    // Device Management & Pairing
    if (path === 'device/pair-token' && req.method === 'POST') {
      const { device_name, user_id } = req.body || {};
      const token = 'dt_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
      const pair_code = Math.floor(100000 + Math.random() * 900000).toString();
      const uid = user_id || authUser?.id || 1;
      const inserted = await sql`
        INSERT INTO device_tokens (user_id, device_name, token, pair_code, status, created_at, expires_at)
        VALUES (${uid}, ${device_name || 'Mobile Scanner'}, ${token}, ${pair_code}, 'active', to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'), to_char(NOW() + interval '30 days', 'YYYY-MM-DD HH24:MI:SS'))
        RETURNING *
      `;
      return res.status(200).json({ code: 0, data: inserted[0] });
    }

    if (path === 'device/verify') {
      const token = req.headers['x-device-token'] || req.query?.token;
      if (!token) return res.status(401).json({ code: 401, message: 'Qurilma tokeni mavjud emas' });
      const rows = await sql`SELECT * FROM device_tokens WHERE token = ${token} AND status = 'active' LIMIT 1`;
      if (rows[0]) {
        await sql`UPDATE device_tokens SET last_used_at = to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS') WHERE id = ${rows[0].id}`;
        return res.status(200).json({ code: 0, data: rows[0], valid: true });
      }
      return res.status(401).json({ code: 401, message: 'Qurilma tokeni yaroqsiz', valid: false });
    }

    if (path.startsWith('device/revoke/')) {
      const devId = parseInt(path.replace('device/revoke/', ''), 10);
      await sql`UPDATE device_tokens SET status = 'revoked' WHERE id = ${devId}`;
      return res.status(200).json({ code: 0, message: 'Qurilma ulanishi bekor qilindi' });
    }

    if (path === 'device/decode-frame') {
      return res.status(200).json({ code: 0, barcode: null, message: 'Kamera tayyor' });
    }

    // Sales Mobile Push & Phone Checkout
    if (path === 'sales/push-pc-sale' && req.method === 'POST') {
      const token = req.headers['x-device-token'] || '';
      const { pc_user_id, items } = req.body || {};
      const pushId = 'PUSH-' + Date.now().toString().slice(-6) + '-' + Math.floor(100 + Math.random() * 900);
      await sql`
        INSERT INTO sales_pushes (id, device_token, pc_user_id, items_json, status, created_at, updated_at)
        VALUES (${pushId}, ${token}, ${pc_user_id || 1}, ${JSON.stringify(items || [])}, 'pending', to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'), to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
      `;
      return res.status(200).json({ code: 0, data: { push_id: pushId, status: 'pending' }, message: 'Savat kompyuterga yuborildi' });
    }

    if (path === 'sales/pending-pushes') {
      const rows = await sql`SELECT * FROM sales_pushes WHERE status = 'pending' ORDER BY id DESC LIMIT 10`;
      const list = rows.map(r => ({
        ...r,
        items: typeof r.items_json === 'string' ? JSON.parse(r.items_json) : (r.items_json || [])
      }));
      return res.status(200).json({ code: 0, data: list });
    }

    if (path.startsWith('sales/push-payload/')) {
      const pushId = path.replace('sales/push-payload/', '');
      const rows = await sql`SELECT * FROM sales_pushes WHERE id = ${pushId} LIMIT 1`;
      if (rows[0]) {
        const items = typeof rows[0].items_json === 'string' ? JSON.parse(rows[0].items_json) : (rows[0].items_json || []);
        return res.status(200).json({ code: 0, data: { ...rows[0], items } });
      }
      return res.status(404).json({ code: 404, message: 'Push topilmadi' });
    }

    if (path === 'sales/respond-push' && req.method === 'POST') {
      const { push_id, action } = req.body || {};
      const newStatus = action === 'accept' ? 'accepted' : 'declined';
      await sql`UPDATE sales_pushes SET status = ${newStatus}, updated_at = to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS') WHERE id = ${push_id}`;
      return res.status(200).json({ code: 0, message: `Savat ${action === 'accept' ? 'qabul qilindi' : 'bekor qilindi'}` });
    }

    if (path === 'sales/phone-checkout' && req.method === 'POST') {
      const { items, payment_type, total_amount, paid_amount, customer_name, customer_phone } = req.body || {};
      const receiptNo = 'KNT-PH-' + Date.now().toString().slice(-6) + '-' + Math.floor(100 + Math.random() * 900);
      const totalVal = parseFloat(total_amount) || 0;
      const paidVal = paid_amount !== undefined ? parseFloat(paid_amount) : totalVal;
      const debtVal = Math.max(0, totalVal - paidVal);

      await sql`
        INSERT INTO sales (
          id, items, total, total_amount, payment_method, status, customer_name, customer_phone, debt_amount, user_id, "createTime"
        )
        VALUES (
          ${receiptNo}, ${JSON.stringify(items || [])}, ${totalVal}, ${totalVal}, ${payment_type || 'cash'}, 'completed',
          ${customer_name || null}, ${customer_phone || null}, ${debtVal}, 'mobile_pos', to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS')
        )
      `;

      if (Array.isArray(items)) {
        for (const item of items) {
          const qty = item.quantity || 1;
          const pid = item.product_id || item.id;
          if (pid) {
            await sql`UPDATE products SET "quantityInStock" = GREATEST(0, "quantityInStock" - ${qty}) WHERE id = ${pid}`;
          }
        }
      }

      return res.status(200).json({
        code: 0,
        data: {
          receipt_number: receiptNo,
          total: totalVal,
          paid: paidVal,
          debt: debtVal
        },
        message: 'Telefon orqali sotuv yakunlandi'
      });
    }

    // QR Codes CRUD
    if (path === 'qr/list') {
      const rows = await sql`SELECT * FROM qr_codes ORDER BY id DESC`;
      return res.status(200).json({ code: 0, data: rows });
    }
    if (path === 'qr/save' && req.method === 'POST') {
      const { taskId, quantity } = req.body || {};
      const id = 'QR-' + Date.now().toString().slice(-6);
      const code = 'KNT-' + Math.random().toString(36).substring(2, 8).toUpperCase();
      await sql`
        INSERT INTO qr_codes (id, task_id, code, quantity, status, "createTime")
        VALUES (${id}, ${taskId || 'TASK-01'}, ${code}, ${quantity || 1}, 'active', to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
      `;
      return res.status(200).json({ code: 0, data: { id, code }, message: 'QR kod yaratildi' });
    }
    if (path === 'qr/delete' && req.method === 'POST') {
      const { ids } = req.body || {};
      if (Array.isArray(ids) && ids.length > 0) {
        await sql`DELETE FROM qr_codes WHERE id = ANY(${ids})`;
      }
      return res.status(200).json({ code: 0, message: 'QR kod o\'chirildi' });
    }

    // Cutting Production Management Endpoints
    if (path === 'cutting/stage/list') {
      const rows = await sql`SELECT * FROM cutting_stages ORDER BY sequence ASC, id ASC`;
      return res.status(200).json({ code: 0, data: rows });
    }
    if (path === 'cutting/stage/save' && req.method === 'POST') {
      const { id, name, code, sequence, description, status } = req.body || {};
      if (id) {
        await sql`
          UPDATE cutting_stages 
          SET name = ${name}, code = ${code || null}, sequence = ${sequence || 1}, description = ${description || null}, status = ${status !== undefined ? status : 1}
          WHERE id = ${id}
        `;
      } else {
        const newId = 'STG-' + Date.now().toString().slice(-5);
        await sql`
          INSERT INTO cutting_stages (id, name, code, sequence, description, status, "createTime")
          VALUES (${newId}, ${name}, ${code || null}, ${sequence || 1}, ${description || null}, ${status !== undefined ? status : 1}, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
        `;
      }
      return res.status(200).json({ code: 0, message: 'Bosqich saqlandi' });
    }
    if (path === 'cutting/stage/delete' && req.method === 'POST') {
      const { ids } = req.body || {};
      if (Array.isArray(ids) && ids.length > 0) {
        await sql`DELETE FROM cutting_stages WHERE id = ANY(${ids})`;
      }
      return res.status(200).json({ code: 0, message: 'Bosqich o\'chirildi' });
    }

    if (path === 'cutting/process/list') {
      const rows = await sql`SELECT * FROM cutting_processes ORDER BY id ASC`;
      return res.status(200).json({ code: 0, data: rows });
    }
    if (path === 'cutting/process/save' && req.method === 'POST') {
      const { id, name, stage_id, description, status } = req.body || {};
      if (id) {
        await sql`
          UPDATE cutting_processes 
          SET name = ${name}, stage_id = ${stage_id || null}, description = ${description || null}, status = ${status !== undefined ? status : 1}
          WHERE id = ${id}
        `;
      } else {
        const newId = 'PRC-' + Date.now().toString().slice(-5);
        await sql`
          INSERT INTO cutting_processes (id, name, stage_id, description, status, "createTime")
          VALUES (${newId}, ${name}, ${stage_id || null}, ${description || null}, ${status !== undefined ? status : 1}, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
        `;
      }
      return res.status(200).json({ code: 0, message: 'Jarayon saqlandi' });
    }
    if (path === 'cutting/process/delete' && req.method === 'POST') {
      const { ids } = req.body || {};
      if (Array.isArray(ids) && ids.length > 0) {
        await sql`DELETE FROM cutting_processes WHERE id = ANY(${ids})`;
      }
      return res.status(200).json({ code: 0, message: 'Jarayon o\'chirildi' });
    }

    if (path === 'cutting/order/list') {
      const rows = await sql`SELECT * FROM cutting_orders ORDER BY id DESC`;
      return res.status(200).json({ code: 0, data: rows });
    }
    if (path === 'cutting/order/save' && req.method === 'POST') {
      const { id, order_no, product_name, quantity, status, remark } = req.body || {};
      if (id) {
        await sql`
          UPDATE cutting_orders 
          SET order_no = ${order_no}, product_name = ${product_name}, quantity = ${quantity || 1}, status = ${status || 'pending'}, remark = ${remark || null}
          WHERE id = ${id}
        `;
      } else {
        const newId = 'ORD-' + Date.now().toString().slice(-6);
        await sql`
          INSERT INTO cutting_orders (id, order_no, product_name, quantity, status, remark, "createTime")
          VALUES (${newId}, ${order_no || ('BUY-' + Date.now().toString().slice(-4))}, ${product_name}, ${quantity || 1}, ${status || 'pending'}, ${remark || null}, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
        `;
      }
      return res.status(200).json({ code: 0, message: 'Buyurtma saqlandi' });
    }
    if (path === 'cutting/order/delete' && req.method === 'POST') {
      const { ids } = req.body || {};
      if (Array.isArray(ids) && ids.length > 0) {
        await sql`DELETE FROM cutting_orders WHERE id = ANY(${ids})`;
      }
      return res.status(200).json({ code: 0, message: 'Buyurtma o\'chirildi' });
    }
    if (path === 'cutting/order/start-production' && req.method === 'POST') {
      const { orderId } = req.body || {};
      if (orderId) {
        await sql`UPDATE cutting_orders SET status = 'in_production' WHERE id = ${orderId}`;
      }
      return res.status(200).json({ code: 0, message: 'Ishlab chiqarish boshlandi' });
    }

    if (path === 'cutting/task/list') {
      const rows = await sql`SELECT * FROM cutting_tasks ORDER BY id DESC`;
      return res.status(200).json({ code: 0, data: rows });
    }
    if (path === 'cutting/task/update-status' && req.method === 'POST') {
      const { taskId, status } = req.body || {};
      if (taskId) {
        await sql`UPDATE cutting_tasks SET status = ${status} WHERE id = ${taskId}`;
      }
      return res.status(200).json({ code: 0, message: 'Vazifa holati yangilandi' });
    }
    if (path === 'cutting/task/execution/list') {
      const rows = await sql`SELECT * FROM cutting_task_executions ORDER BY id DESC`;
      return res.status(200).json({ code: 0, data: rows });
    }
    if (path === 'cutting/task/execution/save' && req.method === 'POST') {
      const { id, task_id, worker_id, worker_name, quantity, status, remark } = req.body || {};
      if (id) {
        await sql`
          UPDATE cutting_task_executions 
          SET task_id = ${task_id}, worker_id = ${worker_id}, worker_name = ${worker_name}, quantity = ${quantity || 1}, status = ${status || 'completed'}, remark = ${remark || null}
          WHERE id = ${id}
        `;
      } else {
        const newId = 'EXEC-' + Date.now().toString().slice(-6);
        await sql`
          INSERT INTO cutting_task_executions (id, task_id, worker_id, worker_name, quantity, status, remark, "createTime")
          VALUES (${newId}, ${task_id}, ${worker_id}, ${worker_name}, ${quantity || 1}, ${status || 'completed'}, ${remark || null}, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))
        `;
      }
      return res.status(200).json({ code: 0, message: 'Bajarish yozuvi saqlandi' });
    }
    if (path === 'cutting/task/execution/delete' && req.method === 'POST') {
      const { ids } = req.body || {};
      if (Array.isArray(ids) && ids.length > 0) {
        await sql`DELETE FROM cutting_task_executions WHERE id = ANY(${ids})`;
      }
      return res.status(200).json({ code: 0, message: 'Bajarish yozuvi o\'chirildi' });
    }

    // 22. GET /api/ai/config
    if (path === 'ai/config') {
      const username = req.query?.username || urlSearchParams.get('username') || authUser?.username || authUser?.sub || 'admin';
      const geminiKey = process.env.GEMINI_API_KEY || process.env.VITE_GEMINI_API_KEY || '';

      let dbUser = null;
      const userRows = await sql`
        SELECT u.*, r."roleName" as role_title, r.permissions as role_perms 
        FROM users u LEFT JOIN roles r ON u."roleId" = r.id 
        WHERE u.username = ${username} LIMIT 1
      `;
      if (userRows[0]) {
        dbUser = userRows[0];
      } else {
        const workerRows = await sql`
          SELECT w.*, r."roleName" as role_title, r.permissions as role_perms 
          FROM workers w LEFT JOIN roles r ON w.role = r."roleName" 
          WHERE w.account = ${username} OR w.employee_code = ${username} LIMIT 1
        `;
        if (workerRows[0]) {
          dbUser = workerRows[0];
        }
      }

      const userRole = dbUser?.role_title || dbUser?.role || (username === 'admin' ? 'Super Administrator' : 'Cashier');
      const isSuper = userRole === 'Super Administrator' || userRole === 'Administrator' || username === 'admin';

      // Company plan check: AI is strictly Pro-only
      const userCompId = dbUser?.company_id || 'comp-default';
      const compRows = await sql`SELECT * FROM companies WHERE id = ${userCompId} LIMIT 1`;
      const comp = compRows[0];
      if (comp && comp.plan !== 'pro' && !isSuper) {
        return res.status(403).json({
          code: 403,
          message: "AI xususiyatlari faqat PRO obuna tarifida mavjud. Iltimos, tarifingizni yangilang.",
          plan: comp.plan,
          features: comp.features || {}
        });
      }

      let allowedTools = [];
      if (isSuper) {
        allowedTools = [
          'create_worker', 'update_worker', 'delete_worker', 'list_workers',
          'create_product', 'add_product_stock', 'update_product', 'delete_product', 'list_products', 'search_product',
          'create_department', 'list_departments',
          'create_position', 'list_positions',
          'create_timesheet', 'create_staff_output', 'list_staff_outputs', 'create_staff_adjustment', 'list_staff_adjustments',
          'list_users', 'list_sales', 'get_sale_receipt', 'list_debtors', 'repay_debt',
          'list_salaries', 'create_salary', 'salary_payout',
          'list_roles', 'create_role', 'delete_role',
          'list_branches', 'create_branch',
          'create_cutting_order', 'delete_cutting_order', 'list_cutting_orders', 'start_production', 'list_cutting_tasks', 'update_task_status',
          'generate_qr_code', 'list_qr_codes', 'delete_qr_code',
          'get_top_selling_products', 'get_sales_analytics', 'get_debt_report'
        ];
      } else {
        // Restricted to Cashier / Sales tools only (NO HR, NO Salary, NO Role editing)
        allowedTools = [
          'list_products', 'search_product', 'add_product_stock',
          'list_sales', 'get_sale_receipt', 'list_debtors', 'repay_debt',
          'get_top_selling_products', 'get_sales_analytics'
        ];
      }

      return res.status(200).json({
        code: 0,
        data: {
          gemini_api_key: geminiKey,
          user: {
            name: dbUser?.full_name || dbUser?.name || username,
            username: username,
            role: userRole,
            is_super: isSuper
          },
          allowed_tools: allowedTools
        }
      });
    }

    // Fallback for any other API route
    return res.status(200).json({
      code: 0,
      data: { list: [], total: 0 },
      message: 'OK'
    });
  } catch (err) {
    console.error('API Router Error:', err);
    return res.status(500).json({
      error: 'API Router Execution Error',
      message: err.message,
      stack: err.stack
    });
  }
}
