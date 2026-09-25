from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Signal

from wyncodex.domain.entry import Entry
from PySide6.QtWidgets import (
    QScrollArea,
)

from wyncodex.domain.argument import Argument
from wyncodex.domain.example import Example

from wyncodex.ui.widgets.argument_display import (
    ArgumentDisplayWidget,
)

from wyncodex.ui.widgets.example_display import (
    ExampleDisplayWidget,
)

from wyncodex.ui.widgets.code_block import (
    CodeBlock,
)


class EntryDetailPage(QWidget):
    edit_requested = Signal(int)
    def __init__(self) -> None:
        super().__init__()

        self._entry: Entry | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout(self)

        root_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()

        layout = QVBoxLayout(content)

        layout.setContentsMargins(
            40,
            36,
            40,
            36,
        )

        layout.setSpacing(14)

        scroll.setWidget(content)

        root_layout.addWidget(scroll)

        context = QLabel("ENTRY")
        context.setObjectName(
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
        self._summary_label.setWordWrap(True)

        self._edit_button = QPushButton(
            "EDIT ENTRY"
        )
        self._edit_button.clicked.connect(
            self._request_edit
        )

        layout.addWidget(context)
        layout.addWidget(
            self._title_label
        )

        layout.addWidget(
            self._summary_label
        )

        layout.addWidget(
            self._edit_button
        )

        self._signature_title = self._section_label(
            "SIGNATURE"
        )
        self._signature_block = CodeBlock()

        self._definition_title = self._section_label(
            "DEFINITION"
        )
        self._definition_label = self._content_label()

        self._mental_model_title = self._section_label(
            "MENTAL MODEL"
        )
        self._mental_model_label = self._content_label()

        self._return_title = self._section_label(
            "RETURN VALUE"
        )
        self._return_label = self._content_label()

        self._gotchas_title = self._section_label(
            "GOTCHAS"
        )
        self._gotchas_label = self._content_label()

        self._notes_title = self._section_label(
            "NOTES"
        )
        self._notes_label = self._content_label()

        self._arguments_title = (
            self._section_label(
                "ARGUMENTS"
            )
        )

        self._arguments_container = QWidget()

        self._arguments_layout = QVBoxLayout(
            self._arguments_container
        )

        self._arguments_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self._examples_title = (
            self._section_label(
                "EXAMPLES"
            )
        )

        self._examples_container = QWidget()

        self._examples_layout = QVBoxLayout(
            self._examples_container
        )

        self._examples_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        sections = (
            (
                self._definition_title,
                self._definition_label,
            ),
            (
                self._mental_model_title,
                self._mental_model_label,
            ),
            (
                self._return_title,
                self._return_label,
            ),
            (
                self._gotchas_title,
                self._gotchas_label,
            ),
            (
                self._notes_title,
                self._notes_label,
            ),
        )

        layout.addSpacing(12)

        layout.addWidget(
            self._signature_title
        )

        layout.addWidget(
            self._signature_block
        )

        for title, content in sections:
            layout.addSpacing(12)
            layout.addWidget(title)
            layout.addWidget(content)

        layout.addSpacing(18)
        layout.addWidget(
            self._arguments_title
        )
        layout.addWidget(
            self._arguments_container
        )

        layout.addSpacing(18)
        layout.addWidget(
            self._examples_title
        )
        layout.addWidget(
            self._examples_container
        )

        layout.addStretch()

    @staticmethod
    def _section_label(
            text: str,
    ) -> QLabel:
        label = QLabel(text)

        label.setObjectName(
            "entrySectionHeader"
        )

        return label

    @staticmethod
    def _content_label() -> QLabel:
        label = QLabel()

        label.setObjectName(
            "entryBody"
        )

        label.setWordWrap(True)

        return label

    def set_entry(
            self,
            entry: Entry,
            arguments: list[Argument],
            examples: list[Example],
            syntax_hint: str | None,
    ) -> None:
        self._entry = entry

        self._title_label.setText(
            entry.title
        )

        self._summary_label.setText(
            entry.summary or ""
        )

        self._summary_label.setVisible(
            bool(entry.summary)
        )

        self._set_section(
            self._definition_title,
            self._definition_label,
            entry.definition,
        )

        self._set_section(
            self._mental_model_title,
            self._mental_model_label,
            entry.mental_model,
        )

        self._set_section(
            self._return_title,
            self._return_label,
            entry.return_value,
        )

        self._set_section(
            self._gotchas_title,
            self._gotchas_label,
            entry.gotchas,
        )

        self._set_section(
            self._notes_title,
            self._notes_label,
            entry.notes,
        )

        has_signature = bool(
            entry.signature
        )

        self._signature_title.setVisible(
            has_signature
        )

        self._signature_block.setVisible(
            has_signature
        )

        if entry.signature:
            self._signature_block.set_code(
                entry.signature,
                syntax_hint,
            )

        self._populate_arguments(
            arguments
        )

        self._populate_examples(
            examples
        )

        self._edit_button.setEnabled(
            entry.id is not None
        )

    @staticmethod
    def _set_section(
            title: QLabel,
            content: QLabel,
            value: str | None,
    ) -> None:
        visible = bool(value)

        title.setVisible(visible)
        content.setVisible(visible)

        content.setText(
            value or ""
        )

    def _populate_arguments(
            self,
            arguments: list[Argument],
    ) -> None:
        self._clear_layout(
            self._arguments_layout
        )

        self._arguments_title.setVisible(
            bool(arguments)
        )

        self._arguments_container.setVisible(
            bool(arguments)
        )

        for argument in arguments:
            self._arguments_layout.addWidget(
                ArgumentDisplayWidget(
                    argument
                )
            )

    def _populate_examples(
            self,
            examples: list[Example],
    ) -> None:
        self._clear_layout(
            self._examples_layout
        )

        self._examples_title.setVisible(
            bool(examples)
        )

        self._examples_container.setVisible(
            bool(examples)
        )

        for example in examples:
            self._examples_layout.addWidget(
                ExampleDisplayWidget(
                    example
                )
            )

    @staticmethod
    def _clear_layout(
            layout: QVBoxLayout,
    ) -> None:
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def _request_edit(self) -> None:
        if (
                self._entry is None
                or self._entry.id is None
        ):
            return

        self.edit_requested.emit(
            self._entry.id
        )