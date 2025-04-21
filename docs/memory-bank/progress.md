# Project Progress
*Last Updated: 2024-07-28 17:30:00*

## Overview
DreamerAI development is progressing steadily, having completed the initial setup, environment configuration, core backend components (FastAPI server, BaseAgent V2, LLM integration, basic DB), Electron frontend shell with build process, several UI panels (Chat, Theatre, PM, Settings), basic orchestration (DreamerFlow V2), local version control backend, and the backend setup for GitHub authentication.

## What Works (Completed Functionality)
*   **Days 1-25 Foundations:** Project structure, Git repo, core documentation, Python venv, Node project setup, essential dependencies (Python/Node).
*   **Backend Core:** FastAPI server (`server.py`) running on port 8000, basic configuration loading (`config.dev.toml`, `.env.development`), Loguru logging (`logger.py`), SQLite DB (`db.py` - dev only), BaseAgent V2 (`base.py` - including RAG, memory, state), hybrid LLM module (`llm.py` - OpenRouter/Ollama), DreamerFlow V2 (`workflow.py` - orchestrating Jeff->Arch->Nexus V1 Sim).
*   **Frontend Shell:** Electron main process (`main.js`), basic React structure (`App.jsx`), Electron Forge build process (Webpack/Babel), placeholder UI panels integrated via MUI Tabs (`MainChatPanel.jsx`, `DreamTheatrePanel.jsx`, `ProjectManagerPanel.jsx`, `SettingsPanel.jsx`).
*   **Key Features (V1):**
    *   Basic Chat: UI (`MainChatPanel`) interaction with Jeff agent (`main_chat.py`) via API endpoint (`/agents/jeff/chat`).
    *   Dream Theatre: WebSocket connection (`ws://localhost:8091`) established between backend (`dream_theatre_service.py`, `server.py`) and frontend (`DreamTheatrePanel.jsx`) for broadcasting agent activity (tested with Jeff).
    *   Subproject Management: Backend API (`/projects/{id}/subprojects`) and UI (`ProjectManagerPanel.jsx`) for creating subprojects.
    *   Local Version Control: Backend (`version_control.py` using GitPython) for local repo init, stage, commit, status checks.
    *   GitHub Auth Prep: Backend endpoint (`/auth/github/token`) created and tested for receiving OAuth token.
*   **Tooling:** `.gitignore` configured, Black linter setup (via `pyproject.toml`), ESLint setup (`eslint.config.mjs`).

## What's Next (In Progress / Upcoming)
*   **Day 26: GitHub Auth UI:** Implementing frontend components (`GitHubSignIn.jsx`, `SettingsPanel.jsx`) using `electron-oauth2` and `keytar` to complete the GitHub login flow.
*   **Version Control:** Remote GitHub operations (push, pull, clone), UI integration for VC actions.
*   **Agent Development:** Implementing the remaining 27 agents and refining existing ones (Nexus, Lewis, Hermie V2+).
*   **UI Development:** Fleshing out UI panels with real functionality, implementing Dreamer Desktop layout (react-grid-layout), adding Dreamcoder interface.
*   **Core Features:** Refining message bridge (`bridge.py`), enhancing DreamerFlow orchestration, implementing SnapApp templates, Spark teaching engine.
*   **Infrastructure:** PostgreSQL migration plan, CI/CD setup (GitHub Actions), potential Dockerization.

## Current Status
*   Completed all tasks for Day 25.
*   Ready to begin Day 26, Task 1: Install Node dependencies for GitHub Auth UI.

## Known Issues & Blockers
*   **GitHub Token Storage:** Currently stored in a global variable in `server.py` (Insecure V1 placeholder).
*   **Dream Theatre Limitation:** Messages broadcast while the Dream Theatre tab is inactive are missed by the UI client.
*   **Missing DB Pool:** `initialize_db_pool`/`close_db_pool` functions in `db.py` are unimplemented (Mitigated with try/except).
*   **Lewis Test Failure:** `AttributeError: 'str' object has no attribute 'get'` during Lewis V1 test (Logged in `issues.log`).
*   **Port Discrepancy:** Backend server port was set to 8090 in `server.py` but test in `main.py` used 8000; Day 25 test succeeded using 8000. Needs verification/standardization (Guide implies 8000).
*   **Expected Failures:** Redis/n8n connections fail as services aren't running.
*   **LLM Errors:** Intermittent OpenRouter `TypeError` (mitigated with checks in `llm.py`).
*   **Tooling/Environment:** CSP warning (`unsafe-eval` in dev), unreliable terminal output capture, `npm audit` vulnerabilities (need investigation).
