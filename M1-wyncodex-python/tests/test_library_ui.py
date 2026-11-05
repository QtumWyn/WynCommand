import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import QSettings, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox, QPlainTextEdit
from wyncodex.database.connection import open_database
from wyncodex.database.migration_runner import run_migrations
from wyncodex.importers.models import ImportMode
from wyncodex.repositories.search_repository import SearchRepository
from wyncodex.services.search_service import SearchService
from wyncodex.services.assembly_service import AssemblyService
from wyncodex.services.library_update_service import LibraryUpdateService, load_package
from wyncodex.ui.main_window import MainWindow
from wyncodex.ui.models.navigation_model import NODE_TYPE_ROLE, NODE_ID_ROLE, NavigationNodeType
from test_library_update import make_services


class LibraryUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = tempfile.TemporaryDirectory()
        QSettings.setDefaultFormat(QSettings.Format.IniFormat)
        QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, cls.settings.name)
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setOrganizationName('WynCodexTests')
        cls.app.setApplicationName('LibraryUpdateTests')

    @classmethod
    def tearDownClass(cls):
        cls.settings.cleanup()

    def test_update_menu_preview_apply_readback_and_downloaded_repeat(self):
        from importlib.resources import files
        with tempfile.TemporaryDirectory() as directory:
            conn = open_database(Path(directory) / 'wyncodex.db')
            run_migrations(conn)
            importer, services = make_services(conn)
            legacy = Path(str(files('wyncodex.resources').joinpath('starter-library.json')))
            importer.import_preview(importer.preview(legacy, ImportMode.STRICT_CREATE), ImportMode.STRICT_CREATE)
            ls, cs, ps, es = services
            search = SearchRepository(conn)
            window = MainWindow(ls, cs, ps, es, importer, SearchService(search), AssemblyService(conn), LibraryUpdateService(conn))
            window.show()
            dialogs = []
            timer = QTimer()
            def answer_dialog():
                dialog = QApplication.activeModalWidget()
                if isinstance(dialog, QMessageBox):
                    dialogs.append((dialog.windowTitle(), dialog.text(), dialog.detailedText()))
                    button = dialog.button(QMessageBox.StandardButton.Yes) or dialog.button(QMessageBox.StandardButton.Ok)
                    if button:
                        button.click()
            timer.timeout.connect(answer_dialog)
            timer.start(10)
            try:
                self.assertTrue(window._update_library_button.isEnabled())
                window._update_library_button.menu().actions()[0].trigger()
                self.assertEqual([x[0] for x in dialogs], ['Update Library', 'Library updated'])
                self.assertIn('New entries: 415', dialogs[0][1])
                self.assertIn('New examples: 659', dialogs[0][1])
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM languages').fetchone()[0], 66)
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM entries').fetchone()[0], 1748)
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM examples').fetchone()[0], 1706)
                paths = {}
                def walk(node, prefix):
                    path = prefix + [node.text().split(' · ', 1)[0].strip()]
                    if node.data(NODE_TYPE_ROLE) == NavigationNodeType.ENTRY:
                        paths[node.data(NODE_ID_ROLE)] = path
                    for i in range(node.rowCount()):
                        walk(node.child(i), path)
                model = window._navigation_model
                for i in range(model.rowCount()):
                    walk(model.item(i), [])
                rust = ls.get_language_by_slug('rust').id
                child = es.get_entry_by_slug(rust, 'hashset-insert')
                self.assertEqual(paths[child.id][-2:], ['HashSet', 'insert()'])
                window._show_entry(child.id)
                self.assertEqual(window._entry_page._title_label.text(), 'insert()')
                self.assertTrue(window._entry_page.findChildren(QPlainTextEdit))
                self.assertTrue(search.search('HashSet union', language_id=rust, language_kind='programming'))
                self.assertTrue(window._set_language_kind('natural'))
                self.assertEqual(model.rowCount(), 23)
                self.assertTrue(window._update_library_button.isVisible())
                natural = conn.execute("SELECT e.id,e.title FROM entries e JOIN languages l ON l.id=e.language_id WHERE l.language_kind='natural' ORDER BY e.id LIMIT 1").fetchone()
                window._show_entry(natural['id'])
                self.assertEqual(window._entry_page._title_label.text(), natural['title'])
                assembly = AssemblyService(conn)
                for track in range(1, 9):
                    self.assertTrue(assembly.entry_ids(track), track)
                backup_count = len(list((Path(directory) / 'backups').glob('*.db')))
                dialogs.clear()
                downloaded = Path(directory) / 'downloaded-library.json'
                downloaded.write_bytes(files('wyncodex.resources').joinpath('public-library.json').read_bytes())
                with patch('wyncodex.ui.main_window.QFileDialog.getOpenFileName', return_value=(str(downloaded), '')):
                    window._update_library_button.menu().actions()[1].trigger()
                self.assertEqual([x[0] for x in dialogs], ['Update Library'])
                self.assertEqual(len(list((Path(directory) / 'backups').glob('*.db'))), backup_count)
                self.assertEqual(conn.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
            finally:
                timer.stop()
                window.close()
                conn.close()


if __name__ == '__main__':
    unittest.main()
