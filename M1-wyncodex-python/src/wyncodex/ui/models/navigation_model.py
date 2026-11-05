from wyncodex.services.assembly_service import TRACKS
from enum import IntEnum

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel

from wyncodex.services.category_service import CategoryService
from wyncodex.services.language_service import LanguageService
from wyncodex.services.package_service import PackageService
from wyncodex.services.entry_service import EntryService


NODE_TYPE_ROLE = int(Qt.ItemDataRole.UserRole) + 1
NODE_ID_ROLE = int(Qt.ItemDataRole.UserRole) + 2
TRACK_ID_ROLE = int(Qt.ItemDataRole.UserRole) + 3


class NavigationNodeType(IntEnum):
    LANGUAGE = 1
    CATEGORY = 2
    PACKAGE = 3
    ENTRY = 4
    TRACK = 5


class NavigationModel(QStandardItemModel):
    def __init__(
            self,
            language_service: LanguageService,
            category_service: CategoryService,
            package_service: PackageService,
            entry_service: EntryService,
            assembly_service=None,
    ) -> None:
        super().__init__()

        self._language_service = language_service
        self._category_service = category_service
        self._package_service = package_service
        self._entry_service = entry_service
        self._assembly_service = assembly_service
        self.language_kind = "programming"
        self._building_track = None

        self.setHorizontalHeaderLabels(["Codex"])

    def reload(self) -> None:
        self.clear()
        self.setHorizontalHeaderLabels(["Codex"])

        languages = self._language_service.get_all_languages(self.language_kind)

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

            if language.slug == "nasm" and self._assembly_service:
                for track in TRACKS:
                    self._building_track = track.id
                    track_item = QStandardItem(track.name)
                    self._configure_item(track_item, NavigationNodeType.TRACK, track.id)
                    track_item.setToolTip(track.description)
                    self._append_categories(track_item, categories, self._assembly_service.category_ids(track.id))
                    language_item.appendRow(track_item)
                self._building_track = None
            else:
                self._append_categories(language_item, categories)

            self.appendRow(
                language_item
            )

    def _append_categories(self, parent_item, categories, allowed_categories=None):
        for category in categories:
            if allowed_categories is not None and category.id not in allowed_categories:
                continue
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
                self._append_entry_tree(
                    category_item,
                    entry,
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
                    self._append_entry_tree(
                        package_item,
                        entry,
                    )

                if package.description:
                    package_item.setToolTip(
                        package.description
                    )

                if allowed_categories is None or package_item.rowCount():
                    category_item.appendRow(package_item)

            parent_item.appendRow(
                category_item
            )

    def _configure_item(
            self,
            item: QStandardItem,
            node_type: NavigationNodeType,
            node_id: int,
    ) -> None:
        item.setEditable(False)
        item.setData(self._building_track, TRACK_ID_ROLE)

        item.setData(
            int(node_type),
            NODE_TYPE_ROLE,
        )

        item.setData(
            node_id,
            NODE_ID_ROLE,
        )

    def _append_entry_tree(
            self,
            parent_item: QStandardItem,
            entry,
    ) -> None:
        if entry.id is None:
            return
        if self._building_track is not None and entry.id not in self._assembly_service.entry_ids(self._building_track):
            return

        label = entry.title

        if entry.entry_kind != "entry":
            label += (
                f"  · {entry.entry_kind}"
            )

        entry_item = QStandardItem(
            label
        )

        self._configure_item(
            entry_item,
            NavigationNodeType.ENTRY,
            entry.id,
        )

        parent_item.appendRow(
            entry_item
        )

        children = (
            self._entry_service
            .get_child_entries(
                entry.id
            )
        )

        for child in children:
            self._append_entry_tree(
                entry_item,
                child,
            )