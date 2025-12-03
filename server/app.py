from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta, date, datetime
import json

# Loads in the environment variables (from .env)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Create sthe Flask App and enable CORS
app = Flask(__name__)
CORS(app)

# Initialize the connection variable
connection_pool = None

def serialize_value(value):
    """Convert non-JSON values to JSON formats that we can use for our table"""
    if value is None:
        return None
    # Converts the time to HH:MM:SS format
    elif isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    # Converts to ISO format string
    elif isinstance(value, (date, datetime)):
        return value.isoformat()
    # Decodes bytes
    elif isinstance(value, (bytes, bytearray)):
        return value.decode('utf-8', errors='ignore')
    # Good type
    else:
        return value

def get_db_connection():
    """Creates and gets the database connection (based on the pool connection -- from db.js)"""
    global connection_pool
    
    if connection_pool is None:
        # Makes sure that all the required environment variables are set
        required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            raise ValueError(f'Required Environment variables missing!')
        
        try:
            # Create the connection
            db_host = os.getenv('DB_HOST')
            db_port = int(os.getenv('DB_PORT', 5432))
            db_name = os.getenv('DB_NAME')
            db_user = os.getenv('DB_USER')
            db_password = os.getenv('DB_PASSWORD')
            
            # Connection string for supabase
            conn_string = (
                f"host={db_host} "
                f"port={db_port} "
                f"dbname={db_name} "
                f"user={db_user} "
                f"password={db_password} "
                f"sslmode=require"
            )
            
            # Tries to create the connection
            connection_pool = psycopg2.pool.SimpleConnectionPool(1, 20, conn_string)
        except Exception as e:
        # If there is an error, print it and describe why
            raise ConnectionError(f'Failed to create connection pool: {str(e)}')    
    return connection_pool.getconn()

