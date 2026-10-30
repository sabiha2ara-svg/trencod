import unittest,time,concurrent.futures
from datetime import date,timedelta
from unittest.mock import patch
import test_creators as fixtures
import server,community
class CommunityTests(unittest.TestCase):
 setUp=fixtures.CreatorTests.setUp
 get=fixtures.CreatorTests.get
 post=fixtures.CreatorTests.post
 def uid(self,c):return self.get(c,'me')['user']['id']
 def circle(self,n):
  uid=self.uid(self.a)
  with server.db() as c:
   for i in range(n):
    fid='fixture-friend-'+str(i)
    c.execute('INSERT OR IGNORE INTO users VALUES(?,?,?,?)',(fid,'Friend'+str(i),'unused','unused'))
    c.execute('INSERT OR IGNORE INTO follows VALUES(?,?,?)',(uid,fid,time.time()));c.execute('INSERT OR IGNORE INTO follows VALUES(?,?,?)',(fid,uid,time.time()))
 def earned(self,r):return {b['key'] for b in r['badges'] if b['earned']}
 def test_coin_badges_exclude_gifts_and_survive_spending(self):
  uid=self.uid(self.a);r=self.get(self.a,'profile');self.assertEqual(r['balance'],100);self.assertNotIn('tc:50',self.earned(r))
  with server.db() as c:
   for amount,reason,key in [(5000,'Milestone bonus','fixture-bonus'),(5000,'Trencod Support: demo','fixture-support'),(5000,'Sale: actual game','fixture-sale'),(-5000,'Bought a bot','fixture-spend')]:
    c.execute('INSERT INTO ledger(user_id,amount,reason,event_key,created) VALUES(?,?,?,?,?)',(uid,amount,reason,key,time.time()))
  r=self.get(self.a,'profile');self.assertEqual(r['counts']['tc'],5000);self.assertEqual(r['eligible_balance'],0)
  self.assertEqual({b for b in self.earned(r) if b.startswith('tc:')},{'tc:'+str(x) for x in [50,100,200,500,1000,2000,5000]})
  server.init();self.assertIn('tc:5000',self.earned(self.get(self.a,'profile')))
 def test_bonus_only_no_badges(self):
  uid=self.uid(self.a)
  with server.db() as c:
   c.execute('INSERT INTO ledger(user_id,amount,reason,event_key,created) VALUES(?,?,?,?,?)',(uid,9000,'Trencod Support: demo','support:fixture',time.time()))
   c.execute('INSERT INTO tp_rewards VALUES(?,?,?,?)',(uid,'2026-01-01',5000,'bonus'))
  r=self.get(self.a,'profile');self.assertEqual(r['tp'],5000);self.assertEqual(r['counts']['tc'],0);self.assertEqual(self.earned(r),set())
 def test_follow_mutual_thresholds_and_public_privacy(self):
  a,b=self.uid(self.a),self.uid(self.b)
  self.post(self.a,'follow',{'id':a,'follow':True},400)
  self.post(self.a,'follow',{'id':b,'follow':True});self.assertEqual(self.get(self.a,'profile')['friends'],0)
  self.post(self.b,'follow',{'id':a,'follow':True});self.assertEqual(self.get(self.a,'profile')['friends'],1)
  self.post(self.a,'follow',{'id':b,'follow':True});self.assertEqual(len(self.get(self.a,'profile')['following']),1)
  self.circle(5);self.assertIn('friends:6',self.earned(self.get(self.a,'profile')))
  self.circle(150);r=self.get(self.a,'profile');self.assertTrue({'friends:6','friends:10','friends:40','friends:80','friends:150'}<=self.earned(r))
  public=self.get(self.b,'profile/'+a)
  for key in ('balance','eligible_balance','tp','activity_days','password','salt'):self.assertNotIn(key,public)
  self.post(self.a,'follow',{'id':b,'follow':False});self.assertIn('friends:150',self.earned(self.get(self.a,'profile')))
 def test_streak_rollover_and_daily_tp_limit(self):
  self.circle(6);first=date(2026,10,1);pid=None
  for i in range(3):
   with patch('community.today',return_value=first+timedelta(days=i)):
    d={'id':pid,'title':'Game','html':'<h1>'+str(i)+'</h1>','css':'','js':''}
    pid=self.post(self.a,'save',d)['id'];d['id']=pid
    self.post(self.a,'save',d) # unchanged retry
    self.post(self.a,'files',{'name':'Sprite','kind':'art','body':{'fps':6,'frames':[['#112233']*256]}})
    r=self.get(self.a,'profile');self.assertEqual(r['tp'],50*(i+1));self.assertEqual(r['streak'],i+1)
  with patch('community.today',return_value=first+timedelta(days=5)):
   r=self.get(self.a,'profile');self.assertEqual(r['streak'],0);self.assertEqual(r['best_streak'],3);self.assertIn('streak:3',self.earned(r))
   self.post(self.a,'save',d);self.assertFalse(self.get(self.a,'profile')['reward_today'])
   self.post(self.a,'save',{**d,'html':'new work'});self.assertEqual(self.get(self.a,'profile')['streak'],1)
 def test_concurrent_reward_and_game_dedup(self):
  self.circle(6);cookie=self.a.get_cookie('trencod_session',domain='127.0.0.1').value
  def save(i):
   c=server.app.test_client();c.set_cookie('trencod_session',cookie,domain='127.0.0.1')
   return c.post('/api/save',json={'title':'same','html':'same code'},base_url=fixtures.BASE).get_json()['id']
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:ids=list(pool.map(save,range(4)))
  for pid in ids:self.post(self.a,'publish',{'id':pid})
  r=self.get(self.a,'profile');self.assertEqual(r['tp'],50);self.assertEqual(r['counts']['games'],1)
  self.post(self.a,'unpublish',{'id':ids[0]});self.assertIn('games:1',self.earned(self.get(self.a,'profile')))
 def test_comments_permissions_reports_and_plain_text(self):
  p=self.post(self.a,'save',{'title':'Game','html':'Play'})['id'];self.post(self.b,'comments',{'project_id':p,'body':'hi'},404)
  self.post(self.a,'publish',{'id':p});body='<img src=x onerror=alert(1)>'
  self.post(self.b,'comments',{'project_id':p,'body':body});r=self.get(self.a,'comments/'+p)['comments'][0];self.assertEqual(r['body'],body)
  self.post(self.b,'comments',{'project_id':p,'body':body},409)
  self.post(self.c,'comments/delete',{'id':r['id']},403);self.post(self.c,'comments/report',{'id':r['id'],'reason':'test'})
  self.post(self.a,'comments/delete',{'id':r['id']});self.assertEqual(self.get(self.b,'comments/'+p)['comments'],[])
 def test_support_budget_no_fake_customer_or_badge(self):
  p=self.post(self.a,'save',{'title':'Unsold','html':'Real code'})['id'];self.post(self.a,'publish',{'id':p});self.post(self.a,'market/list',{'project_id':p,'price':50,'credit':True})
  self.get(self.b,'market');self.assertEqual(self.get(self.a,'wallet')['balance'],100)
  with server.db() as c:
   c.execute('UPDATE support_budget SET enabled=1,balance=80');c.execute('UPDATE projects SET updated=? WHERE id=?',(time.time()-8*86400,p))
  for i in range(3):self.get(self.b,'market')
  self.assertEqual(self.get(self.a,'wallet')['balance'],150)
  with server.db() as c:
   self.assertEqual(c.execute('SELECT balance FROM support_budget').fetchone()[0],30)
   self.assertEqual(c.execute('SELECT COUNT(*) FROM support_purchases').fetchone()[0],1)
   self.assertEqual(c.execute('SELECT COUNT(*) FROM licenses').fetchone()[0],0)
  self.assertNotIn('tc:50',self.earned(self.get(self.a,'profile')))
if __name__=='__main__':unittest.main(verbosity=2)
