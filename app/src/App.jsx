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
    const [lastBackendMessage, setLastBackendMessage] = useState(''); // To display test messages

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

    // Effect hook to set up the backend listener
    useEffect(() => {
        const port = 3000;
        const server = http.createServer((req, res) => {
            // Listen only for POST requests on /update path (from Python backend)
            if (req.method === 'POST' && req.url === '/update') {
                let body = '';
                req.on('data', chunk => {
                    body += chunk.toString(); // Convert Buffer chunks to string
                });
                req.on('end', () => {
                    console.log('Received backend message:', body);
                    setLastBackendMessage(`Received @ ${new Date().toLocaleTimeString()}: ${body}`); // Update state to display message
                    // --- TODO LATER: Process the message based on its content ---
                    // e.g., if (body.type === 'progress') { updateProgressBar(body.data); }
                    // e.g., if (body.agent === 'Jeff') { addJeffMessageToChatPanel(body.content); }
                    res.writeHead(200, { 'Content-Type': 'text/plain' });
                    res.end('Message Received by UI');
                });
                req.on('error', (err) => {
                     console.error('Request error in UI listener:', err);
                     res.writeHead(500);
                     res.end('Server error processing request');
                 });
            } else {
                 // Respond to other requests (e.g., GET requests) if needed, or ignore
                 res.writeHead(404);
                 res.end('Not Found');
            }
        });

        server.listen(port, '127.0.0.1', () => {
            console.log(`UI Backend Listener started on port ${port}`);
        });

        server.on('error', (err) => {
             console.error(`UI Listener Server error: ${err}`);
             // Handle specific errors like EADDRINUSE if port is taken
             if (err.code === 'EADDRINUSE') {
                console.error(`ERROR: Port ${port} is already in use. Backend bridge may fail.`);
                setLastBackendMessage(`ERROR: Cannot listen on Port ${port}. It might be in use.`);
             }
         });

        // Cleanup function to close the server when the component unmounts
        return () => {
            console.log('Closing UI Backend Listener...');
            server.close();
        };
    }, []); // Empty dependency array ensures this runs only once on mount

    // Define theme (using default dark theme for now)
    const theme = createTheme({
        palette: {
            mode: 'dark',
        },
    });

    // Define Tab Labels (can be internationalized later)
    const tabLabels = ["Chat", "Plan/Build", "Dream Theatre", "Project Manager", "Settings"];

    // Placeholder Content for Tabs
    const renderTabContent = (tabIndex) => {
        // Later, these will render specific panel components
        switch(tabIndex) {
            case 0: return <Typography>Chat Panel Placeholder (Jeff's Home)</Typography>;
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
                    {/* Display last backend message for testing the listener */}
                    <Typography variant="caption" sx={{ mt: 2, display: 'block', color: 'grey.500' }}>
                        {`Last backend message: ${lastBackendMessage || '(None received yet)'}`}
                    </Typography>
                </Box>
            </Box>
        </ThemeProvider>
    );
}

// Export the App component
exports.default = App; 