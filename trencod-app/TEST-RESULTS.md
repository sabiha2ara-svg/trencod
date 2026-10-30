# Trencod 0.8 validation — 30 October 2026

31 Python unittest groups pass. Coverage includes existing authentication and scrypt migration, project isolation/publishing/remixing, origin and host checks, old asset purchases, concurrent purchase idempotency, milestones and duplicate-claim prevention, private rooms and member removal, shared-file revision conflicts, pixel data validation/persistence, source-license seller transfers and immutable purchase snapshots, purchased-copy resale restriction, unavailable AI purchase without charge, configured AI unlock and mocked Responses API output, and database import without overwriting existing data.

Actual Chromium 134 browser flow passed with two independent accounts:
- Registration and login cookies; new nickname privacy copy.
- Create a room, join by invite, send and receive a team message.
- Save shared game code and load it from the second account.
- Draw pixels, duplicate a frame, change it, save a team animation and play it.
- Insert the generated PNG-based animation into an empty code project.
- Save and publish a game; list its source license.
- Buy from the second account, debit the buyer and import the licensed version with required attribution.
- Confirm disabled unconfigured bots and absence of daily giveaways.
- View mobile layout at 390px and switch light/dark mode without horizontal overflow.

Desktop Studio, art editor, and mobile art editor screenshots were visually inspected. JavaScript syntax and Python compilation pass. Distribution excludes user databases, environments and private configuration.

Limitations: AI provider calls were mocked, not live. Payment checkout is intentionally unavailable. The Windows BAT launchers and tkinter picker were not run on Windows, but the underlying SQLite import function was tested. Hosting was not deployed. This is a small beta, not a completed public marketplace or Discord-scale collaboration service. See OWNER-SETUP.md.


0.6 validation:
- Permanent 50–5,000 eligible-TC badges survive spending and restart; gifts, support credits and bonus TP cannot unlock them.
- Mutual follows, exact friend thresholds, repeat-follow idempotency, and private/public profile field separation.
- UTC streak rollover and gap reset; best streak retained; concurrent saves award only 50 TP per user/day; unchanged saves award nothing.
- Repeated publishing and duplicate source copies do not multiply game credits.
- Comment visibility, text escaping, delete permissions, duplicate-post prevention and report storage.
- Support program defaults off; budget is debited once, seller credited once, customer licenses are not fabricated, support is excluded from badges.
- Actual Chromium two-account UI test passed: header opens Profile, Sign out only inside own profile, mutual follow/unfollow, group badge, daily TP after code save, publishing, comments containing HTML rendered as text, public creator profiles, badge category filtering, mobile no horizontal overflow, dark/light theme and successful signout.
- Desktop and mobile profile screenshots visually inspected.

Studio Support is implemented but not enabled or funded in the deliverable. No real purchases or external messages were sent; all flow tests used disposable local databases.


0.7 validation — all seven features:
- Random discovery excludes private games and the previous random selection.
- Visual scene schema validation, permissions, stale revision rejection, external-code conflict detection, and persistence across initialization.
- Public-only remix ancestry, with private ancestor titles omitted.
- Creator-owned playtest requests, author exclusion from self-feedback, report updates and closed-request rejection.
- Jam entry snapshots, one entry per user/week, no self-votes, idempotent category voting, deadline rejection and closed-week winners.
- Following-only devlog feed, replies and deletion permissions.
- Frozen game-listing preview; art listing ownership; concurrent art purchases charge exactly once, credit the seller and preserve the purchased snapshot after unlisting.

Actual Chromium end-to-end UI flow passed for two independent accounts:
- Drag a player in the visual scene, play with keyboard, collect a coin, save and publish.
- Random game discovery, another random game without repeating the previous one.
- Enter the weekly jam, vote from a second account, play its frozen submitted version.
- Open a playtest request and submit structured player feedback.
- Create a remix and inspect the two-node family tree.
- Post a devlog, see it in the follower feed and reply.
- Preview a saved source listing, list pixel animation, try moving its preview character, buy from the second account and prepare it for insertion into Code.
- Mobile 390px layout without horizontal overflow; light/dark mode.

No uncaught browser page errors in this flow. Desktop builder, Jam and art-shop screens plus mobile builder were visually inspected. Source syntax checks passed. Windows launcher/picker, actual hosting and live AI/payment integrations remain untested here as previously documented.

0.8 validation:
- Five added unittest groups cover private play queues, hidden games,
  idempotent saves, owner-only history, stale restore conflicts, reversible
  restore, twenty-version retention, migration persistence, guest denial,
  inbox isolation and a read cutoff that does not swallow later events.
- Headless Chromium with two separate account sessions passed: description
  search and type filters, A-Z sort control, private Play later save/list,
  inbox mark-read, code edit/save, history sandbox preview, JSON download,
  restore as private draft and preservation of the replaced code.
- All seven 0.7 browser feature flows passed again against 0.8.
- Mobile 390px layout has no horizontal overflow; light/dark screenshots
  inspected. No uncaught JavaScript errors in these browser flows.
- Windows launcher, external deployment, live AI and payments were not tested.
