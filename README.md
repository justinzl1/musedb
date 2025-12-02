# MuseDB Web App

## Prerequisites

**For Node.js frontend:**
- Node.js (v16 or higher)
- npm

**For Python backend:**
- Python 3.8 or higher
- pip

**Both require:**
- Your Supabase database credentials (our team will assist you with this)

## Setup Instructions

### Python Backend

**Backend Setup (Run separately):**

1. **Navigate to server directory and set up virtual environment**:
   ```bash
   cd server
   ./setup.sh
   ```
   Or manually:
   ```bash
   cd server
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Ensure your `.env` file is configured** in the project root:
   Make sure you have a `.env` file in the root directory (`musedb/.env`) with your database credentials:
   ```
   DB_HOST=your_supabase_host
   DB_PORT=5432
   DB_NAME=postgres
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```

3. **Run the backend server**:
   ```bash
   # From the server directory
   source venv/bin/activate
   python3 app.py
   ```
   Or use the run script:
   ```bash
   ./run.sh
   ```
   The backend will run on `http://localhost:3001`

**Frontend Setup (Run separately):**

1. **Install frontend dependencies** (from project root):
   ```bash
   cd client
   npm install
   ```

2. **Run the frontend**:
   ```bash
   npm run dev
   ```
   The frontend will run on `http://localhost:3000`

3. **Open your browser**:
   Navigate to `http://localhost:3000` to view the web app.

## Available Scripts

**Python Backend (Recommended):**
- `cd server && ./setup.sh` - Set up virtual environment and install dependencies
- `cd server && source venv/bin/activate && python3 app.py` - Run backend server
- `cd server && ./run.sh` - Run backend server (shortcut)

**Frontend:**
- `cd client && npm install` - Install frontend dependencies
- `cd client && npm run dev` - Start frontend dev server
- `cd client && npm run build` - Build for production