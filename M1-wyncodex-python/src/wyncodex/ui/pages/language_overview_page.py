from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout
from wyncodex.domain.language import Language
from wyncodex.domain.category import Category
from wyncodex.ui.widgets.overview_card import OverviewCard


class LanguageOverviewPage(QWidget):
    add_category_requested = Signal(int)
    category_selected = Signal(int)
    def __init__(self) -> None:
        super().__init__()

        self._language: Language | None = None

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

        self._add_category_button = QPushButton(
            "+ CATEGORY"
        )

        self._add_category_button.setObjectName(
            "primaryButton"
        )

        self._edit_language_button = QPushButton(
            "EDIT LANGUAGE"
        )

        self._add_category_button.clicked.connect(
            self._request_add_category
        )

        # We'll wire these up in the next slices.
        self._edit_language_button.setEnabled(False)

        button_row.addWidget(
            self._add_category_button
        )

        button_row.addWidget(
            self._edit_language_button
        )

        button_row.addStretch()

        layout.addWidget(self._title_label)
        layout.addWidget(self._description_label)

        layout.addSpacing(12)

        layout.addLayout(button_row)

        children_label = QLabel(
            "CATEGORIES"
        )

        children_label.setObjectName(
            "sectionLabel"
        )

        self._category_grid = QGridLayout()

        self._category_grid.setHorizontalSpacing(
            12
        )

        self._category_grid.setVerticalSpacing(
            12
        )

        layout.addSpacing(18)

        layout.addWidget(
            children_label
        )

        layout.addLayout(
            self._category_grid
        )

        layout.addStretch()

    def set_language(
            self,
            language: Language,
            categories: list[Category],
    ) -> None:
        self._language = language

        self._title_label.setText(
            language.name.upper()
        )

        description = (
                language.description
                or "No description yet."
        )

        self._description_label.setText(
            description
        )
        self._add_category_button.setEnabled(
            language.id is not None
        )
        self._populate_categories(
            categories
        )

    def _request_add_category(self) -> None:
        if (
                self._language is None
                or self._language.id is None
        ):
            return

        self.add_category_requested.emit(
            self._language.id
        )

    def _populate_categories(
            self,
            categories: list[Category],
    ) -> None:
        self._clear_category_grid()

        for index, category in enumerate(
                categories
        ):
            if category.id is None:
                continue

            card = OverviewCard(
                item_id=category.id,
                title=category.name,
                description=category.description,
            )

            card.clicked.connect(
                self.category_selected.emit
            )

            row = index // 2
            column = index % 2

            self._category_grid.addWidget(
                card,
                row,
                column,
            )


    def _clear_category_grid(self) -> None:
        while self._category_grid.count():
            item = self._category_grid.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()