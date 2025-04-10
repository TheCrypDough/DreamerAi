# DreamerAI Context Memory Aid

## Day 1: Initial Project Setup & Refined Configuration
*   **Summary**: Established base project structure in C:\DreamerAI. Initialized Git repository and linked to GitHub remote (TheCrypDough/DreamerAi). Created structured configuration files (`data/config/.env.development` for secrets, `data/config/config.dev.toml` for settings). Established symbolic link `data/models` -> `C:\Users\thecr\.ollama\models` (manually by user). Created `.gitignore` file. Pushed initial structure and configuration to GitHub.
*   **Key Decisions**: Adopted TOML for structured configuration alongside `.env` for secrets, preparing for flexible LLM loading (Day 6). Followed directory structure defined in rules.
*   **Anthony's Feedback/Vibe**: Initial setup approved after verifying GitHub push. Ready to proceed.
*   **Blocking Issues**: Encountered issues running multi-step script commands due to terminal modification/interruption. Switched to step-by-step execution. Required manual creation of symbolic link due to lack of Administrator privileges in terminal session.

## Day 2: Environment Setup & Core Dependencies (2025-04-10)

*   **Summary:** Established Python virtual environment (`venv/`) and installed core Python dependencies (`requirements.txt`) including FastAPI, Uvicorn, Ollama, RAGstack, Transformers, PyYAML, python-dotenv, etc. Initialized Node.js project in `app/` (`package.json`), installed core runtime dependencies (React, Electron, MUI, etc.) and development dependencies (`eslint`). Configured ESLint using the flat config format (`eslint.config.mjs`) with Airbnb rules (via individual plugins due to v9 compatibility issues). Updated `.gitignore`.
*   **Key Decisions:** Used `--legacy-peer-deps` to install ESLint Airbnb plugins due to version conflict with ESLint v9. Adopted ESLint flat config format (`eslint.config.mjs`).
*   **Anthony's Feedback:** Emphasized not "half-assing" the ESLint setup, requiring adherence to Airbnb standards. Noted terminal output issues.
*   **Blocking Issues:** Significant issues with `npm install` for ESLint plugins due to peer dependency conflicts (ESLint v9 vs Airbnb config) and unreliable terminal execution/output. Resolved by manually confirming installation via `package.json` and using `--legacy-peer-deps`. Initial Git commits were incomplete due to failed installations; corrected with a final comprehensive commit.

## Day 2 (Revised): Environment Setup & Core Dependencies (2025-04-10)

*   **Summary:** Established Python virtual environment (`venv/`) and installed core Python dependencies (`requirements.txt`). Initialized Node.js project in `app/` (`package.json`), installed core runtime dependencies (React, Electron, MUI, `@dnd-kit/core` instead of `react-beautiful-dnd`). Installed ESLint v9 and compatible plugins (`eslint-plugin-react`, `eslint-plugin-react-hooks`, `eslint-plugin-jsx-a11y`, `eslint-plugin-import`). Configured ESLint using the flat config format (`eslint.config.mjs`) with recommended settings (instead of incompatible `eslint-config-airbnb`). Updated `.gitignore`.
*   **Key Decisions:** Replaced incompatible `react-beautiful-dnd` with `@dnd-kit/core`. Abandoned `eslint-config-airbnb` due to ESLint v9 incompatibility, opting for recommended ESLint/React/JSX-A11y rulesets within flat config. Used `--legacy-peer-deps` to force installations past dependency conflicts.
*   **Anthony's Feedback:** Directed revert to Day 2 to properly handle dependency conflicts with React 19 / ESLint 9. Emphasized using compatible, modern libraries (`dnd-kit`) and configurations.
*   **Blocking Issues:** Initial ESLint setup using `npx eslint --init` did not prompt for style guides. Direct installation of `eslint-config-airbnb` failed due to peer dependency conflict with ESLint v9. Installations of other packages were also blocked by ESLint conflicts until `--legacy-peer-deps` flag was used. Resolved by removing `eslint-config-airbnb` and configuring ESLint using recommended rulesets compatible with v9.

## Day 3: BaseAgent & Logging System (2025-04-10)

*   **Summary:** Created `engine/agents/base.py` defining the `BaseAgent` abstract class using Pydantic (including `Message`, `Memory`, `AgentState`) and `abc`. Added `user_dir` parameter to `__init__`. Implemented basic `run` loop with `step` abstraction and basic error handling. Created `engine/core/logger.py` with `DreamerLogger` class using Loguru, configuring console, development file, error file, and rules_check file sinks. Added `log_rules_check` helper. Added test blocks to both files.
*   **Key Decisions:** Used Loguru for flexible logging. Made `BaseAgent` require `user_dir` on init. Used Pydantic for agent structure.
*   **Anthony's Feedback:** N/A.
*   **Blocking Issues:** Initial test of `BaseAgent` failed with Pydantic `ValueError` because `agent_chat_dir` was set before being declared. Resolved by declaring `agent_chat_dir` as a model field.
