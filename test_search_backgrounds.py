import unittest
import test_creators as fixtures
import test_sprites
from discovery import validate_scene
class SearchBackgroundTests(unittest.TestCase):
 setUp=fixtures.CreatorTests.setUp
 post=fixtures.CreatorTests.post
 get=fixtures.CreatorTests.get
 def test_creators_without_games_and_case_and_at(self):
  for query in ['creatora','%40CREATORA']:
   result=self.get(self.c,'creators?q='+query)
   self.assertEqual([x['name'] for x in result['creators']],['CreatorA'])
   self.assertEqual(set(result['creators'][0]),{'id','name'})
  self.assertEqual(self.get(self.c,'creators?q=%25')['creators'],[])
 def test_background_save_reopen_preview(self):
  for theme in ['night','meadow','desert','snow','sunset','space','solid']:
   scene=test_sprites.SpriteTests.scene(self);scene['background']={'theme':theme,'color':'#123456'}
   result=self.post(self.a,'visual/save',{'title':'Background test','scene':scene})
   self.assertEqual(self.get(self.a,'visual/'+result['id'])['scene']['background'],scene['background'])
   self.assertIn('drawSceneBackground',result['code']['js'])
   self.assertIn('"theme": "'+theme+'"',result['code']['js'])
 def test_background_invalid(self):
  for bg in [{'theme':'evil'},{'theme':'solid','color':'url(x)'},'meadow']:
   scene=test_sprites.SpriteTests.scene(self);scene['background']=bg
   with self.assertRaises(ValueError):validate_scene(scene)
