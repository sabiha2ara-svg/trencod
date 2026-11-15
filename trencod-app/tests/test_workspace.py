import unittest
import test_creators as fixtures
server=fixtures.server
class WorkspaceTests(unittest.TestCase):
 setUp=fixtures.CreatorTests.setUp
 post=fixtures.CreatorTests.post
 get=fixtures.CreatorTests.get
 def test_workspace_assets_are_served(self):
  for path in ['/workspace.js','/workspace.css']:
   with self.a.get(path,base_url=fixtures.BASE) as response:
    self.assertEqual(response.status_code,200)
 def test_source_tree_survives_save_publish_remix(self):
  import subprocess,pathlib
  root=pathlib.Path(__file__).resolve().parents[1]
  code="const w=require('./public/workspace.js');process.stdout.write(w.compile(w.load({html:'<h1>Hi</h1>',css:'body{color:red}',js:'window.test=true'})));"
  html=subprocess.check_output(['node','-e',code],cwd=root,text=True)
  pid=self.post(self.a,'save',{'title':'Folder game','html':html})['id']
  self.post(self.a,'publish',{'id':pid})
  clone=self.post(self.b,'remix',{'id':pid})['id']
  self.assertEqual(self.get(self.b,'project/'+clone)['project']['html'],html)
