# MuseDB Backend Server

Python Flask backend server for the MuseDB web application.

## Setup

1. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Running the Server

**Make sure your `.env` file is in the project root** (`../.env`), not in the server directory (this current directory)

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
