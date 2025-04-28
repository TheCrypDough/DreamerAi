const { app, BrowserWindow, ipcMain, safeStorage, shell } = require('electron');
const path = require('path');
const http = require('http'); // Added for Bridge Listener
const https = require('https'); // NEW - For secure token exchange request
const url = require('url'); // NEW - For parsing redirect URL
const querystring = require('querystring'); // NEW - For token exchange body

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
console.log(`[Main Process] app.getAppPath() = ${app.getAppPath()}`);
const dotenvPath = path.resolve(app.getAppPath(), 'data', 'config', '.env.development');
require('dotenv').config({ path: dotenvPath, override: true, debug: true });
console.log(`[Main Process] Attempting to load .env from: ${dotenvPath}`);

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

// --- GitHub Keytar Config (Consistent Names) ---
const GITHUB_KEYCHAIN_SERVICE = 'DreamerAI_GitHub_Token_Service_D66';
const GITHUB_KEYCHAIN_ACCOUNT = 'user_github_access_token';
// --- Backend Config ---
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8090'; // Use env var or default to 8090

// --- Temporary Redirect Server Config --- (Moved here for helpers)
const REDIRECT_PORT = 9876; // Ensure matches GitHub App config
const REDIRECT_HOST = 'localhost';
const REDIRECT_URI = `http://${REDIRECT_HOST}:${REDIRECT_PORT}/github_callback`;
let tempServer = null;
let resolveRedirectPromise = null;
let rejectRedirectPromise = null;
// --------------------------------------

let mainWindow = null; // Make mainWindow accessible in this scope

// --- Helper Functions (Moved Before createWindow for Clarity) ---

