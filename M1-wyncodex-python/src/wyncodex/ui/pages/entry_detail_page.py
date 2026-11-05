from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QScrollArea,
)
from PySide6.QtCore import Signal, Qt
from wyncodex.ui.widgets.natural_example_display import NaturalExampleDisplayWidget
from wyncodex.domain.entry import Entry
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
from wyncodex.ui.widgets.overview_card import (
    OverviewCard,
)

class EntryDetailPage(QWidget):
    edit_requested = Signal(int)
    add_child_requested = Signal(int)
    member_selected = Signal(int)
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
        self._title_label.setWordWrap(True)
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

        self._add_child_button = QPushButton(
            "+ MEMBER"
        )

        self._add_child_button.clicked.connect(
            self._request_add_child
        )

        layout.addWidget(
            self._add_child_button
        )

        self._members_title = (
            self._section_label(
                "MEMBERS"
            )
        )

        self._members_container = QWidget()

        self._members_layout = QGridLayout(
            self._members_container
        )

        self._members_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self._members_layout.setHorizontalSpacing(
            12
        )

        self._members_layout.setVerticalSpacing(
            12
        )

        layout.addSpacing(18)

        layout.addWidget(
            self._members_title
        )

        layout.addWidget(
            self._members_container
        )

        self._signature_title = self._section_label(
            "SIGNATURE"
        )
        self._signature_block = CodeBlock()
        self._pattern_label = self._content_label()
        self._natural_metadata = []
        for name in ("FORMALITY", "DIALECT / VARIETY", "RELATED CONCEPTS"):
            self._natural_metadata.append((self._section_label(name), self._content_label()))

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

        layout.addWidget(self._pattern_label)
        for title, content in (*sections, *self._natural_metadata):
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
        label.setTextFormat(Qt.TextFormat.PlainText)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)

        return label

    def set_entry(
            self,
            entry: Entry,
            arguments: list[Argument],
            examples: list[Example],
            members: list[Entry],
            syntax_hint: str | None,
            natural: bool = False,
    ) -> None:
        self._entry = entry
        self._natural = natural
        self._title_label.setTextFormat(Qt.TextFormat.PlainText)
        self._summary_label.setTextFormat(Qt.TextFormat.PlainText)
        for label, regular, natural_title in [
            (self._signature_title, "SIGNATURE", "PATTERN / GRAMMAR"),
            (self._definition_title, "DEFINITION", "EXPLANATION"),
            (self._mental_model_title, "MENTAL MODEL", "USAGE / STRUCTURE"),
            (self._return_title, "RETURN VALUE", "MEANING / TRANSLATION"),
            (self._gotchas_title, "GOTCHAS", "COMMON MISTAKES / GOTCHAS"),
            (self._members_title, "MEMBERS", "SUBENTRIES")]:
            label.setText(natural_title if natural else regular)
        self._add_child_button.setText("+ SUBENTRY" if natural else "+ MEMBER")
        for (title, label), value in zip(self._natural_metadata, (entry.formality, entry.dialect, entry.related_concepts)):
            self._set_section(title, label, value if natural else None)
        self._pattern_label.setText(entry.signature or "")
        self._pattern_label.setVisible(natural and bool(entry.signature))

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

        self._signature_block.setVisible(has_signature and not natural)

        if entry.signature and not natural:
            self._signature_block.set_code(
                entry.signature,
                syntax_hint,
            )

        self._populate_members(
            members
        )

        self._populate_arguments([] if natural else arguments)

        self._populate_examples(
            examples
        )

        self._edit_button.setEnabled(
            entry.id is not None
        )

        self._add_child_button.setEnabled(
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
                (NaturalExampleDisplayWidget if self._natural else ExampleDisplayWidget)(example)
            )

    @staticmethod
    def _clear_layout(
            layout: QLayout,
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

    def _request_add_child(self) -> None:
        if (
                self._entry is None
                or self._entry.id is None
        ):
            return

        self.add_child_requested.emit(
            self._entry.id
        )


    def _populate_members(
            self,
            members: list[Entry],
    ) -> None:
        self._clear_layout(
            self._members_layout
        )

        has_members = bool(
            members
        )

        self._members_title.setVisible(
            has_members
        )

        self._members_container.setVisible(
            has_members
        )

        for index, member in enumerate(
                members
        ):
            if member.id is None:
                continue

            card = OverviewCard(
                item_id=member.id,
                title=(
                    f"{member.title} "
                    f"· {member.entry_kind}"
                ),
                description=(
                        member.summary
                        or member.definition
                ),
            )

            card.clicked.connect(
                self.member_selected.emit
            )

            row = index // 2
            column = index % 2

            self._members_layout.addWidget(
                card,
                row,
                column,
            )