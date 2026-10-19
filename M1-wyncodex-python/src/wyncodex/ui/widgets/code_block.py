from math import ceil

from PySide6.QtCore import (
    Qt,
    QTimer,
)

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


SYNTAX_LABELS: dict[str, str] = {
    "csharp": "C#",
    "c-sharp": "C#",
    "c#": "C#",

    "cpp": "C++",
    "c-plus-plus": "C++",
    "c++": "C++",

    "fsharp": "F#",
    "f-sharp": "F#",
    "f#": "F#",

    "javascript": "JAVASCRIPT",
    "typescript": "TYPESCRIPT",
    "powershell": "POWERSHELL",
    "nasm": "NASM",
}


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

        self._editor.setReadOnly(
            True
        )

        self._editor.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self._editor.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

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
        self._editor.setPlainText(
            code
        )

        if label is not None:
            display_label = label

        elif syntax_hint:
            normalized_hint = (
                syntax_hint
                .strip()
                .lower()
            )

            display_label = (
                SYNTAX_LABELS.get(
                    normalized_hint,
                    syntax_hint.upper(),
                )
            )

        else:
            display_label = "TEXT"

        self._language_label.setText(
            display_label
        )

        self._highlighter.set_syntax_hint(
            syntax_hint
        )

        self._resize_to_contents()

        # Run once more after Qt has resolved
        # whether a horizontal scrollbar is needed.
        QTimer.singleShot(
            0,
            self._resize_to_contents,
        )

    def _resize_to_contents(
            self,
    ) -> None:
        line_count = max(
            1,
            self._editor
            .document()
            .blockCount(),
            )

        line_height = (
            self._editor
            .fontMetrics()
            .lineSpacing()
        )

        document_margin = (
            self._editor
            .document()
            .documentMargin()
        )

        frame_height = (
                self._editor.frameWidth()
                * 2
        )

        contents_margins = (
            self._editor.contentsMargins()
        )

        widget_margins_height = (
                contents_margins.top()
                + contents_margins.bottom()
        )

        horizontal_scrollbar_height = 0

        horizontal_scrollbar = (
            self._editor
            .horizontalScrollBar()
        )

        if horizontal_scrollbar.isVisible():
            horizontal_scrollbar_height = (
                horizontal_scrollbar
                .sizeHint()
                .height()
            )

        # A little breathing room also protects
        # against stylesheet padding/font rounding.
        extra_padding = 16

        target_height = ceil(
            line_count * line_height
            + document_margin * 2
            + frame_height
            + widget_margins_height
            + horizontal_scrollbar_height
            + extra_padding
        )

        self._editor.setFixedHeight(
            target_height
        )