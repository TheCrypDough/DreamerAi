# System Design Patterns and Architecture

**Last Updated:** 2024-07-27 18:35:00 # Placeholder

## Core Architecture
- **Hybrid Desktop Application:** Uses Electron for the frontend shell (`app/`) and a Python backend (`engine/`) running locally.
- **Microservices-like Backend (Agents):** The `engine/` aims for modularity, with distinct AI agents potentially running as separate processes or managed services (long-term vision). Currently, they are Python classes within the `engine/agents/` directory, interacting via a FastAPI server (`engine/core/server.py`).
- **Centralized Configuration:** Uses TOML (`data/config/config.dev.toml`) for general settings and `.env` files (`data/config/.env.development`) for secrets (API keys, etc.), loaded at startup.
- **Message/Event-Driven (Future):** While currently using basic FastAPI calls, the plan likely involves more robust inter-process communication (IPC) between Electron and the backend, and potentially message queues (like Redis pub/sub) between backend components.

## Key Design Patterns
- **Agent-Based System:** Core logic encapsulated in specialized AI agents (e.g., `MainChatAgent`, `Jeff`, etc.) inheriting from a `BaseAgent` (`engine/agents/base.py`).
- **Configuration-Driven LLM Selection:** The LLM module (`engine/ai/llm.py`) selects and interacts with AI models (local Ollama, cloud OpenRouter) based on settings in `config.dev.toml`, supporting provider preference lists and agent-specific overrides.
- **Hybrid LLM Strategy:** Leverages both local models (Ollama) for potential cost savings, offline capability, or specific tasks, and powerful cloud models (via OpenRouter) for high-quality generation, allowing flexible fallback and tiering.
- **Singleton Pattern (Implicit):** Core services like the logger (`DreamerLogger`), database (`DreamerDB`), and LLM manager (`LLM`) are often instantiated once and accessed globally or passed via dependency injection.
- **Logging Facade:** Uses Loguru via `DreamerLogger` (`engine/core/logger.py`) to provide a consistent logging interface across the backend, directing output to console and multiple files.
- **Repository Pattern (Simplified):** The `DreamerDB` class (`engine/core/db.py`) acts as a simple data access layer for the SQLite database (initially).
- **Caching (Planned):** LLM responses will be cached using Redis (`engine/ai/llm.py` has integration, Day 38 activation) to improve performance and reduce costs.

## Component Relationships
```mermaid
graph TD
    subgraph Frontend (Electron/React - app/)
        UI[UI Panels - React Components]
        Renderer[renderer.js]
        Main[main.js - Electron Main Process]
        Preload[preload.js]
    end

    subgraph Backend (Python - engine/)
        Server[FastAPI Server - core/server.py]
        LLM[LLM Module - ai/llm.py]
        DB[Database - core/db.py]
        Logger[Logger - core/logger.py]
        BaseAgent[BaseAgent - agents/base.py]
        Agent1[Agent: MainChat - agents/main_chat.py]
        AgentN[Agent: ...]
    end

    subgraph Data (data/)
        ConfigTOML[config.dev.toml]
        ConfigENV[.env.development]
        SQLiteDB[dreamer.db]
        OllamaModels[(Ollama Models - via Symlink)]
        Redis[(Redis - External/Docker)]
    end

    UI --> Renderer
    Renderer -- IPC --> Main
    Main -- Loads --> index.html & Preload
    Renderer -- Fetch API --> Server

    Server -- Uses --> Agent1
    Server -- Uses --> AgentN
    Agent1 -- Inherits --> BaseAgent
    AgentN -- Inherits --> BaseAgent
    BaseAgent -- Uses --> LLM
    BaseAgent -- Uses --> DB
    BaseAgent -- Uses --> Logger
    
    LLM -- Uses --> Redis
    LLM -- Reads --> ConfigTOML
    LLM -- Reads --> ConfigENV
    LLM -- Accesses --> OllamaModels
    LLM -- Calls --> OpenRouterAPI[External: OpenRouter API]

    Server -- Reads --> ConfigTOML
    DB -- Accesses --> SQLiteDB
    Logger -- Writes --> LogFiles[docs/logs/*]

    ConfigTOML & ConfigENV -- Contain Settings --> DB & LLM & Server & Agents
``` 