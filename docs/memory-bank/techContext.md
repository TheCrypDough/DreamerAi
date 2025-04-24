# DreamerAI Tech Context (V2.0 - As of End of Day 18)
Last Updated: [2025-04-19 18:00:45] (Reflecting approximate time of last provided log)
This document details the current technical stack, configurations, environment details, constraints, and known issues relevant to the DreamerAI project development.
Core Languages & Runtimes
Python: 3.11.x (Explicitly downgraded from 3.13 during Day 2 dependency setup due to tiktoken/Rust build issues). Managed via venv.
Node.js: v20.x+ (Required for npm and Electron). Managed globally/system-wide.
Frameworks
Backend API: FastAPI (using uvicorn[standard] ASGI server - Setup Day 5, WS capability from standard).
Frontend UI Core: React.js (v18+ via createRoot - Setup Day 4, Build via Forge Day 10).
Desktop Shell: Electron (Setup Day 4, Build via Forge Day 10).
UI Libraries & Tools
Component Library: Material-UI (MUI Core: @mui/material, @emotion/react, @emotion/styled - Installed Day 2).
Note: @mui/lab (for TreeView) and @mui/icons-material are not yet installed as of Day 18.
Drag & Drop: @dnd-kit/core (Installed Day 2 - Replaces react-beautiful-dnd). Usage planned Day 146+.
Layout: react-grid-layout (Installed Day 2 - Usage planned for UI panel customization).
Build/Packaging: electron-forge with Webpack/Babel loaders (Setup Day 10 Deviation). electron-builder installed for installer generation (Setup Day 2/Config Day 68 plan).
Databases & Caching
Core Application DB (Dev): SQLite (dreamer.db file in data/db/ - Setup Day 5). Managed via engine/core/db.py (V1 SQLite3).
Core Application DB (Prod Plan): PostgreSQL (Migration planned Day 98+). psycopg driver installed (Day 2) but PG service/connection not yet active.
RAG Vector DB (Dev V1): ChromaDB (Persistent Client storing data in data/rag_dbs/rag_*.db/ directories - Setup Day 8 / BaseAgent V2 Day 72).
Caching: Redis Client library (redis-py) installed (Day 2). Redis server connection attempted by LLM class but fails (Service not running via Docker Compose D37+ yet). Caching is disabled. (Ref Error Log D18).
AI Libraries & Models
LLM Client (Cloud): openai library (used for OpenRouter API access - Setup Day 6).
LLM Client (Local): ollama library (Installed Day 2, Used Day 6). ollama serve required running manually.
LLM Access Wrapper: engine/ai/llm.py (V2: Config-driven OpenRouter/Ollama hybrid, Redis cache placeholder - D6).
Core Models (Configured V1):
cloud_tier1 (OpenRouter): google/gemini-2.5-pro-exp-03-25:free (Specified D6 Update) - Note: Log shows intermittent TypeError (NoneType not subscriptable) when calling this D18.
ollama: gemma3:12b (Default, requires manual pull)
RAG Embedding: sentence-transformers library (all-MiniLM-L6-v2 model - Setup BaseAgent V2 D72).
RAG Framework: lightrag library installed (Day 2 Corrected) but RAG logic in BaseAgent V2 uses chromadb API directly.
Fine-tuning (Planned): transformers, datasets, torch libraries installed (Day 2 Corrected) for future Distiller Agent (Billy V1 D64+).
Development Tools & DevOps
Version Control: Git / GitHub (TheCrypDough/DreamerAi) (Setup Day 1). GitPython library installed (D2). engine/core/version_control.py placeholder planned D24.
Environment Management: Python venv (Setup Day 2).
Package Managers: pip (Python), npm (Node.js).
Linters/Formatters: black (Python), eslint (JavaScript/React via eslint.config.mjs) (Setup D2).
Testing Framework: Pytest structure planned (Day 39).
Containerization (Planned): Docker / Docker Compose (Setup planned Day 36+).
Configuration: TOML (config.dev.toml), DotEnv (.env.development) (Setup Day 1). tomllib, python-dotenv libs used.
Key Libraries (Python)
pydantic (Data validation, BaseAgent models).
loguru (Logging - Setup Day 3).
aiohttp (Async HTTP for UI Bridge / n8n Handoff - Setup Day 13).
requests (Used by LLM Ollama check).
python-jose[cryptography] (JWT Planned D101+).
cryptography (Encryption Planned D48+).
fastapi, uvicorn[standard].
See requirements.txt for full list.
Key Libraries (Node)
react, react-dom.
electron.
@mui/material, @emotion/react, @emotion/styled.
i18next, react-i18next (i18n planned D60).
keytar (Auth token storage planned D26+).
firebase (Auth planned D56+).
ws (WebSocket client planned D20+).
See app/package.json for full list.
Networking & Communication
Backend API Server: FastAPI running on http://localhost:8000 (D5).
Frontend UI Bridge Listener: Node HTTP server in App.jsx running on http://localhost:3131 (D13 Fix) receiving POST /update.
WebSocket Server (Dream Theatre - Planned): Endpoint /ws/dreamtheatre on FastAPI server (ws://localhost:8000/...) planned (D62). Frontend listener setup (D20).
Internal Backend->Frontend: V1 uses aiohttp POST to Bridge Listener URL (D13). WebSocket planned V2+.
Internal Agent Comms: V1 uses direct Python calls (e.g., main.py). EventManager planned (D45+). Hermie routing planned (D19+).
External: LLM API calls (OpenRouter, Ollama), n8n Webhook POST (planned D33).
Known Constraints & Issues (End of Day 18)
Python Version: Requires Python 3.11 specifically due to Day 2 tiktoken build issue resolution (manual user action).
Manual Service Start: Requires ollama serve and n8n start (Day 33+) to be run manually in separate terminals for related features to function during testing.
Redis Cache: Redis client installed, but cache connection fails (ConnectionRefusedError) and cache is disabled because Redis server setup via Docker Compose is deferred (Day 38).
n8n Handoff: Functional n8n call logic exists in Jeff (D33 plan), but connection fails (ClientConnectorError) because n8n server isn't running/configured in test setup (Day 18 log).
UI Bridge: Bridge communication (backend aiohttp POST -> frontend Node HTTP listener) requires listener active on specific port (3131 after D13 fix) and CORS configuration on FastAPI allows this origin.
Missing DB Pool Functions: initialize_db_pool / close_db_pool were needed by main.py D18 test setup, but don't exist in the Day 5 SQLite db.py context. Handled via try/except ImportError in main.py. Full PG setup needed (Day 96+).
OpenRouter Intermittent Error: Logs occasionally show TypeError: 'NoneType' object is not subscriptable during _generate_openai_compatible (See D16, D18 Issues). The Ollama fallback currently mitigates this during testing. Needs monitoring.
Agent Development Status: Only core placeholders/V1 implementations exist for key agents. Many agents (Sophia, Spark, QA, Docs, Deploy, Specialists, Maintenance, etc.) are non-functional placeholders inheriting BaseAgent V2 as of Day 18.
Security: V1 security posture is basic. Known TODOs include secure GitHub secret handling (D107), robust session/auth context (D101/D106), full encryption implementation (D74), Electron hardening beyond defaults (D66), etc.
Test Environment: Tests primarily run via main.py script, direct agent calls, and manual UI checks. Formal Pytest framework setup planned (D39). Test artifact clutter in Users/ directory is a known issue to be addressed (Ref D109 Cleanup Plan).
(End of COMPLETE Updated techContext.md V2)
