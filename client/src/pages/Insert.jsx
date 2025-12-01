import React, { useState } from 'react';
import '../App.css';

function Insert() {
  const [songName, setSongName] = useState('');
  const [artistName, setArtistName] = useState('');
  const [albumName, setAlbumName] = useState('');
  const [albumReleaseDate, setAlbumReleaseDate] = useState('');
  const [albumDescription, setAlbumDescription] = useState('');
  const [trackLength, setTrackLength] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!songName.trim() || !artistName.trim() || !albumName.trim()) {
      setError('Song name, artist name, and album name are required');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const response = await fetch('/api/insert/music', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          song_name: songName.trim(),
          artist_name: artistName.trim(),
          album_name: albumName.trim(),
          album_release_date: albumReleaseDate.trim() || null,
          album_description: albumDescription.trim() || null,
          track_length: trackLength.trim() || null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Insert failed');
      }

      const result = await response.json();
      setSuccess('Successfully added song to database');
      
      // Reset form
      setSongName('');
      setArtistName('');
      setAlbumName('');
      setAlbumReleaseDate('');
      setAlbumDescription('');
      setTrackLength('');
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
            <label htmlFor="song-name">Song Name:</label>
            <input
              id="song-name"
              type="text"
              value={songName}
              onChange={(e) => setSongName(e.target.value)}
              placeholder="Enter song name"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="artist-name">Artist Name:</label>
            <input
              id="artist-name"
              type="text"
              value={artistName}
              onChange={(e) => setArtistName(e.target.value)}
              placeholder="Enter artist name"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="album-name">Album Name:</label>
            <input
              id="album-name"
              type="text"
              value={albumName}
              onChange={(e) => setAlbumName(e.target.value)}
              placeholder="Enter album name"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="album-release-date">Album Release Date (optional):</label>
            <input
              id="album-release-date"
              type="text"
              value={albumReleaseDate}
              onChange={(e) => setAlbumReleaseDate(e.target.value)}
              placeholder="YYYY-MM-DD"
            />
          </div>

          <div className="form-group">
            <label htmlFor="album-description">Album Description (optional):</label>
            <input
              id="album-description"
              type="text"
              value={albumDescription}
              onChange={(e) => setAlbumDescription(e.target.value)}
              placeholder="Enter album description"
            />
          </div>

          <div className="form-group">
            <label htmlFor="track-length">Track Length (optional):</label>
            <input
              id="track-length"
              type="text"
              value={trackLength}
              onChange={(e) => setTrackLength(e.target.value)}
              placeholder="HH:MM:SS"
            />
          </div>

          <button type="submit" className="submit-button" disabled={loading}>
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
