# Active Project Context

**Last Updated:** 2024-07-27 21:20:00 # Placeholder

## Current Focus
- Completed Day 10 (UI Shell: Tabs, Beginner Mode & Backend Listener).
- Successfully implemented electron-forge build process (Webpack/Babel) as a deviation to handle JSX transpilation.
- Verified UI shell functionality, including MUI components and backend listener.
- Transitioning to Day 11.

## Recent Changes & Decisions
- Created `app/src/App.jsx` with React/MUI components and HTTP listener.
- Updated `renderer.js` to mount `App.jsx`.
- Deviated from guide sequence: Installed and configured `electron-forge`, `plugin-webpack`, `babel`, and related loaders/dependencies.
- Created `forge.config.js`, `webpack.main.config.js`, `webpack.renderer.config.js`, `webpack.rules.js`.
- Modified `package.json` (main entry point, forge scripts, dependencies).
- Modified `main.js` (Forge WEBPACK_ENTRY constants).
- Modified `forge.config.js` (added `devContentSecurityPolicy`).
- Modified `index.html` (removed hardcoded script tag).

## Next Steps
- Begin Day 11 tasks as per `DreamerAi_Guide.md`.
- Task 1: (Placeholder - Get from Guide).

## Active Considerations
- Need to address `npm audit` vulnerabilities later.
- Backend bridge needs implementation to send messages to the UI listener.
- Placeholder UI content needs replacement with actual panel components.

## Current Work Focus

*   **Current Task:** Day 21 Task 4: Start Backend Server (`engine/core/server.py`).
*   **Goal:** Launch the main FastAPI backend server, which now includes the WebSocket endpoint (`/ws/dream-theatre/{client_id}`) managed by `DreamTheatreService`.
*   **Next Steps:** After starting the server, proceed to Day 21 Task 5: Perform Frontend Test (Online Backend) to verify WebSocket connection establishment.

## Recent Changes

*   Completed Day 21 Task 1: Created `dream_theatre_panel.py` and `dream_theatre_service.py`.
*   Completed Day 21 Task 2: Integrated the Dream Theatre panel into the React frontend (`App.jsx`), including adding the WebSocket connection logic in `DreamTheatrePanel.js`.
*   Completed Day 21 Task 3: Performed frontend testing with the backend *offline*. Verified UI loaded and expected connection errors occurred for both the Chat API fetch and the Dream Theatre WebSocket.

## Active Decisions & Considerations

*   The backend server needs to be started in the `engine/core` directory using `uvicorn server:app --reload --port 8090`.
*   The WebSocket endpoint is running on the same FastAPI instance but implicitly uses port `8091` based on the frontend connection string `ws://localhost:8091/`. Need to ensure the backend server is configured to handle WebSocket connections appropriately (FastAPI handles this inherently, but port discrepancy needs monitoring if issues arise, though `8091` might be a separate WebSocket-specific server in a future iteration - for now, assume FastAPI handles it on 8090).
*   The frontend test (Task 5) will confirm if the WebSocket connection succeeds now.

*Last Updated: 2025-04-21 HH:MM:SS* 