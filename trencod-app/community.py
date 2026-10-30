"""Permanent achievements, private progress, follows, comments, budgeted platform support."""
import hashlib,json,secrets,time
from datetime import datetime,timezone,date,timedelta
from flask import g,jsonify,request

BADGES={
 'tc':[(50,'First Fifty'),(100,'Century'),(200,'Growing Creator'),(500,'Rising Star'),(1000,'One Thousand'),(2000,'Creator Elite'),(5000,'Five Thousand Club')],
 'streak':[(3,'Finding Your Rhythm'),(7,'One Week'),(14,'Two Weeks'),(30,'Creative Month'),(100,'Hundred Days')],
 'games':[(1,'First Release'),(5,'Game Maker'),(10,'Game Builder'),(25,'Game Collection'),(50,'Game Studio')],
 'friends':[(6,'First Circle'),(10,'Friendly Creator'),(40,'Big Circle'),(80,'Community Builder'),(150,'Connected Creator')]
}
def today():return datetime.now(timezone.utc).date()
def schema(c):
 c.executescript('''
 CREATE TABLE IF NOT EXISTS achievements(user_id TEXT,key TEXT,earned REAL,PRIMARY KEY(user_id,key));
 CREATE TABLE IF NOT EXISTS activity_days(user_id TEXT,day TEXT,PRIMARY KEY(user_id,day));
 CREATE TABLE IF NOT EXISTS tp_rewards(user_id TEXT,day TEXT,amount INTEGER,reason TEXT,PRIMARY KEY(user_id,day));
 CREATE TABLE IF NOT EXISTS credited_games(user_id TEXT,project_id TEXT,code_hash TEXT,PRIMARY KEY(user_id,project_id),UNIQUE(user_id,code_hash));
 CREATE TABLE IF NOT EXISTS follows(user_id TEXT,target_id TEXT,created REAL,PRIMARY KEY(user_id,target_id),CHECK(user_id!=target_id));
 CREATE TABLE IF NOT EXISTS comments(id INTEGER PRIMARY KEY AUTOINCREMENT,project_id TEXT,user_id TEXT,body TEXT,created REAL,hidden INTEGER DEFAULT 0);
 CREATE TABLE IF NOT EXISTS comment_reports(user_id TEXT,comment_id INTEGER,reason TEXT,created REAL,PRIMARY KEY(user_id,comment_id));
 CREATE TABLE IF NOT EXISTS support_budget(id INTEGER PRIMARY KEY CHECK(id=1),balance INTEGER CHECK(balance>=0),enabled INTEGER DEFAULT 0);
 INSERT OR IGNORE INTO support_budget VALUES(1,0,0);
 CREATE TABLE IF NOT EXISTS support_purchases(id TEXT PRIMARY KEY,day TEXT UNIQUE,listing_id TEXT UNIQUE,seller_id TEXT,title TEXT,price INTEGER,body TEXT,credit INTEGER,created REAL);
 CREATE TABLE IF NOT EXISTS support_funding(id INTEGER PRIMARY KEY,amount INTEGER,created REAL);
 CREATE INDEX IF NOT EXISTS follow_targets ON follows(target_id);
 CREATE INDEX IF NOT EXISTS comments_project ON comments(project_id,id);
 ''')

def friends(c,uid):return c.execute('SELECT COUNT(*) FROM follows a JOIN follows b ON a.user_id=b.target_id AND a.target_id=b.user_id WHERE a.user_id=?',(uid,)).fetchone()[0]
def streaks(c,uid):
 days=[date.fromisoformat(x[0]) for x in c.execute('SELECT day FROM activity_days WHERE user_id=? ORDER BY day',(uid,))];best=run=0;previous=None
 for d in days:
  run=run+1 if previous and d==previous+timedelta(days=1) else 1
  best=max(best,run);previous=d
 current=run if previous in (today(),today()-timedelta(days=1)) else 0
 return current,best,days

def activity(c,uid,kind,body,room_id=None):
 if kind=='code' and not any(str(body.get(k,'')).strip() for k in ('html','css','js')):return
 if kind=='art' and not any(any(frame) for frame in body['frames']):return
 day=today().isoformat();c.execute('INSERT OR IGNORE INTO activity_days VALUES(?,?)',(uid,day))
 # A creator with six or more mutual friends can earn one daily collaboration bonus.
 if friends(c,uid)>=6:
  c.execute('INSERT OR IGNORE INTO tp_rewards VALUES(?,?,50,?)',(uid,day,'Daily creator bonus'))

def credit_game(c,uid,pid):
 p=c.execute('SELECT * FROM projects WHERE id=? AND owner=? AND published=1',(pid,uid)).fetchone()
 if not p or p['parent'] or c.execute('SELECT 1 FROM licensed_projects WHERE project_id=?',(pid,)).fetchone():return
 parts=[' '.join(p[k].split()) for k in ('html','css','js')]
 if not any(parts):return
 fingerprint=hashlib.sha256(json.dumps(parts).encode()).hexdigest()
 c.execute('INSERT OR IGNORE INTO credited_games VALUES(?,?,?)',(uid,pid,fingerprint))

