from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta, date, datetime
import json

# Load .env from parent directory (project root)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
CORS(app)

# Database connection pool
connection_pool = None

def serialize_value(value):
    """Convert non-JSON-serializable values to JSON-serializable formats"""
    if value is None:
        return None
    elif isinstance(value, timedelta):
        # Convert timedelta to string format (HH:MM:SS)
        total_seconds = int(value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    elif isinstance(value, (date, datetime)):
        # Convert date/datetime to ISO format string
        return value.isoformat()
    elif isinstance(value, (bytes, bytearray)):
        # Convert bytes to string
        return value.decode('utf-8', errors='ignore')
    else:
        return value

def get_db_connection():
    """Get a database connection from the pool"""
    global connection_pool
    
    if connection_pool is None:
        # Validate required environment variables
        required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            raise ValueError(f'Missing required environment variables: {", ".join(missing)}')
        
        try:
            # Get connection parameters
            db_host = os.getenv('DB_HOST')
            db_port = int(os.getenv('DB_PORT', 5432))
            db_name = os.getenv('DB_NAME')
            db_user = os.getenv('DB_USER')
            db_password = os.getenv('DB_PASSWORD')
            
            # Debug: print connection info (without password)
            print(f"Connecting to: {db_host}:{db_port}, database: {db_name}, user: {db_user}")
            
            # Build connection string with SSL mode for Supabase
            # psycopg2 accepts connection string format
            conn_string = (
                f"host={db_host} "
                f"port={db_port} "
                f"dbname={db_name} "
                f"user={db_user} "
                f"password={db_password} "
                f"sslmode=require"
            )
            
            connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20, conn_string
            )
        except Exception as e:
            raise ConnectionError(f'Failed to create connection pool: {str(e)}')
    
    return connection_pool.getconn()

def release_db_connection(conn):
    """Release a database connection back to the pool"""
    if connection_pool and conn:
        connection_pool.putconn(conn)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Server is running'})

@app.route('/api/tables', methods=['GET'])
def get_tables():
    """Get all table names from the database"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """
        
        cursor.execute(query)
        tables = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        return jsonify(tables)
        
    except Exception as e:
        print(f'Error fetching tables: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        release_db_connection(conn)

@app.route('/api/tables/<table_name>', methods=['GET'])
def get_table_data(table_name):
    """Get data from a specific table"""
    conn = None
    try:
        # Sanitize table name to prevent SQL injection
        sanitized_table_name = ''.join(c for c in table_name if c.isalnum() or c == '_')
        
        if not sanitized_table_name:
            return jsonify({'error': 'Invalid table name'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get column names and data
        query = f"SELECT * FROM {sanitized_table_name} ORDER BY 1 LIMIT 1000;"
        cursor.execute(query)
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        # Convert rows to dictionaries and serialize non-JSON values
        data = []
        for row in rows:
            row_dict = {}
            for col, val in zip(columns, row):
                row_dict[col] = serialize_value(val)
            data.append(row_dict)
        
        cursor.close()
        
        return jsonify({
            'columns': columns,
            'rows': data,
            'count': len(data)
        })
        
    except Exception as e:
        print(f'Error fetching data from {table_name}: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        release_db_connection(conn)

@app.route('/api/all-data', methods=['GET'])
def get_all_data():
    """Get all data from all tables"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all table names
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """
        cursor.execute(query)
        tables = [row[0] for row in cursor.fetchall()]
        
        all_data = {}
        
        for table in tables:
            cursor.execute(f"SELECT * FROM {table} ORDER BY 1 LIMIT 1000;")
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            # Convert rows to dictionaries and serialize non-JSON values
            data = []
            for row in rows:
                row_dict = {}
                for col, val in zip(columns, row):
                    row_dict[col] = serialize_value(val)
                data.append(row_dict)
            all_data[table] = {
                'columns': columns,
                'rows': data,
                'count': len(data)
            }
        
        cursor.close()
        return jsonify(all_data)
        
    except Exception as e:
        print(f'Error fetching all data: {str(e)}')
        return jsonify({'error': str(e)}), 500
    finally:
        release_db_connection(conn)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3001))
    print(f'🚀 Server running on http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, debug=True)

