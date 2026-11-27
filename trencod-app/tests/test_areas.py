import unittest
import test_creators as fixtures
from discovery import validate_scene
class AreaTests(unittest.TestCase):
 setUp=fixtures.CreatorTests.setUp
 post=fixtures.CreatorTests.post
 get=fixtures.CreatorTests.get
 def scene(self):
  return {'world_width':1600,'speed':220,'jump':450,'gravity':950,'objects':[{'type':'player','x':50,'y':100,'w':24,'h':32},{'type':'goal','x':1540,'y':370,'w':30,'h':50},{'type':'platform','x':900,'y':300,'w':120,'h':24,'movement':'patrol','move_speed':80}]}
 def test_roundtrip(self):
  s=self.scene();r=self.post(self.a,'visual/save',{'title':'Two areas','scene':s})
  self.assertEqual(self.get(self.a,'visual/'+r['id'])['scene'],s)
  self.assertIn('worldWidth',r['code']['js']);self.assertIn('carry',r['code']['js'])
 def test_bounds(self):
  for width in [0,801,4800,1600.0,True]:
   s=self.scene();s['world_width']=width
   with self.assertRaises(ValueError):validate_scene(s)
  s=self.scene();s['objects'][2]['x']=1550
  with self.assertRaises(ValueError):validate_scene(s)
