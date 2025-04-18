import React, { useState, useEffect } from 'react';
import { Typography, Container, CircularProgress, Alert } from '@mui/material';

function App() {
  const [apiStatus, setApiStatus] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Basic fetch example to interact with the described backend endpoint
  useEffect(() => {
    // Assuming the backend runs on http://localhost:8000 (default FastAPI port)
    // Adjust the URL if your backend runs elsewhere
    fetch('http://localhost:8000/')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        setApiStatus(data.message || 'No message received');
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch API status:", err);
        setError(`Failed to connect to API: ${err.message}`);
        setLoading(false);
      });
  }, []); // Empty dependency array means this runs once on mount

  return (
    <Container maxWidth="sm" style={{ marginTop: '2rem' }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Basic API Server Frontend
      </Typography>

      <Typography variant="body1" paragraph>
        This frontend interacts with the minimal FastAPI backend.
      </Typography>

      <Typography variant="h6" component="h2">
        Core Feature: API Status
      </Typography>

      {loading && <CircularProgress />}

      {error && <Alert severity="error">{error}</Alert>}

      {!loading && !error && (
        <Alert severity="success">
          API Status: {apiStatus}
        </Alert>
      )}

    </Container>
  );
}

export default App;