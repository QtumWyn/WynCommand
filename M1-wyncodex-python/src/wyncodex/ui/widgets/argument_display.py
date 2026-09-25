from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
)

from wyncodex.domain.argument import (
    Argument,
)


class ArgumentDisplayWidget(QFrame):
    def __init__(
            self,
            argument: Argument,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName(
            "argumentCard"
        )

        layout = QVBoxLayout(self)

        name = QLabel(argument.name)
        name.setObjectName(
            "argumentName"
        )

        details = []

        if argument.type_text:
            details.append(
                argument.type_text
            )

        details.append(
            (
                "required"
                if argument.required
                else "optional"
            )
        )

        if argument.default_value:
            details.append(
                f"default: "
                f"{argument.default_value}"
            )

        metadata = QLabel(
            " · ".join(details)
        )

        metadata.setObjectName(
            "argumentMetadata"
        )

        description = QLabel(
            argument.description
            or ""
        )

        description.setObjectName(
            "entryBody"
        )

        description.setWordWrap(True)

        layout.addWidget(name)
        layout.addWidget(metadata)

        if argument.description:
            layout.addWidget(
                description
            )