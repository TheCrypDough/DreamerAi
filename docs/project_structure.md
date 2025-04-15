

# DreamerAI Project Structure (Multi-Environment - Aligned Vision 2025-03-29)

**Note:** This document outlines the mirrored file structure across Development, Test, and Production environments. Environment-specific configurations, databases, logs, and potentially model strategies differ, but the core layout is consistent. The canonical definition is maintained in the Development environment at `C:\DreamerAI\docs\project_structure.md`.

## Shared Resources

*   **Local Models:** `C:\Users\thecr\.ollama\models`
    *   Contains base models used for local inference (e.g., during development or for specific agents).
    *   Accessed via symlinks from `data/models/` in Dev, potentially Test. Prod environment might use different strategy (e.g., cloud APIs, optimized deployed models).

## 1. Development Environment (Primary Workspace)

*   **Root:** `C:\DreamerAI\`
Use code with caution.
Markdown
C:\DreamerAI
│
├── app\ # Electron/React Frontend (Panelized "Dreamer Desktop")
│ ├── components\ # React UI Panel Modules & Components
│ │ ├── MainChatPanel.js, DreamcoderPanel.js, ThinkTankPanel.js, ... (etc.)
│ ├── src\ # Core React files (App.jsx, analytics.js)
│ ├── utils\ # Frontend utilities (backup.js, crypto.js)
│ ├── ... (firebase.js, i18n.js, index.html, main.js, package.json, preload.js, renderer.js)
│
├── data\ # Configuration, Databases, RAG DBs, Model Symlink (Dev)
│ ├── config\ # Dev Configurations
│ │ ├── .env.development
│ │ └── config.dev.toml
│ ├── db\ # Dev Databases
│ │ ├── dreamer.db # Main SQLite DB for Dev
│ │ └── (postgres_info_dev.txt) # Dev PostgreSQL connection details (if/when used)
│ ├── models\ # Symlink to Local AI Models
│ │ └── (symlink) # -> C:\Users\Admin.ollama\models
│ └── rag_dbs\ # Agent RAG DBs (Dev instances)
│ ├── rag_jeff.db, rag_arch.db, ... (etc.)
│
├── docs\ # Documentation, Logs, Tracking Files (Master Copies)
│ ├── daily_progress\ # daily_context_log.md
│ ├── logs\ # Dev Logs (rules_check.log, issues.log, errors.log, migration_tracker.md)
│ ├── mcp\ # mcp_catalog.md
│ ├── templates\ # rules_template.md
│ ├── user\ # user_guide.md
│ ├── project_structure.md # This File (Canonical Definition)
│ ├── tasks.md
│ ├── dreamerai_context.md
│ ├── cursor_rules.md # Cursor Rules for Dev
│ └── ... (Other Master Docs)
│
├── engine\ # Python Backend & Core Logic (Dev)
│ ├── agents\ # All 28 Agent Scripts & Runtime Rules (Dev)
│ │ ├── base.py, main_chat.py, rules_jeff.md, ... (etc.)
│ ├── core\ # Core Backend Services & Utilities (Dev)
│ │ ├── workflow.py, db.py, server.py, bridge.py, ... (etc.)
│ ├── ai\ # AI-specific Modules (Dev)
│ │ ├── llm.py, distiller.py, archon/
│ └── tools\ # Shared agent tools (Dev)
│ └── tool_collection.py
│
├── n8n_workflows\ # n8n Automation Workflows (Dev instances/configs)
│ ├── update_rules_workflow.json, task_router_workflow.json, ... (etc.)
│
├── plugins\ # User-installable plugins (Dev testing area)
│ └── (e.g., game_dev_pack_dev/)
│
├── projects\ # Generated project outputs (Dev - Runtime Managed)
│ └── (e.g., project_dev_123/)
│
├── templates\ # SnapApp Project Templates (Master Source)
│ ├── web, mobile, game, blockchain, community/
│
├── Users\ # User Workspace (Dev - Runtime Managed)
│ └── [User Name]\Projects[Project Name]\ (Includes Chats/, models/, etc.)
│
├── backups\ # Local backup storage (Dev)
│ └── backup.json
│
├── dist\ # Build Distribution Files (Dev builds)
│ └── dreamerai-setup-dev.exe
│
├── Dockerfile # Docker build configuration (can be env-specific if needed)
├── build.bat # Windows build script
├── README.md # Main project README
├── requirements.txt # Python dependencies
└── .gitignore # Git ignore configuration

## 2. Test Environment

*   **Root:** `D:\DreamerAI_Test\` (Mirrors Dev structure)
Use code with caution.
D:\DreamerAI_Test
│
├── app\ # Frontend - Mirrored from Dev
│ ├── components
│ ├── src
│ ├── utils
│ └── ...
│
├── data\ # Test Data & Configs
│ ├── config\ # Test Configurations
│ │ ├── .env.test
│ │ └── config.test.toml
│ ├── db\ # Test Databases
│ │ ├── dreamer_test.db
│ │ └── (postgres_info_test.txt)
│ ├── models\ # Symlink to Local AI Models (or uses specific test models)
│ │ └── (symlink) # -> C:\Users\Admin.ollama\models\ (or dedicated test models)
│ └── rag_dbs\ # Agent RAG DBs (Test instances)
│ ├── rag_jeff_test.db, ... (etc.)
│
├── docs\ # Test Documentation & Logs (Copies or specific test logs)
│ ├── daily_progress\ # Test Progress
│ ├── logs\ # Test Logs (rules_check_test.log, etc.)
│ └── ... (Mirrored structure, potentially with test-specific content)
│
├── engine\ # Backend Logic (Mirrored from Dev)
│ ├── agents
│ ├── core
│ ├── ai
│ └── tools
│
├── n8n_workflows\ # n8n Workflows (Test instances/configs)
│ └── ...
│
├── plugins\ # Plugins for testing
│ └── ...
│
├── projects\ # Generated project outputs (Test)
│ └── ...
│
├── templates\ # SnapApp Templates (Copied from Dev or test-specific)
│ └── ...
│
├── Users\ # User Workspace (Test)
│ └── ...
│
├── backups\ # Local backup storage (Test)
│ └── backup_test.json
│
├── dist\ # Build outputs (Test builds)
│ └── dreamerai-setup-test.exe
│
├── Dockerfile # (May use same as Dev or test-specific version)
├── build.bat # Build script configured for Test env
├── README_test.md # Test environment specifics
├── requirements_test.txt # (If different from Dev)
└── .gitignore

## 3. Production Environment

*   **Root:** `D:\DreamerAI_Prod\` (Mirrors Dev/Test structure)
Use code with caution.
D:\DreamerAI_Prod
│
├── app\ # Frontend - Mirrored/Deployed Stable Version
│ ├── components
│ ├── src
│ ├── utils
│ └── ...
│
├── data\ # Production Data & Configs
│ ├── config\ # Production Configurations
│ │ ├── .env.production
│ │ └── config.prod.toml
│ ├── db\ # Production Databases
│ │ ├── dreamer_prod.db # SQLite (if used initially)
│ │ └── (postgres_info_prod.txt) # Prod PostgreSQL connection details
│ ├── models\ # Model Strategy (May differ - e.g., cloud APIs, optimized models)
│ │ └── (Symlink if local models used, or config files for cloud endpoints)
│ └── rag_dbs\ # Agent RAG DBs (Production instances)
│ ├── rag_jeff_prod.db, ... (etc.)
│
├── docs\ # Production Documentation & Logs (Runtime Focused)
│ ├── daily_progress\ # User Activity/Usage Logs
│ ├── logs\ # Production Runtime Logs (errors, performance)
│ └── ... (User Guide, Maintenance Guide primarily)
│
├── engine\ # Backend Logic (Deployed Stable Version)
│ ├── agents
│ ├── core
│ ├── ai
│ └── tools
│
├── n8n_workflows\ # n8n Workflows (Production instances/configs)
│ └── ...
│
├── plugins\ # Approved/Installed Plugins for Production
│ └── ...
│
├── projects\ # User-Generated Projects (Production - Live Data)
│ └── ...
│
├── templates\ # SnapApp Templates (Production - Stable Versions)
│ └── ...
│
├── Users\ # User Workspace (Production - Live User Data)
│ └── ...
│
├── backups\ # Local backup storage (Production - Critical)
│ └── backup_prod.json
│
├── dist\ # Deployed Executable / Installation Files
│ └── dreamerai-setup.exe
│
├── Dockerfile # Docker config for Production deployment
├── build.bat # (Likely not used directly, CI/CD handles build)
├── README_prod.md # Production environment notes (if needed)
├── requirements_prod.txt # Production Python dependencies
└── .gitignore

**Explanation of Multi-Environment Structure:**

*   **Consistency:** The core folder structure (`app`, `data`, `docs`, `engine`, etc.) is maintained across all three environments for predictability.
*   **Isolation:** Critical components like configuration (`data/config`), databases (`data/db`), logs (`docs/logs`), and user data (`Users`, `projects`) are kept separate for each environment. This prevents development activities from impacting testing or production, and vice-versa.
*   **Configuration:** Each environment uses its own `.env.*` and `config.*.toml` files, allowing for different API keys, database connections, model endpoints (e.g., Dev uses local Ollama, Prod uses optimized cloud models), and feature flags.
*   **Models:** While Dev and Test might use the symlink to the shared local models (`C:\Users\thecr\.ollama\models`), Production might rely more heavily on cloud APIs or specifically optimized/deployed models, configured via `config.prod.toml`.
*   **Build/Deployment:** Each environment can have its own build artifacts (`dist/`) and potentially tailored `Dockerfile` or `requirements.txt` if needed, although consistency is often preferred. CI/CD pipelines (using GitHub Actions, mentioned in Tech Stack) would typically handle building and deploying to Test and Prod based on code merged into specific branches (e.g., `develop` -> Test, `main` -> Prod).
*   **Purpose:**
    *   **Dev:** Active development, experimentation, feature building.
    *   **Test:** Staging area for QA, integration testing, verifying builds before release.
    *   **Prod:** Live environment for end-users, focused on stability and performance.





_________________________________________________________________________________________________________________________________________________________________________








Project Structure for DreamerAI, planning/pre-development based on Implementation_Guide.txt as of 4/6/2025 1:06 AM EST
**IMPORTANT Distinction: User Workspace vs. Project Output**

*   **`C:\DreamerAI\Users\[UserName]\Projects\[ProjectName]\` (User Workspace):** This directory structure is **exclusively for the user's organization, thoughts, ideas, inputs, reference files, and DreamerAI's internal operational data related to the project (e.g., `Chats`, `Overview`, `Backtable`, `Tutorials`, agent-specific rules/memory persisted here).** Code snippets or intermediate artifacts used *during* the thought process might reside here, but **NOT the final generated application code.** This space is customizable by the user (subfolders, notes).
*   **`C:\DreamerAI\projects\[ProjectID or Name]\output\` (Project Output Directory - V1 Assumption):** This separate root directory (or a configurable path) is where DreamerAI agents (Nexus, Coders, Scribe, Nike) **write the final, generated source code, documentation (README), build scripts, and packaged artifacts** that constitute the deliverable application/component. This ensures a clean separation between the user's conceptual workspace and the tangible project output suitable for export or deployment. **Agent implementation MUST respect this separation.** *(Note: Exact root `C:\DreamerAI\projects\` structure needs final definition)*.

If there are additions or changes made to this file structure in development they should update automatically as mentioned in the cursor_rules.md


Shared

D:\DreamerAI_Models\                     # AI model storage directory (shared across environments)
└── (model files)                        # Actual model files (e.g., gemma2:2b, gemma2:9b)


Development (Default)

C:\DreamerAI\                            # Development environment (default)
├── app\                                 # Frontend application files (Electron/React UI)
│   ├── components\                      # Reusable React components
│   │   ├── BuildItTab.js                # Component for the "Build It" workflow step
│   │   ├── DreamItTab.js                # Component for the "Dream It" workflow step with project input
│   │   ├── FeedbackForm.jsx             # Feedback submission form component
│   │   ├── LaunchItTab.js               # Component for the "Launch It" step with export options
│   │   ├── Marketplace.js               # Placeholder for plugin marketplace UI
│   │   ├── Playground.js                # Interactive coding playground component
│   │   ├── RecoveryPanel.js             # UI for restoring project backups
│   │   └── ShareSnippet.js              # Component for generating shareable code snippet URLs
│   ├── src\                             # Source files for the React frontend
│   │   ├── App.jsx                      # Main React app component with tabs and UI logic
│   │   └── analytics.js                 # PostHog analytics integration for usage tracking
│   ├── utils\                           # Utility scripts for the frontend
│   │   ├── backup.js                    # Backup scheduling and restoration logic
│   │   └── crypto.js                    # AES encryption/decryption for project data
│   ├── firebase.js                     # Firebase configuration for user authentication
│   ├── i18n.js                         # Internationalization setup with translations
│   ├── index.html                      # Main HTML entry point for Electron
│   ├── main.js                         # Electron main process script
│   ├── package.json                    # NPM dependencies and scripts for the frontend
│   ├── preload.js                      # Electron preload script (currently empty)
│   └── renderer.js                     # Renderer process script with UI logic and tabs
├── data\                                # Manages project data and resources
│   ├── config\                          # Configuration files for development
│   │   ├── .env.development             # Environment variables (e.g., API keys) for dev
│   │   └── config.dev.toml              # Dev environment config (e.g., model: gemma2:2b)
│   ├── db\                              # SQLite databases for development
│   │   ├── dreamer.db                   # Main database for projects and chats
│   │   └── projects.db                  # Database for project metadata
│   └── models\                          # Symlink to AI model storage
│       └── (symlink)                    # Points to D:\DreamerAI_Models\
├── docs\                                # Centralizes documentation for development
│   ├── daily_progress\                  # Daily progress logs
│   │   └── progress.md                  # Weekly summaries of development progress
│   ├── dev\                             # Developer notes
│   │   └── upgrade_suggestion.md        # Suggestions for future upgrades
│   ├── logs\                            # Logs for actions and debugging
│   │   ├── mcp_agent\log.txt            # Logs for MCP Agent operations
│   │   └── rules_check.log              # General action and rule review logs
│   ├── user\                            # User guides and manuals
│   │   └── user_guide.md                # User manual with troubleshooting tips
│   ├── launch_announcement.md           # Public launch announcement for v1.0.0
│   ├── penetration_testing_plan.md      # Security audit plan for Week 9
│   ├── post_launch_notes.md             # Feedback and update plans post-launch
│   └── v1.1_features.md                 # Roadmap for v1.1 features
├── engine\                              # Houses Python backend logic
│   ├── agents\                          # Individual agent scripts
│   │   ├── base.py                      # BaseAgent class with memory and state
│   │   ├── coding.py                    # Rak (backend) and Shak (frontend) coding agents
│   │   ├── code_reviewer.py             # Agent for AI-driven code review suggestions
│   │   ├── enoch.py                     # Enoch overseer for coordinating coding agents
│   │   ├── main_chat.py                 # Main Chat Agent (Chef Jeff) with "Just Chat"
│   │   ├── mcp_agent.py                 # MCP Agent for managing prompts and tools
│   │   └── planning.py                  # Planning Agent for project blueprints
│   ├── core\                            # Core functionality
│   │   ├── backup.py                    # BackupManager for cloud backups
│   │   ├── bridge.py                    # Backend-to-frontend communication bridge
│   │   ├── cloud_sync.py                # Cloud sync with Dropbox and encryption
│   │   ├── db.py                        # SQLite database management with MCP tables
│   │   ├── logger.py                    # Logging system using Loguru
│   │   ├── project_manager.py           # Project and subproject management logic
│   │   ├── server.py                    # FastAPI server for backend endpoints
│   │   └── workflow.py                  # DreamerFlow for orchestrating 6-step workflow
│   ├── llm_service.py                   # Standalone LLM microservice (FastAPI)
│   ├── llm.py                           # Hybrid LLM with Ollama, DeepSeek, and Grok
│   ├── plugins.py                       # PluginManager for loading custom plugins
│   └── tools\                           # Shared tools for agents
│       └── tool_collection.py           # ToolCollection with fetch_url and parse_html
├── plugins\                             # Directory for custom plugins
│   └── (example_plugin.py)              # Placeholder for future plugin scripts
├── projects\                            # Holds generated outputs for dev projects
│   ├── [project_id]\                    # Unique directory per project (e.g., 1, 2)
│   │   ├── chat_summary.txt             # Summary from chat-based project creation
│   │   ├── data_analysis.txt            # Analysis of uploaded project files
│   │   └── (project files)              # Generated code, assets, etc.
│   └── current\                         # Active project directory for export
├── templates\                           # Pre-built code templates for various app types
│   ├── blockchain\                      # Blockchain app templates
│   │   └── (Solana programs)            # Placeholder for Solana templates
│   ├── game\                            # Game development templates
│   │   └── (Unity snippets)             # Placeholder for Unity snippets
│   ├── mobile\                          # Mobile app templates
│   │   └── (React Native)               # Placeholder for React Native templates
│   └── web\                             # Web app templates
│       └── (React starter)              # Placeholder for React starter templates
├── Users\                               # Organizes user thoughts and projects for dev
│   ├── [User Name]\                     # User-specific directory (e.g., Example User)
│   │   ├── Projects\                    # Active projects
│   │   │   ├── [Project Name]\          # Project directory (e.g., Example Project)
│   │   │   │   ├── Chats\               # Chat histories with agents
│   │   │   │   │   ├── [Agent Name]\    # Agent-specific chats (e.g., Jeff)
│   │   │   │   │   │   └── (chat logs)  # Individual chat files
│   │   │   │   ├── Overview\            # Project overview and notes
│   │   │   │   ├── Backtable\           # Background ideas and suggestions
│   │   │   │   ├── Tutorials\           # Educational resources
│   │   │   │   └── Recycle Bin\         # Deleted items for the project
│   │   │   └── [Subproject Name]\       # Subproject directory (similar structure)
│   │   └── Completed Projects\          # Completed projects
│   │       └── [Completed Project Name]\# Final files and documentation
├── backups\                             # Local backup storage for dev
│   └── backup.json                      # Daily backup of project data
├── cloud_backup\                        # Mock cloud backup storage for dev
│   └── ([project_id].json)              # Encrypted project backups
├── dist\                                # Stores distribution files
│   └── dreamerai-setup.exe              # Final production executable
├── Dockerfile                           # Docker configuration for full app containerization
├── build.bat                            # Build script for compiling the app
├── deploy.sh                            # Deployment script for Docker
├── README.md                            # Project overview and setup instructions
├── requirements.txt                     # Python dependencies (e.g., bleach, cryptography)
└── .gitignore                           # Files and dirs to ignore in Git (e.g., venv/, *.log)

Test

D:\DreamerAI_Test\                       # Testing environment
├── app\                                 # Frontend application files (Electron/React UI)
│   ├── components\                      # Reusable React components
│   │   ├── BuildItTab.js                # Component for the "Build It" workflow step
│   │   ├── DreamItTab.js                # Component for the "Dream It" workflow step with project input
│   │   ├── FeedbackForm.jsx             # Feedback submission form component
│   │   ├── LaunchItTab.js               # Component for the "Launch It" step with export options
│   │   ├── Marketplace.js               # Placeholder for plugin marketplace UI
│   │   ├── Playground.js                # Interactive coding playground component
│   │   ├── RecoveryPanel.js             # UI for restoring project backups
│   │   └── ShareSnippet.js              # Component for generating shareable code snippet URLs
│   ├── src\                             # Source files for the React frontend
│   │   ├── App.jsx                      # Main React app component with tabs and UI logic
│   │   └── analytics.js                 # PostHog analytics integration for usage tracking
│   ├── utils\                           # Utility scripts for the frontend
│   │   ├── backup.js                    # Backup scheduling and restoration logic
│   │   └── crypto.js                    # AES encryption/decryption for project data
│   ├── firebase.js                     # Firebase configuration for user authentication
│   ├── i18n.js                         # Internationalization setup with translations
│   ├── index.html                      # Main HTML entry point for Electron
│   ├── main.js                         # Electron main process script
│   ├── package.json                    # NPM dependencies and scripts for the frontend
│   ├── preload.js                      # Electron preload script (currently empty)
│   └── renderer.js                     # Renderer process script with UI logic and tabs
├── data\                                # Manages project data and resources for testing
│   ├── config\                          # Configuration files for testing
│   │   ├── .env.test                    # Environment variables (e.g., test API keys) for test
│   │   └── config.test.toml             # Test environment config (e.g., model: gemma2:2b)
│   ├── db\                              # SQLite databases for testing
│   │   ├── dreamer_test.db              # Test database for projects and chats
│   │   └── projects_test.db             # Test database for project metadata
│   └── models\                          # Symlink to AI model storage
│       └── (symlink)                    # Points to D:\DreamerAI_Models\
├── docs\                                # Centralizes documentation for testing
│   ├── daily_progress\                  # Daily progress logs for testing
│   │   └── progress.md                  # Weekly summaries of testing progress
│   ├── dev\                             # Developer notes for testing
│   │   └── upgrade_suggestion.md        # Suggestions for future upgrades
│   ├── logs\                            # Logs for actions and debugging in test
│   │   ├── mcp_agent\log.txt            # Logs for MCP Agent operations
│   │   └── rules_check.log              # General action and rule review logs
│   ├── user\                            # User guides and manuals for test
│   │   └── user_guide.md                # User manual with troubleshooting tips
│   ├── launch_announcement.md           # Public launch announcement for v1.0.0 (test context)
│   ├── penetration_testing_plan.md      # Security audit plan for testing
│   ├── post_launch_notes.md             # Feedback and update plans post-launch (test)
│   └── v1.1_features.md                 # Roadmap for v1.1 features (test context)
├── engine\                              # Houses Python backend logic for testing
│   ├── agents\                          # Individual agent scripts
│   │   ├── base.py                      # BaseAgent class with memory and state
│   │   ├── coding.py                    # Rak (backend) and Shak (frontend) coding agents
│   │   ├── code_reviewer.py             # Agent for AI-driven code review suggestions
│   │   ├── enoch.py                     # Enoch overseer for coordinating coding agents
│   │   ├── main_chat.py                 # Main Chat Agent (Chef Jeff) with "Just Chat"
│   │   ├── mcp_agent.py                 # MCP Agent for managing prompts and tools
│   │   └── planning.py                  # Planning Agent for project blueprints
│   ├── core\                            # Core functionality
│   │   ├── backup.py                    # BackupManager for cloud backups
│   │   ├── bridge.py                    # Backend-to-frontend communication bridge
│   │   ├── cloud_sync.py                # Cloud sync with Dropbox and encryption
│   │   ├── db.py                        # SQLite database management with MCP tables
│   │   ├── logger.py                    # Logging system using Loguru
│   │   ├── project_manager.py           # Project and subproject management logic
│   │   ├── server.py                    # FastAPI server for backend endpoints
│   │   └── workflow.py                  # DreamerFlow for orchestrating 6-step workflow
│   ├── llm_service.py                   # Standalone LLM microservice (FastAPI)
│   ├── llm.py                           # Hybrid LLM with Ollama, DeepSeek, and Grok
│   ├── plugins.py                       # PluginManager for loading custom plugins
│   └── tools\                           # Shared tools for agents
│       └── tool_collection.py           # ToolCollection with fetch_url and parse_html
├── plugins\                             # Directory for custom plugins in test
│   └── (example_plugin.py)              # Placeholder for future plugin scripts
├── projects\                            # Holds generated outputs for test projects
│   ├── [project_id]\                    # Unique directory per project (e.g., 1, 2)
│   │   ├── chat_summary.txt             # Summary from chat-based project creation
│   │   ├── data_analysis.txt            # Analysis of uploaded project files
│   │   └── (project files)              # Generated code, assets, etc.
│   └── current\                         # Active project directory for export
├── templates\                           # Pre-built code templates for various app types
│   ├── blockchain\                      # Blockchain app templates
│   │   └── (Solana programs)            # Placeholder for Solana templates
│   ├── game\                            # Game development templates
│   │   └── (Unity snippets)             # Placeholder for Unity snippets
│   ├── mobile\                          # Mobile app templates
│   │   └── (React Native)               # Placeholder for React Native templates
│   └── web\                             # Web app templates
│       └── (React starter)              # Placeholder for React starter templates
├── Users\                               # Organizes user thoughts and projects for test
│   ├── [User Name]\                     # User-specific directory (e.g., Example User)
│   │   ├── Projects\                    # Active projects
│   │   │   ├── [Project Name]\          # Project directory (e.g., Example Project)
│   │   │   │   ├── Chats\               # Chat histories with agents
│   │   │   │   │   ├── [Agent Name]\    # Agent-specific chats (e.g., Jeff)
│   │   │   │   │   │   └── (chat logs)  # Individual chat files
│   │   │   │   ├── Overview\            # Project overview and notes
│   │   │   │   ├── Backtable\           # Background ideas and suggestions
│   │   │   │   ├── Tutorials\           # Educational resources
│   │   │   │   └── Recycle Bin\         # Deleted items for the project
│   │   │   └── [Subproject Name]\       # Subproject directory (similar structure)
│   │   └── Completed Projects\          # Completed projects
│   │       └── [Completed Project Name]\# Final files and documentation
├── backups\                             # Local backup storage for test
│   └── backup_test.json                 # Daily backup of test project data
├── cloud_backup\                        # Mock cloud backup storage for test
│   └── ([project_id].json)              # Encrypted test project backups
├── dist\                                # Stores distribution files for test
│   └── dreamerai-setup.exe              # Test executable (if needed)
├── Dockerfile                           # Docker configuration for test environment
├── build.bat                            # Build script for test environment
├── deploy.sh                            # Deployment script for test environment
├── README.md                            # Test environment instructions
├── requirements.txt                     # Python dependencies for test environment
└── .gitignore                           # Files and dirs to ignore in Git (e.g., venv/, *.log)

Production

D:\DreamerAI_Prod\                       # Production environment
├── app\                                 # Frontend application files (Electron/React UI)
│   ├── components\                      # Reusable React components
│   │   ├── BuildItTab.js                # Component for the "Build It" workflow step
│   │   ├── DreamItTab.js                # Component for the "Dream It" workflow step with project input
│   │   ├── FeedbackForm.jsx             # Feedback submission form component
│   │   ├── LaunchItTab.js               # Component for the "Launch It" step with export options
│   │   ├── Marketplace.js               # Placeholder for plugin marketplace UI
│   │   ├── Playground.js                # Interactive coding playground component
│   │   ├── RecoveryPanel.js             # UI for restoring project backups
│   │   └── ShareSnippet.js              # Component for generating shareable code snippet URLs
│   ├── src\                             # Source files for the React frontend
│   │   ├── App.jsx                      # Main React app component with tabs and UI logic
│   │   └── analytics.js                 # PostHog analytics integration for usage tracking
│   ├── utils\                           # Utility scripts for the frontend
│   │   ├── backup.js                    # Backup scheduling and restoration logic
│   │   └── crypto.js                    # AES encryption/decryption for project data
│   ├── firebase.js                     # Firebase configuration for user authentication
│   ├── i18n.js                         # Internationalization setup with translations
│   ├── index.html                      # Main HTML entry point for Electron
│   ├── main.js                         # Electron main process script
│   ├── package.json                    # NPM dependencies and scripts for the frontend
│   ├── preload.js                      # Electron preload script (currently empty)
│   └── renderer.js                     # Renderer process script with UI logic and tabs
├── data\                                # Manages project data and resources for production
│   ├── config\                          # Configuration files for production
│   │   ├── .env.production              # Environment variables (e.g., prod API keys) for prod
│   │   └── config.prod.toml             # Prod environment config (e.g., model: gemma2:9b)
│   ├── db\                              # SQLite databases for production
│   │   ├── dreamer_prod.db              # Prod database for projects and chats
│   │   └── projects_prod.db             # Prod database for project metadata
│   └── models\                          # Symlink to AI model storage
│       └── (symlink)                    # Points to D:\DreamerAI_Models\
├── docs\                                # Centralizes documentation for production
│   ├── daily_progress\                  # Daily progress logs for production
│   │   └── progress.md                  # Weekly summaries of production usage
│   ├── dev\                             # Developer notes for production
│   │   └── upgrade_suggestion.md        # Suggestions for future upgrades
│   ├── logs\                            # Logs for actions and debugging in prod
│   │   ├── mcp_agent\log.txt            # Logs for MCP Agent operations
│   │   └── rules_check.log              # General action and rule review logs
│   ├── user\                            # User guides and manuals for prod
│   │   └── user_guide.md                # User manual with troubleshooting tips
│   ├── launch_announcement.md           # Public launch announcement for v1.0.0 (prod context)
│   ├── penetration_testing_plan.md      # Security audit plan for production
│   ├── post_launch_notes.md             # Feedback and update plans post-launch (prod)
│   └── v1.1_features.md                 # Roadmap for v1.1 features (prod context)
├── engine\                              # Houses Python backend logic for production
│   ├── agents\                          # Individual agent scripts
│   │   ├── base.py                      # BaseAgent class with memory and state
│   │   ├── coding.py                    # Rak (backend) and Shak (frontend) coding agents
│   │   ├── code_reviewer.py             # Agent for AI-driven code review suggestions
│   │   ├── enoch.py                     # Enoch overseer for coordinating coding agents
│   │   ├── main_chat.py                 # Main Chat Agent (Chef Jeff) with "Just Chat"
│   │   ├── mcp_agent.py                 # MCP Agent for managing prompts and tools
│   │   └── planning.py                  # Planning Agent for project blueprints
│   ├── core\                            # Core functionality
│   │   ├── backup.py                    # BackupManager for cloud backups
│   │   ├── bridge.py                    # Backend-to-frontend communication bridge
│   │   ├── cloud_sync.py                # Cloud sync with Dropbox and encryption
│   │   ├── db.py                        # SQLite database management with MCP tables
│   │   ├── logger.py                    # Logging system using Loguru
│   │   ├── project_manager.py           # Project and subproject management logic
│   │   ├── server.py                    # FastAPI server for backend endpoints
│   │   └── workflow.py                  # DreamerFlow for orchestrating 6-step workflow
│   ├── llm_service.py                   # Standalone LLM microservice (FastAPI)
│   ├── llm.py                           # Hybrid LLM with Ollama, DeepSeek, and Grok
│   ├── plugins.py                       # PluginManager for loading custom plugins
│   └── tools\                           # Shared tools for agents
│       └── tool_collection.py           # ToolCollection with fetch_url and parse_html
├── plugins\                             # Directory for custom plugins in prod
│   └── (example_plugin.py)              # Placeholder for future plugin scripts
├── projects\                            # Holds generated outputs for prod projects
│   ├── [project_id]\                    # Unique directory per project (e.g., 1, 2)
│   │   ├── chat_summary.txt             # Summary from chat-based project creation
│   │   ├── data_analysis.txt            # Analysis of uploaded project files
│   │   └── (project files)              # Generated code, assets, etc.
│   └── current\                         # Active project directory for export
├── templates\                           # Pre-built code templates for various app types
│   ├── blockchain\                      # Blockchain app templates
│   │   └── (Solana programs)            # Placeholder for Solana templates
│   ├── game\                            # Game development templates
│   │   └── (Unity snippets)             # Placeholder for Unity snippets
│   ├── mobile\                          # Mobile app templates
│   │   └── (React Native)               # Placeholder for React Native templates
│   └── web\                             # Web app templates
│       └── (React starter)              # Placeholder for React starter templates
├── Users\                               # Organizes user thoughts and projects for prod
│   ├── [User Name]\                     # User-specific directory (e.g., Example User)
│   │   ├── Projects\                    # Active projects
│   │   │   ├── [Project Name]\          # Project directory (e.g., Example Project)
│   │   │   │   ├── Chats\               # Chat histories with agents
│   │   │   │   │   ├── [Agent Name]\    # Agent-specific chats (e.g., Jeff)
│   │   │   │   │   │   └── (chat logs)  # Individual chat files
│   │   │   │   ├── Overview\            # Project overview and notes
│   │   │   │   ├── Backtable\           # Background ideas and suggestions
│   │   │   │   ├── Tutorials\           # Educational resources
│   │   │   │   └── Recycle Bin\         # Deleted items for the project
│   │   │   └── [Subproject Name]\       # Subproject directory (similar structure)
│   │   └── Completed Projects\          # Completed projects
│   │       └── [Completed Project Name]\# Final files and documentation
├── backups\                             # Local backup storage for prod
│   └── backup_prod.json                 # Daily backup of prod project data
├── cloud_backup\                        # Mock cloud backup storage for prod
│   └── ([project_id].json)              # Encrypted prod project backups
├── dist\                                # Stores distribution files for prod
│   └── dreamerai-setup.exe              # Final production executable
├── Dockerfile                           # Docker configuration for prod environment
├── build.bat                            # Build script for prod environment
├── deploy.sh                            # Deployment script for prod environment
├── README.md                            # Prod environment instructions
├── requirements.txt                     # Python dependencies for prod environment
└── .gitignore                           # Files and dirs to ignore in Git (e.g., venv/, *.log)


Explanation of the Structure
Development Environment (C:\DreamerAI\):
This is the default environment where active coding and experimentation occur.

It contains the full structure as provided, including frontend (app\), backend (engine\), data, documentation, and more.

Testing Environment (D:\DreamerAI_Test\):
Mirrors the development environment with the same level of detail.

Uses test-specific configurations (e.g., .env.test, config.test.toml) and databases (e.g., dreamer_test.db) to isolate testing from development and production.

Suitable for validating changes before they go live.

Production Environment (D:\DreamerAI_Prod\):
Also mirrors the development environment with the same detailed structure.

Uses production-specific configurations (e.g., .env.production, config.prod.toml) and databases (e.g., dreamer_prod.db) to ensure stability and isolation.

Replaces the original D:\DreamerAI_Main\ (which only had the executable) to meet your requirement for a fully detailed production environment.

Contains the full source code and data structure, not just the deployed executable, allowing for consistency with dev and test.

Shared Model Storage (D:\DreamerAI_Models\):
A centralized directory for AI model files, linked via symlinks from each environment’s data\models\ directory.

Ensures all environments use the same models without duplicating files.

Key Differences Across Environments:
Configuration Files: Each environment has its own .env and config.toml files tailored to its purpose (e.g., different API keys, model versions).

Databases: Separate databases (e.g., dreamer.db for dev, dreamer_test.db for test, dreamer_prod.db for prod) ensure data isolation.

Backups: Each environment has its own backup files (e.g., backup.json, backup_test.json, backup_prod.json) to maintain independence.

Running the Application:
Each environment can be run independently from its respective directory. For example:
Dev: electron C:\DreamerAI\app\main.js

Test: electron D:\DreamerAI_Test\app\main.js

Prod: electron D:\DreamerAI_Prod\app\main.js

Alternatively, you can use the dist\dreamerai-setup.exe from each environment after building it with build.bat.

