# Trencod 0.16.0 — Support and reliability

## Owner setup
1. Deploy this full trencod-app folder. Database initialization adds the feedback table without deleting existing records.
2. Sign in to your owner account. Open `/api/me` on your own website and copy your **user.id** (not username or session cookie).
3. Set Render environment variable `TRENCOD_SUPPORT_ADMINS` to that ID. Multiple authorized support IDs may be comma-separated. Do not put arbitrary usernames here.
4. Redeploy/restart. Visit `/help` while signed in. The inbox shows up to 200 most recently updated tickets. Other users see only their own latest 100 reports.
5. Write a reply and select open/investigating/resolved. Replies are stored in the database; no email is sent. This is a single current reply, not a conversation thread. Monitor the inbox manually.

The footer opens Help/Contact in a new tab so the current editor stays open. Users need an account to send private reports (five per hour). Login failures can prevent sending: configure a separate public contact address yourself if needed. No invented email address is included. Security reports must stay private. Reports include only fields entered by the user, account ID and timestamps; no automatic console log or screenshot collection.

## Reliability changes
- A shared-file save response cannot set the ID/revision of another file opened while the save was running.
- Out-of-order shared-file loads are ignored; typing in the current editor cancels applying a pending load.
- Market UI sends the displayed price and credit requirement for a transactional check. A mismatch returns 409 without charging. Older clients which omit these fields retain the existing API behavior.
- Successful game purchases return the transferred project ID. Existing transactional single-buyer transfer and access restrictions remain in effect.

## Public docs
`/help` includes tutorials, ownership terms, community rules, changelog and a source-based backend/security description. It does not claim an audit, deployment verification, guaranteed backups or full sandbox network/CPU isolation. Shared code is revisioned, not a real-time collaborative editor.

## Owner operational checklist
Use HTTPS with correct TRENCOD_PUBLIC_URL/Render external URL. Keep DATABASE_URL and API keys in server environment variables only. Maintain database backups and test restores separately. Check `/healthz` reports postgres on Render. SQLite local files are not a hosted backup. Download personal project exports regularly. Confirm Studio save/reopen and a test sale before inviting more users. Do not run untrusted Python directly on the web server.
