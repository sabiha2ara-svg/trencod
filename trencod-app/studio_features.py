"""Creator rooms, revisioned shared files, marketplace and optional AI adapter."""
import json, secrets, time, os, re, urllib.request, urllib.error
from datetime import datetime, timezone
from flask import g, jsonify, request

def schema(c):
    c.executescript('''
    CREATE TABLE IF NOT EXISTS milestones(user_id TEXT,day INTEGER,PRIMARY KEY(user_id,day));
    CREATE TABLE IF NOT EXISTS rooms(id TEXT PRIMARY KEY,owner TEXT,name TEXT,invite TEXT UNIQUE,created REAL);
    CREATE TABLE IF NOT EXISTS members(room_id TEXT,user_id TEXT,PRIMARY KEY(room_id,user_id));
    CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY,room_id TEXT,user_id TEXT,body TEXT,created REAL);
    CREATE TABLE IF NOT EXISTS studio_files(id TEXT PRIMARY KEY,room_id TEXT,owner TEXT,name TEXT,kind TEXT,body TEXT,revision INTEGER,updated REAL);
    CREATE TABLE IF NOT EXISTS listings(id TEXT PRIMARY KEY,owner TEXT,project_id TEXT UNIQUE,title TEXT,description TEXT,price INTEGER,credit INTEGER,body TEXT,active INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS licenses(user_id TEXT,listing_id TEXT,body TEXT,title TEXT,seller TEXT,credit INTEGER,price INTEGER,created REAL,PRIMARY KEY(user_id,listing_id));
    CREATE TABLE IF NOT EXISTS licensed_projects(project_id TEXT PRIMARY KEY,listing_id TEXT,user_id TEXT);
    CREATE TABLE IF NOT EXISTS bot_licenses(user_id TEXT,bot TEXT,PRIMARY KEY(user_id,bot));
    CREATE INDEX IF NOT EXISTS messages_room ON messages(room_id,id);
    ''')

