const React = require('react');
const { useState, useEffect } = React; // Import hooks
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

// --- App Component ---

function App() {
    // State for active tab and beginner mode
    const [activeTab, setActiveTab] = useState(0); // Index of the active tab
    const [beginnerMode, setBeginnerMode] = useState(false);
    const [lastBackendMessage, setLastBackendMessage] = useState({}); // Store parsed JSON

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
                        console.log('Received structured backend message:', receivedData);
                        setLastBackendMessage(receivedData);
                        res.writeHead(200, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({ status: 'Message Received by UI (/update)', received: receivedData })); // Updated status msg
                    } catch (e) {
                        console.error('Failed to parse incoming JSON from backend (/update):', e); // Updated log msg
                        console.error('Received Raw Body (/update):', body); 
                        setLastBackendMessage({ error: 'Failed to parse backend message (/update)', raw: body });
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
             if (err.code === 'EADDRINUSE') {
                console.error(`ERROR: Port ${port} is already in use. Backend bridge may fail.`);
                setLastBackendMessage({ error: 'Cannot listen on Port', port: port });
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

    // Modify placeholder content rendering slightly to show structured message
    const renderTabContent = (tabIndex) => {
        // Example: Display last message details in the Chat tab
        if (tabIndex === 0) {
             return React.createElement(Box, null,
                 React.createElement(Typography, null, "Chat Panel Placeholder"),
                 React.createElement(Typography, { variant: 'caption', sx: { mt: 2, display: 'block', color: 'grey.500' } },
                     // Display structured data from state
                     `Last backend message: Agent='${lastBackendMessage?.agent || 'N/A'}', Type='${lastBackendMessage?.type || 'N/A'}', Payload='${JSON.stringify(lastBackendMessage?.payload)?.substring(0, 100) || '(None)'}...'`
                 )
             );
        }
        // ... (Keep other placeholders) ...
        switch(tabIndex) {
            case 1: return <Typography>Plan/Build Panel Placeholder (Arch/Nexus/Coders)</Typography>;
            case 2: return <Typography>Dream Theatre Placeholder (Hermie's View)</Typography>;
            case 3: return <Typography>Project Manager Placeholder (User/Subprojects)</Typography>;
            case 4: return <Typography>Settings Panel Placeholder</Typography>;
            default: return <Typography>Unknown Tab</Typography>;
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
                        control={<Switch checked={beginnerMode} onChange={handleBeginnerModeChange} />}
                        label="Beginner Mode"
                    />
                </Box>
                {/* Tabs Navigation */}
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={activeTab} onChange={handleTabChange} aria-label="DreamerAI Main Navigation Tabs">
                        {tabLabels.map((label, index) => (
                            <Tab label={label} key={index} />
                        ))}
                    </Tabs>
                </Box>
                {/* Main Content Area (swaps based on active tab) */}
                <Box sx={{ p: 3, flexGrow: 1, overflowY: 'auto' }}> {/* Added flexGrow and overflow */}
                    {renderTabContent(activeTab)}
                </Box>
            </Box>
        </ThemeProvider>
    );
}

// Export the App component
exports.default = App; 