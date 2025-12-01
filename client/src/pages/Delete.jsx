import React, { useState } from 'react';
import '../App.css';

// Delete song or artist or album page
function Delete() {
  const [deleteType, setDeleteType] = useState('song');
  const [deleteValue, setDeleteValue] = useState('');
  const [previewData, setPreviewData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  // Preview records to be deleted
  const handlePreview = async () => {
    if (!deleteValue.trim()) {
      setError('Please enter a name to search for');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await fetch('/api/delete/preview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: deleteType,
          value: deleteValue.trim(),
        }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Preview failed');
      }
      // Get preview data
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
    if (!deleteValue.trim()) {
      setError('Please enter a name to delete');
      return;
    }

    if (!previewData) {
      setError('Please preview records first');
      return;
    }

    // Check if this is a cascading delete (artist or album with multiple entries)
    const isCascading = (deleteType === 'artist' || deleteType === 'album') && previewData.affected_count > 1;
    
    let confirmMessage = '';
    if (isCascading) {
      confirmMessage = `Warning: Deleting this ${deleteType} will also delete ${previewData.affected_count - 1} related record(s) due to cascading deletes. Are you sure you want to proceed?`;
    } else {
      confirmMessage = `Are you sure you want to delete this ${deleteType}? This action cannot be undone.`;
    }

    if (!window.confirm(confirmMessage)) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const response = await fetch('/api/delete/music', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: deleteType,
          value: deleteValue.trim(),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Delete failed');
      }

      const result = await response.json();
      setSuccess(`Successfully deleted ${result.deleted_count} record(s)`);
      setPreviewData(null);
      setDeleteValue('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  // Render delete form and preview table
  return (
    <main className="main-content">
      <h2>Delete Data</h2>
        <p style={{ color: '#d32f2f', marginBottom: '20px' }}>
          Warning: This action cannot be undone. Please preview records before deleting.
        </p>
        
        <form onSubmit={(e) => { e.preventDefault(); handlePreview(); }} className="delete-form">
          <div className="form-group">
            <label htmlFor="delete-type">Delete Type:</label>
            <select
              id="delete-type"
              value={deleteType}
              onChange={(e) => {
                setDeleteType(e.target.value);
                setPreviewData(null);
                setDeleteValue('');
              }}
              required
            >
              <option value="song">Song</option>
              <option value="artist">Artist</option>
              <option value="album">Album</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="delete-value">Name:</label>
            <input
              id="delete-value"
              type="text"
              value={deleteValue}
              onChange={(e) => setDeleteValue(e.target.value)}
              placeholder={`Enter ${deleteType} name...`}
              required
            />
          </div>

          <div className="button-group">
            <button type="button" onClick={handlePreview} className="preview-button" disabled={loading || !deleteValue.trim()}>
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
            <h3>Records to be Deleted</h3>
            {previewData.affected_count > 0 ? (
              <>
                <div className="preview-info">
                  <p>This will delete {previewData.affected_count} record(s).</p>
                  {(deleteType === 'artist' || deleteType === 'album') && previewData.affected_count > 1 && (
                    <p style={{ color: '#d32f2f', fontWeight: 'bold' }}>
                      Warning: This will also delete related records due to cascading deletes.
                    </p>
                  )}
                </div>
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
                  {loading ? 'Deleting...' : 'Delete Record(s)'}
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
  );
}

export default Delete;
