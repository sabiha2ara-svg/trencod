NEON 0.9 UPDATE: For hosted setup, follow NEON-SETUP.txt first. Older SQLite/disk instructions below apply only to local/older installations.

# Trencod Studio workspace update

Includes the previous exclusive-sale fix. Read EXCLUSIVE-SALES-UPDATE.md before deploying; back up the LIVE database first.

## Use
Open Code or edit a project. Explorer is on the left, source editor in the middle, purchased/configured AI assistant on the right. Maximize is directly above the code; Restore exits it. Ctrl+S saves, Ctrl+Enter runs.

- + File accepts paths such as scripts/player.js or styles/world.css. + Folder creates directories. Rename/delete files; click an empty folder to delete it. Keep index.html as entry.
- Reference scripts with <script src="scripts/player.js"></script> and styles with <link rel="stylesheet" href="styles/world.css">. Local classic JS and linked CSS (including quoted CSS imports) are bundled for play/export. SVG images can be linked locally. External URLs remain external.
- Source tree is embedded in the project HTML, so existing history, sale, remix and save APIs keep it. No database column migration is needed for the workspace.
- Source backup downloads editable JSON; Restore backup restores that tree. Download HTML exports the playable game with source embedded. Published/remixable games therefore expose source, as before.
- Pixel art opens a 16x16 canvas with color, eraser, undo, clear, PNG download and insertion into index.html. Full multi-frame animation remains in Studio → Pixel art.
- Font size and Wrap controls adjust the editor. Unsaved work has browser-local recovery; save/download before leaving. This is a plain-text editor, not the Monaco/VS Code engine; syntax highlighting and autocomplete are not included.
- AI uses existing purchased bots, server-side provider configuration, and existing quota. It shares only the question, plus the active file when Include current file is checked. Suggestions never change files automatically. No API key is included in this ZIP.

## Beta boundaries
64 text files + 64 folders; 90 KB source and 150 KB compiled output. HTML/CSS/classic JavaScript plus editable SVG/JSON/TXT. JSON fetch, HTML multi-page navigation, npm modules, Python/Java/C++ execution, and binary file imports are not bundled. Update code references yourself after rename/delete. Remote resources require a network connection. Missing local assets produce a named error instead of silently publishing a broken reference.

## Validation
40 Python tests passed (accounts/community/marketplace plus static assets and source preservation through save/publish/remix). 11 JavaScript compiler tests passed. JavaScript syntax checks passed. Automated browser interaction/visual checks were unavailable because the browser executable was missing. No live website deployment performed.

## Deployment
Do not delete your existing repository/service/data. Confirm and download a backup of the live Render database before redeploying, especially on a free instance. Replace source files with the extracted trencod-app folder at repository root. Existing Google verification meta tag is preserved. Deployment details are in EXCLUSIVE-SALES-UPDATE.md.

## Visual sprite library (included)
Visual Editor now has a Sprite library below its canvas/actions:
1. Select a player, enemy, coin, platform or goal on the canvas.
2. Choose a starter sprite, Draw new sprite, My artwork, or Purchased artwork.
3. Click the design to apply it. Play preview runs the sprite's animation; Save game stores it.

12 original starter designs: dog, cat, robot, slime, ghost, star, heart, coin, tree, flower, flag, crystal. They are free to use. Drawing creates a 16x16 single-frame design inside this game. Use the existing Pixel & animation editor for saved multi-frame art. My artwork fetches your currently accessible personal files; Purchased artwork uses your recorded creator-art purchases (including earlier licenses). Legacy demo HTML sprite packs are not imported here.

32 unique designs and 100 objects per scene, with a 100 KB total sprite budget; 1–16 frames per design. Reusing the same design does not duplicate pixel data. Remove unused designs to free space. Sprites change appearance; collision boxes and player/enemy behavior remain the selected object's existing behavior. This is not a new AI character/behavior editor. Art is embedded in exported/remixable games and is inspectable, not DRM.

Updated validation: 47 Python tests, 11 workspace compiler tests, and 2 sprite JavaScript checks pass. Tests cover retained scene artwork, generated runtime, invalid/missing/oversized sprites, legacy scenes, 12 starter designs, animation timing and transparent pixels. Browser interaction/visual testing remains unverified. No live deployment.
