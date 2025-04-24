const React = require('react');
const { useState } = React;
const PropTypes = require('prop-types'); // Import PropTypes
const { Button, Box, Typography } = require('@mui/material'); // Added Box and Typography
// Dynamically import electron-oauth2 to handle potential issues in non-Electron envs?
// For simplicity V1, use standard require. Ensure running within Electron.
let OAuth;
let keytar;
try {
    OAuth = require('electron-oauth2').default; // Note the .default
    keytar = require('keytar');
} catch (error) {
    console.error("Failed to load electron-oauth2 or keytar. GitHub auth unavailable.", error);
    // Handle the error gracefully in the component, e.g., disable the button
}

// --- TODO: SECURE CONFIG INJECTION ---
// HARDCODING SECRETS HERE IS BAD PRACTICE & INSECURE.
// Replace these with a secure method to get config into the renderer process,
// e.g., via contextBridge in preload.js or IPC calls to the main process
// which reads from the environment/config files safely.
const GITHUB_CLIENT_ID_PLACEHOLDER = "Ov23li40T3xrObxKqbXP";
const GITHUB_CLIENT_SECRET_PLACEHOLDER = "4ee406c6f14d4baa7de718e17cb9fe68b4a1f25c";
// --- END TODO ---

/**
 * @param {object} props
 * @param {function({accessToken: string}): void} props.onSignInSuccess - Callback function on successful sign-in.
 */
function GitHubSignIn({ onSignInSuccess }) {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSignIn = async () => {
        if (!OAuth || !keytar) {
            setError("GitHub Sign-In libraries not loaded.");
            return;
        }

        setIsLoading(true);
        setError(null);

        const config = {
            clientId: GITHUB_CLIENT_ID_PLACEHOLDER, // Use placeholder or injected config
            clientSecret: GITHUB_CLIENT_SECRET_PLACEHOLDER, // Use placeholder or injected config
            authorizationUrl: 'https://github.com/login/oauth/authorize',
            tokenUrl: 'https://github.com/login/oauth/access_token',
            useBasicAuthorizationHeader: false,
            // The redirectUri must match exactly what's configured in your GitHub OAuth App settings.
            // 'http://localhost' is often used for simple Electron setups, but might need adjustment.
            redirectUri: 'http://localhost'
        };

        // Ensure window options are suitable (size might need adjustment)
        const windowOptions = {
             width: 800,
             height: 600,
             webPreferences: {
                 nodeIntegration: false, // Keep nodeIntegration false for the auth window itself
                 contextIsolation: true
            }
        };

        const githubOAuth = new OAuth(config, windowOptions);

        try {
            console.log("Initiating GitHub OAuth flow...");
            // Request 'repo' scope for full repository access
            const token = await githubOAuth.getAccessToken({ scope: 'repo' });
            console.log('GitHub OAuth Success:', token); // Log full token object initially for debug

            if (!token || !token.access_token) {
                throw new Error("Received invalid token object from GitHub.");
            }

            // Store the access token securely using keytar
            // Use a service name and account name convention
            const service = 'DreamerAI_GitHub';
            const account = 'user_access_token'; // Or link to user ID later
            await keytar.setPassword(service, account, token.access_token);
            console.log(`Token stored securely in keychain (Service: ${service})`);

            // Send the token to the backend V1 endpoint
            console.log("Sending token to backend...");
            const backendResponse = await fetch('http://localhost:8000/auth/github/token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: token.access_token })
            });

            if (!backendResponse.ok) {
                const errorData = await backendResponse.json();
                throw new Error(`Backend token storage failed: ${errorData.detail || backendResponse.statusText}`);
            }
            console.log("Backend acknowledged token receipt.");

            // Call the success handler passed from parent (e.g., SettingsPanel)
            if (onSignInSuccess) {
                // Pass relevant info, maybe username if available, or just signal success
                onSignInSuccess({ accessToken: token.access_token });
            }

        } catch (err) {
            console.error('GitHub OAuth Error:', err);
            setError(`GitHub Sign-In Failed: ${err.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    if (!OAuth || !keytar) {
         return React.createElement(Button, { variant: "contained", disabled: true }, "GitHub Sign-In Unavailable");
    }

    // Corrected the return statement to use Box and Typography
    return React.createElement(Box, null,
        React.createElement(Button, {
            variant: "contained",
            color: "primary",
            onClick: handleSignIn,
            disabled: isLoading
        }, isLoading ? "Signing In..." : "Sign in with GitHub"),
        error && React.createElement(Typography, { color: "error", sx: { mt: 1 } }, error)
    );
}

// Add propTypes definition
GitHubSignIn.propTypes = {
    onSignInSuccess: PropTypes.func.isRequired
};

exports.default = GitHubSignIn; 