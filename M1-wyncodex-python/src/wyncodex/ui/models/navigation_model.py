from enum import IntEnum

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel

from wyncodex.services.category_service import CategoryService
from wyncodex.services.language_service import LanguageService
from wyncodex.services.package_service import PackageService
from wyncodex.services.entry_service import EntryService


NODE_TYPE_ROLE = int(Qt.ItemDataRole.UserRole) + 1
NODE_ID_ROLE = int(Qt.ItemDataRole.UserRole) + 2


class NavigationNodeType(IntEnum):
    LANGUAGE = 1
    CATEGORY = 2
    PACKAGE = 3
    ENTRY = 4


class NavigationModel(QStandardItemModel):
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

        self.setHorizontalHeaderLabels(["Codex"])

    def reload(self) -> None:
        self.clear()
        self.setHorizontalHeaderLabels(["Codex"])

        languages = self._language_service.get_all_languages()

        for language in languages:
            if language.id is None:
                continue

            language_item = QStandardItem(
                language.name
            )

            self._configure_item(
                language_item,
                NavigationNodeType.LANGUAGE,
                language.id,
            )

            categories = (
                self._category_service
                .get_categories_for_language(
                    language.id
                )
            )

            for category in categories:
                if category.id is None:
                    continue

                category_item = QStandardItem(
                    category.name
                )

                self._configure_item(
                    category_item,
                    NavigationNodeType.CATEGORY,
                    category.id,
                )

                direct_entries = (
                    self._entry_service
                    .get_direct_entries_for_category(
                        category.id
                    )
                )

                for entry in direct_entries:
                    if entry.id is None:
                        continue

                    entry_item = QStandardItem(
                        entry.title
                    )

                    self._configure_item(
                        entry_item,
                        NavigationNodeType.ENTRY,
                        entry.id,
                    )

                    category_item.appendRow(
                        entry_item
                    )

                packages = (
                    self._package_service
                    .get_packages_for_category(
                        category.id
                    )
                )

                for package in packages:
                    if package.id is None:
                        continue

                    label = package.name

                    if package.summary:
                        label += (
                            f" · {package.summary}"
                        )

                    package_item = QStandardItem(
                        label
                    )

                    self._configure_item(
                        package_item,
                        NavigationNodeType.PACKAGE,
                        package.id,
                    )

                    entries = (
                        self._entry_service
                        .get_entries_for_package(
                            package.id
                        )
                    )

                    for entry in entries:
                        if entry.id is None:
                            continue

                        entry_item = QStandardItem(
                            entry.title
                        )

                        self._configure_item(
                            entry_item,
                            NavigationNodeType.ENTRY,
                            entry.id,
                        )

                        package_item.appendRow(
                            entry_item
                        )

                    if package.description:
                        package_item.setToolTip(
                            package.description
                        )

                    category_item.appendRow(
                        package_item
                    )

                language_item.appendRow(
                    category_item
                )

            self.appendRow(
                language_item
            )

    @staticmethod
    def _configure_item(
            item: QStandardItem,
            node_type: NavigationNodeType,
            node_id: int,
    ) -> None:
        item.setEditable(False)

        item.setData(
            int(node_type),
            NODE_TYPE_ROLE,
        )

        item.setData(
            node_id,
            NODE_ID_ROLE,
        )