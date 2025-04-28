const React = require('react');
const { useState, useEffect } = React;
const Box = require('@mui/material/Box').default;
const Button = require('@mui/material/Button').default;
const Typography = require('@mui/material/Typography').default;
const CircularProgress = require('@mui/material/CircularProgress').default;
let GitHubIcon; 
try { 
    const icons = require('@mui/icons-material'); 
    GitHubIcon = icons.GitHub;
} catch(e){
    console.error("GitHub Icon Load Error", e);
    GitHubIcon = null; // Fallback if icon loading fails
}

// Day 26.1: Triggers main process flow, handles final success/error response.

function GitHubSignIn({ onCheckStatus, setGitHubError }) {
    const [isLoading, setIsLoading] = useState(false);
    const [statusMessage, setStatusMessage] = useState('');

    const setStatus = (message, isError = false) => {
        setStatusMessage(message);
        if (isError && setGitHubError) setGitHubError(message);
        else if (!isError && setGitHubError) setGitHubError(null);
    };

    useEffect(() => { 
        // Clear status on mount
        setStatus(''); 
    }, []); // Empty dependency array ensures this runs only once on mount

    const handleStartAuthFlow = async () => {
        setIsLoading(true);
        setStatus('Starting GitHub Link process...', false);

        if (!window.electronAPI?.invoke) {
            setStatus("Error: Secure communication unavailable.", true);
            setIsLoading(false); return;
        }

        try {
            // Trigger the main process flow via secure IPC invoke
            console.log("GitHubSignIn: Invoking 'start-github-auth'...");
            const result = await window.electronAPI.invoke('start-github-auth');
            console.log("GitHubSignIn: Received result from 'start-github-auth':", result);

            if (!result || !result.success) {
                // Handle failure response from main process
                throw new Error(result?.error || 'Main process failed to link GitHub account.');
            }

            // --- SUCCESS! Main process handled everything --- 
            // Update status message and trigger parent re-check
            setStatus("GitHub Account Linked Successfully! Verifying...", false);
            if (onCheckStatus) {
                // Ask parent (SettingsPanel) to re-verify status via Keytar/IPC
                 console.log("GitHubSignIn: Sign-in success reported by main process, triggering parent status check...");
                 await onCheckStatus(); // Wait for check to complete
            } else {
                 console.warn("GitHubSignIn: onCheckStatus prop not provided.");
                 // Optionally handle the missing callback case, maybe just stop loading
                 setIsLoading(false);
            }
             // State update (setIsLoading=false) should happen in onCheckStatus in parent or here if no callback

        } catch (err) {
             console.error('GitHubSignIn: Error triggering/completing GitHub auth flow:', err);
             setStatus(`Error linking account: ${err.message}`, true);
             setIsLoading(false); // Stop loading on specific error here
        }
        // Note: setIsLoading(false) is handled on error or if onCheckStatus is missing.
        // If onCheckStatus exists, it (or the parent) is responsible for setting loading state after re-verification.
    };

    const isAvailable = window.electronAPI?.invoke;

    return React.createElement(Box, null,
        React.createElement(Button, {
            variant: "contained",
            color: "secondary",
            onClick: handleStartAuthFlow,
            disabled: isLoading || !isAvailable,
            startIcon: isLoading ? React.createElement(CircularProgress, { size: 20, color:"inherit" }) : (GitHubIcon ? React.createElement(GitHubIcon) : null)
        }, isLoading ? "Linking (Check Browser)..." : (isAvailable ? "Link GitHub Account" : "Link Unavailable")),
        // Display Status/Error Message from the IPC call attempt/result
        statusMessage && React.createElement(Typography, {
             color: statusMessage.startsWith("Error") ? "error" : (statusMessage.includes("Successfully") ? "success.main" : "text.secondary"), // Color success green
             variant:"caption", sx: { mt: 1, display:'block' } 
         }, statusMessage)
    );
}

// Use module.exports for CommonJS compatibility with Electron Forge Webpack setup
module.exports = GitHubSignIn; 
// ============================================
// END: C:\DreamerAI\app\components\GitHubSignIn.jsx
// ============================================ 