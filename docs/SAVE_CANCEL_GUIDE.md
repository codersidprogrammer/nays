# Table Editor: Save/Cancel with Callbacks

## Overview

The table editor now includes professional **Save** and **Cancel** buttons in the toolbar with built-in confirmation dialogs and a signal-based callback system. This allows you to handle data changes in real-time and integrate with other components or services.

## New Features

### 1. Save Button
- **Function**: Save edited data and emit callback signal
- **Keyboard Shortcut**: `Ctrl+S`
- **Behavior**: 
  - Shows confirmation dialog before saving
  - Emits `dataSaved` signal with complete data
  - Clears undo/redo stacks after successful save
  - Updates status bar with save confirmation

### 2. Cancel Button
- **Function**: Discard changes and revert to last saved state
- **Behavior**:
  - Shows confirmation only if there are unsaved changes
  - Emits `operationCancelled` signal
  - Clears undo/redo stacks
  - Updates status bar with cancellation message

### 3. Callback System
The editor uses **PySide6 Signals** for callbacks, allowing you to:
- Connect multiple callbacks to the same event
- Handle data in multiple formats (dict and numpy)
- Process data in other components or services
- Maintain loose coupling between components

## Signals (Callbacks)

### `dataSaved` Signal
Emitted when user confirms the Save operation.

**Emits**: Dictionary containing:
```python
{
    'dict': List[Dict[str, Any]],      # Data as list of dictionaries
    'numpy': np.ndarray,                # Data as 2D numpy array
    'rowCount': int,                    # Number of rows
    'colCount': int,                    # Number of columns
    'headers': List[str]                # Column headers/names
}
```

### `operationCancelled` Signal
Emitted when user confirms the Cancel operation.

**Emits**: None (no parameters)

## Usage Methods

### Method 1: Using `createTableEditor()` with Manual Signal Connection

```python
from nays.ui.handler import createTableEditor

# Create editor
table = createTableEditor(
    headers=['name', 'email', 'active'],
    data=[
        {'name': 'Alice', 'email': 'alice@example.com', 'active': True},
        {'name': 'Bob', 'email': 'bob@example.com', 'active': False},
    ],
    column_types={'active': 'checkbox'}
)

# Define callback handlers
def on_data_saved(callback_data):
    """Handle saved data."""
    data_dict = callback_data['dict']
    data_numpy = callback_data['numpy']
    row_count = callback_data['rowCount']
    headers = callback_data['headers']
    
    print(f"Saved {row_count} rows with headers: {headers}")
    # Do something with the data
    # - Save to database
    # - Update other components
    # - Export to file
    # - Send to API

def on_cancel():
    """Handle cancel operation."""
    print("Operation cancelled - no changes applied")

# Connect signals
table.dataSaved.connect(on_data_saved)
table.operationCancelled.connect(on_cancel)

# Show the editor
table.show()
```

### Method 2: Using `createTableEditorWithCallback()` (Convenience Function)

```python
from nays.ui.handler import createTableEditorWithCallback

def handle_save(callback_data):
    """Process saved data."""
    # Access data in both formats
    data_list = callback_data['dict']
    data_array = callback_data['numpy']
    
    # Update your service/database
    save_to_database(data_list)
    # Or: send_to_api(data_array)

def handle_cancel():
    """Handle cancellation."""
    print("Changes discarded")

# Create editor with callbacks already connected
table = createTableEditorWithCallback(
    headers=['task', 'assignee', 'status'],
    data=[
        {'task': 'Task 1', 'assignee': 'Alice', 'status': 'Pending'},
        {'task': 'Task 2', 'assignee': 'Bob', 'status': 'In Progress'},
    ],
    column_types={'status': 'combo'},
    combo_options={'status': ['Pending', 'In Progress', 'Completed']},
    on_save=handle_save,
    on_cancel=handle_cancel
)

table.show()
```

## Practical Examples

### Example 1: Save to Database

```python
def save_to_database(callback_data):
    """Save data to database."""
    import sqlite3
    
    data_dict = callback_data['dict']
    headers = callback_data['headers']
    
    conn = sqlite3.connect('mydata.db')
    cursor = conn.cursor()
    
    # Insert or update rows
    for row in data_dict:
        # Your database insert/update logic here
        pass
    
    conn.commit()
    conn.close()
    print(f"✓ Saved {len(data_dict)} rows to database")

table = createTableEditorWithCallback(
    headers=['id', 'name', 'email'],
    data=load_from_database(),
    on_save=save_to_database
)
table.show()
```

