import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { getDbConnection } from './db.js';
import { getTableData, getTableNames } from './queries.js';

// Configures the environment
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Allows the server to accept JSON request from other places (such as frontend app)
app.use(cors());
app.use(express.json());

// Make's sure the server is running
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Server is running' });
});

// Get the table names
app.get('/api/tables', async (req, res) => {
  let client;
  try {
    client = await getDbConnection();
    const tables = await getTableNames(client);
    res.json(tables);

  } catch (error) {
    console.error('Error fetching table names:', error);
    res.status(500).json({ error: error.message });
  } finally {
    if (client) client.release();
  }
});

// Get data from one table
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

// Get data from all tables
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
    console.error('Error fetching data:', error);
    res.status(500).json({ error: error.message });
  } finally {
    if (client) client.release();
  }
});

app.listen(PORT, () => {
  console.log(`Server running: http://localhost:${PORT}`);
});

