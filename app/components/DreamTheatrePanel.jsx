const React = require('react');
const { useEffect, useState, useRef } = React;
const Box = require('@mui/material/Box').default;
const Typography = require('@mui/material/Typography').default;

const WEBSOCKET_URL = 'ws://localhost:8081'; // Dedicated port for Dream Theatre updates

function DreamTheatrePanel() {
    const [connectionStatus, setConnectionStatus] = useState('Connecting...');
    const [lastMessage, setLastMessage] = useState(null);
    const ws = useRef(null); // Use ref to hold the WebSocket instance

    useEffect(() => {
        console.log('DreamTheatrePanel: Attempting to connect WebSocket...');
        setConnectionStatus('Connecting...');

        // Establish WebSocket connection
        ws.current = new WebSocket(WEBSOCKET_URL);

        ws.current.onopen = () => {
            console.log('DreamTheatre WebSocket Connected');
            setConnectionStatus('Connected');
            // Optional: Send an initial message if needed by backend protocol
            // ws.current.send(JSON.stringify({ type: 'ui_hello', component: 'DreamTheatre' }));
        };

        ws.current.onmessage = (event) => {
            try {
                 // Assuming messages are JSON strings
                const message = JSON.parse(event.data);
                console.log('DreamTheatre WebSocket Message Received:', message);
                setLastMessage(message);
                // --- TODO LATER: Process message data to update UI state ---
                // e.g., updateAgentStatus(message.agent, message.status, message.progress);
            } catch (error) {
                console.error('DreamTheatre WebSocket: Failed to parse message:', event.data, error);
            }
        };

        ws.current.onerror = (error) => {
            console.error('DreamTheatre WebSocket Error:', error);
            setConnectionStatus(`Error (Check Console - Is backend WS server on ${WEBSOCKET_URL} running?)`);
        };

        ws.current.onclose = (event) => {
            console.log('DreamTheatre WebSocket Closed:', event.code, event.reason);
            setConnectionStatus(`Closed (Code: ${event.code})${event.reason ? ' Reason: '+event.reason : ''}`);
            // Optional: Implement reconnection logic here if desired
        };

        // Cleanup function: close WebSocket connection when component unmounts
        return () => {
            console.log('DreamTheatrePanel: Cleaning up WebSocket connection.');
            if (ws.current && ws.current.readyState === WebSocket.OPEN) {
                ws.current.close();
            }
            ws.current = null; // Clear ref
        };
    }, []); // Empty dependency array ensures this runs only once on mount

    // Basic Display V1
    return React.createElement(Box, { sx: { p: 2 } },
        React.createElement(Typography, { variant: 'h6', gutterBottom: true }, "Dream Theatre"),
        React.createElement(Typography, { variant: 'subtitle1', gutterBottom: true }, `Connection Status: ${connectionStatus}`),
        React.createElement(Typography, { variant: 'body1', gutterBottom: true },
            "Agent activity and real-time project progress will appear here."
        ),
         // Display last received message for debugging V1
         React.createElement(Box, { sx: { mt: 2, p: 1, border: '1px dashed grey', maxHeight: 100, overflowY: 'auto'} },
             React.createElement(Typography, { variant: 'caption' }, "Last Raw Message Received:"),
             React.createElement('pre', { style: {fontSize: '0.8em', whiteSpace: 'pre-wrap', wordBreak: 'break-all'} },
                 lastMessage ? JSON.stringify(lastMessage, null, 2) : '(None yet)'
             )
        )
    );
}

exports.default = DreamTheatrePanel; 