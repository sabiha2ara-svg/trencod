# Trencod 0.12.2 — Insert saved animations in Code

1. Design → Pixel & animation: draw your frames and Save to My projects.
2. Open your game in Code. Click Animation / saved art in the editor toolbar.
3. Find your saved animation by name. Preview it, set size (16–512 px), speed, horizontal flip, and optional Play/Pause controls.
4. Click Insert into game. The code goes inside index.html and Run previews the game.
5. Press Save; Publish when ready for others to play.

No manual copying of HTML/CSS, no AI purchase, and no API key needed.
Use in game in the drawing studio now saves your artwork before explaining the insertion steps.
The picker includes saved pixel art and accessible team pixel/animation files. Vector files remain in Vector Studio.
Each insertion creates an independent copy with an embedded PNG sprite sheet. Editing the original art later does not change already-inserted copies. Multiple copies can have their own Play/Pause button.
The picker inserts visuals only. Use Code → Music to attach game music.
Existing source/compiled-size limits still apply; oversized insertion is rejected before changing your code.
Canvas-based games can display this as an HTML overlay; it does not automatically become a collision-enabled game character. Python practice is separate.

## Deploy
Extract this ZIP. Upload/replace trencod-app at the same repository path. Do not create an extra nested trencod-app folder. Commit, then deploy the latest commit in Render. Leave your DATABASE_URL and other existing environment variables unchanged. Refresh with Ctrl+Shift+R. /healthz shows 0.12.2 after this version deploys.

## Validation
Automated DOM tests exercise saved-art selection, preview generation, size/speed/flip, independent Play/Pause, empty search, insertion preserving the existing HTML, and source compile/reopen. Existing JavaScript regression tests pass. Native-browser visual layout has not been manually checked in this environment.
