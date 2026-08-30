import { getPool } from '../_db.js';
import jwt from 'jsonwebtoken';

const SECRET_KEY = process.env.SECRET_KEY || 'super-secret-key-that-is-hard-to-guess';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ code: 405, message: 'Method Not Allowed' });
  }

  try {
    const { username, password } = req.body || {};
    const pool = getPool();

    const userRes = await pool.query('SELECT * FROM users WHERE username = $1', [username]);
    let user = userRes.rows[0];

    if (!user) {
      const workerRes = await pool.query(
        'SELECT * FROM workers WHERE account = $1 OR employee_code = $1 OR name = $1 LIMIT 1',
        [username]
      );
      const worker = workerRes.rows[0];
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
        const ins = await pool.query(
          `INSERT INTO users (username, full_name, role, "roleId", permissions) 
           VALUES ($1, $2, $3, $4, $5) RETURNING *`,
          ['admin', 'Administrator', 'Super Administrator', '1', JSON.stringify(['*.*.*'])]
        );
        user = ins.rows[0];
      } else {
        return res.status(200).json({ code: 500, message: "Xodim topilmadi yoki parol noto'g'ri" });
      }
    }

    const token = 'Bearer ' + jwt.sign({ sub: user.username }, SECRET_KEY, { expiresIn: '12h' });

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
  } catch (err) {
    console.error('Login error:', err);
    return res.status(200).json({ code: 500, message: 'Server xatoligi: ' + err.message });
  }
}
