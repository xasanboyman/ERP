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
  const [pathname] = rawUrl.split('?');
  const path = pathname.replace(/^\/+|\/+$/g, '');
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
      const pageIndex = parseInt(req.query?.pageIndex || 1, 10);
      const pageSize = parseInt(req.query?.pageSize || 20, 10);
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
      const pageIndex = parseInt(req.query?.pageIndex || 1, 10);
      const pageSize = parseInt(req.query?.pageSize || 20, 10);
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

    // 10. GET /api/role/list
    if (path === 'role/list') {
      const rows = await sql`SELECT * FROM roles ORDER BY id ASC`;
      return res.status(200).json({ code: 0, data: { total: rows.length, list: rows } });
    }

    // 11. GET /api/department/list
    if (path === 'department/list') {
      const rows = await sql`SELECT * FROM departments ORDER BY id ASC`;
      return res.status(200).json({ code: 0, data: { total: rows.length, list: rows } });
    }

    // 12. GET /api/salary/list
    if (path === 'salary/list') {
      const pageIndex = parseInt(req.query?.pageIndex || 1, 10);
      const pageSize = parseInt(req.query?.pageSize || 500, 10);
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
      const pageIndex = parseInt(req.query?.pageIndex || 1, 10);
      const pageSize = parseInt(req.query?.pageSize || 500, 10);
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
      const pageIndex = parseInt(req.query?.pageIndex || 1, 10);
      const pageSize = parseInt(req.query?.pageSize || 20, 10);
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

    // 16. GET /api/hr/output/list
    if (path === 'hr/output/list') {
      const rows = await sql`SELECT * FROM staff_outputs ORDER BY id DESC`;
      return res.status(200).json({ code: 0, data: { total: rows.length, list: rows } });
    }

    // 17. GET /api/branch/list
    if (path === 'branch/list') {
      const rows = await sql`SELECT * FROM branches ORDER BY id ASC`;
      return res.status(200).json({ code: 0, data: { total: rows.length, list: rows } });
    }

    // 18. GET /api/classifier/list
    if (path === 'classifier/list') {
      const rows = await sql`SELECT * FROM classifier_items ORDER BY id ASC`;
      return res.status(200).json({ code: 0, data: { total: rows.length, list: rows } });
    }

    // 19. GET /api/analysis/financial-overview
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

    // 20. GET /api/analysis/total
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
