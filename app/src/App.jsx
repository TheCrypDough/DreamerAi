const React = require('react');
const { useState, useEffect, useCallback } = React; // Added useCallback
const http = require('http'); // Node.js http module for listener

// Import Material UI components
const { ThemeProvider, createTheme } = require('@mui/material/styles');
const CssBaseline = require('@mui/material/CssBaseline').default;
const Box = require('@mui/material/Box').default;
const Tabs = require('@mui/material/Tabs').default;
const Tab = require('@mui/material/Tab').default;
const Switch = require('@mui/material/Switch').default;
const FormControlLabel = require('@mui/material/FormControlLabel').default;
const Typography = require('@mui/material/Typography').default; // For displaying content
const Alert = require('@mui/material/Alert').default; // For showing errors
const Snackbar = require('@mui/material/Snackbar').default;

// Import Panels
const MainChatPanel = require('../components/MainChatPanel').default;
const DreamTheatrePanel = require('../components/DreamTheatrePanel').default;

// --- App Component ---

function App() {
    // State for active tab and beginner mode
    const [activeTab, setActiveTab] = useState(0); // Index of the active tab
    const [beginnerMode, setBeginnerMode] = useState(false);
    const [chatMessages, setChatMessages] = useState([
        { role: 'assistant', content: "Welcome to DreamerAI! I'm Jeff. How can I help you build today?" } // Initial welcome
    ]);
    const [lastBackendStatus, setLastBackendStatus] = useState(''); // For non-chat updates
    const [uiError, setUiError] = useState(null); // For displaying UI/Network errors

    // Handle tab change
    const handleTabChange = (event, newValue) => {
        console.log(`Switching to tab index: ${newValue}`);
        setActiveTab(newValue);
    };

    // Handle beginner mode toggle
    const handleBeginnerModeChange = (event) => {
        const isBeginner = event.target.checked;
        console.log(`Beginner Mode Toggled: ${isBeginner}`);
        setBeginnerMode(isBeginner);
        // Add logic later to change UI based on beginnerMode state
    };

    const handleCloseError = (event, reason) => {
        if (reason === 'clickaway') return;
        setUiError(null);
    };

    // Backend Communication
    // Function to send message TO backend (Jeff)
    const handleSendMessage = useCallback(async (message) => {
        console.log(`Sending message to Jeff: ${message}`);
        // Optimistically update UI
        setChatMessages(prev => [...prev, { role: 'user', content: message }]);

        try {
            const response = await fetch('http://localhost:8090/agents/jeff/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_input: message })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Backend error: ${response.status} - ${errorData.detail || 'Unknown error'}`);
            }
            const result = await response.json();
            console.log("Backend acknowledgment:", result); // e.g., {"status": "received"}
            // NOTE: Jeff's actual chat response comes back via the Bridge Listener below

        } catch (error) {
            console.error("Failed to send message to backend:", error);
            setUiError(`Failed to send message: ${error.message}`);
            // Optional: Add message indicating failure to chat panel
            setChatMessages(prev => [...prev, { role: 'system', content: `Error sending message: ${error.message}` }]);
        }
    }, []); // useCallback to stabilize the function reference

    // MODIFY Effect hook for backend listener - Revert to specific path check
    useEffect(() => {
        const port = 3131; // Keep changed port
        const server = http.createServer((req, res) => {
            // Revert DEBUG: Log only specific requests if needed
            // console.log(`Listener (Port ${port}) received request: Method=${req.method}, URL=${req.url}`);

            // Revert check: Check for POST method AND specific /update path
            if (req.method === 'POST' && req.url === '/update') {
                // console.log(`POST request received for URL: ${req.url}`); // Keep logging specific URL?
                let body = '';
                req.on('data', chunk => { body += chunk.toString(); });
                req.on('end', () => {
                    // Keep JSON parsing logic
                    try {
                        const receivedData = JSON.parse(body);
                        console.log('UI Listener received:', receivedData);

                        // Process based on message type/agent
                        if (receivedData.agent === 'Jeff' && receivedData.type === 'chat_response') {
                            // Add Jeff's response to chat
                             // Check if payload is an error object or string
                            const content = typeof receivedData.payload === 'object' && receivedData.payload.error
                                ? `Jeff Error: ${receivedData.payload.error}`
                                : receivedData.payload;
                             setChatMessages(prev => [...prev, { role: 'assistant', content: content }]);
                        } else if (receivedData.type === 'error') {
                             // Handle generic error messages from backend agents
                             console.error("Backend Agent Error:", receivedData.payload);
                             setChatMessages(prev => [...prev, { role: 'system', content: `Agent Error: ${receivedData.payload}` }]);
                        } else {
                            // Handle other message types later (e.g., progress, status)
                            setLastBackendStatus(`Received: ${receivedData.type} from ${receivedData.agent}`);
                        }

                        res.writeHead(200, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({ status: 'Message Received by UI (/update)' })); // Updated status msg
                    } catch (e) {
                        console.error('UI Listener: Failed to parse JSON:', e, 'Body:', body);
                        setUiError('Received invalid message from backend.');
                        res.writeHead(400, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({ status: 'error', message: 'Invalid JSON received (/update)' }));
                    }
                });
                 req.on('error', (err) => {
                     console.error('Request error in UI listener (/update):', err); // Updated log msg
                     if (!res.writableEnded) {
                         res.writeHead(500);
                         res.end('Server error processing request (/update)');
                     }
                 });
            } else {
                 // Handle non-POST or non-/update requests
                 // console.log(`Non-POST/update request (${req.method}) received for URL: ${req.url}. Responding 404.`);
                 if (!res.writableEnded) {
                     res.writeHead(404);
                     res.end('Not Found'); // Revert status msg
                 }
            }
        });

        server.listen(port, '127.0.0.1', () => {
            console.log(`UI Backend Listener started on port ${port}`); // <-- Updated log message
        });

        server.on('error', (err) => {
             console.error(`UI Listener Server error (Port ${port}): ${err}`); // <-- Updated log message
             setUiError(`UI Listener failed: ${err.message}`); // Set UI error state
             if (err.code === 'EADDRINUSE') {
                console.error(`ERROR: Port ${port} is already in use. Backend bridge may fail.`);
             }
         });

        // Cleanup function to close the server when the component unmounts
        return () => {
            console.log('Closing UI Backend Listener...');
            server.close();
        };
    }, []);

    // Define theme (using default dark theme for now)
    const theme = createTheme({
        palette: {
            mode: 'dark',
        },
    });

    // Define Tab Labels (can be internationalized later)
    const tabLabels = ["Chat", "Plan/Build", "Dream Theatre", "Project Manager", "Settings"];

    // MODIFY Render Content for Active Tab
    const renderTabContent = (tabIndex) => {
        switch (tabIndex) {
            case 0: // Chat Panel
                return React.createElement(MainChatPanel, { messages: chatMessages, onSendMessage: handleSendMessage });
            case 1: return React.createElement(Typography, null, "Plan/Build Panel Placeholder");
            case 2: // Dream Theatre Panel
                return React.createElement(DreamTheatrePanel); // Render the new panel
            case 3: return React.createElement(Typography, null, "Project Manager Placeholder");
            case 4: return React.createElement(Typography, null, "Settings Panel Placeholder");
            default: return React.createElement(Typography, null, "Unknown Tab");
        }
    };

    // Render the main UI
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline /> {/* Ensures consistent baseline styles */}
            <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
                {/* Header Area (Example: Toggle Switch) */}
                <Box sx={{ p: 1, display: 'flex', justifyContent: 'flex-end' }}>
                    <FormControlLabel
                        control={React.createElement(Switch, { checked: beginnerMode, onChange: handleBeginnerModeChange })}
                        label="Beginner Mode"
                    />
                </Box>
                {/* Tabs Navigation */}
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={activeTab} onChange={handleTabChange} aria-label="DreamerAI Main Navigation Tabs">
                        {tabLabels.map((label, index) => (
                            React.createElement(Tab, { label: label, key: index })
                        ))}
                    </Tabs>
                </Box>
                {/* Main Content Area (swaps based on active tab) */}
                <Box sx={{ p: 3, flexGrow: 1, overflowY: 'auto' }}> {/* Added flexGrow and overflow */}
                    {renderTabContent(activeTab)}
                </Box>
                {/* Error Snackbar */}
                <Snackbar open={!!uiError} autoHideDuration={6000} onClose={handleCloseError}>
                    <Alert onClose={handleCloseError} severity="error" sx={{ width: '100%' }}>
                        {uiError}
                    </Alert>
                </Snackbar>
            </Box>
        </ThemeProvider>
    );
}

// Export the App component
exports.default = App; 