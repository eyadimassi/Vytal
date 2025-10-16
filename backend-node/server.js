// backend-node/server.js

const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
const PORT = 8080;

app.use(cors());
app.use(express.json());

const PYTHON_API_URL = 'http://backend-python:5000/chat';


app.post('/api/chat', async (req, res) => {
  try {
    console.log('Received request from frontend:', req.body.message);
    console.log('Forwarding request to Python service at:', PYTHON_API_URL);

    const response = await axios.post(PYTHON_API_URL, {
      message: req.body.message,
      chat_history: req.body.chat_history || [],
    });

    console.log('Successfully received response from Python service.');
    res.json(response.data);

  } catch (error) {
    
    console.error('--- FAILED TO PROXY REQUEST TO PYTHON SERVICE ---');
    if (error.response) {
      
      console.error('Python service responded with an error status.');
      console.error('Status:', error.response.status);
      console.error('Data:', error.response.data);
    } else if (error.request) {
      
      console.error('No response was received from the Python service.');
      console.error('This often means the service name is wrong or the container is not running/reachable.');
      console.error('Error Code:', error.code); 
    } else {
      
      console.error('An error occurred while setting up the request:', error.message);
    }
    console.error('-------------------------------------------------');
    res.status(500).json({ error: 'Failed to get response from AI service.' });
  }
});

app.listen(PORT, () => {
  console.log(`Node.js backend server is running on http://localhost:${PORT}`);
});