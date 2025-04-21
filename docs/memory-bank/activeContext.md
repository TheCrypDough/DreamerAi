# DreamerAI Active Context (Memory Bank)
Last Updated: 2025-04-18 02:21:00 (After Day 18 Completion & Correction)

## Current Work Focus
*   **Starting Day:** Day 19 - Hermie V1 Basic Routing Simulation.
*   **Goal:** Implement Hermie's initial task distribution simulation to Arch (Planning) and Lewis (Administrator).

## Recent Changes (Corrected Day 18 - Hermie V1 Placeholder Test)
*   **Completed:** Successfully executed the *corrected* scope for Day 18.
*   **Verification:** Confirmed `engine/agents/communications.py` contains the correct `HermieAgent` V1 placeholder code, inheriting from the stabilized `BaseAgent` V2.
*   **Testing:** Replaced `main.py` content with a script focused *exclusively* on testing the Hermie V1 structure and its inherited RAG V2 capabilities. This test ran successfully, verifying:
    *   Hermie V1 initialization.
    *   Successful RAG query via inherited `query_rag`.
    *   Correct simulation log messages.
    *   Correct static success dictionary returned.
    *   Graceful handling (via `try/except`) of missing DB Pool functions (`initialize_db_pool`, `close_db_pool`) in `engine.core.db`.
*   **RAG Seeding:** Created and ran a temporary seed script (`seed_rag_hermie.py`) to populate Hermie's RAG DB, then deleted the script.
*   **Corrections:** This followed a significant correction process where incorrect changes made earlier in the day (based on a misunderstanding of Day 18's scope) were reverted using Git. Strict adherence to the guide's task sequence and scope is now reinforced.

## Next Steps
*   Proceed with the first task of Day 19 as defined in `DreamerAi_Guide.md`: Modify `engine/agents/communications.py` (HermieAgent `__init__` and `run` methods for basic routing).
*   Follow subsequent Day 19 tasks sequentially: Modify Arch and Lewis to add `receive_task`, update `main.py` for testing, execute test, commit/push.

## Active Decisions & Considerations
*   **Guide Adherence:** Strict adherence to the `DreamerAi_Guide.md` task order and scope for Day 19 is mandatory.
*   **BaseAgent V2 Adaptation:** Continue applying the established strategy: prioritize guide *intent* but adapt code snippets (especially for core functions like RAG, memory, state) to use the standardized `BaseAgent` V2 methods.
*   **DB Pool Functions:** The missing `initialize_db_pool`/`close_db_pool` functions in `engine.core.db` remain a known issue to be addressed later, likely during PostgreSQL integration (Day 100 target). Current tests needing DB context (like BaseAgent V2 init) should continue to handle their absence gracefully if possible.
*   **Open Issues:** Keep track of open issues logged in `issues.log` (e.g., Jeff n8n handoff verification).

# Active Context
*Last Updated: 2024-07-28 17:30:00*

*   **Current work focus:** Starting Day 26, Task 1: Navigate to C:\DreamerAI\app. Run npm install electron-oauth2 keytar.
*   **Recent changes:** Completed Day 25 (Tasks 1-8): Added GitHub OAuth placeholders/config to `.env.development` and `config.dev.toml`. Created backend FastAPI endpoint `/auth/github/token` in `server.py` (using global variable for V1 token storage). Added `httpx` dependency to `requirements.txt`. Created and ran `test_github_token_endpoint` function in `main.py` to verify endpoint functionality. Confirmed successful token reception via logs (HTTP 200). Pushed all changes to GitHub.
*   **Next steps:** Proceed with Day 26, Task 1: Install required Node dependencies (`electron-oauth2`, `keytar`) for the GitHub Authentication UI component.
*   **Active decisions:** Confirmed `/auth/github/token` endpoint functions correctly on port 8000. Deferred unrelated Old Guide Day 25 features (JetBrains, Testing, Templates, Subprojects, UX) per plan. Using global variable for backend token storage is temporary (V1), requires secure, user-specific solution later.
