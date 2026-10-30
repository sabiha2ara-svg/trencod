"""Copy a previous installation's database without overwriting either installation."""
import sqlite3
from pathlib import Path

def main():
    import tkinter as tk
    from tkinter import filedialog,messagebox
    root=tk.Tk();root.withdraw()
    selected=filedialog.askdirectory(title='Choose your OLD trencod-app folder (the one containing data)')
    if not selected:return
    source=Path(selected)/'data'/'trencod.sqlite3'
    destination=Path(__file__).resolve().parent/'data'/'trencod.sqlite3'
    if not source.is_file():messagebox.showerror('Old data not found','Choose the old trencod-app folder containing data/trencod.sqlite3. Nothing was changed.');return
    if source.resolve()==destination.resolve():messagebox.showinfo('Already here','You selected this installation. Your accounts are already here.');return
    if destination.exists():messagebox.showerror('Existing accounts protected','This new folder already has a database. Nothing was overwritten. Use a freshly extracted ZIP for importing your old installation.');return
    try:
        import_database(source,destination)
        messagebox.showinfo('Creators restored','Accounts, games and wallets copied. Your old folder is unchanged. Now open START-TRENCOD.bat in the new folder.')
    except Exception as error:messagebox.showerror('Import did not finish',str(error)+'\nYour old installation is unchanged.')

def import_database(source,destination):
    import shutil
    destination.parent.mkdir(parents=True,exist_ok=True)
    temp=destination.with_suffix('.importing')
    created=False
    try:
        with sqlite3.connect(source.resolve().as_uri()+'?mode=ro',uri=True) as old,sqlite3.connect(temp) as new:
            old.backup(new)
            if new.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Database check failed.')
            if not new.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchone():raise ValueError('This is not a Trencod user database.')
        with destination.open('xb') as out:
            created=True
            with temp.open('rb') as data:shutil.copyfileobj(data,out)
    except Exception:
        if created:destination.unlink(missing_ok=True)
        raise
    finally:temp.unlink(missing_ok=True)

if __name__=='__main__':main()
