# Quick Reference: Embedded Editor for Your Code

## The One Thing You Need to Know

**Your existing code that uses `TableViewHandler` with `loadFromConfigAsColumns()` can now be wrapped with Save/Cancel editor in ONE function call:**

```python
from nays.ui.handler import createTableEditorEmbedded

# Your existing setup (8+ lines):
# handler = TableViewHandler(...)
# handler.applyDarkStyle()
# handler.loadFromConfigAsColumns(...)
# vm.bind(...)

# NEW (replace with this):
def on_save(data):
    self.vm.onLineElementDefinitionChanged(data['dict'])

editor = createTableEditorEmbedded(
    table_view=self.tableLineElementDefinition,
    headers=["ID", "GLEN", "IOPT", "Material Id", "Set As Output", "IPOLY Usage"],
    config_data=_data,
    on_save=on_save,
    apply_dark_style=True,
    combo_display_mode="both"
)
editor.show()
```

## That's It!

Your table now has:
- ✨ Save button (with confirmation)
- ✨ Cancel button (with confirmation)
- ✨ Toolbar (Edit, Undo, Redo, Copy, Paste, Filter, etc.)
- ✨ Status bar (real-time feedback)
- ✨ Undo/Redo (Ctrl+Z / Ctrl+Y)
- ✨ Keyboard shortcuts (Ctrl+S to save, etc.)

All while keeping:
- ✅ Your `loadFromConfigAsColumns()` logic
- ✅ Your data loading from ViewModel
- ✅ Your callback pattern
- ✅ Your dark theme

## Complete Code (Copy & Paste)

```python
from nays.ui.handler import createTableEditorEmbedded

def __setTableElementDefinition(self):
    # Your existing code stays the same
    _data = self.vm.dataLoader.getGroup('line')\
            .getSubgroup('elementDefinition').get()

    materialSegmentData = next(
        (item for item in _data if item.get('name') == 'IPOLY'), 
        None
    )
    materialSegmentData['items'] = [
        {mat.id: mat.eahigh} 
        for _, mat in enumerate(self.vm.charm3dMaterialPolyService.getAll())
    ]

    for i, item in enumerate(_data):
        if item.get('name') == 'IPOLY':
            _data[i] = materialSegmentData
            break
    
    # NEW: Define callback
    def on_save(callback_data):
        self.vm.onLineElementDefinitionChanged(callback_data['dict'])
    
    # NEW: Create editor (replaces old handler setup)
    self.tableLineElementDefinitionEditor = createTableEditorEmbedded(
        table_view=self.tableLineElementDefinition,
        headers=["ID", "GLEN", "IOPT", "Material Id", "Set As Output", "IPOLY Usage"],
        config_data=_data,
        on_save=on_save,
        apply_dark_style=True,
        combo_display_mode="both"
    )
    
    # Show editor
    self.tableLineElementDefinitionEditor.show()
```

## Files to Read

1. **`YOUR_CODE_TRANSFORMATION.md`** ← Start here
   - Your exact code before/after
   - Copy this into your project

2. **`EMBEDDED_EDITOR_INTEGRATION.md`**
   - Complete guide with patterns
   - MDI integration
   - Advanced usage

3. **`test/example_embedded_editor_integration.py`**
   - Working example you can run
   - Shows ViewModel integration

## Function Reference

```python
createTableEditorEmbedded(
    table_view,                    # Your table view
    headers,                       # Column headers
    config_data,                   # Your config from dataLoader
    on_save=None,                  # What to do when user saves
    on_cancel=None,                # What to do when user cancels
    apply_dark_style=True,         # Apply dark theme
    combo_display_mode="both"      # How to show combo values
)
```

## Callback Data

```python
def on_save(callback_data):
    # Your data as list of dicts
    data_dict = callback_data['dict']  # [{'ID': 1, 'GLEN': 10, ...}, ...]
    
    # Your data as numpy array
    data_numpy = callback_data['numpy']  # For bulk operations
    
    # Metadata
    row_count = callback_data['rowCount']
    col_count = callback_data['colCount']
    headers = callback_data['headers']
    
    # Do whatever you need
    self.vm.onLineElementDefinitionChanged(data_dict)
```

## That's All You Need

- ✅ One function import
- ✅ One callback definition
- ✅ One function call
- ✅ One `.show()` call

Everything else works the same!

---

**For detailed guidance:** Read `YOUR_CODE_TRANSFORMATION.md`
