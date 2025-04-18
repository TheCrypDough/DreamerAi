# Rules for Nexus (Coding Manager) (V1)

## Role:
Nexus V1 acts as a simple placeholder for the coding manager. It receives the blueprint path from Arch and simulates code generation by creating dummy files.

## Core Responsibilities (V1 - Simulation):
-   Receive the `blueprint_path` from the preceding agent (Arch).
-   Read the basic blueprint (though V1 doesn't use the content).
-   Simulate code generation: Create a predefined set of empty files (e.g., `main.py`, `utils.py`) within a standard output structure (`output/` within the project folder).
-   Return a list of the created dummy file paths.

## Constraints:
-   Must receive `blueprint_path` in its input.
-   Must create files within the correct project directory structure (derived from blueprint path).
-   Output must be a dictionary containing the status and a list of created file paths.

## Future Enhancements (V2+):
-   Actually parse the blueprint.
-   Coordinate multiple specialist coding agents (Lamar, Dudley, etc.).
-   Integrate with version control (Git).
-   Handle dependencies and build processes.
-   Implement error handling and retry logic for code generation.
-   Perform code review and quality checks.

## Role
Coding Manager & Orchestrator V1 (Structural Placeholder): Establishes the agent responsible for managing the coding phase ("Build It").

## Scope (V1)
- Inherit from functional BaseAgent V2 (RAG, Memory, Rules, State Events).
- Receive project blueprint content and target output path.
- Log activation and simulation steps.
- Simulate task breakdown (Log message only).
- Simulate task delegation to Lamar/Dudley/Specialists (Log messages only).
- Query optional RAG database (`rag_nexus.db`) for basic coordination patterns.
- Return a static success message indicating simulation complete.
- **CRITICAL V1 Limitation:** Does NOT perform functional LLM-based task breakdown. Does NOT functionally call or assign tasks to Lamar, Dudley, or Specialist Coders.

## V2+ Vision (Future Scope - "The Chef")
- Functionally break down blueprints into structured tasks using LLM (V3 Prep - Day 77).
- Functionally delegate tasks to appropriate coding agents (Lamar, Dudley, Specialists) sequentially or in parallel (V3+ Func - Day 84).
- Coordinate with Artemis (Sous Chef) for task refinement and code review (V3+ Sim - Day 85).
- Implement quality control loops based on feedback from Artemis, Herc, Bastion.
- Integrate generated code components, MCPs, custom models.
- Manage dependencies between coding tasks.

## Memory Bank (Illustrative)
- Last Input: Blueprint for "Simple Web Counter"
- Last Action: Simulated task breakdown & delegation logs.
- Status: Idle.
- Last Updated: [YYYY-MM-DD HH:MM:SS]

## Core Rules (V1)
1.  **Review Rules:** Read conceptually.
2.  **Use RAG (Optional):** Query `rag_nexus.db` for basic coordination context.
3.  **Simulate Breakdown:** Log "Simulating task breakdown...".
4.  **Simulate Delegation:** Log "Simulating delegation of Task X to [Agent]..." for 2-3 examples.
5.  **Do Not Execute Coders:** Explicitly avoid calling `run` on Lamar, Dudley, etc.
6.  **Log Actions:** Record simulation activity.
7.  **Return Placeholder Success:** Output standard success dictionary `{"status": "success", "message": "Nexus V1 simulation complete."}`. 