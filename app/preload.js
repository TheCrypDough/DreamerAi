// C:\DreamerAI\app\preload.js (Updated for Day 26 Rev 6 Secure IPC)
const { contextBridge, ipcRenderer } = require('electron');

console.log('Preload Script: Executing...');

// Define allowed channels for invoke for security
// Whitelist ONLY the channels the Renderer needs to trigger in Main
const validInvokeChannels = [
    // Keep JWT handlers (D105)
    'secure-jwt-save',
    'secure-jwt-get',
    'secure-jwt-delete',
    // Keep Keytar handlers (D66 - Used by main process to store token later)
    'secure-keytar-save',
    'secure-keytar-get',
    'secure-keytar-delete',
    // 'get-github-client-id', // REMOVE - Obsolete with main process flow
    // --- NEW Channel for D26 Rev 6 ---
    'start-github-auth' // Trigger for main process flow
    // Add other invoke channels as needed
];

// Define allowed channels for send (if needed later)
// const validSendChannels = [];

// Define allowed channels for receive (if needed later)
// const validReceiveChannels = [];

// Expose a controlled API to the Renderer process (window.electronAPI)
try {
    contextBridge.exposeInMainWorld(
        'electronAPI', // This will be window.electronAPI in the renderer
        {
            /**
             * Securely invoke an IPC channel handled by the main process.
             * @param {string} channel - The whitelisted IPC channel name.
             * @param {any} [data] - Optional data to send.
             * @returns {Promise<any>} - Promise resolving with the handler's response.
             */
            invoke: (channel, data) => {
                if (validInvokeChannels.includes(channel)) {
                    console.log(`Preload: Invoking channel '${channel}'...`); // Debug log
                    // Send the request to the main process and return the promise
                    return ipcRenderer.invoke(channel, data);
                } else {
                    console.error(`Preload: Denied invoke call to unauthorized channel: ${channel}`);
                    // Reject the promise if the channel is not valid
                    return Promise.reject(new Error(`Invalid IPC channel invoked: ${channel}`));
                }
            },
            // Add send/on methods here later if needed, with similar whitelisting
            /*
            send: (channel, data) => {
                if (validSendChannels.includes(channel)) {
                    ipcRenderer.send(channel, data);
                } else {
                    console.error(`Preload: Denied send call to unauthorized channel: ${channel}`);
                }
            },
            on: (channel, func) => {
                if (validReceiveChannels.includes(channel)) {
                    // Deliberately strip event as it includes `sender`
                    ipcRenderer.on(channel, (event, ...args) => func(...args));
                } else {
                    console.error(`Preload: Denied listener setup for unauthorized channel: ${channel}`);
                }
            }
            */
        }
    );
    console.log('Context Bridge API "electronAPI" exposed successfully.');
} catch (error) {
    console.error('Error setting up context bridge in preload script:', error);
} 