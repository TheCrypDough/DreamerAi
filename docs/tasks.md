# DreamerAI Task List (EVERT "Cursor Task" within the daily DreamerAi_Guide.md entries MUST be logged)

## Day 1: Initial Project Setup & Refined Configuration
* Status: DONE
* Details: Create base project structure (C:\DreamerAI\), initialize Git, link remote, set up structured config files (.env.development, config.dev.toml), define .gitignore, set up Ollama model symlink. Follow detailed steps in DreamerAi_Guide.md Day 1.

## Day 2: Environment Setup & Core Dependencies
Cursor Task: Create and activate Python venv in C:\DreamerAI\.
Done
Cursor Task: Install specified Python dependencies using pip (FastAPI, Uvicorn standard, requests, dotenv, pydantic, loguru, tenacity, pyyaml, numpy, aiofiles, colorama, black, ollama, ragstack, transformers, datasets, redis, GitPython, python-jose[cryptography], cryptography, bleach, cachetools, websockets, scikit-learn, pandas, httpx, psycopg[binary,pool], dependency-injector, pip-audit). Generate requirements.txt via pip freeze.
Done
Cursor Task: Navigate to C:\DreamerAI\app\.
Done
Cursor Task: Initialize npm (npm init -y).
Done
Cursor Task: Install specified Node.js library dependencies using npm install (electron, react, react-dom, @mui/material, @emotion/react, @emotion/styled, @dnd-kit/core, react-grid-layout, i18next, react-i18next, posthog-js, electron-oauth2, keytar, firebase, ws, framer-motion, joi, @mui/lab, @mui/icons-material, intro.js). Ensure n8n is NOT listed.
Done
Cursor Task: Install Node.js dev dependencies (npm install --save-dev eslint).
Done
Cursor Task: Initialize ESLint (npx eslint --init, follow React/JS prompts).
Done
Cursor Task: Navigate back to C:\DreamerAI\.
Done
Cursor Task: Ensure .gitignore includes node_modules/, .eslintcache, /venv/.
Done
Cursor Task: Stage ALL new/modified files (excluding venv), commit (Day 2: Env Setup & Core Dependencies (Consolidated)), push.
Done
Cursor Task: Execute Auto-Update Triggers & Workflow.
Done
* Overall Status: Done
* Details: Create Python venv, install Python/Node deps, setup linters. Follow detailed steps in DreamerAi_Guide.md Day 2.
* Issues: (any issues during the daily implementation)

## Day 3: BaseAgent & Logging System
Cursor Task: Create the file C:\DreamerAI\engine\agents\base.py.
Done
Cursor Task: Implement the Message, Memory, AgentState, and BaseAgent classes within base.py using the provided code, including __init__ with name and user_dir, basic memory management, state tracking, async run method, abstract step method, and basic internal logging via loguru.
Done
Cursor Task: Create the file C:\DreamerAI\engine\core\logger.py.
Done
Cursor Task: Implement the DreamerLogger class within logger.py using loguru to configure file logging sinks (e.g., dreamerai_dev.log, errors.log) with rotation and formatting. Ensure logs are written to C:\DreamerAI\docs\logs\.
Done
Cursor Task: Add basic test execution block (if __name__ == "__main__":) in base.py to allow simple testing of the BaseAgent structure (e.g., creating a dummy TestAgent).
Done
Cursor Task: Stage changes, commit, and push to GitHub.
Done
* Overall Status: DONE
* Details: Implement BaseAgent class (base.py) and DreamerLogger (logger.py). Verified via test blocks.
* Issues: None.

## Day 4: Electron Frontend Skeleton
* Overall Status: DONE
* Details: Create basic Electron main process, preload script, renderer process, and HTML entry point. Update package.json scripts. Test basic window launch. Follow detailed steps in DreamerAi_Guide.md Day 4.
* Issues: None anticipated.
*   Cursor Task: Create app/main.js (using Day 4 Guide code) - DONE
*   Cursor Task: Create app/index.html (using Day 4 Guide code) - DONE
*   Cursor Task: Create app/renderer.js (using Day 4 Guide code) - DONE
*   Cursor Task: Create app/preload.js (using Day 4 Guide code) - DONE
*   Cursor Task: Modify app/package.json (add main, start, lint scripts - using Day 4 Guide code) - DONE
*   Cursor Task: Test Electron app with npm start - DONE
*   Cursor Task: Stage Day 4 changes, commit, and push. - DONE
*   Cursor Task: Execute Auto-Update Triggers & Workflow for Day 4. - DONE

