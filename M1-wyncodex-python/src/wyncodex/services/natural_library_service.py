"""Create requested empty reference sections once, without overwriting user edits."""
import sqlite3
from uuid import UUID, uuid5

LANGUAGES = (
    'Russian', 'Romanian', 'Esperanto', 'Finnish', 'Icelandic', 'Swedish',
    'Danish', 'German', 'Bulgarian', 'Korean', 'Georgian', 'Kabardian',
    'Chechen', 'Tuvan', 'Tatar', 'Kazakh', 'Belorussian', 'Japanese',
    'French', 'Swahili', 'Xhosa', 'Mongolian', 'Greenlandic',
)
CATEGORIES = (
    ('writing-pronunciation', 'Writing & Pronunciation', 'Add writing-system notes and optional pronunciation guidance.'),
    ('grammar', 'Grammar', 'Add patterns, explanations, and your own examples.'),
    ('vocabulary', 'Vocabulary', 'Add words, meanings, and usage notes.'),
    ('expressions', 'Expressions', 'Add expressions with translation and context.'),
    ('examples', 'Examples', 'Add original text, translation, and word-by-word breakdowns.'),
    ('common-mistakes', 'Common Mistakes', 'Record corrections, contrasts, and reminders.'),
)
NAMESPACE = UUID('6b53dd26-4e71-4f85-9171-777e4a75fb03')

def seed_natural_library(connection: sqlite3.Connection) -> dict[str, int]:
    if connection.execute("SELECT 1 FROM app_metadata WHERE key='natural_library_seed_v1'").fetchone():
        return {'languages': 0, 'categories': 0}
    counts = {'languages': 0, 'categories': 0}
    connection.execute('BEGIN IMMEDIATE')
    try:
        if connection.execute("SELECT 1 FROM app_metadata WHERE key='natural_library_seed_v1'").fetchone():
            connection.commit()
            return counts
        for name in LANGUAGES:
            slug = 'natural-' + name.lower()
            identity = str(uuid5(NAMESPACE, slug))
            row = connection.execute('SELECT id, language_kind FROM languages WHERE uuid=? OR slug=?', (identity, slug)).fetchone()
            if row:
                if row['language_kind'] != 'natural':
                    raise ValueError(f'Natural-language seed conflicts with {name}; existing data was not changed.')
                language_id = row['id']
            else:
                cursor = connection.execute('INSERT INTO languages(uuid,name,slug,description,language_kind) VALUES(?,?,?,?,?)',
                    (identity, name, slug, f'Your editable {name} reference. Add notes and examples in any script; pronunciation and romanization are optional.', 'natural'))
                language_id = cursor.lastrowid
                counts['languages'] += 1
            for position, (category_slug, title, description) in enumerate(CATEGORIES):
                cursor = connection.execute('INSERT OR IGNORE INTO categories(uuid,language_id,name,slug,description,sort_order) VALUES(?,?,?,?,?,?)',
                    (str(uuid5(NAMESPACE, slug+'/'+category_slug)), language_id, title, category_slug, description, position))
                counts['categories'] += cursor.rowcount
        connection.execute("INSERT INTO app_metadata(key,value) VALUES('natural_library_seed_v1','1')")
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
    return counts
