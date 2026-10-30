"""Trencod beta: Flask + Waitress, persistent SQLite, demo-only coins."""
import hashlib, hmac, json, os, secrets, sqlite3, time, webbrowser, threading
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, g
from werkzeug.exceptions import HTTPException

ROOT=Path(__file__).resolve().parent
PUBLIC=ROOT/'public'
DATA=Path(os.environ.get('TRENCOD_DATA_DIR',str(ROOT/'data')))
DATA.mkdir(parents=True,exist_ok=True)
DB=DATA/'trencod.sqlite3'
PORT=int(os.environ.get('PORT',os.environ.get('TRENCOD_PORT','8765')))
HOST=os.environ.get('TRENCOD_HOST','0.0.0.0' if os.environ.get('RENDER') else '127.0.0.1')
PUBLIC_URL=os.environ.get('TRENCOD_PUBLIC_URL',os.environ.get('RENDER_EXTERNAL_URL','')).rstrip('/')
SECURE=PUBLIC_URL.startswith('https://')
ORIGINS={f'http://127.0.0.1:{PORT}',f'http://localhost:{PORT}'}
if PUBLIC_URL:ORIGINS.add(PUBLIC_URL)
HOSTS={urlparse(x).netloc for x in ORIGINS}
app=Flask(__name__,static_folder=None)
app.config['MAX_CONTENT_LENGTH']=600000

def db():
    c=sqlite3.connect(DB,timeout=20);c.row_factory=sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON');return c

def fail(message,status=400):return jsonify(error=message),status

def text(data,key,maxlen,required=False):
    v=data.get(key,'')
    if not isinstance(v,str):raise ValueError(f'{key} must be text.')
    if len(v)>maxlen or (required and not v.strip()):raise ValueError(f'Please enter {key} (up to {maxlen} characters).')
    return v

def init():
    if DB.exists() and not (DATA/'before-0.8.sqlite3').exists():
        with sqlite3.connect(DB) as source, sqlite3.connect(DATA/'before-0.8.sqlite3') as backup: source.backup(backup)
    with db() as c:
        c.execute('PRAGMA journal_mode=WAL')
        c.executescript('''
        CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,name TEXT UNIQUE COLLATE NOCASE,salt TEXT,password TEXT);
        CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user_id TEXT,expires REAL);
        CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,owner TEXT,title TEXT,description TEXT,html TEXT,css TEXT,js TEXT,published INTEGER DEFAULT 0,parent TEXT,created REAL,updated REAL);
        CREATE TABLE IF NOT EXISTS wallets(user_id TEXT PRIMARY KEY,balance INTEGER NOT NULL CHECK(balance>=0));
        CREATE TABLE IF NOT EXISTS ledger(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id TEXT,amount INTEGER,reason TEXT,event_key TEXT,created REAL,UNIQUE(user_id,event_key));
        CREATE TABLE IF NOT EXISTS purchases(user_id TEXT,item_id TEXT,created REAL,PRIMARY KEY(user_id,item_id));
        CREATE TABLE IF NOT EXISTS favorites(user_id TEXT,project_id TEXT,PRIMARY KEY(user_id,project_id));
        CREATE TABLE IF NOT EXISTS limits(key TEXT PRIMARY KEY,count INTEGER,expires REAL);
        CREATE TABLE IF NOT EXISTS reports(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id TEXT,project_id TEXT,reason TEXT,created REAL,resolved INTEGER DEFAULT 0);
        CREATE INDEX IF NOT EXISTS sessions_expiry ON sessions(expires);
        CREATE INDEX IF NOT EXISTS published_projects ON projects(published,updated);
        ''')
        from studio_features import schema
        schema(c)
        from community import schema as community_schema
        community_schema(c)
        from discovery import schema as discovery_schema
        discovery_schema(c)
        from quality import schema as quality_schema
        quality_schema(c)
        seeds=json.loads((ROOT/'games.json').read_text(encoding='utf-8'))
        for p in seeds:
            # Update only built-in games, never a user's project or remix.
            c.execute('INSERT INTO projects VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET html=excluded.html,css=excluded.css,js=excluded.js,description=excluded.description WHERE projects.owner=\'trencod-team\'',
                      (p['id'],'trencod-team',p['title'],p['description'],p['html'],p['css'],p['js'],1,None,time.time(),time.time()))

