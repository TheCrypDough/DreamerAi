const { app, BrowserWindow, ipcMain, safeStorage, shell } = require('electron');
const path = require('path');
const http = require('http'); // Added for Bridge Listener

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
  app.quit();
}

// --- Attempt Keytar Load ---
let keytar = null;
try {
    keytar = require('keytar');
    console.log("[Main Process D26] Keytar loaded successfully (Prerequisite check OK).");
} catch (error){
    console.error("!!! [Main Process D26] Failed to load keytar. GitHub token storage will fail! Run `npm run rebuild`? !!!", error);
    keytar = null;
}
// -------------------------

// Keep JWT storage V1 vars...
let encryptedJwtBuffer = null; let encryptionAvailable = false;

// --- HTTP Bridge Listener Port ---
const BRIDGE_LISTENER_PORT = process.env.BRIDGE_LISTENER_PORT || 3131;

// --- GitHub Config Check (Env Vars - Needs setup for D26.1+) ---
// Load dotenv configuration based on the environment
require('dotenv').config({ path: path.resolve(__dirname, '..', 'data', 'config', '.env.development') });

const GITHUB_CLIENT_ID_MAIN = process.env.GITHUB_CLIENT_ID;
const GITHUB_CLIENT_SECRET_MAIN = process.env.GITHUB_CLIENT_SECRET;
let githubCredentialsOk = true;
if (!GITHUB_CLIENT_ID_MAIN || !GITHUB_CLIENT_SECRET_MAIN) {
    console.error("!!! [Main Process D26] GitHub Client ID or Secret NOT FOUND in environment variables! OAuth flow will fail. Check data/config/.env.development !!!");
    githubCredentialsOk = false;
} else {
    console.log("[Main Process D26] GitHub Client ID found (Env var check OK).");
}
// -----------------------------------------------------------

let mainWindow = null; // Make mainWindow accessible in this scope

const createWindow = () => {
  // Create the browser window.
  mainWindow = new BrowserWindow({ // Assign to the outer scope variable
    width: 1200, // Starting width
    height: 800, // Starting height
    webPreferences: {
      // preload: path.join(__dirname, 'preload.js'), // INCORRECT: __dirname is inside .webpack
      preload: MAIN_WINDOW_PRELOAD_WEBPACK_ENTRY, // CORRECT: Use variable provided by Forge Webpack
      nodeIntegration: false, // SECURE
      contextIsolation: true, // SECURE
      devTools: !app.isPackaged
    }
  });

  // Load the index.html of the app.
  // mainWindow.loadFile(path.join(__dirname, 'index.html')); // Old way
  // --- CORRECTED Loading Logic for Electron Forge + Webpack ---
   // The MAIN_WINDOW_WEBPACK_ENTRY variable will be populated by webpack. Define it if not present.
   // This variable name is specific to electron-forge.
   if (typeof MAIN_WINDOW_WEBPACK_ENTRY !== 'undefined' && MAIN_WINDOW_WEBPACK_ENTRY) {
        console.log(`[Main Process D26] Loading Renderer Entry: ${MAIN_WINDOW_WEBPACK_ENTRY}`);
        mainWindow.loadURL(MAIN_WINDOW_WEBPACK_ENTRY);
   } else {
        // Fallback for environments where MAIN_WINDOW_WEBPACK_ENTRY might not be defined
        // Adjust the path according to your project structure if main.js is not in src/
        // Correct path might be '../renderer/main_window/index.html' relative to .webpack/main
        // CORRECTED FALLBACK: Load source index.html directly
        const indexPath = path.join(__dirname, 'index.html'); 
        console.warn(`[Main Process D26] MAIN_WINDOW_WEBPACK_ENTRY undefined, attempting to load fallback: file://${indexPath}`);
        mainWindow.loadFile(indexPath).catch(err => {
          console.error("[Main Process D26] Fallback loadFile failed:", err);
          // Provide a more robust fallback or error handling
          mainWindow.loadURL('data:text/html;charset=utf-8,<title>Error</title><h1>Failed to load application content</h1><p>Check console logs for details.</p>');
        });
   }
   // --- End Corrected Logic ---

  if (!app.isPackaged) mainWindow.webContents.openDevTools();
  // Store mainWindow reference? Maybe for IPC send later?
  // global.mainWindow = mainWindow; // Avoid globals if possible
};

