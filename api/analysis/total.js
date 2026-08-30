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
  } catch (err) {
    return res.status(500).json({ error: 'Analysis Total Error', message: err.message });
  }
}
