# DreamerAI Task List (EVERY "Cursor Task" within the daily DreamerAi_Guide.md entries MUST be performed IN ORDER as they appear and must be logged here)

## Day [XX]: [Concise Day Title from Guide]
*   **Cursor Task:** [Exact Task Description 1 from Guide Day XX]
    *   Status: [TODO | IN PROGRESS | DONE | FAILED]
*   **Cursor Task:** [Exact Task Description 2 from Guide Day XX]
    *   Status: [TODO | IN PROGRESS | DONE | FAILED]
*   **Cursor Task:** [Exact Task Description 3 from Guide Day XX]
    *   Status: [TODO | IN PROGRESS | DONE | FAILED]
*   ... (Add all `Cursor Task:` items for the day in order) ...
*   **Cursor Task:** Execute Auto-Update Triggers & Workflow.
    *   Status: [TODO | DONE]
*   **Overall Day Status:** [TODO | IN PROGRESS | DONE | FAILED - Needs Manual Fix]
*   **Summary:** [Brief 1-sentence summary of the Day's goal from Guide Description]
*   **Issues Encountered:** [List any Issue IDs or brief descriptions logged in issues.log/errors.log during this day's implementation, or "None"]

---

## Day 1: Initial Project Setup & Refined Configuration (OpenRouter/Ollama Ready!), Planting the Flag!
*   **Cursor Task:** Execute the provided batch script block below in an Administrator Terminal. This will: Create main C:\DreamerAI\ directory and subdirectories based on project_structure.md. Create the model symlink. Initialize Git, configure local user, add GitHub remote. Create structured .env.development (with OPENROUTER_API_KEY placeholder) and config.dev.toml (configured for OpenRouter & Ollama gemma3:12b). Create .gitignore. Stage and commit initial setup. Push initial commit to GitHub remote (origin main).
    *   Status: DONE
*   **Cursor Task:** Remind Anthony to replace "YOUR_OPENROUTER_API_KEY_HERE" in C:\DreamerAI\data\config\.env.development with his actual OpenRouter key.
    *   Status: DONE
*   **Cursor Task:** Verify all directories and files were created correctly and the initial push to GitHub was successful by checking the file system and the GitHub repository webpage (TheCrypDough/DreamerAi).
    *   Status: DONE
*   **Cursor Task:** Present Summary for Approval: "Task 'Day 1: Initial Setup (OpenRouter/Ollama Config)' complete. Implementation: Created dir structure, Git repo, symlink. Configured .env/.toml for OpenRouter (Llama 3 70B default) + Ollama (gemma3:12b fallback). Created .gitignore. Initial commit pushed. Reminded Anthony to add OpenRouter API key. Tests/Verification: Directory structure created, config files present, symlink created, GitHub repo received initial commit - Verified OK. Requesting approval to proceed to 'Day 2: Environment Setup (LightRAG/ChromaDB Update)'. (yes/no/details?)"
    *   Status: DONE
*   **Cursor Task:** (Upon Approval) Execute Auto-Update Triggers & Workflow (update tasks.md to Day 2, update cursor_rules.md current task, update Memory Bank, logs, commit etc.).
    *   Status: DONE
*   **Overall Day Status:** DONE
*   **Summary:** Setting up the core project directory structure, initializing Git, linking to GitHub, creating initial .gitignore, and establishing configuration files (.env.development, config.dev.toml) for OpenRouter and Ollama.
*   **Issues Encountered:** Error running batch script (see errors.log)

---
*(Next Day's Entry Starts Here)*

## Day 2: Environment Setup & Core Dependencies (RAG & DND Update), Gearing Up the Workshop!
*   **Cursor Task:** Create and activate the Python virtual environment (venv) within C:\DreamerAI\.
    *   Status: DONE
*   **Cursor Task:** Install core Python dependencies using pip and generate requirements.txt. Include: fastapi, uvicorn[standard], requests, python-dotenv, pydantic, loguru, tenacity, pyyaml, numpy, aiofiles, colorama, black, ollama, transformers, datasets, redis, GitPython, python-jose[cryptography], cryptography, bleach, cachetools, websockets, scikit-learn, pandas, httpx, dependency-injector, firebase-admin, "psycopg[binary,pool]", pip-audit, lightrag, chromadb, sentence-transformers, torch, torchvision, torchaudio.
    *   Status: DONE
*   **Cursor Task:** Configure the Black linter (optional, can use defaults via pyproject.toml later).
    *   Status: DONE
*   **Cursor Task:** Navigate into the app directory (cd app).
    *   Status: DONE
*   **Cursor Task:** Initialize npm project (npm init -y).
    *   Status: DONE
*   **Cursor Task:** Install core Node.js dependencies using npm install. Include: electron, react, react-dom, @mui/material, @emotion/react, @emotion/styled, @dnd-kit/core, i18next, react-i18next, posthog-js, electron-oauth2, keytar, firebase, ws, joi, intro.js, @mui/lab, @mui/icons-material. Ensure n8n and react-beautiful-dnd are NOT included.
    *   Status: DONE
*   **Cursor Task:** Install Node.js dev dependencies: npm install --save-dev eslint electron-builder.
    *   Status: DONE
*   **Cursor Task:** Initialize ESLint configuration (npx eslint --init) and follow prompts for React/JS project setup.
    *   Status: DONE
*   **Cursor Task:** Navigate back to the root directory (cd ..).
    *   Status: DONE
*   **Cursor Task:** Update .gitignore to include node_modules/, app/node_modules/, .eslintcache.
    *   Status: DONE
*   **Cursor Task:** Present Summary for Approval: "Task 'Day 2: Environment Setup (RAG/DND Corrected)' complete. Implementation: Created venv. Installed Python deps (incl. LightRAG/ChromaDB/ST/Torch, other consolidated libs; excluded ragstack). In app/, initialized npm, installed Node deps (incl. @dnd-kit/core, other V1.1 libs; excluded n8n, react-beautiful-dnd). Installed Node dev deps (eslint, electron-builder). Configured ESLint. Updated .gitignore. Tests/Verification: Checked requirements.txt for correct Python libs. Checked app/package.json for correct Node libs & devDeps. Verified eslint config file created. Verified .gitignore updated. Verified venv created. Requesting approval to proceed to 'Day 3: BaseAgent & Logging System (Log Dir Update)'. (yes/no/details?)"
    *   Status: DONE
*   **Cursor Task:** (Upon Approval) Stage ALL changes, commit, push. Execute Auto-Update Workflow.
    *   Status: DONE
*   **Overall Day Status:** DONE
*   **Summary:** Establish Python venv, install Python (LightRAG/ChromaDB) & Node (@dnd-kit) deps, setup linters.
*   **Issues Encountered:** Failed to install Python dependencies (`tiktoken` needs Rust - see errors.log)

---
*(Next Day's Entry Starts Here)*

## Day 3: BaseAgent & Logging System, The Heartbeat Starts!
*   **Cursor Task:** Create the file C:\DreamerAI\engine\agents\base.py.
    *   Status: DONE
*   **Cursor Task:** Implement the Message, Memory, AgentState, and BaseAgent classes within base.py using the provided code, including __init__ with name and user_dir, basic memory management, state tracking, async run method, abstract step method, and basic internal logging via loguru.
    *   Status: DONE
*   **Cursor Task:** Create the file C:\DreamerAI\engine\core\logger.py.
    *   Status: DONE
*   **Cursor Task:** Implement the DreamerLogger class within logger.py using loguru to configure file logging sinks (e.g., dreamerai_dev.log, errors.log) with rotation and formatting. Ensure logs are written to C:\DreamerAI\docs\logs\.
    *   Status: DONE
*   **Cursor Task:** Add basic test execution block (if __name__ == "__main__":) in base.py to allow simple testing of the BaseAgent structure (e.g., creating a dummy TestAgent).
    *   Status: DONE
*   **Cursor Task:** Stage changes, commit, and push to GitHub.
    *   Status: DONE # Manual commit/push required
*   **Cursor Task:** (Upon Approval) Execute Auto-Update Triggers & Workflow.
    *   Status: DONE
*   **Overall Day Status:** TODO
*   **Summary:** Implement foundational BaseAgent class and centralized Loguru logging system.
*   **Issues Encountered:** None

---
*(Next Day's Entry Starts Here)*