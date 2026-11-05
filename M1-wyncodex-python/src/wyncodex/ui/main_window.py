from wyncodex.services.assembly_service import TRACKS, TRACK_BY_ID
from PySide6.QtCore import (
    QModelIndex,
    QSettings,
    QSignalBlocker,
    QSortFilterProxyModel,
    Qt,
)
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
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
    TRACK_ID_ROLE,
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
            assembly_service=None,
            library_service=None,
    ) -> None:
        super().__init__()
        self._settings = QSettings()
        self._language_kind = self._settings.value("library/languageKind", "programming")
        if self._language_kind not in ("programming", "natural"):
            self._language_kind = "programming"
        self._assembly_service = assembly_service
        self._library_service = library_service
        self._assembly_track = None

        self._navigation_history: list[
            tuple[NavigationNodeType, int, int | None]
        ] = []

        self._history_index: int = -1

        self._replaying_history: bool = False

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
            assembly_service,
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

        self._set_language_kind(self._language_kind, force=True)

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

        mode_bar = QWidget()
        mode_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        mode_layout = QHBoxLayout(mode_bar)
        mode_layout.setContentsMargins(18, 8, 18, 8)
        self._mode_group = QButtonGroup(self)
        self._mode_buttons = {}
        for kind, title in [("programming", "Programming"), ("natural", "Natural Languages")]:
            button = QPushButton(title)
            button.setCheckable(True)
            button.setObjectName("modeButton")
            button.setAccessibleName(title)
            button.clicked.connect(lambda checked=False, kind=kind: self._set_language_kind(kind))
            self._mode_group.addButton(button)
            self._mode_buttons[kind] = button
            mode_layout.addWidget(button)
        mode_layout.addStretch()
        layout.addWidget(stripe)
        layout.addWidget(mode_bar)
        layout.addWidget(self._splitter, 1)

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

        self._search_language_filter = QComboBox()

        self._search_language_filter.setObjectName(
            "searchLanguageFilter"
        )

        self._search_language_filter.setAccessibleName(
            "Search language"
        )

        self._search_language_filter.setToolTip(
            "Limit search results to a language."
        )

        self._search_language_filter.setMaxVisibleItems(8)

        self._search_language_filter.view().setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self._search_language_filter.currentIndexChanged.connect(
            self._search_language_changed
        )

        self._assembly_track_filter = QComboBox()
        self._assembly_track_filter.setObjectName("searchLanguageFilter")
        self._assembly_track_filter.setMaxVisibleItems(8)
        self._assembly_track_filter.setAccessibleName("Assembly target")
        self._assembly_track_filter.setVisible(False)
        self._assembly_track_filter.addItem("Assembly target: all", None)
        for track in TRACKS[1:]:
            self._assembly_track_filter.addItem(track.name, track.id)
        self._assembly_track_filter.currentIndexChanged.connect(self._search_track_changed)

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

        self._import_json_button = import_json_button = QPushButton(
            "IMPORT JSON"
        )

        import_json_button.setObjectName(
            "primaryButton"
        )

        import_json_button.clicked.connect(
            self._import_json
        )

        self._update_library_button = QPushButton('UPDATE LIBRARY')
        self._update_library_button.setObjectName('primaryButton')
        self._update_library_button.setEnabled(self._library_service is not None)
        update_menu = QMenu(self._update_library_button)
        update_menu.addAction('Use bundled library', lambda: self._update_library())
        update_menu.addAction('Open downloaded library…', self._open_library_file)
        self._update_library_button.setMenu(update_menu)

        layout.addWidget(title)

        layout.addWidget(
            self._search_field
        )

        layout.addWidget(
            self._search_language_filter
        )

        layout.addWidget(self._assembly_track_filter)
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

        layout.addWidget(self._update_library_button)

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

        navigation_bar_widget = QWidget()

        navigation_bar_widget.setObjectName(
            "navigationBar"
        )

        navigation_bar = QHBoxLayout(
            navigation_bar_widget
        )

        navigation_bar.setContentsMargins(
            18,
            12,
            18,
            8,
        )

        navigation_bar.setSpacing(
            8
        )

        self._back_button = QPushButton("←")
        self._forward_button = QPushButton("→")

        self._back_button.setObjectName(
            "primaryButton"
        )

        self._forward_button.setObjectName(
            "primaryButton"
        )

        self._back_button.setFixedWidth(46)
        self._forward_button.setFixedWidth(46)

        self._back_button.setToolTip(
            "Back"
        )

        self._forward_button.setToolTip(
            "Forward"
        )

        self._back_button.clicked.connect(
            self._go_back
        )

        self._forward_button.clicked.connect(
            self._go_forward
        )

        navigation_bar.addWidget(
            self._back_button
        )

        navigation_bar.addWidget(
            self._forward_button
        )

        navigation_bar.addStretch()

        layout.addWidget(
            navigation_bar_widget
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

        self._assembly_page = LanguageOverviewPage()
        self._assembly_page._children_label.setText("TARGETS")
        self._assembly_page._add_category_button.hide()
        self._assembly_page._edit_language_button.hide()
        self._assembly_page.category_selected.connect(self._show_assembly_track)
        self._content_stack.addWidget(self._assembly_page)

        self._language_page = LanguageOverviewPage()

        self._language_page.add_category_requested.connect(
            self._open_category_editor
        )

        self._language_page.category_selected.connect(
            self._navigate_to_category
        )

        self._language_page.edit_requested.connect(self._edit_language)
        self._category_page = CategoryOverviewPage()
        self._category_page.edit_requested.connect(self._edit_category)

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

        self._entry_page.member_selected.connect(
            self._navigate_to_entry
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
            language_kind=self._language_kind,
        )

        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self._navigation_model.reload()
            self._refresh_search_languages()

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

        self._set_assembly_track(source_index.data(TRACK_ID_ROLE))

        match node_type:
            case NavigationNodeType.TRACK:
                self._show_assembly_track(node_id)
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

        if language is None or language.language_kind != self._language_kind:
            return

        self._set_assembly_track(None)
        self._record_navigation(
            NavigationNodeType.LANGUAGE,
            language_id,
        )
        if language.slug == "nasm" and self._assembly_service:
            with QSignalBlocker(self._search_language_filter):
                self._search_language_filter.setCurrentIndex(self._search_language_filter.findData(language_id))
            self._assembly_track_filter.setVisible(True)
            self._assembly_page.set_language(language, [])
            self._assembly_page._title_label.setText("ASSEMBLY")
            self._assembly_page._description_label.setText("Choose a target before browsing categories. ISA, operating system, ABI and assembler syntax are separate choices. Shared x86-64 entries also appear in Linux and Windows.")
            self._assembly_page._populate_categories(list(TRACKS))
            self._content_stack.setCurrentWidget(self._assembly_page)
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


    def _set_assembly_track(self, track_id):
        self._assembly_track = track_id
        if hasattr(self, "_assembly_track_filter"):
            with QSignalBlocker(self._assembly_track_filter):
                self._assembly_track_filter.setCurrentIndex(self._assembly_track_filter.findData(track_id if track_id else None))

    def _show_assembly_track(self, track_id):
        if self._language_kind != "programming" or not self._assembly_service:
            return
        self._set_assembly_track(track_id)
        self._assembly_track_filter.setVisible(True)
        language_id = self._assembly_service.language_id()
        language = self._language_service.get_language_by_id(language_id)
        with QSignalBlocker(self._search_language_filter):
            self._search_language_filter.setCurrentIndex(self._search_language_filter.findData(language_id))
        allowed = self._assembly_service.category_ids(track_id)
        categories = [c for c in self._category_service.get_categories_for_language(language_id) if c.id in allowed]
        self._language_page.set_language(language, categories)
        self._language_page._title_label.setText(TRACK_BY_ID[track_id].name.upper())
        self._language_page._description_label.setText(TRACK_BY_ID[track_id].description)
        self._content_stack.setCurrentWidget(self._language_page)
        self._record_navigation(NavigationNodeType.TRACK, track_id)
        if self._search_field.text().strip():
            self._search(self._search_field.text())

    def _scoped_entries(self, entries):
        if self._assembly_service and self._assembly_track is not None:
            return self._assembly_service.filter_entries(entries, self._assembly_track)
        return entries

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

        if category is None or not self._language_in_mode(category.language_id):
            return

        self._record_navigation(
            NavigationNodeType.CATEGORY,
            category_id,
        )

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

        if self._assembly_service and category.language_id == self._assembly_service.language_id():
            entries = self._scoped_entries(entries)
            packages = [p for p in packages if self._scoped_entries(self._entry_service.get_entries_for_package(p.id))]
        else:
            self._set_assembly_track(None)
        self._category_page.set_category(category, packages, entries, natural=self._language_kind == "natural")

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

        if package is None or self._language_kind != "programming":
            return

        self._record_navigation(
            NavigationNodeType.PACKAGE,
            package_id,
        )

        entries = (
            self._entry_service
            .get_entries_for_package(
                package_id
            )
        )

        self._package_page.set_package(
            package,
            self._scoped_entries(entries),
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
            natural=self._language_kind == "natural",
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
            natural=self._language_kind == "natural",
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
            if node_type == NavigationNodeType.ENTRY:
                self._show_entry(node_id)
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

        previous = self._language_tree.currentIndex()
        self._language_tree.setCurrentIndex(proxy_index)
        if previous == proxy_index:
            self._on_navigation_changed(proxy_index, QModelIndex())

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
                    and (node_type == NavigationNodeType.LANGUAGE or index.data(TRACK_ID_ROLE) == self._assembly_track)
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

        if entry is None or not self._language_in_mode(entry.language_id):
            return

        if self._assembly_service:
            if entry.language_id != self._assembly_service.language_id():
                self._set_assembly_track(None)
            elif self._assembly_track is None or entry.id not in self._assembly_service.entry_ids(self._assembly_track):
                self._set_assembly_track(0)
        self._record_navigation(
            NavigationNodeType.ENTRY,
            entry_id,
        )

        arguments = (
            self._entry_service
            .get_arguments_for_entry(
                entry_id
            )
        )

        members = (
            self._entry_service
            .get_child_entries(
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

        if language and language.slug == "nasm" and self._assembly_service:
            syntax_hint = self._assembly_service.syntax_hint(entry_id)
        self._entry_page.set_entry(
            entry,
            arguments,
            examples,
            members,
            syntax_hint,
            natural=self._language_kind == "natural",
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

        if language.language_kind == "natural":
            return "text"
        if language.slug == "nasm":
            return TRACK_BY_ID[self._assembly_track].syntax_hint if self._assembly_track is not None else "text"
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
            natural=self._language_kind == "natural",
        )

        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self._navigation_model.reload()
            self._language_tree.expandAll()

            self._show_entry(
                entry_id
            )

    def _open_library_file(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, 'Open WynCodex library', '', 'WynCodex library (*.json)')
        if filename:
            self._update_library(Path(filename))

    def _update_library(self, source_path=None) -> None:
        from wyncodex.services.library_update_service import load_package
        if self._library_service is None:
            return
        try:
            document = load_package(source_path)
            preview = self._library_service.preview(document)
        except Exception as error:
            QMessageBox.warning(self, 'Library could not be read', str(error))
            return
        lines = [f'Library {document["version"]}', '']
        for table in ('languages', 'categories', 'packages', 'entries', 'arguments', 'examples', 'tags', 'entry_tags', 'entry_relations'):
            count = preview.added.get(table, 0)
            if count:
                lines.append(f'New {table.replace("_", " ")}: {count}')
        lines += ['', 'Your existing entries and examples will be kept.',
                  f'Existing records with different content kept: {len(preview.differences)}',
                  f'Records skipped to preserve deletions or conflicting identities: {len(preview.skipped)}']
        details = '\n'.join(f'{item["table"]}: {item["title"]} — kept existing {", ".join(item["fields"])}' for item in preview.differences)
        details += '\n' + '\n'.join(f'{item["table"]}: {item["title"]} — {item["reason"]}' for item in preview.skipped)
        dialog = QMessageBox(self)
        dialog.setWindowTitle('Update Library')
        dialog.setText('\n'.join(lines))
        if details.strip():
            dialog.setDetailedText(details.strip())
        if preview.added_total == 0:
            dialog.setInformativeText('No missing library content was found. Nothing was changed.')
            dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
            dialog.exec()
            return
        dialog.setInformativeText('A database backup will be saved before adding this content.')
        dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)
        if dialog.exec() != QMessageBox.StandardButton.Yes:
            return
        try:
            result = self._library_service.apply(document)
        except Exception as error:
            QMessageBox.critical(self, 'Library update failed', f'Library changes were rolled back.\n\n{error}')
            return
        self._set_language_kind(self._language_kind, force=True)
        message = f'Added {result.added.get("entries", 0)} entries and {result.added.get("examples", 0)} examples.\nExisting content was kept.'
        if result.backup:
            message += f'\n\nBackup: {result.backup}'
        QMessageBox.information(self, 'Library updated', message)

    def _import_json(self) -> None:
        if self._language_kind != "programming":
            return
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

        self._refresh_search_languages()

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

    def _refresh_search_languages(self) -> None:
        selected_language_id = (
            self._search_language_filter.currentData()
        )

        languages = self._language_service.get_all_languages(self._language_kind)

        with QSignalBlocker(self._search_language_filter):
            self._search_language_filter.clear()
            self._search_language_filter.addItem(
                "All languages",
                None,
            )

            for language in languages:
                if language.id is not None:
                    self._search_language_filter.addItem(
                        language.name,
                        language.id,
                    )

            selected_index = self._search_language_filter.findData(
                selected_language_id
            )

            self._search_language_filter.setCurrentIndex(
                max(0, selected_index)
            )

        if self._search_field.text().strip():
            self._search(self._search_field.text())

    def _search_language_changed(self, _index):
        is_assembly = bool(self._language_kind == "programming" and self._assembly_service and self._search_language_filter.currentData() == self._assembly_service.language_id())
        self._assembly_track_filter.setVisible(is_assembly)
        if not is_assembly:
            self._set_assembly_track(None)
        self._search(self._search_field.text())

    def _search_track_changed(self, _index):
        track_id = self._assembly_track_filter.currentData()
        if self._assembly_service:
            self._show_assembly_track(track_id or 0)

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

        if len(query) < (1 if self._language_kind == "natural" else 2):
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
                query,
                language_kind=self._language_kind,
                language_id=(
                    self._search_language_filter.currentData()
                ),
                assembly_track=(self._assembly_track if self._assembly_service and self._search_language_filter.currentData() == self._assembly_service.language_id() else None),
            )
        )

        self._search_results.clear()

        # Empty natural sections must also be discoverable before the first note.
        if self._language_kind == "natural":
            query_key = query.casefold()
            selected_id = self._search_language_filter.currentData()
            languages = self._language_service.get_all_languages("natural")
            languages.sort(key=lambda language: (language.name.casefold() != query_key, not language.name.casefold().startswith(query_key), language.name.casefold()))
            for language in languages:
                if selected_id is not None and selected_id != language.id:
                    continue
                aliases = language.name + (" Belarusian" if language.slug == "natural-belorussian" else "")
                if query_key in aliases.casefold():
                    item = QListWidgetItem(f"{language.name}\nLanguage reference")
                    item.setData(Qt.ItemDataRole.UserRole, ("language", language.id))
                    self._search_results.addItem(item)
                for category in self._category_service.get_categories_for_language(language.id):
                    if query_key in category.name.casefold():
                        item = QListWidgetItem(f"{category.name}\n{language.name}")
                        item.setData(Qt.ItemDataRole.UserRole, ("category", category.id))
                        self._search_results.addItem(item)
        count = len(results) + self._search_results.count()

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

        if isinstance(entry_id, (tuple, list)) and len(entry_id) == 2:
            kind, node_id = entry_id
            if kind == "language":
                self._show_language(node_id)
            elif kind == "category":
                self._show_category(node_id)
            return
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
            natural=self._language_kind == "natural",
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

    def _record_navigation(
            self,
            node_type: NavigationNodeType,
            node_id: int,
    ) -> None:
        if self._replaying_history:
            return

        destination = (
            node_type,
            node_id,
            self._assembly_track,
        )

        if (
                self._history_index >= 0
                and self._navigation_history[
            self._history_index
        ] == destination
        ):
            return

        # If we went Back and then choose
        # somewhere new, discard the old
        # Forward branch.
        if (
                self._history_index
                < len(
            self._navigation_history
        ) - 1
        ):
            self._navigation_history = (
                self._navigation_history[
                    :self._history_index + 1
                ]
            )

        self._navigation_history.append(
            destination
        )

        self._history_index = (
                len(self._navigation_history) - 1
        )

        self._update_history_buttons()

    def _go_back(
            self,
    ) -> None:
        if self._history_index <= 0:
            return

        self._history_index -= 1

        self._replay_history_destination()


    def _go_forward(
            self,
    ) -> None:
        if (
                self._history_index
                >= len(
            self._navigation_history
        ) - 1
        ):
            return

        self._history_index += 1

        self._replay_history_destination()

    def _replay_history_destination(
            self,
    ) -> None:
        if not (
                0
                <= self._history_index
                < len(
            self._navigation_history
        )
        ):
            return

        node_type, node_id, track_id = (
            self._navigation_history[
                self._history_index
            ]
        )

        self._replaying_history = True

        try:
            self._set_assembly_track(track_id)
            self._navigate_to_node(
                node_type,
                node_id,
            )

        finally:
            self._replaying_history = False

        self._update_history_buttons()

    def _update_history_buttons(
            self,
    ) -> None:
        self._back_button.setEnabled(
            self._history_index > 0
        )

        self._forward_button.setEnabled(
            (
                    self._history_index >= 0
                    and self._history_index
                    < len(
                self._navigation_history
            ) - 1
            )
        )
    def _language_in_mode(self, language_id):
        language = self._language_service.get_language_by_id(language_id)
        return language is not None and language.language_kind == self._language_kind

    def _set_language_kind(self, kind, *, force=False):
        if kind not in ("programming", "natural"):
            return False
        # An editor owns its draft until Save or Cancel. Modal dialogs also block
        # mouse/keyboard access to this bar; guard direct/queued calls as well.
        modal = QApplication.activeModalWidget()
        if modal is not None and modal is not self:
            self._mode_buttons[self._language_kind].setChecked(True)
            modal.raise_()
            modal.setFocus()
            return False
        if kind == self._language_kind and not force:
            self._mode_buttons[kind].setChecked(True)
            return True
        self._language_kind = kind
        self._navigation_model.language_kind = kind
        self._mode_buttons[kind].setChecked(True)
        self._set_assembly_track(None)
        with QSignalBlocker(self._search_field):
            self._search_field.clear()
        self._navigation_history.clear()
        self._history_index = -1
        self._update_history_buttons()
        self._navigation_model.reload()
        self._refresh_search_languages()
        self._assembly_track_filter.hide()
        self._import_json_button.setVisible(kind == "programming")
        self._search_field.setPlaceholderText("Search languages, categories, notes…" if kind == "natural" else "Search languages, packages, entries...")
        self._search("")
        self._content_stack.setCurrentWidget(self._welcome_page)
        self._settings.setValue("library/languageKind", kind)
        self._settings.sync()
        return True

    def _edit_language(self, language_id):
        language = self._language_service.get_language_by_id(language_id)
        if language is None or not self._language_in_mode(language_id):
            return
        dialog = LanguageEditorDialog(self._language_service, self, language=language)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._navigation_model.reload()
            self._refresh_search_languages()
            self._show_language(language_id)

    def _edit_category(self, category_id):
        category = self._category_service.get_category_by_id(category_id)
        if category is None or not self._language_in_mode(category.language_id):
            return
        dialog = CategoryEditorDialog(self._category_service, category.language_id, self, category=category)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._navigation_model.reload()
            self._show_category(category_id)
