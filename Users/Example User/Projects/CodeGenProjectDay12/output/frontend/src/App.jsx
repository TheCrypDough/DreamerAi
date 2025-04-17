import React, { useState } from 'react';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';

function App() {
  // State for the counter value, initialized to 0
  const [count, setCount] = useState(0);

  // Function to handle incrementing the counter
  const handleIncrement = () => {
    setCount(prevCount => prevCount + 1);
  };

  // Function to handle decrementing the counter
  const handleDecrement = () => {
    setCount(prevCount => prevCount - 1);
  };

  return (
    <Container maxWidth="sm" sx={{ textAlign: 'center', mt: 5 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        Simple Counter App
      </Typography>

      <Typography variant="h1" component="div" sx={{ my: 4 }}>
        {count}
      </Typography>

      <Box sx={{ '& button': { m: 1 } }}> {/* Adds margin around buttons */}
        <Button
          variant="contained"
          color="secondary"
          onClick={handleDecrement}
          aria-label="Decrement count"
        >
          Decrement (-)
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={handleIncrement}
          aria-label="Increment count"
        >
          Increment (+)
        </Button>
      </Box>

      {/* Placeholder for future extension point display */}
      {/* <Box sx={{ mt: 5 }}>
        <Typography variant="caption" display="block" gutterBottom>
          Future Backend Integration Area
        </Typography>
      </Box> */}
    </Container>
  );
}

export default App;