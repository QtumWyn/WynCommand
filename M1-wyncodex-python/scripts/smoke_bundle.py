"""Launch the built executable against fresh and old disposable profiles."""
import json
import hashlib
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'tests')]
from test_library_update import make_services, snapshot
from wyncodex.database.connection import open_database
from wyncodex.database.migration_runner import run_migrations
from wyncodex.importers.models import ImportMode

executable = Path(sys.argv[1]).resolve()
results = []
with tempfile.TemporaryDirectory(prefix='wyncodex-bundle-smoke-') as directory:
    for mode, expected_entries in [('fresh', 1748), ('legacy', 1333)]:
        profile = Path(directory) / mode
        db = profile / 'data/WynCommand/WynCodex/wyncodex.db'
        if mode == 'legacy':
            conn = open_database(db)
            run_migrations(conn)
            importer, _ = make_services(conn)
            path = ROOT / 'src/wyncodex/resources/starter-library.json'
            importer.import_preview(importer.preview(path, ImportMode.STRICT_CREATE), ImportMode.STRICT_CREATE)
            conn.execute("UPDATE entries SET notes='Recipient annotation retained during schema upgrade' WHERE id=(SELECT min(id) FROM entries)")
            conn.execute('DROP INDEX idx_languages_kind')
            conn.execute('ALTER TABLE languages DROP COLUMN language_kind')
            for field in ('formality', 'dialect', 'related_concepts'):
                conn.execute('ALTER TABLE entries DROP COLUMN ' + field)
            for field in ('romanization', 'pronunciation'):
                conn.execute('ALTER TABLE examples DROP COLUMN ' + field)
            conn.execute('DELETE FROM schema_migrations WHERE version=7')
            conn.commit()
            legacy_before = snapshot(conn)
            conn.close()
        env = os.environ.copy()
        env.update(QT_QPA_PLATFORM='offscreen', XDG_DATA_HOME=str(profile / 'data'), XDG_CONFIG_HOME=str(profile / 'config'), XDG_CACHE_HOME=str(profile / 'cache'))
        process = subprocess.Popen([str(executable)], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 30
            ready = False
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    raise RuntimeError(f'Packaged app exited early ({process.returncode}): {stdout}\n{stderr}')
                if db.exists():
                    try:
                        with closing(sqlite3.connect(db.as_uri() + '?mode=ro', uri=True)) as conn:
                            ready = conn.execute('SELECT COUNT(*) FROM entries').fetchone()[0] == expected_entries and conn.execute('SELECT max(version) FROM schema_migrations').fetchone()[0] == 7
                    except sqlite3.Error:
                        pass
                if ready:
                    break
                time.sleep(0.1)
            if not ready:
                raise RuntimeError('Packaged app did not initialize its disposable database.')
            time.sleep(1)
            if process.poll() is not None:
                raise RuntimeError('Packaged app failed after database initialization.')
        finally:
            if process.poll() is None:
                process.terminate()
            stdout, stderr = process.communicate(timeout=10)
        if 'Traceback' in stderr:
            raise RuntimeError(stderr)
        with closing(sqlite3.connect(db.as_uri() + '?mode=ro', uri=True)) as conn:
            assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
            assert not conn.execute('PRAGMA foreign_key_check').fetchall()
            count = conn.execute('SELECT COUNT(*) FROM languages').fetchone()[0]
            assert count == (66 if mode == 'fresh' else 42)
            if mode == 'legacy':
                assert conn.execute('SELECT notes FROM entries ORDER BY id LIMIT 1').fetchone()[0] == 'Recipient annotation retained during schema upgrade'
                backups = list((db.parent / 'backups').glob('*.db'))
                assert len(backups) == 1
                with closing(sqlite3.connect(backups[0])) as backup:
                    assert snapshot(backup) == legacy_before
        results.append({'profile': mode, 'languages': count, 'entries': expected_entries, 'packaged_app_started': True, 'integrity': 'ok'})
output = ROOT / 'dist/release/SMOKE-TEST.json'
output.write_text(json.dumps(results, indent=2) + '\n')
checksums = output.parent / 'SHA256SUMS'
with checksums.open('a') as checksum_file:
    checksum_file.write(hashlib.sha256(output.read_bytes()).hexdigest() + '  ' + output.name + '\n')
print(json.dumps(results, indent=2))
