"""Owner-only local/server-shell tools. Never expose this file as an HTTP route."""
import sys, getpass, secrets
from pathlib import Path
from server import init, db, password_hash, DATA
init()
command=sys.argv[1] if len(sys.argv)>1 else 'help'
if command=='reports':
    with db() as c:
        for r in c.execute('SELECT * FROM reports WHERE resolved=0 ORDER BY created DESC'):print(dict(r))
elif command=='hide' and len(sys.argv)==3:
    with db() as c:
        c.execute('UPDATE projects SET published=0 WHERE id=?',(sys.argv[2],))
        c.execute('UPDATE reports SET resolved=1 WHERE project_id=?',(sys.argv[2],))
    print('Project hidden; associated reports marked resolved.')
elif command=='reset-password' and len(sys.argv)==3:
    password=getpass.getpass('New password (8+ characters): ')
    if len(password)<8:raise SystemExit('Password too short.')
    salt=secrets.token_hex(16)
    with db() as c:
        row=c.execute('SELECT id FROM users WHERE name=?',(sys.argv[2],)).fetchone()
        if not row:raise SystemExit('Username not found.')
        c.execute('UPDATE users SET salt=?,password=? WHERE id=?',(salt,password_hash(password,salt),row['id']))
        c.execute('DELETE FROM sessions WHERE user_id=?',(row['id'],))
    print('Password updated; previous sessions signed out.')
elif command=='support-fund' and len(sys.argv)==3:
    import time
    amount=int(sys.argv[2])
    if not 1<=amount<=1000000:raise SystemExit('Use 1 to 1,000,000 test TC.')
    with db() as c:
        c.execute('UPDATE support_budget SET balance=balance+? WHERE id=1',(amount,))
        c.execute('INSERT INTO support_funding(amount,created) VALUES(?,?)',(amount,time.time()))
    print('Test support budget funded. This is platform-issued TC, not real revenue.')
elif command in ('support-on','support-off'):
    with db() as c:c.execute('UPDATE support_budget SET enabled=? WHERE id=1',(int(command=='support-on'),))
    print('Support program',command)
elif command=='comment-reports':
    with db() as c:
        for r in c.execute('SELECT r.*,c.body FROM comment_reports r JOIN comments c ON c.id=r.comment_id WHERE c.hidden=0'):print(dict(r))
elif command=='hide-comment' and len(sys.argv)==3:
    with db() as c:c.execute('UPDATE comments SET hidden=1 WHERE id=?',(int(sys.argv[2]),))
    print('Comment hidden.')
elif command=='backup':
    import sqlite3,time
    target=DATA/('backup-'+time.strftime('%Y%m%d-%H%M%S')+'.sqlite3')
    with db() as source,sqlite3.connect(target) as destination:source.backup(destination)
    print('Backup saved to',target)
else:print('Usage: python manage.py reports | hide PROJECT_ID | reset-password USERNAME | backup | support-fund AMOUNT | support-on | support-off | comment-reports | hide-comment ID')
