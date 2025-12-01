import React, { useState, useEffect } from 'react';
import '../App.css';

function Delete() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState('');
  const [columns, setColumns] = useState([]);
  const [deleteColumn, setDeleteColumn] = useState('');
  const [deleteValue, setDeleteValue] = useState('');
  const [previewData, setPreviewData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    fetchTables();
  }, []);

  useEffect(() => {
    if (selectedTable) {
      fetchColumns(selectedTable);
    } else {
      setColumns([]);
      setDeleteColumn('');
      setPreviewData(null);
    }
  }, [selectedTable]);

  const fetchTables = async () => {
    try {
      const response = await fetch('/api/tables');
      if (!response.ok) throw new Error('Failed to fetch tables');
      const data = await response.json();
      setTables(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const fetchColumns = async (tableName) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/tables/${tableName}`);
      if (!response.ok) throw new Error('Failed to fetch columns');
      const data = await response.json();
      setColumns(data.columns);
      if (data.columns.length > 0) {
        setDeleteColumn(data.columns[0]);
      }
      setPreviewData(null);
      setError(null);
      setSuccess(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePreview = async () => {
    if (!selectedTable || !deleteColumn || !deleteValue.trim()) {
      setError('Please select a table, column, and enter a value');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          table: selectedTable,
          column: deleteColumn,
          value: deleteValue.trim(),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Preview failed');
      }

      const data = await response.json();
      setPreviewData(data);
    } catch (err) {
      setError(err.message);
      setPreviewData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedTable || !deleteColumn || !deleteValue.trim()) {
      setError('Please select a table, column, and enter a value');
      return;
    }

    if (!window.confirm(`Are you sure you want to delete ${previewData?.rows.length || 0} record(s)? This action cannot be undone.`)) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const response = await fetch('/api/delete', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          table: selectedTable,
          column: deleteColumn,
          value: deleteValue.trim(),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Delete failed');
      }

      const result = await response.json();
      setSuccess(`Successfully deleted ${result.deleted_count} record(s) from ${selectedTable}`);
      setPreviewData(null);
      setDeleteValue('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <main className="main-content" style={{ maxWidth: '100%' }}>
        <h2>Delete Data</h2>
        <p style={{ color: '#d32f2f', marginBottom: '20px', fontWeight: '500' }}>
          ⚠️ Warning: This action cannot be undone. Please preview records before deleting.
        </p>
        
        <form onSubmit={(e) => { e.preventDefault(); handlePreview(); }} className="delete-form">
          <div className="form-group">
            <label htmlFor="table-select">Select Table:</label>
            <select
              id="table-select"
              value={selectedTable}
              onChange={(e) => setSelectedTable(e.target.value)}
              required
            >
              <option value="">-- Select a table --</option>
              {tables.map((table) => (
                <option key={table} value={table}>
                  {table}
                </option>
              ))}
            </select>
          </div>

          {selectedTable && columns.length > 0 && (
            <>
              <div className="form-group">
                <label htmlFor="column-select">Delete By Column:</label>
                <select
                  id="column-select"
                  value={deleteColumn}
                  onChange={(e) => setDeleteColumn(e.target.value)}
                  required
                >
                  {columns.map((column) => (
                    <option key={column} value={column}>
                      {column}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="delete-value">Value to Match:</label>
                <input
                  id="delete-value"
                  type="text"
                  value={deleteValue}
                  onChange={(e) => setDeleteValue(e.target.value)}
                  placeholder="Enter value to match..."
                  required
                />
              </div>
            </>
          )}

          <div className="button-group">
            <button type="button" onClick={handlePreview} className="preview-button" disabled={loading || !selectedTable}>
              {loading ? 'Loading...' : 'Preview Records'}
            </button>
          </div>
        </form>

        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}

        {success && (
          <div className="success-message">
            <p>{success}</p>
          </div>
        )}

        {previewData && (
          <div className="table-viewer" style={{ marginTop: '30px' }}>
            <h3>Records to be Deleted ({previewData.rows.length})</h3>
            {previewData.rows.length > 0 ? (
              <>
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        {previewData.columns.map((column) => (
                          <th key={column}>{column}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {previewData.rows.map((row, idx) => (
                        <tr key={idx}>
                          {previewData.columns.map((column) => (
                            <td key={column}>
                              {row[column] !== null && row[column] !== undefined
                                ? String(row[column])
                                : <span className="null-value">NULL</span>}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <button onClick={handleDelete} className="delete-button" disabled={loading}>
                  {loading ? 'Deleting...' : `Delete ${previewData.rows.length} Record(s)`}
                </button>
              </>
            ) : (
              <div className="empty-state">
                <p>No records found matching the criteria</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default Delete;

