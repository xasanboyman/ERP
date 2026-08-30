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

function authenticate(req, res) {
  const authHeader = req?.headers?.authorization || req?.headers?.Authorization;
  if (!authHeader) {
    res.status(401).json({
      code: 401,
      message: 'Avtorizatsiya talab qilinadi. Iltimos, tizimga kiring.'
    });
    return null;
  }

  let token = String(authHeader).trim();
  if (token.startsWith('Bearer ') || token.startsWith('bearer ')) {
    token = token.slice(7).trim();
  }

  try {
    const payload = jwt.verify(token, SECRET_KEY);
    return payload;
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      res.status(401).json({
        code: 401,
        message: 'Sessiya muddati tugadi. Iltimos qaytadan kiring.'
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
            role: worker.role || 'Cashier',
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

      const token = 'Bearer ' + jwt.sign({ sub: user.username, id: user.id }, SECRET_KEY, { expiresIn: '8h' });
      let permissions = user.permissions;
      if (typeof permissions === 'string') {
        try { permissions = JSON.parse(permissions); } catch (e) { permissions = []; }
      }
      if (!Array.isArray(permissions)) {
        permissions = ['*.*.*'];
      }

      return res.status(200).json({
        code: 0,
        data: {
          id: user.id || 1,
          username: user.username || username,
          full_name: user.full_name || user.username || 'admin',
          initials: (user.full_name || user.username || 'AD').substring(0, 2).toUpperCase(),
          avatar: user.avatar || '',
          role: user.role || 'Super Administrator',
          roleId: user.roleId || '1',
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

    // 9. GET /api/worker/list
    if (path === 'worker/list') {
      const pageIndex = parseInt(req.query?.pageIndex || urlSearchParams.get('pageIndex') || 1, 10);
      const pageSize = parseInt(req.query?.pageSize || urlSearchParams.get('pageSize') || 20, 10);
      const offset = (pageIndex - 1) * pageSize;
      const [countRes, rows] = await Promise.all([
        sql`SELECT count(*) FROM workers`,
        sql`SELECT * FROM workers ORDER BY id DESC LIMIT ${pageSize} OFFSET ${offset}`
      ]);
      return res.status(200).json({
        code: 0,
        data: {
          total: parseInt(countRes[0].count, 10),
          list: rows
        }
      });
    }

    // 10. Roles Endpoints
    if (path === 'role/list') {
      const roleName = req.query?.roleName || urlSearchParams.get('roleName');
      if (roleName) {
        return res.status(200).json({ code: 0, data: defaultAdminRoutes });
      }
      const rows = await sql`SELECT * FROM roles ORDER BY id ASC`;
      return res.status(200).json({ code: 0, data: { total: rows.length, list: rows } });
    }

    if (path === 'role/list2') {
      return res.status(200).json({ code: 0, data: defaultRoleKeys });
    }

    if (path === 'role/table') {
      const rows = await sql`SELECT * FROM roles ORDER BY id ASC`;
      return res.status(200).json({ code: 0, data: { total: rows.length, list: rows } });
    }

    if (path === 'role/save' && req.method === 'POST') {
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
      const { id } = req.body || {};
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
