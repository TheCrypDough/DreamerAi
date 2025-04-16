# Technical Context and Stack

**Last Updated:** 2024-07-27 18:35:00 # Placeholder

## Core Technologies
- **Programming Languages:** Python (Backend), JavaScript (Frontend - Electron/React).
- **Backend Framework:** FastAPI (for creating APIs served by agents).
- **Frontend Framework:** Electron (Desktop Shell), React.js (UI Library).
- **UI Styling:** Material-UI (MUI) with Emotion.
- **Database:** SQLite (Development), PostgreSQL (Planned for production/scale).
- **AI Model Interaction:**
    - **Configuration:** `tomllib` (Python 3.11+) for TOML config, `python-dotenv` for environment variables.
    - **Cloud Models:** `openai` Python library (for OpenAI-compatible APIs like OpenRouter).
    - **Local Models:** `ollama` Python library (if direct interaction needed beyond basic `requests`), `requests` library (for status checks and basic generation).
    - **Caching:** `redis` Python library (for LLM response caching - planned).
- **Logging:** Loguru.
- **Data Handling/Validation:** Pydantic (Backend - e.g., in BaseAgent).
- **Version Control:** Git, GitHub.
- **Package Management:** `pip` (Python), `npm` (Node.js).
- **Containerization (Future):** Docker (planned for deployment/Redis).

## Development Environment
- **OS:** Windows 11 Pro (Primary Dev Machine).
- **IDE/Editor:** VS Code with Cursor AI extension.
- **Python Version:** 3.11.x (specifically chosen for `tomllib` and `tiktoken` compatibility after issues with 3.12/3.13).
- **Node.js Version:** Latest LTS recommended.
- **Virtual Environment:** Python `venv` located at `C:\DreamerAI\venv`.

## Key Libraries & Dependencies (Illustrative - Not Exhaustive)
- **Python (`requirements.txt`):** `fastapi`, `uvicorn`, `requests`, `python-dotenv`, `pydantic`, `loguru`, `tomllib`, `openai`, `ollama`, `redis`, `sqlite3` (built-in), `psycopg[binary,pool]` (planned), `lightrag`, `chromadb`, `sentence-transformers`, `torch`.
- **Node.js (`app/package.json`):** `electron`, `react`, `react-dom`, `@mui/material`, `@emotion/react`, `@emotion/styled`, `@dnd-kit/core`, `eslint` (dev).

## Technical Constraints & Considerations
- Python 3.11+ required for `tomllib`.
- Initial `tiktoken` installation required Rust build tools and specific Python version (resolved by using 3.11).
- Electron security defaults (CSP) need review and proper configuration beyond initial development.
- Current DB interaction is basic; needs ORM or more robust query building for complexity.
- LLM Caching via Redis is not yet active. 