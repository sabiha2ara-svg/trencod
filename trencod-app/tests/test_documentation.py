import unittest,xml.etree.ElementTree as ET
import test_creators as fixtures
server=fixtures.server
class DocumentationTests(unittest.TestCase):
 setUp=fixtures.CreatorTests.setUp
 post=fixtures.CreatorTests.post
 get=fixtures.CreatorTests.get
 def test_public_pages_without_login(self):
  client=server.app.test_client()
  for path in ('about','privacy','security','market-guide','getting-started','changelog','community','status'):
   with client.get('/'+path,base_url=fixtures.BASE) as r:
    self.assertEqual(r.status_code,200);self.assertIn(b'<title>',r.data);self.assertIn(b'name="description"',r.data);self.assertIn(b'<main id="content">',r.data)
  self.assertEqual(client.get('/api/feedback',base_url=fixtures.BASE).status_code,401)
 def test_sitemap_public_urls_only_and_config(self):
  old=server.PUBLIC_URL
  try:
   server.PUBLIC_URL='https://trencod.example'
   r=self.a.get('/sitemap.xml',base_url=fixtures.BASE)
   self.assertEqual(r.status_code,200)
   urls=[x.text for x in ET.fromstring(r.data).iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
   self.assertIn('https://trencod.example/privacy',urls)
   self.assertFalse(any('/api/' in x or '#' in x or '/status' in x for x in urls))
   page=self.a.get('/privacy',base_url=fixtures.BASE).get_data(as_text=True)
   self.assertIn('rel="canonical" href="https://trencod.example/privacy"',page)
   robots=self.a.get('/robots.txt',base_url=fixtures.BASE).get_data(as_text=True)
   self.assertIn('Sitemap: https://trencod.example/sitemap.xml',robots)
   server.PUBLIC_URL=''
   self.assertEqual(self.a.get('/sitemap.xml',base_url=fixtures.BASE).status_code,503)
  finally:server.PUBLIC_URL=old

 def test_public_docs_stay_available_when_database_fails(self):
  from unittest.mock import patch
  with patch.object(server,'db',side_effect=RuntimeError('unavailable')):
   self.assertEqual(self.a.get('/security',base_url=fixtures.BASE).status_code,200)
   self.assertEqual(self.a.get('/help',base_url=fixtures.BASE).status_code,200)
   r=self.a.get('/healthz',base_url=fixtures.BASE)
   self.assertEqual(r.status_code,503);self.assertEqual(r.get_json()['error'],'Database unavailable')
