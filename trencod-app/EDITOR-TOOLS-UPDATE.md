# Trencod 0.14.2 — Find, Replace and Duplicate

Code editor toolbar:
- Find & Replace: opens an inline panel for the selected file. Ctrl+F / Cmd+F inside the editor opens it too.
- Find next: selects the next exact, case-sensitive match and wraps at the end.
- Replace selected: replaces the selected match. If none is selected, first selects the next match; click again to replace.
- Replace all: asks confirmation with occurrence count. Literal text only; this also changes comments and strings, not just variable names.
- Undo replacement: restores the last replacement only while that same file still has the replacement result. Later typing disables it to protect newer changes.
- Duplicate file: creates a sibling such as main-copy.py or main-copy-2.py. Original stays unchanged. Update imports/links yourself if needed.

Replacements and duplicates enter the existing unsaved draft flow. Press Save to keep them in My projects. Existing source size/file-count limits apply. Copying index.html creates an editing copy, not an additional website entry point.

Includes the Python/mobile fixes from 0.14.1 and ANIMATION-IN-CODE.md.

Validation: literal matching (including punctuation and Unicode), replacements, stale-match rejection, duplicate naming, source immutability, size rejection, save/reopen roundtrip, Python regression and workspace compilation tests pass. Browser visual checks were unavailable in this environment.

UPLOAD CAREFULLY:
1. Extract this ZIP.
2. Open the existing trencod-app folder on GitHub.
3. Add file > Upload files.
4. Upload the CONTENTS of the extracted trencod-app folder into it.
5. Commit, then deploy the latest commit in Render with Root Directory trencod-app.
Do not create trencod-app/trencod-app. Keep your Render environment variables.