def release_db_connection(conn):
    """Release the database connection"""
    if connection_pool and conn:
        connection_pool.putconn(conn)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Makes sure that the server is running"""
    return jsonify({'status': 'ok', 'message': 'Server is running'})

@app.route('/api/tables', methods=['GET'])
def get_tables():
    """Makes sure that one can get all table names from the database"""
    conn = None
    try:
        # Get the connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query to get all table names
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
        # Returns list of tables
        return jsonify(tables)
        
    except Exception as e:
        # If there is an error, print it and return Error 500
        print(f'Error fetching tables!')
        return jsonify({'error': str(e)}), 500
    finally:
        # Kills DB Connection
        release_db_connection(conn)

@app.route('/api/tracks/joined', methods=['GET'])
def get_tracks_joined():
    """Get tracks with their associated artists and albums"""
    conn = None
    try:
        # Get limit and offset from query parameters
        limit = request.args.get('limit', type=int, default=15)
        offset = request.args.get('offset', type=int, default=0)
        
        # Get the connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total count
        count_query = "SELECT COUNT(DISTINCT t.track_id) FROM Track t;"
        cursor.execute(count_query)
        total_count = cursor.fetchone()[0]
        
        # Get tracks with their albums and artists - SQL Query
        query = """
            SELECT DISTINCT
                t.track_id,
                t.name AS track_name,
                t.length AS track_length,
                a.album_id,
                a.name AS album_name,
                a.release_date AS album_release_date,
                a.description AS album_description
            FROM Track t
            INNER JOIN Album a ON t.album_id = a.album_id
            ORDER BY t.track_id
            LIMIT %s OFFSET %s;
        """
        
        # Execute the main query and gets the output
        cursor.execute(query, (limit, offset))
        tracks = cursor.fetchall()
        
        # Get all associated artists
        results = []
        for track in tracks:
            track_id = track[0]
            
            # Get all artists for this track - SQL Query
            artist_query = """
                SELECT ar.artist_id, ar.name, ar.type, ar.description
                FROM Artist ar
                INNER JOIN ArtistTrack at ON ar.artist_id = at.artist_id
                WHERE at.track_id = %s
                ORDER BY ar.name;
            """
            cursor.execute(artist_query, (track_id,))
            artists = cursor.fetchall()
            
            # Formats the artists
            artist_list = []
            for artist in artists:
                artist_list.append({
                    'artist_id': artist[0],
                    'name': artist[1],
                    'type': artist[2],
                    'description': artist[3]
                })
            
            # Get album artists - SQL Query
            album_artist_query = """
                SELECT ar.artist_id, ar.name, ar.type, ar.description
                FROM Artist ar
                INNER JOIN ArtistAlbum aa ON ar.artist_id = aa.artist_id
                WHERE aa.album_id = %s
                ORDER BY ar.name;
            """
            cursor.execute(album_artist_query, (track[3],))
            album_artists = cursor.fetchall()
            
            # Combine track artists and album artists
            all_artists = {artist[0]: {
                'artist_id': artist[0],
                'name': artist[1],
                'type': artist[2],
                'description': artist[3]
            } for artist in artists}
            
            # Add album artists, avoiding duplicates
            for artist in album_artists:
                if artist[0] not in all_artists:
                    all_artists[artist[0]] = {
                        'artist_id': artist[0],
                        'name': artist[1],
                        'type': artist[2],
                        'description': artist[3]
                    }
            
            # Append the track with this info
            results.append({
                'track_id': track_id,
                'track_name': track[1],
                'track_length': serialize_value(track[2]),
                'album_id': track[3],
                'album_name': track[4],
                'album_release_date': serialize_value(track[5]) if track[5] else None,
                'album_description': track[6],
                'artists': list(all_artists.values())
            })
        
        cursor.close()
        
        # Return the results with the info
        return jsonify({
            'results': results,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count
        })
        
    except Exception as e:
        # If there is an error, print it and return Error 500
        print(f'Error fetching joined tracks!')
        return jsonify({'error': str(e)}), 500
    finally:
        # Kills DB Connection
        release_db_connection(conn)

@app.route('/api/tables/<table_name>', methods=['GET'])
def get_table_data(table_name):
    """Get data from a specific table -- based on the table name"""
    conn = None
    try:
        # Sanitize table name so there is no SQL injection
        sanitized_table_name = ''.join(c for c in table_name if c.isalnum() or c == '_')
        
        if not sanitized_table_name:
            return jsonify({'error': 'Invalid table name'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get data from the table - SQL Query
        query = f"SELECT * FROM {sanitized_table_name} ORDER BY 1 LIMIT 1000;"
        cursor.execute(query)
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        # Convert rows to dictionaries and to JSON values
        data = []
        for row in rows:
            row_dict = {}
            for col, val in zip(columns, row):
                row_dict[col] = serialize_value(val)
            data.append(row_dict)
        
        cursor.close()

        # Return the data
        return jsonify({
            'columns': columns,
            'rows': data,
            'count': len(data)
        })
        
    except Exception as e:
        # If there is an error, print it and return Error 500
        print(f'Error fetching data from {table_name}!')
        return jsonify({'error': str(e)}), 500
    finally:
        # Kills DB Connection
        release_db_connection(conn)

@app.route('/api/tables/<table_name>/columns', methods=['GET'])
def get_table_columns(table_name):
    """Get column information for a specific table"""
    conn = None
    try:
        # Sanitize table name so there is no SQL injection
        sanitized_table_name = ''.join(c for c in table_name if c.isalnum() or c == '_')
        
        # If not sanitized, returns  400
        if not sanitized_table_name:
            return jsonify({'error': 'Invalid table name'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get column information - SQL Query
        query = """
            SELECT 
                column_name,
                data_type,
                is_nullable,
                CASE WHEN is_identity = 'YES' THEN true ELSE false END as is_identity
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = 'public'
            ORDER BY ordinal_position;
        """
        cursor.execute(query, (sanitized_table_name,))
        
        # Formats the columns
        columns = []
        for row in cursor.fetchall():
            columns.append({
                'column_name': row[0],
                'data_type': row[1],
                'is_nullable': row[2] == 'YES',
                'is_identity': row[3]
            })
        
        cursor.close()

        # Return the columns
        return jsonify(columns)
        
    except Exception as e:
        # If there is an error, print it and return Error 500
        print(f'Error fetching columns from {table_name}!')
        return jsonify({'error': str(e)}), 500
    finally:
        # Kills DB Connection
        release_db_connection(conn)

@app.route('/api/all-data', methods=['GET'])
def get_all_data():
    """Get all data from all tables within the database """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all table names - SQL Query
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """
        cursor.execute(query)

        # Stores all table names
        tables = [row[0] for row in cursor.fetchall()]
        
        all_data = {}
        
        # For each table, get the data
        for table in tables:
            # Get data from the table - SQL Query
            cursor.execute(f"SELECT * FROM {table} ORDER BY 1 LIMIT 1000;")
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            # Convert rows to dictionaries and stores JSON values
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

        # Return all data
        return jsonify(all_data)
        
    except Exception as e:
        # If there is an error, print it and return Error 500
        print(f'Error fetching all data!')
        return jsonify({'error': str(e)}), 500
    finally:
        # Kills DB Connection
        release_db_connection(conn)

