# Trencod 0.14.1 — Python and mobile fixes

Python: select a .py file, enter input() answers under the editor (one answer per line), then Run Python. Missing answers produce EOFError; add more lines and rerun. Inputs reset when leaving the editor; they are not published.

Python now receives project TXT/JSON resources as well as Python modules. Relative paths start at the project root. Imports can resolve both the project root and selected script folder. Packages bundled by Pyodide are loaded from imports; arbitrary pip packages are not automatically installed. First startup and additional packages require internet. Desktop GUI, pygame, and Python web servers remain unsupported. Runtime-created files are temporary; Save preserves editor source, not generated Python files. Execution still has a 15-second limit and Stop control.

Mobile: horizontally scrollable navigation, larger touch targets, full-width editor panels, compact file list, wrapping tool buttons, readable form text, contained dialogs, and automatic preview scrolling after Run. Maximize supports scrolling and a usable preview height.

Validation: Python worker simulation covers input queue/EOF, resource files, root imports, package loading, Stop, source escaping and save roundtrip. Related source/vector/sprite/music tests run separately. Actual Pyodide CDN execution and mobile browser rendering were not verified: local Chromium could not launch due to an environment socket restriction.

Deploy: extract ZIP, update existing trencod-app files in GitHub, commit, deploy latest commit on Render, hard refresh. Keep DATABASE_URL and other Render environment variables. This ZIP has no account database or secrets.
