# MuseDB Web App

A web application to view and explore your Supabase PostgreSQL database through a modern, user-friendly interface.

## Features

- 🎨 Modern, responsive UI
- 📊 View all database tables
- 🔍 Browse table data with pagination
- ⚡ Fast and efficient data loading
- 🔒 Secure database connection using environment variables

## Prerequisites

**For Node.js backend:**
- Node.js (v16 or higher)
- npm or yarn

**For Python backend (recommended - simpler!):**
- Python 3.8 or higher
- pip

**Both require:**
- Your Supabase database credentials (already in your `.env` file)

## Setup Instructions

### Option 1: Python Backend (Recommended - Easier!)

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

## Project Structure

```
musedb/
├── server/              # Backend server (Python - recommended)
│   ├── app.py          # Python Flask server
│   ├── requirements.txt # Python dependencies
│   ├── setup.sh        # Setup script for virtual environment
│   ├── run.sh          # Run script for backend
│   ├── venv/           # Python virtual environment (created by setup.sh)
│   ├── index.js        # Node.js Express server (alternative)
│   ├── db.js           # Node.js database connection
│   └── queries.js      # Node.js database query functions
├── client/             # React frontend (completely separate)
│   ├── src/
│   │   ├── App.jsx     # Main React component
│   │   ├── App.css     # Styles
│   │   └── main.jsx    # React entry point
│   └── package.json
├── .env                # Database credentials (in project root)
└── package.json        # Root package.json (for Node.js backend only)
```

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

## Usage

1. Once the app is running, you'll see a list of all tables in the sidebar
2. Click on any table name to view its data
3. The main panel will display the table contents in a formatted table
4. Tables are limited to 1000 rows for performance (you can modify this in `server/app.py` for Python or `server/queries.js` for Node.js)

## Troubleshooting

- **Connection errors**: Make sure your `.env` file has the correct Supabase credentials
- **Port already in use**: 
  - Python: Change the port in `server/app.py` (line with `port = int(os.getenv('PORT', 3001))`)
  - Node.js: Change the port in `server/index.js` (line with `const PORT = ...`)
  - Frontend: Change the port in `client/vite.config.js`
- **Module not found (Node.js)**: Run `npm run install-all` again
- **Module not found (Python)**: 
  - Make sure you've activated the virtual environment: `source server/venv/bin/activate`
  - Or run `cd server && ./setup.sh` to set up the environment
- **Python not found**: Make sure Python 3.8+ is installed and in your PATH
- **pip install fails**: Use the virtual environment setup script: `cd server && ./setup.sh`

## Production Deployment

For production deployment:

1. Build the frontend:
   ```bash
   npm run build
   ```

2. The built files will be in `client/dist/`

3. **Python backend**: You can use gunicorn or uwsgi to serve the Flask app:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:3001 server.app:app
   ```

4. **Node.js backend**: Use PM2 or similar process manager:
   ```bash
   npm install -g pm2
   pm2 start server/index.js
   ```

5. You can also deploy to services like Heroku, Railway, or Render.

