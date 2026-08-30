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
    const rows = await sql`SELECT * FROM branches ORDER BY id ASC`;
    return res.status(200).json({
      code: 0,
      data: {
        total: rows.length,
        list: rows
      }
    });
  } catch (err) {
    return res.status(500).json({ code: 500, message: err.message });
  }
}