def sync(c,uid):
 eligible=peak=0
 for r in c.execute('SELECT amount,reason FROM ledger WHERE user_id=? ORDER BY id',(uid,)):
  if r['amount']>0 and r['reason'].startswith('Sale: '):eligible+=r['amount']
  elif r['amount']<0:eligible=max(0,eligible+r['amount'])
  peak=max(peak,eligible)
 for r in c.execute('SELECT id FROM projects WHERE owner=? AND published=1',(uid,)).fetchall():credit_game(c,uid,r['id'])
 current,best,days=streaks(c,uid)
 counts={'tc':peak,'streak':best,'games':c.execute('SELECT COUNT(*) FROM credited_games WHERE user_id=?',(uid,)).fetchone()[0],'friends':friends(c,uid)}
 for category,defs in BADGES.items():
  for amount,name in defs:
   if counts[category]>=amount:c.execute('INSERT OR IGNORE INTO achievements VALUES(?,?,?)',(uid,f'{category}:{amount}',time.time()))
 earned={r['key']:r['earned'] for r in c.execute('SELECT * FROM achievements WHERE user_id=?',(uid,))}
 badges=[dict(key=f'{cat}:{amount}',category=cat,threshold=amount,name=name,earned=earned.get(f'{cat}:{amount}'),progress=min(counts[cat],amount)) for cat,defs in BADGES.items() for amount,name in defs]
 return dict(badges=badges,counts=counts,eligible_balance=eligible,streak=current,best_streak=best,activity_days=[d.isoformat() for d in days],tp=c.execute('SELECT COALESCE(SUM(amount),0) FROM tp_rewards WHERE user_id=?',(uid,)).fetchone()[0],reward_today=bool(c.execute('SELECT 1 FROM tp_rewards WHERE user_id=? AND day=?',(uid,today().isoformat())).fetchone()))

def support_draw(c):
 """Called on market visits; maximum one funded support purchase per UTC day."""
 budget=c.execute('SELECT * FROM support_budget WHERE id=1').fetchone();day=today().isoformat()
 if not budget['enabled'] or budget['balance']<=0 or c.execute('SELECT 1 FROM support_purchases WHERE day=?',(day,)).fetchone():return None
 rows=c.execute('''SELECT l.* FROM listings l JOIN projects p ON p.id=l.project_id JOIN wallets w ON w.user_id=l.owner
 WHERE l.active=1 AND p.published=1 AND p.updated<=? AND l.price BETWEEN 1 AND ?
 AND NOT EXISTS(SELECT 1 FROM licenses x WHERE x.listing_id=l.id)
 AND NOT EXISTS(SELECT 1 FROM support_purchases x WHERE x.listing_id=l.id OR (x.seller_id=l.owner AND x.created>?))''',(time.time()-7*86400,min(100,budget['balance']),time.time()-30*86400)).fetchall()
 if not rows:return None
 p=secrets.choice(rows);sid=secrets.token_hex(12)
 c.execute('UPDATE support_budget SET balance=balance-? WHERE id=1',(p['price'],))
 c.execute('UPDATE wallets SET balance=balance+? WHERE user_id=?',(p['price'],p['owner']))
 c.execute('INSERT INTO ledger(user_id,amount,reason,event_key,created) VALUES(?,?,?,?,?)',(p['owner'],p['price'],'Trencod Support: '+p['title'],'support:'+sid,time.time()))
 c.execute('INSERT INTO support_purchases VALUES(?,?,?,?,?,?,?,?,?)',(sid,day,p['id'],p['owner'],p['title'],p['price'],p['body'],p['credit'],time.time()))
 return sid

