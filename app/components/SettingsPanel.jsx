const React = require('react');
const Box = require('@mui/material/Box').default;
const Typography = require('@mui/material/Typography').default;
const GitHubSignIn = require('./GitHubSignIn').default;

function SettingsPanel() {
    return React.createElement(Box, { sx: { p: 2 } },
        React.createElement(Typography, { variant: 'h5', gutterBottom: true }, "Settings"),
        React.createElement(Typography, { variant: 'body1', sx:{ mb: 3 } },
            "Configure DreamerAI application settings, manage integrations, and customize your experience."
        ),
        React.createElement(GitHubSignIn, null),
        React.createElement(Typography, { variant: 'body2', sx:{mt: 3, color: 'grey.500'} },
            "(Other settings options will appear here later)."
        )
    );
}

exports.default = SettingsPanel; 