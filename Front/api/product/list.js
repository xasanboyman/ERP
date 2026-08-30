import pg from 'pg';
const { Pool } = pg;

const DATABASE_URL = process.env.DATABASE_URL || 'postgresql://neondb_owner:npg_OgGezc9umYl0@ep-hidden-mountain-a5l36vpb-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require';

let pool;
function getPool() {
  if (!pool) {
    let connStr = DATABASE_URL;
    if (connStr.startsWith('postgres://')) {
      connStr = connStr.replace('postgres://', 'postgresql://');
    }
    connStr = connStr.replace('&channel_binding=require', '').replace('?channel_binding=require', '');
    pool = new Pool({
      connectionString: connStr,
      ssl: { rejectUnauthorized: false },
      max: 10,
      idleTimeoutMillis: 30000,
    });
  }
  return pool;
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', '*');

  if (req.method === 'OPTIONS') return res.status(200).end();

  try {
    const p = getPool();
    const pageIndex = parseInt(req.query?.pageIndex || 1, 10);
    const pageSize = parseInt(req.query?.pageSize || 20, 10);
    const offset = (pageIndex - 1) * pageSize;

    const countRes = await p.query('SELECT count(*) FROM products');
    const total = parseInt(countRes.rows[0].count, 10);

    const rowsRes = await p.query(
      'SELECT * FROM products ORDER BY id DESC LIMIT $1 OFFSET $2',
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
    return res.status(500).json({ error: 'Product List Error', message: err.message });
  }
}