def install(app,core):
 db,auth,fail,text,limited=[core[k] for k in ('db','auth','fail','text','limited')]
 @app.get('/api/profile')
 @app.get('/api/profile/<uid>')
 def profile(uid=None):
  if uid is None:
   if not g.user:return fail('Sign in to open your profile.',401)
   uid=g.user['id']
  with db() as c:
   c.execute('BEGIN IMMEDIATE');u=c.execute('SELECT id,name FROM users WHERE id=?',(uid,)).fetchone()
   if not u:return fail('Creator not found.',404)
   data=sync(c,uid);mine=bool(g.user and uid==g.user['id'])
   following=[dict(x) for x in c.execute('SELECT u.id,u.name FROM follows f JOIN users u ON f.target_id=u.id WHERE f.user_id=? ORDER BY f.created DESC',(uid,))]
   followers=[dict(x) for x in c.execute('SELECT u.id,u.name FROM follows f JOIN users u ON f.user_id=u.id WHERE f.target_id=? ORDER BY f.created DESC',(uid,))]
   projects=[dict(x) for x in c.execute('SELECT id,title,description FROM projects WHERE owner=? AND published=1 ORDER BY updated DESC',(uid,))]
   public=dict(user=dict(u),mine=mine,badges=[b for b in data['badges'] if mine or b['earned']],friends=data['counts']['friends'],following=following,followers=followers,projects=projects,is_following=bool(g.user and any(x['id']==g.user['id'] for x in followers)))
   if mine:
    balance=c.execute('SELECT balance FROM wallets WHERE user_id=?',(uid,)).fetchone()
    public.update(data,balance=balance[0] if balance else 0,today=today().isoformat())
  return jsonify(public)

 @app.post('/api/follow')
 @auth
 def follow():
  uid=text(g.data,'id',30,True);enabled=g.data.get('follow')
  if type(enabled)!=bool:return fail('Choose follow or unfollow.')
  if uid==g.user['id']:return fail('You cannot follow yourself.')
  if limited('follow:'+g.user['id'],60,3600):return fail('Please wait before following more creators.',429)
  with db() as c:
   c.execute('BEGIN IMMEDIATE')
   if not c.execute('SELECT 1 FROM users WHERE id=?',(uid,)).fetchone():return fail('Creator not found.',404)
   if enabled:c.execute('INSERT OR IGNORE INTO follows VALUES(?,?,?)',(g.user['id'],uid,time.time()))
   else:c.execute('DELETE FROM follows WHERE user_id=? AND target_id=?',(g.user['id'],uid))
   sync(c,g.user['id']);sync(c,uid)
  return jsonify(ok=True)

 @app.get('/api/creators')
 def creators():
  q=request.args.get('q','').strip()[:24]
  with db() as c:rows=c.execute('SELECT id,name FROM users WHERE name LIKE ? ORDER BY name LIMIT 40',('%'+q+'%',)).fetchall()
  return jsonify(creators=[dict(x) for x in rows])

 @app.get('/api/comments/<pid>')
 def comments(pid):
  p=core['project'](pid)
  if not p or not p['published']:return fail('Public game not found.',404)
  with db() as c:rows=c.execute('SELECT c.id,c.user_id,c.body,c.created,u.name FROM comments c JOIN users u ON u.id=c.user_id WHERE project_id=? AND hidden=0 ORDER BY c.id DESC LIMIT 100',(pid,)).fetchall()
  return jsonify(comments=[dict(r,can_delete=bool(g.user and g.user['id'] in (r['user_id'],p['owner']))) for r in rows])

 @app.post('/api/comments')
 @auth
 def comment():
  pid=text(g.data,'project_id',30,True);body=text(g.data,'body',1000,True).strip();p=core['project'](pid)
  if not p or not p['published']:return fail('Public game not found.',404)
  if limited('comment:'+g.user['id'],10,300):return fail('Please slow down. Maximum ten comments per five minutes.',429)
  with db() as c:
   if c.execute('SELECT 1 FROM comments WHERE user_id=? AND project_id=? AND body=? AND created>?',(g.user['id'],pid,body,time.time()-60)).fetchone():return fail('You just posted that comment.',409)
   c.execute('INSERT INTO comments(project_id,user_id,body,created) VALUES(?,?,?,?)',(pid,g.user['id'],body,time.time()))
  return jsonify(ok=True)

 @app.post('/api/comments/delete')
 @auth
 def delete_comment():
  with db() as c:
   r=c.execute('SELECT c.user_id,p.owner FROM comments c JOIN projects p ON c.project_id=p.id WHERE c.id=?',(g.data.get('id'),)).fetchone()
   if not r or g.user['id'] not in (r['user_id'],r['owner']):return fail('Only the author or game creator can remove this comment.',403)
   c.execute('UPDATE comments SET hidden=1 WHERE id=?',(g.data.get('id'),))
  return jsonify(ok=True)

 @app.post('/api/comments/report')
 @auth
 def report_comment():
  reason=text(g.data,'reason',500,True)
  if limited('comment-report:'+g.user['id'],10,3600):return fail('Please wait before reporting more comments.',429)
  with db() as c:
   r=c.execute('SELECT project_id FROM comments WHERE id=? AND hidden=0',(g.data.get('id'),)).fetchone()
   if not r or not core['project'](r['project_id']):return fail('Comment not found.',404)
   c.execute('INSERT OR IGNORE INTO comment_reports VALUES(?,?,?,?)',(g.user['id'],g.data.get('id'),reason,time.time()))
  return jsonify(ok=True)

 @app.get('/api/support')
 def support_status():
  with db() as c:
   b=c.execute('SELECT enabled,balance FROM support_budget WHERE id=1').fetchone()
   rows=c.execute('SELECT title,price,created FROM support_purchases ORDER BY created DESC LIMIT 10').fetchall()
  return jsonify(enabled=bool(b['enabled']),funded=b['balance']>0,purchases=[dict(x) for x in rows])
