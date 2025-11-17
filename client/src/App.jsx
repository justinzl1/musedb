import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [tableData, setTableData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTables();
  }, []);

  const fetchTables = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/tables');
      if (!response.ok) throw new Error('Failed to fetch tables');
      const data = await response.json();
      setTables(data);
      if (data.length > 0) {
        setSelectedTable(data[0]);
        fetchTableData(data[0]);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchTableData = async (tableName) => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`/api/tables/${tableName}`);
      if (!response.ok) throw new Error(`Failed to fetch data from ${tableName}`);
      const data = await response.json();
      setTableData(data);
      setSelectedTable(tableName);
    } catch (err) {
      setError(err.message);
      setTableData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleTableSelect = (tableName) => {
    fetchTableData(tableName);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎵 MuseDB Database Viewer</h1>
        <p>Explore your music database</p>
      </header>

      <div className="app-container">
        <aside className="sidebar">
          <h2>Tables</h2>
          {loading && !tableData && <div className="loading">Loading tables...</div>}
          {error && <div className="error">Error: {error}</div>}
          <ul className="table-list">
            {tables.map((table) => (
              <li
                key={table}
                className={selectedTable === table ? 'active' : ''}
                onClick={() => handleTableSelect(table)}
              >
                {table}
              </li>
            ))}
          </ul>
        </aside>

        <main className="main-content">
          {loading && tableData && (
            <div className="loading-overlay">
              <div className="loading">Loading data...</div>
            </div>
          )}
          
          {error && tableData === null && (
            <div className="error-message">
              <h3>Error</h3>
              <p>{error}</p>
              <button onClick={() => fetchTables()}>Retry</button>
            </div>
          )}

          {tableData && !error && (
            <div className="table-viewer">
              <h2>{selectedTable}</h2>
              <div className="table-info">
                <span>{tableData.count} rows</span>
                {tableData.count >= 1000 && (
                  <span className="warning">(showing first 1000 rows)</span>
                )}
              </div>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      {tableData.columns.map((column) => (
                        <th key={column}>{column}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {tableData.rows.length === 0 ? (
                      <tr>
                        <td colSpan={tableData.columns.length} className="empty">
                          No data found
                        </td>
                      </tr>
                    ) : (
                      tableData.rows.map((row, idx) => (
                        <tr key={idx}>
                          {tableData.columns.map((column) => (
                            <td key={column}>
                              {row[column] !== null && row[column] !== undefined
                                ? String(row[column])
                                : <span className="null-value">NULL</span>}
                            </td>
                          ))}
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {!tableData && !loading && !error && (
            <div className="empty-state">
              <p>Select a table to view its data</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;

