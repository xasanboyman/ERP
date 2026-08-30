import { getSql } from '../_db.js';
import { authenticate } from '../_auth.js';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', '*');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const user = authenticate(req, res);
  if (!user) return;

  try {
    const sql = getSql();
    const pageIndex = parseInt(req.query?.pageIndex || 1, 10);
    const pageSize = parseInt(req.query?.pageSize || 20, 10);
    const offset = (pageIndex - 1) * pageSize;

    const countRes = await sql`SELECT count(*) FROM activity_logs`;
    const total = parseInt(countRes[0].count, 10);

    const rows = await sql`
      SELECT * FROM activity_logs ORDER BY id DESC LIMIT ${pageSize} OFFSET ${offset}
    `;

    return res.status(200).json({
      code: 0,
      data: {
        total,
        list: rows
      }
    });
  } catch (err) {
    return res.status(500).json({ error: 'Activity List Error', message: err.message });
  }
}
