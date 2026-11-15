import unittest,json
import test_creators as fixtures
from discovery import validate_scene
server=fixtures.server
class SpriteTests(unittest.TestCase):
 setUp=fixtures.CreatorTests.setUp
 post=fixtures.CreatorTests.post
 get=fixtures.CreatorTests.get
 def scene(self):
  return {'speed':220,'jump':450,'gravity':950,'sprites':{'dog':{'name':'Doggy','fps':6,'frames':[['#123456']+[None]*255]}},'objects':[{'type':'player','x':10,'y':10,'w':24,'h':32,'sprite':'dog'},{'type':'goal','x':740,'y':370,'w':30,'h':50}]}
 def test_sprite_saved_and_generated(self):
  s=self.scene();r=self.post(self.a,'visual/save',{'title':'Dog world','scene':s})
  self.assertEqual(self.get(self.a,'visual/'+r['id'])['scene'],s)
  self.assertIn('drawSpritePixels',r['code']['js'])
  self.assertIn('Doggy',r['code']['js'])
 def test_missing_sprite_rejected(self):
  s=self.scene();s['objects'][0]['sprite']='missing'
  with self.assertRaises(ValueError):validate_scene(s)
 def test_invalid_pixel_rejected(self):
  s=self.scene();s['sprites']['dog']['frames'][0][0]='url(javascript:bad)'
  with self.assertRaises(ValueError):validate_scene(s)
 def test_bad_animation_frames_rejected(self):
  for frame in [[],['#ffffff']*257]:
   s=self.scene();s['sprites']['dog']['frames']=[frame]
   with self.assertRaises(ValueError):validate_scene(s)
 def test_legacy_scene_without_sprites(self):
  s=self.scene();del s['sprites'];del s['objects'][0]['sprite'];self.assertEqual(validate_scene(s),s)
 def test_oversized_art_rejected(self):
  s=self.scene();s['sprites']={str(i):{'name':'Art','fps':6,'frames':[['#123456']*256 for _ in range(16)]} for i in range(4)}
  with self.assertRaises(ValueError):validate_scene(s)
 def test_sprite_script_served(self):
  with self.a.get('/sprites.js',base_url=fixtures.BASE) as response:self.assertEqual(response.status_code,200)
