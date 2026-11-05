from PySide6.QtWidgets import QDialog, QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QCheckBox, QMessageBox, QWidget


class GuardedDialog(QDialog):
    """Keep drafts when Escape, Cancel or the window close button is accidental."""
    def remember_initial_state(self):
        self._initial_state = self._form_state()

    def _form_state(self):
        values = []
        for widget in self.findChildren(QWidget):
            if isinstance(widget, QLineEdit):
                values.append(widget.text())
            elif isinstance(widget, (QTextEdit, QPlainTextEdit)):
                values.append(widget.toPlainText())
            elif isinstance(widget, QComboBox):
                values.append(widget.currentText())
            elif isinstance(widget, QCheckBox):
                values.append(widget.isChecked())
        return tuple(values)

    def reject(self):
        if hasattr(self, '_initial_state') and self._form_state() != self._initial_state:
            choice = QMessageBox.question(self, 'Unsaved changes', 'Discard your unsaved changes?',
                QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel)
            if choice != QMessageBox.StandardButton.Discard:
                return
        super().reject()

    def closeEvent(self, event):
        self.reject()
        event.setAccepted(self.result() == QDialog.DialogCode.Rejected and not self.isVisible())
