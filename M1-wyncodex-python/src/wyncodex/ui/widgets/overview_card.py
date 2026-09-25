from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
)


class OverviewCard(QFrame):
    clicked = Signal(int)

    def __init__(
            self,
            item_id: int,
            title: str,
            description: str | None = None,
            parent=None,
    ) -> None:
        super().__init__(parent)

        self._item_id = item_id

        self.setObjectName(
            "overviewCard"
        )

        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            13,
            16,
            13,
        )

        layout.setSpacing(6)

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "overviewCardTitle"
        )

        description_label = QLabel(
            description or "No description yet."
        )

        description_label.setObjectName(
            "overviewCardDescription"
        )

        description_label.setWordWrap(True)

        layout.addWidget(
            title_label
        )

        layout.addWidget(
            description_label
        )

    def mouseReleaseEvent(
            self,
            event: QMouseEvent,
    ) -> None:
        if (
                event.button()
                == Qt.MouseButton.LeftButton
        ):
            self.clicked.emit(
                self._item_id
            )

        super().mouseReleaseEvent(
            event
        )