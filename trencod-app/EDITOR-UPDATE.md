# Trencod 0.12.1 — Learning-first editor

## Changes
- Hold Shift while dragging Ellipse/Rectangle to draw a circle/square. Shift during movement constrains to the dominant horizontal/vertical axis.
- Copy answer and AI settings now use separate full-width rows with clear spacing in the AI sidebar.
- Normal (50 TC): one hint, a simple explanation, at most 8 example lines.
- Smart (150 TC): existing-code debugging, reasoning and test suggestions, at most 20 example lines.
- Both are tutors: no automatic file edits, upload or publish actions. Model instructions and a response guard discourage whole-app answers; this is not an absolute guarantee about model output. Existing purchases remain valid. Configured AI credentials/models are still required; all manual editors remain free.
- Main Design / Code / Python tabs. Pixel and Vector are nested inside Design alongside Visual game. Python is also visible in the main header. Saved game IDs carry between Design and Code. Code cannot automatically become a visual scene. Visual saves regenerate code: save a copy to preserve separate code edits.
- Colored HTML, CSS, JS, PY and other file-type markers in Explorer.
- Wrapping toolbars and responsive columns; Run and Save in maximized Code; Restore inside maximized Vector.
- Python practice executes the selected .py file in a browser worker with Pyodide 0.29.3. First run needs internet and downloads a runtime. Basic print, maths, functions and local Python imports are supported. No server execution, pygame UI or interactive input. Stop, a 15-second execution limit and an output limit prevent runaway practice sessions. Save retains Python source; Publish still publishes the HTML web game.
- All 0.10 vector, badge and ownership features retained.

## Upload
1. Download your current source backup before replacing files.
2. Extract the ZIP. Upload/replace its trencod-app folder at the existing GitHub repository root. Do not create trencod-app/trencod-app.
3. Commit and deploy the latest commit on Render. Keep the same Neon DATABASE_URL and existing environment settings. Never upload your .env or database credentials to GitHub.
4. Hard refresh the site. /healthz should report version 0.12.1 and storage postgres.

## Browser check after deployment
- At desktop and narrow phone widths, open Code and confirm buttons wrap without overlap. Maximize, Run, Save, then Restore.
- Open Python practice, Run the starter and expect My score: 5. Try Stop. If the runtime/CDN is blocked, source remains saveable; report the displayed error.
- Save/reopen a project with a .py file and confirm its source is retained. Python programs are practice source, not published Python web apps.
- Save a visual game, use its Code link, then return through Design. Confirm any unsaved-work prompt before switching.
- Confirm 50 vector starters, owned bots and existing creator projects remain available.

Validation details are in TEST-RESULTS.md. Real-browser rendering and CDN/WASM execution could not be checked in the build environment. This ZIP has not been deployed to your live account.
