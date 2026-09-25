from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from wyncodex.domain.category import Category
from wyncodex.domain.package import Package
from wyncodex.ui.widgets.overview_card import OverviewCard
from wyncodex.domain.entry import Entry


class CategoryOverviewPage(QWidget):
    add_package_requested = Signal(int)
    package_selected = Signal(int)
    add_entry_requested = Signal(int)
    entry_selected = Signal(int)

    def __init__(self) -> None:
        super().__init__()

        self._category: Category | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            40,
            36,
            40,
            36,
        )

        layout.setSpacing(14)

        self._context_label = QLabel("CATEGORY")
        self._context_label.setObjectName(
            "breadcrumbLabel"
        )

        self._title_label = QLabel()
        self._title_label.setObjectName(
            "pageTitle"
        )

        self._description_label = QLabel()
        self._description_label.setObjectName(
            "pageDescription"
        )
        self._description_label.setWordWrap(True)

        button_row = QHBoxLayout()

        self._add_package_button = QPushButton(
            "+ PACKAGE"
        )

        self._add_entry_button = QPushButton(
            "+ ENTRY"
        )

        self._add_entry_button.setObjectName(
            "accentButton"
        )

        self._add_entry_button.clicked.connect(
            self._request_add_entry
        )

        button_row.addWidget(
            self._add_entry_button
        )

        self._add_package_button.setObjectName(
            "primaryButton"
        )
        self._add_package_button.clicked.connect(
            self._request_add_package
        )

        self._edit_category_button = QPushButton(
            "EDIT CATEGORY"
        )
        self._edit_category_button.setEnabled(False)

        button_row.addWidget(
            self._add_package_button
        )
        button_row.addWidget(
            self._edit_category_button
        )
        button_row.addStretch()

        children_label = QLabel("PACKAGES")
        children_label.setObjectName(
            "sectionLabel"
        )

        self._package_grid = QGridLayout()
        self._package_grid.setHorizontalSpacing(12)
        self._package_grid.setVerticalSpacing(12)

        entries_label = QLabel(
            "ENTRIES"
        )

        entries_label.setObjectName(
            "sectionLabel"
        )

        self._entry_grid = QGridLayout()
        self._entry_grid.setHorizontalSpacing(12)
        self._entry_grid.setVerticalSpacing(12)

        layout.addWidget(self._context_label)
        layout.addWidget(self._title_label)
        layout.addWidget(self._description_label)

        layout.addSpacing(12)
        layout.addLayout(button_row)

        layout.addSpacing(18)
        layout.addWidget(children_label)
        layout.addLayout(self._package_grid)

        layout.addSpacing(18)
        layout.addWidget(entries_label)
        layout.addLayout(self._entry_grid)

        layout.addStretch()

    def set_category(
            self,
            category: Category,
            packages: list[Package],
            entries: list[Entry],
    ) -> None:
        self._category = category

        self._title_label.setText(
            category.name.upper()
        )

        self._description_label.setText(
            category.description
            or "No description yet."
        )

        self._add_package_button.setEnabled(
            category.id is not None
        )

        self._populate_packages(packages)

        self._add_entry_button.setEnabled(
            category.id is not None
        )

        self._populate_entries(entries)

    def _request_add_package(self) -> None:
        if (
                self._category is None
                or self._category.id is None
        ):
            return

        self.add_package_requested.emit(
            self._category.id
        )

    def _populate_packages(
            self,
            packages: list[Package],
    ) -> None:
        self._clear_package_grid()

        for index, package in enumerate(packages):
            if package.id is None:
                continue

            card = OverviewCard(
                item_id=package.id,
                title=package.name,
                description=(
                        package.summary
                        or package.description
                ),
            )

            card.clicked.connect(
                self.package_selected.emit
            )

            row = index // 2
            column = index % 2

            self._package_grid.addWidget(
                card,
                row,
                column,
            )

    def _clear_package_grid(self) -> None:
        while self._package_grid.count():
            item = self._package_grid.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def _request_add_entry(self) -> None:
        if (
                self._category is None
                or self._category.id is None
        ):
            return

        self.add_entry_requested.emit(
            self._category.id
        )

    def _populate_entries(
            self,
            entries: list[Entry],
    ) -> None:
        self._clear_entry_grid()

        for index, entry in enumerate(entries):
            if entry.id is None:
                continue

            card = OverviewCard(
                item_id=entry.id,
                title=entry.title,
                description=(
                        entry.summary
                        or entry.definition
                ),
            )

            card.clicked.connect(
                self.entry_selected.emit
            )

            row = index // 2
            column = index % 2

            self._entry_grid.addWidget(
                card,
                row,
                column,
            )


    def _clear_entry_grid(self) -> None:
        while self._entry_grid.count():
            item = self._entry_grid.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()