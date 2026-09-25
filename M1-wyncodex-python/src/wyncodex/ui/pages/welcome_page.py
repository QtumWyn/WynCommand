from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class WelcomePage(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)

        label = QLabel(
            "Select a language to begin exploring WynCodex."
        )

        label.setObjectName("placeholderLabel")

        label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(label)