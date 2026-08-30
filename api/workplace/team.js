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
    const rows = await sql`SELECT * FROM workplace_teams ORDER BY id ASC`;
    return res.status(200).json({
      code: 0,
      data: rows
    });
  } catch (err) {
    return res.status(500).json({ error: 'Workplace Team Error', message: err.message });
  }
}
