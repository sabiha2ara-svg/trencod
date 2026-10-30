# Trencod 0.8: what works and what still needs connecting

Working: accounts; published browser games; private team rooms with invite codes, text chat (three-second polling), owner removal and invite rotation; shared revisioned HTML/CSS/JavaScript files; free 16×16 pixel drawing and up to 16 animation frames; PNG sprite-sheet, editable JSON and animated HTML export; artwork insertion into games; creator source-license sales and seller coin earnings; purchased-version snapshots; bot unlock accounting; account milestone bonuses.

A new code project is empty. Built-in games are examples, not newly generated creator projects. Teams edit and explicitly save shared files, with conflict detection; this is not simultaneous character-by-character editing. Chat is server-stored, not end-to-end encrypted. Files and chat are private to room members and the server owner.

## Keep accounts during updates

Keep the same database. Desktop users can run UPGRADE-KEEP-CREATORS.bat in a newly extracted folder, before first startup, and choose the old installation. The import copies SQLite via its backup API, including committed WAL data; it does not overwrite a destination database. Python's tkinter folder picker is needed. The Windows launcher and picker still need validation on Windows.

On hosting, keep the same persistent disk and TRENCOD_DATA_DIR across deployments. Do not upload a blank replacement data folder. Deploy source changes to the same service. The first 0.8 migration creates data/before-0.8.sqlite3 if a database exists. All schema changes are additive. The usual manage.py backup command also remains available. Without keeping or importing the database, a separate folder is a separate installation.

## Coin rules used in this build

Signup gives 100 TC once. At account age 60 days, +200 TC can be claimed once. At 90 days, +300 TC can be claimed once. These are grants, not balance resets, and do not repeat. Age is calculated from the recorded welcome bonus. The old daily giveaway endpoint is disabled. Existing balances and old asset purchases are preserved.

A source-license purchase atomically debits the buyer and credits the seller the full price. Concurrent retries cannot charge twice. Buyers retain the purchased code and license terms if the seller changes or removes the listing. The listed version changes only when its owner explicitly updates the listing. Bot unlock prices are 2,000 and 5,000 TC; no extra coin charge per prompt. Beta usage is capped at 20 AI requests per user per UTC day across bots; failed requests count. These limits are shown before purchase.

This is still a test economy. Alternate-account welcome-bonus farming is not prevented by these limits. Identity/abuse controls, refunds, disputes and moderation are needed before a real-money launch. Coin scarcity alone does not create demand; useful games, art and dependable tools do.

## AI connection

An actual server-side OpenAI Responses API adapter is implemented. No key is included and no live AI call was made in testing. The site owner sets these server environment variables:

- OPENAI_API_KEY: provider key; never put it in frontend code, chat or GitHub.
- TRENCOD_NORMAL_MODEL: model ID available to that provider account for Normal Bot.
- TRENCOD_SMART_MODEL: model ID available to that provider account for Smart Bot.

Choose the two model IDs deliberately; the names do not guarantee different intelligence if you configure the same model. Restart the server after configuration. Configure a provider-side spending limit. Provider usage costs are separate from test Trencoins. Set neither key nor models until you intend to enable paid provider calls. A configured connection is not a guarantee that provider billing/quota is working.

Only the submitted prompt is sent. Room files and messages are not uploaded automatically. AI returns reviewable suggestions and does not execute, edit, save or publish code. It can propose game code and pixel-art designs as text; this is not an image-generation service. Each response has a token cap and a network timeout. API responses are requested with store=false; provider policies still apply.

API reference: https://developers.openai.com/api/reference/resources/responses/methods/create

## Real-money checkout

The requested 10,000 TC for US $100 pack is shown as unavailable. No payment form or fake successful purchase exists. A payment provider, merchant account, verified payment webhooks, idempotent fulfillment, refunds and chargeback handling must be connected before enabling it. No seller cash-out exists. Do not market test coins as redeemable cash.

## Source licenses and credit

Games remain free to play; buyers purchase a source reuse license. The seller chooses optional creator credit or required credit in the exported game and external store listing. This beta does not attempt to measure how much code has changed. Creator credit is included automatically in a purchased download when required. Trencod exports include platform credit. External listing text remains the publisher's responsibility.

Browser game code is inspectable. This is licensing, not DRM or source secrecy. Existing free-remix rights are not revoked by later listing a game. Known purchased copies and remixes cannot be relisted as originals through the marketplace. A rights checkbox is not automated copyright verification; copied/reuploaded code can bypass lineage checks. Required credit can also be manually removed from exported source; enforcement is not automatic.

