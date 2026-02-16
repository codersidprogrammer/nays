# Table Editor Component

A professional, reusable table editor component for PyQt6/PySide6 applications with a comprehensive toolbar and status bar.

## Features

- **Professional Toolbar** with 12 action buttons:
  - Edit, Undo, Redo
  - Copy, Paste
  - Filter, Refresh
  - Add Row, Delete Row, Clear All
  - Export as List, Export as NumPy

- **Status Bar** showing:
  - Current action messages
  - Row and column count

- **Data Editing**:
  - Text, checkbox, and dropdown cells
  - In-place cell editing
  - Full keyboard support

- **Advanced Features**:
  - Undo/Redo (Ctrl+Z / Ctrl+Y)
  - Copy/Paste (Ctrl+C / Ctrl+V)
  - Filter and restore
  - Data import/export

- **Multiple Data Formats**:
  - List of dictionaries
  - NumPy arrays
  - Empty tables for user input

- **Styling**:
  - Light theme (default)
  - Dark theme
  - Professional appearance

- **Use Cases**:
  - Subwindow in MDI applications
  - Modal dialogs
  - Standalone applications
  - Data editing utilities

## Installation

The table editor is part of the NAYS framework. Import it from:

```python
from nays.ui.handler import createTableEditor
```

## Quick Start

### Simple Table from List of Dictionaries

```python
from PySide6.QtWidgets import QApplication
from nays.ui.handler import createTableEditor
import sys

app = QApplication(sys.argv)

# Define data
headers = ['Name', 'Age', 'Email']
data = [
    {'Name': 'Alice', 'Age': 28, 'Email': 'alice@example.com'},
    {'Name': 'Bob', 'Age': 35, 'Email': 'bob@example.com'},
]

# Create table editor
editor = createTableEditor(headers=headers, data=data)
editor.show()

sys.exit(app.exec())
```

### Table from NumPy Array

```python
import numpy as np
from nays.ui.handler import createTableEditor

headers = ['ID', 'Value', 'Status']
data = np.array([
    [1, 100, 'Active'],
    [2, 200, 'Inactive'],
])

editor = createTableEditor(headers=headers, data=data)
editor.show()
```

## Usage Guide

### Function Signature

```python
def createTableEditor(
    headers: List[str],
    data: Optional[Union[List[Dict[str, Any]], np.ndarray]] = None,
    column_types: Optional[Dict[str, str]] = None,
    combo_options: Optional[Dict[str, List[str]]] = None,
    enable_toolbar: bool = True,
    apply_style: bool = True,
    dark_mode: bool = False,
    parent=None
) -> TableEditorWidget:
```

### Parameters

#### `headers` (required)
List of column names/headers. These define the table structure.

```python
headers = ['Name', 'Email', 'Phone', 'Active']
```

#### `data` (optional)
Initial data to populate the table. Can be:

**List of dictionaries:**
```python
data = [
    {'Name': 'Alice', 'Email': 'alice@ex.com', 'Phone': '555-1234', 'Active': True},
    {'Name': 'Bob', 'Email': 'bob@ex.com', 'Phone': '555-5678', 'Active': False},
]
```

**NumPy 2D array:**
```python
data = np.array([
    ['Alice', 'alice@ex.com', '555-1234', True],
    ['Bob', 'bob@ex.com', '555-5678', False],
])
```

**None (empty table):**
```python
data = None  # Creates empty table for user to fill
```

#### `column_types` (optional)
Dictionary mapping column names to cell types. Supported types:
- `'text'` - Plain text editor (default)
- `'checkbox'` - Boolean checkbox
- `'combo'` - Dropdown menu

```python
column_types = {
    'Email': 'text',
    'Active': 'checkbox',
    'Status': 'combo',
}
```

#### `combo_options` (optional)
Dictionary mapping column names to lists of dropdown options.

```python
combo_options = {
    'Status': ['Active', 'Inactive', 'Pending'],
    'Category': ['Electronics', 'Furniture', 'Stationery'],
}
```

#### `enable_toolbar` (optional, default: True)
Show/hide the toolbar with buttons for add row, delete row, export, etc.

```python
editor = createTableEditor(
    headers=headers,
    data=data,
    enable_toolbar=True  # Show toolbar
)
```

#### `apply_style` (optional, default: True)
Apply default professional styling to the table.

```python
editor = createTableEditor(
    headers=headers,
    data=data,
    apply_style=True
)
```

#### `dark_mode` (optional, default: False)
Use dark theme instead of light theme. Only applies if `apply_style=True`.

