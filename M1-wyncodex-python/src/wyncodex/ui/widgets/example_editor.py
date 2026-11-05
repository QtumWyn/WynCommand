from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtGui import QTextOption
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QFormLayout,
    QLayout,
    QHBoxLayout,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from wyncodex.domain.example import (
    Example,
    ExampleDraft,
)

from wyncodex.ui.widgets.code_highlighter import (
    PygmentsHighlighter,
)


class ExampleEditorWidget(QFrame):
    remove_requested = Signal(object)

    def __init__(
            self,
            default_syntax_hint: str | None = None,
            example: Example | None = None,
            parent=None,
            natural: bool = False,
    ) -> None:
        super().__init__(parent)

        self._natural = natural
        self.setObjectName(
            "editorCard"
        )

        layout = QVBoxLayout(self)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)

        form = QFormLayout()

        self._title_field = QLineEdit()

        self._type_field = QComboBox()
        self._type_field.setEditable(True)

        self._type_field.addItems(
            [
                "basic",
                "practical",
                "wyncommand",
                "edge-case",
                "performance",
            ]
        )

        self._type_field.setCurrentText(
            "practical"
        )

        if natural:
            self._type_field.clear()
            self._type_field.addItems(["example", "phrase", "dialogue", "contrast"])
        self._syntax_field = QLineEdit()

        if default_syntax_hint:
            self._syntax_field.setText(
                default_syntax_hint
            )

        self._code_field = QPlainTextEdit()

        self._code_field.setLineWrapMode(
            QPlainTextEdit.LineWrapMode.NoWrap
        )

        self._code_field.setMinimumHeight(
            140
        )

        self._output_field = QPlainTextEdit()

        self._output_field.setLineWrapMode(
            QPlainTextEdit.LineWrapMode.NoWrap
        )

        self._output_field.setMaximumHeight(
            100
        )

        self._explanation_field = QTextEdit()

        self._explanation_field.setMaximumHeight(
            100
        )

        self._explanation_field.setLineWrapMode(
            QTextEdit.LineWrapMode.WidgetWidth
        )

        self._explanation_field.setWordWrapMode(
            QTextOption.WrapMode
            .WrapAtWordBoundaryOrAnywhere
        )

        self._explanation_field.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        form.addRow(
            "Title",
            self._title_field,
        )

        form.addRow(
            "Type",
            self._type_field,
        )

        form.addRow(
            "Syntax",
            self._syntax_field,
        )

        form.addRow(
            "Original text" if natural else "Code",
            self._code_field,
        )

        form.addRow(
            "Translation" if natural else "Output",
            self._output_field,
        )

        form.addRow(
            "Word-by-word breakdown / notes" if natural else "Explanation",
            self._explanation_field,
        )

        self._explanation_field.setAcceptRichText(False)
        self._romanization_field = QLineEdit()
        self._pronunciation_field = QLineEdit()
        for title, field in [("Romanization (optional)", self._romanization_field), ("Pronunciation (optional)", self._pronunciation_field)]:
            field.setParent(self)
            if natural:
                form.addRow(title, field)
            else:
                field.hide()
        if natural:
            form.setRowVisible(self._syntax_field, False)
            self._syntax_field.setText("text")
            self._code_field.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
            self._output_field.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self._highlighter = PygmentsHighlighter(
            self._code_field.document(),
            self._syntax_field.text(),
        )

        self._syntax_field.textChanged.connect(
            self._highlighter.set_syntax_hint
        )

        if example is not None:
            self._romanization_field.setText(example.romanization or "")
            self._pronunciation_field.setText(example.pronunciation or "")
            self._title_field.setText(
                example.title
            )

            self._type_field.setCurrentText(
                example.example_type
            )

            self._syntax_field.setText(
                example.syntax_hint
                or default_syntax_hint
                or ""
            )

            self._code_field.setPlainText(
                example.code
            )

            self._output_field.setPlainText(
                example.output or ""
            )

            self._explanation_field.setPlainText(
                example.explanation or ""
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
        buttons.addWidget(remove_button)

        layout.addLayout(form)
        layout.addLayout(buttons)

    def to_draft(
            self,
    ) -> ExampleDraft:
        return ExampleDraft(
            title=self._title_field.text(),
            code=self._code_field.toPlainText(),
            output=self._output_field.toPlainText(),
            explanation=(
                self._explanation_field
                .toPlainText()
            ),
            example_type=(
                self._type_field
                .currentText()
            ),
            syntax_hint="text" if self._natural else self._syntax_field.text(),
            romanization=self._romanization_field.text(),
            pronunciation=self._pronunciation_field.text(),
        )