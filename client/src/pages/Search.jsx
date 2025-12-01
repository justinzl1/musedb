import React, { useState } from 'react';
import '../App.css';

// Search music page
function Search() {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await fetch('/api/search/music', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery.trim(),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Search failed');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
      setResults(null);
    } finally {
      setLoading(false);
    }
  };
  // Render search form and results
  return (
    <main className="main-content">
      <h2>Search Music</h2>
        <p style={{ color: '#666', marginBottom: '30px' }}>
          Search for songs, artists, or albums. Results will show tracks with their associated artists.
        </p>
        
        <form onSubmit={handleSearch} className="music-search-form">
          <div className="search-bar-container">
            <input
              type="text"
              className="music-search-input"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search for a song, artist, or album..."
              disabled={loading}
            />
            <button type="submit" className="music-search-button" disabled={loading || !searchQuery.trim()}>
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}

        {results && (
          <div className="music-results" style={{ marginTop: '30px' }}>
            <h3>Search Results</h3>
            <div className="table-info">
              <span>{results.length} result(s) found</span>
            </div>
            {results.length > 0 ? (
              <div className="music-results-list">
                {results.map((result, idx) => (
                  <div key={idx} className="music-result-card">
                    <div className="music-result-header">
                      <h4 className="track-name">{result.track_name}</h4>
                      {result.track_length && (
                        <span className="track-length">{result.track_length}</span>
                      )}
                    </div>
                    <div className="music-result-details">
                      <div className="music-result-artists">
                        <span className="detail-label">Artist(s):</span>
                        <span className="detail-value">
                          {result.artists && result.artists.length > 0
                            ? result.artists.join(', ')
                            : 'Unknown'}
                        </span>
                      </div>
                      <div className="music-result-album">
                        <span className="detail-label">Album:</span>
                        <span className="detail-value">
                          {result.album_name || 'Unknown'}
                        </span>
                        {result.album_release_date && (
                          <span className="album-date"> ({result.album_release_date})</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <p>No results found. Try a different search term.</p>
              </div>
            )}
          </div>
        )}
    </main>
  );
}

export default Search;
