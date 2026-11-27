import os,unittest
from unittest.mock import patch
import test_creators as fixtures
server=fixtures.server
class SupportTests(unittest.TestCase):
 setUp=fixtures.CreatorTests.setUp
 post=fixtures.CreatorTests.post
 get=fixtures.CreatorTests.get
 def test_private_reports_and_owner_reply(self):
  report={'category':'studio','subject':'Save issue','body':'Open Studio and save: error shown.'}
  anon=server.app.test_client();self.post(anon,'feedback',report,401)
  tid=self.post(self.a,'feedback',report)['id']
  self.assertEqual(self.get(self.b,'feedback')['tickets'],[])
  self.post(self.b,'feedback/'+tid+'/reply',{'status':'resolved','reply':'x'},403)
  uid=self.get(self.b,'me')['user']['id']
  with patch.dict(os.environ,{'TRENCOD_SUPPORT_ADMINS':uid}):
   self.assertEqual(self.get(self.b,'feedback')['tickets'][0]['id'],tid)
   self.post(self.b,'feedback/'+tid+'/reply',{'status':'investigating','reply':'Checking this save.'})
  server.init()
  self.assertEqual(self.get(self.a,'feedback')['tickets'][0]['reply'],'Checking this save.')
  self.assertEqual(self.a.get('/help',base_url=fixtures.BASE).status_code,200)
 def test_report_validation_and_limit(self):
  self.post(self.a,'feedback',{'category':'bad','subject':'x','body':'x'},400)
  self.post(self.a,'feedback',{'category':'bug','subject':'   ','body':'x'},400)
  for _ in range(5):self.post(self.a,'feedback',{'category':'bug','subject':'x','body':'x'})
  self.post(self.a,'feedback',{'category':'bug','subject':'x','body':'x'},429)
 def test_changed_sale_terms_do_not_charge(self):
  pid=self.post(self.a,'save',{'title':'Sale','html':'new unique game'})['id']
  self.post(self.a,'publish',{'id':pid})
  self.post(self.a,'market/list',{'project_id':pid,'price':25,'credit':False})
  lid=self.get(self.b,'market')['items'][0]['id']
  self.post(self.a,'market/list',{'project_id':pid,'price':40,'credit':True})
  self.post(self.b,'market/buy',{'id':lid,'expected_price':25,'expected_credit':False},409)
  self.assertEqual(self.get(self.b,'wallet')['balance'],100)
  self.assertEqual(self.get(self.a,'mine')['projects'][0]['id'],pid)
  result=self.post(self.b,'market/buy',{'id':lid,'expected_price':40,'expected_credit':True})
  self.assertEqual(result['id'],pid)
