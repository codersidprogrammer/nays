# Quick Reference: Save/Cancel Callbacks

## What's New

✅ **Save Button** - Toolbar button with confirmation to save data and emit callbacks  
✅ **Cancel Button** - Toolbar button with confirmation to cancel edits  
✅ **Signals** - `dataSaved` and `operationCancelled` for callback handling  
✅ **Convenience Function** - `createTableEditorWithCallback()` for easy setup  
✅ **Keyboard Shortcut** - Ctrl+S to save  

## Two Ways to Use It

### Way 1: Manual Signal Connection (More Control)
```python
from nays.ui.handler import createTableEditor

editor = createTableEditor(headers=['name', 'email'], data=[])

def my_save_handler(callback_data):
    print(f"Saved {callback_data['rowCount']} rows")
    data_list = callback_data['dict']
    data_array = callback_data['numpy']

editor.dataSaved.connect(my_save_handler)
editor.show()
```

### Way 2: With Callbacks Pre-connected (Simpler)
```python
from nays.ui.handler import createTableEditorWithCallback

def handle_save(callback_data):
    print(f"Saved {callback_data['rowCount']} rows")

editor = createTableEditorWithCallback(
    headers=['name', 'email'],
    data=[],
    on_save=handle_save
)
editor.show()
```

## What You Get in the Callback

```python
callback_data = {
    'dict': [...],           # Your data as List[Dict]
    'numpy': np.array(...),  # Your data as NumPy array
    'rowCount': 5,           # Number of rows
    'colCount': 2,           # Number of columns
    'headers': ['col1', 'col2']  # Column names
}
```

## Real-World Example

```python
from nays.ui.handler import createTableEditorWithCallback

employees = [
    {'name': 'Alice', 'email': 'alice@company.com'},
    {'name': 'Bob', 'email': 'bob@company.com'},
]

def save_to_database(callback_data):
    """Save employee data to database."""
    for employee in callback_data['dict']:
        # Update database
        db.update_employee(employee)
    print(f"✓ Saved {callback_data['rowCount']} employees")

def handle_cancel():
    """Handle cancellation."""
    print("Changes discarded")

# Create and show editor
editor = createTableEditorWithCallback(
    headers=['name', 'email'],
    data=employees,
    on_save=save_to_database,
    on_cancel=handle_cancel
)
editor.show()
```

## Toolbar Buttons (Updated)

**Data Management:**
- Add Row - Add empty row
- Delete Row - Remove selected row
- Clear All - Remove all rows

**Editing:**
- Edit - Edit selected cell
- Undo (Ctrl+Z) - Undo last change
- Redo (Ctrl+Y) - Redo last undo
- Copy (Ctrl+C) - Copy selected rows
- Paste (Ctrl+V) - Paste copied rows
- Filter - Filter by column
- Refresh - Clear filter

**Features:**
- Export as List - Show data export info
- Export as NumPy - Show array export info

**Save/Cancel:** ⭐ NEW
- **Save (Ctrl+S)** - Save with confirmation → triggers callback
- **Cancel** - Cancel with confirmation → triggers cancel signal

## What Happens When You Click Save

1. Confirmation dialog appears asking to confirm save
2. If user clicks "Yes":
   - Data is gathered in both formats (dict and numpy)
   - Complete package is emitted via `dataSaved` signal
   - Your callback function receives the data
   - Status bar shows "✓ Saved N rows"
   - Undo/Redo stacks are cleared
3. If user clicks "No":
   - Nothing happens, dialog closes

## What Happens When You Click Cancel

1. If there are changes:
   - Confirmation dialog asks to confirm cancellation
   - If user clicks "Yes":
     - `operationCancelled` signal is emitted
     - Status bar shows "Operation cancelled"
     - Undo/Redo stacks are cleared
   - If user clicks "No":
     - Nothing happens, dialog closes

2. If there are NO changes:
   - Signal is emitted immediately (no confirmation needed)

## Key Features

| Feature | Details |
|---------|---------|
| **Data Format** | Both dict and numpy array in one callback |
| **Confirmation** | Built-in dialogs prevent accidental saves |
| **Undo/Redo** | Cleared after successful save |
| **Keyboard** | Ctrl+S shortcut available |
| **Status Bar** | Updates with operation results |
| **Multiple Callbacks** | Can connect multiple callbacks to same signal |
| **Backwards Compatible** | Existing code still works unchanged |

## Integration Examples

### With Database
```python
def save_to_db(data):
    import sqlite3
    conn = sqlite3.connect('mydata.db')
    for row in data['dict']:
        conn.execute("INSERT INTO table VALUES ...", row)
    conn.commit()

editor = createTableEditorWithCallback(
    headers=['...'], data=[...], on_save=save_to_db
)
```

### With Another Widget
```python
def update_display(data):
    # Update another part of your UI
    self.list_widget.setData(data['dict'])
    self.status_label.setText(f"Updated: {data['rowCount']} items")

editor = createTableEditorWithCallback(
    headers=['...'], data=[...], on_save=update_display
)
```

### With File Export
```python
def export_data(data):
    import json
    # Export as JSON
    with open('data.json', 'w') as f:
        json.dump(data['dict'], f)
    # Export as CSV
    import csv
    with open('data.csv', 'w') as f:
        csv.DictWriter(f, data['headers']).writerows(data['dict'])

editor = createTableEditorWithCallback(
    headers=['...'], data=[...], on_save=export_data
)
```

## Keyboard Shortcuts Summary

| Key | Action |
|-----|--------|
| Ctrl+S | Save |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+C | Copy |
| Ctrl+V | Paste |
| Double-click | Edit cell |

## Files Changed/Created

**Modified:**
- `nays/ui/handler/table_editor.py` - Added Save/Cancel buttons and signals
- `nays/ui/handler/__init__.py` - Exported new convenience function

**Created:**
- `test/example_save_cancel_callbacks.py` - 3 complete usage examples
- `test/test_save_cancel_callbacks.py` - 7 automated tests (all passing ✅)
- `SAVE_CANCEL_GUIDE.md` - Complete 850+ line documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation details

## Common Questions

**Q: When should I use which method?**  
A: Use `createTableEditorWithCallback()` for simple cases, use manual signals for more complex scenarios.

**Q: Can I connect multiple callbacks?**  
A: Yes! `editor.dataSaved.connect(callback1)` then `editor.dataSaved.connect(callback2)` - both will trigger.

**Q: What if I want to update data after save?**  
A: Your callback receives the data in both formats, so you can process it however you need.

**Q: Can I validate data before save?**  
A: Yes, write validation logic in your save callback and show error dialogs if validation fails.

**Q: Is the data persistent?**  
A: No, the editor just notifies your callback. You handle persistence in your callback function.

**Q: How do I use it as a subwindow?**  
A: Pass `parent=your_main_window` when creating, or use `mdi.addSubWindow(editor)` for MDI apps.

## Learn More

- **Examples**: `test/example_save_cancel_callbacks.py`
- **Full API**: `SAVE_CANCEL_GUIDE.md`
- **Tests**: `test/test_save_cancel_callbacks.py`
- **Implementation**: `IMPLEMENTATION_SUMMARY.md`

---

**Status**: ✅ Production Ready | All Tests Passing | Fully Documented
