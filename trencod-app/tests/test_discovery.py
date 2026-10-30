import unittest,time,json,concurrent.futures
from unittest.mock import patch
import test_creators as fixtures
import server,discovery
class DiscoveryTests(unittest.TestCase):
 setUp=fixtures.CreatorTests.setUp
 get=fixtures.CreatorTests.get
 post=fixtures.CreatorTests.post
 def game(self,c,title='Game',body='one'):
  pid=self.post(c,'save',{'title':title,'html':body,'css':'','js':''})['id'];self.post(c,'publish',{'id':pid});return pid
 def scene(self):return {'speed':200,'jump':450,'gravity':900,'objects':[{'type':'player','x':30,'y':350,'w':24,'h':30},{'type':'goal','x':750,'y':350,'w':30,'h':50},{'type':'platform','x':0,'y':420,'w':800,'h':30}]}
 def test_random_public_excludes_previous(self):
  pid=self.post(self.a,'save',{'title':'Private','html':'secret'})['id']
  for _ in range(8):self.assertNotEqual(self.get(self.a,'discover/random?exclude=star-dash')['project']['id'],'star-dash')
  self.assertNotEqual(self.get(self.b,'discover/random')['project']['id'],pid)
  with server.db() as c:c.execute('UPDATE projects SET published=0')
  self.get(self.a,'discover/random',404)
 def test_visual_validation_permissions_conflicts(self):
  scene=self.scene();self.assertIn('requestAnimationFrame',self.post(self.a,'visual/preview',{'scene':scene})['code']['js'])
  self.post(self.a,'visual/preview',{'scene':{**scene,'speed':999}},400)
  r=self.post(self.a,'visual/save',{'title':'Visual','scene':scene});pid=r['id']
  self.get(self.b,'visual/'+pid,404);self.post(self.b,'visual/save',{'id':pid,'title':'hack','scene':scene,'revision':1},403)
  self.post(self.a,'visual/save',{'id':pid,'title':'Visual','scene':scene,'revision':0},409)
  self.post(self.a,'publish',{'id':pid});self.assertFalse(self.get(self.a,'visual/'+pid)['code_changed'])
  self.post(self.a,'save',{'id':pid,'title':'Changed','html':'custom code','css':'','js':''})
  self.assertTrue(self.get(self.a,'visual/'+pid)['code_changed'])
  self.post(self.a,'visual/save',{'id':pid,'title':'Visual','scene':scene,'revision':1},409)
  self.post(self.a,'visual/save',{'id':pid,'title':'Visual','scene':scene,'revision':1,'overwrite':True})
  server.init();self.assertEqual(self.get(self.a,'visual/'+pid)['revision'],2)
 def test_tree_hides_private_titles(self):
  p=self.game(self.a);child=self.post(self.b,'remix',{'id':p})['id'];self.post(self.b,'publish',{'id':child})
  self.assertEqual(len(self.get(self.a,'remix-tree/'+child)['nodes']),2)
  self.post(self.a,'unpublish',{'id':p});r=self.get(self.b,'remix-tree/'+child);self.assertTrue(r['hidden_parent']);self.assertEqual(len(r['nodes']),1)
  self.get(self.b,'remix-tree/'+p,404)
 def test_playtest_feedback_upsert_and_closed(self):
  p=self.game(self.a);self.post(self.b,'playtests',{'id':p,'question':'hi'},403)
  self.post(self.a,'playtests',{'id':p,'question':'Is jumping clear?'})
  feedback={'id':p,'enjoyed':'Movement','stuck':'Second jump','suggestion':'Add a sign'}
  self.post(self.a,'playtests/feedback',feedback,400);self.post(self.b,'playtests/feedback',feedback)
  self.post(self.b,'playtests/feedback',{**feedback,'suggestion':'Add checkpoints'})
  r=self.get(self.a,'playtests/'+p);self.assertEqual(len(r['feedback']),1);self.assertEqual(r['feedback'][0]['suggestion'],'Add checkpoints')
  self.post(self.a,'playtests',{'id':p,'question':'done','open':False});self.post(self.b,'playtests/feedback',feedback,409)
 def test_jam_freeze_votes_deadline_winners(self):
  j=self.get(self.a,'jams')['jam'];p=self.game(self.a,'Jam entry','snapshot')
  eid=self.post(self.a,'jams/enter',{'id':p,'jam':j['id']})['id']
  self.post(self.a,'jams/enter',{'id':p,'jam':j['id']},409)
  self.post(self.a,'save',{'id':p,'title':'Updated','html':'changed','css':'','js':''})
  self.assertEqual(self.get(self.b,'jams/entry/'+eid)['code']['html'],'snapshot')
  self.post(self.a,'jams/vote',{'id':eid,'category':'fun'},400)
  self.post(self.b,'jams/vote',{'id':eid,'category':'fun'});self.post(self.b,'jams/vote',{'id':eid,'category':'fun'})
  self.assertEqual(self.get(self.a,'jams')['entries'][0]['votes']['fun'],1)
  with patch('discovery.now',return_value=j['ends']+1):
   self.post(self.b,'jams/vote',{'id':eid,'category':'art'},409)
   r=self.get(self.a,'jams?id='+j['id']);self.assertTrue(r['closed']);self.assertEqual(r['winners']['fun'],[eid])
 def test_devlogs_follow_feed_replies_permissions(self):
  a=self.get(self.a,'me')['user']['id'];p=self.game(self.a)
  did=self.post(self.a,'devlogs',{'title':'Progress','body':'Boss fight works','project_id':p})['id']
  self.assertEqual(self.get(self.b,'devlogs?feed=following')['posts'],[])
  self.post(self.b,'follow',{'id':a,'follow':True});self.assertEqual(len(self.get(self.b,'devlogs?feed=following')['posts']),1)
  self.post(self.b,'devlogs/reply',{'id':did,'body':'Nice!'});r=self.get(self.a,'devlogs')['posts'][0]['replies'][0]
  self.post(self.c,'devlogs/delete',{'reply':r['id']},403);self.post(self.a,'devlogs/delete',{'reply':r['id']})
  self.post(self.b,'devlogs/delete',{'id':did},403);self.post(self.a,'devlogs/delete',{'id':did})
  self.assertEqual(self.get(self.b,'devlogs')['posts'],[])
 def test_market_preview_frozen_and_art_sale_idempotent(self):
  p=self.game(self.a,body='listed version');self.post(self.a,'market/list',{'project_id':p,'price':50,'credit':False});lid=self.get(self.a,'market')['items'][0]['id']
  self.post(self.a,'save',{'id':p,'title':'Changed','html':'new version','css':'','js':''});self.assertEqual(self.get(self.b,'market/preview/'+lid)['code']['html'],'listed version')
  art={'frames':[['#112233']*256,['']*256],'fps':6};fid=self.post(self.a,'files',{'name':'Alien','kind':'art','body':art})['id']
  self.post(self.b,'art-market/list',{'id':fid,'price':20,'rights':True},403)
  self.post(self.a,'art-market/list',{'id':fid,'price':20,'rights':True});aid=self.get(self.b,'art-market')['items'][0]['id']
  cookie=self.b.get_cookie('trencod_session',domain='127.0.0.1').value
  def buy(_):
   c=server.app.test_client();c.set_cookie('trencod_session',cookie,domain='127.0.0.1');return c.post('/api/art-market/buy',json={'id':aid},base_url=fixtures.BASE).status_code
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:self.assertEqual(list(pool.map(buy,range(4))),[200]*4)
  self.assertEqual(self.get(self.a,'wallet')['balance'],120);self.assertEqual(self.get(self.b,'wallet')['balance'],80)
  self.post(self.a,'art-market/unlist',{'id':aid});self.assertEqual(self.get(self.b,'art-market')['owned'][0]['body'],art)
if __name__=='__main__':unittest.main(verbosity=2)
