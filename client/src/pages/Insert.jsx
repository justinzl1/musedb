import React, { useState, useEffect } from 'react';
import '../App.css';

function Insert() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState('');
  const [columns, setColumns] = useState([]);
  const [formData, setFormData] = useState({});
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
      setFormData({});
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
      // First get column info to check for identity columns
      const response = await fetch(`/api/tables/${tableName}`);
      if (!response.ok) throw new Error('Failed to fetch columns');
      const data = await response.json();
      
      // Get column metadata to identify identity columns
      const metaResponse = await fetch(`/api/tables/${tableName}/columns`);
      let identityColumns = [];
      if (metaResponse.ok) {
        const metaData = await metaResponse.json();
        identityColumns = metaData.filter(col => col.is_identity).map(col => col.column_name);
      }
      
      // Filter out identity columns from the form
      const editableColumns = data.columns.filter(col => !identityColumns.includes(col));
      setColumns(editableColumns);
      
      // Initialize form data with empty values for editable columns only
      const initialData = {};
      editableColumns.forEach((col) => {
        initialData[col] = '';
      });
      setFormData(initialData);
      setError(null);
      setSuccess(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (column, value) => {
    setFormData((prev) => ({
      ...prev,
      [column]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedTable) {
      setError('Please select a table');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      // Prepare data - convert empty strings to null for optional fields
      const insertData = {};
      columns.forEach((col) => {
        const value = formData[col];
        insertData[col] = value === '' ? null : value;
      });

      const response = await fetch('/api/insert', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          table: selectedTable,
          data: insertData,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Insert failed');
      }

      const result = await response.json();
      setSuccess(`Successfully inserted record into ${selectedTable}`);
      
      // Reset form
      const resetData = {};
      columns.forEach((col) => {
        resetData[col] = '';
      });
      setFormData(resetData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <main className="main-content" style={{ maxWidth: '100%' }}>
        <h2>Insert Data</h2>
        
        <form onSubmit={handleSubmit} className="insert-form">
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
            <div className="form-fields">
              <h3>Enter Data:</h3>
              <p style={{ color: '#666', fontSize: '0.9em', marginBottom: '15px' }}>
                Note: Auto-generated columns (like IDs) are excluded and will be created automatically.
              </p>
              {columns.map((column) => (
                <div key={column} className="form-group">
                  <label htmlFor={`field-${column}`}>
                    {column}:
                  </label>
                  <input
                    id={`field-${column}`}
                    type="text"
                    value={formData[column] || ''}
                    onChange={(e) => handleInputChange(column, e.target.value)}
                    placeholder={`Enter ${column} (leave empty for NULL)`}
                  />
                </div>
              ))}
            </div>
          )}

          <button type="submit" className="submit-button" disabled={loading || !selectedTable}>
            {loading ? 'Inserting...' : 'Insert Record'}
          </button>
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
      </main>
    </div>
  );
}

export default Insert;

