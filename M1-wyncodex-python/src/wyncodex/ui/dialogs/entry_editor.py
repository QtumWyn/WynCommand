from PySide6.QtCore import Qt
from PySide6.QtGui import QTextOption
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from wyncodex.services.entry_service import (
    EntryService,
)
from wyncodex.ui.widgets.argument_editor import (
    ArgumentEditorWidget,
)

from wyncodex.ui.widgets.example_editor import (
    ExampleEditorWidget,
)

from wyncodex.domain.entry import Entry
from wyncodex.domain.argument import Argument
from wyncodex.domain.example import Example


class EntryEditorDialog(QDialog):
    def __init__(
            self,
            entry_service: EntryService,
            category_id: int,
            package_id: int | None = None,
            default_syntax_hint: str | None = None,
            entry: Entry | None = None,
            arguments: list[Argument] | None = None,
            examples: list[Example] | None = None,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self._entry_service = entry_service
        self._category_id = category_id
        self._package_id = package_id

        self._entry = entry

        self._existing_arguments = (
                arguments or []
        )

        self._existing_examples = (
                examples or []
        )

        self._default_syntax_hint = (
            default_syntax_hint
        )

        self._argument_editors: list[
            ArgumentEditorWidget
        ] = []

        self._example_editors: list[
            ExampleEditorWidget
        ] = []

        self.setWindowTitle(
            "Edit Entry"
            if entry is not None
            else "Add Entry"
        )
        self.resize(680, 760)

        self._build_ui()

        if self._entry is not None:
            self._load_existing_entry()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self._title_field = QLineEdit()
        self._summary_field = QTextEdit()

        self._configure_text_area(
            self._summary_field,
            65,
        )

        self._signature_field = QTextEdit()
        self._definition_field = QTextEdit()
        self._mental_model_field = QTextEdit()
        self._return_value_field = QTextEdit()
        self._gotchas_field = QTextEdit()
        self._notes_field = QTextEdit()

        self._summary_field.setPlaceholderText(
            "Short description for cards"
        )

        self._configure_text_area(
            self._signature_field,
            80,
        )

        self._configure_text_area(
            self._definition_field,
            120,
        )

        self._configure_text_area(
            self._mental_model_field,
            120,
        )

        self._configure_text_area(
            self._return_value_field,
            90,
        )

        self._configure_text_area(
            self._gotchas_field,
            110,
        )

        self._configure_text_area(
            self._notes_field,
            110,
        )

        form.addRow(
            "Title",
            self._title_field,
        )

        form.addRow(
            "Summary",
            self._summary_field,
        )

        form.addRow(
            "Signature",
            self._signature_field,
        )

        form.addRow(
            "Definition",
            self._definition_field,
        )

        form.addRow(
            "Mental Model",
            self._mental_model_field,
        )

        form.addRow(
            "Return Value",
            self._return_value_field,
        )

        form.addRow(
            "Gotchas",
            self._gotchas_field,
        )

        form.addRow(
            "Notes",
            self._notes_field,
        )

        self._tabs = QTabWidget()

        # -------------------------
        # Overview tab
        # -------------------------

        overview_tab = QWidget()
        overview_layout = QVBoxLayout(
            overview_tab
        )

        overview_layout.addLayout(form)
        overview_layout.addStretch()

        self._tabs.addTab(
            overview_tab,
            "Overview",
        )

        # -------------------------
        # Arguments tab
        # -------------------------

        arguments_tab = QWidget()
        arguments_layout = QVBoxLayout(
            arguments_tab
        )

        arguments_scroll = QScrollArea()
        arguments_scroll.setWidgetResizable(True)

        arguments_container = QWidget()

        self._arguments_layout = QVBoxLayout(
            arguments_container
        )

        self._arguments_layout.addStretch()

        arguments_scroll.setWidget(
            arguments_container
        )

        add_argument_button = QPushButton(
            "+ ARGUMENT"
        )

        add_argument_button.setObjectName(
            "accentButton"
        )

        add_argument_button.clicked.connect(
            self._add_argument
        )

        arguments_layout.addWidget(
            arguments_scroll
        )

        arguments_layout.addWidget(
            add_argument_button
        )

        self._tabs.addTab(
            arguments_tab,
            "Arguments",
        )

        # -------------------------
        # Examples tab
        # -------------------------

        examples_tab = QWidget()
        examples_layout = QVBoxLayout(
            examples_tab
        )

        examples_scroll = QScrollArea()
        examples_scroll.setWidgetResizable(True)

        examples_container = QWidget()

        self._examples_layout = QVBoxLayout(
            examples_container
        )

        self._examples_layout.addStretch()

        examples_scroll.setWidget(
            examples_container
        )

        add_example_button = QPushButton(
            "+ EXAMPLE"
        )

        add_example_button.setObjectName(
            "primaryButton"
        )

        add_example_button.clicked.connect(
            self._add_example
        )

        examples_layout.addWidget(
            examples_scroll
        )

        examples_layout.addWidget(
            add_example_button
        )

        self._tabs.addTab(
            examples_tab,
            "Examples",
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

        layout.addWidget(
            self._tabs
        )

        layout.addWidget(
            self._message_label
        )

        layout.addWidget(buttons)

        self._title_field.setFocus()

    @staticmethod
    def _configure_text_area(
            field: QTextEdit,
            maximum_height: int,
    ) -> None:
        field.setMaximumHeight(
            maximum_height
        )

        field.setAcceptRichText(False)

        field.setLineWrapMode(
            QTextEdit.LineWrapMode.WidgetWidth
        )

        field.setWordWrapMode(
            QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere
        )

        field.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

    def _save(self) -> None:
        try:
            arguments = [
                editor.to_draft()
                for editor
                in self._argument_editors
            ]

            examples = [
                editor.to_draft()
                for editor
                in self._example_editors
            ]

            if self._entry is None:
                self._entry_service.create_entry(
                    category_id=self._category_id,
                    package_id=self._package_id,

                    title=self._title_field.text(),

                    summary=(
                        self._summary_field
                        .toPlainText()
                    ),

                    signature=(
                        self._signature_field
                        .toPlainText()
                    ),

                    definition=(
                        self._definition_field
                        .toPlainText()
                    ),

                    mental_model=(
                        self._mental_model_field
                        .toPlainText()
                    ),

                    return_value=(
                        self._return_value_field
                        .toPlainText()
                    ),

                    gotchas=(
                        self._gotchas_field
                        .toPlainText()
                    ),

                    notes=(
                        self._notes_field
                        .toPlainText()
                    ),

                    arguments=arguments,
                    examples=examples,
                )
            else:
                self._entry_service.update_entry(
                    entry_id=self._entry.id,
                    title=self._title_field.text(),

                    summary=(
                        self._summary_field
                        .toPlainText()
                    ),

                    signature=(
                        self._signature_field
                        .toPlainText()
                    ),

                    definition=(
                        self._definition_field
                        .toPlainText()
                    ),

                    mental_model=(
                        self._mental_model_field
                        .toPlainText()
                    ),

                    return_value=(
                        self._return_value_field
                        .toPlainText()
                    ),

                    gotchas=(
                        self._gotchas_field
                        .toPlainText()
                    ),

                    notes=(
                        self._notes_field
                        .toPlainText()
                    ),

                    arguments=arguments,
                    examples=examples,
                )

        except ValueError as error:
            self._message_label.setText(
                str(error)
            )
            return

        self.accept()

    def _add_argument(self) -> None:
        editor = ArgumentEditorWidget()

        editor.remove_requested.connect(
            self._remove_argument
        )

        self._argument_editors.append(
            editor
        )

        position = (
                self._arguments_layout.count()
                - 1
        )

        self._arguments_layout.insertWidget(
            position,
            editor,
        )


    def _remove_argument(
            self,
            editor: ArgumentEditorWidget,
    ) -> None:
        if editor in self._argument_editors:
            self._argument_editors.remove(
                editor
            )

        editor.deleteLater()

    def _add_example(self) -> None:
        editor = ExampleEditorWidget(
            self._default_syntax_hint
        )

        editor.remove_requested.connect(
            self._remove_example
        )

        self._example_editors.append(
            editor
        )

        position = (
                self._examples_layout.count()
                - 1
        )

        self._examples_layout.insertWidget(
            position,
            editor,
        )


    def _remove_example(
            self,
            editor: ExampleEditorWidget,
    ) -> None:
        if editor in self._example_editors:
            self._example_editors.remove(
                editor
            )

        editor.deleteLater()

    def _load_existing_entry(self) -> None:
        if self._entry is None:
            return

        self._title_field.setText(
            self._entry.title
        )

        self._summary_field.setPlainText(
            self._entry.summary or ""
        )

        self._signature_field.setPlainText(
            self._entry.signature or ""
        )

        self._definition_field.setPlainText(
            self._entry.definition or ""
        )

        self._mental_model_field.setPlainText(
            self._entry.mental_model or ""
        )

        self._return_value_field.setPlainText(
            self._entry.return_value or ""
        )

        self._gotchas_field.setPlainText(
            self._entry.gotchas or ""
        )

        self._notes_field.setPlainText(
            self._entry.notes or ""
        )

        for argument in self._existing_arguments:
            self._add_argument_from_existing(
                argument
            )

        for example in self._existing_examples:
            self._add_example_from_existing(
                example
            )
    def _add_argument_from_existing(
            self,
            argument: Argument,
    ) -> None:
        editor = ArgumentEditorWidget(
            argument
        )

        editor.remove_requested.connect(
            self._remove_argument
        )

        self._argument_editors.append(
            editor
        )

        position = (
                self._arguments_layout.count()
                - 1
        )

        self._arguments_layout.insertWidget(
            position,
            editor,
        )

    def _add_example_from_existing(
            self,
            example: Example,
    ) -> None:
        editor = ExampleEditorWidget(
            default_syntax_hint=(
                self._default_syntax_hint
            ),
            example=example,
        )

        editor.remove_requested.connect(
            self._remove_example
        )

        self._example_editors.append(
            editor
        )

        position = (
                self._examples_layout.count()
                - 1
        )

        self._examples_layout.insertWidget(
            position,
            editor,
        )