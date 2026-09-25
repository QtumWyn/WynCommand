from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
)
from PySide6.QtCore import Qt

from wyncodex.services.package_service import (
    PackageService,
)


class PackageEditorDialog(QDialog):
    def __init__(
            self,
            package_service: PackageService,
            category_id: int,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self._package_service = package_service
        self._category_id = category_id

        self.setWindowTitle("Add Package")
        self.resize(500, 400)

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self._name_field = QLineEdit()
        self._summary_field = QLineEdit()
        self._description_field = QTextEdit()
        self._description_field.setLineWrapMode(
            QTextEdit.LineWrapMode.WidgetWidth
        )

        self._description_field.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self._summary_field.setPlaceholderText(
            "e.g. Plotting, charts"
        )

        self._description_field.setMaximumHeight(
            140
        )

        form.addRow(
            "Name",
            self._name_field,
        )

        form.addRow(
            "Summary",
            self._summary_field,
        )

        form.addRow(
            "Description",
            self._description_field,
        )

        self._message_label = QLabel()
        self._message_label.setObjectName(
            "validationLabel"
        )
        self._message_label.setWordWrap(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        save_button = buttons.button(
            QDialogButtonBox.StandardButton.Save
        )

        save_button.setObjectName(
            "primaryButton"
        )

        buttons.accepted.connect(
            self._save
        )

        buttons.rejected.connect(
            self.reject
        )

        layout.addLayout(form)

        layout.addWidget(
            self._message_label
        )

        layout.addWidget(buttons)

        self._name_field.setFocus()

    def _save(self) -> None:
        try:
            self._package_service.create_package(
                category_id=self._category_id,
                name=self._name_field.text(),
                summary=self._summary_field.text(),
                description=(
                    self._description_field
                    .toPlainText()
                ),
            )

        except ValueError as error:
            self._message_label.setText(
                str(error)
            )
            return

        self.accept()