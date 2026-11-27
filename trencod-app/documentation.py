"""Public, server-rendered documentation. No user data in the sitemap."""
import json
from html import escape
from urllib.parse import urlsplit
from flask import Response,request

def install(app,core):
    root=core['ROOT'];pages=json.loads((root/'docs_metadata.json').read_text())
    def base():
        value=core['PUBLIC_URL'].rstrip('/')
        parsed=urlsplit(value)
        return value if parsed.scheme in ('https','http') and parsed.netloc and not parsed.username and not parsed.query and not parsed.fragment else ''
    links=[('/about','About'),('/getting-started','Tutorials'),('/security','Security'),('/privacy','Privacy'),('/market-guide','Buying & selling'),('/community','Community'),('/changelog','Changelog'),('/status','Status'),('/help#contact','Contact')]
    style='''body{margin:0;background:#0b1020;color:#edf1ff;font:17px/1.7 system-ui}main,header,footer{max-width:920px;margin:auto;padding:24px}header{border-bottom:1px solid #35415c}a{color:#88e8d8;text-underline-offset:4px}nav{display:flex;gap:12px 22px;flex-wrap:wrap;margin-top:20px}nav a{padding:4px 0}h1{font-size:clamp(30px,6vw,48px);line-height:1.2}h2{margin-top:32px;font-size:24px}p,li{overflow-wrap:anywhere}section{border:1px solid #35415c;padding:20px;border-radius:14px;background:#171f35}small{color:#b7c4dd}button{padding:12px 20px;background:#b8acff;border:0;border-radius:8px;font:inherit;cursor:pointer}button:disabled{opacity:.6}a:focus-visible,button:focus-visible{outline:3px solid #fff;outline-offset:4px}.skip{display:block}footer{border-top:1px solid #35415c}'''
    def render(title,description,body,path):
        canonical='<link rel="canonical" href="'+escape(base()+path,quote=True)+'">' if base() else ''
        nav=''.join('<a href="'+url+'"'+(' aria-current="page"' if path==url else '')+'>'+label+'</a>' for url,label in links)
        return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(title)+' | Trencod</title><meta name="description" content="'+escape(description,quote=True)+'">'+canonical+'<style>'+style+'</style></head><body><header><a class="skip" href="#content">Skip to content</a><a href="/">Trencod · Play. Create. Remix.</a><nav aria-label="Documentation">'+nav+'</nav></header><main id="content"><small>BETA · Documentation updated 27 November 2026</small><h1>'+escape(title)+'</h1><p>'+escape(description)+'</p>'+body+'</main><footer>Demo coins have no cash value. <a href="/help#contact">Report an issue</a> · <a href="/">Return to Trencod</a></footer></body></html>'
    def document():
        slug=request.path.lstrip('/');page=pages[slug]
        return render(page['title'],page['description'],(root/'public/docs'/f'{slug}.html').read_text(),request.path)
    for slug in pages:app.add_url_rule('/'+slug,'docs_'+slug,document,methods=['GET'])
    @app.get('/status')
    def status():
        body='''<section><h2>Live service check</h2><p id="status" role="status">Press Check now to test app and database reachability.</p><button id="check">Check now</button></section><p>This is a point-in-time check from this browser, not independent monitoring, uptime history, a security scan or a backup verification. If the entire website is unavailable, this page may be unavailable too.</p><script>
const b=document.getElementById('check'),s=document.getElementById('status');b.onclick=async()=>{b.disabled=true;s.textContent='Checking…';const abort=new AbortController(),timer=setTimeout(()=>abort.abort(),25000);try{const r=await fetch('/healthz',{cache:'no-store',signal:abort.signal}),x=await r.json();if(!r.ok||!x.ok)throw Error('Service or database check failed.');s.textContent='App and database responded · Version '+x.version+' · Storage '+x.storage+' · Checked '+new Date().toLocaleString();}catch(e){s.textContent='Could not confirm service availability. Try again or report the problem.';}finally{clearTimeout(timer);b.disabled=false;}};
</script>'''
        return render('Service status','Check the currently deployed version and database reachability.',body,'/status')
    @app.get('/sitemap.xml')
    def sitemap():
        if not base():return Response('Set TRENCOD_PUBLIC_URL to the public site origin before submitting a sitemap.',status=503,mimetype='text/plain')
        paths=['/','/help']+['/'+slug for slug in pages]
        body='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+escape(base()+path)+'</loc></url>' for path in paths)+'</urlset>'
        return Response(body,mimetype='application/xml')
    @app.get('/robots.txt')
    def robots():
        return Response('User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /healthz\n'+('Sitemap: '+base()+'/sitemap.xml\n' if base() else ''),mimetype='text/plain')
