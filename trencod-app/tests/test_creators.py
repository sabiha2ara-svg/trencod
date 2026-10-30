import os,sys,tempfile,unittest,time,json,concurrent.futures
from pathlib import Path
from unittest.mock import patch
scratch=tempfile.TemporaryDirectory();os.environ['TRENCOD_DATA_DIR']=scratch.name
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server
BASE='http://127.0.0.1:8765'
class CreatorTests(unittest.TestCase):
 def setUp(self):
  server.DB=Path(scratch.name)/(os.urandom(8).hex()+'.db');server.init()
  self.a=server.app.test_client();self.b=server.app.test_client();self.c=server.app.test_client()
  for c,n in [(self.a,'CreatorA'),(self.b,'CreatorB'),(self.c,'Outsider')]:self.post(c,'register',{'name':n,'password':'test-pass-123'})
 def post(self,c,p,data,status=200):
  r=c.post('/api/'+p,json=data,base_url=BASE);self.assertEqual(r.status_code,status,r.get_json());return r.get_json()
 def get(self,c,p,status=200):
  r=c.get('/api/'+p,base_url=BASE);self.assertEqual(r.status_code,status,r.get_json());return r.get_json()
 def test_milestones(self):
  self.post(self.a,'daily',{},410);self.post(self.a,'milestones',{'day':60},409)
  uid=self.get(self.a,'me')['user']['id']
  with server.db() as c:c.execute("UPDATE ledger SET created=? WHERE user_id=? AND event_key='welcome'",(time.time()-91*86400,uid))
  for d in (60,90):self.post(self.a,'milestones',{'day':d});self.post(self.a,'milestones',{'day':d},409)
  self.assertEqual(self.get(self.a,'wallet')['balance'],600)
  server.init();self.assertEqual(self.get(self.a,'wallet')['balance'],600)
 def test_rooms_permissions_conflict_removal(self):
  rid=self.post(self.a,'rooms',{'name':'Team'})['id'];r=self.get(self.a,'rooms/'+rid)
  self.get(self.b,'rooms/'+rid,403);self.post(self.b,'rooms/join',{'code':r['room']['invite']})
  self.post(self.b,'rooms/'+rid+'/message',{'body':'<script>alert(1)</script>'});self.assertEqual(len(self.get(self.a,'rooms/'+rid)['messages']),1)
  payload={'room_id':rid,'kind':'code','name':'Shared','body':{'html':'<h1>hi</h1>','css':'','js':''}}
  f=self.post(self.a,'files',payload);self.get(self.c,'files/'+f['id'],404)
  self.post(self.b,'files',{**payload,**f});self.post(self.a,'files',{**payload,**f},409)
  self.assertEqual(self.get(self.a,'files/'+f['id'])['file']['revision'],2)
  uid=self.get(self.b,'me')['user']['id'];self.post(self.a,'rooms/'+rid+'/manage',{'action':'remove','user_id':uid})
  self.get(self.b,'rooms/'+rid,403);self.get(self.b,'files/'+f['id'],404);self.post(self.b,'rooms/join',{'code':r['room']['invite']},404)
 def test_art_validation_persistence(self):
  body={'frames':[['#5eead4']*256,['']*256],'fps':6};f=self.post(self.a,'files',{'name':'Sprite','kind':'art','body':body})
  server.init();self.assertEqual(self.get(self.a,'files/'+f['id'])['file']['body'],body)
  self.post(self.a,'files',{'name':'Bad','kind':'art','body':{'fps':6,'frames':[['javascript:x']*256]}},400)
 def test_sales_snapshot_idempotency(self):
  pid=self.post(self.a,'save',{'title':'My game','html':'original','css':'','js':''})['id'];self.post(self.a,'publish',{'id':pid})
  self.post(self.a,'market/list',{'project_id':pid,'price':50,'credit':True});lid=self.get(self.b,'market')['items'][0]['id']
  self.post(self.b,'remix',{'id':pid},403);self.get(self.b,'market/owned/'+lid,403)
  cookie=self.b.get_cookie('trencod_session',domain='127.0.0.1').value
  def buy(_):
   c=server.app.test_client();c.set_cookie('trencod_session',cookie,domain='127.0.0.1');return c.post('/api/market/buy',json={'id':lid,'price':0},base_url=BASE).status_code
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:self.assertEqual(list(pool.map(buy,range(4))),[200]*4)
  self.assertEqual(self.get(self.a,'wallet')['balance'],150);self.assertEqual(self.get(self.b,'wallet')['balance'],50)
  self.post(self.a,'save',{'id':pid,'title':'My game','html':'new','css':'','js':''});self.post(self.a,'market/list',{'project_id':pid,'price':90,'credit':False})
  owned=self.get(self.b,'market/owned/'+lid)['license'];self.assertEqual(owned['body']['html'],'original');self.assertTrue(owned['credit'])
  copy=self.post(self.b,'market/import',{'id':lid})['id'];self.post(self.b,'publish',{'id':copy});self.post(self.b,'market/list',{'project_id':copy,'price':10,'credit':False},403)
  self.post(self.a,'market/unlist',{'id':lid});self.get(self.b,'market/owned/'+lid)
 def test_upgrade_copies_without_overwrite(self):
  from upgrade import import_database
  import sqlite3
  target=Path(scratch.name)/('import-'+os.urandom(5).hex())/'trencod.sqlite3'
  import_database(server.DB,target)
  with sqlite3.connect(target) as c:self.assertEqual(c.execute('SELECT count(*) FROM users').fetchone()[0],3)
  before=target.read_bytes()
  with self.assertRaises(FileExistsError):import_database(server.DB,target)
  self.assertEqual(target.read_bytes(),before)
  self.assertEqual(self.get(self.a,'me')['user']['name'],'CreatorA')
 def test_ai_gate_and_mock(self):
  self.post(self.a,'bots/buy',{'id':'normal'},503);self.assertEqual(self.get(self.a,'wallet')['balance'],100)
  uid=self.get(self.a,'me')['user']['id']
  with patch.dict(os.environ,{'OPENAI_API_KEY':'test-only','TRENCOD_NORMAL_MODEL':'test-model'}):
   self.post(self.a,'bots/ask',{'id':'normal','prompt':'hi'},403)
   with server.db() as c:c.execute('UPDATE wallets SET balance=6000 WHERE user_id=?',(uid,))
   self.post(self.a,'bots/buy',{'id':'normal'});self.post(self.a,'bots/buy',{'id':'normal'});self.assertEqual(self.get(self.a,'wallet')['balance'],4000)
   import io
   with patch('urllib.request.urlopen',return_value=io.BytesIO(json.dumps({'output':[{'content':[{'type':'output_text','text':'Suggested code'}]}]}).encode())) as mock:
    self.assertEqual(self.post(self.a,'bots/ask',{'id':'normal','prompt':'Help me'})['answer'],'Suggested code');self.assertEqual(mock.call_args.args[0].full_url,'https://api.openai.com/v1/responses')
if __name__=='__main__':unittest.main(verbosity=2)
