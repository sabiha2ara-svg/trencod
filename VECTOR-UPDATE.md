# Trencod 0.10 — Vector Studio and creator rewards

## Update your existing website
1. Profile > Download my projects: keep a project/art backup on your computer.
2. Extract this ZIP. Upload the complete `trencod-app` folder to the existing
   GitHub repository root, replacing files at their existing paths. Do not upload
   a nested `trencod-app/trencod-app` folder or upload the ZIP itself.
3. Commit changes. Render > Manual Deploy > Deploy latest commit if needed.
4. Keep the existing DATABASE_URL and Neon project. No new database is needed.
5. After Live, /healthz should show version 0.10.0 and storage postgres.
6. Refresh the app with Ctrl+Shift+R. Studio > Vector Studio opens the new tool.

The update adds a reward-claims table automatically. Existing accounts, projects,
wallet balances and bought AI unlocks remain in the same database. No destructive
migration is included. A full database backup is separate from My projects export.

## Vector Studio
- 50 original editable vector starters: 20 animals, 5 characters, 10 nature
  designs, and 15 food/object designs. No Scratch artwork is copied.
- Rectangle, ellipse, triangle and freehand pencil; select/move, fill/outline,
  numeric resize/rotation, editable path points, layer order, duplicate/delete,
  undo/redo, search and expanded editor layout.
- Save to your account, reopen, save a copy, SVG export and editable JSON backup.
- Visual editor: choose a scene object, then click a vector starter or My artwork.
  Vector geometry stays vector in the generated playable game and export.
- Each drawing supports 160 shapes, 400 points per path, and 100 KB total.
  A visual game supports 32 distinct designs at once from the library of 50,
  within the existing 100 KB total sprite limit.
- This is a basic shape/path editor inspired by familiar drawing workflows,
  not full Scratch: no Bezier handles, grouping, vector costume animation,
  arbitrary SVG import or vector-art marketplace in this release.
  Imported editable JSON is validated before rendering. SVG exports can be used
  in your Code projects. Pixel art/animation and its marketplace remain available.

## Achievement Trencoins
Coin-balance badges are no longer shown or awarded. Existing internal achievement
records are retained. Complete a milestone, open Profile and click Claim once.

| Milestone | Thresholds | TC reward at each threshold |
|---|---|---|
| Original published apps/games | 1, 5, 10, 25, 50 | 10, 50, 100, 200, 400 |
| Mutual friends | 5, 10, 40, 80, 150 | 20, 40, 80, 120, 200 |
| Saved creation streak (days) | 3, 7, 14, 30, 100 | 5, 15, 30, 60, 150 |

One reward per account per achievement. Old qualifying achievements can claim
once too. Retries and simultaneous claims pay once. Unfollow/refollow cannot pay
again. Exact duplicate code, bought games and remixes do not count as new original
releases. This does not identify every near-copy or fake account; beta coins still
have no cash value. TP and earlier age-based milestones are unchanged.

## Cheaper AI
Normal Bot: 2,000 -> 50 TC. Smart Bot: 5,000 -> 150 TC.
Existing owners keep access; no automatic retroactive refund. Both retain the
shared 20-request daily cap. An owner-configured API key/model is still required;
unconfigured bots do not charge. The provider's actual API billing is separate
from Trencoins and has not been changed by this release.