// --- Helper: Start Temporary Redirect Server ---
function startTemporaryRedirectServer() {
    return new Promise((resolve, reject) => {
        if (tempServer) { // Prevent multiple servers
             console.warn("[TempServer] Already running. Closing existing...");
             closeTemporaryRedirectServer();
             setTimeout(() => startTemporaryRedirectServer().then(resolve).catch(reject), 200); // Retry after small delay
             return;
        }
        resolveRedirectPromise = resolve;
        rejectRedirectPromise = reject;
        tempServer = http.createServer(async (req, res) => {
            const requestUrl = url.parse(req.url, true);
            const query = requestUrl.query;
            let handled = false; // Flag to ensure promise resolved/rejected only once

            if (requestUrl.pathname === '/github_callback') {
                if (query.error) {
                    const errorMsg = `GitHub Auth Error: ${query.error} (${query.error_description || 'No desc.'})`;
                    console.error(`[TempServer] ${errorMsg}`);
                    if (rejectRedirectPromise && !handled) { handled = true; rejectRedirectPromise(new Error(errorMsg)); }
                    res.writeHead(400, { 'Content-Type': 'text/html' });
                    res.end(`<html><head><title>OAuth Error</title></head><body><h1>OAuth Error</h1><p>${errorMsg}</p><p>You can close this window.</p><script>window.close();</script></body></html>`);
                } else if (query.code) {
                    console.log("[TempServer] Authorization code received.");
                    if (resolveRedirectPromise && !handled) { handled = true; resolveRedirectPromise(query.code); }
                    res.writeHead(200, { 'Content-Type': 'text/html' });
                    res.end("<html><head><title>Success!</title></head><body><h1>Success!</h1><p>Authentication successful. You can close this window now.</p><script>window.close();</script></body></html>");
                } else {
                    const errorMsg = "Invalid callback request received (missing code/error).";
                    console.error(`[TempServer] ${errorMsg}`);
                    if (rejectRedirectPromise && !handled) { handled = true; rejectRedirectPromise(new Error(errorMsg)); }
                    res.writeHead(400, { 'Content-Type': 'text/html' });
                    res.end(`<html><head><title>Error</title></head><body><h1>Error</h1><p>${errorMsg}</p><script>window.close();</script></body></html>`);
                }
                closeTemporaryRedirectServer(); // Close after handling
            } else {
                 res.writeHead(404); res.end('Not Found by Temp Server');
            }
        }).listen(REDIRECT_PORT, REDIRECT_HOST, () => {
            console.log(`[TempServer] Listening on ${REDIRECT_URI}`);
        });
        tempServer.on('error', (err) => {
            console.error(`[TempServer] Server error: ${err}`);
             if (rejectRedirectPromise) {
                 if (err.code === 'EADDRINUSE') {
                     rejectRedirectPromise(new Error(`Port ${REDIRECT_PORT} already in use. Please close the other application or change REDIRECT_PORT in main.js and GitHub App settings.`));
                 } else {
                     rejectRedirectPromise(err);
                 }
             }
            closeTemporaryRedirectServer();
        });
    });
}
// --- Helper: Close Temporary Redirect Server ---
function closeTemporaryRedirectServer() {
    if (tempServer) {
        tempServer.close(() => { console.log('[TempServer] Closed.'); tempServer = null; resolveRedirectPromise = null; rejectRedirectPromise = null; });
    } else { 
        resolveRedirectPromise = null; 
        rejectRedirectPromise = null; 
    }
}
// --- Helper: Exchange Code for Token ---
async function exchangeCodeForToken(code) {
    console.log('[Main Process] Exchanging authorization code for access token...');
    return new Promise((resolve, reject) => {
        const postData = querystring.stringify({
            client_id: GITHUB_CLIENT_ID_MAIN,
            client_secret: GITHUB_CLIENT_SECRET_MAIN,
            code: code,
            redirect_uri: REDIRECT_URI,
        });

        const options = {
            hostname: 'github.com',
            port: 443,
            path: '/login/oauth/access_token',
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': Buffer.byteLength(postData),
                'Accept': 'application/json' // Request JSON response
            }
        };

        const req = https.request(options, (res) => {
            let responseBody = '';
            res.on('data', (chunk) => { responseBody += chunk; });
            res.on('end', () => {
                try {
                    if (res.statusCode >= 200 && res.statusCode < 300) {
                        const parsedBody = JSON.parse(responseBody);
                        if (parsedBody.access_token) {
                            console.log('[Main Process] Access token obtained successfully.');
                            resolve(parsedBody.access_token);
                        } else if (parsedBody.error) {
                            reject(new Error(`GitHub Token Exchange Error: ${parsedBody.error} (${parsedBody.error_description || 'No description'})`));
                        } else {
                            reject(new Error('Invalid response format from GitHub token endpoint.'));
                        }
                    } else {
                        reject(new Error(`GitHub Token Exchange Failed: Status Code ${res.statusCode}. Response: ${responseBody}`));
                    }
                } catch (e) {
                    reject(new Error(`Error parsing GitHub token response: ${e.message}. Response: ${responseBody}`));
                }
            });
        });

        req.on('error', (e) => {
            console.error('[Main Process] Error during token exchange request:', e);
            reject(new Error(`Network error during token exchange: ${e.message}`));
        });

        req.write(postData);
        req.end();
    });
}

// --- Helper: Send Token to Backend ---
async function sendTokenToBackend(accessToken) {
     console.log(`[Main Process] Sending token to backend at ${BACKEND_URL}/auth/github/token`);
     return new Promise((resolve, reject) => {
         const postData = JSON.stringify({ token: accessToken });
         const backendUrlParts = url.parse(BACKEND_URL + '/auth/github/token');

         const options = {
             hostname: backendUrlParts.hostname,
             port: backendUrlParts.port || (backendUrlParts.protocol === 'https:' ? 443 : 80),
             path: backendUrlParts.pathname,
             method: 'POST',
             headers: {
                 'Content-Type': 'application/json',
                 'Content-Length': Buffer.byteLength(postData)
             }
         };

         const req = (backendUrlParts.protocol === 'https:' ? https : http).request(options, (res) => {
             let responseBody = '';
             res.on('data', (chunk) => { responseBody += chunk; });
             res.on('end', () => {
                 if (res.statusCode >= 200 && res.statusCode < 300) {
                     console.log('[Main Process] Token successfully sent to backend.');
                     resolve({ success: true, response: responseBody });
                 } else {
                     console.error(`[Main Process] Backend notification failed: Status ${res.statusCode}. Response: ${responseBody}`);
                     reject(new Error(`Backend error (Status ${res.statusCode}): ${responseBody || 'No response body'}`));
                 }
             });
         });

         req.on('error', (e) => {
             console.error('[Main Process] Error sending token to backend:', e);
             reject(new Error(`Network error sending token to backend: ${e.message}`));
         });

         req.write(postData);
         req.end();
     });
}

