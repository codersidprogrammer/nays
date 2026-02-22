def getIndexFromString(mode_str):
    # Split into parts: "MODE" and "1)"
    parts = mode_str.split("(")
    paramName = parts[0]  # "MODE"
    num = int(parts[1].replace(")", ""))  # Extract number and convert to int
    colIndex = num - 1  # Convert to zero-based index
    return paramName, colIndex


def replaceSpecialChars(s: str, replace_with: str = "_", allow_spaces: bool = False) -> str:
    """Normalize and replace special characters in `s`.

    - Normalizes Unicode to ASCII where possible (accents removed).
    - Replaces any character that is not alphanumeric (or space when
      `allow_spaces=True`) with `replace_with`.
    - Collapses repeated `replace_with` characters into a single one and
      trims leading/trailing separators.

    Examples:
        replaceSpecialChars("Café & Co.") -> "Cafe_Co"
        replaceSpecialChars("a/b\\c", '-') -> "a-b-c"

    Args:
        s: Input string.
        replace_with: Replacement character/string for special chars.
        allow_spaces: If True, keep spaces (they are not replaced).

    Returns:
        The cleaned string.
    """
    import re
    import unicodedata

    if s is None:
        return s

    # Normalize unicode (e.g., é -> e)
    normalized = unicodedata.normalize("NFKD", s)
    ascii_bytes = normalized.encode("ascii", "ignore")
    cleaned = ascii_bytes.decode("ascii")

    # Choose pattern: allow alnum and optionally spaces
    if allow_spaces:
        pattern = r"[^0-9A-Za-z\s]"
    else:
        pattern = r"[^0-9A-Za-z]"

    # Replace unwanted chars with the replacement
    result = re.sub(pattern, replace_with, cleaned)

    # If spaces are allowed we may want to collapse multiple spaces to one
    if allow_spaces:
        result = re.sub(r"\s+", " ", result).strip()

    # Collapse multiple replacement characters into one
    if replace_with:
        esc = re.escape(replace_with)
        result = re.sub(rf"{esc}+", replace_with, result)
        result = result.strip(replace_with)

    return result
