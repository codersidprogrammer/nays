# Quick Reference: Transform Your Table View in 3 Steps

## Your Situation

You have this in your UI code:
```python
self.tableLineElementDefinition = QTableView(self.tab_15)
self.verticalLayout_16.addWidget(self.tableLineElementDefinition)
```

## Solution: 3 Easy Steps

### Step 1: Import (at the top of your file)
```python
from nays.ui.handler import createTableEditorEmbedded
```

### Step 2: Define Save Callback
```python
def on_save_handler(callback_data):
    # Your existing callback logic
    self.vm.onLineElementDefinitionChanged(callback_data['dict'])
```

### Step 3: Transform Your Table View
```python
editor = createTableEditorEmbedded(
    table_view=self.tableLineElementDefinition,  # YOUR WIDGET!
    headers=["ID", "GLEN", "IOPT", "Material Id", "Set As Output", "IPOLY Usage"],
    config_data=_data,
    on_save=on_save_handler,
    apply_dark_style=True,
    combo_display_mode="both"
)
```

## Done! Your table now has:
- ✅ Toolbar with buttons
- ✅ Save/Cancel with confirmations
- ✅ Undo/Redo (Ctrl+Z, Ctrl+Y)
- ✅ Copy/Paste (Ctrl+C, Ctrl+V)
- ✅ Filter, Export, and more
- ✅ Professional UI

## Show It
```python
editor.setWindowTitle("Line Element Definition Editor")
editor.resize(900, 600)
editor.show()
```

## Or Embed It in Your Layout
```python
# Replace the table view in your layout
index = self.verticalLayout_16.indexOf(self.tableLineElementDefinition)
self.verticalLayout_16.removeWidget(self.tableLineElementDefinition)
self.verticalLayout_16.insertWidget(index, editor)
```

## Parameters Explained

| Parameter | What to pass |
|-----------|-------------|
| `table_view` | Your existing `self.tableLineElementDefinition` |
| `headers` | Column header names: `["ID", "Col1", "Col2", ...]` |
| `config_data` | Your config list from `dataLoader.get()` |
| `on_save` | Function to call when user clicks Save |
| `apply_dark_style` | `True` for dark theme, `False` for light |
| `combo_display_mode` | `"both"`, `"key"`, or `"value"` for combo boxes |

## That's All You Need!

Your `QTableView` is now transformed into a professional table editor.

---

**For detailed information:** See [TRANSFORM_EXISTING_TABLEVIEW.md](TRANSFORM_EXISTING_TABLEVIEW.md)

**For complete example:** See [test/test_real_world_transform.py](test/test_real_world_transform.py)
