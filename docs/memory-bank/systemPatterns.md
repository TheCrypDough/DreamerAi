# DreamerAI System Patterns (V1 - Placeholder)

**Overall Architecture:** Multi-agent system (MAS) orchestrated by DreamerFlow within a Desktop Application shell.
**Frontend:** Electron Shell + React/MUI Panelized UI (Dreamer Desktop).
**Backend:** Python/FastAPI service providing API and hosting agent logic.
**Communication:** HTTP Bridge (V1), WebSockets (V1+), EventManager (V1+).
**Data:** SQLite (Dev V1), PostgreSQL planned. Local RAG DBs (ChromaDB V1). Config files (.toml/.env).
**AI:** Hybrid LLM (Local Ollama + Cloud API via Config). Specialized agents inheriting BaseAgent. RAG integration. Distillation planned.

---
*Note: Content requires review and update based on Day 1 completion and overall project goals.*
