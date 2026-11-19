# Trencod 0.11 validation

- Existing 59 Python tests passed on SQLite; 3 new AI coaching tests passed separately.
- 58 Python tests passed on PostgreSQL 16.2 using real psycopg TCP connections
  against a disposable local database. Only the SQLite file-copy test is excluded.
  Includes concurrent exclusive purchases and concurrent one-time badge claims.
- Existing 11 workspace assertions and 2 pixel sprite assertions passed under Node.
- Vector checks: all 50 starters validated by backend; all 50 SVG exports and
  canvas renderer paths checked. Canvas-rendered sprite contact sheet inspected.
- Temporary DOM harness using LinkeDOM exercised 50-card gallery, selection,
  layer selection, duplicate, undo/redo, save/reopen, SVG export, search and maximize.
- Python and modified JavaScript syntax checked.

New integration coverage includes vector ownership, stale-revision rejection,
backup inclusion, invalid coordinate/color rejection, generated game embedding,
removed coin badges, cheaper bot prices, badge eligibility, idempotency, competing
claims, restart/schema initialization, refollow and republish cases.

Limitations: the full browser could not launch in this environment because its
Unix socket operation was blocked. DOM tests do not verify actual pointer events,
responsive layout or accessibility in a real browser. No test used your Neon
credentials or changed your live Render site. Local PostgreSQL testing does not
verify Neon SSL/network conditions. AI provider calls remain mocked in tests.

After deployment: check /healthz; draw/drag a shape; save and reopen a vector;
apply it in Visual editor and play; claim a qualifying badge twice (only one payment);
check existing account/projects; refresh and verify wallet and art persist.

Run: python -m unittest discover -s tests -v
Run: node --test tests/*.cjs
For PostgreSQL: tests/run_postgres.py requires a disposable test database and
DELETES its public schema for each test. NEVER use production DATABASE_URL there.

0.11 checks:
- Python file save/load round trip and HTML script misuse rejection passed.
- Python iframe source escaping, worker dispatch, selected file paths and Stop passed
  with mocked runtime in a Node VM. This does not verify the CDN/WASM in a browser.
- Workspace DOM: Python creation, unique names, icons, Run dispatch, maximize/restore,
  visible Save, same-project navigation passed with LinkeDOM.
- Normal/Smart budgets and full-HTML response rejection tested.
- Full browser layout and actual browser Python execution remain unverified here.

## 0.12.0 My projects + music validation
- Full Python integration suite: 67 SQLite tests passed; 66 passed on a disposable real PostgreSQL database (one SQLite-specific copy test excluded).
- New coverage: audio upload/auth/type/size/quota checks, public playback bytes and HTTP Range, persistence after schema initialization, account-backup audio inclusion, art + scene music round trips, publish access, invalid music settings, creation classifications, private and team membership access.
- Node tests: music source-tree compile/reopen, replacement/removal without duplicate audio, malicious settings rejection; existing workspace, sprites, vector and Python tests passed.
- DOM tests (LinkeDOM with mocked canvas/audio): draw, duplicate frame, attach music, Play/Pause calls, save animation, My projects thumbnail and filter, reopen animation, export playback markup, quick pixel drawer account save. Existing vector editor and code/Python editor DOM tests passed.
- Native browser layout, actual speaker output and real-browser codec decoding could not be exercised here. Audio formats/codecs must be supported by the user's browser. Audio headers are checked, but malformed audio may still fail playback and display an error.
- No live Render deploy or production Neon modification was performed.
