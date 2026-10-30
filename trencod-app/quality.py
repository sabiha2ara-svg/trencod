"""Private play queue, saved code history and an in-app activity inbox."""
import json,time,math
from flask import g,jsonify

def schema(c):
 c.executescript('''
 CREATE TABLE IF NOT EXISTS play_later(user_id TEXT,project_id TEXT,created REAL,PRIMARY KEY(user_id,project_id));
 CREATE TABLE IF NOT EXISTS inbox_seen(user_id TEXT PRIMARY KEY,seen REAL);
 CREATE TABLE IF NOT EXISTS project_versions(id INTEGER PRIMARY KEY AUTOINCREMENT,project_id TEXT,body TEXT,saved REAL);
 CREATE INDEX IF NOT EXISTS versions_project ON project_versions(project_id,id);
 CREATE TRIGGER IF NOT EXISTS keep_project_version BEFORE UPDATE ON projects
 WHEN OLD.owner!='trencod-team' AND (OLD.title!=NEW.title OR OLD.description!=NEW.description OR OLD.html!=NEW.html OR OLD.css!=NEW.css OR OLD.js!=NEW.js)
 BEGIN
 INSERT INTO project_versions(project_id,body,saved) VALUES(OLD.id,json_object('title',OLD.title,'description',OLD.description,'html',OLD.html,'css',OLD.css,'js',OLD.js),OLD.updated);
 DELETE FROM project_versions WHERE project_id=OLD.id AND id NOT IN (SELECT id FROM project_versions WHERE project_id=OLD.id ORDER BY id DESC LIMIT 20);
 END;
 ''')

def install(app,core):
 db,auth,fail,text=[core[k] for k in ('db','auth','fail','text')]
 def owned(c,pid):return c.execute('SELECT * FROM projects WHERE id=? AND owner=?',(pid,g.user['id'])).fetchone()

 @app.get('/api/play-later')
 @auth
 def queue():
  with db() as c:
   rows=c.execute(core['SELECT']+' JOIN play_later q ON q.project_id=p.id WHERE q.user_id=? AND p.published=1 ORDER BY q.created DESC',(g.user['id'],)).fetchall()
   favorites={r[0] for r in c.execute('SELECT project_id FROM favorites WHERE user_id=?',(g.user['id'],))}
  return jsonify(projects=[{**{k:r[k] for k in r.keys() if k not in ('html','css','js')},'favorite':r['id'] in favorites} for r in rows])

 @app.post('/api/play-later')
 @auth
 def queue_save():
  pid=text(g.data,'id',30,True);enabled=g.data.get('saved')
  if type(enabled)!=bool:return fail('Choose save or remove.')
  with db() as c:
   if enabled:
    if not c.execute('SELECT 1 FROM projects WHERE id=? AND published=1',(pid,)).fetchone():return fail('Public game not found.',404)
    if c.execute('SELECT COUNT(*) FROM play_later WHERE user_id=?',(g.user['id'],)).fetchone()[0]>=500:return fail('Your list is full. Remove a game first.')
    c.execute('INSERT OR IGNORE INTO play_later VALUES(?,?,?)',(g.user['id'],pid,time.time()))
   else:c.execute('DELETE FROM play_later WHERE user_id=? AND project_id=?',(g.user['id'],pid))
  return jsonify(saved=enabled)

 @app.get('/api/history/<pid>')
 @auth
 def history_list(pid):
  with db() as c:
   p=owned(c,pid)
   if not p:return fail('Your project was not found.',404)
   rows=c.execute('SELECT id,body,saved FROM project_versions WHERE project_id=? ORDER BY id DESC',(pid,)).fetchall()
  return jsonify(title=p['title'],updated=p['updated'],versions=[{'id':r['id'],'title':json.loads(r['body'])['title'],'saved':r['saved']} for r in rows])

 @app.get('/api/history/<pid>/<int:vid>')
 @auth
 def history_detail(pid,vid):
  with db() as c:
   if not owned(c,pid):return fail('Your project was not found.',404)
   r=c.execute('SELECT body FROM project_versions WHERE project_id=? AND id=?',(pid,vid)).fetchone()
  if not r:return fail('Saved version no longer available.',404)
  body=json.loads(r['body']);return jsonify(title=body['title'],code=body)

 @app.post('/api/history/restore')
 @auth
 def history_restore():
  pid=text(g.data,'id',30,True)
  if type(g.data.get('version'))!=int:return fail('Choose a saved version.')
  with db() as c:
   c.execute('BEGIN IMMEDIATE');p=owned(c,pid)
   if not p:return fail('Your project was not found.',404)
   if g.data.get('updated')!=p['updated']:return fail('Your project changed in another tab. Reload history before restoring.',409)
   r=c.execute('SELECT body FROM project_versions WHERE project_id=? AND id=?',(pid,g.data['version'])).fetchone()
   if not r:return fail('Saved version no longer available.',404)
   body=json.loads(r['body'])
   c.execute('UPDATE projects SET title=?,description=?,html=?,css=?,js=?,published=0,updated=? WHERE id=?',(*(body[k] for k in ('title','description','html','css','js')),time.time(),pid))
  return jsonify(ok=True)

 @app.get('/api/inbox')
 @auth
 def inbox():
  uid=g.user['id'];until=time.time();events=[]
  with db() as c:
   seen=c.execute('SELECT seen FROM inbox_seen WHERE user_id=?',(uid,)).fetchone();seen=seen[0] if seen else 0
   queries=[
    ("SELECT u.name||' followed you' message,'profile/'||u.id link,f.created FROM follows f JOIN users u ON u.id=f.user_id WHERE f.target_id=?",(uid,)),
    ("SELECT u.name||' commented on '||p.title message,'play/'||p.id link,c.created FROM comments c JOIN users u ON u.id=c.user_id JOIN projects p ON p.id=c.project_id WHERE p.owner=? AND c.user_id!=? AND c.hidden=0 AND p.published=1",(uid,uid)),
    ("SELECT u.name||' remixed '||p.title message,'play/'||r.id link,r.created FROM projects r JOIN projects p ON p.id=r.parent JOIN users u ON u.id=r.owner WHERE p.owner=? AND r.owner!=? AND r.published=1",(uid,uid)),
    ("SELECT u.name||' tested '||p.title message,'playtests/'||p.id link,f.created FROM playtest_feedback f JOIN projects p ON p.id=f.project_id JOIN users u ON u.id=f.user_id WHERE p.owner=? AND p.published=1",(uid,)),
    ("SELECT reason||' · +'||amount||' TC' message,'wallet' link,created FROM ledger WHERE user_id=? AND amount>0 AND reason LIKE 'Sale: %'",(uid,))]
   for sql,args in queries:
    events.extend(dict(r) for r in c.execute('SELECT * FROM ('+sql+') WHERE created<=? ORDER BY created DESC LIMIT 100',(*args,until)))
  events=sorted(events,key=lambda r:r['created'],reverse=True)[:100]
  return jsonify(events=[dict(e,unread=e['created']>seen) for e in events],unread=sum(e['created']>seen for e in events),until=until)

 @app.post('/api/inbox/read')
 @auth
 def inbox_read():
  until=g.data.get('until')
  if type(until) not in (int,float) or not math.isfinite(until) or until<0 or until>time.time():return fail('Reload the inbox before marking it read.')
  with db() as c:c.execute('INSERT INTO inbox_seen VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET seen=MAX(seen,excluded.seen)',(g.user['id'],until))
  return jsonify(ok=True)
