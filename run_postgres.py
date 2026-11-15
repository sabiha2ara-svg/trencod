"""Run integration tests in a DISPOSABLE PostgreSQL database.
Usage: TRENCOD_TEST_DATABASE_URL=postgresql://... python tests/run_postgres.py
Never point this at production: it recreates the public schema for each test.
"""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
url=os.environ.get('TRENCOD_TEST_DATABASE_URL')
if not url:raise SystemExit('Set TRENCOD_TEST_DATABASE_URL to a disposable local test database.')
os.environ['DATABASE_URL']=url
import psycopg
import server

def reset():
 with server.db() as c:
  c.raw.execute('DROP SCHEMA public CASCADE');c.raw.execute('CREATE SCHEMA public')

reset()
import test_creators, test_server
for cls in (test_creators.CreatorTests,test_server.FlowTests):
 old=cls.setUp
 def setup(self,original=old):reset();original(self)
 cls.setUp=setup
# Other modules alias the patched fixture setUp on import.
suite=unittest.defaultTestLoader.discover(str(Path(__file__).parent))
# Local SQLite-file copying has a separate SQLite test; all API tests run on PG.
def flatten(s):
 for t in s:
  if isinstance(t,unittest.TestSuite):yield from flatten(t)
  elif not t.id().endswith('test_upgrade_copies_without_overwrite'):yield t
suite=unittest.TestSuite(flatten(suite))
r=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not r.wasSuccessful())
