import pg from 'pg';
const { Pool } = pg;

const DATABASE_URL = process.env.DATABASE_URL || 'postgresql://neondb_owner:npg_OgGezc9umYl0@ep-hidden-mountain-a5l36vpb-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require';

let pool;

export function getPool() {
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
