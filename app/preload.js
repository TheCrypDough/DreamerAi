// C:\DreamerAI\app\preload.js
// This file runs in a privileged environment before the renderer process.
// It's often used to expose specific Node.js APIs to the renderer securely
// via the contextBridge API when contextIsolation is true.
// For now, with contextIsolation: false, it can be empty or used minimally.

window.addEventListener('DOMContentLoaded', () => {
  console.log('Preload script executed');
  // Example: Expose minimal Electron APIs if needed later
  // const { contextBridge, ipcRenderer } = require('electron')
  // contextBridge.exposeInMainWorld('electronAPI', {
  //   sendMessage: (channel, data) => ipcRenderer.send(channel, data)
  // })
}); 