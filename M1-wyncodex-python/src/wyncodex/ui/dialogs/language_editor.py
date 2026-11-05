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

from wyncodex.services.language_service import LanguageService


from wyncodex.ui.dialogs.guarded_dialog import GuardedDialog


class LanguageEditorDialog(GuardedDialog):
    def __init__(
            self,
            language_service: LanguageService,
            parent=None,
            *, language_kind="programming", language=None,
    ) -> None:
        super().__init__(parent)

        self._language_service = language_service
        self._language = language
        self._language_kind = language.language_kind if language else language_kind

        self.setWindowTitle("Add Language")
        self.resize(460, 320)

        self._build_ui()
        self.setWindowTitle(("Edit" if language else "Add") + (" Natural Language" if self._language_kind == "natural" else " Programming Language"))
        if language:
            self._name_field.setText(language.name)
            self._description_field.setPlainText(language.description or "")
        self.remember_initial_state()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self._name_field = QLineEdit()
        self._description_field = QTextEdit()
        self._description_field.setLineWrapMode(
            QTextEdit.LineWrapMode.WidgetWidth
        )

        self._description_field.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self._description_field.setMaximumHeight(100)

        form.addRow("Name", self._name_field)
        form.addRow("Description", self._description_field)

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

        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)

        layout.addLayout(form)
        layout.addWidget(self._message_label)
        layout.addWidget(buttons)

        self._name_field.setFocus()

    def _save(self) -> None:
        try:
            values = dict(name=self._name_field.text(), description=self._description_field.toPlainText())
            if self._language:
                self._language_service.update_language(self._language.id, **values)
            else:
                self._language_service.create_language(language_kind=self._language_kind, **values)

        except ValueError as error:
            self._message_label.setText(str(error))
            return

        self.accept()