const { app, BrowserWindow, ipcMain, safeStorage, shell } = require('electron');
const path = require('path');

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
  app.quit();
}

// Assume keytar require/check from Day 66/105 remains for secure token *storage* later
let keytar = null;
try {
    keytar = require('keytar');
    console.log("[Main Process] Keytar loaded successfully.");
} catch (error) {
     console.error("[Main Process] Failed to load keytar. Secure GitHub token storage unavailable.", error);
     keytar = null;
}
const GITHUB_KEYCHAIN_SERVICE_APP_V2 = 'DreamerAI_GitHub_App_V2'; // Use V2 service name
const GITHUB_KEYCHAIN_ACCOUNT_APP = 'user_github_token';
// -------------------------------------

// Keep secure JWT storage logic (D105)
let encryptedJwtBuffer = null;
let encryptionAvailable = false;
// ---------------------------------------------------------


// --- GitHub Config Check (Essential for D26.1+ Flow) ---
// Load .env.development from data/config relative to C:\DreamerAI
// Assumes 'dotenv' installed in 'app/' directory
try {
    // Correct path assuming main.js is in app/
    require('dotenv').config({ path: path.resolve(__dirname, '../data/config/.env.development') });
    console.log("[Main Process] dotenv: Attempted to load .env.development");
} catch (err) {
    console.error("[Main Process] dotenv: Failed to load .env.development:", err);
}

const GITHUB_CLIENT_ID_MAIN = process.env.GITHUB_CLIENT_ID;
const GITHUB_CLIENT_SECRET_MAIN = process.env.GITHUB_CLIENT_SECRET; // KEEP IN MAIN ONLY
let githubCredentialsOk = true;

if (!GITHUB_CLIENT_ID_MAIN || GITHUB_CLIENT_ID_MAIN.includes("YOUR_")) {
    console.warn("Main: GitHub Client ID missing/placeholder in environment.");
    githubCredentialsOk = false;
}
if (!GITHUB_CLIENT_SECRET_MAIN || GITHUB_CLIENT_SECRET_MAIN.includes("YOUR_")) {
    console.warn("Main: GitHub Client Secret missing/placeholder in environment.");
    githubCredentialsOk = false;
}

if (githubCredentialsOk) {
    console.log("Main: GitHub Client ID/Secret appear configured (Ready for D26.1+).");
} else {
    console.error("!!! CRITICAL SETUP ISSUE: GitHub credentials missing/placeholders in environment. OAuth flow WILL fail later. !!!");
}
// ------------------------------------------------------