Art creation/export is free. Old demo sprite purchases remain downloadable. In-game coin spending, voice/video calls, automatic moderation, email/password recovery, native Android builds and non-web-language runners are not implemented in this release.

## Hosting

Use the existing Render upload guide and render.yaml with a persistent disk. This build has not been deployed. Localhost addresses work only on the host computer; team members need the same hosted server. SQLite supports this small single-instance beta, not a globally scaled Discord replacement. Start with a small invited testing group.


## Profile and achievements (0.6)

The header Profile button opens your account page. Sign out appears only inside your own profile. Other creator profiles show earned badges, public games, followers and following, but do not expose wallet balance, TP or daily activity history. Creator usernames link to their profiles from game cards, game pages and comments. The Creators directory supports username search.

Badges are permanent and persisted in SQLite:
- Eligible TC balance milestones: 50, 100, 200, 500, 1,000, 2,000, 5,000.
- Creative streak: 3, 7, 14, 30, 100 consecutive UTC days.
- Original published games: 1, 5, 10, 25, 50.
- Mutual friends: 6 (more than five), 10, 40, 80, 150.

Both users following each other makes a mutual friend. A single follower does not count. Earned friend badges remain after unfollowing; the live friend count changes. Exact/whitespace-equivalent code copies, republishing the same project, remixes and known purchased copies do not add extra original-game credits. This is basic duplicate detection, not gameplay-quality assessment or a plagiarism detector.

TC badge eligibility is calculated from creator-sale ledger credits minus spending, clamped at zero after each debit. Spending consumes this eligible balance first. The highest eligible balance ever reached unlocks the badges. Welcome, daily and milestone grants, Studio Support credits and all TP bonuses are excluded. For old accounts, their ledger reconstructs prior peaks. Current original published projects can be backfilled; old daily editing history cannot be reconstructed and streak recording starts with 0.6. A recovered historical badge’s unlock timestamp is its recognition time, not an invented original date.

Creators with at least six mutual friends earn 50 bonus TP on the first nonempty changed code/art save of each UTC day. Repeating a save, changing only a title, chat, comments, passive visits or adding more groups gives no extra reward. All personal and shared editors use the same per-user daily limit. TP is separate from TC, cannot be spent/converted, and never unlocks a badge by itself. Saving changed code/art records streak activity even before six friends. Daily boundary is 00:00 UTC / 05:30 India time. A missed day resets current streak, preserving best streak and earned badges. Alternate-account friendship farming is still possible; this beta does not verify unique humans.

## Comments

Published games accept signed-in comments (1,000 characters; ten per five minutes). Comments render as plain text. The comment author or game creator can remove them. Other users can report a comment for owner review. Reports do not automatically hide text; there is no automatic content moderation. Owner commands:

    python manage.py comment-reports
    python manage.py hide-comment COMMENT_ID

The latest 100 visible comments are shown. Comments are public on public games; no private-game comments are exposed. Removed text remains server-side for review but is hidden in the UI.

## Random Studio Support purchases

This is a transparent platform-funded program, not fake customer activity. Default budget is zero, program disabled. To explicitly fund it with test coins and enable:

    python manage.py support-fund 1000
    python manage.py support-on

To stop it:

    python manage.py support-off

The command issues a finite test-coin treasury and records the funding. It does not spend real money. This source of coins is separate from user-earned sales and must be considered before any paid economy launch. Do not treat these purchases as evidence of market demand.

When somebody visits Creator Market, an enabled/funded program may randomly choose one eligible unsold listing. Maximum one purchase per UTC day; price no greater than 100 TC or remaining budget; at most one support purchase per seller per rolling 30 days; no repeat support purchase of the same listing. The underlying game must be public and unchanged for seven days with no customer license purchases. This is not a background scheduler: on days with no market visit, no draw occurs.

The treasury debit, seller credit and purchased source/license snapshot are atomic. Retries cannot buy twice that day. The seller ledger explicitly says Trencod Support, these credits do not count toward TC badges, and no fake follower/customer account is created. Listing selection is not guaranteed. The frontend clearly displays whether the program is inactive or funded and enabled.

## Seven creator/discovery features (0.7)