```python
editor = createTableEditor(
    headers=headers,
    data=data,
    apply_style=True,
    dark_mode=True  # Dark theme
)
```

## Examples

### Example 1: Simple Employee List

```python
from nays.ui.handler import createTableEditor

headers = ['First Name', 'Last Name', 'Email', 'Department']
data = [
    {'First Name': 'Alice', 'Last Name': 'Johnson', 'Email': 'alice@company.com', 'Department': 'Engineering'},
    {'First Name': 'Bob', 'Last Name': 'Smith', 'Email': 'bob@company.com', 'Department': 'Sales'},
    {'First Name': 'Carol', 'Last Name': 'White', 'Email': 'carol@company.com', 'Department': 'Marketing'},
]

editor = createTableEditor(headers=headers, data=data)
editor.show()
```

### Example 2: Product Inventory with Dropdowns

```python
from nays.ui.handler import createTableEditor

headers = ['Product Name', 'Category', 'Status', 'Quantity']
data = [
    {'Product Name': 'Laptop', 'Category': 'Electronics', 'Status': 'Active', 'Quantity': 15},
    {'Product Name': 'Desk Chair', 'Category': 'Furniture', 'Status': 'Inactive', 'Quantity': 8},
]

column_types = {
    'Category': 'combo',
    'Status': 'combo',
}

combo_options = {
    'Category': ['Electronics', 'Furniture', 'Stationery'],
    'Status': ['Active', 'Inactive', 'Pending'],
}

editor = createTableEditor(
    headers=headers,
    data=data,
    column_types=column_types,
    combo_options=combo_options
)
editor.show()
```

### Example 3: Test Results with Checkboxes

```python
from nays.ui.handler import createTableEditor
import numpy as np

headers = ['Test Name', 'Result 1', 'Result 2', 'Result 3', 'Passed']
data = np.array([
    ['Unit Test', True, False, True, True],
    ['Integration Test', False, True, True, False],
    ['Performance Test', True, True, True, True],
])

column_types = {
    'Result 1': 'checkbox',
    'Result 2': 'checkbox',
    'Result 3': 'checkbox',
    'Passed': 'checkbox',
}

editor = createTableEditor(
    headers=headers,
    data=data,
    column_types=column_types
)
editor.show()
```

### Example 4: Dark Theme

```python
editor = createTableEditor(
    headers=['Name', 'Email'],
    data=[{'Name': 'Alice', 'Email': 'alice@ex.com'}],
    apply_style=True,
    dark_mode=True  # Use dark theme
)
editor.show()
```
### Example 7: As MDI Subwindow

```python
from PySide6.QtWidgets import QMainWindow, QMdiArea

main = QMainWindow()
mdi = QMdiArea()
main.setCentralWidget(mdi)
main.resize(1200, 800)

# Create table editor
editor = createTableEditor(
    headers=['Name', 'Email', 'Active'],
    data=[
        {'Name': 'Alice', 'Email': 'alice@ex.com', 'Active': True},
        {'Name': 'Bob', 'Email': 'bob@ex.com', 'Active': False},
    ],
    column_types={'Active': 'checkbox'}
)

# Add as subwindow
sub = mdi.addSubWindow(editor)
sub.show()

main.show()
```

### Example 8: Toolbar and Status Bar in Action

```python
# Create editor with toolbar and status bar
editor = createTableEditor(
    headers=['ID', 'Name', 'Value'],
    data=numpy_data,
    enable_toolbar=True,  # Show toolbar (default)
    apply_style=True      # Apply styling (default)
)

# The toolbar provides:
# - Edit, Undo, Redo for modifications
# - Copy, Paste for data manipulation
# - Filter, Refresh for data viewing
# - Add/Delete/Clear for row management
# - Export options for data extraction

# The status bar shows:
# - "Ready" when idle
# - "Row added" when adding rows
# - "Filtered: 5 of 10 rows" when filtering
# - "Rows: 10 | Cols: 5" for current dimensions

editor.show()
```
### Example 5: Data Edit and Export

```python
from nays.ui.handler import createTableEditor
import numpy as np

# Create editor with initial data
editor = createTableEditor(
    headers=['Name', 'Score'],
    data=[
        {'Name': 'Student 1', 'Score': 95},
        {'Name': 'Student 2', 'Score': 87},
    ]
)
editor.show()

# Later, retrieve edited data
# As list of dictionaries:
edited_data_dict = editor.getDataAsDict()
print(edited_data_dict)

# As NumPy array:
edited_data_numpy = editor.getDataAsNumpy()
print(edited_data_numpy)
```

## API Reference

### TableEditorWidget Methods

The `createTableEditor()` function returns a `TableEditorWidget` object with the following methods:

