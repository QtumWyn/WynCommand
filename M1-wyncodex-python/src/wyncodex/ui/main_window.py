from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTreeView,
    QVBoxLayout,
    QWidget,
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


class MainWindow(QMainWindow):
    def __init__(
            self,
            language_service: LanguageService,
            category_service: CategoryService,
            package_service: PackageService,
            entry_service: EntryService,
    ) -> None:
        super().__init__()

        self._language_service = language_service
        self._category_service = category_service
        self._package_service = package_service
        self._entry_service = entry_service

        self.setWindowTitle("WynCodex")
        self.resize(1100, 700)

        self._navigation_model = NavigationModel(
            language_service,
            category_service,
            package_service,
            entry_service,
        )

        self._build_ui()

        self._navigation_model.reload()
        self._language_tree.expandAll()

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("centralRoot")

        layout = QVBoxLayout(root)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        stripe = QFrame()
        stripe.setObjectName("transStripe")
        stripe.setFixedHeight(3)

        splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        left_panel = self._build_left_panel()
        right_panel = self._build_right_panel()

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(stripe)
        layout.addWidget(splitter)

        self.setCentralWidget(root)

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("navigationPanel")

        layout = QVBoxLayout(panel)

        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("LANGUAGES")
        title.setObjectName("sectionLabel")

        self._language_tree = QTreeView()

        self._language_tree.setModel(
            self._navigation_model
        )

        self._language_tree.selectionModel().currentChanged.connect(
            self._on_navigation_changed
        )

        self._language_tree.setHeaderHidden(True)

        add_language_button = QPushButton(
            "+ LANGUAGE"
        )

        add_language_button.setObjectName(
            "accentButton"
        )

        add_language_button.clicked.connect(
            self._open_language_editor
        )

        layout.addWidget(title)
        layout.addWidget(self._language_tree)
        layout.addWidget(add_language_button)

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

        raw_node_type = current.data(
            NODE_TYPE_ROLE
        )

        node_id = current.data(
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
            self._language_tree.expandAll()

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
        index = self._find_navigation_index(
            node_type,
            node_id,
        )

        if not index.isValid():
            return

        parent = index.parent()

        while parent.isValid():
            self._language_tree.expand(
                parent
            )
            parent = parent.parent()

        self._language_tree.setCurrentIndex(
            index
        )

        self._language_tree.scrollTo(
            index
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