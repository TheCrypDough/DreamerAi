const React = require('react');
const ReactDOM = require('react-dom/client'); // Use createRoot for React 18+

function App() {
    // Simple functional component for initial display
    const [backendMessage, setBackendMessage] = React.useState("Loading...");

    React.useEffect(() => {
        // Run once on mount
        console.log("Renderer: Attempting to fetch from backend...");
        fetch('http://localhost:8000/') // Fetch from the FastAPI root endpoint
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Renderer: Received data from backend:", data);
                setBackendMessage(data.message || "Data received, but no message key.");
            })
            .catch(error => {
                console.error('Renderer: Error fetching from backend:', error);
                setBackendMessage("Error connecting to backend.");
            });
    }, []); // Empty dependency array means run only once on mount

    return React.createElement('div', null, 
        React.createElement('h1', null, 'Hello from DreamerAI!'),
        React.createElement('p', null, `Backend Status: ${backendMessage}`)
    );
}

// Use the new React 18+ root API
const rootElement = document.getElementById('root');
if (rootElement) {
    const root = ReactDOM.createRoot(rootElement);
    root.render(React.createElement(App));
} else {
    console.error("Target container 'root' not found in index.html.");
} 