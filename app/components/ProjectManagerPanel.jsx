const React = require('react');
const { useState } = React;
const Box = require('@mui/material/Box').default;
const Typography = require('@mui/material/Typography').default;
const TextField = require('@mui/material/TextField').default;
const Button = require('@mui/material/Button').default;
const CircularProgress = require('@mui/material/CircularProgress').default;
const Alert = require('@mui/material/Alert').default;

function ProjectManagerPanel() {
    // State for creating subprojects
    const [parentProjectId, setParentProjectId] = useState('');
    const [subprojectName, setSubprojectName] = useState('');
    const [isCreatingSubproject, setIsCreatingSubproject] = useState(false);
    const [subprojectStatus, setSubprojectStatus] = useState({ message: '', severity: '' }); // For user feedback

    // TODO V2: Need state for projects list & better way to select parent project ID

    const handleCreateSubproject = async () => {
        if (!parentProjectId || !subprojectName) {
             setSubprojectStatus({ message: 'Parent Project ID and Subproject Name are required.', severity: 'warning'});
             return;
        }
        setIsCreatingSubproject(true);
        setSubprojectStatus({ message: '', severity: '' }); // Clear previous status
        console.log(`Attempting to create subproject '${subprojectName}' under parent ID ${parentProjectId}`);

        try {
             const response = await fetch(`http://localhost:8090/projects/${parentProjectId}/subprojects`, { // Corrected port to 8090
                 method: 'POST',
                 headers: { 'Content-Type': 'application/json' },
                 body: JSON.stringify({
                      subproject_name: subprojectName,
                      user_id: "Example User" // TODO: Replace with actual user ID from auth
                 })
             });

            const result = await response.json();

            if (!response.ok) {
                 // Use detail from FastAPI error response if available
                 throw new Error(result.detail || `HTTP error ${response.status}`);
             }

            console.log("Subproject creation response:", result);
            setSubprojectStatus({ message: result.message || 'Subproject created!', severity: 'success' });
            // Clear fields on success
            setParentProjectId('');
            setSubprojectName('');
             // TODO V2: Refresh project list/tree view here

        } catch (error) {
             console.error("Failed to create subproject:", error);
             setSubprojectStatus({ message: `Subproject creation failed: ${error.message}`, severity: 'error'});
        } finally {
             setIsCreatingSubproject(false);
        }
    };

    return React.createElement(Box, { sx: { p: 2 } },
        React.createElement(Typography, { variant: 'h5', gutterBottom: true }, "Project Manager"),

        // --- Subproject Creation V1 ---
        React.createElement(Box, { sx: { mt: 3, p: 2, border: '1px solid grey', borderRadius: '4px'} },
             React.createElement(Typography, { variant: 'h6', gutterBottom: true }, "Create New Subproject"),
             React.createElement(TextField, {
                 label: "Parent Project ID",
                 variant: "outlined",
                 size: "small",
                 value: parentProjectId,
                 onChange: (e) => setParentProjectId(e.target.value),
                 fullWidth: true,
                 margin: "normal",
                 helperText: "V1: Enter the ID of the existing parent project." // Clarify V1 limitation
             }),
             React.createElement(TextField, {
                 label: "New Subproject Name",
                 variant: "outlined",
                 size: "small",
                 value: subprojectName,
                 onChange: (e) => setSubprojectName(e.target.value),
                 fullWidth: true,
                 margin: "normal"
             }),
            React.createElement(Button, {
                variant: 'contained',
                onClick: handleCreateSubproject,
                disabled: isCreatingSubproject,
                sx: { mt: 1 }
             },
                isCreatingSubproject ? React.createElement(CircularProgress, { size: 24 }) : "Create Subproject"
             ),
            // Display Status/Error Messages
            subprojectStatus.message && React.createElement(Alert, {
                 severity: subprojectStatus.severity || 'info', // Default to 'info'
                 sx: { mt: 2 }
                 },
                 subprojectStatus.message
            )
        ),

        // --- Placeholder for Project List/Tree View ---
        React.createElement(Typography, { variant: 'body2', sx:{mt: 4, color: 'grey.500'} },
             "(Project and subproject list/navigation will be added later)."
        )
    );
}

exports.default = ProjectManagerPanel; 