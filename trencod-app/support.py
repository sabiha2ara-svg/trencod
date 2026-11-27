"""Private support tickets. No email delivery; the owner reviews the inbox."""
import os,secrets,time
from flask import g,jsonify,send_from_directory

def install(app,core):
    db,auth,fail,text,limited=[core[k] for k in ('db','auth','fail','text','limited')]
    def owner():
        return bool(g.user and g.user['id'] in {x.strip() for x in os.environ.get('TRENCOD_SUPPORT_ADMINS','').split(',') if x.strip()})
    @app.get('/help')
    def help_page():return send_from_directory(core['PUBLIC'],'help.html')
    @app.get('/api/feedback')
    @auth
    def tickets():
        with db() as c:
            rows=c.execute('SELECT * FROM feedback ORDER BY updated DESC LIMIT 200' if owner() else 'SELECT * FROM feedback WHERE user_id=? ORDER BY updated DESC LIMIT 100',() if owner() else (g.user['id'],)).fetchall()
        return jsonify(tickets=[dict(r) for r in rows],admin=owner(),staff_configured=bool(os.environ.get('TRENCOD_SUPPORT_ADMINS','').strip()))
    @app.post('/api/feedback')
    @auth
    def submit():
        category=g.data.get('category')
        if category not in ('bug','studio','purchase','account','idea','security'):return fail('Choose a report category.')
        subject=text(g.data,'subject',120,True).strip();body=text(g.data,'body',4000,True).strip()
        if not subject or not body:return fail('Describe the problem before sending.')
        if limited('feedback:'+g.user['id'],5,3600):return fail('Maximum five reports per hour. Please wait.',429)
        ticket=secrets.token_hex(12);now=time.time()
        with db() as c:c.execute('INSERT INTO feedback VALUES(?,?,?,?,?,?,?,?,?)',(ticket,g.user['id'],category,subject,body,'open','',now,now))
        return jsonify(id=ticket,status='open')
    @app.post('/api/feedback/<ticket>/reply')
    @auth
    def reply(ticket):
        if not owner():return fail('Support owner access required.',403)
        status=g.data.get('status');message=text(g.data,'reply',4000,True).strip()
        if status not in ('open','investigating','resolved') or not message:return fail('Choose a status and write a reply.')
        with db() as c:
            if not c.execute('UPDATE feedback SET status=?,reply=?,updated=? WHERE id=?',(status,message,time.time(),ticket)).rowcount:return fail('Report not found.',404)
        return jsonify(ok=True)