const createWindow = () => {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 1400, // Increased size
    height: 900,
    webPreferences: {
      // preload: path.join(__dirname, 'preload.js'), // Old insecure way
      // --- Ensure preload points to Webpack entry ---
      preload: MAIN_WINDOW_PRELOAD_WEBPACK_ENTRY, // Use Webpack preload entry
      // --- Security Hardening (From D66/Guide) ---
      nodeIntegration: false, // Disable Node.js in renderer
      contextIsolation: true, // Enable context isolation
      sandbox: false, // Default false, consider enabling later if feasible
      // --- Enable DevTools if not packaged ---
      devTools: !app.isPackaged
    }
  });

  // Load the URL for the windows.
  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) { // Use VITE URLs if provided by Forge V6+
    console.log(`[Main Process] Loading Renderer URL: ${MAIN_WINDOW_VITE_DEV_SERVER_URL}`);
    mainWindow.loadURL(MAIN_WINDOW_VITE_DEV_SERVER_URL);
  } else if (MAIN_WINDOW_WEBPACK_ENTRY) { // Fallback for older Forge/Webpack
    console.log(`[Main Process] Loading Renderer File: ${MAIN_WINDOW_WEBPACK_ENTRY}`);
    mainWindow.loadURL(MAIN_WINDOW_WEBPACK_ENTRY); // Use Webpack main window entry
  } else {
    // Fallback if neither Webpack nor Vite URLs are defined (should not happen with standard Forge setup)
    const indexPath = path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME || 'main_window'}/index.html`);
    console.error(`[Main Process] Critical Error: Cannot find entry point URL. Falling back to: ${indexPath}`);
    mainWindow.loadFile(indexPath);
  }

  // Open DevTools automatically if not packaged
  if (!app.isPackaged) {
    mainWindow.webContents.openDevTools();
  }
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  console.log("[Main Process] App Ready.");

  // --- Check safeStorage Availability (From D105) ---
  encryptionAvailable = safeStorage.isEncryptionAvailable();
  if (!encryptionAvailable) {
    console.warn("************************************************************");
    console.warn("WARNING: safeStorage encryption NOT AVAILABLE on this system!");
    console.warn("         Internal JWT session token cannot be stored securely.");
    console.warn("************************************************************");
  } else {
    console.log("[Main Process] safeStorage encryption is available.");
  }
  // ---------------------------------

  // --- Setup IPC Handlers ---
  console.log("[Main Process] Setting up IPC Handlers...");

  // Keep JWT ('secure-jwt-*') handlers (From D105)
  ipcMain.handle('secure-jwt-save', async (event, token) => {
    console.log(`IPC >> Received 'secure-jwt-save'`);
    if (!encryptionAvailable) { console.error("IPC << safeStorage unavailable."); return { success: false, error: "Encryption unavailable." }; }
    if (!token || typeof token !== 'string') return { success: false, error: "Invalid JWT provided." };
    try {
      encryptedJwtBuffer = safeStorage.encryptString(token);
      console.log(`IPC << Internal JWT encrypted via safeStorage (Size: ${encryptedJwtBuffer?.length || 0} bytes).`);
      return { success: true };
    } catch (error) { console.error(`IPC secure-jwt-save Error: ${error}`); encryptedJwtBuffer = null; return { success: false, error: error.message }; }
  });
   ipcMain.handle('secure-jwt-get', async (event) => {
    console.log(`IPC >> Received 'secure-jwt-get'`);
    if (!encryptionAvailable) { console.error("IPC << safeStorage unavailable."); return { success: false, error: "Encryption unavailable.", token: null }; }
    if (!encryptedJwtBuffer) { console.log("IPC << No internal JWT currently stored."); return { success: true, token: null }; } // Return success/null if empty
    try {
      const decryptedToken = safeStorage.decryptString(encryptedJwtBuffer);
      console.log(`IPC << Internal JWT decrypted via safeStorage.`);
      return { success: true, token: decryptedToken };
    } catch (error) { console.error(`IPC secure-jwt-get Error: ${error}`); encryptedJwtBuffer = null; return { success: false, error: error.message, token: null }; }
  });
  ipcMain.handle('secure-jwt-delete', async (event) => {
    console.log(`IPC >> Received 'secure-jwt-delete'`);
    encryptedJwtBuffer = null; // Simply clear the buffer V1
    console.log(`IPC << Internal JWT cleared.`);
    return { success: true };
  });


  // Keep Keytar ('secure-keytar-*') handlers (From D66 - For storing GH token later in D26.1+)
  if (keytar) {
    ipcMain.handle('secure-keytar-save', async (event, { service, account, token }) => {
      console.log(`IPC >> Received 'secure-keytar-save' for service: ${service}`);
      if (!keytar) { console.error("IPC << Keytar unavailable."); return { success: false, error: "Keytar unavailable." }; }
      if (!service || !account || !token) return { success: false, error: "Missing service, account, or token."};
      // Enforce specific service/account for GitHub token for security V2
      if (service !== GITHUB_KEYCHAIN_SERVICE_APP_V2 || account !== GITHUB_KEYCHAIN_ACCOUNT_APP) {
         console.error(`IPC << Denied keytar save for unexpected service/account: ${service}/${account}`);
         return { success: false, error: "Invalid service/account for GitHub token." };
      }
      try {
        await keytar.setPassword(service, account, token);
        console.log(`IPC << GitHub Token stored via keytar (Service: ${service}).`);
        return { success: true };
      } catch (error) { console.error(`IPC secure-keytar-save Error: ${error}`); return { success: false, error: error.message }; }
    });
    ipcMain.handle('secure-keytar-get', async (event, { service, account }) => {
      console.log(`IPC >> Received 'secure-keytar-get' for service: ${service}`);
      if (!keytar) { console.error("IPC << Keytar unavailable."); return { success: false, error: "Keytar unavailable.", token: null }; }
      if (!service || !account) return { success: false, error: "Missing service or account.", token: null };
      // Enforce specific service/account
       if (service !== GITHUB_KEYCHAIN_SERVICE_APP_V2 || account !== GITHUB_KEYCHAIN_ACCOUNT_APP) {
           console.error(`IPC << Denied keytar get for unexpected service/account: ${service}/${account}`);
           return { success: false, error: "Invalid service/account for GitHub token.", token: null };
      }
      try {
        const token = await keytar.getPassword(service, account);
        console.log(`IPC << GitHub Token retrieved via keytar (Token Found: ${!!token}).`);
        return { success: true, token: token }; // Returns token string or null
      } catch (error) { console.error(`IPC secure-keytar-get Error: ${error}`); return { success: false, error: error.message, token: null }; }
    });
    ipcMain.handle('secure-keytar-delete', async (event, { service, account }) => {
      console.log(`IPC >> Received 'secure-keytar-delete' for service: ${service}`);
      if (!keytar) { console.error("IPC << Keytar unavailable."); return { success: false, error: "Keytar unavailable." }; }
       if (!service || !account) return { success: false, error: "Missing service or account."};
       // Enforce specific service/account
       if (service !== GITHUB_KEYCHAIN_SERVICE_APP_V2 || account !== GITHUB_KEYCHAIN_ACCOUNT_APP) {
           console.error(`IPC << Denied keytar delete for unexpected service/account: ${service}/${account}`);
           return { success: false, error: "Invalid service/account for GitHub token." };
      }
      try {
        const success = await keytar.deletePassword(service, account);
        console.log(`IPC << GitHub Token delete status via keytar: ${success}`);
        return { success: success };
      } catch (error) { console.error(`IPC secure-keytar-delete Error: ${error}`); return { success: false, error: error.message }; }
    });
  } else {
    // Setup fallback handlers if keytar failed to load
    const keytarError = { success: false, error: "Keytar module failed to load in main process." };
    ipcMain.handle('secure-keytar-save', async () => keytarError);
    ipcMain.handle('secure-keytar-get', async () => ({ ...keytarError, token: null }));
    ipcMain.handle('secure-keytar-delete', async () => keytarError);
    console.error("IPC: Keytar handlers setup with error fallback as module failed to load.");
  }


  // --- NEW V2 GitHub OAuth Trigger IPC Handler Placeholder ---
  ipcMain.handle('start-github-auth', async () => {
    console.log("IPC >> Received 'start-github-auth' request.");
    if (!githubCredentialsOk) {
      const errorMsg = 'GitHub credentials incorrectly configured in main process environment.';
      console.error(`IPC << Error for 'start-github-auth': ${errorMsg}`);
      return { success: false, error: errorMsg };
    }
    // TODO D26.1+: Implement Main Process OAuth Flow logic HERE
    //      1. Generate state parameter, store it temporarily (e.g., in memory)
    //      2. Construct the GitHub authorization URL (include client_id, scope, state, redirect_uri - maybe handled internally?)
    //      3. Use shell.openExternal(authUrl) to open the user's default browser
    //      4. Setup handler for custom protocol redirect (dreamerai://oauth/github/callback?code=...&state=...) OR listen on localhost for redirect
    //      5. In handler: Validate state parameter.
    //      6. Use `fetch` or similar in main process to POST code + client_id + client_secret to GitHub token endpoint
    //      7. Receive access token.
    //      8. Securely store token using `keytar.setPassword(GITHUB_KEYCHAIN_SERVICE_APP_V2, GITHUB_KEYCHAIN_ACCOUNT_APP, token)`
    //      9. Return success/failure to the invoking renderer process.
    //      10. Optionally, send event back to UI to update status proactively?
    console.warn("<<<<< TODO D26.1+: Implement Main Process GitHub OAuth Flow logic here. See comments. >>>>>");
    // Return placeholder failure for Day 26
    return { success: false, error: 'Main process GitHub OAuth flow not implemented yet (Planned D26.1+).' };
  });
  // ---------------------------------------------------

  console.log("[Main Process] IPC Handlers Setup Complete.");
  // -----------------------------

  createWindow(); // Create window AFTER handlers are setup

  app.on('activate', () => {
    // On OS X it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// In this file, you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here. 