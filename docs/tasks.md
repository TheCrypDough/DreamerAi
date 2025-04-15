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
    *   Status: FAILED
*   **Cursor Task:** Remind Anthony to replace "YOUR_OPENROUTER_API_KEY_HERE" in C:\DreamerAI\data\config\.env.development with his actual OpenRouter key.
    *   Status: TODO
*   **Cursor Task:** Verify all directories and files were created correctly and the initial push to GitHub was successful by checking the file system and the GitHub repository webpage (TheCrypDough/DreamerAi).
    *   Status: TODO
*   **Cursor Task:** Present Summary for Approval: "Task 'Day 1: Initial Setup (OpenRouter/Ollama Config)' complete. Implementation: Created dir structure, Git repo, symlink. Configured .env/.toml for OpenRouter (Llama 3 70B default) + Ollama (gemma3:12b fallback). Created .gitignore. Initial commit pushed. Reminded Anthony to add OpenRouter API key. Tests/Verification: Directory structure created, config files present, symlink created, GitHub repo received initial commit - Verified OK. Requesting approval to proceed to 'Day 2: Environment Setup (LightRAG/ChromaDB Update)'. (yes/no/details?)"
    *   Status: TODO
*   **Cursor Task:** (Upon Approval) Execute Auto-Update Triggers & Workflow (update tasks.md to Day 2, update cursor_rules.md current task, update Memory Bank, logs, commit etc.).
    *   Status: TODO
*   **Overall Day Status:** TODO
*   **Summary:** Setting up the core project directory structure, initializing Git, linking to GitHub, creating initial .gitignore, and establishing configuration files (.env.development, config.dev.toml) for OpenRouter and Ollama.
*   **Issues Encountered:** Error running batch script (see errors.log)

---
*(Next Day's Entry Starts Here)*