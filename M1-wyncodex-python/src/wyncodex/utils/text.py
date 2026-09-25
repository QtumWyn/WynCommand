import re
import unicodedata


_SYMBOL_REPLACEMENTS = {
    "+": " plus ",
    "#": " sharp ",
    "&": " and ",
    "@": " at ",
}


def slugify(value: str) -> str:
    value = value.strip()

    for symbol, replacement in _SYMBOL_REPLACEMENTS.items():
        value = value.replace(
            symbol,
            replacement,
        )

    value = unicodedata.normalize(
        "NFKD",
        value,
    )

    value = "".join(
        character
        for character in value
        if not unicodedata.combining(character)
    )

    value = value.casefold()

    value = re.sub(
        r"[^a-z0-9]+",
        "-",
        value,
    )

    return value.strip("-")

def clean_optional_text(
        value: str | None,
) -> str | None:
    if value is None:
        return None

    cleaned = value.strip()

    return cleaned or None