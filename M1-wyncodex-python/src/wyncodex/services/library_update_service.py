"""Versioned, additive library updates that never replace a user's records."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from collections import Counter
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path
from uuid import uuid4


FIELDS = {
    'languages': 'name slug description color icon_name is_enabled sort_order language_kind',
    'categories': 'name slug description sort_order',
    'packages': 'name slug summary description sort_order',
    'entries': 'title slug signature definition mental_model return_value gotchas notes sort_order summary entry_kind formality dialect related_concepts',
    'arguments': 'position name type_text description required default_value',
    'examples': 'title code explanation example_type syntax_hint sort_order output romanization pronunciation',
    'tags': 'name slug',
    'entry_relations': 'relation_type sort_order',
    'entry_tags': '',
}
REFERENCES = {
    'languages': {},
    'categories': {'language_id': 'languages'},
    'packages': {'category_id': 'categories'},
    'entries': {'language_id': 'languages', 'category_id': 'categories', 'package_id': 'packages', 'parent_entry_id': 'entries'},
    'arguments': {'entry_id': 'entries'},
    'examples': {'entry_id': 'entries'},
    'tags': {},
    'entry_relations': {'source_entry_id': 'entries', 'target_entry_id': 'entries'},
    'entry_tags': {'entry_id': 'entries', 'tag_id': 'tags'},
}
ORDER = tuple(FIELDS)
NULLABLE_REFS = {'category_id', 'package_id', 'parent_entry_id'}
INTEGER_FIELDS = {'is_enabled', 'sort_order', 'position', 'required'}


def content_hash(records: dict) -> str:
    encoded = json.dumps(records, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def validate_package(document: dict) -> None:
    expected = {'wyncodex_library_schema', 'library_id', 'version', 'database_schema', 'content_sha256', 'records'}
    if not isinstance(document, dict) or set(document) != expected:
        raise ValueError('Invalid library manifest fields.')
    if document['wyncodex_library_schema'] != 1 or document['database_schema'] != 7:
        raise ValueError('This library requires a different application/schema version.')
    for key in ('library_id', 'version'):
        value = document[key]
        if not isinstance(value, str) or not value or len(value) > 100:
            raise ValueError('Invalid library identity/version.')
    records = document['records']
    if not isinstance(records, dict) or set(records) != set(ORDER):
        raise ValueError('Invalid library record groups.')
    ids = {table: set() for table in ORDER}
    for table in ORDER:
        if not isinstance(records[table], list) or len(records[table]) > 100_000:
            raise ValueError('Invalid library record list.')
        expected_fields = set(FIELDS[table].split()) | set(REFERENCES[table])
        if table != 'entry_tags':
            expected_fields.add('uuid')
        for row in records[table]:
            if not isinstance(row, dict) or set(row) != expected_fields:
                raise ValueError(f'Invalid fields in {table}.')
            if table != 'entry_tags':
                identity = row['uuid']
                if not isinstance(identity, str) or not identity or len(identity) > 100 or identity in ids[table]:
                    raise ValueError(f'Duplicate or invalid identity in {table}.')
                ids[table].add(identity)
            for key in FIELDS[table].split():
                value = row[key]
                if key in INTEGER_FIELDS:
                    if type(value) is not int:
                        raise ValueError(f'Invalid integer {table}.{key}.')
                elif value is not None and not isinstance(value, str):
                    raise ValueError(f'Invalid text {table}.{key}.')
            for key in REFERENCES[table]:
                value = row[key]
                if value is None and key in NULLABLE_REFS:
                    continue
                if not isinstance(value, str) or not value:
                    raise ValueError(f'Invalid reference {table}.{key}.')
    for table in ORDER:
        for row in records[table]:
            for key, target in REFERENCES[table].items():
                value = row[key]
                if value is not None and value not in ids[target]:
                    raise ValueError(f'Missing reference {table}.{key}.')
    languages = {row['uuid']: row for row in records['languages']}
    categories = {row['uuid']: row for row in records['categories']}
    packages = {row['uuid']: row for row in records['packages']}
    entries = {row['uuid']: row for row in records['entries']}
    for row in languages.values():
        if row['language_kind'] not in ('programming', 'natural') or row['is_enabled'] not in (0, 1):
            raise ValueError('Invalid language kind or enabled flag.')
    for row in entries.values():
        category, package, parent = row['category_id'], row['package_id'], row['parent_entry_id']
        if category and categories[category]['language_id'] != row['language_id']:
            raise ValueError('Entry category belongs to a different language.')
        if package and packages[package]['category_id'] != category:
            raise ValueError('Entry package belongs to a different category.')
        if parent and any(entries[parent][key] != row[key] for key in ('language_id', 'category_id', 'package_id')):
            raise ValueError('Entry parent belongs to a different scope.')
    for identity in entries:
        seen = set()
        current = identity
        while current:
            if current in seen:
                raise ValueError('Library entry hierarchy contains a cycle.')
            seen.add(current)
            current = entries[current]['parent_entry_id']
    if document['content_sha256'] != content_hash(records):
        raise ValueError('Library checksum mismatch.')


def load_package(path: Path | None = None) -> dict:
    resource = path if path is not None else resources.files('wyncodex.resources').joinpath('public-library.json')
    raw = resource.read_bytes()
    if len(raw) > 30_000_000:
        raise ValueError('Library package is too large.')
    document = json.loads(raw)
    validate_package(document)
    return document


def database_path(connection: sqlite3.Connection) -> Path | None:
    row = next(row for row in connection.execute('PRAGMA database_list') if row[1] == 'main')
    return Path(row[2]) if row[2] else None


def backup_database(connection: sqlite3.Connection, *, locked: bool = False) -> Path | None:
    """Use SQLite backup, including committed WAL content; never copy a live file."""
    path = database_path(connection)
    if path is None:
        return None  # Disposable memory databases only.
    directory = path.parent / 'backups'
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    destination = directory / f'wyncodex-before-update-{stamp}-{uuid4().hex[:8]}.db'
    # A connection inside BEGIN IMMEDIATE cannot back itself up. A separate
    # reader sees the stable pre-write snapshot while the writer lock is held.
    source = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) if locked else connection
    try:
        with closing(sqlite3.connect(destination)) as target:
            source.backup(target)
            if target.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise RuntimeError('Backup integrity check failed.')
    finally:
        if locked:
            source.close()
    destination.chmod(0o600)
    return destination


def prepare_database(connection: sqlite3.Connection) -> Path | None:
    """Safeguard an existing profile before upgrading its database schema."""
    from wyncodex.database.migration_runner import run_migrations
    existing = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='languages'").fetchone()
    backup = None
    if existing:
        version = connection.execute('SELECT max(version) FROM schema_migrations').fetchone()[0] or 0
        if version > 7:
            raise ValueError('This profile belongs to a newer WynCodex application.')
        if version < 7:
            backup = backup_database(connection)
    run_migrations(connection)
    return backup


@dataclass
class UpdateResult:
    added: dict[str, int] = field(default_factory=dict)
    reused: dict[str, int] = field(default_factory=dict)
    differences: list[dict] = field(default_factory=list)
    skipped: list[dict] = field(default_factory=list)
    backup: Path | None = None

    @property
    def added_total(self) -> int:
        return sum(self.added.values())


class LibraryUpdateService:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def preview(self, document: dict) -> UpdateResult:
        validate_package(document)
        if self.connection.in_transaction:
            raise RuntimeError('Finish the current database transaction first.')
        copy = sqlite3.connect(':memory:')
        self.connection.backup(copy)
        copy.row_factory = sqlite3.Row
        copy.execute('PRAGMA foreign_keys=ON')
        try:
            return LibraryUpdateService(copy).apply(document)
        finally:
            copy.close()

    def apply(self, document: dict) -> UpdateResult:
        validate_package(document)
        conn = self.connection
        if conn.in_transaction:
            raise RuntimeError('Finish the current database transaction first.')
        version = conn.execute('SELECT max(version) FROM schema_migrations').fetchone()[0]
        if version != document['database_schema']:
            raise ValueError('Upgrade the application before importing this library.')
        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('BEGIN IMMEDIATE')
        try:
            backup = backup_database(conn, locked=True)
            result = self._merge(document)
            result.backup = backup
            if conn.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise RuntimeError('Database integrity check failed; update rolled back.')
            if conn.execute('PRAGMA foreign_key_check').fetchall():
                raise RuntimeError('Broken library relationship; update rolled back.')
            conn.commit()
            return result
        except BaseException:
            conn.rollback()
            raise

    def _merge(self, document: dict) -> UpdateResult:
        conn = self.connection
        key = 'library_update:' + document['library_id']
        saved = conn.execute('SELECT value FROM app_metadata WHERE key=?', (key,)).fetchone()
        old_state = json.loads(saved[0]) if saved else {}
        aliases = old_state.get('identities', {})
        mappings = {table: {} for table in ORDER}
        added, reused = Counter(), Counter()
        result = UpdateResult()
        for table in ORDER:
            pending = list(document['records'][table])
            while pending:
                next_pending = []
                progressed = False
                for incoming in pending:
                    if table == 'entries' and incoming['parent_entry_id'] is not None and incoming['parent_entry_id'] not in mappings['entries']:
                        next_pending.append(incoming)
                        continue
                    progressed = True
                    identity = incoming.get('uuid')
                    values = {key: incoming[key] for key in FIELDS[table].split()}
                    missing = False
                    for reference, target in REFERENCES[table].items():
                        source_id = incoming[reference]
                        mapped = mappings[target].get(source_id) if source_id is not None else None
                        if source_id is not None and mapped is None:
                            missing = True
                        values[reference] = mapped
                    if missing:
                        if identity:
                            mappings[table][identity] = None
                        result.skipped.append({'table': table, 'title': incoming.get('title', incoming.get('name', 'Relationship')), 'reason': 'Referenced record was kept deleted or has conflicting identity.'})
                        continue
                    if table == 'entry_tags':
                        cursor = conn.execute('INSERT OR IGNORE INTO entry_tags(entry_id,tag_id) VALUES(?,?)', (values['entry_id'], values['tag_id']))
                        (added if cursor.rowcount else reused)[table] += 1
                        continue
                    table_aliases = aliases.setdefault(table, {})
                    prior_identity = table_aliases.get(identity)
                    local = conn.execute(f'SELECT * FROM {table} WHERE uuid=?', (prior_identity or identity,)).fetchone()
                    if prior_identity and local is None:
                        mappings[table][identity] = None
                        result.skipped.append({'table': table, 'title': incoming.get('title', incoming.get('name', 'Record')), 'reason': 'Previously imported record was deleted locally; kept deleted.'})
                        continue
                    if local is None:
                        local = self._legacy_match(table, values)
                    if local is not None:
                        # Never attach incoming children/examples to an unrelated
                        # record whose UUID or scoped slug happens to collide.
                        identity_fields = list(REFERENCES[table])
                        if table == 'languages':
                            identity_fields.append('language_kind')
                        if any(local[field] != values[field] for field in identity_fields):
                            mappings[table][identity] = None
                            result.skipped.append({'table': table, 'title': incoming.get('title', incoming.get('name', 'Record')), 'reason': 'Existing record has a different parent, scope, or language kind.'})
                            continue
                        changed = [field for field in FIELDS[table].split() if local[field] != values[field]]
                        if changed:
                            result.differences.append({'table': table, 'title': incoming.get('title', incoming.get('name', 'Record')), 'fields': changed})
                        reused[table] += 1
                        local_id, local_uuid = local['id'], local['uuid']
                    else:
                        values = {'uuid': identity, **values}
                        columns = ','.join(values)
                        placeholders = ','.join('?' for _ in values)
                        cursor = conn.execute(f'INSERT INTO {table}({columns}) VALUES({placeholders})', tuple(values.values()))
                        local_id, local_uuid = cursor.lastrowid, identity
                        added[table] += 1
                    mappings[table][identity] = local_id
                    table_aliases[identity] = local_uuid
                if next_pending and not progressed:
                    raise ValueError('Library entry hierarchy contains a cycle.')
                pending = next_pending
        state = {'version': document['version'], 'sha256': document['content_sha256'], 'identities': aliases}
        if state != old_state:
            conn.execute('INSERT INTO app_metadata(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP', (key, json.dumps(state, sort_keys=True)))
        result.added = dict(added)
        result.reused = dict(reused)
        return result

    def _legacy_match(self, table: str, values: dict):
        keys = {
            'languages': ['slug'],
            'categories': ['language_id', 'slug'],
            'packages': ['category_id', 'slug'],
            'entries': ['language_id', 'slug'],
            'arguments': ['entry_id', 'name', 'position'],
            'examples': ['entry_id', 'title', 'code', 'example_type', 'syntax_hint'],
            'tags': ['slug'],
            'entry_relations': ['source_entry_id', 'target_entry_id', 'relation_type'],
        }[table]
        # NULL-aware comparison; trim harmless outer whitespace from legacy code.
        conditions = ["trim(replace(code, char(13), '')) IS trim(replace(?, char(13), ''))" if field == 'code' else f'{field} IS ?' for field in keys]
        return self.connection.execute(f'SELECT * FROM {table} WHERE ' + ' AND '.join(conditions) + ' ORDER BY id LIMIT 1', tuple(values[field] for field in keys)).fetchone()
