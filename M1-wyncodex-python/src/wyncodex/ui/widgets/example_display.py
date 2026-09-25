from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
)

from wyncodex.domain.example import Example
from wyncodex.ui.widgets.code_block import (
    CodeBlock,
)


class ExampleDisplayWidget(QFrame):
    def __init__(
            self,
            example: Example,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName(
            "exampleCard"
        )

        layout = QVBoxLayout(self)

        title = QLabel(
            example.title
        )

        title.setObjectName(
            "exampleTitle"
        )

        example_type = QLabel(
            example.example_type.upper()
        )

        example_type.setObjectName(
            "exampleType"
        )

        code = CodeBlock()

        code.set_code(
            example.code,
            example.syntax_hint,
        )

        layout.addWidget(title)
        layout.addWidget(example_type)
        layout.addWidget(code)

        if example.explanation:
            explanation = QLabel(
                example.explanation
            )

            explanation.setObjectName(
                "entryBody"
            )

            explanation.setWordWrap(True)

            layout.addWidget(
                explanation
            )