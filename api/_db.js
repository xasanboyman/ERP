import { neon } from '@neondatabase/serverless';

const DATABASE_URL = process.env.DATABASE_URL || 'postgresql://neondb_owner:npg_ArFp1ORwLbX6@ep-sparkling-fog-axd0fzvc-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require';

let sqlClient;

export function getSql() {
  if (!sqlClient) {
    let connStr = DATABASE_URL;
    if (connStr.startsWith('postgres://')) {
      connStr = connStr.replace('postgres://', 'postgresql://');
    }
    connStr = connStr.replace('&channel_binding=require', '').replace('?channel_binding=require', '');
    sqlClient = neon(connStr);
  }
  return sqlClient;
}