def password_hash(password,salt):
    return 'pbkdf2$600000$'+hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),600000).hex()

def verify_password(password,row):
    saved=row['password']
    if saved.startswith('pbkdf2$'):
        _,rounds,hashed=saved.split('$')
        return hmac.compare_digest(hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(row['salt']),int(rounds)).hex(),hashed)
    # Keep accounts from the first Trencod ZIP working.
    if not hasattr(hashlib,'scrypt'):raise ValueError('This older account needs a Python build with scrypt. Your data has not been changed.')
    return hmac.compare_digest(hashlib.scrypt(password.encode(),salt=bytes.fromhex(row['salt']),n=16384,r=8,p=1).hex(),saved)

def wallet_init(c,uid):
    if c.execute('INSERT OR IGNORE INTO wallets VALUES(?,100)',(uid,)).rowcount:
        c.execute('INSERT INTO ledger(user_id,amount,reason,event_key,created) VALUES(?,?,?,?,?)',(uid,100,'Welcome bonus','welcome',time.time()))

def current_user():
    token=request.cookies.get('trencod_session','')
    if not token:return None
    with db() as c:
        r=c.execute('SELECT u.id,u.name FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=? AND s.expires>?',(hashlib.sha256(token.encode()).hexdigest(),time.time())).fetchone()
        return dict(r) if r else None

def auth(fn):
    @wraps(fn)
    def call(*args,**kwargs):
        if not g.user:return fail('Please sign in or create a free account first.',401)
        return fn(*args,**kwargs)
    return call

def limited(key,maximum,seconds):
    with db() as c:
        c.execute('BEGIN IMMEDIATE')
        c.execute('DELETE FROM limits WHERE expires<?',(time.time(),))
        r=c.execute('SELECT count FROM limits WHERE key=?',(key,)).fetchone()
        if r and r['count']>=maximum:return True
        c.execute('INSERT INTO limits VALUES(?,1,?) ON CONFLICT(key) DO UPDATE SET count=count+1',(key,time.time()+seconds))
    return False

@app.before_request
def before():
    if request.host not in HOSTS:return fail('Wrong server address. Open '+(PUBLIC_URL or f'http://127.0.0.1:{PORT}'),403)
    if request.method=='POST':
        if request.headers.get('Origin') and request.headers['Origin'] not in ORIGINS:return fail('Please open Trencod using its main website address.',403)
        if request.mimetype!='application/json':return fail('Please send JSON.',415)
        data=request.get_json()
        if not isinstance(data,dict):return fail('Invalid request.')
        g.data=data
        who=hashlib.sha256((request.remote_addr or 'unknown').encode()).hexdigest()
        if request.path in ('/api/login','/api/register') and limited(who+request.path,30,300):return fail('Too many attempts. Please wait five minutes.',429)
    g.user=current_user()

@app.after_request
def headers(response):
    response.headers['Cache-Control']='no-store'
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='same-origin'
    response.headers['Content-Security-Policy']="frame-ancestors 'none'"
    if SECURE:response.headers['Strict-Transport-Security']='max-age=31536000'
    return response

@app.errorhandler(ValueError)
def invalid(e):return fail(str(e))
@app.errorhandler(HTTPException)
def http_error(e):return fail(e.description,e.code)
@app.errorhandler(Exception)
def unexpected(e):
    app.logger.exception('Request failed')
    return fail('The server could not finish that action. Your existing projects are safe. Please try again.',500)

