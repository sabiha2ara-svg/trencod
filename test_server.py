import os,sys,tempfile,unittest,json,sqlite3,hashlib,concurrent.futures
from pathlib import Path
scratch=tempfile.TemporaryDirectory()
os.environ['TRENCOD_DATA_DIR']=scratch.name
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server
server.init()
BASE='http://127.0.0.1:8765'
class FlowTests(unittest.TestCase):
    def setUp(self):
        server.DB=Path(scratch.name)/('case-'+os.urandom(5).hex()+'.sqlite3');server.init()
        self.a=server.app.test_client();self.b=server.app.test_client();self.guest=server.app.test_client()
        for c,name in [(self.a,'CreatorA'),(self.b,'CreatorB')]:self.post(c,'register',{'name':name,'password':'test-password'})
    def get(self,c,p,status=200):
        r=c.get('/api/'+p,base_url=BASE);self.assertEqual(r.status_code,status,r.get_json());return r.get_json()
    def post(self,c,p,data,status=200,**kw):
        r=c.post('/api/'+p,json=data,base_url=BASE,**kw);self.assertEqual(r.status_code,status,r.get_json());return r.get_json()
    def test_login_logout_errors_and_case_insensitivity(self):
        self.assertEqual(self.get(self.a,'me')['user']['name'],'CreatorA')
        self.post(self.a,'logout',{});self.assertIsNone(self.get(self.a,'me')['user'])
        self.post(self.a,'login',{'name':'CreatorA','password':'wrong'},401)
        self.post(self.a,'login',{'name':'creatora','password':'test-password'})
        self.post(self.guest,'register',{'name':'CreatorA','password':'longpassword'},409)
        self.post(self.guest,'register',{'name':'bad space','password':'longpassword'},400)
        self.post(self.guest,'register',{'name':'goodname','password':'short'},400)
    def test_old_scrypt_account_migration(self):
        salt=os.urandom(16).hex();password=hashlib.scrypt(b'old-password',salt=bytes.fromhex(salt),n=16384,r=8,p=1).hex()
        with server.db() as c:c.execute('INSERT INTO users VALUES(?,?,?,?)',('old-user','OldUser',salt,password))
        self.post(self.guest,'login',{'name':'OldUser','password':'old-password'})
        with server.db() as c:self.assertTrue(c.execute('SELECT password FROM users WHERE id=?',('old-user',)).fetchone()[0].startswith('pbkdf2$'))
    def test_private_publish_remix_and_permissions(self):
        p=self.post(self.a,'save',{'title':'Space Racer','html':'<h1>Race</h1>','css':'','js':''})['id']
        self.get(self.b,'project/'+p,404);self.get(self.guest,'project/'+p,404)
        self.post(self.b,'save',{'id':p,'title':'No','html':'','css':'','js':''},403)
        self.post(self.b,'publish',{'id':p},403)
        self.post(self.a,'publish',{'id':p});self.assertTrue(any(x['id']==p for x in self.get(self.b,'projects')['projects']))
        copy=self.post(self.b,'remix',{'id':p})['id'];self.get(self.a,'project/'+copy,404)
        self.assertEqual(self.get(self.b,'project/'+copy)['project']['parent'],p)
        self.post(self.a,'unpublish',{'id':p});self.get(self.b,'project/'+p,404)
        self.get(self.b,'project/'+copy)
    def test_wallet_daily_shop_and_idempotency(self):
        self.assertEqual(self.get(self.a,'wallet')['balance'],100)
        self.get(self.a,'item/pixel-alien',403)
        self.post(self.a,'daily',{},410)
        self.assertEqual(self.get(self.a,'wallet')['balance'],100)
        self.post(self.a,'buy',{'id':'pixel-alien','price':0})
        self.assertEqual(self.get(self.a,'wallet')['balance'],80)
        self.post(self.a,'buy',{'id':'pixel-alien'});self.assertEqual(self.get(self.a,'wallet')['balance'],80)
        self.assertIn('<svg',self.get(self.a,'item/pixel-alien')['item']['source'])
        self.get(self.b,'item/pixel-alien',403)
        self.post(self.a,'buy',{'id':'fake'},404)
        with server.db() as c:c.execute('UPDATE wallets SET balance=0 WHERE user_id=?',(self.get(self.a,'me')['user']['id'],))
        self.post(self.a,'buy',{'id':'pixel-heart'},409)
        self.get(self.a,'item/pixel-heart',403)
        server.init();self.assertEqual(self.get(self.a,'wallet')['balance'],0)
    def test_concurrent_purchase_charges_once(self):
        cookie=self.a.get_cookie('trencod_session',domain='127.0.0.1').value
        def buy(_):
            c=server.app.test_client();c.set_cookie('trencod_session',cookie,domain='127.0.0.1')
            return c.post('/api/buy',json={'id':'pixel-alien'},base_url=BASE).status_code
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:self.assertEqual(list(pool.map(buy,range(4))),[200]*4)
        self.assertEqual(self.get(self.a,'wallet')['balance'],80)
    def test_favorites_reports_security_assets(self):
        self.post(self.guest,'favorite',{'id':'star-dash'},401)
        self.assertTrue(self.post(self.a,'favorite',{'id':'star-dash'})['favorite'])
        self.assertEqual(len(self.get(self.a,'favorites')['projects']),1)
        self.assertFalse(self.post(self.a,'favorite',{'id':'star-dash'})['favorite'])
        self.post(self.a,'report',{'id':'star-dash','reason':'test report'})
        self.post(self.a,'daily',{},403,headers={'Origin':'https://evil.example'})
        r=self.a.post('/api/daily',data='{}',content_type='text/plain',base_url=BASE);self.assertEqual(r.status_code,415)
        self.assertEqual(self.a.get('/',base_url='http://evil.example').status_code,403)
        for path in ['/','/app.js','/style.css','/intro.js','/intro.css','/trencod-icon.png','/healthz']:
            response=self.a.get(path,base_url=BASE);self.assertEqual(response.status_code,200);response.close()
        self.assertEqual(len(self.get(self.a,'projects')['projects']),3)
if __name__=='__main__':unittest.main(verbosity=2)
