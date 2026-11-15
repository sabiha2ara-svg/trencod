"""Native PostgreSQL equivalents of the SQLite history and ownership guards."""

def trigger(c, name, table, events, timing, body):
    c.lock()
    c.raw.execute(f'''CREATE OR REPLACE FUNCTION {name}_fn() RETURNS trigger
    LANGUAGE plpgsql AS $trencod$ BEGIN {body} RETURN NEW; END; $trencod$''')
    c.raw.execute(f'DROP TRIGGER IF EXISTS {name} ON {table}')
    c.raw.execute(f'CREATE TRIGGER {name} {timing} {events} ON {table} FOR EACH ROW EXECUTE FUNCTION {name}_fn()')

def history_trigger(c):
    trigger(c, 'keep_project_version', 'projects', 'UPDATE', 'BEFORE', '''
    IF OLD.owner!='trencod-team' AND (OLD.title IS DISTINCT FROM NEW.title
       OR OLD.description IS DISTINCT FROM NEW.description OR OLD.html IS DISTINCT FROM NEW.html
       OR OLD.css IS DISTINCT FROM NEW.css OR OLD.js IS DISTINCT FROM NEW.js) THEN
      INSERT INTO project_versions(project_id,body,saved) VALUES(OLD.id,
        json_build_object('title',OLD.title,'description',OLD.description,'html',OLD.html,'css',OLD.css,'js',OLD.js)::text,OLD.updated);
      DELETE FROM project_versions WHERE project_id=OLD.id AND id NOT IN
        (SELECT id FROM project_versions WHERE project_id=OLD.id ORDER BY id DESC LIMIT 20);
    END IF;
    ''')

def exclusive_triggers(c):
    code = ' AND '.join(f"(s.body::jsonb->>'{k}')=NEW.{k}" for k in ('html','css','js'))
    for table, kind, match in [('projects','code',code),('studio_files','art','s.body=NEW.body')]:
        for event in ('INSERT','UPDATE'):
            guard = '(NEW.published=1 OR NEW.html!=OLD.html OR NEW.css!=OLD.css OR NEW.js!=OLD.js) AND ' if table=='projects' and event=='UPDATE' else ''
            trigger(c, f'exclusive_{table}_{event.lower()}', table, event, 'BEFORE', f'''
            IF {guard}EXISTS(SELECT 1 FROM exclusive_sales s WHERE s.kind='{kind}'
              AND s.buyer!=NEW.owner AND {match}) THEN
              RAISE EXCEPTION 'exclusive content belongs to another creator' USING ERRCODE='23514';
            END IF;''')
    for table, kind, licenses in [('listings','code','licenses'),('art_listings','art','art_licenses')]:
        trigger(c, f'exclusive_{table}', table, 'INSERT OR UPDATE', 'BEFORE', f'''
        IF NEW.active=1 AND (EXISTS(SELECT 1 FROM exclusive_sales s WHERE s.kind='{kind}' AND s.body=NEW.body)
          OR EXISTS(SELECT 1 FROM {licenses} x WHERE x.body=NEW.body)) THEN
          RAISE EXCEPTION 'exclusive content cannot be resold' USING ERRCODE='23514';
        END IF;''')
    trigger(c, 'exclusive_close_duplicates', 'exclusive_sales', 'INSERT', 'AFTER', '''
    IF NEW.kind='code' THEN
      UPDATE projects SET published=0 WHERE owner=NEW.seller AND id!=NEW.asset_id
       AND html=(NEW.body::jsonb->>'html') AND css=(NEW.body::jsonb->>'css') AND js=(NEW.body::jsonb->>'js');
      UPDATE listings SET active=0 WHERE body=NEW.body;
    ELSIF NEW.kind='art' THEN
      UPDATE art_listings SET active=0 WHERE body=NEW.body;
    END IF;
    ''')