## Day 5: SQLite Database & Basic UI Bridge
* Overall Status: DONE
* Details: Implement initial SQLite DB setup (engine/core/db.py) for local dev persistence (projects table). Setup basic FastAPI/Uvicorn server (engine/core/server.py) as the backend-frontend bridge. Test bridge with a fetch call from renderer. Follow detailed steps in DreamerAi_Guide.md Day 5.
* Issues: None anticipated.
*   Cursor Task: Create the file C:\DreamerAI\engine\core\db.py. - DONE
*   Cursor Task: Implement the DreamerDB class in db.py using sqlite3 to connect to C:\DreamerAI\data\db\dreamer.db and create the initial projects table. Include basic methods like add_project, get_project, and close. Add logging using logger_instance. Explicitly comment that this is for dev and PostgreSQL is planned for scale. - DONE
*   Cursor Task: Modify C:\DreamerAI\engine\core\server.py. Import FastAPI and uvicorn. Instantiate the FastAPI app. Add a simple root endpoint (@app.get("/")) that returns {"message": "DreamerAI Backend Online"}. Add the if __name__ == "__main__": block to run the server using uvicorn.run. - DONE
*   Cursor Task: Modify C:\DreamerAI\app\renderer.js. Add a useEffect hook that runs once on component mount. Inside the hook, use fetch to make a GET request to the backend's root URL (http://localhost:8000/). Log the response to the console to verify the bridge connection. - DONE
*   Cursor Task: Run the backend server: Open a new terminal in C:\DreamerAI, activate venv (.\venv\Scripts\activate), and run using `uvicorn engine.core.server:app --reload`. Leave this terminal running. - DONE
*   Cursor Task: Run the frontend app: Open another terminal in C:\DreamerAI\app and run `npm start`. - DONE
*   Cursor Task: Verify the frontend window opens and check the Electron DevTools console (Ctrl+Shift+I) for the logged message from the successful backend fetch. Verify dreamer.db is created in data/db/. Stop both the frontend app and the backend server (Ctrl+C in terminals). - DONE
*   Cursor Task: Stage changes, commit, and push. - DONE
*   Cursor Task: Execute Auto-Update Triggers & Workflow for Day 5. - DONE

## Day 6: Config-Driven Hybrid LLM Setup
* Overall Status: DONE
* Details: Implement LLMManager (engine/ai/llm.py) to handle multiple providers (Ollama, OpenAI-compatible) via config/env. Test OpenRouter and Ollama initialization/status. Verified via test block. Addressed Ollama status check path issue via manual code fix.
* Issues: Initial Ollama status check failed due to suspected environment/tooling issue preventing code updates; resolved via manual code fix.
*   Cursor Task: Create engine/ai/llm.py with LLMManager class. - DONE
*   Cursor Task: Implement configuration loading (toml, dotenv) in LLMManager. - DONE
*   Cursor Task: Implement provider initialization (_initialize_providers) for 'ollama' and 'openai_compatible' types. - DONE
*   Cursor Task: Implement status checking (_check_ollama_status, potentially others). - DONE (Manual Fix Required)
*   Cursor Task: Implement generation methods (_generate_ollama, _generate_openai_compatible). - DONE
*   Cursor Task: Implement main generate method with priority/fallback logic. - DONE
*   Cursor Task: Add test block (if __name__ == "__main__") to test configuration loading and generation with different providers/overrides. - DONE
*   Cursor Task: Create/Update .env.development and config.dev.toml for Ollama and OpenRouter. - DONE
*   Cursor Task: Run test block, debug, log issues/resolutions. - DONE
*   Cursor Task: Stage changes, commit, push. - DONE
*   Cursor Task: Execute Auto-Update Triggers & Workflow for Day 6. - DONE

## Day 7: Nexus Agent - The Orchestrator
* Overall Status: DONE
* Details: Create the Nexus agent (engine/ai/nexus.py) responsible for managing the overall AI workflow and delegating tasks to other specialized agents. Implement basic initialization using the LLM class. Add a test block. Fixed multiple errors during testing (logger init, LLM class name, Pydantic field/init, AgentState, generate() args).
* Issues: Initial implementation had several errors requiring debugging during test execution.
*   Cursor Task: Ensure the directory C:\DreamerAI\engine\ai\ exists. Create an empty __init__.py file inside it if it doesn't exist. - DONE
*   Cursor Task: Create the file C:\DreamerAI\engine\ai\nexus.py. - DONE
*   Cursor Task: Populate C:\DreamerAI\engine\ai\nexus.py with the complete Python code provided in the guide (including imports, Nexus class, and if __name__ == "__main__" test block). - DONE
*   Cursor Task: Activate the virtual environment (C:\DreamerAI\venv\Scripts\activate). - DONE
*   Cursor Task: Execute the test block by running python -m engine.ai.nexus from the C:\DreamerAI directory. Observe the output logs to verify initialization and the successful generation attempt using the LLM. - DONE
*   Cursor Task: Stage the new files (engine/ai/nexus.py), commit, and push to GitHub. - DONE
*   Cursor Task: Execute Auto-Update Triggers & Workflow for Day 7. - DONE

## Day 8: Building Chef Jeff (Main Chat Agent)
- **8.1**: Create `C:\DreamerAI\engine\agents\rules_jeff.md`. Populate from `docs/templates/rules_template.md`, defining Jeff's Role and Scope as User Conduit, Conversationalist, Task Router. - **DONE**
- **8.2**: Create and execute a temporary Python script `C:\DreamerAI\scripts\seed_rag_jeff.py` to initialize and seed Jeff's RAG DB (resolved using ChromaDB). - **DONE**
- **8.3**: Modify `C:\DreamerAI\engine\agents\main_chat.py`. Implement the `ChefJeff` class with ChromaDB RAG retrieval. - **DONE**
- **8.4**: Test ChefJeff Class
- Status: DONE
- Details: Execute the `if __name__ == "__main__"` test block in `main_chat.py` (`python -m engine.agents.main_chat` after activating venv). Verify output shows connection to RAG (ChromaDB load/query), loading of rules, attempt to call LLM (log should indicate preference for configured 'cloud_tier1' model), placeholder function logs, and a response (or AI unavailable error). Check logs. Follow detailed steps in DreamerAi_Guide.md Day 8.
- **8.5**: Delete the temporary seed script (`seed_rag_jeff.py`). Stage changes, commit, and push. - **TODO**

## [Add entries for Day 8+ from DreamerAi_Guide.md marked as PENDING]
