"""Exclusive marketplace guards. Exact content matching is not plagiarism detection."""
import json

def migrate(c):
    c.execute('CREATE TABLE IF NOT EXISTS exclusive_migrations(version INTEGER PRIMARY KEY)')
    if not c.execute('SELECT 1 FROM exclusive_migrations WHERE version=1').fetchone():
        # Old sellers accepted non-exclusive terms: require a fresh listing.
        c.execute('UPDATE listings SET active=0')
        c.execute('UPDATE art_listings SET active=0')
        c.execute('INSERT INTO exclusive_migrations VALUES(1)')
    c.executescript('''
    UPDATE listings SET active=0 WHERE id IN (SELECT listing_id FROM licenses)
      OR id IN (SELECT listing_id FROM support_purchases);
    UPDATE art_listings SET active=0 WHERE id IN (SELECT listing_id FROM art_licenses);
    ''')
    if getattr(c,'dialect',None)=='postgres':
        from postgres_schema import exclusive_triggers
        exclusive_triggers(c)
        return
    # Exact code comparison ignores JSON key order, not edits to the actual code.
    code=" AND ".join(f"json_extract(s.body,'$.{k}')=NEW.{k}" for k in ('html','css','js'))
    for table,kind,match,owner in [('projects','code',code,'owner'),('studio_files','art','s.body=NEW.body','owner')]:
        for event in ('INSERT','UPDATE'):
            guard="(NEW.published=1 OR NEW.html!=OLD.html OR NEW.css!=OLD.css OR NEW.js!=OLD.js) AND " if table=='projects' and event=='UPDATE' else ''
            c.execute(f'''CREATE TRIGGER IF NOT EXISTS exclusive_{table}_{event.lower()}
            BEFORE {event} ON {table}
            WHEN {guard}EXISTS(SELECT 1 FROM exclusive_sales s WHERE s.kind='{kind}'
              AND s.buyer!=NEW.{owner} AND {match})
            BEGIN SELECT RAISE(ABORT,'exclusive content belongs to another creator'); END''')
    for table,kind in [('listings','code'),('art_listings','art')]:
        for event in ('INSERT','UPDATE'):
            c.execute(f'''CREATE TRIGGER IF NOT EXISTS exclusive_{table}_{event.lower()}
            BEFORE {event} ON {table} WHEN NEW.active=1 AND (
              EXISTS(SELECT 1 FROM exclusive_sales s WHERE s.kind='{kind}' AND s.body=NEW.body)
              OR EXISTS(SELECT 1 FROM {'licenses' if kind=='code' else 'art_licenses'} x WHERE x.body=NEW.body))
            BEGIN SELECT RAISE(ABORT,'exclusive content cannot be resold'); END''')
    # A seller may have previously saved another identical project. Remove its
    # public availability atomically with the sale, without deleting its record.
    c.executescript('''
    CREATE TRIGGER IF NOT EXISTS exclusive_close_code_duplicates AFTER INSERT ON exclusive_sales
    WHEN NEW.kind='code' BEGIN
      UPDATE projects SET published=0 WHERE owner=NEW.seller AND id!=NEW.asset_id
       AND html=json_extract(NEW.body,'$.html') AND css=json_extract(NEW.body,'$.css') AND js=json_extract(NEW.body,'$.js');
      UPDATE listings SET active=0 WHERE body=NEW.body;
    END;
    CREATE TRIGGER IF NOT EXISTS exclusive_close_art_duplicates AFTER INSERT ON exclusive_sales
    WHEN NEW.kind='art' BEGIN
      UPDATE art_listings SET active=0 WHERE body=NEW.body;
    END;
    ''')
