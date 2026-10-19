from PySide6.QtCore import (
    QModelIndex,
    QSettings,
    QSortFilterProxyModel,
    Qt,
)
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTreeView,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
    QListWidget,
    QListWidgetItem,
)

from wyncodex.services.language_service import LanguageService
from wyncodex.services.category_service import CategoryService
from wyncodex.services.package_service import PackageService
from wyncodex.ui.models.navigation_model import (
    NODE_ID_ROLE,
    NODE_TYPE_ROLE,
    NavigationModel,
    NavigationNodeType,
)
from wyncodex.importers.models import (
    ImportMode,
    ImportValidationError,
)
from wyncodex.ui.dialogs.language_editor import LanguageEditorDialog
from wyncodex.ui.dialogs.category_editor import (
    CategoryEditorDialog,
)
from wyncodex.ui.dialogs.package_editor import (
    PackageEditorDialog,
)
from wyncodex.ui.pages.language_overview_page import (
    LanguageOverviewPage,
)
from wyncodex.ui.pages.welcome_page import WelcomePage
from wyncodex.ui.pages.category_overview_page import (
    CategoryOverviewPage,
)
from wyncodex.ui.pages.package_overview_page import (
    PackageOverviewPage,
)

from wyncodex.services.entry_service import (
    EntryService,
)

from wyncodex.ui.dialogs.entry_editor import (
    EntryEditorDialog,
)

from wyncodex.ui.pages.entry_detail_page import (
    EntryDetailPage,
)
from wyncodex.importers.json_importer import (
    JsonImportService,
)
from wyncodex.services.search_service import (
    SearchService,
)