1. **Play something new.** A random published game opens. The immediately previous random choice is excluded; signed-in creators are shown another creator’s game when available. Private drafts never enter discovery. This is uniform random discovery, not personalized ranking.
2. **Visual editor.** A bounded 800×450, single-level 2D platformer builder with drag-to-move player, platforms, coins, chasing enemies and goal. Coordinates/dimensions and movement speed, jump strength and gravity are adjustable. Undo, validated scene-JSON import/export, sandboxed preview, save/copy, publishing and generated-code viewing work. Saved scenes have revisions; stale tabs cannot overwrite newer scenes. Editing generated code does not update the visual scene. Regeneration asks before replacing externally changed code; save-a-copy preserves both. The visual editor is a platformer builder, not a general-purpose Scratch block language, 3D engine or animation state-machine editor. Pixel art can be inserted through the existing Code editor after purchase/creation; applying custom animated sprites to visual-editor objects is not yet supported.
3. **Weekly Game Jam.** UTC Monday-to-Monday windows, eight rotating themes. One newly created, published original game per creator per week; remixes and known purchased copies are rejected. Entries freeze the submitted code. Each account has one vote per category (Best Art, Most Fun, Most Creative); changing a vote moves it. Self-votes and late votes are rejected. Closed jam pages show highest-vote winners, including ties; no winner is declared for a category with zero votes. Unpublished games are hidden. Awards are on the jam results page, not extra profile badges, money or coins. There is no theme compliance judge or unique-human vote verification. Weekly windows are derived from server time; no external scheduled job is needed. Weeks first visited are persisted for the recent archive.
4. **Test my game.** Creators open/close a request on a published game with a focused question. Other players play it and submit three fields: enjoyed, got stuck, and suggestion. One report per player/game can be updated. Feedback is public, and the tested game update timestamp is recorded. The newest 100 requests/reports are displayed. This feature does not validate that a person actually played before commenting or assess quality automatically.
5. **Remix family tree.** Public ancestry and descendant links, with the selected game highlighted. Private/unavailable ancestors are omitted and explained. A connected view is bounded to 200 games. Credit relationships use the existing remix parent field; copied/reuploaded source cannot be recognized automatically.
6. **Playable shop previews.** Game-code previews play the frozen version stored in the listing rather than the seller’s latest game. Personal pixel art/animations can also be listed for demo TC: buyers can move/jump the preview sprite and change its backdrop/scale before purchase. Art purchases atomically transfer TC to the seller and retain an immutable licensed version. Owned animations and PNG sprite sheets can be downloaded; Use in my game sends the sprite markup to Code → Insert artwork. The art reuse license permits modification and game export, optional attribution, and prohibits standalone asset resale. Shared team art is not eligible for listing. Preview source is inspectable and is not DRM. Ownership confirmation does not automatically verify copyright or prevent copying.
7. **Creator devlogs.** Public progress posts, optional links to the author’s public game, all-creators and following feeds, and text replies. Creators can delete their posts and replies to them; reply authors can delete their own replies. Profiles link to creator-specific updates. Limits: ten posts per day, 15 replies per five minutes; latest 50 posts and 30 replies per post. No email/push notification is sent. No automatic moderation is provided; keep the beta to an invited testing group.

These features preserve the earlier TC/TP distinctions, achievements, themes, intro behavior, Studio rooms, sign-in and profiles. Real-money checkout and a live AI provider connection remain separate unfinished integrations; no external purchase, deployment or AI charge was made for this update.

## Everyday creator tools (0.8)
- Inbox is an authenticated in-app feed of the latest 100 existing follow,
  visible game comment, public remix, playtest and creator-sale events.
  Read status persists per account. It refreshes on navigation or Refresh;
  there are no push notifications, email sends or background polling.
  Deleted/unfollowed/hidden source events disappear. Existing events may
  appear unread on first use. No chat message contents enter this inbox.
- Private Play later lists persist per account, up to 500 games. Games made
  private disappear from the list and return if their owner republishes.
  This list does not grant access to private code or purchased licenses.
- Explore filters work on the loaded game list: title/creator/description,
  original/remix/visual type, newest/likes/title. No tags or personalized
  recommendation engine are implied. Newest uses last updated time.
- Code history retains 20 prior versions per project after changed saves.
  The pre-change title, description and HTML/CSS/JS are recorded in the same
  database transaction, including changes from the Visual editor.
  Private owner-only preview/download/restore; restore checks for concurrent
  project changes, records the current code and unpublishes the project.
  It does not award daily editing rewards. Identical saves do not add versions.
  Visual scene JSON is not versioned; restoring code can make the visual
  scene and code differ. The existing visual overwrite warning protects it.
  Art/shared-room file history is not included. Purchased license snapshots
  remain unchanged, and license restrictions stay attached to the project.
  Saved versions increase database size; use manage.py backup regularly.
