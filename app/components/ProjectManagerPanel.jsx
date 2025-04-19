const React = require('react');
const Box = require('@mui/material/Box').default;
const Typography = require('@mui/material/Typography').default;

function ProjectManagerPanel() {
    // Basic placeholder content for V1
    return (
        <Box sx={{ p: 2 }}>
            <Typography variant="h5" gutterBottom>
                Project Manager
            </Typography>
            <Typography variant="body1">
                Project listing, subproject creation, and version control integration will appear here. (V1 Placeholder)
            </Typography>
            {/* Future content: Project list, create/open buttons, Git status etc. */}
        </Box>
    );
}

exports.default = ProjectManagerPanel; 