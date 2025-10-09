// backend-node/server.js
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const morgan = require('morgan');

const app = express();

// Middleware
app.use(cors()); // Allow requests from our React frontend
app.use(express.json()); // Parse JSON bodies
app.use(morgan('dev')); // Logger for requests

// Define the Python service URL. 'backend-python' is the service name we'll use in Docker Compose.
const PYTHON_API_URL = 'http://backend-python:5000/chat';

// Define the chat route
app.post('/api/chat', async (req, res) => {
    try {
        const { message, chat_history } = req.body;

        console.log('Forwarding request to Python service...');
        const pythonResponse = await axios.post(PYTHON_API_URL, {
            message: message,
            chat_history: chat_history
        });

        console.log('Received response from Python service.');
        res.json(pythonResponse.data);

    } catch (error) {
        console.error('Error calling Python service:', error.message);
        res.status(500).json({ error: 'Failed to get response from AI service.' });
    }
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
    console.log(`Node.js server listening on port ${PORT}`);
});