#### `getDataAsDict() -> List[Dict[str, Any]]`
Get all table data as a list of dictionaries.

```python
data = editor.getDataAsDict()
# Result: [{'Name': 'Alice', 'Age': 28}, ...]
```

#### `getDataAsNumpy() -> np.ndarray`
Get all table data as a NumPy array.

```python
array = editor.getDataAsNumpy()
# Result: numpy array with shape (rows, columns)
```

#### `setData(data: Union[List[Dict], np.ndarray])`
Replace table data with new data.

```python
new_data = [
    {'Name': 'Charlie', 'Age': 42},
    {'Name': 'Diana', 'Age': 31},
]
editor.setData(new_data)
```

#### Handler Properties

Access the underlying `TableViewHandler` via `editor.handler`:

```python
# Get row count
num_rows = editor.handler.rowCount

# Get column count
num_cols = editor.handler.columnCount

# Get selected row
selected = editor.handler.getSelectedRow()

# Add a row programmatically
editor.handler.addRow({'Name': 'New Person', 'Age': 25})

# Delete a specific row
editor.handler.deleteRow(0)

# Clear all rows
editor.handler.clearAll()
```

### Toolbar Actions

The toolbar provides 12 action buttons for common operations:

| Button | Shortcut | Description |
|--------|----------|-------------|
| Edit | - | Edit the selected cell (or double-click) |
| Undo | Ctrl+Z | Undo the last action |
| Redo | Ctrl+Y | Redo the last undone action |
| Copy | Ctrl+C | Copy selected rows to clipboard |
| Paste | Ctrl+V | Paste rows from clipboard |
| Filter | - | Filter table by column value |
| Refresh | - | Refresh and clear filter |
| Add Row | - | Add a new empty row |
| Delete Row | - | Delete the selected row |
| Clear All | - | Clear all data (with confirmation) |
| Export as List | - | Export data as list of dictionaries |
| Export as NumPy | - | Export data as numpy array |

### Keyboard Shortcuts

```
Ctrl+Z          Undo last action
Ctrl+Y          Redo last undone action
Ctrl+C          Copy selected rows
Ctrl+V          Paste rows from clipboard
Double-click    Edit cell
```

### Status Bar

The status bar appears at the bottom of the editor and displays:

- **Action messages**: Feedback about operations (e.g., "Row added", "Undo", "Filter applied")
- **Row/Column info**: Current number of rows and columns in the table
- **Filter status**: Shows filtered row count when filter is active

```
Status message                    Rows: 10 | Cols: 5
```

## Column Types Reference

### Text Cell (default)

Simple text input field.

```python
column_types = {'Email': 'text'}
```

### Checkbox Cell

Boolean value displayed as a checkbox. Values should be True/False.

```python
column_types = {'Active': 'checkbox'}

data = [
    {'Name': 'Item 1', 'Active': True},
    {'Name': 'Item 2', 'Active': False},
]
```

### ComboBox Cell

Dropdown list for predefined options.

```python
column_types = {'Status': 'combo'}
combo_options = {'Status': ['Active', 'Inactive', 'Pending']}

data = [
    {'Item': 'Product A', 'Status': 'Active'},
    {'Item': 'Product B', 'Status': 'Pending'},
]
```

## Styling

### Light Theme (Default)

```python
editor = createTableEditor(
    headers=['Name', 'Email'],
    data=data,
    apply_style=True,
    dark_mode=False
)
```

### Dark Theme

```python
editor = createTableEditor(
    headers=['Name', 'Email'],
    data=data,
    apply_style=True,
    dark_mode=True
)
```

### No Styling

```python
editor = createTableEditor(
    headers=['Name', 'Email'],
    data=data,
    apply_style=False
)
```

## Advanced Features

### Undo/Redo Support

The editor maintains an undo/redo stack (default 20 steps) for all data modifications:

```python
editor = createTableEditor(headers=['Name'], data=[{'Name': 'Alice'}])

# Make changes
editor.handler.addRow({'Name': 'Bob'})
editor.handler.deleteRow(0)

# Undo last deletion
editor.undoBtn.click()  # or Ctrl+Z

# Redo last undo
editor.redoBtn.click()  # or Ctrl+Y
```

The undo stack is cleared when:
- New data is loaded via `setData()`
- Data is exported
- Application starts

### Copy/Paste Functionality

Copy and paste selected rows:

```python
# Select multiple rows and copy (Ctrl+C)
# The copied data is stored in clipboard

# Paste (Ctrl+V)
# New rows are added to the table with copied data
```

### Filter Functionality

Filter table by column values:

