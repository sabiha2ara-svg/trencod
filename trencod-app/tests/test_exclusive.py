import concurrent.futures,json,time,unittest
import test_creators as fixtures
server=fixtures.server
class ExclusiveTests(unittest.TestCase):
 setUp=fixtures.CreatorTests.setUp
 post=fixtures.CreatorTests.post
 get=fixtures.CreatorTests.get
 def game_listing(self,body='exclusive test code'):
  pid=self.post(self.a,'save',{'title':'Exclusive','html':body})['id']
  self.post(self.a,'publish',{'id':pid})
  self.post(self.a,'market/list',{'project_id':pid,'price':25,'credit':False})
  return pid,self.get(self.a,'market')['items'][0]['id']
 def test_different_buyers_race_and_permissions(self):
  pid,lid=self.game_listing()
  cookies=[x.get_cookie('trencod_session',domain='127.0.0.1').value for x in (self.b,self.c)]
  def buy(cookie):
   client=server.app.test_client();client.set_cookie('trencod_session',cookie,domain='127.0.0.1')
   return client.post('/api/market/buy',json={'id':lid},base_url=fixtures.BASE).status_code
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(buy,cookies))
  self.assertEqual(sorted(results),[200,409])
  winner=(self.b,self.c)[results.index(200)];loser=(self.b,self.c)[results.index(409)]
  self.assertEqual(self.get(winner,'wallet')['balance'],75)
  self.assertEqual(self.get(loser,'wallet')['balance'],100)
  self.assertEqual(self.get(self.a,'wallet')['balance'],125)
  self.assertEqual(self.get(self.a,'mine')['projects'],[])
  self.assertEqual(self.get(winner,'mine')['projects'][0]['id'],pid)
  self.assertFalse(self.get(winner,'mine')['projects'][0]['published'])
  self.assertEqual(self.get(winner,'market')['items'],[])
  self.post(self.a,'publish',{'id':pid},403)
  self.post(self.a,'unpublish',{'id':pid},403)
  self.post(self.a,'save',{'id':pid,'title':'steal','html':'x'},403)
  self.get(self.a,'history/'+pid,404)
  for _ in range(2):self.assertEqual(self.post(winner,'market/import',{'id':lid})['id'],pid)
  self.post(winner,'save',{'id':pid,'title':'My purchase','html':'updated by buyer'})
  self.post(winner,'publish',{'id':pid})
  self.post(self.a,'remix',{'id':pid},403)
  self.post(self.a,'save',{'title':'Reuploaded','html':'exclusive test code'},409)
  server.init()
  self.assertEqual(len(self.get(winner,'mine')['projects']),1)
 def test_duplicate_before_sale_is_unpublished(self):
  pid,lid=self.game_listing()
  copy=self.post(self.a,'save',{'title':'Saved copy','html':'exclusive test code'})['id']
  self.post(self.a,'publish',{'id':copy})
  self.post(self.b,'market/buy',{'id':lid})
  self.post(self.a,'publish',{'id':copy},409)
  self.assertFalse(self.get(self.a,'mine')['projects'][0]['published'])
 def test_legacy_sales_are_preserved_and_closed(self):
  pid,lid=self.game_listing()
  uid=self.get(self.b,'me')['user']['id']
  with server.db() as c:
   row=c.execute('SELECT * FROM listings WHERE id=?',(lid,)).fetchone()
   c.execute('INSERT INTO licenses VALUES(?,?,?,?,?,?,?,?)',(uid,lid,row['body'],row['title'],'CreatorA',0,25,time.time()))
  server.init()
  self.assertEqual(self.get(self.a,'market')['items'],[])
  self.get(self.b,'market/owned/'+lid)
  self.post(self.a,'market/list',{'project_id':pid,'price':25,'credit':False},409)
  self.assertEqual(self.get(self.a,'mine')['projects'][0]['id'],pid)
 def test_art_transfer_and_duplicate_block(self):
  body={'fps':4,'frames':[['#112233']*256]}
  fid=self.post(self.a,'files',{'name':'Art','kind':'art','body':body})['id']
  self.post(self.a,'art-market/list',{'id':fid,'price':20,'rights':True})
  lid=self.get(self.b,'art-market')['items'][0]['id']
  self.post(self.b,'art-market/buy',{'id':lid})
  self.post(self.c,'art-market/buy',{'id':lid},409)
  self.get(self.a,'files/'+fid,404)
  self.assertEqual(self.get(self.b,'files/'+fid)['file']['body'],body)
  self.assertEqual(self.get(self.b,'art-market')['items'],[])
  self.post(self.a,'files',{'name':'Copy','kind':'art','body':body},409)
  self.post(self.b,'art-market/list',{'id':fid,'price':20,'rights':True},409)
 def test_insufficient_funds_preserves_listing_and_owner(self):
  pid,lid=self.game_listing()
  uid=self.get(self.b,'me')['user']['id']
  with server.db() as c:c.execute('UPDATE wallets SET balance=0 WHERE user_id=?',(uid,))
  self.post(self.b,'market/buy',{'id':lid},409)
  self.assertEqual(self.get(self.a,'mine')['projects'][0]['id'],pid)
  self.assertEqual(len(self.get(self.a,'market')['items']),1)

 def test_initial_upgrade_pauses_existing_offers_once(self):
  pid,lid=self.game_listing()
  with server.db() as c:c.execute('DELETE FROM exclusive_migrations')
  server.init()
  self.assertEqual(self.get(self.b,'market')['items'],[])
  self.post(self.a,'market/list',{'project_id':pid,'price':25,'credit':False})
  server.init()
  self.assertEqual(len(self.get(self.b,'market')['items']),1)
 def test_art_buyers_race(self):
  body={'fps':5,'frames':[['#abcdef']*256]}
  fid=self.post(self.a,'files',{'name':'Art race','kind':'art','body':body})['id']
  self.post(self.a,'art-market/list',{'id':fid,'price':20,'rights':True})
  lid=self.get(self.b,'art-market')['items'][0]['id']
  cookies=[x.get_cookie('trencod_session',domain='127.0.0.1').value for x in (self.b,self.c)]
  def buy(cookie):
   client=server.app.test_client();client.set_cookie('trencod_session',cookie,domain='127.0.0.1')
   return client.post('/api/art-market/buy',json={'id':lid},base_url=fixtures.BASE).status_code
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(buy,cookies))
  self.assertEqual(sorted(results),[200,409])
  self.assertEqual(self.get(self.a,'wallet')['balance'],120)
  self.assertEqual(sorted([self.get(x,'wallet')['balance'] for x in (self.b,self.c)]),[80,100])
