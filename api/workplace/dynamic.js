import { getSql } from '../_db.js';
import { authenticate } from '../_auth.js';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', '*');
  if (req.method === 'OPTIONS') return res.status(200).end();

  try {
    const user = authenticate(req, res);
    if (!user) return;

    const sql = getSql();
    const rows = await sql`SELECT * FROM workplace_dynamics ORDER BY id DESC LIMIT 10`;
    const logs = rows.map(r => {
      let keys = r.keys;
      if (typeof keys === 'string') {
        try { keys = JSON.parse(keys); } catch(e) { keys = [keys]; }
      }
      return { keys, time: r.time };
    });

    return res.status(200).json({
      code: 0,
      data: logs
    });
  } catch (err) {
    return res.status(500).json({ error: 'Workplace Dynamic Error', message: err.message, stack: err.stack });
  }
}
