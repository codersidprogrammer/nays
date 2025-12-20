
import numpy as np

def format_float_sci(value):
    """
    Formats a single float value in scientific notation with 4 decimal places.

    Parameters:
        value (float): The float value to format.

    Returns:
        str: Formatted string in scientific notation (e.g., 1.2345E+03).
    """
    return f"{value:.4E}"

def format_float_sci_spec(value, format_spec='%.4E'):
    """
    Formats a single float value in scientific notation with 4 decimal places.

    Parameters:
        value (float): The float value to format.

    Returns:
        str: Formatted string in scientific notation (e.g., 1.2345E+03).
    """
    return format_spec % value

def format_whitespace(value, width=8):
    """
    Formats any value (string or number) with right-justified whitespace to a specified width.

    Parameters:
        value: The value to format (str, int, float, etc.).
        width (int): The total width for the formatted string (default is 8).

    Returns:
        str: The value as a string, right-justified to the given width.
    """
    return str(value).rjust(width)

def format_array(arr):
    """
    Formats a NumPy array into a space-separated string.
    
    - Floats are formatted to 3 decimal places.
    - Integers are converted to string directly.

    Parameters:
        arr (np.ndarray): A NumPy array of floats or ints.

    Returns:
        str: Formatted string.
    """
    arr = np.asarray(arr)  # Ensure input is an ndarray
    if np.issubdtype(arr.dtype, np.floating):
        return "         ".join([f"{v:.3f}" for v in arr.flatten()])
    else:
        return "         ".join([str(v) for v in arr.flatten()])
    
def format_array_as_int(arr):
    """
    Converts a NumPy array to integers and formats it into a space-separated string.

    - All elements are cast to integers.
    - Output is a space-separated string of integers.

    Parameters:
        arr (np.ndarray): A NumPy array of floats or ints.

    Returns:
        str: Formatted string of integers.
    """
    arr = np.asarray(arr)  # Ensure input is an ndarray
    arr_int = arr.astype(int)  # Convert all elements to integers
    return "         ".join([str(v) for v in arr_int.flatten()])

def format_array_as_int_spec(arr, format_spec='%d'):
    arr = np.asarray(arr)  # Ensure input is an ndarray
    arr_int = arr.astype(int)  # Convert all elements to integers
    return " ".join([format_spec % v for v in arr_int.flatten()])

def format_array_as_float_spec(arr, format_spec='%.3f'):
    arr = np.asarray(arr)  # Ensure input is an ndarray
    arr_float = arr.astype(float)  # Convert all elements to floats
    return " ".join([format_spec % v for v in arr_float.flatten()])


def format_matrix(matrix, format_spec=True):
    """
    Formats a 2D NumPy array (matrix) into a multi-line string.

    - Each row is placed on a new line.
    - If format_spec is True, each element is formatted with 3 decimal places.
    - If format_spec is False, elements are returned as their string representations without formatting.

    Parameters:
        matrix (np.ndarray): A 2D NumPy array to format.
        format_spec (bool): Whether to apply float formatting (default is True).

    Returns:
        str: A multi-line string where each line represents a formatted matrix row.
    """
    lines = []
    for row in matrix:
        if format_spec:
            formatted_row = "   ".join(f"{v:.3f}" for v in row)
        else:
            formatted_row = "   ".join(str(v) for v in row)
        lines.append(formatted_row)
    return "\n   ".join(lines)


def format_array_sci(arr):
    """
    Formats a NumPy array into a space-separated string in scientific notation.

    - All values are formatted as scientific notation with 4 decimal places (e.g., 1.6560E+07).
    - Works for both floats and ints.

    Parameters:
        arr (np.ndarray): A NumPy array of floats or ints.

    Returns:
        str: Formatted string in scientific notation.
    """
    arr = np.asarray(arr)  # Ensure input is an ndarray
    return "         ".join([f"{v:.4E}" for v in arr.flatten()])


def format_matrix_sci(matrix, format_spec=True):
    """
    Formats a 2D NumPy array (matrix) into a multi-line string using scientific notation.

    - Each row is placed on a new line.
    - If format_spec is True, elements are formatted in scientific notation with 4 decimal places.
    - If format_spec is False, elements are returned as their string representations without formatting.

    Parameters:
        matrix (np.ndarray): A 2D NumPy array to format.
        format_spec (bool): Whether to apply scientific formatting (default is True).

    Returns:
        str: A multi-line string where each line represents a formatted matrix row.
    """
    matrix = np.asarray(matrix)
    lines = []
    for row in matrix:
        if format_spec:
            formatted_row = "".join(("  " if f"{v:.4E}".startswith("-") else "   ") + f"{v:.4E}" for v in row)
        else:
            formatted_row = "   ".join(str(v) for v in row)
        lines.append(formatted_row)
    return "\n".join(lines)

def format_matrix_sci_spec(matrix, format_spec='%.4E'):
    """
    Formats a 2D NumPy array (matrix) into a multi-line string with custom format specification.
    
    Parameters:
        matrix (np.ndarray): A 2D NumPy array to format.
        format_spec (str): Format specification string (default is '%.4E').
    
    Returns:
        str: A multi-line string where each line represents a formatted matrix row.
    """
    matrix = np.asarray(matrix)  # Ensure input is an ndarray
    matrix_float = matrix.astype(float)  # Convert all elements to floats
    lines = []
    for row in matrix_float:
        formatted_row = " ".join([format_spec % v for v in row])
        lines.append(formatted_row)
    return "\n".join(lines)

def format_array_sci_spec(arr, format_spec='%.4E'):
    """
    Universal array formatter supporting multiple format types
    
    Parameters:
        arr: NumPy array or list
        format_spec: Format string
            - Float: '%6f', '%8.2f', '%-10.3f'
            - Scientific: '%.4E', '%12.3E', '%-15.4e'
            - Integer: '%6d', '%8d'
            - General: '%g', '%10g'
    
    Returns:
        str: Formatted string with values separated by spaces
    """
    arr = np.asarray(arr)
    return " ".join([format_spec % float(v) for v in arr.flatten()])