// --- Ensure single instance lock --- //
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', (event, commandLine, workingDirectory) => {
    // Someone tried to run a second instance, we should focus our window.
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
    // Handle protocol links if needed (e.g., for OAuth callbacks if using custom protocol)
    // Example: Handle dreamerai:// links
    const url = commandLine.pop(); // Get the last argument which might be the URL
    if (url && url.startsWith('dreamerai://')) {
      console.log(`[Main Process D26] Second instance opened with URL: ${url}`);
      // Implement logic to handle the URL, e.g., parse OAuth code
      // mainWindow.webContents.send('protocol-link', url);
    }
  });

  // Create mainWindow, load the rest of the app, etc...
  app.whenReady().then(() => {
   // Load environment variables (Moved earlier)
   console.log("[Main Process D26] App ready.");

   encryptionAvailable = safeStorage.isEncryptionAvailable(); // Check safeStorage
   console.log(`[Main Process D26] safeStorage Available: ${encryptionAvailable}`);

   // --- Setup IPC Handlers ---
   // Existing handlers (JWT, Keytar Placeholders/Functional if implemented D66/D105)
   ipcMain.handle('secure-jwt-save', async (event, token) => { /* D105 Logic/Placeholder */ console.warn("IPC: secure-jwt-save not implemented"); return { success: false, error: 'Not implemented' }; });
   ipcMain.handle('secure-jwt-get', async (event) => { /* D105 Logic/Placeholder */ console.warn("IPC: secure-jwt-get not implemented"); return { success: false, token: null, error: 'Not implemented' }; });
   ipcMain.handle('secure-jwt-delete', async (event) => { /* D105 Logic/Placeholder */ console.warn("IPC: secure-jwt-delete not implemented"); return { success: false, error: 'Not implemented' }; });

   const GITHUB_KEYCHAIN_SERVICE = 'DreamerAI_GitHub_Token_Service_D66';
   const GITHUB_KEYCHAIN_ACCOUNT = 'user_github_access_token';
   if (keytar) { // Only setup if keytar loaded
       ipcMain.handle('secure-keytar-save', async (event, { service, account, token }) => { /* D66 Functional Logic Here */ console.warn("IPC: secure-keytar-save not implemented"); return { success: false, error: 'Not implemented' }; });
       ipcMain.handle('secure-keytar-get', async (event, { service, account }) => { /* D66 Functional Logic Here */ console.warn("IPC: secure-keytar-get not implemented"); return { success: false, token: null, error: 'Not implemented' }; });
       ipcMain.handle('secure-keytar-delete', async (event, { service, account }) => { /* D66 Functional Logic Here */ console.warn("IPC: secure-keytar-delete not implemented"); return { success: false, error: 'Not implemented' }; });
        console.log("[Main Process D26] IPC: Keytar placeholder handlers configured.");
    } else { 
        // Define fallback handlers if keytar is not available
        const keytarError = 'Keytar native module not loaded. Secure storage unavailable.';
        ipcMain.handle('secure-keytar-save', async () => ({ success: false, error: keytarError }));
        ipcMain.handle('secure-keytar-get', async () => ({ success: false, token: null, error: keytarError }));
        ipcMain.handle('secure-keytar-delete', async () => ({ success: false, error: keytarError }));
        console.error("[Main Process D26] IPC: Keytar fallback error handlers configured."); 
    }

   // --- Day 26 Placeholder GitHub Auth Trigger --- //
   ipcMain.handle('start-github-auth', async () => {
       console.warn("IPC <<< Received 'start-github-auth' request from renderer.");
       console.error("<<<<< ERROR: Actual GitHub OAuth logic not implemented yet. TODO: Implement in Day 26.1+ >>>>>");
       // In a real implementation (Day 26.1+), this would:
       // 1. Check if githubCredentialsOk
       // 2. Generate state, construct GitHub authorization URL
       // 3. Open the URL in the default browser using shell.openExternal()
       // 4. Setup a temporary server OR use protocol handler to catch the redirect
       // 5. Exchange code for token
       // 6. Save token securely (using keytar handler)
       // 7. Return success/failure to renderer
       return { success: false, error: 'Main process GitHub OAuth flow not implemented yet (Planned D26.1+).' };
   });
   console.log("[Main Process D26] IPC: 'start-github-auth' placeholder handler configured.");
   // ------------------------------------------ //

   createWindow(); // Create the main window

   // --- Add HTTP Bridge Listener Server (Moved from App.jsx) ---
   const bridgeServer = http.createServer((req, res) => {
        if (req.method === 'POST' && req.url === '/update') {
            let body = '';
            req.on('data', chunk => { body += chunk; });
            req.on('end', () => {
                try {
                    const receivedData = JSON.parse(body);
                    console.log(`[Main Process Bridge Listener (Port ${BRIDGE_LISTENER_PORT})] Received:`, receivedData);
                    // Send data to Renderer via IPC instead of setting state directly
                    if (mainWindow && mainWindow.webContents) {
                        mainWindow.webContents.send('bridge-message', receivedData);
                    }
                } catch (e) {
                    console.error(`[Main Process Bridge Listener] JSON parse error:`, e);
                    // Optionally send error back to renderer?
                    if (mainWindow && mainWindow.webContents) {
                         mainWindow.webContents.send('bridge-message', { type: 'error', payload: 'Invalid bridge message received from backend.' });
                    }
                }
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ status: 'OK' }));
            });
            req.on('error', (err) => {
                console.error('[Main Process Bridge Listener] Request error:', err);
                if (mainWindow && mainWindow.webContents) {
                     mainWindow.webContents.send('bridge-message', { type: 'error', payload: `Backend bridge request error: ${err.message}` });
                }
            });
        } else {
            console.log(`[Main Process Bridge Listener] Received non-POST/update request: ${req.method} ${req.url}`);
            res.writeHead(404);
            res.end('Not Found');
        }
   });

   bridgeServer.listen(BRIDGE_LISTENER_PORT, '127.0.0.1', () => {
        console.log(`[Main Process] HTTP Bridge Listener started successfully on port ${BRIDGE_LISTENER_PORT}`);
   });

   bridgeServer.on('error', (err) => {
        console.error(`[Main Process] HTTP Bridge Listener error: ${err}`);
        // Optionally send error back to renderer?
        if (mainWindow && mainWindow.webContents) {
            mainWindow.webContents.send('bridge-message', { type: 'error', payload: `UI Listener failed to start on port ${BRIDGE_LISTENER_PORT}: ${err.message}. Is the port in use?` });
        }
   });
   // --- End HTTP Bridge Listener Server ---

   app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });

  }); // End app.whenReady()
}

app.on('window-all-closed', () => {
  // --- Close Bridge Server Gracefully ---
  if (bridgeServer) {
      console.log("[Main Process] Closing HTTP Bridge Listener...");
      bridgeServer.close((err) => {
          if (err) console.error("[Main Process] Error closing HTTP Bridge Listener:", err);
          else console.log("[Main Process] HTTP Bridge Listener closed.");
      });
  }
  // --- End Close Bridge Server ---
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// In this file, you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here. 