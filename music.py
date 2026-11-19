"""Small, immutable music clips stored alongside creator data (including Neon)."""
import base64, binascii, io, json, math, re, secrets, time
from flask import g, jsonify, send_file
MAX_BYTES=300000
MAX_CLIPS=20

def validate_music(value):
    if value is None:return None
    if not isinstance(value,dict) or not isinstance(value.get('id'),str) or not re.fullmatch(r'[a-f0-9]{24}',value['id']):raise ValueError('Choose a saved music clip.')
    volume=value.get('volume',0.5);loop=value.get('loop',True)
    if type(volume) not in (int,float) or not math.isfinite(volume) or not 0<=volume<=1:raise ValueError('Music volume must be between 0 and 1.')
    if type(loop) is not bool:raise ValueError('Choose whether music should loop.')
    return {'id':value['id'],'volume':volume,'loop':loop}

def music_markup(value,origin):
    m=validate_music(value)
    if not m:return ''
    from html import escape
    url=escape(origin.rstrip('/')+'/media/music/'+m['id'],quote=True)
    return '<section aria-label="Game music"><p>Music · Press play to listen</p><audio controls preload="none" '+('loop ' if m['loop'] else '')+'src="'+url+'" onloadedmetadata="this.volume='+str(m['volume'])+'" style="max-width:100%"></audio></section>'

def install(app,core):
    db,auth,fail,text=[core[k] for k in ('db','auth','fail','text')]
    @app.get('/api/music')
    @auth
    def music_list():
        with db() as c:rows=c.execute('SELECT id,name,mime,size,created FROM music_clips WHERE owner=? ORDER BY created DESC',(g.user['id'],)).fetchall()
        return jsonify(clips=[dict(r) for r in rows],max_bytes=MAX_BYTES,max_clips=MAX_CLIPS)
    @app.post('/api/music')
    @auth
    def music_upload():
        name=text(g.data,'name',80,True).strip();encoded=g.data.get('data')
        if not name or not isinstance(encoded,str) or len(encoded)>400000:return fail('Choose a music clip up to 300 KB.')
        try:raw=base64.b64decode(encoded,validate=True)
        except (ValueError,binascii.Error):return fail('Invalid audio upload.')
        if not raw or len(raw)>MAX_BYTES:return fail('Choose a music clip up to 300 KB.')
        if len(raw)>12 and raw[:4]==b'RIFF' and raw[8:12]==b'WAVE':mime='audio/wav'
        elif len(raw)>27 and raw[:4]==b'OggS':mime='audio/ogg'
        elif len(raw)>10 and (raw[:3]==b'ID3' or raw[0]==255 and raw[1]&224==224):mime='audio/mpeg'
        else:return fail('Use an MP3, Ogg or WAV audio file.')
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            if c.execute('SELECT COUNT(*) FROM music_clips WHERE owner=?',(g.user['id'],)).fetchone()[0]>=MAX_CLIPS:return fail('Your music library holds up to 20 clips. Reuse an existing clip.',409)
            mid=secrets.token_hex(12)
            c.execute('INSERT INTO music_clips VALUES(?,?,?,?,?,?,?)',(mid,g.user['id'],name,mime,len(raw),encoded,time.time()))
        return jsonify(clip={'id':mid,'name':name,'mime':mime,'size':len(raw)})
    @app.get('/media/music/<mid>')
    def music_audio(mid):
        if not re.fullmatch(r'[a-f0-9]{24}',mid):return fail('Music not found.',404)
        with db() as c:r=c.execute('SELECT mime,body FROM music_clips WHERE id=?',(mid,)).fetchone()
        if not r:return fail('Music not found.',404)
        return send_file(io.BytesIO(base64.b64decode(r['body'])),mimetype=r['mime'],conditional=True,download_name='music.'+{'audio/mpeg':'mp3','audio/ogg':'ogg','audio/wav':'wav'}[r['mime']])
