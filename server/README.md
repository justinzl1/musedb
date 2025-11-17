# MuseDB Backend Server

Python Flask backend server for the MuseDB web application.

## Setup

1. **Create and activate virtual environment**:
   ```bash
   ./setup.sh
   ```
   
   Or manually:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Running the Server

**Make sure your `.env` file is in the project root** (`../.env`), not in the server directory.

1. **Activate virtual environment** (if not already activated):
   ```bash
   source venv/bin/activate
   ```

2. **Run the server**:
   ```bash
   python3 app.py
   ```
   
   Or use the run script:
   ```bash
   ./run.sh
   ```

The server will start on `http://localhost:3001`

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/tables` - Get all table names
- `GET /api/tables/<table_name>` - Get data from a specific table
- `GET /api/all-data` - Get all data from all tables

## Environment Variables

The server reads from `.env` in the project root:
- `DB_HOST` - Database host
- `DB_PORT` - Database port (default: 5432)
- `DB_NAME` - Database name
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password
- `PORT` - Server port (default: 3001)