def install(app, core):
    db,auth,fail,text,limited,wallet_init=[core[x] for x in ('db','auth','fail','text','limited','wallet_init')]
    def member(c,rid):
        return c.execute('SELECT 1 FROM members WHERE room_id=? AND user_id=?',(rid,g.user['id'])).fetchone()
    def payload(d):
        kind=d.get('kind')
        body=d.get('body')
        if kind=='code':
            if not isinstance(body,dict):raise ValueError('Code must contain HTML, CSS and JavaScript.')
            return kind,json.dumps({k:text(body,k,150000) for k in ('html','css','js')})
        if kind=='art':
            if not isinstance(body,dict):raise ValueError('Invalid animation.')
            frames=body.get('frames');fps=body.get('fps')
            if type(fps)!=int or not 1<=fps<=24:raise ValueError('Animation speed must be 1–24 FPS.')
            if not isinstance(frames,list) or not 1<=len(frames)<=16:raise ValueError('Use 1–16 frames.')
            for frame in frames:
                if not isinstance(frame,list) or len(frame)!=256 or any(not isinstance(x,str) or not re.fullmatch(r'#[a-fA-F0-9]{6}|',x) for x in frame):raise ValueError('Use a 16 × 16 pixel frame with hex colors.')
            return kind,json.dumps({'frames':frames,'fps':fps})
        raise ValueError('Choose code or pixel art.')

    @app.get('/api/milestones')
    @auth
    def milestones():
        with db() as c:
            wallet_init(c,g.user['id'])
            start=c.execute("SELECT created FROM ledger WHERE user_id=? AND event_key='welcome'",(g.user['id'],)).fetchone()[0]
            claimed={x[0] for x in c.execute('SELECT day FROM milestones WHERE user_id=?',(g.user['id'],))}
        return jsonify(bonuses=[dict(day=d,amount=a,available=time.time()>=start+d*86400,claimed=d in claimed,due=start+d*86400) for d,a in [(60,200),(90,300)]])

    @app.post('/api/milestones')
    @auth
    def claim():
        day=g.data.get('day')
        if type(day)!=int or day not in (60,90):return fail('Unknown milestone.')
        amount={60:200,90:300}[day]
        with db() as c:
            c.execute('BEGIN IMMEDIATE');wallet_init(c,g.user['id'])
            start=c.execute("SELECT created FROM ledger WHERE user_id=? AND event_key='welcome'",(g.user['id'],)).fetchone()[0]
            if time.time()<start+day*86400:return fail('This milestone is not available yet.',409)
            if c.execute('SELECT 1 FROM milestones WHERE user_id=? AND day=?',(g.user['id'],day)).fetchone():return fail('Already claimed.',409)
            c.execute('INSERT INTO milestones VALUES(?,?)',(g.user['id'],day))
            c.execute('UPDATE wallets SET balance=balance+? WHERE user_id=?',(amount,g.user['id']))
            c.execute('INSERT INTO ledger(user_id,amount,reason,event_key,created) VALUES(?,?,?,?,?)',(g.user['id'],amount,f'{day}-day bonus',f'milestone:{day}',time.time()))
        return jsonify(ok=True)

    @app.get('/api/rooms')
    @auth
    def rooms():
        with db() as c:rows=c.execute('SELECT r.* FROM rooms r JOIN members m ON r.id=m.room_id WHERE m.user_id=? ORDER BY created DESC',(g.user['id'],)).fetchall()
        return jsonify(rooms=[dict(x) for x in rows])

    @app.post('/api/rooms')
    @auth
    def create_room():
        name=text(g.data,'name',60,True).strip();rid=secrets.token_hex(12)
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            if c.execute('SELECT COUNT(*) FROM rooms WHERE owner=?',(g.user['id'],)).fetchone()[0]>=20:return fail('Maximum 20 rooms per creator.')
            c.execute('INSERT INTO rooms VALUES(?,?,?,?,?)',(rid,g.user['id'],name,secrets.token_urlsafe(18),time.time()))
            c.execute('INSERT INTO members VALUES(?,?)',(rid,g.user['id']))
        return jsonify(id=rid)

    @app.post('/api/rooms/join')
    @auth
    def join_room():
        if limited('join:'+g.user['id'],20,300):return fail('Try again in five minutes.',429)
        code=text(g.data,'code',100,True).strip()
        with db() as c:
            r=c.execute('SELECT id FROM rooms WHERE invite=?',(code,)).fetchone()
            if not r:return fail('Invite code not found.',404)
            c.execute('INSERT OR IGNORE INTO members VALUES(?,?)',(r['id'],g.user['id']))
        return jsonify(id=r['id'])

    @app.get('/api/rooms/<rid>')
    @auth
    def room(rid):
        with db() as c:
            if not member(c,rid):return fail('Join this Studio with its invite code first.',403)
            r=dict(c.execute('SELECT * FROM rooms WHERE id=?',(rid,)).fetchone())
            people=[dict(x) for x in c.execute('SELECT u.id,u.name FROM members m JOIN users u ON u.id=m.user_id WHERE room_id=?',(rid,))]
            messages=[dict(x) for x in c.execute('SELECT m.*,u.name FROM messages m JOIN users u ON m.user_id=u.id WHERE room_id=? ORDER BY m.id DESC LIMIT 100',(rid,))][::-1]
            files=[dict(x) for x in c.execute('SELECT id,name,kind,revision,updated FROM studio_files WHERE room_id=? ORDER BY updated DESC',(rid,))]
        return jsonify(room=r,members=people,messages=messages,files=files)

    @app.post('/api/rooms/<rid>/message')
    @auth
    def message(rid):
        body=text(g.data,'body',2000,True).strip()
        with db() as c:
            if not member(c,rid):return fail('Members only.',403)
        if limited('chat:'+g.user['id'],30,60):return fail('Slow down—30 messages per minute.',429)
        with db() as c:c.execute('INSERT INTO messages(room_id,user_id,body,created) VALUES(?,?,?,?)',(rid,g.user['id'],body,time.time()))
        return jsonify(ok=True)

    @app.post('/api/rooms/<rid>/manage')
    @auth
    def manage_room(rid):
        with db() as c:
            r=c.execute('SELECT owner FROM rooms WHERE id=?',(rid,)).fetchone()
            if not r or r['owner']!=g.user['id']:return fail('Only the room owner can manage members.',403)
            if g.data.get('action')=='rotate':c.execute('UPDATE rooms SET invite=? WHERE id=?',(secrets.token_urlsafe(18),rid))
            elif g.data.get('action')=='remove':
                uid=text(g.data,'user_id',30,True)
                if uid==g.user['id']:return fail('The owner cannot be removed.')
                c.execute('DELETE FROM members WHERE room_id=? AND user_id=?',(rid,uid))
                c.execute('UPDATE rooms SET invite=? WHERE id=?',(secrets.token_urlsafe(18),rid))
            else:return fail('Unknown action.')
        return jsonify(ok=True)

    @app.get('/api/files')
    @auth
    def files():
        with db() as c:rows=c.execute('SELECT id,name,kind,revision,updated FROM studio_files WHERE room_id IS NULL AND owner=? ORDER BY updated DESC',(g.user['id'],)).fetchall()
        return jsonify(files=[dict(x) for x in rows])

    @app.get('/api/files/<fid>')
    @auth
    def file_get(fid):
        with db() as c:
            r=c.execute('SELECT * FROM studio_files WHERE id=?',(fid,)).fetchone()
            if not r or (not member(c,r['room_id']) if r['room_id'] else r['owner']!=g.user['id']):return fail('File not found or access removed.',404)
            out=dict(r);out['body']=json.loads(out['body'])
        return jsonify(file=out)

    @app.post('/api/files')
    @auth
    def file_save():
        changed=True;kind,body=payload(g.data);name=text(g.data,'name',80,True).strip();fid=g.data.get('id');rid=g.data.get('room_id') or None
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            if fid:
                r=c.execute('SELECT * FROM studio_files WHERE id=?',(fid,)).fetchone()
                if not r or (not member(c,r['room_id']) if r['room_id'] else r['owner']!=g.user['id']):return fail('No access to this file.',403)
                if r['kind']!=kind:return fail('File type cannot change.')
                if type(g.data.get('revision'))!=int or r['revision']!=g.data['revision']:return fail('A teammate saved a newer version. Your edits are still here. Download a backup, then reload the shared file.',409)
                changed=r['body']!=body;rid=r['room_id']
                c.execute('UPDATE studio_files SET name=?,body=?,revision=revision+1,updated=? WHERE id=?',(name,body,time.time(),fid));rev=r['revision']+1
            else:
                if rid and not member(c,rid):return fail('Join the room before sharing.',403)
                if c.execute('SELECT COUNT(*) FROM studio_files WHERE owner=?',(g.user['id'],)).fetchone()[0]>=300:return fail('Maximum 300 Studio files per creator.')
                fid=secrets.token_hex(12);rev=1
                c.execute('INSERT INTO studio_files VALUES(?,?,?,?,?,?,?,?)',(fid,rid,g.user['id'],name,kind,body,rev,time.time()))
            if changed:
                from community import activity
                activity(c,g.user['id'],kind,json.loads(body),rid)
        return jsonify(id=fid,revision=rev)

    @app.get('/api/market')
    def market():
        uid=g.user['id'] if g.user else ''
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            from community import support_draw
            support_draw(c)
            rows=c.execute('SELECT l.id,l.owner,l.project_id,l.title,l.description,l.price,l.credit,u.name AS seller,EXISTS(SELECT 1 FROM licenses x WHERE x.listing_id=l.id AND x.user_id=?) AS owned FROM listings l JOIN users u ON u.id=l.owner WHERE active=1',(uid,)).fetchall()
            owned=c.execute('SELECT listing_id AS id,title,seller,credit,price FROM licenses WHERE user_id=?',(uid,)).fetchall()
        return jsonify(items=[dict(x) for x in rows],owned=[dict(x) for x in owned])

    @app.post('/api/market/list')
    @auth
    def market_list():
        pid=text(g.data,'project_id',30,True);price=g.data.get('price');credit=g.data.get('credit')
        if type(price)!=int or not 1<=price<=1000000:return fail('Price must be a whole number from 1 to 1,000,000 TC.')
        if type(credit)!=bool:return fail('Choose whether creator credit is required.')
        with db() as c:
            p=c.execute('SELECT * FROM projects WHERE id=? AND owner=? AND published=1',(pid,g.user['id'])).fetchone()
            if not p:return fail('Publish your own game before listing it.',403)
            if p['parent'] or c.execute('SELECT 1 FROM licensed_projects WHERE project_id=?',(pid,)).fetchone():return fail('Remixes cannot be sold as original code in this beta.',403)
            body=json.dumps({k:p[k] for k in ('html','css','js')});lid=secrets.token_hex(12)
            c.execute('INSERT INTO listings VALUES(?,?,?,?,?,?,?,?,1) ON CONFLICT(project_id) DO UPDATE SET title=excluded.title,description=excluded.description,price=excluded.price,credit=excluded.credit,body=excluded.body,active=1',(lid,g.user['id'],pid,p['title'],p['description'],price,int(credit),body))
        return jsonify(ok=True)

    @app.post('/api/market/unlist')
    @auth
    def market_unlist():
        with db() as c:c.execute('UPDATE listings SET active=0 WHERE id=? AND owner=?',(g.data.get('id'),g.user['id']))
        return jsonify(ok=True)

    @app.post('/api/market/buy')
    @auth
    def market_buy():
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            p=c.execute('SELECT l.*,u.name seller FROM listings l JOIN users u ON u.id=l.owner WHERE l.id=? AND active=1',(g.data.get('id'),)).fetchone()
            if not p:return fail('Listing unavailable.',404)
            if p['owner']==g.user['id']:return fail('You already own your game.')
            if c.execute('SELECT 1 FROM licenses WHERE user_id=? AND listing_id=?',(g.user['id'],p['id'])).fetchone():return jsonify(ok=True)
            wallet_init(c,g.user['id']);wallet_init(c,p['owner'])
            if not c.execute('UPDATE wallets SET balance=balance-? WHERE user_id=? AND balance>=?',(p['price'],g.user['id'],p['price'])).rowcount:return fail('Not enough Trencoins.',409)
            c.execute('UPDATE wallets SET balance=balance+? WHERE user_id=?',(p['price'],p['owner']))
            c.execute('INSERT INTO licenses VALUES(?,?,?,?,?,?,?,?)',(g.user['id'],p['id'],p['body'],p['title'],p['seller'],p['credit'],p['price'],time.time()))
            for uid,amount,reason in [(g.user['id'],-p['price'],'License: '+p['title']),(p['owner'],p['price'],'Sale: '+p['title'])]:
                c.execute('INSERT INTO ledger(user_id,amount,reason,event_key,created) VALUES(?,?,?,?,?)',(uid,amount,reason,'license:'+p['id']+':'+g.user['id'],time.time()))
        return jsonify(ok=True)

    @app.get('/api/market/owned/<lid>')
    @auth
    def owned_license(lid):
        with db() as c:r=c.execute('SELECT * FROM licenses WHERE user_id=? AND listing_id=?',(g.user['id'],lid)).fetchone()
        if not r:return fail('Purchase a license first.',403)
        out=dict(r);out['body']=json.loads(out['body']);return jsonify(license=out)

    @app.post('/api/market/import')
    @auth
    def import_license():
        import html
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            r=c.execute('SELECT * FROM licenses WHERE user_id=? AND listing_id=?',(g.user['id'],g.data.get('id'))).fetchone()
            if not r:return fail('Purchase this license first.',403)
            if c.execute('SELECT COUNT(*) FROM projects WHERE owner=?',(g.user['id'],)).fetchone()[0]>=200:return fail('Project limit reached.')
            body=json.loads(r['body']);pid=secrets.token_hex(12)
            if r['credit']:body['html']+='\n<footer>Original creator: @'+html.escape(r['seller'])+'</footer>'
            c.execute('INSERT INTO projects VALUES(?,?,?,?,?,?,?,?,?,?,?)',(pid,g.user['id'],r['title'],'Licensed from @'+r['seller'],body['html'],body['css'],body['js'],0,None,time.time(),time.time()))
            c.execute('INSERT INTO licensed_projects VALUES(?,?,?)',(pid,r['listing_id'],g.user['id']))
        return jsonify(id=pid)

    def bots():
        key=os.environ.get('OPENAI_API_KEY','')
        return [dict(id=k,name=n,price=p,ready=bool(key and os.environ.get(env)),model=os.environ.get(env,'')) for k,n,p,env in [('normal','Normal Bot',2000,'TRENCOD_NORMAL_MODEL'),('smart','Smart Bot',5000,'TRENCOD_SMART_MODEL')]]

    @app.get('/api/bots')
    def bot_list():
        with db() as c:owned={x[0] for x in c.execute('SELECT bot FROM bot_licenses WHERE user_id=?',(g.user['id'],))} if g.user else set()
        return jsonify(bots=[{k:v for k,v in dict(b,owned=b['id'] in owned).items() if k!='model'} for b in bots()],daily_limit=20)

    @app.post('/api/bots/buy')
    @auth
    def bot_buy():
        b=next((x for x in bots() if x['id']==g.data.get('id')),None)
        if not b:return fail('Bot not found.',404)
        if not b['ready']:return fail('The site owner has not connected this AI yet. No coins charged.',503)
        with db() as c:
            c.execute('BEGIN IMMEDIATE');wallet_init(c,g.user['id'])
            if c.execute('SELECT 1 FROM bot_licenses WHERE user_id=? AND bot=?',(g.user['id'],b['id'])).fetchone():return jsonify(ok=True)
            if not c.execute('UPDATE wallets SET balance=balance-? WHERE user_id=? AND balance>=?',(b['price'],g.user['id'],b['price'])).rowcount:return fail('Not enough Trencoins.',409)
            c.execute('INSERT INTO bot_licenses VALUES(?,?)',(g.user['id'],b['id']))
            c.execute('INSERT INTO ledger(user_id,amount,reason,event_key,created) VALUES(?,?,?,?,?)',(g.user['id'],-b['price'],'Unlocked '+b['name'],'bot:'+b['id'],time.time()))
        return jsonify(ok=True)

    @app.post('/api/bots/ask')
    @auth
    def bot_ask():
        prompt=text(g.data,'prompt',20000,True);b=next((x for x in bots() if x['id']==g.data.get('id')),None)
        if not b or not b['ready']:return fail('AI connection is not configured.',503)
        with db() as c:
            if not c.execute('SELECT 1 FROM bot_licenses WHERE user_id=? AND bot=?',(g.user['id'],b['id'])).fetchone():return fail('Unlock this bot in the shop first.',403)
        today=datetime.now(timezone.utc).strftime('%Y-%m-%d')
        if limited('ai:'+g.user['id']+':'+today,20,86400):return fail('Daily beta limit reached: 20 requests across your bots.',429)
        payload={'model':b['model'],'store':False,'max_output_tokens':3000,'instructions':'You help Trencod creators write HTML/CSS/JavaScript games and design pixel art. Explain clearly. Never claim you saved, published or changed files. Return suggested code for review. Do not request passwords or personal information.','input':prompt}
        req=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY'],'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=15) as response:r=json.load(response)
            answer='\n'.join(part.get('text',part.get('refusal','')) for item in r.get('output',[]) for part in item.get('content',[]) if part.get('type') in ('output_text','refusal'))
            if not answer:return fail('AI returned no text. Try a shorter question.',502)
            return jsonify(answer=answer)
        except (urllib.error.URLError,TimeoutError,ValueError):return fail('AI provider unavailable or its configuration needs attention. Your work has not changed.',502)
