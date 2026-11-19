# Trencod 0.13.0

## Play tab: creators in the main search box
Type a username in the existing Search games or creators box on Play. Matching creator profiles appear above game results. This includes creators without published games. Names work regardless of letter case, and an optional @ is accepted for creator lookup. The standalone Creators directory is retained. Up to 40 profiles are shown per query.

## Export artwork directly from Visual game
Select an object, apply a bitmap or vector sprite, then press Copy / export sprite code in Sprite library.
- HTML / SVG: copy and paste into the body of your game's index.html.
- Canvas JavaScript: paste into a JS file, then call the generated uniquely named sprite.draw(ctx, x, y, width, height, performance.now()) in your existing game loop.
- Copy code and Download code are both available. If clipboard access fails, the code is selected for Ctrl+C.
This copies artwork, including bitmap animation frames. Movement, collisions and game rules are not exported with the individual sprite. Use Save & edit code for the whole visual game. Original art is unchanged.

## 50 more sprites
100 editable vector starters, plus the existing 12 pixel starters. New designs include dungeon key, shield, sword, bow, helmet, boot, backpack, compass, map, lantern, candle, book, gem, crown, medal, clock, telescope, camera, gamepad, battery, magnet, traffic light, signpost, bridge, tent, campfire, snowman, cactus, palm, pinecone, snow peaks, rainbow, lightning, raindrop, snowflake, planet rings, satellite, UFO, train, balloon, bicycle, pizza, ice cream, cupcake, carrot, watermelon, banana, pear, cherry and honey jar.
Search the starter library by name. The per-game limits remain 32 sprite designs and 100 objects.

## Backgrounds
Visual game → World background: Night hills, Meadow, Desert, Snow, Sunset, Space or Solid color. Choose a custom sky color or Reset sky color. Undo supports background changes. Backgrounds persist in saves and scene backups, and render in published/exported games. Sprite transparency no longer paints a dark rectangle over the background.
No personal-photo import was added, as requested.

## Install
Extract ZIP, replace trencod-app at its existing GitHub path, commit and deploy the latest commit in Render. Keep DATABASE_URL and existing environment variables. Refresh Ctrl+Shift+R. /healthz should show 0.13.0.

## Checks
70 SQLite backend tests and 69 PostgreSQL backend tests passed. JavaScript tests cover creator search races, bitmap/vector code exports, background Undo/save, 100 sprite exports, and prior editor/music workflows. Native-browser visual inspection has not been performed in this environment.
