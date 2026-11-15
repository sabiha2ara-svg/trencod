# Trencod exclusive sales update

This update replaces NEW game-code and personal-artwork marketplace purchases with a one-buyer ownership transfer. Demo TC only; no real-money processing.

## What changes
- One database transaction performs the debit, seller credit, purchase record, ownership transfer and listing removal. Concurrent buyers cannot both purchase; retries by the winning buyer do not charge twice.
- The existing game ID moves to the buyer's My Projects as a PRIVATE draft containing the listing's advertised code snapshot. The seller cannot save, publish, unpublish, restore history or relist that project. The buyer can edit and publish it. Open in editor opens that same project rather than creating extra copies.
- Personal artwork moves to the buyer's editable Studio files. Seller access is removed and the art listing closes.
- Exact copies of sold code/art are blocked from saving under another account and from being sold again. Existing identical seller project copies are unpublished in the sale transaction. This is NOT a plagiarism detector: edited/reformatted copies, earlier downloads, embedded art and external publication cannot be comprehensively blocked. The existing game Report feature remains available.
- Existing creator-credit conditions remain recorded; required credit is included in transferred code and snapshot downloads. Reselling purchased projects/art is disabled in this version.
- Automatic platform-support purchases are paused. Old demo sprite pack purchases are unchanged.

## Existing shops and buyers
On first upgrade, ALL old game/art listings are paused so sellers can review the new exclusive terms. Unsold originals can be relisted. Previously licensed games/art cannot be retroactively sold as exclusive; all existing licenses, buyers, balances and sale history are retained. A game already bought by two people stays licensed to both. This update does not silently revoke either purchase or pick an owner for it.

## Before uploading to GitHub / redeploying
The uploaded ZIP contains source code, not the LIVE Render database. A code ZIP is not a backup of accounts, balances or published user games.
1. Confirm where the live database is stored and make an off-server backup before redeploying. The app uses TRENCOD_DATA_DIR/trencod.sqlite3. If data is on Render's temporary filesystem, a redeploy may remove it. A startup backup cannot rescue data that vanished during deployment.
2. Keep your existing repository and all existing database files. Do NOT delete the repository, service or data folder.
3. Extract this ZIP locally. It contains a trencod-app folder at the top level. In GitHub repository ROOT (the page showing trencod-app), choose Add file > Upload files and drag that extracted trencod-app folder. GitHub should show paths such as trencod-app/server.py, NOT trencod-app/trencod-app/server.py.
4. Commit the update. Render auto-deploys if enabled. Root Directory stays trencod-app. Build stays pip install -r requirements.txt. Start stays python server.py --no-browser.
5. With persistent data intact, startup makes before-exclusive-sales.sqlite3 once and adds the new tables/triggers. No account/project deletion migration is performed.
6. Test with two test accounts and a NEW original project. List for 25 TC; buy from the second account. Confirm the project moved, listing disappeared, seller is denied edit/publish, buyer can edit, and a third account cannot buy it.
7. Google verification tag in public/index.html is preserved.

## Validation
38 automated tests passed, including separate game and artwork buyer races, same-buyer retries, insufficient balances, ownership permissions, duplicate handling, legacy-license preservation and migration idempotency. Existing account, Studio, history and community tests pass. Changed JavaScript passes Node syntax checks. Browser visual testing was not completed because the browser executable was unavailable; live Render deployment was not performed.
