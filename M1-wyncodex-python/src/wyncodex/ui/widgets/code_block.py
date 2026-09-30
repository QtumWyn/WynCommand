from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPlainTextEdit,
    QSizePolicy,
    QVBoxLayout,
)

from wyncodex.ui.widgets.code_highlighter import (
    PygmentsHighlighter,
)


class CodeBlock(QFrame):
    def __init__(
            self,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName(
            "codeBlock"
        )

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            12,
            10,
            12,
            10,
        )

        layout.setSpacing(6)

        self._language_label = QLabel()
        self._language_label.setObjectName(
            "codeLanguage"
        )

        self._editor = QPlainTextEdit()

        self._editor.setObjectName(
            "codeViewer"
        )

        self._editor.setReadOnly(True)

        self._editor.setLineWrapMode(
            QPlainTextEdit.LineWrapMode.NoWrap
        )

        self._editor.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        layout.addWidget(
            self._language_label
        )

        layout.addWidget(
            self._editor
        )

        self._highlighter = (
            PygmentsHighlighter(
                self._editor.document()
            )
        )

    def set_code(
            self,
            code: str,
            syntax_hint: str | None = None,
            label: str | None = None,
    ) -> None:
        self._editor.setPlainText(code)

        self._language_label.setText(
            label
            or (
                syntax_hint.upper()
                if syntax_hint
                else "TEXT"
            )
        )

        self._highlighter.set_syntax_hint(
            syntax_hint
        )

        line_count = max(
            1,
            code.count("\n") + 1,
            )

        visible_lines = min(
            max(line_count, 1),
            14,
        )

        line_height = (
            self._editor.fontMetrics()
            .lineSpacing()
        )

        self._editor.setFixedHeight(
            visible_lines * line_height
            + 20
        )

        self.updateGeometry()