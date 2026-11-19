import base64,io,json,unittest,wave
import test_creators as fixtures
import test_sprites
import server
from music import validate_music
BASE=fixtures.BASE
class MusicProjectsTests(unittest.TestCase):
 setUp=fixtures.CreatorTests.setUp
 post=fixtures.CreatorTests.post
 get=fixtures.CreatorTests.get
 def clip(self):
  f=io.BytesIO()
  with wave.open(f,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(b'\0\0'*800)
  self.raw=f.getvalue()
  return self.post(self.a,'music',{'name':'My loop.wav','data':base64.b64encode(self.raw).decode()})['clip']
 def test_upload_play_range_permissions_and_backup(self):
  clip=self.clip();mid=clip['id'];anonymous=server.app.test_client()
  r=anonymous.get('/media/music/'+mid,base_url=BASE);self.assertEqual(r.status_code,200);self.assertEqual(r.data,self.raw);self.assertEqual(r.mimetype,'audio/wav')
  r=anonymous.get('/media/music/'+mid,headers={'Range':'bytes=0-9'},base_url=BASE);self.assertEqual(r.status_code,206);self.assertEqual(r.data,self.raw[:10])
  self.assertEqual(len(self.get(self.a,'music')['clips']),1);self.assertEqual(self.get(self.b,'music')['clips'],[])
  self.get(anonymous,'music',401);self.post(anonymous,'music',{'name':'bad'},401)
  self.assertEqual(self.get(self.a,'my-backup')['music_clips'][0]['id'],mid)
  server.init();self.assertEqual(self.get(self.a,'music')['clips'][0]['id'],mid)
 def test_invalid_audio_and_quota(self):
  for data in ['bad%','',base64.b64encode(b'<html>not audio</html>').decode(),'a'*400004]:self.post(self.a,'music',{'name':'fake.mp3','data':data},400)
  self.clip()
  uid=self.get(self.a,'me')['user']['id']
  with server.db() as c:
   for n in range(19):c.execute('INSERT INTO music_clips VALUES(?,?,?,?,?,?,?)',(str(n).zfill(24),uid,'test','audio/wav',1,'AA==',0))
  self.post(self.a,'music',{'name':'extra.wav','data':base64.b64encode(self.raw).decode()},409)
 def test_music_survives_animation_visual_game_save_and_reload(self):
  clip=self.clip();music={'id':clip['id'],'volume':0.3,'loop':True}
  body={'frames':[['#123456']*256,['']*256],'fps':8,'music':music}
  f=self.post(self.a,'files',{'name':'Dancing dog','kind':'art','body':body})
  self.assertEqual(self.get(self.a,'files/'+f['id'])['file']['body'],body)
  scene=test_sprites.SpriteTests.scene(self);scene['music']=music
  v=self.post(self.a,'visual/save',{'title':'Musical game','scene':scene})
  self.assertIn('/media/music/'+clip['id'],v['code']['html']);self.assertIn('<audio controls',v['code']['html'])
  self.assertEqual(self.get(self.a,'visual/'+v['id'])['scene']['music'],music)
  self.assertFalse(self.get(self.a,'visual/'+v['id'])['code_changed'])
  self.post(self.a,'publish',{'id':v['id']});self.assertIn(clip['id'],self.get(self.b,'project/'+v['id'])['project']['html'])
  body['music']['id']='f'*24;self.post(self.a,'files',{'name':'Missing','kind':'art','body':body},400)
 def test_my_projects_classifies_existing_art_and_preserves_privacy(self):
  def art(name,frames):return self.post(self.a,'files',{'name':name,'kind':'art','body':{'frames':[['']*256]*frames,'fps':6}})
  pixel=art('Pixel',1);animation=art('Animation',2)
  vector=self.post(self.a,'files',{'name':'Vector','kind':'vector','body':{'type':'vector','name':'Vector','shapes':[]}})
  room=self.post(self.a,'rooms',{'name':'Our studio'})['id']
  team=self.post(self.a,'files',{'room_id':room,'name':'Team animation','kind':'art','body':{'frames':[['']*256]*3,'fps':6}})
  items=self.get(self.a,'creations')['creations'];types={x['id']:x['category'] for x in items}
  self.assertEqual(types[pixel['id']],'pixel');self.assertEqual(types[animation['id']],'animation');self.assertEqual(types[vector['id']],'vector')
  self.assertEqual(self.get(self.b,'creations')['creations'],[])
  invite=self.get(self.a,'rooms/'+room)['room']['invite'];self.post(self.b,'rooms/join',{'code':invite})
  self.assertEqual([x['id'] for x in self.get(self.b,'creations')['creations']],[team['id']])
  uid=self.get(self.b,'me')['user']['id'];self.post(self.a,'rooms/'+room+'/manage',{'action':'remove','user_id':uid})
  self.assertEqual(self.get(self.b,'creations')['creations'],[])
  server.init();self.assertEqual(len(self.get(self.a,'creations')['creations']),4)
 def test_music_metadata_rejects_active_content(self):
  for m in [{'id':'javascript:alert(1)'},{'id':'a'*24,'volume':float('nan')},{'id':'a'*24,'volume':1,'loop':'yes'}]:
   with self.assertRaises(ValueError):validate_music(m)
if __name__=='__main__':unittest.main()
