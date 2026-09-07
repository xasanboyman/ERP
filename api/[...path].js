import { neon } from '@neondatabase/serverless';
import jwt from 'jsonwebtoken';

const DATABASE_URL = process.env.DATABASE_URL || 'postgresql://neondb_owner:npg_OgGezc9umYl0@ep-hidden-mountain-a5l36vpb-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require';
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
  },
  {
    path: '/sales',
    component: '#',
    redirect: '/sales/pos',
    name: 'SalesRoot',
    meta: {
      title: 'Sotuvlar (POS)',
      icon: 'vi-ep:shopping-cart-full',
      alwaysShow: true
    },
    children: [
      {
        path: 'pos',
        component: 'views/Sales/Pos',
        name: 'SalesPos',
        meta: {
          title: 'Sotuvlar (POS)',
          noCache: true
        }
      },
      {
        path: 'debtors',
        component: 'views/Sales/Debtors',
        name: 'SalesDebtors',
        meta: {
          title: 'Nasiyalar (Qarzlar)',
          noCache: true
        }
      }
    ]
  },
  {
    path: '/hr',
    component: '#',
    redirect: '/hr/workers',
    name: 'HRRoot',
    meta: {
      title: 'Xodimlar (HR)',
      icon: 'vi-ep:avatar',
      alwaysShow: true
    },
    children: [
      {
        path: 'workers',
        component: 'views/Worker/Worker',
        name: 'WorkerManagement',
        meta: {
          title: 'Xodimlar Ro\'yxati',
          noCache: true
        }
      },
      {
        path: 'timesheets',
        component: 'views/StaffHR/Timesheet',
        name: 'TimesheetManagement',
        meta: {
          title: 'Ish Vaqti (Davomat)',
          noCache: true
        }
      },
      {
        path: 'outputs',
        component: 'views/StaffHR/Output',
        name: 'OutputManagement',
        meta: {
          title: 'Kunlik Ishbay Ishlab Chiqarish',
          noCache: true
        }
      },
      {
        path: 'adjustments',
        component: 'views/StaffHR/Adjustment',
        name: 'AdjustmentManagement',
        meta: {
          title: 'Mukofot va Jarimalar',
          noCache: true
        }
      },
      {
        path: 'salary',
        component: 'views/Salary/Salary',
        name: 'SalaryManagement',
        meta: {
          title: 'Oylik Maoshlar',
          noCache: true
        }
      }
    ]
  },
  {
    path: '/authorization',
    component: '#',
    redirect: '/authorization/role',
    name: 'Authorization',
    meta: {
      title: 'Huquqlar & Sozlamalar',
      icon: 'vi-eos-icons:role-binding',
      alwaysShow: true
    },
    children: [
      {
        path: 'department',
        component: 'views/Authorization/Department/Department',
        name: 'Department',
        meta: {
          title: 'Bo\'limlar',
          noCache: true
        }
      },
      {
        path: 'role',
        component: 'views/Authorization/Role/Role',
        name: 'Role',
        meta: {
          title: 'Rollar',
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
  '/product',
  '/product/list',
  '/sales',
  '/sales/pos',
  '/sales/debtors',
  '/hr',
  '/hr/workers',
  '/hr/timesheets',
  '/hr/outputs',
  '/hr/adjustments',
  '/hr/salary',
  '/authorization',
  '/authorization/department',
  '/authorization/role'
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
  if (rawUrl.startsWith('/api')) {
    rawUrl = rawUrl.substring(4);
  }
  const [pathname, search] = rawUrl.split('?');
  const path = pathname.replace(/^\/+|\/+$/g, '');
  const urlSearchParams = new URLSearchParams(search || '');
  const sql = getSql();

  try {
    // 1. POST /api/user/login (Public)
    if (path === 'user/login' && req.method === 'POST') {
      const { username, password } = req.body || {};
      const userRows = await sql`SELECT * FROM users WHERE username = ${username}`;
      let user = userRows[0];

      if (!user) {
        const workerRows = await sql`
          SELECT * FROM workers WHERE account = ${username} OR employee_code = ${username} OR name = ${username} LIMIT 1
        `;
        const worker = workerRows[0];
        if (worker) {
          user = {
            id: worker.id,
            username: worker.account || `worker_${worker.id}`,
            full_name: worker.name,
            role: worker.role || 'Oddiy xodim',
            roleId: '3',
            avatar: worker.avatar || '',
            permissions: []
          };
        }
      }

      if (!user) {
        if (username === 'admin') {
          const ins = await sql`
            INSERT INTO users (username, full_name, role, "roleId", permissions) 
            VALUES ('admin', 'Administrator', 'Super Administrator', '1', ${JSON.stringify(['*.*.*'])}) RETURNING *
          `;
          user = ins[0];
        } else {
          return res.status(200).json({ code: 500, message: "Xodim topilmadi yoki parol noto'g'ri" });
        }
      }

      // Ensure user has a valid role and roleId:
      if (!user.role) {
        user.role = user.username === 'admin' ? 'Super Administrator' : 'Oddiy xodim';
        user.roleId = user.username === 'admin' ? '1' : '3';
      }

      const token = 'Bearer ' + jwt.sign({ sub: user.username, id: user.id }, SECRET_KEY, { expiresIn: '8h' });
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

    // ALL OTHER ENDPOINTS REQUIRE VALID TOKEN
    const authUser = authenticate(req, res);
    if (!authUser) return;

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

    if (path === 'user/updateAvatar' && req.method === 'POST') {
      const { username, avatar } = req.body || {};
      await sql`UPDATE users SET avatar = ${avatar} WHERE username = ${username}`;
      const userRows = await sql`SELECT * FROM users WHERE username = ${username}`;
      return res.status(200).json({ code: 0, data: userRows[0] || { username, avatar }, message: 'Avatar saqlandi' });
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
      const offset = (pageIndex - 1) * pageSize;
      const [countRes, rows] = await Promise.all([
        sql`SELECT count(*) FROM products`,
        sql`SELECT * FROM products ORDER BY id DESC LIMIT ${pageSize} OFFSET ${offset}`
      ]);
      return res.status(200).json({
        code: 0,
        data: {
          total: parseInt(countRes[0].count, 10),
          list: rows
        }
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
      const roleName = req.query?.roleName || urlSearchParams.get('roleName') || authUser?.role || authUser?.sub;
      if (roleName) {
        let permissions = ['*.*.*'];
        if (roleName !== 'Super Administrator' && roleName !== 'admin') {
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
        return res.status(200).json({ code: 0, data: filterRoutesByRole(permissions) });
      }
      const rows = await sql`SELECT * FROM roles ORDER BY id ASC`;
      return res.status(200).json({ code: 0, data: { total: rows.length, list: rows } });
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
      const { id, departmentName, parentId, status, remark } = req.body || {};
      if (id) {
        await sql`
          UPDATE departments 
          SET "departmentName" = ${departmentName}, "parentId" = ${parentId || null}, status = ${status !== undefined ? status : 1}, remark = ${remark || null}
          WHERE id = ${id}
        `;
      } else {
        const newId = 'dept_' + Date.now().toString(36);
        await sql`
          INSERT INTO departments (id, "departmentName", "parentId", status, remark, "createTime")
          VALUES (${newId}, ${departmentName}, ${parentId || null}, ${status !== undefined ? status : 1}, ${remark || null}, NOW())
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
      const rows = await sql`SELECT * FROM workers WHERE department_id = ${deptId} OR department = ${deptId}`;
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

    // 13. GET /api/sales/list
    if (path === 'sales/list') {
      const pageIndex = parseInt(req.query?.pageIndex || urlSearchParams.get('pageIndex') || 1, 10);
      const pageSize = parseInt(req.query?.pageSize || urlSearchParams.get('pageSize') || 500, 10);
      const offset = (pageIndex - 1) * pageSize;
      const [countRes, rows] = await Promise.all([
        sql`SELECT count(*) FROM sales`,
        sql`SELECT * FROM sales ORDER BY id DESC LIMIT ${pageSize} OFFSET ${offset}`
      ]);
      return res.status(200).json({
        code: 0,
        data: {
          total: parseInt(countRes[0].count, 10),
          list: rows
        }
      });
    }

    // GET /api/sales/debtors
    if (path === 'sales/debtors') {
      const search = (req.query?.search || urlSearchParams.get('search') || '').toLowerCase().trim();
      const statusFilter = req.query?.status || urlSearchParams.get('status');

      const [debtSales, payments] = await Promise.all([
        sql`SELECT * FROM sales WHERE payment_method = 'nasiya' OR (debt_amount IS NOT NULL AND debt_amount > 0) ORDER BY created_at DESC`,
        sql`SELECT * FROM debt_payments ORDER BY created_at DESC`
      ]);

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
    }

    // GET /api/sales/debtor-detail
    if (path === 'sales/debtor-detail') {
      const name = req.query?.name || urlSearchParams.get('name');
      if (!name) {
        return res.status(200).json({ code: 0, data: null });
      }

      const [debtSales, payments] = await Promise.all([
        sql`
          SELECT * FROM sales 
          WHERE (customer_name = ${name} OR receipt_number LIKE ${'%' + name + '%'}) 
            AND (payment_method = 'nasiya' OR (debt_amount IS NOT NULL AND debt_amount > 0))
          ORDER BY created_at DESC
        `,
        sql`
          SELECT * FROM debt_payments 
          WHERE customer_name = ${name}
          ORDER BY created_at DESC
        `
      ]);

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
    }

    // POST /api/sales/repay-debt
    if (path === 'sales/repay-debt' && req.method === 'POST') {
      const { customer_name, customer_phone, amount, payment_method, cashier_name, remark } = req.body || {};
      const numAmount = parseFloat(amount) || 0;
      const receipt_number = 'PAY-' + Date.now().toString(36).toUpperCase() + '-' + Math.floor(1000 + Math.random() * 9000);
      const paymentId = 'PMT-' + Date.now().toString(36);
      const nowStr = new Date().toISOString().replace('T', ' ').substring(0, 19);

      await sql`
        INSERT INTO debt_payments (id, receipt_number, customer_name, customer_phone, amount, payment_method, cashier_name, remark, created_at)
        VALUES (${paymentId}, ${receipt_number}, ${customer_name}, ${customer_phone || null}, ${numAmount}, ${payment_method || 'naqd'}, ${cashier_name || 'admin'}, ${remark || null}, ${nowStr})
      `;

      const debtSales = await sql`
        SELECT * FROM sales 
        WHERE (customer_name = ${customer_name}) 
          AND (payment_method = 'nasiya' OR (debt_amount IS NOT NULL AND debt_amount > 0))
      `;
      const allPayments = await sql`SELECT * FROM debt_payments WHERE customer_name = ${customer_name}`;
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

      await sql`
        INSERT INTO sales (
          id, receipt_number, cashier_name, customer_name, customer_phone,
          payment_method, total_amount, paid_amount, debt_amount, total_items,
          discount, remark, created_at
        ) VALUES (
          ${saleId}, ${recNo}, ${cashier_name || 'admin'}, ${customer_name || null}, ${customer_phone || null},
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

    // 18. GET /api/branch/list
    if (path === 'branch/list') {
      const rows = await sql`SELECT * FROM branches ORDER BY id ASC`;
      return res.status(200).json({ code: 0, data: { total: rows.length, list: rows } });
    }

    // 19. GET /api/classifier/list
    if (path === 'classifier/list') {
      const rows = await sql`SELECT * FROM classifier_items ORDER BY id ASC`;
      return res.status(200).json({ code: 0, data: { total: rows.length, list: rows } });
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