@app.route('/api/search', methods=['POST'])
def search_data():
    """Search for records in a table based on the column value"""
    conn = None
    try:
        # Get the JSON data from the request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get table, column, and search value
        table_name = data.get('table')
        column_name = data.get('column')
        search_value = data.get('value')
        
        if not all([table_name, column_name, search_value]):
            return jsonify({'error': 'Missing required fields: table, column, value'}), 400
        
        # Makes sure to sanitize table and column names for no SQL injection
        sanitized_table = ''.join(c for c in table_name if c.isalnum() or c == '_')
        sanitized_column = ''.join(c for c in column_name if c.isalnum() or c == '_')
        
        if not sanitized_table or not sanitized_column:
            return jsonify({'error': 'Invalid table or column name'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Make sure to use parameterized query to prevent SQL injection - SQL Query
        query = f'SELECT * FROM {sanitized_table} WHERE {sanitized_column}::text ILIKE %s ORDER BY 1;'
        cursor.execute(query, (f'%{search_value}%',))
        
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        # Convert rows to dictionaries and changes to JSON values
        data_list = []
        for row in rows:
            row_dict = {}
            for col, val in zip(columns, row):
                row_dict[col] = serialize_value(val)
            data_list.append(row_dict)
        
        cursor.close()
        
        # Return the search results
        return jsonify({
            'columns': columns,
            'rows': data_list,
            'count': len(data_list)
        })
        
    except Exception as e:
        # If there is an error, print it and return Error 500
        print(f'Error searching data!')
        return jsonify({'error': str(e)}), 500
    finally:
        # Kills DB Connection
        release_db_connection(conn)

@app.route('/api/search/music', methods=['POST'])
def search_music():
    """Search for music across tracks, artists, and albums using a query"""
    conn = None
    try:
        # Get the JSON data from the request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get the search query
        search_query = data.get('query')
        if not search_query:
            return jsonify({'error': 'Missing search query'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Search across tracks, artists, and albums - SQL Query
        query = """
            SELECT DISTINCT
                t.track_id,
                t.name AS track_name,
                t.length AS track_length,
                a.album_id,
                a.name AS album_name,
                a.release_date AS album_release_date
            FROM Track t
            INNER JOIN Album a ON t.album_id = a.album_id
            LEFT JOIN ArtistTrack at ON t.track_id = at.track_id
            LEFT JOIN Artist ar ON at.artist_id = ar.artist_id
            WHERE 
                t.name ILIKE %s
                OR ar.name ILIKE %s
                OR a.name ILIKE %s
            ORDER BY t.name, a.name;
        """
        
        search_pattern = f'%{search_query}%'
        cursor.execute(query, (search_pattern, search_pattern, search_pattern))
        
        tracks = cursor.fetchall()
        
        # Group tracks and collect all artists for each track
        results = []
        track_artists_map = {}
        
        # First collects track info
        for track in tracks:
            track_id = track[0]
            if track_id not in track_artists_map:
                track_artists_map[track_id] = {
                    'track_id': track_id,
                    'track_name': track[1],
                    'track_length': serialize_value(track[2]),
                    'album_id': track[3],
                    'album_name': track[4],
                    'album_release_date': serialize_value(track[5]) if track[5] else None,
                    'artists': []
                }
        
        # Second gets all artists for each track
        for track_id in track_artists_map.keys():
            artist_query = """
                SELECT ar.name
                FROM Artist ar
                INNER JOIN ArtistTrack at ON ar.artist_id = at.artist_id
                WHERE at.track_id = %s
                ORDER BY ar.name;
            """
            cursor.execute(artist_query, (track_id,))
            artists = [row[0] for row in cursor.fetchall()]
            track_artists_map[track_id]['artists'] = artists
        
        # Lists the final results
        results = list(track_artists_map.values())
        
        cursor.close()

        # Return the search results
        return jsonify(results)
        
    except Exception as e:
        # If there is an error, print it and return Error 500
        print(f'Error searching music!')
        return jsonify({'error': str(e)}), 500
    finally:
        # Kills DB Connection
        release_db_connection(conn)

@app.route('/api/insert', methods=['POST'])
def insert_data():
    """Insert a new record into a table"""
    conn = None
    try:
        # Get the JSON data from the request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get table name and data to insert
        table_name = data.get('table')
        insert_data_dict = data.get('data')
        
        if not table_name or not insert_data_dict:
            return jsonify({'error': 'Missing required fields: table, data'}), 400
        
        # Sanitize table name to prevent SQL injection
        sanitized_table = ''.join(c for c in table_name if c.isalnum() or c == '_')
        if not sanitized_table:
            return jsonify({'error': 'Invalid table name'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query to get column info for the table - SQL Query
        cursor.execute(f"""
            SELECT 
                c.column_name, 
                c.data_type,
                CASE WHEN c.is_identity = 'YES' THEN true ELSE false END as is_identity
            FROM information_schema.columns c
            WHERE c.table_name = %s AND c.table_schema = 'public'
            ORDER BY c.ordinal_position;
        """, (sanitized_table,))
        
        # Get column names, types, and identity columns
        table_columns = cursor.fetchall()
        column_names = [col[0] for col in table_columns]
        column_types = {col[0]: col[1] for col in table_columns}
        identity_columns = {col[0] for col in table_columns if col[2]}
        
        # Filter out columns that don't exist
        valid_data = {k: v for k, v in insert_data_dict.items() 
                     if k in column_names and k not in identity_columns}
        
        # Also filter out empty values
        filtered_data = {}
        for k, v in valid_data.items():
            if v is not None and v != '':
                filtered_data[k] = v
        
        if not filtered_data:
            return jsonify({'error': 'No valid data provided'}), 400
        
        # Build INSERT query - SQL Query
        columns = list(filtered_data.keys())
        placeholders = ', '.join(['%s'] * len(columns))
        column_names_str = ', '.join([f'"{col}"' for col in columns])
        
        # Uses parameterized query to prevent SQL injection
        query = f'INSERT INTO {sanitized_table} ({column_names_str}) VALUES ({placeholders}) RETURNING *;'
        
        # Prepare values while doing correct type conversion
        values = []
        for col in columns:
            val = filtered_data[col]
            # Try to convert based on column type
            col_type = column_types.get(col, '').upper()
            if 'INT' in col_type:
                try:
                    values.append(int(val))
                except ValueError:
                    return jsonify({'error': f'Invalid integer value for column {col}'}), 400
            elif 'DATE' in col_type:
                values.append(val)
            elif 'INTERVAL' in col_type:
                values.append(val)
            else:
                values.append(str(val))
        
        cursor.execute(query, values)
        result = cursor.fetchone()
        
        # Get the inserted row
        columns_result = [desc[0] for desc in cursor.description]
        inserted_row = {}
        for col, val in zip(columns_result, result):
            inserted_row[col] = serialize_value(val)
        
        conn.commit()
        cursor.close()
        
        # Return the inserted record
        return jsonify({
            'success': True,
            'message': 'Record inserted successfully',
            'data': inserted_row
        })
        
    # If there is an error then rollback; print it and return Error
    except psycopg2.IntegrityError as e:
        conn.rollback()
        return jsonify({'error': f'Database constraint violation: {str(e)}'}), 400
    except Exception as e:
        if conn:
            conn.rollback()
        print(f'Error inserting data!')
        return jsonify({'error': str(e)}), 500
    finally:
        # Kills DB Connection
        release_db_connection(conn)

@app.route('/api/delete', methods=['DELETE'])
def delete_data():
    """Delete records from a table matching a column value"""
    conn = None
    try:
        # Get the JSON data from the request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get table name, column, and value to delete
        table_name = data.get('table')
        column_name = data.get('column')
        delete_value = data.get('value')
        
        if not all([table_name, column_name, delete_value]):
            return jsonify({'error': 'Missing required fields: table, column, value'}), 400
        
        # Sanitize table and column names to prevent SQL injection
        sanitized_table = ''.join(c for c in table_name if c.isalnum() or c == '_')
        sanitized_column = ''.join(c for c in column_name if c.isalnum() or c == '_')
        
        if not sanitized_table or not sanitized_column:
            return jsonify({'error': 'Invalid table or column name'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Use parameterized query for the delete value to prevent SQL injection
        query = f'DELETE FROM {sanitized_table} WHERE {sanitized_column}::text ILIKE %s;'
        cursor.execute(query, (f'%{delete_value}%',))
        
        # Get number of deleted records
        deleted_count = cursor.rowcount
        conn.commit()
        cursor.close()
        
        # Return the result
        return jsonify({
            'success': True,
            'message': f'Deleted {deleted_count} record(s)',
            'deleted_count': deleted_count
        })
    
    # If there is an error then rollback; print it and return Error
    except psycopg2.IntegrityError as e:
        conn.rollback()
        return jsonify({'error': f'Cannot delete due to foreign key constraint: {str(e)}'}), 400
    except Exception as e:
        if conn:
            conn.rollback()
        print(f'Error deleting data!')
        return jsonify({'error': str(e)}), 500
    finally:
        # Kills DB Connection
        release_db_connection(conn)

@app.route('/api/insert/music', methods=['POST'])
def insert_music():
    """Insert a song with artist and album (and will add in the nation and genre if given)"""
    conn = None
    try:
        # Get the JSON data from the request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get the details from the request
        song_name = data.get('song_name')
        artist_name = data.get('artist_name')
        album_name = data.get('album_name')
        album_release_date = data.get('album_release_date')
        album_description = data.get('album_description')
        track_length = data.get('track_length')
        nation_name = data.get('nation_name')
        nation_comment = data.get('nation_comment')
        artist_description = data.get('artist_description')
        genre_name = data.get('genre_name')
        genre_description = data.get('genre_description')
        
        # Make sure all required information is present
        if not all([song_name, artist_name, album_name]):
            return jsonify({'error': 'Song name, artist name, and album name are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Handles Nation if not cucrently within the DB
        nation_id = None
        if nation_name:
            # Sees if the nation already exists
            cursor.execute("SELECT nation_id FROM Nation WHERE name ILIKE %s;", (nation_name,))
            nation_row = cursor.fetchone()
            if nation_row:
                nation_id = nation_row[0]
            else:
                # Adds the new nation in
                cursor.execute(
                    "INSERT INTO Nation (name, comment) VALUES (%s, %s) RETURNING nation_id;",
                    (nation_name, nation_comment)
                )
                nation_id = cursor.fetchone()[0]
        
        # Handles Artist if not currently within the DB
        cursor.execute("SELECT artist_id FROM Artist WHERE name ILIKE %s;", (artist_name,))
        artist_row = cursor.fetchone()
        if artist_row:
            artist_id = artist_row[0]
        else:
            # Create new artist
            if not nation_id:
                # If nation not provided in request, try to find one in DB
                cursor.execute("SELECT nation_id FROM Nation LIMIT 1;")
                nation_row = cursor.fetchone()
                if not nation_row:
                    return jsonify({'error': 'No nation found in database and none provided. Please add a nation.'}), 400
                nation_id = nation_row[0]
            
            # Insert
            cursor.execute(
                "INSERT INTO Artist (name, description, nation_id) VALUES (%s, %s, %s) RETURNING artist_id;",
                (artist_name, artist_description, nation_id)
            )
            artist_id = cursor.fetchone()[0]
            
        # Handles Genre if not cucrently within the DB
        if genre_name:
            # Tries to select the Genre
            cursor.execute("SELECT genre_id FROM Genre WHERE name ILIKE %s;", (genre_name,))
            genre_row = cursor.fetchone()
            if genre_row:
                genre_id = genre_row[0]
            else:
                # If not in the DB, then insert it in
                cursor.execute(
                    "INSERT INTO Genre (name, description) VALUES (%s, %s) RETURNING genre_id;",
                    (genre_name, genre_description)
                )
                genre_id = cursor.fetchone()[0]
            
            cursor.execute(
                "SELECT 1 FROM ArtistGenre WHERE artist_id = %s AND genre_id = %s;",
                (artist_id, genre_id)
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO ArtistGenre (artist_id, genre_id) VALUES (%s, %s);",
                    (artist_id, genre_id)
                )
        
        # Handles Album if not cucrently within the DB -- Tries to get the Album
        cursor.execute("SELECT album_id FROM Album WHERE name ILIKE %s;", (album_name,))
        album_row = cursor.fetchone()
        if album_row:
            album_id = album_row[0]
        else:
            # If the album is not there, then add it in
            cursor.execute(
                "INSERT INTO Album (name, release_date, description) VALUES (%s, %s, %s) RETURNING album_id;",
                (album_name, album_release_date if album_release_date else None, album_description if album_description else None)
            )
            album_id = cursor.fetchone()[0]
        
        # Link artist to album
        cursor.execute(
            "SELECT 1 FROM ArtistAlbum WHERE artist_id = %s AND album_id = %s;",
            (artist_id, album_id)
        )
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO ArtistAlbum (artist_id, album_id) VALUES (%s, %s);",
                (artist_id, album_id)
            )
        
        # Check if track already exists in the album, if not then add
        cursor.execute(
            "SELECT track_id FROM Track WHERE name ILIKE %s AND album_id = %s;",
            (song_name, album_id)
        )
        track_row = cursor.fetchone()
        
        if track_row:
            track_id = track_row[0]
            message = 'Song already exists in album'
        else:
            # Create track and then adds to the DB
            cursor.execute(
                "INSERT INTO Track (name, length, album_id) VALUES (%s, %s, %s) RETURNING track_id;",
                (song_name, track_length if track_length else None, album_id)
            )
            track_id = cursor.fetchone()[0]
            message = 'Song inserted successfully'
        
        # Link artist to track
        cursor.execute(
            "SELECT 1 FROM ArtistTrack WHERE artist_id = %s AND track_id = %s;",
            (artist_id, track_id)
        )
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO ArtistTrack (artist_id, track_id) VALUES (%s, %s);",
                (artist_id, track_id)
            )
        
        conn.commit()
        cursor.close()
        
        # Return the Json data
        return jsonify({
            'success': True,
            'message': message,
            'track_id': track_id
        })
        
    # If there is an error then rollback; print it and return Error
    except psycopg2.IntegrityError as e:
        if conn:
            conn.rollback()
        return jsonify({'error': f'Database constraint violation: {str(e)}'}), 400
    except Exception as e:
        if conn:
            conn.rollback()
        print(f'Error inserting music!')
        return jsonify({'error': str(e)}), 500
    finally:
        # Kills DB Connection
        release_db_connection(conn)

@app.route('/api/delete/preview', methods=['POST'])
def delete_preview():
    """Preview what will be deleted so that the user knows the impact"""
    conn = None
    try:
        # Get the JSON data from the request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get delete type and value
        delete_type = data.get('type')
        delete_value = data.get('value')
        
        if not all([delete_type, delete_value]):
            return jsonify({'error': 'Missing type or value'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Depending on delete type, prepare the preview - SQL Queries
        if delete_type == 'song':
            # Get song and count affected records
            query = "SELECT * FROM Track WHERE name ILIKE %s;"
            cursor.execute(query, (f'%{delete_value}%',))
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            # Count affected
            affected_count = len(rows)
            
        elif delete_type == 'artist':
            # Get artist and count all related records
            cursor.execute("SELECT artist_id FROM Artist WHERE name ILIKE %s;", (f'%{delete_value}%',))
            artists = cursor.fetchall()
            if not artists:
                return jsonify({
                    'columns': [],
                    'rows': [],
                    'affected_count': 0
                })
            
            artist_ids = [a[0] for a in artists]
            
            # Count tracks associated with this artist
            cursor.execute(
                "SELECT COUNT(DISTINCT t.track_id) FROM Track t INNER JOIN ArtistTrack at ON t.track_id = at.track_id WHERE at.artist_id = ANY(%s);",
                (artist_ids,)
            )
            track_count = cursor.fetchone()[0]
            
            # Count albums associated with this artist
            cursor.execute(
                "SELECT COUNT(DISTINCT a.album_id) FROM Album a INNER JOIN ArtistAlbum aa ON a.album_id = aa.album_id WHERE aa.artist_id = ANY(%s);",
                (artist_ids,)
            )
            album_count = cursor.fetchone()[0]
            
            # Count tracks in those albums
            cursor.execute(
                "SELECT COUNT(*) FROM Track t INNER JOIN Album a ON t.album_id = a.album_id INNER JOIN ArtistAlbum aa ON a.album_id = aa.album_id WHERE aa.artist_id = ANY(%s);",
                (artist_ids,)
            )
            album_track_count = cursor.fetchone()[0]
            
            # Returns the total affected count
            affected_count = len(artists) + album_count + track_count + album_track_count
            
            # Return the data
            query = "SELECT * FROM Artist WHERE name ILIKE %s;"
            cursor.execute(query, (f'%{delete_value}%',))
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
        elif delete_type == 'album':
            # Get album and count related tracks
            cursor.execute("SELECT album_id FROM Album WHERE name ILIKE %s;", (f'%{delete_value}%',))
            albums = cursor.fetchall()
            if not albums:
                return jsonify({
                    'columns': [],
                    'rows': [],
                    'affected_count': 0
                })
            
            album_ids = [a[0] for a in albums]
            
            # Count tracks that will be deleted
            cursor.execute(
                "SELECT COUNT(*) FROM Track WHERE album_id = ANY(%s);",
                (album_ids,)
            )
            track_count = cursor.fetchone()[0]
            
            # Get total affected count
            affected_count = len(albums) + track_count
            
            # Return the data
            query = "SELECT * FROM Album WHERE name ILIKE %s;"
            cursor.execute(query, (f'%{delete_value}%',))
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
        else:
            return jsonify({'error': 'Invalid delete type'}), 400
        
        # Convert rows to dictionaries and to JSON values
        data_list = []
        for row in rows:
            row_dict = {}
            for col, val in zip(columns, row):
                row_dict[col] = serialize_value(val)
            data_list.append(row_dict)
        
        cursor.close()
        
        # Return the data
        return jsonify({
            'columns': columns,
            'rows': data_list,
            'affected_count': affected_count
        })
        
    except Exception as e:
        # If there is an error, print it and return Error 500
        print(f'Error previewing delete!')
        return jsonify({'error': str(e)}), 500
    finally:
        # Kills DB Connection
        release_db_connection(conn)

@app.route('/api/delete/music', methods=['DELETE'])
def delete_music():
    """Delete a song, artist, or album"""
    conn = None
    try:
        # Get the JSON data from the request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Get delete type and value
        delete_type = data.get('type')
        delete_value = data.get('value')
        
        if not all([delete_type, delete_value]):
            return jsonify({'error': 'Missing type or value'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        deleted_count = 0
        
        if delete_type == 'song':
            # Delete the track
            cursor.execute("DELETE FROM Track WHERE name ILIKE %s;", (f'%{delete_value}%',))
            deleted_count = cursor.rowcount
            
        elif delete_type == 'artist':
            # Get the artist IDs
            cursor.execute("SELECT artist_id FROM Artist WHERE name ILIKE %s;", (f'%{delete_value}%',))
            artist_ids = [row[0] for row in cursor.fetchall()]
            
            if artist_ids:
                # Get album IDs from this artist
                cursor.execute(
                    "SELECT DISTINCT album_id FROM ArtistAlbum WHERE artist_id = ANY(%s);",
                    (artist_ids,)
                )
                album_ids = [row[0] for row in cursor.fetchall()]
                
                # Delete all tracks associated with this artist
                if album_ids:
                    cursor.execute(
                        """DELETE FROM Track 
                           WHERE track_id IN (SELECT track_id FROM ArtistTrack WHERE artist_id = ANY(%s))
                           AND album_id NOT IN (SELECT unnest(%s::int[]));""",
                        (artist_ids, album_ids)
                    )
                else:
                    # No albums, so delete all tracks
                    cursor.execute(
                        "DELETE FROM Track WHERE track_id IN (SELECT track_id FROM ArtistTrack WHERE artist_id = ANY(%s));",
                        (artist_ids,)
                    )
                tracks_deleted = cursor.rowcount
                
                # Delete all albums associated with this artist (this will cascade delete tracks in those albums)
                if album_ids:
                    cursor.execute(
                        "DELETE FROM Album WHERE album_id = ANY(%s);",
                        (album_ids,)
                    )
                    albums_deleted = cursor.rowcount
                else:
                    albums_deleted = 0
                
                # Delete the artist and cascade delete the rest
                cursor.execute("DELETE FROM Artist WHERE artist_id = ANY(%s);", (artist_ids,))
                artists_deleted = cursor.rowcount
                
                # Return JSON response
                deleted_count = artists_deleted + albums_deleted + tracks_deleted
            
        elif delete_type == 'album':
            # Delete the album and cascade delete the rest
            cursor.execute("DELETE FROM Album WHERE name ILIKE %s;", (f'%{delete_value}%',))
            deleted_count = cursor.rowcount
        else:
            return jsonify({'error': 'Invalid delete type'}), 400
        
        conn.commit()
        cursor.close()
        
        # Return JSON response
        return jsonify({
            'success': True,
            'message': f'Deleted {deleted_count} record(s)',
            'deleted_count': deleted_count
        })
    
    # If there is a constraint violation, rollback and return Error 400
    except psycopg2.IntegrityError as e:
        if conn:
            conn.rollback()
        return jsonify({'error': f'Cannot delete due to constraint: {str(e)}'}), 400
    except Exception as e:
        if conn:
            conn.rollback()
        print(f'Error deleting music!')
        return jsonify({'error': str(e)}), 500
    finally:
        # Kills DB Connection
        release_db_connection(conn)

if __name__ == '__main__':
    # Starts the server and the connection
    port = int(os.getenv('PORT', 3001))
    print(f'Server running on http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, debug=True)

