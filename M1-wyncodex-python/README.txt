WynCodex 0.2.0-alpha

A desktop reference browser for programming and natural languages.
Public library 2026.11.05: 66 languages, 280 categories, 110 packages,
1,748 entries, 1,706 examples, 95 arguments, and 33 Assembly tags.

UPGRADING ON KUBUNTU

1. Download WynCodex-v0.2.0-alpha-linux-x86_64.zip from:
   https://github.com/QtumWyn/WynCommand/releases/tag/v0.2.0-alpha
2. Finish any open edits and close the older WynCodex window.
3. Extract the entire archive into a new application folder. Keep its _internal
   folder beside the WynCodex executable. Run that new WynCodex executable.
4. For an existing library, select UPDATE LIBRARY > Use bundled library.
   Review the additions and confirm. Existing entries/examples remain intact.
   A new profile receives the bundled collection automatically.
5. Point any desktop shortcut at the new executable after checking the update.

Application files and your reference database are stored separately. On Kubuntu,
the normal database is ~/.local/share/WynCommand/WynCodex/wyncodex.db.
Do not delete or replace that file to upgrade. Backups are saved in the adjacent
backups directory before a schema upgrade or library import. These are complete
SQLite backups, including committed WAL data.

The Linux release workflow builds on Ubuntu 22.04 x86_64 with Python 3.11 for
Kubuntu/Ubuntu 22.04 and newer. Qt still needs desktop graphics/system libraries.
Windows, macOS, ARM and older distributions are not tested by this release.
The executable does not require a separately installed Python.

LIBRARY UPDATES

UPDATE LIBRARY is available in Programming and Natural Languages.
Use bundled library applies the collection included with this app version.
Open downloaded library accepts the separate versioned public-library JSON.
Use that option for later content-only downloads. The older IMPORT JSON button
remains available for legacy programming-reference packs.

The updater adds missing languages, categories, packages, entries, examples,
arguments, tags, and relationships. It preserves nested members, natural-language
fields, and Assembly track tags. It never replaces your existing text or deletes
your records. If an incoming record differs, your version stays and the preview's
details name the fields that differ. Missing examples can be added to an entry
that already exists. Legacy records are matched by scoped keys/content; imported
identities are remembered so repeated imports do not multiply records. Previously
imported records you delete stay deleted.

If you edited both the title and code of an old example before its first library
update, the original published example may be added alongside your local version.
Both are retained; repeating the same update will not add more copies.

This button updates reference content. It does not download or replace the app
executable. Obtain application updates from the Releases page.

RECOVERY

Close all WynCodex windows before restoring a database. Retain the current database
and any -wal/-shm files as a separate recovery copy; restore a verified backup to
the normal database path while the application is closed. Use the app version
matching that backup's schema or a newer version. Never copy a database over an
open application. Keep a backup before any manual recovery.

SOURCE AND BUILD

Source: https://github.com/QtumWyn/WynCommand/tree/main/M1-wyncodex-python
Python >=3.11. In an isolated virtual environment:

  python -m pip install -r requirements-build.txt
  PYTHONPATH=src QT_QPA_PLATFORM=offscreen python -B -m unittest discover -s tests -v
  PYTHONPATH=src python scripts/build_release.py
  PYTHONPATH=src QT_QPA_PLATFORM=offscreen python scripts/smoke_bundle.py dist/WynCodex/WynCodex

The Linux workflow builds on Ubuntu 22.04, tests an older starter-library upgrade,
tests local edit preservation/rollback/repeated imports, and launches the packaged
app using isolated temporary data/config directories.

The public reference package is a logical content export. It contains no live
database, credentials, local configuration, or application history. Code examples
retain their stated toolchain versions and execution limitations; not every
third-party framework example has been executed.
