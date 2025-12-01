# MuseDB Web App

## Prerequisites

**For Node.js backend:**
- Node.js (v16 or higher)
- npm

**For Python backend:**
- Python 3.8 or higher
- pip

**Both require:**
- Your Supabase database credentials (already in your `.env` file)

## Setup Instructions

### Option 1: Python Backend

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

### Option 2: Node.js Backend

1. **Install dependencies** (run this from the project root):
   ```bash
   npm run install-all
   ```
   This will install dependencies for both the server and client.

2. **Ensure your `.env` file is configured** (same as above)

3. **Start the development servers**:
   ```bash
   npm run dev
   ```
   This will start both the Node.js backend server (port 3001) and frontend dev server (port 3000).

4. **Open your browser**:
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

**Node.js Backend (Alternative):**
- `npm run dev` - Start Node.js backend + React frontend
- `npm run server` - Start only the Node.js backend server
- `npm run install-all` - Install all Node.js dependencies