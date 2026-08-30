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
    const [pCount, wCount, tCount] = await Promise.all([
      sql`SELECT count(*) FROM products`,
      sql`SELECT count(*) FROM workers`,
      sql`SELECT count(*) FROM todos WHERE completed = 0`
    ]);

    const totalProducts = parseInt(pCount[0].count, 10);
    const totalWorkers = parseInt(wCount[0].count, 10);
    const totalTodos = parseInt(tCount[0].count, 10);

    return res.status(200).json({
      code: 0,
      data: {
        project: totalProducts,
        access: 100 + totalWorkers * 10,
        todo: totalTodos
      }
    });
  } catch (err) {
    return res.status(500).json({ error: 'Workplace Total Error', message: err.message });
  }
}
