TRENCOD 0.9 — NEON DATA UPDATE

Saaiq: pehle NEON-SETUP.txt padho.

Is ZIP mein:
- Neon PostgreSQL support: accounts, games, artwork, coins and sales in external DB.
- Render par DATABASE_URL na ho to startup stops; temporary SQLite fallback nahi.
- Profile > Download my projects: your current games and personal artwork backup.
- Exclusive sale fix, sprite library, pixel drawer, extra files/folders,
  maximize editor, history, and existing AI panel retained.

IMPORTANT: ZIP download karne se live website update nahi hoti.
Render mein DATABASE_URL set karna aur GitHub code update karna dono zaroori hain.
Purana deleted data is ZIP se wapas nahi aayega. Existing SQLite data automatically
Neon mein transfer nahi hota. Agar abhi live/local data bacha ho, backup lo before moving.
Neon account connection and real deployment have not been tested here.

Local PC: START-TRENCOD.bat (uses local SQLite unless DATABASE_URL is set).
Render/Neon: follow NEON-SETUP.txt.
Developer verification: TEST-RESULTS.md.
