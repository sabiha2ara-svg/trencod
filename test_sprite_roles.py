import unittest
import test_creators as fixtures
import test_sprites
from discovery import validate_scene
class SpriteRoleTests(unittest.TestCase):
 setUp=fixtures.CreatorTests.setUp
 post=fixtures.CreatorTests.post
 get=fixtures.CreatorTests.get
 def test_role_motion_roundtrip_and_costume_change(self):
  s=test_sprites.SpriteTests.scene(self)
  s['objects'].extend([{'type':'pet','x':40,'y':40,'w':32,'h':32,'movement':'follow','move_speed':100,'sprite':'dog'},{'type':'enemy','x':500,'y':200,'w':32,'h':32,'movement':'patrol','move_speed':80,'sprite':'dog'},{'type':'decoration','x':200,'y':50,'w':32,'h':32,'movement':'still','move_speed':0}])
  r=self.post(self.a,'visual/save',{'title':'Roles test','scene':s})
  saved=self.get(self.a,'visual/'+r['id'])['scene'];self.assertEqual(saved,s)
  before=[dict(o) for o in saved['objects']];s['sprites']['dog']['frames'][0][0]='#abcdef'
  r2=self.post(self.a,'visual/save',{'id':r['id'],'revision':r['revision'],'title':'New costume','scene':s})
  self.assertEqual(self.get(self.a,'visual/'+r2['id'])['scene']['objects'],before)
  self.assertIn('moveActor',r2['code']['js'])
 def test_invalid_motion_or_duplicate_player(self):
  for fields in [{'movement':'fly'},{'movement':'chase'},{'move_speed':-1},{'move_speed':float('inf')}]:
   s=test_sprites.SpriteTests.scene(self);s['objects'][0].update(fields)
   with self.assertRaises(ValueError):validate_scene(s)
  s=test_sprites.SpriteTests.scene(self);s['objects'].append(dict(s['objects'][0]))
  with self.assertRaises(ValueError):validate_scene(s)
