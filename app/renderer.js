const React = require('react');
const ReactDOM = require('react-dom/client'); // Use createRoot for React 18+

function App() {
    // Simple functional component for initial display

    // Add useEffect to test backend connection on mount
    React.useEffect(() => {
        console.log("Attempting to connect to backend...");
        fetch('http://localhost:8000/') // Fetch from the FastAPI backend
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Backend Connection Success:", data.message);
                // Optionally display status in UI later
            })
            .catch(error => {
                console.error("Backend Connection Failed:", error);
                // Optionally display error in UI later
            });
    }, []); // Empty dependency array means this runs once on mount

    return React.createElement('h1', null, 'Hello from DreamerAI!');
}

// Use the new React 18+ root API
const rootElement = document.getElementById('root');
if (rootElement) {
    const root = ReactDOM.createRoot(rootElement);
    root.render(React.createElement(App));
} else {
    console.error("Target container 'root' not found in index.html.");
} 