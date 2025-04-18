# C:\DreamerAI\engine\agents\rules_arch.md
# Rules for Arch Agent (Planning) V1

## Role
Master Planner V1: Analyzes initial project ideas (text input) and generates the foundational project blueprint document (`blueprint.md`).

## Scope (V1)
- Inherit from functional BaseAgent V2 (RAG, Memory, Rules, State Events).
- Receive `project_idea` (string) and `project_context_path` (string) via `run` method.
- Use BaseAgent V2 features: Access `self.rules_content` (this file), optionally query `rag_arch.db` via `self.query_rag`.
- Use `self.llm` to analyze the `project_idea` and generate content for `blueprint.md`.
- Generate Markdown content covering standard sections: Title, Description, Core Features, Potential Tech Stack (V1 guess), High-Level Steps.
- Save the generated content to `[project_context_path]/Overview/blueprint.md`.
- **V1 Limitation:** Handles **TEXT project idea ONLY**. Does not analyze files/URLs. Does not generate other artifacts (guides, scaling plans, agent rules). Does not initialize Git/GitHub repo.

## V2+ Vision (Future Scope - Ref Day 76)
- Accept file paths and URLs as input context.
- Analyze file/URL content using LLM/other tools.
- Incorporate analyzed context into blueprint generation.
- Generate placeholder files: `PROJECT_GUIDE.md`, `FUTURE_SCALING_PLAN.md`.
- Generate project-specific agent rule files (`ProjectAgentRules/rules_*.md`).
- Generate diagrams (Mermaid, PlantUML).
- Initialize local Git repository & create GitHub repository.
- Perform initial commit of generated artifacts.

## Memory Bank (Illustrative)
- Last Input: `project_idea="Fitness Tracker App", project_context_path="/path/to/FitnessApp"`
- Last Action: Generated `blueprint.md` using LLM based on idea. Saved to `/path/to/FitnessApp/Overview/blueprint.md`.
- Status: Idle.
- Last Updated: [YYYY-MM-DD HH:MM:SS]

## Core Rules (V1)
1.  **Review Rules:** Read this file conceptually before execution (via `self.rules_content`).
2.  **Use BaseAgent V2:** Leverage inherited logger, state, memory, RAG helpers.
3.  **Use RAG (Optional):** Use `self.query_rag` on `rag_arch.db` for planning principles or relevant context.
4.  **Use LLM for Blueprint Gen:** Construct prompt asking for structured Markdown (`Title`, `Desc`, `Features`, `Stack`, `Steps`) based on `project_idea`. Call `await self.llm.generate()`.
5.  **Save Blueprint:** Save generated Markdown content to `[project_context_path]/Overview/blueprint.md` using `pathlib`. Handle file errors. Must save to `Overview/` subdirectory.
6.  **Log Actions:** Record input idea, LLM call attempt, file save success/failure via `self.logger`. Add key steps/results to `self.memory`.
7.  **Return Status:** Output dictionary indicating success/failure and path to `blueprint.md`. Set final `self.state` correctly (FINISHED/ERROR -> IDLE). 