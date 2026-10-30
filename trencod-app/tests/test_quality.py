import unittest,time
import test_creators as fixtures
import server
class QualityTests(unittest.TestCase):
 setUp=fixtures.CreatorTests.setUp
 get=fixtures.CreatorTests.get
 post=fixtures.CreatorTests.post
 def game(self):
  p=self.post(self.a,'save',{'title':'First','html':'first'})['id'];self.post(self.a,'publish',{'id':p});return p
 def test_queue_private_idempotent_hidden_games(self):
  p=self.game()
  for _ in range(2):self.post(self.b,'play-later',{'id':p,'saved':True})
  self.assertEqual(len(self.get(self.b,'play-later')['projects']),1)
  self.assertEqual(self.get(self.c,'play-later')['projects'],[])
  self.assertNotIn('html',self.get(self.b,'play-later')['projects'][0])
  self.post(self.a,'unpublish',{'id':p});self.assertEqual(self.get(self.b,'play-later')['projects'],[])
  self.post(self.b,'play-later',{'id':p,'saved':True},404)
  self.post(self.b,'play-later',{'id':p,'saved':False})
 def test_history_restore_permissions_conflicts_and_undo(self):
  p=self.game();self.assertEqual(self.get(self.a,'history/'+p)['versions'],[])
  self.post(self.a,'save',{'id':p,'title':'Second','html':'second'})
  h=self.get(self.a,'history/'+p);v=h['versions'][0]['id'];self.assertEqual(self.get(self.a,f'history/{p}/{v}')['code']['html'],'first')
  self.get(self.b,'history/'+p,404);self.get(self.b,f'history/{p}/{v}',404)
  self.post(self.b,'history/restore',{'id':p,'version':v,'updated':h['updated']},404)
  self.post(self.a,'history/restore',{'id':p,'version':v,'updated':0},409)
  self.post(self.a,'history/restore',{'id':p,'version':v,'updated':h['updated']})
  self.assertFalse(self.get(self.a,'project/'+p)['project']['published']);self.get(self.b,'project/'+p,404)
  restored=self.get(self.a,'history/'+p);undo=restored['versions'][0]['id']
  self.assertEqual(self.get(self.a,f'history/{p}/{undo}')['code']['html'],'second')
  self.post(self.a,'history/restore',{'id':p,'version':undo,'updated':restored['updated']})
  self.assertEqual(self.get(self.a,'project/'+p)['project']['html'],'second')
 def test_history_retention_and_upgrade(self):
  p=self.game()
  for n in range(24):self.post(self.a,'save',{'id':p,'title':'Game','html':str(n)})
  h=self.get(self.a,'history/'+p);self.assertEqual(len(h['versions']),20)
  self.post(self.a,'save',{'id':p,'title':'Game','html':'23'})
  self.assertEqual(self.get(self.a,'history/'+p)['versions'],h['versions'])
  server.init();self.assertEqual(len(self.get(self.a,'history/'+p)['versions']),20)
 def test_inbox_visibility_mark_read_cutoff(self):
  p=self.game();uid=self.get(self.a,'me')['user']['id'];self.post(self.b,'follow',{'id':uid,'follow':True})
  self.post(self.b,'comments',{'project_id':p,'body':'Nice game'})
  r=self.get(self.a,'inbox');self.assertEqual(r['unread'],2)
  self.assertEqual(self.get(self.c,'inbox')['events'],[])
  self.post(self.a,'inbox/read',{'until':time.time()+500},400)
  self.post(self.a,'inbox/read',{'until':r['until']})
  self.assertEqual(self.get(self.a,'inbox')['unread'],0)
  self.post(self.c,'comments',{'project_id':p,'body':'Hello'})
  self.post(self.a,'inbox/read',{'until':r['until']})
  self.assertEqual(self.get(self.a,'inbox')['unread'],1)
  self.post(self.a,'unpublish',{'id':p})
  self.assertEqual(len(self.get(self.a,'inbox')['events']),1)
 def test_guest_denied(self):
  guest=server.app.test_client()
  for path in ('play-later','history/star-dash','inbox'):self.get(guest,path,401)
  for path,body in [('play-later',{'id':'star-dash','saved':True}),('inbox/read',{'until':0}),('history/restore',{'id':'star-dash','version':1})]:self.post(guest,path,body,401)
if __name__=='__main__':unittest.main()
