from PySide6.QtGui import (
    QColor,
    QFont,
    QTextCharFormat,
    QSyntaxHighlighter,
)

from pygments import lex

from pygments.lexers import (
    get_lexer_by_name,
)

from pygments.lexers.special import (
    TextLexer,
)

from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    String,
)

from pygments.util import (
    ClassNotFound,
)

from wyncodex.ui.theme import palette


LEXER_ALIASES: dict[str, str] = {
    "c-sharp": "csharp",
    "c#": "csharp",
    "cs": "csharp",

    "c-plus-plus": "cpp",
    "c++": "cpp",
    "cplusplus": "cpp",

    "f-sharp": "fsharp",
    "f#": "fsharp",
    "fs": "fsharp",

    "java-script": "javascript",
    "js": "javascript",

    "type-script": "typescript",
    "ts": "typescript",

    "power-shell": "powershell",
    "ps1": "powershell",

    "assembly": "nasm",

    "shell": "bash",
    "sh": "bash",
}


class PygmentsHighlighter(
    QSyntaxHighlighter
):
    def __init__(
            self,
            document,
            syntax_hint: str | None = None,
    ) -> None:
        super().__init__(document)

        self._lexer = TextLexer()

        self.set_syntax_hint(
            syntax_hint
        )

    def set_syntax_hint(
            self,
            syntax_hint: str | None,
    ) -> None:
        if not syntax_hint:
            self._lexer = TextLexer()

            self.rehighlight()

            return

        normalized_hint = (
            syntax_hint
            .strip()
            .lower()
        )

        lexer_name = (
            LEXER_ALIASES.get(
                normalized_hint,
                normalized_hint,
            )
        )

        try:
            if lexer_name == "php":
                self._lexer = (
                    get_lexer_by_name(
                        "php",
                        startinline=True,
                    )
                )

            else:
                self._lexer = (
                    get_lexer_by_name(
                        lexer_name
                    )
                )

        except ClassNotFound:
            self._lexer = TextLexer()

        self.rehighlight()

    def highlightBlock(
            self,
            text: str,
    ) -> None:
        offset = 0

        for token_type, value in lex(
                text,
                self._lexer,
        ):
            if offset >= len(text):
                break

            length = min(
                len(value),
                len(text) - offset,
                )

            if length <= 0:
                continue

            text_format = (
                self._format_for_token(
                    token_type
                )
            )

            self.setFormat(
                offset,
                length,
                text_format,
            )

            offset += len(value)

    @staticmethod
    def _format_for_token(
            token_type,
    ) -> QTextCharFormat:
        text_format = QTextCharFormat()

        text_format.setForeground(
            QColor(
                palette.BONE
            )
        )

        if token_type in Comment:
            text_format.setForeground(
                QColor(
                    palette.DIM_ASH
                )
            )

        elif token_type in Keyword:
            text_format.setForeground(
                QColor(
                    palette.PASTEL_PINK
                )
            )

            text_format.setFontWeight(
                QFont.Weight.Bold
            )

        elif (
                token_type in Name.Function
                or token_type in Name.Class
                or token_type in Name.Builtin
        ):
            text_format.setForeground(
                QColor(
                    palette.PASTEL_BLUE
                )
            )

        elif token_type in String:
            text_format.setForeground(
                QColor(
                    palette.VIOLET
                )
            )

        elif token_type in Number:
            text_format.setForeground(
                QColor(
                    palette.PASTEL_BLUE
                )
            )

        elif token_type in Operator:
            text_format.setForeground(
                QColor(
                    palette.WINE
                )
            )

        return text_format