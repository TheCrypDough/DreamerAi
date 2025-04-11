const React = require('react');
const ReactDOM = require('react-dom/client'); // Use createRoot for React 18+

function App() {
    // Simple functional component for initial display
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