import copy
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from uuid import uuid4

from wyncodex.database.connection import open_database
from wyncodex.database.migration_runner import run_migrations
from wyncodex.importers.models import ImportMode
from wyncodex.services.library_update_service import (
    ORDER, LibraryUpdateService, content_hash, load_package, validate_package, prepare_database,
)


def make_services(conn):
    from wyncodex.repositories.language_repository import LanguageRepository
    from wyncodex.repositories.category_repository import CategoryRepository
    from wyncodex.repositories.package_repository import PackageRepository
    from wyncodex.repositories.entry_repository import EntryRepository
    from wyncodex.repositories.argument_repository import ArgumentRepository
    from wyncodex.repositories.example_repository import ExampleRepository
    from wyncodex.services.language_service import LanguageService
    from wyncodex.services.category_service import CategoryService
    from wyncodex.services.package_service import PackageService
    from wyncodex.services.entry_service import EntryService
    from wyncodex.importers.json_importer import JsonImportService
    lr, cr, pr = LanguageRepository(conn), CategoryRepository(conn), PackageRepository(conn)
    er, ar, xr = EntryRepository(conn), ArgumentRepository(conn), ExampleRepository(conn)
    ls, cs, ps = LanguageService(lr), CategoryService(cr, lr), PackageService(pr, cr)
    es = EntryService(er, cr, pr, ar, xr)
    return JsonImportService(conn, ls, cs, ps, es), (ls, cs, ps, es)


def snapshot(conn):
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    return {table: [tuple(r) for r in conn.execute(f'SELECT * FROM {table} ORDER BY rowid')] for table in tables}


class LibraryUpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = load_package()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.conn = open_database(Path(self.temp.name) / 'profile' / 'wyncodex.db')
        run_migrations(self.conn)
        self.service = LibraryUpdateService(self.conn)

    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()

    def seal(self, doc):
        doc['content_sha256'] = content_hash(doc['records'])
        return doc

    def seed_legacy(self):
        from importlib.resources import files
        importer, _ = make_services(self.conn)
        path = Path(str(files('wyncodex.resources').joinpath('starter-library.json')))
        importer.import_preview(importer.preview(path, ImportMode.STRICT_CREATE), ImportMode.STRICT_CREATE)

    def test_fresh_profile_exact_counts_and_repeat_is_noop(self):
        before = snapshot(self.conn)
        preview = self.service.preview(self.document)
        self.assertEqual(snapshot(self.conn), before)
        self.assertFalse((Path(self.temp.name) / 'profile/backups').exists())
        result = self.service.apply(self.document)
        expected = {table: len(rows) for table, rows in self.document['records'].items() if rows}
        self.assertEqual(result.added, expected)
        self.assertEqual(result.added, preview.added)
        self.assertEqual(result.differences, [])
        self.assertEqual(result.skipped, [])
        for table in ORDER:
            self.assertEqual(self.conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0], len(self.document['records'][table]))
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM languages WHERE language_kind='natural'").fetchone()[0], 23)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM entries WHERE parent_entry_id IS NOT NULL').fetchone()[0], 198)
        after = snapshot(self.conn)
        self.assertEqual(self.service.apply(self.document).added_total, 0)
        self.assertEqual(snapshot(self.conn), after)
        self.assertEqual(self.conn.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        self.assertEqual(self.conn.execute('PRAGMA foreign_key_check').fetchall(), [])
        self.assertTrue(result.backup.is_file())
        with closing(sqlite3.connect(result.backup)) as backup:
            self.assertEqual(snapshot(backup), before)
        self.assertEqual(result.backup.stat().st_mode & 0o777, 0o600)

    def test_legacy_upgrade_preserves_all_rows_and_adds_missing_examples(self):
        self.seed_legacy()
        entry = self.conn.execute("SELECT e.id FROM entries e JOIN languages l ON l.id=e.language_id WHERE l.slug='rust' AND e.slug='vec-t'").fetchone()[0]
        self.conn.execute('UPDATE entries SET definition=? WHERE id=?', ('My own explanation', entry))
        example = self.conn.execute('SELECT id FROM examples ORDER BY id LIMIT 1').fetchone()[0]
        self.conn.execute('UPDATE examples SET explanation=? WHERE id=?', ('My annotated example', example))
        self.conn.execute('INSERT INTO examples(uuid,entry_id,title,code) VALUES(?,?,?,?)', (str(uuid4()), entry, 'My extra example', 'let personal = 42;'))
        # A recipient-only language and entry must survive the shared update.
        language = self.conn.execute('INSERT INTO languages(uuid,name,slug) VALUES(?,?,?)', (str(uuid4()), 'Personal Notes', 'personal-notes')).lastrowid
        category = self.conn.execute('INSERT INTO categories(uuid,language_id,name,slug) VALUES(?,?,?,?)', (str(uuid4()), language, 'Notes', 'notes')).lastrowid
        self.conn.execute('INSERT INTO entries(uuid,language_id,category_id,title,slug,definition) VALUES(?,?,?,?,?,?)', (str(uuid4()), language, category, 'Local note', 'local-note', 'Keep this private local draft.'))
        self.conn.commit()
        before = snapshot(self.conn)
        result = self.service.apply(self.document)
        after = snapshot(self.conn)
        for table, rows in before.items():
            if table != 'app_metadata':
                self.assertTrue(set(rows).issubset(after[table]), table)
        self.assertEqual(result.added['entries'], 415)
        self.assertEqual(result.added['examples'], 659)
        self.assertTrue(result.differences)
        self.assertEqual(result.skipped, [])
        self.assertEqual(self.conn.execute('SELECT definition FROM entries WHERE id=?', (entry,)).fetchone()[0], 'My own explanation')
        self.assertEqual(self.conn.execute('SELECT explanation FROM examples WHERE id=?', (example,)).fetchone()[0], 'My annotated example')
        self.assertEqual(self.service.apply(self.document).added_total, 0)
        self.assertEqual(snapshot(self.conn), after)

    def test_failed_import_rolls_back_and_keeps_valid_backup(self):
        before = snapshot(self.conn)
        class FailingService(LibraryUpdateService):
            def _merge(self, document):
                super()._merge(document)
                raise RuntimeError('Simulated failure before commit')
        with self.assertRaisesRegex(RuntimeError, 'Simulated failure'):
            FailingService(self.conn).apply(self.document)
        self.assertEqual(snapshot(self.conn), before)
        backups = list((Path(self.temp.name) / 'profile/backups').glob('*.db'))
        self.assertEqual(len(backups), 1)
        with closing(sqlite3.connect(backups[0])) as backup:
            self.assertEqual(snapshot(backup), before)

    def test_checksum_duplicate_missing_reference_and_cycle_rejected(self):
        original = snapshot(self.conn)
        bad = copy.deepcopy(self.document)
        bad['content_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'checksum'):
            self.service.apply(bad)
        bad = copy.deepcopy(self.document)
        bad['records']['examples'].append(bad['records']['examples'][0])
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.service.apply(self.seal(bad))
        bad = copy.deepcopy(self.document)
        bad['records']['entries'][0]['parent_entry_id'] = 'missing'
        with self.assertRaisesRegex(ValueError, 'Missing reference'):
            self.service.apply(self.seal(bad))
        bad = copy.deepcopy(self.document)
        row = bad['records']['entries'][0]
        row['parent_entry_id'] = row['uuid']
        with self.assertRaisesRegex(ValueError, 'cycle'):
            self.service.apply(self.seal(bad))
        self.assertEqual(snapshot(self.conn), original)
        self.assertFalse((Path(self.temp.name) / 'profile/backups').exists())

    def test_cross_scope_reference_is_rejected(self):
        bad = copy.deepcopy(self.document)
        row = bad['records']['entries'][0]
        row['category_id'] = next(c['uuid'] for c in bad['records']['categories'] if c['language_id'] != row['language_id'])
        with self.assertRaisesRegex(ValueError, 'different language'):
            validate_package(self.seal(bad))

    def test_local_edits_and_deletions_survive_later_library_version(self):
        self.service.apply(self.document)
        source = self.document['records']['examples'][0]
        self.conn.execute('UPDATE examples SET code=? WHERE uuid=?', ('my replacement code', source['uuid']))
        deleted = self.document['records']['examples'][1]
        self.conn.execute('DELETE FROM examples WHERE uuid=?', (deleted['uuid'],))
        self.conn.commit()
        changed = copy.deepcopy(self.document)
        changed['version'] = 'test-next-version'
        changed['records']['examples'][0]['code'] = 'new publisher code'
        result = self.service.apply(self.seal(changed))
        self.assertEqual(result.added_total, 0)
        self.assertEqual(self.conn.execute('SELECT code FROM examples WHERE uuid=?', (source['uuid'],)).fetchone()[0], 'my replacement code')
        self.assertIsNone(self.conn.execute('SELECT id FROM examples WHERE uuid=?', (deleted['uuid'],)).fetchone())
        self.assertEqual(len(result.skipped), 1)

    def test_unicode_natural_fields_and_relationships_round_trip(self):
        doc = copy.deepcopy(self.document)
        natural_id = next(l['uuid'] for l in doc['records']['languages'] if l['language_kind'] == 'natural')
        entry = next(e for e in doc['records']['entries'] if e['language_id'] == natural_id)
        example = next(x for x in doc['records']['examples'] if x['entry_id'] == entry['uuid'])
        example['romanization'] = 'transliteration fixture'
        example['pronunciation'] = '音声 — кириллица'
        other = next(e for e in doc['records']['entries'] if e['language_id'] == natural_id and e['uuid'] != entry['uuid'])
        doc['records']['entry_relations'].append({'uuid': str(uuid4()), 'source_entry_id': entry['uuid'], 'target_entry_id': other['uuid'], 'relation_type': 'related', 'sort_order': 0})
        self.service.apply(self.seal(doc))
        stored = self.conn.execute('SELECT * FROM examples WHERE uuid=?', (example['uuid'],)).fetchone()
        self.assertEqual(stored['pronunciation'], example['pronunciation'])
        self.assertEqual(stored['romanization'], example['romanization'])
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM entry_relations').fetchone()[0], 1)

    def test_downloaded_library_uses_same_validator(self):
        path = Path(self.temp.name) / 'library.json'
        path.write_text(json.dumps(self.document, ensure_ascii=False), encoding='utf-8')
        self.assertEqual(load_package(path), self.document)

    def test_schema_six_upgrade_is_backed_up_and_keeps_original_values(self):
        from importlib.resources import files
        legacy = open_database(Path(self.temp.name) / 'legacy' / 'wyncodex.db')
        try:
            legacy.execute('CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT)')
            for path in sorted(files('wyncodex.database.migrations').iterdir()):
                if path.name.endswith('.sql') and int(path.name.split('_')[0]) <= 6:
                    legacy.executescript(path.read_text())
                    legacy.execute('INSERT INTO schema_migrations(version) VALUES(?)', (int(path.name.split('_')[0]),))
            legacy.execute('INSERT INTO languages(uuid,name,slug) VALUES(?,?,?)', (str(uuid4()), 'My Language', 'my-language'))
            legacy.commit()
            before = snapshot(legacy)
            old_columns = [r[1] for r in legacy.execute('PRAGMA table_info(languages)')]
            backup = prepare_database(legacy)
            self.assertEqual(legacy.execute('SELECT max(version) FROM schema_migrations').fetchone()[0], 7)
            self.assertEqual([tuple(r) for r in legacy.execute('SELECT '+','.join(old_columns)+' FROM languages ORDER BY rowid')], before['languages'])
            with closing(sqlite3.connect(backup)) as saved:
                self.assertEqual(snapshot(saved), before)
            self.assertIsNone(prepare_database(legacy))
        finally:
            legacy.close()


if __name__ == '__main__':
    unittest.main()
