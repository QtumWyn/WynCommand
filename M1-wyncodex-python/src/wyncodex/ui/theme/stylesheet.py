from PySide6.QtWidgets import QApplication

from wyncodex.ui.theme import palette


def build_stylesheet() -> str:
    return f"""
        QWidget {{
            color: {palette.BONE};
            font-family: "JetBrains Mono";
            font-size: 11pt;
        }}

        QMainWindow,
        QDialog {{
            background-color: {palette.VOID_BLACK};
        }}

        QWidget#centralRoot {{
            background-color: {palette.VOID_BLACK};
        }}

        QWidget#navigationPanel {{
            background-color: {palette.CATHEDRAL_BLACK};
            border-right: 1px solid {palette.IRON};
        }}

        QWidget#contentPanel {{
            background-color: {palette.VOID_BLACK};
        }}


        /* ---------- Labels ---------- */

        QLabel {{
            background-color: transparent;
        }}

        QLabel#sectionLabel {{
            color: {palette.ASH};
            font-size: 9pt;
            font-weight: bold;
            letter-spacing: 2px;
        }}

        QLabel#placeholderLabel {{
            color: {palette.DIM_ASH};
            font-size: 11pt;
        }}

        QLabel#validationLabel {{
            color: {palette.PASTEL_PINK};
            font-size: 9pt;
        }}
        
        QLabel#pageTitle {{
            color: {palette.BONE};
        
            font-family: "Cinzel";
            font-size: 22pt;
            font-weight: bold;
        
            letter-spacing: 3px;
        }}
        
        QLabel#pageDescription {{
            color: {palette.ASH};
        
            font-family: "JetBrains Mono";
            font-size: 10pt;
        }}
        
        QLabel#breadcrumbLabel {{
            color: {palette.PASTEL_BLUE};
        
            font-family: "JetBrains Mono";
            font-size: 8pt;
            font-weight: bold;
        
            letter-spacing: 2px;
        }}
        
        QLabel#pageSummary {{
            color: {palette.PASTEL_PINK};
        
            font-family: "JetBrains Mono";
            font-size: 10pt;
            font-weight: bold;
        
            letter-spacing: 1px;
        }}
        
        QFrame#overviewCard {{
            background-color: {palette.RAISED_BLACK};
        
            border: 1px solid {palette.IRON};
            border-radius: 8px;
        }}
        
        QFrame#overviewCard:hover {{
            background-color: {palette.HOVER_BLACK};
        
            border-color: {palette.PASTEL_BLUE};
        }}
        
        QLabel#overviewCardTitle {{
            color: {palette.BONE};
        
            font-family: "JetBrains Mono";
            font-size: 11pt;
            font-weight: bold;
        
            letter-spacing: 0.8px;
        }}
        
        QLabel#overviewCardDescription {{
            color: {palette.ASH};
        
            font-family: "JetBrains Mono";
            font-size: 9pt;
        }}
        
        QLabel#entrySectionHeader {{
            color: {palette.PASTEL_BLUE};
        
            font-family: "JetBrains Mono";
            font-size: 9pt;
            font-weight: bold;
        
            letter-spacing: 1.5px;
        }}
        
        QLabel#entryBody {{
            color: {palette.BONE};
        
            font-family: "JetBrains Mono";
            font-size: 10pt;
        }}
        
        QLabel#pageSummary {{
            color: {palette.PASTEL_PINK};
        
            font-family: "JetBrains Mono";
            font-size: 10pt;
            font-weight: bold;
        }}
        
        QFrame#codeBlock {{
            background-color: {palette.CATHEDRAL_BLACK};
        
            border: 1px solid {palette.IRON};
            border-radius: 8px;
        }}
        
        QLabel#codeLanguage {{
            color: {palette.PASTEL_PINK};
        
            font-family: "JetBrains Mono";
            font-size: 8pt;
            font-weight: bold;
        
            letter-spacing: 1.5px;
        }}
        
        QPlainTextEdit#codeViewer {{
            background-color: {palette.VOID_BLACK};
        
            color: {palette.BONE};
        
            border: 1px solid {palette.IRON};
            border-radius: 6px;
        
            padding: 8px;
        
            font-family: "JetBrains Mono";
            font-size: 10pt;
        }}
        
        QFrame#editorCard {{
            background-color: {palette.RAISED_BLACK};
        
            border: 1px solid {palette.IRON};
            border-radius: 8px;
        
            padding: 8px;
        }}
        
        QFrame#editorCard:hover {{
            border-color: {palette.BRIGHT_IRON};
        }}
        
        QFrame#argumentCard,
        QFrame#exampleCard {{
            background-color: {palette.RAISED_BLACK};
        
            border: 1px solid {palette.IRON};
            border-radius: 8px;
        
            padding: 8px;
        }}
        
        QLabel#argumentName,
        QLabel#exampleTitle {{
            color: {palette.PASTEL_PINK};
        
            font-family: "JetBrains Mono";
            font-size: 11pt;
            font-weight: bold;
        }}
        
        QLabel#argumentMetadata {{
            color: {palette.PASTEL_BLUE};
        
            font-family: "JetBrains Mono";
            font-size: 9pt;
        }}
        
        QLabel#exampleType {{
            color: {palette.VIOLET};
        
            font-family: "JetBrains Mono";
            font-size: 8pt;
            font-weight: bold;
        
            letter-spacing: 1px;
        }}


        /* ---------- Navigation ---------- */

        QTreeView {{
            background-color: {palette.CATHEDRAL_BLACK};
            border: 1px solid {palette.IRON};
            border-radius: 6px;

            outline: none;

            padding: 4px;
        }}

        QTreeView::item {{
            min-height: 30px;

            color: {palette.ASH};

            border-left: 3px solid transparent;
            border-radius: 4px;

            padding-left: 8px;
        }}

        QTreeView::item:hover {{
            background-color: {palette.HOVER_BLACK};
            color: {palette.BONE};

            border-left: 3px solid {palette.PASTEL_BLUE};
        }}

        QTreeView::item:selected {{
            background-color: {palette.SELECTED_BLACK};
            color: {palette.BONE};

            border-left: 3px solid {palette.PASTEL_PINK};
        }}


        /* ---------- Text input ---------- */

        QLineEdit,
        QTextEdit {{
            background-color: {palette.RAISED_BLACK};

            color: {palette.BONE};

            border: 1px solid {palette.IRON};
            border-radius: 6px;

            padding: 7px;

            selection-background-color: {palette.VIOLET};
            selection-color: {palette.SOFT_WHITE};
        }}

        QLineEdit:hover,
        QTextEdit:hover {{
            border-color: {palette.BRIGHT_IRON};
        }}

        QLineEdit:focus,
        QTextEdit:focus {{
            background-color: {palette.HOVER_BLACK};

            border: 1px solid {palette.PASTEL_BLUE};
        }}


        /* ---------- Buttons ---------- */

        QPushButton {{
            background-color: {palette.RAISED_BLACK};

            color: {palette.BONE};

            border: 1px solid {palette.IRON};
            border-radius: 6px;

            padding: 7px 14px;

            font-weight: bold;
        }}

        QPushButton:hover {{
            background-color: {palette.HOVER_BLACK};

            border-color: {palette.PASTEL_BLUE};
        }}

        QPushButton:pressed {{
            background-color: {palette.SELECTED_BLACK};

            border-color: {palette.VIOLET};
        }}

        QPushButton#accentButton {{
            border-color: {palette.VIOLET};
        }}

        QPushButton#accentButton:hover {{
            border-color: {palette.PASTEL_PINK};
        }}

        QPushButton#primaryButton {{
            background-color: {palette.SELECTED_BLACK};

            border-color: {palette.VIOLET};
        }}

        QPushButton#primaryButton:hover {{
            background-color: {palette.HOVER_BLACK};

            border-color: {palette.PASTEL_PINK};
        }}


        /* ---------- Splitter ---------- */

        QSplitter::handle {{
            background-color: {palette.IRON};
        }}

        QSplitter::handle:horizontal {{
            width: 1px;
        }}

        QSplitter::handle:hover {{
            background-color: {palette.VIOLET};
        }}


        /* ---------- Trans stripe ---------- */

        QFrame#transStripe {{
            border: none;

            background: qlineargradient(
                x1: 0,
                y1: 0,
                x2: 1,
                y2: 0,

                stop: 0.00 {palette.PASTEL_BLUE},
                stop: 0.20 {palette.PASTEL_BLUE},

                stop: 0.20 {palette.PASTEL_PINK},
                stop: 0.40 {palette.PASTEL_PINK},

                stop: 0.40 {palette.SOFT_WHITE},
                stop: 0.60 {palette.SOFT_WHITE},

                stop: 0.60 {palette.PASTEL_PINK},
                stop: 0.80 {palette.PASTEL_PINK},

                stop: 0.80 {palette.PASTEL_BLUE},
                stop: 1.00 {palette.PASTEL_BLUE}
            );
        }}
    """


def apply_theme(app: QApplication) -> None:
    app.setStyleSheet(build_stylesheet())