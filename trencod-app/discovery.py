"""Discovery, visual builder, jams, playtests, remix trees and creator devlogs."""
import json,secrets,time,math
from datetime import datetime,timezone,timedelta
from flask import g,request,jsonify
THEMES=['One-button Adventure','Underwater City','Tiny Planet','Lost in the Library','Friendly Monsters','A World Without Gravity','Two Worlds, One Hero','The Last Light']
def now():return time.time()
def schema(c):
 c.executescript('''
 CREATE TABLE IF NOT EXISTS visual_scenes(project_id TEXT PRIMARY KEY,body TEXT,revision INTEGER,code_updated REAL);
 CREATE TABLE IF NOT EXISTS jams(id TEXT PRIMARY KEY,theme TEXT,starts REAL,ends REAL);
 CREATE TABLE IF NOT EXISTS jam_entries(id TEXT PRIMARY KEY,jam_id TEXT,user_id TEXT,project_id TEXT,title TEXT,body TEXT,created REAL,UNIQUE(jam_id,user_id));
 CREATE TABLE IF NOT EXISTS jam_votes(jam_id TEXT,user_id TEXT,category TEXT,entry_id TEXT,PRIMARY KEY(jam_id,user_id,category));
 CREATE TABLE IF NOT EXISTS playtest_requests(project_id TEXT PRIMARY KEY,question TEXT,created REAL,open INTEGER DEFAULT 1);
 CREATE TABLE IF NOT EXISTS playtest_feedback(project_id TEXT,user_id TEXT,enjoyed TEXT,stuck TEXT,suggestion TEXT,version REAL,created REAL,PRIMARY KEY(project_id,user_id));
 CREATE TABLE IF NOT EXISTS devlogs(id TEXT PRIMARY KEY,user_id TEXT,title TEXT,body TEXT,project_id TEXT,created REAL);
 CREATE TABLE IF NOT EXISTS devlog_replies(id INTEGER PRIMARY KEY AUTOINCREMENT,post_id TEXT,user_id TEXT,body TEXT,created REAL);
 CREATE TABLE IF NOT EXISTS art_listings(id TEXT PRIMARY KEY,user_id TEXT,file_id TEXT UNIQUE,title TEXT,body TEXT,price INTEGER,active INTEGER DEFAULT 1);
 CREATE TABLE IF NOT EXISTS art_licenses(user_id TEXT,listing_id TEXT,title TEXT,body TEXT,price INTEGER,seller TEXT,created REAL,PRIMARY KEY(user_id,listing_id));
 ''')
