const React = require('react');
const ReactDOM = require('react-dom/client'); // Use createRoot for React 18+
const App = require('./src/App').default; // Import the main App component from App.jsx

// Ensure the root element exists
const rootElement = document.getElementById('root');

if (rootElement) {
    // Create a root.
    const root = ReactDOM.createRoot(rootElement);

    // Initial render: Render the App component to the root.
    root.render(React.createElement(React.StrictMode, null, React.createElement(App)));
    console.log('React application mounted.');
} else {
    console.error("Target container 'root' not found in index.html. React app cannot mount.");
} 