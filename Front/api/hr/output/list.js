import { getSql } from '../../_db.js';
import { authenticate } from '../../_auth.js';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', '*');
  if (req.method === 'OPTIONS') return res.status(200).end();

  try {
    const user = authenticate(req, res);
    if (!user) return;

    const sql = getSql();
    const rows = await sql`SELECT * FROM staff_outputs ORDER BY id DESC`;
    return res.status(200).json({
      code: 0,
      data: {
        total: rows.length,
        list: rows
      }
    });
  } catch (err) {
    return res.status(200).json({
      code: 0,
      data: {
        total: 0,
        list: []
      }
    });
  }
}
