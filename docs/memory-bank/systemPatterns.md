# System Patterns

*Last Updated: 2024-07-29 16:00:00*

## Architecture Overview

- **Hybrid Desktop Application:** Electron frontend (React, MUI) interacting with a Python backend (FastAPI).
- **Agent-Based Core:** Backend logic driven by specialized AI agents (inheriting `BaseAgent`) orchestrated by `DreamerFlow`.
- **UI Panels:** Frontend UI organized into distinct panels managed by `App.jsx` tabs (Chat, Dream Theatre, Project Manager, Settings, etc.).
- **Configuration Driven:** Behavior influenced by `.env.development` and `config.dev.toml`.
- **Local DB (Dev):** SQLite (`dreamer.db`) for initial development (projects, subprojects).
- **RAG:** ChromaDB with SentenceTransformers used for agent-specific knowledge bases (e.g., `rag_jeff.db`, `rag_nexus.db`), accessed via `BaseAgent` V2 helpers.
- **Local LLM Fallback:** Ollama configured as a fallback/alternative LLM provider.
- **Cloud LLM Primary:** OpenRouter configured as the primary LLM provider.
- **Version Control:** Git managed via Python (`GitPython`) for local operations; GitHub integration for remote operations and OAuth.

## Key Technical Decisions & Patterns

- **Build System:** Electron Forge with Webpack used for building and packaging the Electron app. Configuration files moved to project root.
- **Native Modules:** `electron-rebuild` used to compile native Node modules (like `keytar`) for the Electron environment.
- **Inter-Process Communication (IPC):**
    - **Secure IPC for Sensitive Ops:** `ipcMain.handle` / `ipcRenderer.invoke` used for actions requiring main process privileges or secret handling (e.g., GitHub OAuth `start-github-auth`). Preload script (`preload.js`) acts as a secure bridge, exposing only whitelisted channels.
    - **HTTP Bridge (V1 - Backend to Frontend):** Python backend (`engine/core/bridge.py`) sends messages via HTTP POST to a listener server running within the React frontend (`App.jsx` `useEffect` hook on port 3131).
    - **WebSocket Bridge (V2 - Backend to Frontend):** FastAPI backend (`engine/core/server.py`, `dream_theatre_service.py`) hosts a WebSocket endpoint (`/ws/dream_theatre`). Frontend (`DreamTheatrePanel.jsx`) connects to this for real-time updates using the native `WebSocket` API. A singleton `ConnectionManager` manages backend connections, allowing agents (`main_chat.py`) to broadcast messages.
- **GitHub Authentication (OAuth 2.0):**
    - **Main Process Flow:** The entire OAuth flow is handled securely within the Electron main process (`main.js`) to avoid exposing secrets to the renderer.
    - **Temporary Redirect Server:** A short-lived local HTTP server (`http://localhost:9876`) is programmatically started to catch the GitHub callback redirect.
    - **Secure Token Exchange:** Authorization code is exchanged for an access token via a direct HTTPS request from the main process to GitHub's token endpoint.
    - **Secure Storage:** The obtained access token is stored securely in the OS keychain using `keytar`.
    - **Backend Notification:** The token is POSTed to a backend endpoint (`/auth/github/token`) for backend use.
- **Agent Design (`BaseAgent` V2):**
    - Asynchronous `run` method as primary entry point.
    - Standardized methods for RAG (`query_rag`, `store_in_rag`).
    - Integrated memory management (`self.memory`).
    - State tracking (`self.state = AgentState.XYZ`).
    - Automatic rule loading (`self.rules_content`).
    - Centralized logging (`self.logger`).
    - UI communication via `self.send_update_to_ui` (currently uses HTTP Bridge V1).
- **Error Handling:** Standard `try...except` blocks, FastAPI `HTTPException`, agent state changes (`AgentState.ERROR`), logging via `loguru`.
- **Configuration Loading:** `tomllib` for TOML, `dotenv` for `.env` files.
- **Logging:** Centralized `loguru` setup (`logger.py`) writing to rotated files in `docs/logs/`.

## Component Relationships

```mermaid
graph TD
    subgraph Frontend (Electron Renderer Process)
        UI[React UI - App.jsx]
        ChatPanel[MainChatPanel.jsx]
        DreamTheatrePanel[DreamTheatrePanel.jsx]
        SettingsPanel[SettingsPanel.jsx]
        GitHubSignIn[GitHubSignIn.jsx]
        Preload[preload.js]
        HTTPListener[HTTP Listener Server (port 3131)]
        WSClient[WebSocket Client]
    end

    subgraph Electron Main Process
        MainJS[main.js]
        IPCMain[ipcMain]
        Keytar[keytar]
        Shell[shell]
        OAuthServer[Temp OAuth Server (port 9876)]
    end

    subgraph Backend (Python/FastAPI)
        Server[server.py - FastAPI App]
        Bridge[bridge.py]
        DB[db.py - DreamerDB SQLite]
        LLM[llm.py - LLM Class]
        Workflow[workflow.py - DreamerFlow]
        BaseAgent[base.py - BaseAgent V2]
        Jeff[main_chat.py - ChefJeff]
        Arch[planning.py - Arch]
        Nexus[coding_manager.py - Nexus]
        Hermie[communications.py - Hermie]
        Lewis[administrator.py - Lewis]
        VC[version_control.py]
        PM[project_manager.py]
        WSService[dream_theatre_service.py - ConnectionManager]
        Logger[logger.py]
        RAGDBs[data/rag_dbs/]
        Config[data/config/]
    end

    subgraph External Services
        GitHubAPI[GitHub API]
        OpenRouterAPI[OpenRouter API]
        Ollama[Local Ollama Server]
        OSKeychain[OS Keychain]
    end

    UI --> ChatPanel & DreamTheatrePanel & SettingsPanel
    SettingsPanel --> GitHubSignIn
    GitHubSignIn -- IPC Request ('start-github-auth') --> Preload -- Secure IPC --> IPCMain
    IPCMain -- Initiates Flow --> MainJS
    MainJS -- Launches Browser --> Shell
    MainJS -- Starts/Stops --> OAuthServer
    Browser -- Redirect --> OAuthServer
    MainJS -- Stores/Retrieves --> Keytar --> OSKeychain
    MainJS -- Exchanges Code --> GitHubAPI
    MainJS -- Sends Token --> Server

    ChatPanel -- Send Message (fetch) --> Server
    Server -- Delegates to --> Workflow
    Workflow -- Orchestrates --> Jeff & Arch & Nexus & Hermie & Lewis
    Jeff & Arch & Nexus & Hermie & Lewis -- Inherit from --> BaseAgent
    BaseAgent -- Uses --> LLM & DB & Logger & RAGDBs & Config
    BaseAgent -- Sends UI Update --> Bridge -- HTTP POST --> HTTPListener
    HTTPListener -- Updates State --> UI

    Server -- Hosts --> WSService
    WSClient -- Connects to --> WSService
    Jeff -- Broadcasts via --> WSService -- Sends Message --> WSClient
    WSClient -- Updates State --> DreamTheatrePanel

    LLM -- Calls --> OpenRouterAPI & Ollama
    VC -- Uses --> GitPython
    Server -- Uses --> PM & DB

    MainJS -- Loads Config --> Config
    Backend -- Loads Config --> Config
