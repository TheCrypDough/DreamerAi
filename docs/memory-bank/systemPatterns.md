# DreamerAI System Patterns (V2.0 - As of End of Day 18)
Last Updated: [2025-04-19 18:00:45] (Reflecting last relevant system state update)
This document describes the core architectural patterns, communication methods, and design strategies employed in the DreamerAI V1 system.
1. Overall Architecture Pattern
Multi-Agent System (MAS) Orchestrated by Workflow: The core intelligence resides in a team of ~28 specialized Python agents (engine/agents/). Their execution is managed by a central workflow orchestrator (engine/core/workflow.py - DreamerFlow).
Desktop Application Shell with Backend Service: The user interacts via a desktop application built with Electron (app/main.js). The UI is rendered using React/MUI (app/src/App.jsx, app/components/). Core logic, agent execution, and data access are handled by a separate Python backend service built with FastAPI (engine/core/server.py).
Configuration-Driven: Key behaviors, model selections, API keys, and paths are managed via configuration files (config.dev.toml, .env.development) loaded at runtime (D1).
Modular Design: Aims for separation of concerns (UI, Backend API, Core Logic, Agent Logic, Data Layer).
2. Core Component Patterns
BaseAgent Class (engine/agents/base.py): Abstract base class (V2 Refactor D72) provides common functionality inherited by all specialized agents:
State Management: Finite states (Idle, Running, Finished, Error) with property setter potentially publishing events (via EventManager V1).
Memory Persistence: Agent conversation/operational history (self.memory) saved/loaded to/from JSON files (Users/.../Chats/[AgentName]/memory.json) on shutdown/init.
RAG Integration: Standardized connection (_initialize_rag_db) and interaction (query_rag, store_in_rag helpers) with agent-specific ChromaDB vector databases (data/rag_dbs/rag_*.db/) using SentenceTransformer embeddings.
Rules Loading: Loads rules_*.md content into self.rules_content.
Logger: Bound Loguru instance per agent.
LLM Access: Configurable LLM instance (self.llm).
Hybrid LLM (engine/ai/llm.py): Abstracts LLM interaction. Dynamically selects providers (Ollama, OpenRouter V1) based on config and agent requests. Includes Redis caching layer (V1 Setup D38, connection currently fails D18). Implements fallback logic.
Workflow Orchestrator (engine/core/workflow.py): DreamerFlow class manages the sequence of agent execution for core project lifecycle tasks. V2 orchestrates Jeff -> Arch -> Nexus (V1 Sim) sequence (D16). Future versions integrate QA loop, other agents, and potentially alternative execution graphs (modes D85+).
Database Layer (engine/core/db.py): V1 uses DreamerDB class encapsulating SQLite3 interactions (dreamer.db). V2+ Planned (D98+) migration to PostgreSQL using psycopg (async driver installed) and likely DreamerDB_PG class refactor.
Dependency Injection (DI - Planned D103): dependency-injector library planned to manage instantiation and injection of core services (DB Pool, LLM, EventManager, StatusManager) primarily into FastAPI endpoints V1. Currently relies on global instances or direct imports V1.
Frontend UI (app/src/App.jsx): Central React component managing main layout (Tabs, Header), core UI state (Theme, Language, Error), and V1 WebSocket/Bridge listener integration. Renders panel components based on active tab.
3. Communication Patterns
Backend <-> Frontend (Primary V1):
UI Bridge (HTTP Push): Backend agents use a helper (engine/core/bridge.py) calling aiohttp.post to send JSON messages to a dedicated HTTP listener server (http://localhost:3131/update) running within the App.jsx frontend component (Setup D13). Primarily used for Jeff's direct chat responses V1.
API Calls (HTTP Request/Response): Frontend UI components use standard fetch to call FastAPI backend API endpoints (http://localhost:8000/...) for actions like sending chat messages (D14), managing projects/subprojects (D23/D34), triggering VC (D28), triggering distillation (D65), getting tool info (D52), managing marketplace (D53/D54). Authentication uses internal JWT Bearer token (Setup D101/D105/D106).
WebSockets (Dream Theatre - V1 Setup): Backend (server.py) includes ConnectionManager and /ws/dreamtheatre endpoint using FastAPI WebSockets (Setup D62). BaseAgent state changes publish events via EventManager V1. A backend listener subscribes to these events and calls the ConnectionManager.broadcast method. Frontend (DreamTheatrePanel.jsx) uses ws client to connect (Setup D20). Refactor D62.1 moved WS connection mgmt to App.jsx for persistence. Displays basic agent status updates received.
Backend Internal (Agent-to-Agent):
Direct Calls (V1/V2): Primarily used within main.py tests or early workflow steps where agents directly call methods on other agent instances (e.g., LewisAgent V2 calling RiddickAgent.run D52, NexusAgent V2 calling Specialists D84). Requires passing agent dictionary (agents: Dict[str, BaseAgent]) during initialization.
Workflow Orchestration (DreamerFlow): Acts as the primary coordinator, sequentially calling agent.run() methods (V6 D93 currently manages Prompt->Jeff->Arch->Nexus->Bastion(S)->Herc(S)->Scribe(S)->Nike(S)).
EventManager (engine/core/event_manager.py): Basic asynchronous Pub/Sub system (V1 D45). Agents can publish events (e.g., status changes D62, task assignments D77). Other agents/listeners can subscribe and react. Used by WebSocket broadcaster V1. Planned primary mechanism for decoupling agent interactions V2+.
n8n Webhook Trigger (V1 Handoff): Jeff V2+ functionally calls an external n8n webhook URL (via aiohttp POST D33) to delegate identified tasks asynchronously, decoupling from the main workflow execution. Processing/routing within n8n deferred.
4. Security Patterns
Authentication: Firebase Authentication (Google Sign-In V1 D56) for primary user identity. Backend verifies Firebase ID Token (D74/D101).
Authorization: Backend uses internal short-lived JWTs signed by server (D101). Sensitive API endpoints use FastAPI Dependency (get_current_active_user D106) to verify JWT and fetch authenticated user context from DB. Endpoint logic performs ownership checks based on user context.
Secret Management: API Keys, DB passwords, JWT secret stored in .env.development, loaded via python-dotenv (D1). Excluded via .gitignore. CRITICAL TODO: GitHub Client Secret still insecure placeholder V1.1 in frontend (D107).
Secure Token Storage: Internal JWT stored using Electron safeStorage via secure IPC channel (window.electronAPI.invoke(...)) managed by main process (D105). GitHub token uses keytar via similar IPC (D66). Backend V1 uses local keytar for GitHub token (D66) - platform dependent, needs refactor/user scoping.
Encryption: cryptography.fernet utilities (engine/core/security_utils.py D48) for symmetric encryption. DREAMERAI_ENCRYPTION_KEY required in .env. Used for Cloud Sync V1 data at rest (D74).
Dependency Scanning: Manual run V1 (pip-audit, npm audit D67). Functional agent (Bastion V2 D80) implements scans via subprocess.
Electron Security: contextIsolation: true, nodeIntegration: false set (D66). Secure preload.js using contextBridge exposes minimal functionality via IPC.
5. Error Handling & Resilience
Basic Try/Except: Most agent run methods and core functions include basic try...except Exception blocks with logging (logger.exception).
HTTPExceptions: FastAPI endpoints use HTTPException for standard API error responses (4xx/5xx).
Graceful Fallbacks: LLM class includes provider fallback (D6). Promptimizer fallback to raw input (D30). Cache failures don't block LLM (D38).
Resilience (Planned): Retries via tenacity (D117), Circuit Breakers via pybreaker (D138). Ogre Agent (V1 placeholder D58) planned for automated log analysis (V2 D90) and fixes (V3+).
QA Loop: DreamerFlow V6 (D93) structurally checks Herc/Bastion V2 results and halts flow on failure (simulated V1 routing back).
6. Testing Patterns
Manual Testing: Primary method V1 (via main.py, API calls, UI interaction). E2E manual testing crucial pre-launch (D70).
Unit Testing (Framework): pytest installed, tests/ structure created, pyproject.toml configured (D39). Basic unit tests exist (test_project_manager_utils.py D39). Requires expansion. Mocking via pytest-mock planned (Ref: 10.68).
Integration Testing: Current testing via main.py performs basic integration checks. Formal integration test suite planned (Ref: 10.99).
QA Agent Testing: Herc V2 runs pytest via subprocess (D79). Bastion V2 runs dep scans (D80).