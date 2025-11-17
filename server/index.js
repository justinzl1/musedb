import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { getDbConnection } from './db.js';
import { getTableData, getTableNames } from './queries.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Server is running' });
});

// Get all table names
app.get('/api/tables', async (req, res) => {
  let client;
  try {
    client = await getDbConnection();
    const tables = await getTableNames(client);
    res.json(tables);
  } catch (error) {
    console.error('Error fetching tables:', error);
    res.status(500).json({ error: error.message });
  } finally {
    if (client) client.release();
  }
});

// Get data from a specific table
app.get('/api/tables/:tableName', async (req, res) => {
  let client;
  try {
    const { tableName } = req.params;
    client = await getDbConnection();
    const data = await getTableData(client, tableName);
    res.json(data);
  } catch (error) {
    console.error(`Error fetching data from ${req.params.tableName}:`, error);
    res.status(500).json({ error: error.message });
  } finally {
    if (client) client.release();
  }
});

// Get all data from all tables
app.get('/api/all-data', async (req, res) => {
  let client;
  try {
    client = await getDbConnection();
    const tables = await getTableNames(client);
    const allData = {};
    
    for (const table of tables) {
      allData[table] = await getTableData(client, table);
    }
    
    res.json(allData);
  } catch (error) {
    console.error('Error fetching all data:', error);
    res.status(500).json({ error: error.message });
  } finally {
    if (client) client.release();
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});

