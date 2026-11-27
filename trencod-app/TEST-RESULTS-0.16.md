# 0.16.0 verification

77 Python unittest tests passed against temporary SQLite databases. Includes support report privacy, admin-only reply, rate limits, restart persistence, changed-price rejection without charge, and existing competing-buyer/exclusive ownership tests.

21 Node tests passed, none skipped. Includes a DOM regression for switching shared files while a save is pending; the previous response cannot overwrite the new file ID.

This is local automated validation, not a penetration test. No live Neon/PostgreSQL run, Render deployment check, or full real-browser/mobile visual inspection was performed for this update. Existing database adapter and hosted configuration require deployment verification.
