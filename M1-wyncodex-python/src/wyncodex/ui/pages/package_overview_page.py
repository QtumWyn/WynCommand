from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout

from wyncodex.domain.entry import Entry
from wyncodex.ui.widgets.overview_card import OverviewCard

from wyncodex.domain.package import Package


class PackageOverviewPage(QWidget):
    add_entry_requested = Signal(
        int,
        int,
    )

    entry_selected = Signal(int)
    def __init__(self) -> None:
        super().__init__()

        self._package: Package | None = None

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

        self._context_label = QLabel(
            "PACKAGE"
        )
        self._context_label.setObjectName(
            "breadcrumbLabel"
        )

        self._title_label = QLabel()
        self._title_label.setObjectName(
            "pageTitle"
        )

        self._summary_label = QLabel()
        self._summary_label.setObjectName(
            "pageSummary"
        )

        self._description_label = QLabel()
        self._description_label.setObjectName(
            "pageDescription"
        )
        self._description_label.setWordWrap(True)

        button_row = QHBoxLayout()

        self._add_entry_button = QPushButton(
            "+ ENTRY"
        )
        self._add_entry_button.setObjectName(
            "primaryButton"
        )

        self._edit_package_button = QPushButton(
            "EDIT PACKAGE"
        )

        self._add_entry_button.clicked.connect(
            self._request_add_entry
        )

        self._edit_package_button.setEnabled(False)

        button_row.addWidget(
            self._add_entry_button
        )

        button_row.addWidget(
            self._edit_package_button
        )

        button_row.addStretch()

        layout.addWidget(
            self._context_label
        )

        layout.addWidget(
            self._title_label
        )

        layout.addWidget(
            self._summary_label
        )

        layout.addWidget(
            self._description_label
        )

        layout.addSpacing(12)

        layout.addLayout(
            button_row
        )

        entries_label = QLabel(
            "ENTRIES"
        )

        entries_label.setObjectName(
            "sectionLabel"
        )

        self._entry_grid = QGridLayout()
        self._entry_grid.setHorizontalSpacing(12)
        self._entry_grid.setVerticalSpacing(12)

        layout.addSpacing(18)
        layout.addWidget(
            entries_label
        )
        layout.addLayout(
            self._entry_grid
        )

        layout.addStretch()

    def set_package(
            self,
            package: Package,
            entries: list[Entry],
    ) -> None:
        self._package = package

        self._title_label.setText(
            package.name.upper()
        )

        self._summary_label.setText(
            package.summary
            or ""
        )

        self._summary_label.setVisible(
            bool(package.summary)
        )

        self._description_label.setText(
            package.description
            or "No description yet."
        )

        self._add_entry_button.setEnabled(
            package.id is not None
        )

        self._populate_entries(entries)

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

    def _request_add_entry(self) -> None:
        if (
                self._package is None
                or self._package.id is None
        ):
            return

        self.add_entry_requested.emit(
            self._package.category_id,
            self._package.id,
        )