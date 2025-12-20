import re
import os

def replaceSpecialChar(text: str, replacingChar: str='_') -> str:
    # Replace any non-alphanumeric character (including whitespace) with underscore
    return re.sub(r'[^a-zA-Z0-9]', replacingChar, text)

def dictToConfigString(data: dict) -> str:
    """
    Converts a dictionary to a multiline string in the format:
    KEY = VALUE

    Args:
        data (dict): The dictionary to convert.

    Returns:
        str: Formatted configuration string.
    """
    return "\n".join(f"{key} = {value}" for key, value in data.items())



def changeExtensionFileName(filepath, new_ext):
    """Safely changes file extension, ignoring dots in folder names."""
    base, _ = os.path.splitext(filepath)  # Splits ONLY the last extension
    return f"{base}.{new_ext.lstrip('.')}"  # Ensures no double dots