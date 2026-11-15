# Trencod 0.9 verification — 2026-11-15

## Executed checks
- 52 Python API/storage tests on SQLite: passed.
- 51 matching API/storage tests against PostgreSQL 16.2 in standalone mode: passed. The SQLite file-copy test is SQLite-only.
- 11 workspace JavaScript assertions and 2 sprite JavaScript assertions: passed.
- Python compilation and changed JavaScript syntax checks: passed.
- Restart check: saved an account, game and artwork; exited both app and standalone Postgres; opened a new app process with a new empty local data directory; login, projects, artwork and wallet balance survived.

Coverage includes case-insensitive login, ownership transfer, duplicate sale blocking,
insufficient-funds handling, purchase retries, version history, visual scenes, workspace
source preservation, private project exports and refusing Render startup without DATABASE_URL.

## Exact limits of this verification
This environment prohibits local sockets. PostgreSQL tests used a temporary stdin/stdout
transport to the real PostgreSQL standalone engine, while running the app's SQL adapter
and PostgreSQL triggers. That transport serializes requests: it verifies SQL/API behavior
but does not validate live network connections, pooled SSL, or real multi-connection lock
contention. SQLite concurrency tests did run with separate connections/threads.
The temporary transport is not included in the ZIP; production uses psycopg 3.

No connection to the user's Neon account was made. No live Render deployment, browser
interaction test, load test, or recovery of previously deleted data was performed.

## Reproduce
Local: python -m unittest discover -s tests -q
JS: node --test tests/workspace.test.cjs tests/sprites.test.cjs
PostgreSQL: set TRENCOD_TEST_DATABASE_URL to a DISPOSABLE test database, then run
python tests/run_postgres.py. This runner recreates public schema for every test.
NEVER point that test variable at your live Neon database.

## Operational design
DATABASE_URL selects PostgreSQL. Render refuses startup without it; connection failures
never fall back to SQLite. Local offline use without DATABASE_URL still uses SQLite.
PostgreSQL uses transaction-scoped advisory locks to serialize beta writes, preserving
multi-table sale/coin operations; this is a correctness-first design, not a high-throughput
scaling claim. Schema and triggers initialize transactionally.

Profile exports contain current owned games and personal art/code files plus visual scenes.
They exclude credentials, other creators' data, team files, wallet records and history;
they are source exports, not a complete account restore mechanism. Full owner backups
use pg_dump. Free services still have quotas and hosting sleep behavior.