class MainWindow(QMainWindow):
    def __init__(
            self,
            language_service: LanguageService,
            category_service: CategoryService,
            package_service: PackageService,
            entry_service: EntryService,
            import_service: JsonImportService,
            search_service: SearchService,
    ) -> None:
        super().__init__()
        self._settings = QSettings()

        self._language_service = language_service
        self._category_service = category_service
        self._package_service = package_service
        self._entry_service = entry_service
        self._import_service = import_service
        self._search_service = search_service

        self.setWindowTitle("WynCodex")
        self.resize(1100, 700)

        self._navigation_model = NavigationModel(
            language_service,
            category_service,
            package_service,
            entry_service,
        )

        self._navigation_proxy = (
            QSortFilterProxyModel(self)
        )

        self._navigation_proxy.setSourceModel(
            self._navigation_model
        )

        self._navigation_proxy.setFilterKeyColumn(
            0
        )

        self._navigation_proxy.setFilterCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )

        self._navigation_proxy.setRecursiveFilteringEnabled(
            True
        )

        self._navigation_proxy.setAutoAcceptChildRows(
            True
        )

        self._build_ui()

        self._restore_window_state()

        self._navigation_model.reload()
        self._language_tree.collapseAll()

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("centralRoot")

        layout = QVBoxLayout(root)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        stripe = QFrame()
        stripe.setObjectName("transStripe")
        stripe.setFixedHeight(3)

        self._splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        left_panel = self._build_left_panel()
        right_panel = self._build_right_panel()

        self._splitter.addWidget(left_panel)
        self._splitter.addWidget(right_panel)

        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)

        layout.addWidget(stripe)
        layout.addWidget(self._splitter)

        self.setCentralWidget(root)

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("navigationPanel")

        layout = QVBoxLayout(panel)

        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("LANGUAGES")
        title.setObjectName("sectionLabel")

        self._search_field = QLineEdit()

        self._search_field.setObjectName(
            "searchField"
        )

        self._search_field.setPlaceholderText(
            "Search languages, packages, entries..."
        )

        self._search_field.setClearButtonEnabled(
            True
        )

        # Create the tree FIRST.
        self._language_tree = QTreeView()

        self._language_tree.setModel(
            self._navigation_proxy
        )

        self._search_field.textChanged.connect(
            self._search
        )

        self._search_field.returnPressed.connect(
            self._open_current_search_result
        )

        self._language_tree.selectionModel().currentChanged.connect(
            self._on_navigation_changed
        )

        self._language_tree.setHeaderHidden(True)

        self._search_status = QLabel()

        self._search_status.setObjectName(
            "sectionLabel"
        )

        self._search_status.setVisible(
            False
        )


        self._search_results = QListWidget()

        self._search_results.setObjectName(
            "searchResults"
        )

        self._search_results.setWordWrap(
            True
        )

        self._search_results.itemClicked.connect(
            self._open_search_result
        )


        self._navigation_stack = (
            QStackedWidget()
        )

        self._navigation_stack.addWidget(
            self._language_tree
        )

        self._navigation_stack.addWidget(
            self._search_results
        )

        self._navigation_stack.setCurrentWidget(
            self._language_tree
        )

        # Now buttons can safely reference the tree.
        tree_controls = QHBoxLayout()

        expand_all_button = QPushButton(
            "EXPAND ALL"
        )

        collapse_all_button = QPushButton(
            "COLLAPSE ALL"
        )

        expand_all_button.setObjectName(
            "primaryButton"
        )

        collapse_all_button.setObjectName(
            "primaryButton"
        )

        expand_all_button.clicked.connect(
            self._language_tree.expandAll
        )

        collapse_all_button.clicked.connect(
            self._language_tree.collapseAll
        )

        tree_controls.addWidget(
            expand_all_button
        )

        tree_controls.addWidget(
            collapse_all_button
        )

        add_language_button = QPushButton(
            "+ LANGUAGE"
        )

        add_language_button.setObjectName(
            "accentButton"
        )

        add_language_button.clicked.connect(
            self._open_language_editor
        )

        import_json_button = QPushButton(
            "IMPORT JSON"
        )

        import_json_button.setObjectName(
            "primaryButton"
        )

        import_json_button.clicked.connect(
            self._import_json
        )

        layout.addWidget(title)

        layout.addWidget(
            self._search_field
        )

        layout.addLayout(
            tree_controls
        )

        layout.addWidget(
            self._search_status
        )

        layout.addWidget(
            self._navigation_stack
        )

        layout.addWidget(
            import_json_button
        )

        layout.addWidget(
            add_language_button
        )

        return panel

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("contentPanel")

        layout = QVBoxLayout(panel)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self._content_stack = QStackedWidget()

        self._content_stack.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Ignored,
        )

        self._content_stack.setMinimumSize(
            0,
            0,
        )

        self._welcome_page = WelcomePage()

        self._language_page = LanguageOverviewPage()

        self._language_page.add_category_requested.connect(
            self._open_category_editor
        )

        self._language_page.category_selected.connect(
            self._navigate_to_category
        )

        self._category_page = CategoryOverviewPage()

        self._category_page.add_package_requested.connect(
            self._open_package_editor
        )

        self._category_page.package_selected.connect(
            self._navigate_to_package
        )

        self._category_page.add_entry_requested.connect(
            self._open_category_entry_editor
        )

        self._category_page.entry_selected.connect(
            self._navigate_to_entry
        )

        self._package_page = (
            PackageOverviewPage()
        )

        self._package_page.add_entry_requested.connect(
            self._open_package_entry_editor
        )

        self._package_page.entry_selected.connect(
            self._navigate_to_entry
        )

        self._entry_page = EntryDetailPage()
        self._entry_page.edit_requested.connect(
            self._open_entry_editor
        )

        self._entry_page.add_child_requested.connect(
            self._open_child_entry_editor
        )

        self._content_stack.addWidget(
            self._entry_page
        )

        self._content_stack.addWidget(
            self._welcome_page
        )

        self._content_stack.addWidget(
            self._language_page
        )

        self._content_stack.addWidget(
            self._category_page
        )

        self._content_stack.addWidget(
            self._package_page
        )

        self._content_stack.setCurrentWidget(
            self._welcome_page
        )

        layout.addWidget(
            self._content_stack
        )

        return panel

    def _open_language_editor(self) -> None:
        dialog = LanguageEditorDialog(
            self._language_service,
            self,
        )

        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self._navigation_model.reload()

    def _on_navigation_changed(
            self,
            current: QModelIndex,
            _previous: QModelIndex,
    ) -> None:
        if not current.isValid():
            self._content_stack.setCurrentWidget(
                self._welcome_page
            )
            return

        source_index = (
            self._navigation_proxy
            .mapToSource(current)
        )

        if not source_index.isValid():
            return

        raw_node_type = source_index.data(
            NODE_TYPE_ROLE
        )

        node_id = source_index.data(
            NODE_ID_ROLE
        )

        if (
                raw_node_type is None
                or node_id is None
        ):
            return

        try:
            node_type = NavigationNodeType(
                raw_node_type
            )
        except ValueError:
            return

        match node_type:
            case NavigationNodeType.LANGUAGE:
                self._show_language(
                    node_id
                )

            case NavigationNodeType.CATEGORY:
                self._show_category(
                    node_id
                )

            case NavigationNodeType.PACKAGE:
                self._show_package(
                    node_id
                )
            case NavigationNodeType.ENTRY:
                self._show_entry(
                    node_id
                )

    def _show_language(
            self,
            language_id: int,
    ) -> None:
        language = (
            self._language_service
            .get_language_by_id(
                language_id
            )
        )

        if language is None:
            return

        categories = (
            self._category_service
            .get_categories_for_language(
                language_id
            )
        )

        self._language_page.set_language(
            language,
            categories,
        )

        self._content_stack.setCurrentWidget(
            self._language_page
        )


    def _show_category(
            self,
            category_id: int,
    ) -> None:
        category = (
            self._category_service
            .get_category_by_id(
                category_id
            )
        )

        if category is None:
            return

        packages = (
            self._package_service
            .get_packages_for_category(
                category_id
            )
        )

        entries = (
            self._entry_service
            .get_direct_entries_for_category(
                category_id
            )
        )

        self._category_page.set_category(
            category,
            packages,
            entries,
        )

        self._content_stack.setCurrentWidget(
            self._category_page
        )

    def _show_package(
            self,
            package_id: int,
    ) -> None:
        package = (
            self._package_service
            .get_package_by_id(
                package_id
            )
        )

        if package is None:
            return

        entries = (
            self._entry_service
            .get_entries_for_package(
                package_id
            )
        )

        self._package_page.set_package(
            package,
            entries,
        )

        self._content_stack.setCurrentWidget(
            self._package_page
        )

    def _open_category_editor(
            self,
            language_id: int,
    ) -> None:
        dialog = CategoryEditorDialog(
            self._category_service,
            language_id,
            self,
        )

        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self._navigation_model.reload()
            self._language_tree.collapseAll()

    def _open_category_entry_editor(
            self,
            category_id: int,
    ) -> None:
        syntax_hint = self._syntax_hint_for_category(
            category_id
        )

        dialog = EntryEditorDialog(
            entry_service=self._entry_service,
            category_id=category_id,
            package_id=None,
            default_syntax_hint=syntax_hint,
            parent=self,
        )

        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self._navigation_model.reload()
            self._language_tree.expandAll()

            self._show_category(
                category_id
            )

    def _open_package_editor(
            self,
            category_id: int,
    ) -> None:
        dialog = PackageEditorDialog(
            self._package_service,
            category_id,
            self,
        )

        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self._navigation_model.reload()
            self._language_tree.expandAll()

    def _open_package_entry_editor(
            self,
            category_id: int,
            package_id: int,
    ) -> None:
        syntax_hint = self._syntax_hint_for_category(
            category_id
        )

        dialog = EntryEditorDialog(
            entry_service=self._entry_service,
            category_id=category_id,
            package_id=package_id,
            default_syntax_hint=syntax_hint,
            parent=self,
        )

        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self._navigation_model.reload()
            self._language_tree.expandAll()

            self._show_package(
                package_id
            )

    def _navigate_to_node(
            self,
            node_type: NavigationNodeType,
            node_id: int,
    ) -> None:
        if self._search_field.text():
            self._search_field.clear()

        source_index = (
            self._find_navigation_index(
                node_type,
                node_id,
            )
        )

        if not source_index.isValid():
            return

        proxy_index = (
            self._navigation_proxy
            .mapFromSource(source_index)
        )

        if not proxy_index.isValid():
            return

        parent = proxy_index.parent()

        while parent.isValid():
            self._language_tree.expand(
                parent
            )

            parent = parent.parent()

        self._language_tree.setCurrentIndex(
            proxy_index
        )

        self._language_tree.scrollTo(
            proxy_index
        )

    def _navigate_to_category(
            self,
            category_id: int,
    ) -> None:
        self._navigate_to_node(
            NavigationNodeType.CATEGORY,
            category_id,
        )


    def _navigate_to_package(
            self,
            package_id: int,
    ) -> None:
        self._navigate_to_node(
            NavigationNodeType.PACKAGE,
            package_id,
        )

    def _find_navigation_index(
            self,
            node_type: NavigationNodeType,
            node_id: int,
            parent: QModelIndex = QModelIndex(),
    ) -> QModelIndex:
        row_count = (
            self._navigation_model
            .rowCount(parent)
        )

        for row in range(row_count):
            index = (
                self._navigation_model
                .index(
                    row,
                    0,
                    parent,
                )
            )

            raw_type = index.data(
                NODE_TYPE_ROLE
            )

            current_id = index.data(
                NODE_ID_ROLE
            )

            if (
                    raw_type == int(node_type)
                    and current_id == node_id
            ):
                return index

            child_result = (
                self._find_navigation_index(
                    node_type,
                    node_id,
                    index,
                )
            )

            if child_result.isValid():
                return child_result

        return QModelIndex()

    def _navigate_to_entry(
            self,
            entry_id: int,
    ) -> None:
        self._navigate_to_node(
            NavigationNodeType.ENTRY,
            entry_id,
        )

    def _show_entry(
            self,
            entry_id: int,
    ) -> None:
        entry = (
            self._entry_service
            .get_entry_by_id(
                entry_id
            )
        )

        if entry is None:
            return

        arguments = (
            self._entry_service
            .get_arguments_for_entry(
                entry_id
            )
        )

        examples = (
            self._entry_service
            .get_examples_for_entry(
                entry_id
            )
        )

        language = (
            self._language_service
            .get_language_by_id(
                entry.language_id
            )
        )

        syntax_hint = (
            language.slug
            if language is not None
            else None
        )

        self._entry_page.set_entry(
            entry,
            arguments,
            examples,
            syntax_hint,
        )

        self._content_stack.setCurrentWidget(
            self._entry_page
        )

    def _syntax_hint_for_category(
            self,
            category_id: int,
    ) -> str | None:
        category = (
            self._category_service
            .get_category_by_id(
                category_id
            )
        )

        if category is None:
            return None

        language = (
            self._language_service
            .get_language_by_id(
                category.language_id
            )
        )

        if language is None:
            return None

        return language.slug

    def _open_entry_editor(
            self,
            entry_id: int,
    ) -> None:
        entry = (
            self._entry_service
            .get_entry_by_id(
                entry_id
            )
        )

        if entry is None:
            return

        arguments = (
            self._entry_service
            .get_arguments_for_entry(
                entry_id
            )
        )

        examples = (
            self._entry_service
            .get_examples_for_entry(
                entry_id
            )
        )

        syntax_hint = (
            self._syntax_hint_for_category(
                entry.category_id
            )
        )

        dialog = EntryEditorDialog(
            entry_service=self._entry_service,
            category_id=entry.category_id,
            package_id=entry.package_id,
            default_syntax_hint=syntax_hint,
            entry=entry,
            arguments=arguments,
            examples=examples,
            parent=self,
        )

        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self._navigation_model.reload()
            self._language_tree.expandAll()

            self._show_entry(
                entry_id
            )

    def _import_json(self) -> None:
        dialog = QFileDialog(
            self,
            "Import WynCodex JSON",
        )

        dialog.setFileMode(
            QFileDialog.FileMode.ExistingFile
        )

        dialog.setNameFilters(
            [
                "WynCodex JSON (*.json)",
                "All Files (*)",
            ]
        )

        dialog.setOption(
            QFileDialog.Option.DontUseNativeDialog,
            True,
        )

        if (
                dialog.exec()
                != QDialog.DialogCode.Accepted
        ):
            return

        selected_files = (
            dialog.selectedFiles()
        )

        if not selected_files:
            return

        file_name = selected_files[0]

        mode_label, accepted = (
            QInputDialog.getItem(
                self,
                "Import Mode",
                "How should WynCodex handle "
                "existing content?",
                [
                    "Merge safely",
                    "Strict create",
                ],
                0,
                False,
            )
        )

        if not accepted:
            return

        if mode_label == "Merge safely":
            mode = (
                ImportMode
                .MERGE_SKIP_EXISTING
            )
        else:
            mode = (
                ImportMode
                .STRICT_CREATE
            )

        try:
            preview = (
                self._import_service
                .preview(
                    Path(file_name),
                    mode=mode,
                )
            )

        except ImportValidationError as error:
            QMessageBox.critical(
                self,
                "Import Validation Failed",
                str(error),
            )
            return

        counts = preview.counts

        message = (
            "This import contains:\n\n"
            f"{counts.languages} languages\n"
            f"{counts.categories} categories\n"
            f"{counts.packages} packages\n"
            f"{counts.entries} entries\n"
            f"{counts.arguments} arguments\n"
            f"{counts.examples} examples\n\n"
            "Import all of this into WynCodex?"
        )

        confirmation = QMessageBox.question(
            self,
            "Import Preview",
            message,
            (
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if (
                confirmation
                != QMessageBox.StandardButton.Yes
        ):
            return

        try:
            import_result = (
                self._import_service
                .import_preview(
                    preview,
                    mode=mode,
                )
            )

        except (
            ValueError,
            RuntimeError,
            OSError,
        ) as error:
            QMessageBox.critical(
                self,
                "Import Failed",
                str(error),
            )
            return

        self._navigation_model.reload()
        self._language_tree.expandAll()

        QMessageBox.information(
            self,
            "Import Complete",
            (
                "Import complete!\n\n"

                "CREATED\n"
                f"Languages: "
                f"{import_result.languages_created}\n"
                f"Categories: "
                f"{import_result.categories_created}\n"
                f"Packages: "
                f"{import_result.packages_created}\n"
                f"Entries: "
                f"{import_result.entries_created}\n"
                f"Arguments: "
                f"{import_result.arguments_created}\n"
                f"Examples: "
                f"{import_result.examples_created}\n\n"

                "REUSED\n"
                f"Languages: "
                f"{import_result.languages_reused}\n"
                f"Categories: "
                f"{import_result.categories_reused}\n"
                f"Packages: "
                f"{import_result.packages_reused}\n\n"

                "SKIPPED\n"
                f"Existing entries: "
                f"{import_result.entries_skipped}"
            ),
        )

    def _search(
            self,
            text: str,
    ) -> None:
        query = text.strip()

        if not query:
            self._search_results.clear()

            self._search_status.clear()

            self._search_status.setVisible(
                False
            )

            self._navigation_stack.setCurrentWidget(
                self._language_tree
            )

            self._language_tree.collapseAll()

            return

        if len(query) < 2:
            self._search_results.clear()

            self._search_status.setText(
                "TYPE AT LEAST 2 CHARACTERS"
            )

            self._search_status.setVisible(
                True
            )

            self._navigation_stack.setCurrentWidget(
                self._search_results
            )

            return

        results = (
            self._search_service.search(
                query
            )
        )

        self._search_results.clear()

        count = len(results)

        self._search_status.setText(
            (
                f"{count} RESULT"
                if count == 1
                else f"{count} RESULTS"
            )
        )

        self._search_status.setVisible(
            True
        )

        for result in results:
            kind = (
                f" · {result.entry_kind}"
                if result.entry_kind
                   and result.entry_kind != "entry"
                else ""
            )

            text = (
                f"{result.title}{kind}\n"
                f"{result.full_path}\n"
                f"{result.preview}"
            )

            item = QListWidgetItem(
                text
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                result.entry_id,
            )

            item.setToolTip(
                result.full_path
            )

            self._search_results.addItem(
                item
            )

        if count:
            self._search_results.setCurrentRow(
                0
            )

        self._navigation_stack.setCurrentWidget(
            self._search_results
        )

    def _open_search_result(
            self,
            item: QListWidgetItem,
    ) -> None:
        entry_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not isinstance(
                entry_id,
                int,
        ):
            return

        self._show_entry(
            entry_id
        )


    def _open_current_search_result(
            self,
    ) -> None:
        item = (
            self._search_results
            .currentItem()
        )

        if item is None:
            return

        self._open_search_result(
            item
        )

    def _open_child_entry_editor(
            self,
            parent_entry_id: int,
    ) -> None:
        parent_entry = (
            self._entry_service
            .get_entry_by_id(
                parent_entry_id
            )
        )

        if parent_entry is None:
            return

        syntax_hint = (
            self._syntax_hint_for_category(
                parent_entry.category_id
            )
        )

        dialog = EntryEditorDialog(
            entry_service=self._entry_service,
            category_id=parent_entry.category_id,
            package_id=parent_entry.package_id,
            parent_entry_id=parent_entry_id,
            default_syntax_hint=syntax_hint,
            parent=self,
        )

        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self._navigation_model.reload()

            self._navigate_to_entry(
                parent_entry_id
            )

            self._language_tree.expand(
                self._language_tree.currentIndex()
            )

    def _restore_window_state(
            self,
    ) -> None:
        geometry = self._settings.value(
            "window/geometry"
        )

        if geometry is not None:
            self.restoreGeometry(
                geometry
            )

        splitter_state = (
            self._settings.value(
                "window/splitter"
            )
        )

        if splitter_state is not None:
            self._splitter.restoreState(
                splitter_state
            )


    def _save_window_state(
            self,
    ) -> None:
        self._settings.setValue(
            "window/geometry",
            self.saveGeometry(),
        )

        self._settings.setValue(
            "window/splitter",
            self._splitter.saveState(),
        )

        self._settings.sync()


    def closeEvent(
            self,
            event,
    ) -> None:
        self._save_window_state()

        super().closeEvent(
            event
        )