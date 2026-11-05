from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


def text_label(text, object_name="entryBody"):
    label = QLabel(text)
    label.setObjectName(object_name)
    label.setTextFormat(Qt.TextFormat.PlainText)
    label.setWordWrap(True)
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
    return label


class NaturalExampleDisplayWidget(QFrame):
    def __init__(self, example, parent=None):
        super().__init__(parent)
        self.setObjectName("exampleCard")
        layout = QVBoxLayout(self)
        layout.addWidget(text_label(example.title, "exampleTitle"))
        for title, value in [("ORIGINAL TEXT", example.code), ("TRANSLATION", example.output),
                ("WORD-BY-WORD BREAKDOWN / NOTES", example.explanation),
                ("ROMANIZATION", example.romanization), ("PRONUNCIATION", example.pronunciation)]:
            if value:
                layout.addWidget(text_label(title, "entrySectionHeader"))
                layout.addWidget(text_label(value))
