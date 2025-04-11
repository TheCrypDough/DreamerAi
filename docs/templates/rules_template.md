# Rules for [Agent Name Placeholder]

## Role
[Briefly define the agent's primary function and archetype within the Dream Team.]
[E.g., User Interaction Conduit, Master Planner, Coding Specialist, etc.]

## Scope
[Detail the specific responsibilities and boundaries of this agent.]
- What inputs does it primarily handle?
- What are its key outputs or artifacts?
- What specific tasks does it perform?
- What are its key limitations (V1)?

## Memory Bank (Illustrative Structure)
[Define the conceptual structure for how this agent's short-term memory or key context should be maintained. This guides logging and potential BaseAgent memory usage.]
- Key Input Context: [Example: Last User Query]
- Key Operational State: [Example: Current Task Status]
- Key Output Context: [Example: Generated Plan Summary]
- Relevant Project Context: [Example: Active Project ID/Name]
- Last Updated: [Placeholder Timestamp Field]

## Core Rules / Operating Principles
[List the fundamental rules governing this agent's behavior.]
1.  **Review Rules:** [Standard: Agent should conceptually review its rules before complex tasks.]
2.  **Use RAG:** [Standard: Specify if/how agent should use its specific RAG DB.]
3.  **Use Assigned LLM:** [Standard: Refer to using LLM via LLM class, respecting config.]
4.  **Maintain Memory:** [Standard: Reference adding key interactions via BaseAgent memory.]
5.  **Task Handoff:** [Specify standard protocol for handing off tasks/results - e.g., Via Hermie/Events.]
6.  **UI Communication:** [Specify standard protocol for UI updates - e.g., Via Bridge/WS.]
7.  **Logging:** [Standard: Use internal self.logger for key actions/decisions.]
8.  **Error Handling:** [Specify basic error reporting approach.]
9.  **Collaboration:** [Specify basic rules for interaction with other specific agents if applicable V1+.]
10. **[Agent Specific Rule 1]:** [Placeholder for unique constraints]
11. **[Agent Specific Rule 2]:** [Placeholder for unique constraints]

## Communication Protocols (V2+)
[Placeholder section for defining specific interaction patterns with other agents later.] 