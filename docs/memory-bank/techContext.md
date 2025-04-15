# DreamerAI Tech Context (V1 - Placeholder)

**Languages:** Python 3.12+, Node.js 20+.
**Frameworks:** FastAPI, Electron, React.
**UI Libs:** Material-UI (MUI).
**Databases:** SQLite3 (Dev V1), ChromaDB (RAG V1), PostgreSQL (Planned Prod). Redis (Cache V1).
**AI Libs:** sentence-transformers, lightrag, chromadb, transformers (planned), datasets (planned), ollama (client).
**DevOps:** Git/GitHub, Docker/Compose (planned), Pytest (planned).
**Key Python Libs:** pydantic, loguru, python-dotenv, tomllib, psycopg (planned), dependency-injector (planned), etc.
**Key Node Libs:** i18next, keytar, firebase, electron-oauth2 (planned), posthog-js (planned), etc.

# Technical Context

## Technologies Used (Initial Setup - Day 1)
- **Version Control:** Git
- **Repository Hosting:** GitHub (TheCrypDough/DreamerAi)
- **Configuration:** TOML (`config.dev.toml`), DotEnv (`.env.development`)
- **Shell:** Windows Command Prompt (for manual script execution), PowerShell (for tool commands)
- **Planned AI Models:** OpenRouter (Cloud - Llama 3 70B default), Ollama (Local - gemma3:12b default)
- **Operating System:** Windows 11 Pro (on Builder PC)

## Development Setup (Initial)
- **Project Root:** `C:\DreamerAI`
- **Local Models Path:** `C:\Users\thecr\.ollama\models` (linked via `C:\DreamerAI\data\models` symlink)
- **Secrets Management:** `OPENROUTER_API_KEY` stored in `.env.development` (requires manual user update).
- **Environment Management:** None setup yet (Pending Day 2 - Python venv).

## Technical Constraints
- Requires Git installation.
- Requires Ollama installation & `gemma3:12b` model pulled.
- `mklink` command requires Administrator privileges (bypassed Day 1 via pre-existing link).
- Cursor tool limitations encountered with complex batch script execution.

## Dependencies (Initial)
- None installed yet (Pending Day 2 - `requirements.txt`).
