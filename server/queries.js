// This returns the names of all tables
export async function getTableNames(client) {
  const query = `
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    ORDER BY table_name;
  `;
  
  const result = await client.query(query);
  return result.rows.map(row => row.table_name);
}

// This returns the table's data: columns, rows, and count
export async function getTableData(client, tableName) {

  // Used to prevent SQL injection
  const sanitizedTableName = tableName.replace(/[^a-zA-Z0-9_]/g, '');
  
  if (!sanitizedTableName) {
    throw new Error('Invalid table name');
  }

  const query = `SELECT * FROM ${sanitizedTableName} ORDER BY 1 LIMIT 1000;`;
  const result = await client.query(query);
  
  return {
    columns: result.fields.map(field => field.name),
    rows: result.rows,
    count: result.rows.length
  };
}

