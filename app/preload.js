// C:\DreamerAI\app\preload.js
// This file runs in a privileged environment before the renderer process.
// It's often used to expose specific Node.js APIs to the renderer securely
// via the contextBridge API when contextIsolation is true.
// For now, with contextIsolation: false, it can be empty or used minimally.

const { contextBridge, ipcRenderer } = require('electron');

// Define allowed channels for invoke for security
const validInvokeChannels = [
    // Keep JWT channels from D105 structure
    'secure-jwt-save', 'secure-jwt-get', 'secure-jwt-delete',
    // Keep Keytar channels from D66 structure
    'secure-keytar-save', 'secure-keytar-get', 'secure-keytar-delete',
    // --- NEW Channel for Day 26 ---
    'start-github-auth'
    // --- REMOVE 'get-github-client-id' if present ---
];

// Whitelist channels for send/receive if needed (e.g., for ui-update)
const validReceiveChannels = ['bridge-message'];

try { 
    contextBridge.exposeInMainWorld('electronAPI', {
        // Securely expose ipcRenderer.invoke, validating the channel first
        invoke: (channel, ...args) => {
            if (validInvokeChannels.includes(channel)) {
                return ipcRenderer.invoke(channel, ...args);
            }
            console.error(`Preload: Blocked invoke call to invalid channel: ${channel}`);
            return Promise.reject(new Error(`Invalid invoke channel: ${channel}`));
        },
        // Example for send/on if needed later:
        // send: (channel, data) => {
        //     if (validSendChannels.includes(channel)) {
        //         ipcRenderer.send(channel, data);
        //     } else {
        //         console.error(`Preload: Blocked send call to invalid channel: ${channel}`);
        //     }
        // },
        // Expose functions for receiving messages from main process
        onBridgeMessage: (callback) => {
            const channel = 'bridge-message';
            if (validReceiveChannels.includes(channel)) {
                // Deliberately strip event as it includes `sender` 
                const listener = (event, ...args) => callback(...args);
                ipcRenderer.on(channel, listener);
                // Return a cleanup function
                return () => ipcRenderer.removeListener(channel, listener);
            } else {
                console.error(`Preload: Blocked listener setup for invalid channel: ${channel}`);
                return () => {}; // Return no-op cleanup
            }
        },
    });
     console.log('Context Bridge API "electronAPI" exposed (D26 Rev 9 Setup).');
} catch (error) { console.error('Preload script error:', error); }

window.addEventListener('DOMContentLoaded', () => {
  console.log('Preload script executed');
  // Example: Expose minimal Electron APIs if needed later
  // const { contextBridge, ipcRenderer } = require('electron')
  // contextBridge.exposeInMainWorld('electronAPI', {
  //   sendMessage: (channel, data) => ipcRenderer.send(channel, data)
  // })
}); 