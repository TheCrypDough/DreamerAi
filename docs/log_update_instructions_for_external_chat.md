# Instructions for Requesting Log Updates via CursorAI

**Purpose:** This document outlines how you (the external chat instance) should request updates to the DreamerAI project logs. You do not have direct file system access. All log updates MUST be performed by CursorAI based on your explicit instructions.

**Core Workflow:**

1.  **Identify Logging Need:** Based on your interaction with the user, your internal processes, or the completion of a task step, determine which log file needs updating according to the project's Logging Protocol (defined in `docs/cursorrules.md`).
2.  **Format Log Entry:** Prepare the exact text for the log entry, strictly adhering to the format specified for that particular log file in the protocol. Include timestamps (YYYY-MM-DD HH:MM:SS) where required.
3.  **Instruct CursorAI:** Send a clear instruction message to CursorAI specifying:
    *   The target log file path (e.g., `docs/logs/issues.log`).
    *   The action (usually "append").
    *   The exact, pre-formatted log entry text.

**Log File Specific Instructions:**

---

### 1. Daily Context Log (`docs/daily_progress/daily_context_log.md`)

*   **Purpose:** Tracks daily progress, decisions, user vibe, suggestions.
*   **Triggers (for you):** When you complete a significant step, make a suggestion to the user, or observe relevant user feedback/vibe.
*   **Formats:**
    *   `Milestone Completed: [Completed Task/Step Description]. Next Task: [Next Task/Step Description]. Feeling: [User's vibe/your assessment]. Date: [YYYY-MM-DD]`
    *   `Suggestion: [Your suggestion detail], Task: [Current overall task name], Rationale: [Brief reason], Feeling: [Your confidence/assessment], Date: [YYYY-MM-DD]`
    *   `Observation: [Note on user interaction, progress, or state]. Date: [YYYY-MM-DD]`
*   **Example Instruction to CursorAI:**
    ```
    Cursor, please append the following entry to docs/daily_progress/daily_context_log.md:
    Milestone Completed: User confirmed understanding of Context7 tool usage. Next Task: Proceed with Day 26 Task 1. Feeling: Positive. Date: 2025-04-23
    ```
    ```
    Cursor, please append the following entry to docs/daily_progress/daily_context_log.md:
    Suggestion: Refactor the WebSocket connection logic in DreamTheatrePanel.jsx for better error handling, Task: Day 26 Task 5 (UI Integration), Rationale: Current logic lacks robust reconnection attempts., Feeling: Confident this improves stability, Date: 2025-04-23
    ```

---

### 2. Issues Log (`docs/logs/issues.log`)

*   **Purpose:** Tracks non-critical issues, warnings, or required adaptations.
*   **Triggers (for you):** When you identify a non-blocking issue, change the status of an issue, or note a resolution.
*   **Formats:**
    *   `[YYYY-MM-DD HH:MM:SS] - Issue Identified: [Issue description]. Task: [Associated Task Name]. Status: Investigating.`
    *   `[YYYY-MM-DD HH:MM:SS] - Issue Status Update: [Issue description]. Task: [Associated Task Name]. Old Status: [Previous Status]. New Status: [Current Status].`
    *   `[YYYY-MM-DD HH:MM:SS] - Issue Resolved: [Issue description]. Task: [Associated Task Name]. Fix: [Brief fix description].`
    *   `[YYYY-MM-DD HH:MM:SS] - INFO: [General informational message, e.g., adaptation notes]. Task: [Associated Task Name].` (Use for Context7 usage, BaseAgent adaptations etc.)
*   **Example Instruction to CursorAI:**
    ```
    Cursor, please append the following entry to docs/logs/issues.log:
    [2025-04-23 21:45:10] - Issue Identified: Frontend component X fails to render under condition Y. Task: Day 26 Task 4. Status: Investigating.
    ```
    ```
    Cursor, please append the following entry to docs/logs/issues.log:
    [2025-04-23 21:55:00] - INFO: Attempting to resolve Context7 ID for keytar. Task: Day 26 Task 2.
    ```
    ```
    Cursor, please append the following entry to docs/logs/issues.log:
    [2025-04-23 22:10:00] - Issue Resolved: Frontend component X rendering failure. Task: Day 26 Task 4. Fix: Corrected state handling logic.
    ```

---

### 3. Errors Log (`docs/logs/errors.log`)

*   **Purpose:** Tracks critical errors that halt execution or cause significant failures.
*   **Triggers (for you):** When you encounter a critical error that stops your current process or requires immediate user/developer attention.
*   **Formats:**
    *   `[YYYY-MM-DD HH:MM:SS] - Error Occurred: [Error type/message]. Task: [Associated Task Name]. Details: [Optional brief details/context].`
    *   `[YYYY-MM-DD HH:MM:SS] - Error Resolved: [Error type/message]. Task: [Associated Task Name]. Fix: [Brief fix description].`
*   **Example Instruction to CursorAI:**
    ```
    Cursor, please append the following entry to docs/logs/errors.log:
    [2025-04-23 21:50:15] - Error Occurred: Unhandled Exception during API call to external service Z. Task: Day 27 Task 3. Details: Service returned 503 status.
    ```

---

### 4. Files Managed Primarily by CursorAI

Updates to the following files are typically triggered by CursorAI's actions or the automated workflow after user approval. You generally do **not** need to request direct updates to these, but you might provide *information* for CursorAI to use when *it* performs the updates:

*   **`docs/logs/rules_check.log`**: Updated by CursorAI *before* its own actions. (No instruction needed from you).
*   **`docs/logs/migration_tracker.md`**: Updated by CursorAI *after* it performs file system operations (create, rename, move, delete). (No direct instruction needed from you, but if you *request* a file operation, CursorAI will log it upon completion).
*   **`docs/tasks.md`**: Updated by CursorAI as part of the Auto-Update Workflow after a task is approved by the user. (You might report sub-task status to the user/Cursor, but Cursor handles the final update).
*   **`docs/dreamerai_context.md`**: Updated by CursorAI as part of the Auto-Update Workflow.
    *   **Providing Info:** If you have key details from a task you assisted with, provide them to CursorAI for inclusion *when the Auto-Update runs*.
    *   **Example Instruction to CursorAI:**
        ```
        Cursor, when you perform the Auto-Update workflow for the completion of '[Task Name]', please ensure the summary for 'docs/dreamerai_context.md' includes the following key points: [Detail 1], [Decision rationale], [Note on issue X resolved].
        ```

**Important:** Always provide the full, correctly formatted log entry text in your instruction to CursorAI. CursorAI relies on your accuracy. 