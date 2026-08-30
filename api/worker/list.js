import { getPool } from '../_db.js';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', '*');

  if (req.method === 'OPTIONS') return res.status(200).end();

  try {
    const pool = getPool();
    const pageIndex = parseInt(req.query?.pageIndex || 1, 10);
    const pageSize = parseInt(req.query?.pageSize || 20, 10);
    const offset = (pageIndex - 1) * pageSize;

    const countRes = await pool.query('SELECT count(*) FROM workers');
    const total = parseInt(countRes.rows[0].count, 10);

    const rowsRes = await pool.query(
      'SELECT * FROM workers ORDER BY id DESC LIMIT $1 OFFSET $2',
      [pageSize, offset]
    );

    return res.status(200).json({
      code: 0,
      data: {
        total,
        list: rowsRes.rows
      }
    });
  } catch (err) {
    return res.status(200).json({ code: 500, message: err.message });
  }
}