def week(c):
 d=datetime.fromtimestamp(now(),timezone.utc);start=(d-timedelta(days=d.weekday())).replace(hour=0,minute=0,second=0,microsecond=0)
 key=start.strftime('%G-W%V');theme=THEMES[(int(start.timestamp())//604800)%len(THEMES)]
 c.execute('INSERT OR IGNORE INTO jams VALUES(?,?,?,?)',(key,theme,start.timestamp(),(start+timedelta(days=7)).timestamp()))
 return dict(c.execute('SELECT * FROM jams WHERE id=?',(key,)).fetchone())
def validate_scene(s):
 if not isinstance(s,dict):raise ValueError('Invalid scene.')
 out={}
 for k,lo,hi in [('speed',60,400),('jump',150,650),('gravity',300,1600)]:
  v=s.get(k)
  if type(v) not in (int,float) or not math.isfinite(v) or not lo<=v<=hi:raise ValueError(f'{k} must be {lo}–{hi}.')
  out[k]=v
 ents=s.get('objects');types={'player','platform','coin','enemy','goal'}
 if not isinstance(ents,list) or not 2<=len(ents)<=100:raise ValueError('Use 2–100 objects.')
 clean=[]
 for e in ents:
  if not isinstance(e,dict) or e.get('type') not in types:raise ValueError('Unknown object.')
  row={'type':e['type']}
  for k,hi in [('x',800),('y',450),('w',800),('h',450)]:
   v=e.get(k)
   if type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=hi or (k in ('w','h') and v<8):raise ValueError('Object coordinates are outside the scene.')
   row[k]=v
  if row['x']+row['w']>800 or row['y']+row['h']>450:raise ValueError('Keep objects inside the canvas.')
  clean.append(row)
 if sum(x['type']=='player' for x in clean)!=1 or sum(x['type']=='goal' for x in clean)!=1:raise ValueError('Keep exactly one player and one finish point.')
 out['objects']=clean;return out

def install(app,core):
 db,auth,fail,text,limited=[core[k] for k in ('db','auth','fail','text','limited')]
 def game(pid):
  p=core['project'](pid)
  return p if p and p['published'] else None
 def owned(c,pid,published=False):
  return c.execute('SELECT * FROM projects WHERE id=? AND owner=?'+(' AND published=1' if published else ''),(pid,g.user['id'])).fetchone()
 def generate(s):
  return {'html':'<h1 id="game-title">Pixel Quest</h1><p id="game-status">Collect all coins, avoid enemies, then reach the flag.</p><canvas id="game" width="800" height="450" tabindex="0" aria-label="Platform game"></canvas><div class="controls"><button id="left">◀</button><button id="jump">Jump</button><button id="right">▶</button><button id="reset">Restart</button></div><p>Arrow keys / A D to move · Space / W to jump</p>',
   'css':'body{margin:0;background:#0c1427;color:#ecf5ff;font:16px system-ui;text-align:center}h1{font-size:22px}canvas{display:block;max-width:100%;height:auto;margin:auto;background:#16243e;touch-action:none}.controls{display:flex;justify-content:center;gap:12px;margin:15px}button{background:#a99bff;color:#17112e;border:0;border-radius:12px;padding:14px 25px;font:inherit;touch-action:none}',
   'js':'const scene='+json.dumps(s)+';\n'+(core['PUBLIC']/'visual-runtime.js').read_text()}

 @app.get('/api/discover/random')
 def random_game():
  previous=request.args.get('exclude','')
  with db() as c:rows=c.execute('SELECT id,title,owner FROM projects WHERE published=1 AND id!=?',(previous,)).fetchall()
  if g.user:
   others=[r for r in rows if r['owner']!=g.user['id']];rows=others or rows
  if not rows:return fail('No other published game yet. Publish one or return to Explore.',404)
  return jsonify(project=dict(secrets.choice(rows)))

 @app.post('/api/visual/preview')
 def visual_preview():return jsonify(code=generate(validate_scene(g.data.get('scene'))))

 @app.get('/api/visual/<pid>')
 @auth
 def visual_get(pid):
  with db() as c:
   p=owned(c,pid);s=c.execute('SELECT * FROM visual_scenes WHERE project_id=?',(pid,)).fetchone()
   if not p or not s:return fail('Your visual project was not found.',404)
  return jsonify(scene=json.loads(s['body']),revision=s['revision'],project=dict(p),code_changed=any(p[k]!=generate(json.loads(s['body']))[k] for k in ('html','css','js')))

 @app.post('/api/visual/save')
 @auth
 def visual_save():
  s=validate_scene(g.data.get('scene'));title=text(g.data,'title',80,True).strip();pid=g.data.get('id');code=generate(s);ts=now()
  with db() as c:
   c.execute('BEGIN IMMEDIATE')
   if pid:
    p=owned(c,pid);old=c.execute('SELECT * FROM visual_scenes WHERE project_id=?',(pid,)).fetchone()
    if not p or not old:return fail('You can edit only your own visual project.',403)
    if g.data.get('revision')!=old['revision']:return fail('This scene changed in another tab. Download your scene backup, then reload.',409)
    if any(p[k]!=generate(json.loads(old['body']))[k] for k in ('html','css','js')) and g.data.get('overwrite') is not True:return fail('The code changed outside the visual editor. Confirm replacement or save a new copy.',409)
    rev=old['revision']+1
    c.execute('UPDATE projects SET title=?,html=?,css=?,js=?,updated=? WHERE id=?',(title,code['html'],code['css'],code['js'],ts,pid))
   else:
    if c.execute('SELECT COUNT(*) FROM projects WHERE owner=?',(g.user['id'],)).fetchone()[0]>=200:return fail('Project limit reached.')
    pid=secrets.token_hex(12);rev=1
    c.execute('INSERT INTO projects VALUES(?,?,?,?,?,?,?,?,?,?,?)',(pid,g.user['id'],title,'Built with the visual editor.',code['html'],code['css'],code['js'],0,None,ts,ts))
   c.execute('INSERT INTO visual_scenes VALUES(?,?,?,?) ON CONFLICT(project_id) DO UPDATE SET body=excluded.body,revision=excluded.revision,code_updated=excluded.code_updated',(pid,json.dumps(s),rev,ts))
   from community import activity
   if not g.data.get('id') or json.loads(old['body'])!=s:activity(c,g.user['id'],'code',code)
  return jsonify(id=pid,revision=rev,code=code)

 @app.get('/api/remix-tree/<pid>')
 def remix_tree(pid):
  if not game(pid):return fail('Public game not found.',404)
  with db() as c:
   rows=c.execute("SELECT p.id,p.parent,p.title,COALESCE(u.name,'Trencod Demos') creator FROM projects p LEFT JOIN users u ON p.owner=u.id WHERE p.published=1").fetchall()
  all_nodes={r['id']:dict(r) for r in rows};root=pid;seen=set()
  while all_nodes[root]['parent'] in all_nodes and root not in seen:
   seen.add(root);root=all_nodes[root]['parent']
  result=[];queue=[root];seen=set()
  while queue and len(result)<200:
   node=queue.pop(0)
   if node in seen:continue
   seen.add(node);result.append(all_nodes[node]);queue.extend(r['id'] for r in rows if r['parent']==node)
  return jsonify(nodes=result,root=root,hidden_parent=bool(all_nodes[root]['parent'] and all_nodes[root]['parent'] not in all_nodes),truncated=bool(queue))

 @app.get('/api/playtests')
 def tests_list():
  with db() as c:rows=c.execute('SELECT r.*,p.title,p.owner,u.name creator,(SELECT COUNT(*) FROM playtest_feedback f WHERE f.project_id=p.id) responses FROM playtest_requests r JOIN projects p ON p.id=r.project_id JOIN users u ON u.id=p.owner WHERE r.open=1 AND p.published=1 ORDER BY r.created DESC LIMIT 100').fetchall()
  return jsonify(requests=[dict(x) for x in rows])

 @app.post('/api/playtests')
 @auth
 def tests_request():
  pid=text(g.data,'id',30,True);question=text(g.data,'question',500,True);opened=g.data.get('open',True)
  if type(opened)!=bool:return fail('Invalid status.')
  with db() as c:
   if not owned(c,pid,True):return fail('Choose your own published game.',403)
   c.execute('INSERT INTO playtest_requests VALUES(?,?,?,?) ON CONFLICT(project_id) DO UPDATE SET question=excluded.question,open=excluded.open',(pid,question,now(),int(opened)))
  return jsonify(ok=True)

 @app.get('/api/playtests/<pid>')
 def tests_detail(pid):
  if not game(pid):return fail('Public game not found.',404)
  with db() as c:
   r=c.execute('SELECT * FROM playtest_requests WHERE project_id=?',(pid,)).fetchone()
   if not r:return fail('No playtest requested.',404)
   rows=c.execute('SELECT f.*,u.name FROM playtest_feedback f JOIN users u ON u.id=f.user_id WHERE project_id=? ORDER BY created DESC LIMIT 100',(pid,)).fetchall()
  return jsonify(request=dict(r),feedback=[dict(x) for x in rows])

 @app.post('/api/playtests/feedback')
 @auth
 def tests_feedback():
  pid=text(g.data,'id',30,True);p=game(pid)
  if not p:return fail('Public game not found.',404)
  if p['owner']==g.user['id']:return fail('Ask another player to test your game.')
  answers=[text(g.data,k,1000,True).strip() for k in ('enjoyed','stuck','suggestion')]
  if limited('playtest:'+g.user['id'],20,3600):return fail('Please wait before posting more feedback.',429)
  with db() as c:
   if not c.execute('SELECT 1 FROM playtest_requests WHERE project_id=? AND open=1',(pid,)).fetchone():return fail('This playtest is closed.',409)
   c.execute('INSERT INTO playtest_feedback VALUES(?,?,?,?,?,?,?) ON CONFLICT(project_id,user_id) DO UPDATE SET enjoyed=excluded.enjoyed,stuck=excluded.stuck,suggestion=excluded.suggestion,version=excluded.version,created=excluded.created',(pid,g.user['id'],*answers,p['updated'],now()))
  return jsonify(ok=True)

 @app.get('/api/jams')
 def jams_get():
  with db() as c:
   current=week(c);key=request.args.get('id',current['id']);j=c.execute('SELECT * FROM jams WHERE id=?',(key,)).fetchone()
   if not j:return fail('Jam not found.',404)
   rows=c.execute('SELECT e.id,e.project_id,e.user_id,e.title,e.created,u.name FROM jam_entries e JOIN users u ON u.id=e.user_id JOIN projects p ON p.id=e.project_id WHERE e.jam_id=? AND p.published=1',(key,)).fetchall()
   entries=[]
   for r in rows:
    e=dict(r);e['votes']={k:c.execute('SELECT COUNT(*) FROM jam_votes WHERE entry_id=? AND category=?',(r['id'],k)).fetchone()[0] for k in ('art','fun','creative')};entries.append(e)
   votes={r['category']:r['entry_id'] for r in c.execute('SELECT * FROM jam_votes WHERE jam_id=? AND user_id=?',(key,g.user['id']))} if g.user else {}
   recent=[dict(x) for x in c.execute('SELECT * FROM jams ORDER BY starts DESC LIMIT 12')]
  winners={k:[e['id'] for e in entries if e['votes'][k]==max([x['votes'][k] for x in entries],default=0) and e['votes'][k]>0] for k in ('art','fun','creative')}
  return jsonify(jam=dict(j),current=current['id'],closed=now()>=j['ends'],entries=entries,my_votes=votes,recent=recent,winners=winners)

 @app.post('/api/jams/enter')
 @auth
 def jam_enter():
  pid=text(g.data,'id',30,True)
  with db() as c:
   c.execute('BEGIN IMMEDIATE');j=week(c)
   if g.data.get('jam')!=j['id']:return fail('This jam has closed. Open the current week.',409)
   p=owned(c,pid,True)
   if not p or p['parent'] or c.execute('SELECT 1 FROM licensed_projects WHERE project_id=?',(pid,)).fetchone():return fail('Submit your own published original game.',403)
   if p['created']<j['starts']:return fail('Create a new game for this week’s theme.')
   if c.execute('SELECT 1 FROM jam_entries WHERE jam_id=? AND user_id=?',(j['id'],g.user['id'])).fetchone():return fail('You already entered this jam. Entries are frozen after submission.',409)
   eid=secrets.token_hex(12);body=json.dumps({k:p[k] for k in ('html','css','js')})
   c.execute('INSERT INTO jam_entries VALUES(?,?,?,?,?,?,?)',(eid,j['id'],g.user['id'],pid,p['title'],body,now()))
  return jsonify(id=eid)

 @app.get('/api/jams/entry/<eid>')
 def jam_play(eid):
  with db() as c:r=c.execute('SELECT e.* FROM jam_entries e JOIN projects p ON p.id=e.project_id WHERE e.id=? AND p.published=1',(eid,)).fetchone()
  if not r:return fail('Entry is unavailable.',404)
  return jsonify(title=r['title'],code=json.loads(r['body']))

 @app.post('/api/jams/vote')
 @auth
 def jam_vote():
  cat=g.data.get('category')
  if cat not in ('art','fun','creative'):return fail('Unknown award category.')
  with db() as c:
   c.execute('BEGIN IMMEDIATE');r=c.execute('SELECT e.*,j.ends FROM jam_entries e JOIN jams j ON j.id=e.jam_id JOIN projects p ON p.id=e.project_id WHERE e.id=? AND p.published=1',(g.data.get('id'),)).fetchone()
   if not r:return fail('Entry unavailable.',404)
   if now()>=r['ends']:return fail('Voting has ended.',409)
   if r['user_id']==g.user['id']:return fail('You cannot vote for your own entry.')
   c.execute('INSERT INTO jam_votes VALUES(?,?,?,?) ON CONFLICT(jam_id,user_id,category) DO UPDATE SET entry_id=excluded.entry_id',(r['jam_id'],g.user['id'],cat,r['id']))
  return jsonify(ok=True)

 @app.get('/api/devlogs')
 def devlogs_get():
  uid=request.args.get('creator');feed=request.args.get('feed');where='1=1';args=[]
  if uid:where='d.user_id=?';args=[uid]
  elif feed=='following':
   if not g.user:return fail('Sign in to see followed creators.',401)
   where='d.user_id IN (SELECT target_id FROM follows WHERE user_id=?)';args=[g.user['id']]
  with db() as c:
   posts=[dict(x) for x in c.execute('SELECT d.*,u.name FROM devlogs d JOIN users u ON u.id=d.user_id WHERE '+where+' ORDER BY d.created DESC LIMIT 50',args)]
   for p in posts:
    if p['project_id'] and not c.execute('SELECT 1 FROM projects WHERE id=? AND published=1',(p['project_id'],)).fetchone():p['project_id']=None
    p['replies']=[dict(x) for x in c.execute('SELECT r.*,u.name FROM devlog_replies r JOIN users u ON r.user_id=u.id WHERE r.post_id=? ORDER BY r.created DESC LIMIT 30',(p['id'],))]
  return jsonify(posts=posts)

 @app.post('/api/devlogs')
 @auth
 def devlogs_post():
  title=text(g.data,'title',100,True).strip();body=text(g.data,'body',3000,True).strip();pid=g.data.get('project_id') or None
  if limited('devlog:'+g.user['id'],10,86400):return fail('Maximum ten updates per day.',429)
  with db() as c:
   if pid and not owned(c,pid,True):return fail('Link one of your own published games.',403)
   did=secrets.token_hex(12);c.execute('INSERT INTO devlogs VALUES(?,?,?,?,?,?)',(did,g.user['id'],title,body,pid,now()))
  return jsonify(id=did)

 @app.post('/api/devlogs/reply')
 @auth
 def devlogs_reply():
  body=text(g.data,'body',1000,True).strip();did=text(g.data,'id',30,True)
  if limited('devlog-reply:'+g.user['id'],15,300):return fail('Please wait before posting more replies.',429)
  with db() as c:
   if not c.execute('SELECT 1 FROM devlogs WHERE id=?',(did,)).fetchone():return fail('Post not found.',404)
   c.execute('INSERT INTO devlog_replies(post_id,user_id,body,created) VALUES(?,?,?,?)',(did,g.user['id'],body,now()))
  return jsonify(ok=True)

 @app.post('/api/devlogs/delete')
 @auth
 def devlogs_delete():
  with db() as c:
   if g.data.get('reply') is not None:
    r=c.execute('SELECT r.user_id,d.user_id owner FROM devlog_replies r JOIN devlogs d ON r.post_id=d.id WHERE r.id=?',(g.data['reply'],)).fetchone()
    if not r or g.user['id'] not in (r['user_id'],r['owner']):return fail('You cannot remove this reply.',403)
    c.execute('DELETE FROM devlog_replies WHERE id=?',(g.data['reply'],))
   else:
    if not c.execute('SELECT 1 FROM devlogs WHERE id=? AND user_id=?',(g.data.get('id'),g.user['id'])).fetchone():return fail('You cannot remove this post.',403)
    c.execute('DELETE FROM devlog_replies WHERE post_id=?',(g.data['id'],));c.execute('DELETE FROM devlogs WHERE id=?',(g.data['id'],))
  return jsonify(ok=True)

 @app.get('/api/market/preview/<lid>')
 def market_preview(lid):
  with db() as c:r=c.execute('SELECT title,body FROM listings WHERE id=? AND active=1',(lid,)).fetchone()
  if not r:return fail('Listing unavailable.',404)
  return jsonify(title=r['title'],code=json.loads(r['body']))

 @app.get('/api/art-market')
 def art_market():
  uid=g.user['id'] if g.user else ''
  with db() as c:
   rows=c.execute('SELECT a.*,u.name seller,EXISTS(SELECT 1 FROM art_licenses x WHERE x.listing_id=a.id AND x.user_id=?) owned FROM art_listings a JOIN users u ON u.id=a.user_id WHERE a.active=1',(uid,)).fetchall()
   bought=c.execute('SELECT * FROM art_licenses WHERE user_id=?',(uid,)).fetchall()
  return jsonify(items=[dict(r,body=json.loads(r['body'])) for r in rows],owned=[dict(r,body=json.loads(r['body'])) for r in bought])

 @app.post('/api/art-market/list')
 @auth
 def art_list():
  price=g.data.get('price')
  if type(price)!=int or not 1<=price<=1000000:return fail('Choose a whole-number price from 1 to 1,000,000 TC.')
  if g.data.get('rights') is not True:return fail('Confirm you own the rights to this artwork.')
  with db() as c:
   r=c.execute("SELECT * FROM studio_files WHERE id=? AND owner=? AND room_id IS NULL AND kind='art'",(g.data.get('id'),g.user['id'])).fetchone()
   if not r:return fail('Choose your own personal artwork. Team artwork cannot be sold here.',403)
   c.execute('INSERT INTO art_listings VALUES(?,?,?,?,?,?,1) ON CONFLICT(file_id) DO UPDATE SET title=excluded.title,body=excluded.body,price=excluded.price,active=1',(secrets.token_hex(12),g.user['id'],r['id'],r['name'],r['body'],price))
  return jsonify(ok=True)

 @app.post('/api/art-market/unlist')
 @auth
 def art_unlist():
  with db() as c:c.execute('UPDATE art_listings SET active=0 WHERE id=? AND user_id=?',(g.data.get('id'),g.user['id']))
  return jsonify(ok=True)

 @app.post('/api/art-market/buy')
 @auth
 def art_buy():
  with db() as c:
   c.execute('BEGIN IMMEDIATE');r=c.execute('SELECT a.*,u.name seller FROM art_listings a JOIN users u ON u.id=a.user_id WHERE a.id=? AND active=1',(g.data.get('id'),)).fetchone()
   if not r:return fail('Listing unavailable.',404)
   if r['user_id']==g.user['id']:return fail('This is your own artwork.')
   if c.execute('SELECT 1 FROM art_licenses WHERE user_id=? AND listing_id=?',(g.user['id'],r['id'])).fetchone():return jsonify(ok=True)
   for uid in (g.user['id'],r['user_id']):core['wallet_init'](c,uid)
   if not c.execute('UPDATE wallets SET balance=balance-? WHERE user_id=? AND balance>=?',(r['price'],g.user['id'],r['price'])).rowcount:return fail('Not enough Trencoins.',409)
   c.execute('UPDATE wallets SET balance=balance+? WHERE user_id=?',(r['price'],r['user_id']))
   c.execute('INSERT INTO art_licenses VALUES(?,?,?,?,?,?,?)',(g.user['id'],r['id'],r['title'],r['body'],r['price'],r['seller'],now()))
   for uid,amount,reason in [(g.user['id'],-r['price'],'Art license: '),(r['user_id'],r['price'],'Sale: ')]:
    c.execute('INSERT INTO ledger(user_id,amount,reason,event_key,created) VALUES(?,?,?,?,?)',(uid,amount,reason+r['title'],'art:'+r['id']+':'+g.user['id'],now()))
  return jsonify(ok=True)
