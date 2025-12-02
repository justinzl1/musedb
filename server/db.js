import pkg from 'pg';
const { Pool } = pkg;
import dotenv from 'dotenv';

dotenv.config();

//Initalize the connection pool
let pool = null;

// Function to get database connection
export function getDbConnection() {
  if (!pool) {
    // Makes sure that all the required environment variables are set
    if (!process.env.DB_HOST || !process.env.DB_NAME || !process.env.DB_USER || !process.env.DB_PASSWORD) {
      throw new Error('Missing Required environment variables, check your .env file!');
    }

    //Creates a new connection pool (for supabase) -- will try it 20 times before erroring out
    pool = new Pool({
      host: process.env.DB_HOST,
      port: process.env.DB_PORT || 5432,
      database: process.env.DB_NAME,
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      ssl: {
        rejectUnauthorized: false
      },
      max: 20,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
    });

    // Handle errors due to the clients being idle by killing the process
    pool.on('error', (err) => {
      console.error('Unexpected error on idle client', err);
      process.exit(-1);
    });
  }

  //Tries to connect
  return pool.connect();
}

