const React = require('react');
const Box = require('@mui/material/Box').default;
const Typography = require('@mui/material/Typography').default;

function ProjectManagerPanel() {
    return React.createElement(Box, { sx: { p: 2 } },
        React.createElement(Typography, { variant: 'h5', gutterBottom: true }, "Project Manager"),
        React.createElement(Typography, { variant: 'body1' },
            "This panel will contain tools for creating, opening, and managing your DreamerAI projects and subprojects."
        ),
        React.createElement(Typography, { variant: 'body2', sx:{mt: 2, color: 'grey.500'} },
            "(Functionality like subproject creation, renaming, deleting, etc., will be added here later based on the guide's plan)."
        )
        // Placeholder for project list, create/open buttons, etc.
    );
}

exports.default = ProjectManagerPanel; 