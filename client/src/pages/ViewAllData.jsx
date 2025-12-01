import React, { useState, useEffect } from 'react';
import '../App.css';

// View all tracks with their associated artists and albums
function ViewAllData() {
  const [joinedData, setJoinedData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [limit] = useState(15);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    fetchJoinedData(0);
  }, []);

  const fetchJoinedData = async (newOffset) => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`/api/tracks/joined?limit=${limit}&offset=${newOffset}`);
      if (!response.ok) throw new Error('Failed to fetch joined data');
      const data = await response.json();
      
      if (newOffset === 0) {

        setJoinedData(data);
      } else {
        setJoinedData(prev => ({
          ...prev,
          results: [...prev.results, ...data.results],
          has_more: data.has_more,
          offset: data.offset
        }));
      }
      setOffset(newOffset + data.results.length);
    } catch (err) {
      setError(err.message);
      setJoinedData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleShowMore = () => {
    fetchJoinedData(offset);
  };
  // Render joined data view
  return (
    <main className="main-content">
      <h2>Tracks with Artists & Albums</h2>
        <p style={{ color: '#666', marginBottom: '20px' }}>
          View all tracks with their associated artists and album information
        </p>

        {loading && !joinedData && (
          <div className="loading">Loading data...</div>
        )}

        {error && (
          <div className="error-message">
            <h3>Error</h3>
            <p>{error}</p>
            <button onClick={() => fetchJoinedData(0)}>Retry</button>
          </div>
        )}

        {joinedData && !error && (
          <div className="joined-data-viewer">
            <div className="table-info">
              <span>Showing {joinedData.results.length} of {joinedData.total_count} tracks</span>
            </div>

            {joinedData.results.length === 0 ? (
              <div className="empty-state">
                <p>No tracks found</p>
              </div>
            ) : (
              <>
                <div className="joined-results-list">
                  {joinedData.results.map((item, idx) => (
                    <div key={item.track_id || idx} className="joined-result-card">
                      <div className="joined-result-header">
                        <h3 className="joined-track-name">{item.track_name}</h3>
                        {item.track_length && (
                          <span className="joined-track-length">{item.track_length}</span>
                        )}
                      </div>
                      
                      <div className="joined-result-content">
                        <div className="joined-result-section">
                          <span className="joined-section-label">Artist(s):</span>
                          <div className="joined-artists-list">
                            {item.artists && item.artists.length > 0 ? (
                              item.artists.map((artist, artistIdx) => (
                                <span key={artist.artist_id || artistIdx} className="joined-artist-tag">
                                  {artist.name}
                                  {artist.type && <span className="artist-type"> ({artist.type})</span>}
                                </span>
                              ))
                            ) : (
                              <span className="no-data">No artists</span>
                            )}
                          </div>
                        </div>

                        <div className="joined-result-section">
                          <span className="joined-section-label">Album:</span>
                          <div className="joined-album-info">
                            <span className="joined-album-name">{item.album_name || 'Unknown'}</span>
                            {item.album_release_date && (
                              <span className="joined-album-date"> • {item.album_release_date}</span>
                            )}
                            {item.album_description && (
                              <div className="joined-album-description">{item.album_description}</div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {joinedData.has_more && (
                  <div className="show-more-container">
                    <button 
                      onClick={handleShowMore} 
                      className="show-more-button"
                      disabled={loading}
                    >
                      {loading ? 'Loading...' : `Show More (${joinedData.total_count - joinedData.results.length} remaining)`}
                    </button>
                  </div>
                )}

                {!joinedData.has_more && joinedData.results.length > 0 && (
                  <div className="end-message">
                    <p>All {joinedData.total_count} tracks displayed</p>
                  </div>
                )}
              </>
            )}
          </div>
        )}
    </main>
  );
}

export default ViewAllData;
