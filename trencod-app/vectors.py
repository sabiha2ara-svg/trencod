"""Small data-only vector format: no SVG markup, scripts, URLs or external assets."""
import math,re,json

def validate_vector(body):
 if not isinstance(body,dict) or body.get('type')!='vector':raise ValueError('Invalid vector drawing.')
 if len(json.dumps(body))>100000:raise ValueError('Keep vector drawings under 100 KB.')
 shapes=body.get('shapes')
 if not isinstance(shapes,list) or len(shapes)>160:raise ValueError('Use up to 160 vector shapes.')
 name=body.get('name','Vector sprite')
 if not isinstance(name,str) or len(name)>80:raise ValueError('Use a name under 80 characters.')
 out=[]
 for s in shapes:
  if not isinstance(s,dict) or s.get('kind') not in ('rect','ellipse','path'):raise ValueError('Invalid vector shape.')
  v={'kind':s['kind']}
  for k,lo,hi in [('x',-256,512),('y',-256,512),('w',1,512),('h',1,512),('rotation',-360,360),('sw',0,20)]:
   n=s.get(k,0 if k in ('rotation','sw') else None)
   if type(n) not in (int,float) or not math.isfinite(n) or not lo<=n<=hi:raise ValueError('Invalid vector coordinates.')
   v[k]=n
  for k in ('fill','stroke'):
   color=s.get(k,'none')
   if not isinstance(color,str) or not re.fullmatch(r'none|#[0-9a-fA-F]{6}',color):raise ValueError('Use hex colors or none.')
   v[k]=color
  if s['kind']=='path':
   pts=s.get('points')
   if not isinstance(pts,list) or not 2<=len(pts)<=400:raise ValueError('Use 2–400 path points.')
   for pair in pts:
    if not isinstance(pair,list) or len(pair)!=2 or any(type(n) not in (int,float) or not math.isfinite(n) or not 0<=n<=256 for n in pair):raise ValueError('Invalid path point.')
   v['points']=pts;v['closed']=s.get('closed') is True
  out.append(v)
 return {'type':'vector','name':name,'shapes':out}
