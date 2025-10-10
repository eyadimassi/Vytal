// backend-node/server.js

const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
const PORT = 8080;

// --- Middleware ---
app.use(cors()); // Enable Cross-Origin Resource Sharing
app.use(express.json()); // Parse incoming JSON requests

// --- The URL for our Python AI service ---
// We use the service name 'backend-python' from docker-compose.yml
// Docker's internal DNS will resolve this to the correct container's IP address.
const PYTHON_API_URL = 'http://backend-python:5000/chat';

// --- Routes ---
app.post('/api/chat', async (req, res) => {
  try {
    console.log('Received request from frontend:', req.body.message);

    // Forward the request from the frontend to the Python service
    const response = await axios.post(PYTHON_API_URL, {
      message: req.body.message,
      chat_history: req.body.chat_history || [],
    });

    console.log('Received response from Python service.');

    // Send the Python service's response back to the frontend
    res.json(response.data);

  } catch (error) {
    console.error('Error proxying request to Python service:', error.message);
    res.status(500).json({ error: 'Failed to get response from AI service.' });
  }
});

// --- Start the Server ---
app.listen(PORT, () => {
  console.log(`Node.js backend server is running on http://localhost:${PORT}`);
});