// --- End Helper Functions ---

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

   // --- Setup Functional IPC Handlers --- 
   // JWT Placeholders (Keep for now)
   ipcMain.handle('secure-jwt-save', async (event, token) => { console.warn("IPC: secure-jwt-save not implemented"); return { success: false, error: 'Not implemented' }; });
   ipcMain.handle('secure-jwt-get', async (event) => { console.warn("IPC: secure-jwt-get not implemented"); return { success: false, token: null, error: 'Not implemented' }; });
   ipcMain.handle('secure-jwt-delete', async (event) => { console.warn("IPC: secure-jwt-delete not implemented"); return { success: false, error: 'Not implemented' }; });

   // Functional Keytar Handlers (Replacing Placeholders)
   if (keytar) { 
        console.log("[Main Process] Configuring Functional Keytar IPC handlers...");
        ipcMain.handle('secure-keytar-get', async (event, { service, account }) => {
            console.log(`IPC: Handling 'secure-keytar-get' for service=${service}, account=${account}`);
            if (!keytar) return { success: false, error: 'Keytar unavailable.' };
            try {
                const secret = await keytar.getPassword(service, account);
                if (secret) {
                     console.log(`IPC: Secret retrieved for ${service}/${account}`);
                     return { success: true, secret: secret };
                 } else {
                     console.log(`IPC: No secret found for ${service}/${account}`);
                     return { success: true, secret: null };
                 }
            } catch (error) {
                console.error(`IPC: Error getting secret for ${service}/${account}:`, error);
                return { success: false, error: error.message || 'Failed to get secret' };
            }
        });
        ipcMain.handle('secure-keytar-save', async (event, { service, account, secret }) => { 
             console.log(`IPC: Handling 'secure-keytar-save' for service=${service}, account=${account}`);
            if (!keytar) return { success: false, error: 'Keytar unavailable.' };
            if (!secret) return { success: false, error: 'Cannot save empty secret.' };
            try {
                await keytar.setPassword(service, account, secret);
                console.log(`IPC: Secret saved successfully for ${service}/${account}`);
                return { success: true };
            } catch (error) {
                console.error(`IPC: Error saving secret for ${service}/${account}:`, error);
                return { success: false, error: error.message || 'Failed to save secret' };
            }
        });
         ipcMain.handle('secure-keytar-delete', async (event, { service, account }) => {
             console.log(`IPC: Handling 'secure-keytar-delete' for service=${service}, account=${account}`);
             if (!keytar) return { success: false, error: 'Keytar unavailable.' };
             try {
                 const deleted = await keytar.deletePassword(service, account);
                 if(deleted) {
                     console.log(`IPC: Secret deleted successfully for ${service}/${account}`);
                     return { success: true, deleted: true };
                 } else {
                     console.log(`IPC: No secret found to delete for ${service}/${account}`);
                     return { success: true, deleted: false };
                 }
             } catch (error) {
                 console.error(`IPC: Error deleting secret for ${service}/${account}:`, error);
                 return { success: false, error: error.message || 'Failed to delete secret' };
             }
         });
    } else { 
        console.error("[Main Process] IPC: Keytar unavailable, configuring fallback error handlers."); 
        const keytarError = { success: false, error: 'Secure storage (keytar) unavailable.' };
        ipcMain.handle('secure-keytar-get', async () => keytarError);
        ipcMain.handle('secure-keytar-save', async () => keytarError);
        ipcMain.handle('secure-keytar-delete', async () => keytarError);
    }

   // Functional GitHub Auth Handler (Day 26.1 - Replacing Placeholder)
   ipcMain.handle('start-github-auth', async () => {
        console.log("IPC: Handling 'start-github-auth' functional request...");
        if (!githubCredentialsOk) return { success: false, error: 'GitHub credentials misconfigured.' };
        if (!keytar) return { success: false, error: 'Secure storage (keytar) unavailable.' };

        let authorizationCode = null; 
        let serverCleanupTimer = null;
        
        const cleanup = () => {
            if (serverCleanupTimer) clearTimeout(serverCleanupTimer);
            closeTemporaryRedirectServer();
        };

        try {
            // Start server and set a timeout
            const serverPromise = startTemporaryRedirectServer();
            serverCleanupTimer = setTimeout(() => {
                 console.warn("[Main Process] GitHub auth timed out waiting for redirect.");
                 rejectRedirectPromise?.(new Error("GitHub authentication timed out."));
                 cleanup(); 
            }, 5 * 60 * 1000); 

            // Construct the GitHub URL
            const authUrl = new URL('https://github.com/login/oauth/authorize');
            authUrl.searchParams.append('client_id', GITHUB_CLIENT_ID_MAIN);
            authUrl.searchParams.append('redirect_uri', REDIRECT_URI);
            authUrl.searchParams.append('scope', 'repo user:email');
            const state = `DREAMERAI_CSRF_${Date.now()}_${Math.random().toString(36).substring(7)}`;
            authUrl.searchParams.append('state', state); 
            console.log(`[Main Process] Generated state for CSRF: ${state}`);
            console.log(`[Main Process] GitHub Auth URL: ${authUrl.toString()}`);

            // --- Fire-and-forget opening the actual GitHub URL --- 
            console.log("[Main Process] Opening external browser for GitHub auth (fire-and-forget)...");
            shell.openExternal(authUrl.toString()); // No await, no check
            console.log("[Main Process] shell.openExternal called. Proceeding to wait for redirect...");
            // --- End Fire-and-forget ---

            console.log("[Main Process] Waiting for authorization code from temporary server...");
            authorizationCode = await serverPromise;
            if (!authorizationCode) throw new Error("Authentication code not received from redirect.");

            // TODO V2: Verify received state matches stored state

            const accessToken = await exchangeCodeForToken(authorizationCode);
            if (!accessToken) throw new Error("Failed to exchange code for access token.");

            console.log("[Main Process] Storing GitHub token securely via Keytar...");
            await keytar.setPassword(GITHUB_KEYCHAIN_SERVICE, GITHUB_KEYCHAIN_ACCOUNT, accessToken);
            console.log("[Main Process] GitHub token stored successfully in Keytar.");

            console.log("[Main Process] Notifying backend of new GitHub token...");
            await sendTokenToBackend(accessToken);

            console.log("[Main Process] GitHub OAuth flow completed successfully!");
            cleanup(); 
            return { success: true };

        } catch (error) {
             console.error("[Main Process] GitHub OAuth Flow Error:", error);
             cleanup(); 
             return { success: false, error: error.message || "Unknown GitHub OAuth error." };
        }
   });
   console.log("[Main Process] Functional IPC handlers configured (Keytar, GitHub Auth).");
   // ---------------------------------------------------------------------- //

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
  let bridgeServer = null; // Define bridgeServer here or ensure it's accessible
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

// Add handler to cleanup temp server on quit
app.on('will-quit', () => {
     console.log("[Main Process] App quitting, ensuring temp server is closed.");
     closeTemporaryRedirectServer();
}); 