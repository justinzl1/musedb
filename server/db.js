import pkg from 'pg';
const { Pool } = pkg;
import dotenv from 'dotenv';

dotenv.config();

let pool = null;

export function getDbConnection() {
  if (!pool) {
    // Validate required environment variables
    if (!process.env.DB_HOST || !process.env.DB_NAME || 
        !process.env.DB_USER || !process.env.DB_PASSWORD) {
      throw new Error('Missing required database environment variables. Please check your .env file.');
    }

    pool = new Pool({
      host: process.env.DB_HOST,
      port: process.env.DB_PORT || 5432,
      database: process.env.DB_NAME,
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      ssl: {
        rejectUnauthorized: false // Required for Supabase
      },
      max: 20,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
    });

    // Handle pool errors
    pool.on('error', (err) => {
      console.error('Unexpected error on idle client', err);
      process.exit(-1);
    });
  }

  return pool.connect();
}

