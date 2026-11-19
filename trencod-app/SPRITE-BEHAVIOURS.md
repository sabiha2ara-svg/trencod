# Trencod 0.14.0 — roles and costumes

## Add sprites from the front toolbar
- + Sprite opens the library in Add new sprite mode. Choose Enemy, Points, Platform, Pet or Decoration behaviour, then click any costume.
- + platform, + points, + enemy, + pet and + decoration add an object with its behaviour ready.
- Player and Goal select the existing objects. This platformer keeps exactly one player and one finish point.
- Sprite shortcuts appear for costumes already used in the game. Each role/costume/movement combination gets a shortcut, reusing its behaviour and settings. Player/Goal shortcuts select those unique objects.

## Behaviour versus appearance
Change selected costume in Sprite library changes only the artwork. Object type, position, size, movement mode and movement speed remain unchanged.
Player uses arrow keys/A/D to move and Space/W to jump. Platform is solid. Points collect on contact; collect all to unlock the goal. Enemy hurts on contact. Pet follows as a friendly flying companion (no combat or platform physics). Decoration has no collision or damage.
Enemy movement: Chase, Patrol (80 pixels either side of its start, clamped to scene bounds), Still. Pet: Follow or Still. Decoration: Still or Patrol. Adjustable speed 0–400 px/s. Player has its own existing movement/jump/gravity controls.
Drag any object to change its starting position. Play preview runs the generated behaviour. Save & edit code opens the whole generated game for manual changes; individual sprite code export still exports artwork, not game rules.

## New costumes
Six original role costumes: Trencod Scout (player), Bramble Bot (enemy), Star Portal (goal), Meadow Platform, Point Spark and Pocket Pup. They are in the sprite library (106 vector designs plus the 12 pixel starters). New scenes and new role objects use these costumes automatically. Existing scenes are not rewritten; select an object and click Use role costume to update its look.
Limits remain 100 objects and 32 embedded designs per game. Multiple objects can share one costume.

## Install
Extract ZIP, upload/replace trencod-app at its existing GitHub path, commit, deploy latest commit on Render, then Ctrl+Shift+R. Keep DATABASE_URL and all existing settings. /healthz reports 0.14.0 after deployment.

## Verification
Automated tests check costume changes preserve behaviour and speed, save/reopen of new roles, validation, movement helpers, vector drawings, and previous editor features. Native-browser visual appearance has not been manually verified here.
