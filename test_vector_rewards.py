import unittest,concurrent.futures,json,subprocess
import test_creators as fixtures
import server
from vectors import validate_vector
import test_sprites
class VectorRewardTests(unittest.TestCase):
 setUp=fixtures.CreatorTests.setUp
 post=fixtures.CreatorTests.post
 get=fixtures.CreatorTests.get
 def art(self):return {'type':'vector','name':'Dog','shapes':[{'kind':'ellipse','x':30,'y':40,'w':150,'h':160,'fill':'#abcdef','stroke':'#123456','sw':2,'rotation':10}]}
 def test_vector_save_reload_auth_revision_and_backup(self):
  body=self.art();f=self.post(self.a,'files',{'kind':'vector','name':'Dog','body':body})
  server.init();self.assertEqual(self.get(self.a,'files/'+f['id'])['file']['body'],body)
  self.get(self.b,'files/'+f['id'],404)
  self.post(self.b,'files',{'kind':'vector','name':'Stolen','body':body,**f},403)
  self.post(self.a,'files',{'kind':'vector','name':'New','body':body,**f})
  self.post(self.a,'files',{'kind':'vector','name':'Conflict','body':body,**f},409)
  self.assertTrue(any(x['id']==f['id'] for x in self.get(self.a,'my-backup')['personal_files']))
 def test_vector_validation_rejects_active_content_and_invalid_numbers(self):
  for key,value in [('fill','url(https://evil)'),('stroke','<script>'),('x',float('nan')),('w',0),('rotation',float('inf'))]:
   body=self.art();body['shapes'][0][key]=value
   with self.assertRaises(ValueError):validate_vector(body)
  body=self.art();body['shapes'][0]['kind']='image'
  self.post(self.a,'vector/validate',{'body':body},400)
  body=self.art();body['shapes'][0].update(onclick='alert(1)',href='https://evil')
  clean=validate_vector(body);self.assertNotIn('onclick',clean['shapes'][0]);self.assertNotIn('href',clean['shapes'][0])
 def test_vector_visual_game_export_and_legacy_scene(self):
  s=test_sprites.SpriteTests.scene(self);s['sprites']['dog']=self.art()
  r=self.post(self.a,'visual/save',{'title':'Vector world','scene':s})
  self.assertIn('function drawVectorSprite',r['code']['js']);self.assertEqual(self.get(self.a,'visual/'+r['id'])['scene'],s)
  self.assertFalse(self.get(self.a,'visual/'+r['id'])['code_changed'])
  legacy=test_sprites.SpriteTests.scene(self);r=self.post(self.a,'visual/preview',{'scene':legacy});self.assertNotIn('function drawVectorSprite',r['code']['js'])
 def test_fifty_library_sprites_validate(self):
  code="const fs=require('fs'),vm=require('vm');vm.runInThisContext(fs.readFileSync('public/vector-core.js','utf8'));console.log(JSON.stringify(vectorLibrary()))"
  library=json.loads(subprocess.check_output(['node','-e',code],text=True))
  self.assertEqual(len(library),50);self.assertEqual(len({x['name'] for x in library}),50)
  for art in library:self.assertTrue(validate_vector(art)['shapes'])
 def test_badge_claim_requirements_atomic_once_and_migration(self):
  self.post(self.a,'achievements/claim',{'key':'games:5'},409)
  self.post(self.a,'achievements/claim',{'key':'tc:50'},409)
  ids=[]
  for i in range(5):
   pid=self.post(self.a,'save',{'title':f'Game {i}','html':f'<h1>Game {i}</h1>'})['id'];ids.append(pid);self.post(self.a,'publish',{'id':pid})
  profile=self.get(self.a,'profile');badge=next(x for x in profile['badges'] if x['key']=='games:5');self.assertTrue(badge['earned']);self.assertEqual(badge['reward'],50)
  # No money moves until claimed. Retries and concurrent requests pay once.
  self.assertEqual(profile['balance'],100)
  cookie=self.a.get_cookie('trencod_session',domain='127.0.0.1').value
  def claim(_):
   c=server.app.test_client();c.set_cookie('trencod_session',cookie,domain='127.0.0.1')
   return c.post('/api/achievements/claim',json={'key':'games:5'},base_url=fixtures.BASE).get_json()['amount']
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:self.assertEqual(sum(pool.map(claim,range(4))),50)
  self.assertEqual(self.get(self.a,'wallet')['balance'],150)
  server.init();self.assertEqual(self.post(self.a,'achievements/claim',{'key':'games:5'})['amount'],0)
  self.post(self.b,'achievements/claim',{'key':'games:5'},409)
  # Unpublish/publish or remix does not earn another original release.
  self.post(self.a,'unpublish',{'id':ids[0]});self.post(self.a,'publish',{'id':ids[0]})
  self.assertEqual(self.get(self.a,'profile')['counts']['games'],5)
 def test_friend_reward_does_not_repeat_on_refollow(self):
  uid=self.get(self.a,'me')['user']['id'];other=self.get(self.b,'me')['user']['id']
  with server.db() as c:
   for i in range(5):
    f=f'friend{i}';c.execute('INSERT INTO users VALUES(?,?,?,?)',(f,f,'unused','unused'))
    c.execute('INSERT INTO follows VALUES(?,?,?)',(uid,f,1));c.execute('INSERT INTO follows VALUES(?,?,?)',(f,uid,1))
  self.assertEqual(self.post(self.a,'achievements/claim',{'key':'friends:5'})['amount'],20)
  self.post(self.a,'follow',{'id':'friend0','follow':False});self.post(self.a,'follow',{'id':'friend0','follow':True})
  self.assertEqual(self.post(self.a,'achievements/claim',{'key':'friends:5'})['amount'],0)
 def test_bot_prices(self):
  self.assertEqual({b['id']:b['price'] for b in self.get(self.a,'bots')['bots']},{'normal':50,'smart':150})
