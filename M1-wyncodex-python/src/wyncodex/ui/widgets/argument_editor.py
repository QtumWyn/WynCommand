from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtGui import QTextOption
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from wyncodex.domain.argument import (
    Argument,
    ArgumentDraft,
)


class ArgumentEditorWidget(QFrame):
    remove_requested = Signal(object)

    def __init__(
            self,
            argument: Argument | None = None,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName(
            "editorCard"
        )

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self._name_field = QLineEdit()
        self._type_field = QLineEdit()
        self._default_field = QLineEdit()

        self._required_field = QCheckBox()
        self._required_field.setChecked(True)

        self._description_field = QTextEdit()

        self._description_field.setMaximumHeight(
            80
        )

        self._description_field.setLineWrapMode(
            QTextEdit.LineWrapMode.WidgetWidth
        )

        self._description_field.setWordWrapMode(
            QTextOption.WrapMode
            .WrapAtWordBoundaryOrAnywhere
        )

        self._description_field.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        form.addRow(
            "Name",
            self._name_field,
        )

        form.addRow(
            "Type",
            self._type_field,
        )

        form.addRow(
            "Required",
            self._required_field,
        )

        form.addRow(
            "Default",
            self._default_field,
        )

        form.addRow(
            "Description",
            self._description_field,
        )

        remove_button = QPushButton(
            "REMOVE"
        )

        remove_button.clicked.connect(
            lambda: self.remove_requested.emit(
                self
            )
        )

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(
            remove_button
        )

        layout.addLayout(form)
        layout.addLayout(buttons)

        if argument is not None:
            self._name_field.setText(
                argument.name
            )

            self._type_field.setText(
                argument.type_text or ""
            )

            self._required_field.setChecked(
                argument.required
            )

            self._default_field.setText(
                argument.default_value or ""
            )

            self._description_field.setPlainText(
                argument.description or ""
            )

    def to_draft(
            self,
    ) -> ArgumentDraft:
        return ArgumentDraft(
            name=self._name_field.text(),
            type_text=self._type_field.text(),
            description=(
                self._description_field
                .toPlainText()
            ),
            required=(
                self._required_field
                .isChecked()
            ),
            default_value=(
                self._default_field.text()
            ),
        )