```python
# Click Filter button to open filter dialog
# - Select column to filter
# - Enter filter text (case-insensitive)
# - Click Apply

# To restore original data: Click Refresh button
```

The filter:
- Is case-insensitive
- Matches partial text
- Preserves original data
- Can be cleared with Refresh button

### Comprehensive Status Feedback

The status bar provides real-time feedback:

```
"Ready"                    Initial state
"Row added | Rows: 11"     After adding row
"Row deleted | Rows: 10"   After deleting row
"Cell added | Rows: 10"    Undo/Redo operation
"Copied 3 row(s)"          Copy operation
"Pasted 3 row(s)"          Paste operation
"Filtered: 5 of 10 rows"   Filter applied
"Filter cleared"           Filter removed
"Table cleared"            All data cleared
"Undone"                   Undo operation
"Redone"                   Redo operation
```

## Best Practices for Robust Usage

### 1. Subwindow Implementation

```python
from PySide6.QtWidgets import QMainWindow, QMdiArea, QApplication

app = QApplication(sys.argv)
main = QMainWindow()
main.setWindowTitle("Data Management System")

# Create MDI area
mdi = QMdiArea()
main.setCentralWidget(mdi)

# Create and add table editor subwindow
data = [{'ID': i, 'Name': f'Item {i}'} for i in range(10)]
editor = createTableEditor(
    headers=['ID', 'Name'],
    data=data,
    enable_toolbar=True  # Professional toolbar
)

sub = mdi.addSubWindow(editor)
sub.show()

main.show()
```

### 2. Data Validation

```python
# Validate data before export
data = editor.getDataAsDict()

# Check for empty cells
def has_empty_cells(data):
    for row in data:
        if any(v is None or v == '' for v in row.values()):
            return True
    return False

if has_empty_cells(data):
    QMessageBox.warning(editor, "Validation", "Please fill all cells")
else:
    # Process valid data
    process_data(data)
```

### 3. Size Management for Subwindows

```python
editor = createTableEditor(headers=['Name', 'Email'], data=data)

# Optimize for different screen sizes
if screen_width < 1024:
    editor.resize(800, 400)
else:
    editor.resize(1200, 700)

# Column width adjustment
editor.tableView.horizontalHeader().setStretchLastSection(True)
editor.tableView.resizeColumnsToContents()
```

### 4. Prevent Accidental Loss

The editor tracks changes via undo/redo:

```python
# Before closing subwindow
def closeEvent(event):
    if editor.undoStack or editor.redoStack:
        reply = QMessageBox.question(
            editor, "Unsaved Changes",
            "You have unsaved changes. Close anyway?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            event.ignore()
            return
    event.accept()
```

### 5. Dynamic Column Types

```python
# Configure column types based on data
column_types = {}
for col in headers:
    if col.endswith('_flag'):
        column_types[col] = 'checkbox'
    elif col.endswith('_status'):
        column_types[col] = 'combo'
    else:
        column_types[col] = 'text'

editor = createTableEditor(
    headers=headers,
    data=data,
    column_types=column_types
)
```

## Troubleshooting

### Table shows empty cells
- Check that dictionary keys match header names (case-sensitive)
- Ensure numpy array columns match the order of headers

### ComboBox not showing options
- Verify `combo_options` dictionary is provided
- Check column name matches exactly in both `column_types` and `combo_options`

### Checkboxes not working
- Ensure values are boolean (True/False), not strings
- Verify column is defined as 'checkbox' in `column_types`

### Data not exporting correctly
- Use `getDataAsDict()` for flexible data, `getDataAsNumpy()` for structured data
- Check that all rows have consistent columns

## Examples Location

Complete working examples available at:

- **`/nays/test/example_table_editor.py`** - Basic usage examples (6 examples)
- **`/nays/test/example_enhanced_table_editor.py`** - Enhanced toolbar/status bar examples (3 examples)

Run examples:
```bash
# Basic examples
python3 nays/test/example_table_editor.py

# Enhanced examples (recommended)
python3 nays/test/example_enhanced_table_editor.py
```

The enhanced examples showcase:
1. Full-featured editor matching your design image
2. Simple data with professional toolbar
3. ComboBox and checkbox columns with toolbar

## Testing

Unit tests are available in `/nays/test/test_table_editor.py`.

Run tests:
```bash
pytest nays/test/test_table_editor.py -v
```

## Related Classes

- `TableViewHandler` - Low-level handler for advanced customization
- `TableViewModel` - The underlying model for table data
- `MultiTypeCellDelegate` - Delegate for per-cell type support

For advanced usage, see the TableViewHandler documentation.
