const React = require('react');
const { useState, useEffect } = React;
const Button = require('@mui/material/Button').default;
const Typography = require('@mui/material/Typography').default;
const CircularProgress = require('@mui/material/CircularProgress').default;
const GitHubIcon = require('@mui/icons-material/GitHub').default;
const Box = require('@mui/material/Box').default;

function GitHubSignIn() {
    const [isLoading, setIsLoading] = useState(false);
    const [statusMessage, setStatusMessage] = useState('');
    const [isError, setIsError] = useState(false);

    const setStatus = (message, error = false) => {
        setStatusMessage(message);
        setIsError(error);
    };

    useEffect(() => {
        // Optionally clear status on component mount or specific events
        setStatus('');
    }, []);

    const handleStartAuthFlow = async () => {
        setIsLoading(true);
        setStatus('Contacting main application...', false);
        
        if (!window.electronAPI?.invoke) {
            setStatus('Error: Electron API bridge not available. Cannot start auth.', true);
            setIsLoading(false);
            return;
        }

        try {
            // Trigger placeholder handler in main.js
            console.log("[GitHubSignIn] Invoking 'start-github-auth'...");
            const result = await window.electronAPI.invoke('start-github-auth');
            console.log("[GitHubSignIn] Received result from main process:", result);

            // Expecting failure V1 because the main process handler is a placeholder
            if (!result || !result.success) {
                throw new Error(result?.error || 'Main process rejected the request.');
            }

            // Success handling (only after Day 26.1+ implementation in main.js)
            // setStatus('GitHub authentication successful! Token should be stored.', false);
        } catch (err) {
             // Display the expected "Not Implemented" error from the placeholder
             console.error("[GitHubSignIn] Error during auth flow:", err);
             setStatus(`Error: ${err.message}`, true);
        } finally {
            setIsLoading(false);
        }
    };

    const isAvailable = window.electronAPI?.invoke;

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, p: 2, border: '1px dashed grey', borderRadius: 1 }}>
            <Typography variant="h6">Link GitHub Account</Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
                Connect your GitHub account to enable related features.
            </Typography>
            <Button
                variant="contained"
                startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <GitHubIcon />}
                onClick={handleStartAuthFlow}
                disabled={isLoading || !isAvailable}
                sx={{ minWidth: '200px' }}
            >
                {isLoading ? 'Processing...' : 'Connect with GitHub'}
            </Button>
            {statusMessage && (
                <Typography 
                    variant="caption" 
                    color={isError ? 'error' : 'text.secondary'}
                    sx={{ mt: 1, textAlign: 'center' }}
                >
                    {statusMessage}
                </Typography>
            )}
            {!isAvailable && (
                 <Typography variant="caption" color="error" sx={{ mt: 1, textAlign: 'center' }}>
                    Error: Cannot communicate with main process. IPC unavailable.
                 </Typography>
            )}
        </Box>
    );
}

exports.default = GitHubSignIn; 