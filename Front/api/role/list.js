import { getPool } from '../_db.js';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', '*');
  if (req.method === 'OPTIONS') return res.status(200).end();

  try {
    const pool = getPool();
    const rowsRes = await pool.query('SELECT * FROM roles ORDER BY id ASC');
    return res.status(200).json({
      code: 0,
      data: {
        total: rowsRes.rows.length,
        list: rowsRes.rows
      }
    });
  } catch (err) {
    return res.status(200).json({ code: 500, message: err.message });
  }
}
