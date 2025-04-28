const React = require('react');
const { useState, useEffect, useCallback, useMemo, useRef } = React;
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
const ProjectManagerPanel = require('../components/ProjectManagerPanel').default;
const SettingsPanel = require('../components/SettingsPanel').default;

const BRIDGE_LISTENER_PORT = 3131; // Make sure this matches bridge.py

// --- App Component ---

function App() {
    // State for active tab and beginner mode
    const [activeTab, setActiveTab] = useState(0); // Index of the active tab
    const [beginnerMode, setBeginnerMode] = useState(false);
    const [chatMessages, setChatMessages] = useState([{ role: 'system', content: 'Welcome to DreamerAI!' }]);
    const [lastBackendStatus, setLastBackendStatus] = useState(''); // For non-chat updates
    const [uiError, setUiError] = useState(null); // For displaying UI/Network errors
    const [isDarkMode, setIsDarkMode] = useState(true);
    const [wsStatus, setWsStatus] = useState('disconnected');
    const wsRef = useRef(null);

    // --- Add Effect Hook to listen for Bridge Messages from Main Process ---
    useEffect(() => {
        if (window.electronAPI && typeof window.electronAPI.onBridgeMessage === 'function') {
            console.log("[App.jsx] Setting up Bridge Message listener...");
            const removeListener = window.electronAPI.onBridgeMessage((receivedData) => {
                console.log('[App.jsx] Bridge Message received from Main:', receivedData);
                if (receivedData.agent === 'Jeff' && receivedData.type === 'chat_response') {
                    setChatMessages(prev => [...prev, { role: 'assistant', content: receivedData.payload }]);
                } else if (receivedData.type === 'error') {
                    setUiError(receivedData.payload || 'Unknown error from backend bridge');
                }
                // Handle other message types if needed
            });

            // Cleanup function to remove the listener when the component unmounts
            return () => {
                console.log("[App.jsx] Removing Bridge Message listener.");
                removeListener();
            };
        } else {
            console.error("[App.jsx] window.electronAPI.onBridgeMessage is not available! Preload script might have failed.");
            setUiError("Critical Error: IPC bridge to main process failed to load.");
        }
    }, []); // Empty dependency array ensures this runs only once on mount
    // --- End Bridge Message Listener ---

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
    // useEffect(() => { // <<<<< SERVER LOGIC REMOVED FROM HERE (Lines 90-125 approx)
    //     const server = http.createServer((req, res) => {
    //          if (req.method === 'POST' && req.url === '/update') {
    //              ...
    //          }
    //     });
    //     server.listen(BRIDGE_LISTENER_PORT, '127.0.0.1', () => { ... });
    //     server.on('error', (err) => { ... });
    //     return () => { server.close(); };
    // }, []); // Run only once on mount <<<<< SERVER LOGIC REMOVED UNTIL HERE

    // Keep Persistent WebSocket Management useEffect from D62.1 ...
     useEffect(() => {
         const WS_URL = 'ws://localhost:8090/ws/dream-theatre/frontend-client'; // Corrected path based on backend logs
         let connectAttempts = 0;
         let maxConnectAttempts = 5; // Limit reconnection attempts
         let reconnectTimeoutId = null;
 
         function connectWebSocket() {
             if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                 console.log('WebSocket already open.');
                 return;
             }
             if (connectAttempts >= maxConnectAttempts) {
                 console.error('WebSocket max reconnect attempts reached.');
                 setWsStatus('failed');
                 setUiError('Failed to connect to Dream Theatre WebSocket after multiple attempts.');
                 return;
             }
 
             console.log(`Attempting WebSocket connection (${connectAttempts + 1}/${maxConnectAttempts})...`);
             setWsStatus('connecting');
             wsRef.current = new WebSocket(WS_URL);
 
             wsRef.current.onopen = () => {
                 console.log('Dream Theatre WebSocket Connected');
                 setWsStatus('connected');
                 setUiError(null); // Clear previous connection errors
                 connectAttempts = 0; // Reset attempts on successful connection
                 // Optional: Send identification or join message
                 // wsRef.current.send(JSON.stringify({ type: 'join', clientId: 'dreamer-ui' }));
             };
 
             wsRef.current.onmessage = (event) => {
                 try {
                     const message = JSON.parse(event.data);
                     console.log('WebSocket Message Received:', message);
                     // Handle different message types from the backend
                     if (message.type === 'agent_update') {
                         // Update specific agent state if needed
                     } else if (message.type === 'broadcast') {
                         // Display broadcast message (maybe in a specific panel or snackbar)
                         setUiError(`Broadcast: ${message.payload}`); // Example: Use Snackbar for broadcasts
                     } else if (message.type === 'error') {
                         setUiError(message.payload || 'Unknown WebSocket error');
                     } else {
                         // Handle other message types as needed
                     }
                 } catch (e) {
                     console.error('Error parsing WebSocket message:', e);
                     setUiError('Received invalid message from WebSocket.');
                 }
             };
 
             wsRef.current.onerror = (error) => {
                 console.error('WebSocket Error:', error);
                 setWsStatus('error');
                 // Don't set UI error here, rely on onclose handling for reconnect/failure message
             };
 
             wsRef.current.onclose = (event) => {
                 console.log(`WebSocket Disconnected. Code: ${event.code}, Reason: ${event.reason || 'N/A'}`);
                 setWsStatus('disconnected');
                 wsRef.current = null;
                 if (connectAttempts < maxConnectAttempts) {
                     const delay = Math.pow(2, connectAttempts) * 1000; // Exponential backoff
                     console.log(`Attempting to reconnect WebSocket in ${delay / 1000}s...`);
                     reconnectTimeoutId = setTimeout(connectWebSocket, delay);
                     connectAttempts++;
                 } else {
                     console.error('WebSocket connection closed permanently after multiple retries.');
                     setUiError('WebSocket connection lost. Please check backend and refresh.');
                     setWsStatus('failed');
                 }
             };
         }
 
         connectWebSocket(); // Initial connection attempt
 
         // Cleanup function
         return () => {
             console.log('Cleaning up WebSocket connection...');
             clearTimeout(reconnectTimeoutId); // Clear any pending reconnect timeout
             if (wsRef.current) {
                 wsRef.current.close(1000, 'Component unmounting'); // Normal closure
                 wsRef.current = null;
             }
             setWsStatus('disconnected');
         };
     }, []); // Empty dependency array ensures this runs only once on mount

    // Define theme (using default dark theme for now)
    const theme = useMemo(() => createTheme({
        palette: {
            mode: isDarkMode ? 'dark' : 'light',
        },
    }), [isDarkMode]);

    // Define Tab Labels (can be internationalized later)
    const tabLabels = ["Main Chat", "Dream Theatre", "Project Manager", "Plan/Build", "Settings"];

    // MODIFY Render Content for Active Tab
    const renderTabContent = (tabIndex) => {
        switch (tabIndex) {
            case 0: // Chat Panel
                return React.createElement(MainChatPanel, { messages: chatMessages, onSendMessage: handleSendMessage });
            case 1: return React.createElement(DreamTheatrePanel, { wsStatus: wsStatus });
            case 2: // Project Manager Panel
                return React.createElement(ProjectManagerPanel);
            case 3: // Plan/Build Panel (NEW)
                // TODO: Replace with actual PlanBuildPanel component later
                return React.createElement(Typography, null, "Plan/Build Panel Placeholder");
            case 4: // Settings Panel (Index shifted)
                return React.createElement(SettingsPanel, { toggleDarkMode: () => setIsDarkMode(!isDarkMode), isDarkMode: isDarkMode });
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