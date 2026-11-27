# Trencod 0.15.0 — Moving platforms and more areas

## Add a moving platform
Visual editor → + Moving platform. Drag it to its starting position, then adjust Movement speed in Selected sprite behaviour. It patrols horizontally up to 80 pixels either side of its start, within world boundaries. A player standing on top is carried along and can jump off. Choose still to stop it. Costume changes preserve this behaviour. Avoid placing its travel path through other platforms or walls.

## Extend the level
Click + Area. Each click adds an adjacent 800 × 450 section with ground and moves the one Goal to the far end. Up to five areas (4000 × 450 total), with 100 objects total. These are sections of one continuous level, not separate levels or rooms. All areas share the background and physics.

Use Editing area to switch the part shown on the editor canvas. New sprites appear in the current area. X coordinates are world coordinates: Area 1 starts at 0, Area 2 at 800, Area 3 at 1600. Selecting Player or Goal shows its area. The game camera follows the player automatically. Collect points across the whole level before reaching the Goal.

Undo can reverse adding an area or platform. Save game preserves the expanded world; Save & edit code includes its generated behaviour. As before, visual edits regenerate generated code, so Save a copy is useful after custom code changes.

## Validation
Automated tests cover adding areas and the five-area limit, area-specific object creation and resizing, editor Undo, moving-platform riding/reversal/jumping/restart, camera tracking across the 800px boundary, save/reopen, invalid world sizes and bounds, and legacy sprite behaviour. Browser rendering has not been manually verified.

## Upload
Extract the ZIP. On GitHub open the EXISTING trencod-app folder, then Add file → Upload files. Upload the contents of the extracted trencod-app folder (not another nested trencod-app folder). Commit and deploy the latest commit on Render. Keep Root Directory trencod-app and existing environment variables.

Includes previous Python, mobile, Find & Replace, Duplicate file, music, animation and sprite updates, plus ANIMATION-IN-CODE.md.