### Example 2: Update Other Components

```python
class MyApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create table editor with save callback
        self.table_editor = createTableEditorWithCallback(
            headers=['product', 'stock', 'price'],
            data=self.load_products(),
            on_save=self.update_inventory,
            on_cancel=self.on_edit_cancelled
        )
    
    def update_inventory(self, callback_data):
        """Update inventory display when data is saved."""
        # Update another widget with new data
        self.inventory_view.setData(callback_data['dict'])
        self.status_bar.showMessage(
            f"Updated: {callback_data['rowCount']} products"
        )
    
    def on_edit_cancelled(self):
        """Handle edit cancellation."""
        self.status_bar.showMessage("Edit cancelled")
    
    def open_editor(self):
        """Open the table editor."""
        self.table_editor.show()
```

### Example 3: Export to Multiple Formats

```python
def save_and_export(callback_data):
    """Save data and create exports."""
    data_dict = callback_data['dict']
    data_numpy = callback_data['numpy']
    headers = callback_data['headers']
    
    # Export as JSON
    import json
    with open('data.json', 'w') as f:
        json.dump(data_dict, f, indent=2)
    
    # Export as CSV
    import csv
    with open('data.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data_dict)
    
    # Export as Excel (requires openpyxl)
    # import openpyxl
    # wb = openpyxl.Workbook()
    # ws = wb.active
    # ws.append(headers)
    # for row in data_dict:
    #     ws.append([row.get(h) for h in headers])
    # wb.save('data.xlsx')
    
    print(f"✓ Exported {len(data_dict)} rows to JSON, CSV")

table = createTableEditorWithCallback(
    headers=['id', 'name', 'email'],
    data=initial_data,
    on_save=save_and_export
)
table.show()
```

### Example 4: Data Validation Before Save

```python
def validate_and_save(callback_data):
    """Validate data before saving."""
    data_dict = callback_data['dict']
    
    # Validate each row
    errors = []
    for i, row in enumerate(data_dict, 1):
        if not row.get('name'):
            errors.append(f"Row {i}: Name is required")
        if not row.get('email') or '@' not in row['email']:
            errors.append(f"Row {i}: Invalid email")
    
    if errors:
        QMessageBox.warning(
            table,
            "Validation Error",
            "Please fix errors:\n" + "\n".join(errors)
        )
        return
    
    # Data is valid, save it
    save_to_database(data_dict)

table = createTableEditorWithCallback(
    headers=['name', 'email'],
    data=[],
    on_save=validate_and_save
)
table.show()
```

## Callback Data Structure

The `callback_data` dictionary includes:

| Key | Type | Description |
|-----|------|-------------|
| `dict` | `List[Dict[str, Any]]` | Data as list of dictionaries |
| `numpy` | `np.ndarray` | Data as 2D numpy array |
| `rowCount` | `int` | Number of data rows |
| `colCount` | `int` | Number of columns |
| `headers` | `List[str]` | Column header names |

### Example Access:
```python
def my_callback(callback_data):
    # Access as dictionaries
    for row in callback_data['dict']:
        print(row['name'])
    
    # Access as numpy array
    values = callback_data['numpy']
    print(f"Shape: {values.shape}")
    
    # Get metadata
    print(f"{callback_data['rowCount']} rows, {callback_data['colCount']} columns")
```

## Confirmation Dialogs

### Save Confirmation
The Save button shows a confirmation dialog:
```
┌─────────────────────────────────────────────┐
│ Confirm Save                                │
├─────────────────────────────────────────────┤
│ Save changes and emit callback?             │
│                                             │
│ This will notify any connected listeners    │
│ about the data changes.                     │
├─────────────────────────────────────────────┤
│                      [ Yes ]  [ No ]        │
└─────────────────────────────────────────────┘
```

### Cancel Confirmation
The Cancel button shows confirmation only if there are unsaved changes:
```
┌─────────────────────────────────────────────┐
│ Confirm Cancel                              │
├─────────────────────────────────────────────┤
│ Discard all changes and revert to           │
│ last saved state?                           │
│                                             │
│ This action cannot be undone.               │
├─────────────────────────────────────────────┤
│                      [ Yes ]  [ No ]        │
└─────────────────────────────────────────────┘
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Save |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+C` | Copy |
| `Ctrl+V` | Paste |

## Status Bar Messages

The status bar updates with operation results:

| Operation | Message |
|-----------|---------|
| Save success | `✓ Saved N rows` |
| Cancel operation | `Operation cancelled` |
| Filter applied | `Filtered: N of M rows` |
| Copy operation | `Copied N row(s)` |
| Paste operation | `Pasted N row(s)` |
| Add row | `Row added \| Rows: N` |
| Delete row | `Row deleted \| Rows: N` |
| Clear all | `Table cleared` |

## Multiple Callback Connections

You can connect multiple callbacks to the same signal:

```python
table = createTableEditor(
    headers=['col1', 'col2'],
    data=[]
)

# Connect multiple save callbacks
table.dataSaved.connect(lambda data: save_to_database(data))
table.dataSaved.connect(lambda data: export_to_csv(data))
table.dataSaved.connect(lambda data: update_ui(data))

# All three callbacks will be triggered when Save is clicked
```

## Integration with MDI Applications

Use the table editor as a subwindow in MDI (Multiple Document Interface) applications:

```python
from PySide6.QtWidgets import QMainWindow, QMdiArea

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create MDI area
        mdi = QMdiArea()
        self.setCentralWidget(mdi)
        
        # Create table editor subwindow
        editor = createTableEditorWithCallback(
            headers=['field1', 'field2'],
            data=[],
            on_save=self.handle_editor_save,
            on_cancel=self.handle_editor_cancel
        )
        
        # Add as subwindow
        subwindow = mdi.addSubWindow(editor)
        subwindow.show()
    
    def handle_editor_save(self, callback_data):
        """Handle data saved from subwindow."""
        print(f"Saved {callback_data['rowCount']} rows")
```

## Performance Considerations

1. **Large Datasets**: For tables with >10,000 rows:
   - Consider implementing pagination in the callback
   - Use numpy array export for bulk operations
   - Implement batch processing in your save handler

2. **Callback Execution**: 
   - Keep callback functions fast to maintain UI responsiveness
   - Offload heavy operations to background threads if needed

3. **Memory**:
   - Both dict and numpy format are included in callback
   - Use the format most suitable for your use case
   - Consider cleaning up large dataframes after processing

## Troubleshooting

### Callback Not Triggered
- Ensure signal is connected before user action: `table.dataSaved.connect(handler)`
- Check that user clicks the toolbar Save button, not just editing data
- Verify handler function signature: `def handler(callback_data):`

### Confirmation Dialog Not Showing
- This is normal for Cancel if there are no unsaved changes
- Save always shows confirmation (as per design)
- Check confirmation was not cancelled by user

### Data Format Issues
- Dict format: Use for row-by-row processing, JSON export
- NumPy format: Use for mathematical operations, bulk updates
- Both formats available simultaneously in callback data

## API Reference

### `createTableEditor()`
Create an editor and manually connect callbacks.

```python
editor = createTableEditor(
    headers: List[str],
    data: Optional[Union[List[Dict], np.ndarray]] = None,
    column_types: Optional[Dict[str, str]] = None,
    combo_options: Optional[Dict[str, List[str]]] = None,
    enable_toolbar: bool = True,
    apply_style: bool = True,
    dark_mode: bool = False,
    parent=None
) -> TableEditorWidget

# Then connect:
editor.dataSaved.connect(my_save_handler)
editor.operationCancelled.connect(my_cancel_handler)
```

### `createTableEditorWithCallback()`
Create an editor with callbacks pre-connected.

```python
editor = createTableEditorWithCallback(
    headers: List[str],
    data: Optional[Union[List[Dict], np.ndarray]] = None,
    column_types: Optional[Dict[str, str]] = None,
    combo_options: Optional[Dict[str, List[str]]] = None,
    on_save: Optional[callable] = None,
    on_cancel: Optional[callable] = None,
    apply_style: bool = True,
    dark_mode: bool = False,
    parent=None
) -> TableEditorWidget
```

## Related Features

- **Toolbar Actions**: Edit, Undo, Redo, Copy, Paste, Filter, Add Row, Delete Row, Clear All, Export
- **Status Bar**: Real-time feedback with operation messages and row/column count
- **Column Types**: Text, Checkbox, ComboBox
- **Styling**: Light and dark themes
- **Data Persistence**: Via callback system (your application handles storage)

For more examples, see:
- `test/example_save_cancel_callbacks.py` - Comprehensive callback examples
- `test/example_enhanced_table_editor.py` - Toolbar and status bar usage
