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
NOTE: For best results on Windows, please use WSL to test connection with the bash scripts.
### Python Backend

**Backend Setup (Run separately):**

1. **Navigate to server directory and set up virtual environment**:
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

3. **Run the backend server with python environment**:
   ```bash
   python3 app.py
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