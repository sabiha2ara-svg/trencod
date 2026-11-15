import os,unittest
from unittest.mock import patch
import test_creators as fixtures
from database import connect,postgres_sql
server=fixtures.server
class StorageTests(unittest.TestCase):
 setUp=fixtures.CreatorTests.setUp
 post=fixtures.CreatorTests.post
 get=fixtures.CreatorTests.get
 def test_export_is_private_and_has_no_auth_secrets(self):
  a=self.post(self.a,'save',{'title':'Mine','html':'<h1>Own code</h1>'})['id']
  b=self.post(self.b,'save',{'title':'Private other','html':'do not export me'})['id']
  f=self.post(self.a,'files',{'name':'Art','kind':'art','body':{'frames':[['#ffffff']*256],'fps':6}})['id']
  export=self.get(self.a,'my-backup')
  self.assertEqual([p['id'] for p in export['projects']],[a])
  self.assertNotIn(b,str(export));self.assertEqual(export['personal_files'][0]['id'],f)
  self.assertEqual(set(export['creator']),{'id','name'})
  self.get(server.app.test_client(),'my-backup',401)
  server.init()
  self.assertEqual(self.get(self.a,'my-backup')['projects'][0]['id'],a)
 def test_render_requires_database_url(self):
  with patch.dict(os.environ,{'RENDER':'true','DATABASE_URL':''}):
   with self.assertRaisesRegex(RuntimeError,'required on Render'):connect(server.DB)
 def test_invalid_database_url_never_falls_back(self):
  with patch.dict(os.environ,{'DATABASE_URL':'psql postgres://bad'}):
   with self.assertRaisesRegex(RuntimeError,'only the connection URL'):connect(server.DB)
 def test_sql_values_not_rewritten(self):
  self.assertEqual(postgres_sql("SELECT 'REAL LIKE ?'"),"SELECT 'REAL LIKE ?'")
 def test_health_checks_database(self):
  with patch.object(server,'db',side_effect=RuntimeError('private db detail')):
   r=server.app.test_client().get('/healthz',base_url=fixtures.BASE)
   self.assertEqual(r.status_code,503);self.assertNotIn('private db detail',r.get_data(as_text=True))