@app.get('/healthz')
def health():return jsonify(ok=True,version='0.8')
@app.get('/api/me')
def me():return jsonify(user=g.user)
@app.post('/api/register')
@app.post('/api/login')
def sign_in():
    data=g.data;name=text(data,'name',24,True).strip();password=text(data,'password',128,True)
    if request.path.endswith('register'):
        if len(name)<3 or not all(ch.isascii() and (ch.isalnum() or ch in '_-.') for ch in name):return fail('Username: 3–24 letters, numbers, dots, hyphens or underscores. No spaces or @. Try trencod_gamecreator. Don’t enter your real name.')
        if len(password)<8:return fail('Choose a password with at least 8 characters.')
        uid=secrets.token_hex(12);salt=secrets.token_hex(16);hashed=password_hash(password,salt)
        try:
            with db() as c:
                c.execute('INSERT INTO users VALUES(?,?,?,?)',(uid,name,salt,hashed));wallet_init(c,uid)
        except sqlite3.IntegrityError:return fail('That username already exists. Choose Sign in, or use a different name.',409)
    else:
        with db() as c:row=c.execute('SELECT * FROM users WHERE name=?',(name,)).fetchone()
        if not row or not verify_password(password,row):return fail('Username or password is incorrect. New here? Choose Create account.',401)
        uid,name=row['id'],row['name']
        if not row['password'].startswith('pbkdf2$'):
            with db() as c:c.execute('UPDATE users SET password=? WHERE id=?',(password_hash(password,row['salt']),uid))
    token=secrets.token_urlsafe(32)
    with db() as c:
        c.execute('DELETE FROM sessions WHERE expires<?',(time.time(),))
        c.execute('INSERT INTO sessions VALUES(?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),uid,time.time()+604800));wallet_init(c,uid)
    response=jsonify(user={'id':uid,'name':name})
    response.set_cookie('trencod_session',token,max_age=604800,httponly=True,samesite='Lax',secure=SECURE,path='/')
    return response

@app.post('/api/logout')
def logout():
    token=request.cookies.get('trencod_session','')
    with db() as c:c.execute('DELETE FROM sessions WHERE token=?',(hashlib.sha256(token.encode()).hexdigest(),))
    response=jsonify(ok=True);response.delete_cookie('trencod_session',path='/',secure=SECURE,samesite='Lax');return response

SELECT="SELECT p.*,EXISTS(SELECT 1 FROM visual_scenes WHERE project_id=p.id) AS visual,(SELECT id FROM listings WHERE project_id=p.id AND active=1) AS source_license,EXISTS(SELECT 1 FROM licensed_projects WHERE project_id=p.id) AS licensed_copy,COALESCE(u.name,'Trencod Studio') AS creator,(SELECT COUNT(*) FROM favorites f WHERE f.project_id=p.id) AS likes FROM projects p LEFT JOIN users u ON p.owner=u.id"
def project(pid):
    with db() as c:r=c.execute(SELECT+' WHERE p.id=?',(pid,)).fetchone()
    if not r or (not r['published'] and (not g.user or g.user['id']!=r['owner'])):return None
    d=dict(r);d['published']=bool(d['published']);return d

@app.get('/api/projects')
@app.get('/api/mine')
@app.get('/api/favorites')
def list_projects():
    if request.path!='/api/projects' and not g.user:return fail('Please sign in first.',401)
    where,args=('p.published=1',())
    if request.path.endswith('mine'):where,args=('p.owner=?',(g.user['id'],))
    if request.path.endswith('favorites'):where,args=('p.published=1 AND p.id IN (SELECT project_id FROM favorites WHERE user_id=?)',(g.user['id'],))
    with db() as c:
        rows=c.execute(SELECT+' WHERE '+where+' ORDER BY p.updated DESC',args).fetchall()
        favorites={r[0] for r in c.execute('SELECT project_id FROM favorites WHERE user_id=?',(g.user['id'],))} if g.user else set()
    result=[]
    for row in rows:
        d=dict(row)
        for field in ('html','css','js'):d.pop(field)
        d['published']=bool(d['published']);d['favorite']=d['id'] in favorites;result.append(d)
    return jsonify(projects=result)

@app.get('/api/project/<pid>')
def get_project(pid):
    p=project(pid)
    if not p:return fail('Project not found or private.',404)
    if g.user:
        with db() as c:p['favorite']=bool(c.execute('SELECT 1 FROM favorites WHERE user_id=? AND project_id=?',(g.user['id'],pid)).fetchone())
    return jsonify(project=p)

@app.post('/api/save')
@auth
def save():
    d=g.data;title=text(d,'title',80,True).strip();description=text(d,'description',300).strip()
    html,css,js=(text(d,k,150000) for k in ('html','css','js'));pid=d.get('id');now=time.time()
    with db() as c:
        c.execute('BEGIN IMMEDIATE')
        changed=True
        if pid:
            row=c.execute('SELECT owner,html,css,js FROM projects WHERE id=?',(pid,)).fetchone()
            if not row or row['owner']!=g.user['id']:return fail('You can edit only your own project. Use Remix to create a copy.',403)
            changed=any(row[k]!=v for k,v in [('html',html),('css',css),('js',js)])
            c.execute('UPDATE projects SET title=?,description=?,html=?,css=?,js=?,updated=? WHERE id=?',(title,description,html,css,js,now,pid))
        else:
            if c.execute('SELECT COUNT(*) FROM projects WHERE owner=?',(g.user['id'],)).fetchone()[0]>=200:return fail('Your account has reached the 200-project beta limit.')
            pid=secrets.token_hex(12)
            c.execute('INSERT INTO projects VALUES(?,?,?,?,?,?,?,?,?,?,?)',(pid,g.user['id'],title,description,html,css,js,0,None,now,now))
        if changed:
            from community import activity
            activity(c,g.user['id'],'code',dict(html=html,css=css,js=js))
    return jsonify(id=pid)

@app.post('/api/publish')
@app.post('/api/unpublish')
@auth
def publish():
    pid=g.data.get('id')
    with db() as c:
        row=c.execute('SELECT owner FROM projects WHERE id=?',(pid,)).fetchone()
        if not row or row['owner']!=g.user['id']:return fail('This is not your project.',403)
        c.execute('UPDATE projects SET published=?,updated=? WHERE id=?',(int(request.path.endswith('/publish')),time.time(),pid))
        if request.path.endswith('/publish'):
            from community import credit_game
            credit_game(c,g.user['id'],pid)
    return jsonify(ok=True)

@app.post('/api/remix')
@auth
def remix():
    with db() as c:
        paid=c.execute('SELECT id FROM listings WHERE project_id=? AND active=1',(g.data.get('id'),)).fetchone()
        licensed=c.execute('SELECT 1 FROM licensed_projects WHERE project_id=?',(g.data.get('id'),)).fetchone()
        if paid or licensed:return fail('This creator sells a source license. Open Creator Market to buy or import your owned copy.',403)
        row=c.execute('SELECT * FROM projects WHERE id=? AND published=1',(g.data.get('id'),)).fetchone()
        if not row:return fail('Published project not found.',404)
        if c.execute('SELECT COUNT(*) FROM projects WHERE owner=?',(g.user['id'],)).fetchone()[0]>=200:return fail('Your account has reached the 200-project beta limit.')
        pid=secrets.token_hex(12);now=time.time()
        c.execute('INSERT INTO projects VALUES(?,?,?,?,?,?,?,?,?,?,?)',(pid,g.user['id'],('Remix of '+row['title'])[:80],row['description'],row['html'],row['css'],row['js'],0,row['id'],now,now))
    return jsonify(id=pid)

@app.post('/api/favorite')
@auth
def favorite():
    pid=g.data.get('id');p=project(pid)
    if not p or not p['published']:return fail('Published project not found.',404)
    with db() as c:
        c.execute('BEGIN IMMEDIATE')
        old=c.execute('SELECT 1 FROM favorites WHERE user_id=? AND project_id=?',(g.user['id'],pid)).fetchone()
        if old:c.execute('DELETE FROM favorites WHERE user_id=? AND project_id=?',(g.user['id'],pid))
        else:c.execute('INSERT INTO favorites VALUES(?,?)',(g.user['id'],pid))
        count=c.execute('SELECT COUNT(*) FROM favorites WHERE project_id=?',(pid,)).fetchone()[0]
    return jsonify(favorite=not bool(old),likes=count)

@app.post('/api/report')
@auth
def report():
    pid=g.data.get('id');p=project(pid)
    if not p:return fail('Project not found.',404)
    reason=text(g.data,'reason',500,True).strip()
    if limited('report:'+g.user['id'],10,3600):return fail('Please wait before sending more reports.',429)
    with db() as c:c.execute('INSERT INTO reports(user_id,project_id,reason,created) VALUES(?,?,?,?)',(g.user['id'],pid,reason,time.time()))
    return jsonify(ok=True)

@app.get('/api/wallet')
@auth
def wallet():
    with db() as c:
        wallet_init(c,g.user['id']);balance=c.execute('SELECT balance FROM wallets WHERE user_id=?',(g.user['id'],)).fetchone()[0]
        ledger=[dict(r) for r in c.execute('SELECT amount,reason,created FROM ledger WHERE user_id=? ORDER BY id DESC LIMIT 30',(g.user['id'],))]
        today=datetime.now(timezone.utc).strftime('%Y-%m-%d')
        claimed=bool(c.execute('SELECT 1 FROM ledger WHERE user_id=? AND event_key=?',(g.user['id'],'daily:'+today)).fetchone())
    return jsonify(balance=balance,ledger=ledger,claimed=claimed,demo=True)

@app.post('/api/daily')
@auth
def daily():return fail('Daily giveaways have ended. Use the one-time milestone bonuses in Wallet.',410)

def products():return json.loads((ROOT/'shop.json').read_text(encoding='utf-8'))
@app.get('/api/shop')
def shop():
    with db() as c:owned={r[0] for r in c.execute('SELECT item_id FROM purchases WHERE user_id=?',(g.user['id'],))} if g.user else set()
    return jsonify(items=[{k:v for k,v in dict(p,owned=p['id'] in owned).items() if k not in ('source',)} for p in products()])

@app.post('/api/buy')
@auth
def buy():
    p=next((x for x in products() if x['id']==g.data.get('id')),None)
    if not p:return fail('Item not found.',404)
    with db() as c:
        c.execute('BEGIN IMMEDIATE');wallet_init(c,g.user['id'])
        if c.execute('SELECT 1 FROM purchases WHERE user_id=? AND item_id=?',(g.user['id'],p['id'])).fetchone():return jsonify(ok=True,already_owned=True)
        changed=c.execute('UPDATE wallets SET balance=balance-? WHERE user_id=? AND balance>=?',(p['price'],g.user['id'],p['price'])).rowcount
        if not changed:return fail('Not enough Trencoins. Check your wallet and milestone bonuses.',409)
        c.execute('INSERT INTO purchases VALUES(?,?,?)',(g.user['id'],p['id'],time.time()))
        c.execute('INSERT INTO ledger(user_id,amount,reason,event_key,created) VALUES(?,?,?,?,?)',(g.user['id'],-p['price'],'Bought '+p['name'],'purchase:'+p['id'],time.time()))
    return jsonify(ok=True)

@app.get('/api/item/<item_id>')
@auth
def item(item_id):
    with db() as c:owned=c.execute('SELECT 1 FROM purchases WHERE user_id=? AND item_id=?',(g.user['id'],item_id)).fetchone()
    if not owned:return fail('Buy this item with demo Trencoins first.',403)
    p=next((x for x in products() if x['id']==item_id),None)
    if not p:return fail('Item not found.',404)
    return jsonify(item=p)

@app.get('/')
@app.get('/index.html')
def index():return send_from_directory(PUBLIC,'index.html')
@app.get('/<filename>')
def static_file(filename):
    if filename not in {'app.js','style.css','intro.css','intro.js','trencod-icon.png','theme.js','theme.css','creator.js','creator.css','profile.js','profile.css','adventures.js','adventures.css','visual-runtime.js','quality.js'}:return fail('Page not found.',404)
    return send_from_directory(PUBLIC,filename)

from studio_features import install
install(app,globals())
from community import install as community_install
community_install(app,globals())
from discovery import install as discovery_install
discovery_install(app,globals())
from quality import install as quality_install
quality_install(app,globals())

if __name__=='__main__':
    import sys
    from waitress.server import create_server
    init()
    address=PUBLIC_URL or f'http://127.0.0.1:{PORT}'
    try:http=create_server(app,host=HOST,port=PORT,threads=8,max_request_body_size=600000)
    except OSError:
        print(f'Port {PORT} is already in use. Close the older Trencod terminal window, then start this version again.')
        raise SystemExit(1)
    print(f'\nTrencod beta: {address}\nKeep this window open. Ctrl+C stops the server.\n')
    if '--no-browser' not in sys.argv and not PUBLIC_URL:threading.Timer(1,lambda:webbrowser.open(address)).start()
    http.run()
