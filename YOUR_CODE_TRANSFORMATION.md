# Your Code Transformation: Direct Implementation Guide

## The Problem You Described

You have existing code using `TableViewHandler` to display and configure tables with config-based data loading (via `loadFromConfigAsColumns()`), and you want to add Save/Cancel functionality without rewriting everything.

## The Solution: `createTableEditorEmbedded()`

The new `createTableEditorEmbedded()` function takes your existing table and data loading approach and wraps it with professional Save/Cancel editor capabilities.

## Your Code: Before & After

### ❌ Before (Your Current Code)

```python
def __setTableElementDefinition(self):
    _data: list[dict[str, any]] = self.vm.dataLoader.getGroup('line')\
            .getSubgroup('elementDefinition')\
                .get()

    materialSegmentData: dict[str, any] = next(
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
    
    self.tableLineElementDefinitionHandler = TableViewHandler(
        self.tableLineElementDefinition, 
        ["ID", "GLEN", "IOPT", "Material Id", "Set As Output", "IPOLY Usage"],
        applyDefaultStyle=True
    )
    self.tableLineElementDefinitionHandler.applyDarkStyle()
    self.tableLineElementDefinitionHandler.loadFromConfigAsColumns(_data, comboDisplayMode="both")
    self.vm.bind(self.tableLineElementDefinitionHandler.dataChanged, self.vm.onLineElementDefinitionChanged)
```

**Issues:**
- No save confirmation
- No undo/redo
- No keyboard shortcuts
- No professional toolbar/status bar
- Data changes immediately (no rollback option)

### ✅ After (With Embedded Editor)

```python
from nays.ui.handler import createTableEditorEmbedded

def __setTableElementDefinition(self):
    _data = self.vm.dataLoader.getGroup('line')\
            .getSubgroup('elementDefinition')\
                .get()

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
    
    # Define what happens when user saves
    def on_save_element_definition(callback_data):
        """Called when user clicks Save and confirms."""
        # Your existing callback - still works!
        self.vm.onLineElementDefinitionChanged(callback_data['dict'])
    
    # Create embedded editor (replaces all the old handler setup!)
    self.tableLineElementDefinitionEditor = createTableEditorEmbedded(
        table_view=self.tableLineElementDefinition,
        headers=["ID", "GLEN", "IOPT", "Material Id", "Set As Output", "IPOLY Usage"],
        config_data=_data,
        on_save=on_save_element_definition,
        apply_dark_style=True,
        combo_display_mode="both"
    )
    
    # Show the editor
    self.tableLineElementDefinitionEditor.show()
```

**Benefits:**
- ✅ Save/Cancel buttons with confirmation dialogs
- ✅ Undo/Redo (Ctrl+Z, Ctrl+Y)
- ✅ Copy/Paste (Ctrl+C, Ctrl+V)
- ✅ Professional toolbar and status bar
- ✅ Data changes only on explicit Save
- ✅ Filter, refresh, add/delete rows
- ✅ All your config data loading still works!

## Line-by-Line Explanation of Changes

### Lines That Don't Change
- Data loading from ViewModel ✅
- Material segment preparation ✅
- All the `_data` manipulation ✅

### What Replaces the Old Handler Setup

**Old (8 lines):**
```python
self.tableLineElementDefinitionHandler = TableViewHandler(...)
self.tableLineElementDefinitionHandler.applyDarkStyle()
self.tableLineElementDefinitionHandler.loadFromConfigAsColumns(...)
self.vm.bind(self.tableLineElementDefinitionHandler.dataChanged, ...)
```

**New (1 function call with embedded handler):**
```python
self.tableLineElementDefinitionEditor = createTableEditorEmbedded(
    table_view=self.tableLineElementDefinition,
    headers=[...],
    config_data=_data,
    on_save=on_save_element_definition,
    apply_dark_style=True,
    combo_display_mode="both"
)
```

## Function Signature - What Each Parameter Does

```python
createTableEditorEmbedded(
    # Required: Your existing table view
    table_view=self.tableLineElementDefinition,
    
    # Required: Column headers (same as before)
    headers=["ID", "GLEN", "IOPT", "Material Id", "Set As Output", "IPOLY Usage"],
    
    # Required: Your config data from dataLoader
    config_data=_data,  # The _data you get from vm.dataLoader
    
    # Optional: What to do when user saves
    on_save=on_save_element_definition,
    
    # Optional: What to do when user cancels (usually not needed)
    on_cancel=None,
    
    # Optional: Apply dark theme (default: True)
    apply_dark_style=True,
    
    # Optional: How to display combo values
    # "key" = show dict keys, "value" = show dict values, "both" = "key: value"
    combo_display_mode="both",
    
    # Optional: Parent widget for dialog hierarchy
    parent=None
)
```

## The Callback Function

The `on_save` function receives data in a structured format:

```python
def on_save_element_definition(callback_data):
    """
    Called when user:
    1. Clicks Save button
    2. Confirms in the dialog
    3. Data is ready to be processed
    """
    
    # Data as list of dicts (your normal use case)
    data_dict = callback_data['dict']
    # Example: [
    #   {'ID': 1, 'GLEN': 10, 'IOPT': True, ...},
    #   {'ID': 2, 'GLEN': 20, 'IOPT': False, ...},
    # ]
    
    # Data as numpy array (for bulk operations)
    data_numpy = callback_data['numpy']
    # Shape: (num_rows, num_cols)
    
    # Metadata
    row_count = callback_data['rowCount']     # 2 in example above
    col_count = callback_data['colCount']     # 6 in example above
    headers = callback_data['headers']        # ['ID', 'GLEN', 'IOPT', ...]
    
    # YOUR EXISTING CALLBACK WORKS HERE!
    self.vm.onLineElementDefinitionChanged(data_dict)
    
    # You can also:
    # - Save to database
    # - Export to file
    # - Update other UI components
    # - Perform calculations on numpy array
    # - Trigger validators
    # - Emit signals to other services
```

## Complete Working Example

Here's your method, fully converted:

```python
from nays.ui.handler import createTableEditorEmbedded

class YourModelClass:  # Whatever class contains this method
    
    def __init__(self, vm):
        self.vm = vm
        self.tableLineElementDefinition = QTableView()  # Your existing table view
        self.tableLineElementDefinitionEditor = None    # Will hold editor
    
    def __setTableElementDefinition(self):
        """
        Replace your existing method with this.
        
        SAME DATA LOADING:
        ✅ Get data from ViewModel
        ✅ Prepare material segment
        ✅ Load config and bind
        
        NEW FEATURES:
        ✨ Save/Cancel buttons
        ✨ Undo/Redo support  
        ✨ Professional toolbar
        ✨ Status bar feedback
        ✨ Modal dialog confirmation
        """
        
        # STEP 1: Load data (UNCHANGED from your code)
        _data: list[dict[str, any]] = self.vm.dataLoader.getGroup('line')\
                .getSubgroup('elementDefinition')\
                    .get()

        # STEP 2: Prepare material segment (UNCHANGED)
        materialSegmentData: dict[str, any] = next(
            (item for item in _data if item.get('name') == 'IPOLY'), 
            None
        )
        
        if materialSegmentData:
            materialSegmentData['items'] = [
                {mat.id: mat.eahigh} 
                for _, mat in enumerate(self.vm.charm3dMaterialPolyService.getAll())
            ]

            for i, item in enumerate(_data):
                if item.get('name') == 'IPOLY':
                    _data[i] = materialSegmentData
                    break
        
        # STEP 3: Define save callback
        def on_save_element_definition(callback_data):
            """
            This replaces:
            self.vm.bind(handler.dataChanged, self.vm.onLineElementDefinitionChanged)
            
            Now you control WHEN the callback is called (only on explicit Save).
            """
            # Your existing callback pattern
            self.vm.onLineElementDefinitionChanged(callback_data['dict'])
            
            # Optional: Do other things
            # self.update_ui()
            # self.validate_data()
            # self.save_to_database()
        
        def on_cancel_element_definition():
            """Optional: Handle when user cancels."""
            print("User cancelled edits - no changes applied")
        
        # STEP 4: Create embedded editor (NEW - ONE FUNCTION CALL!)
        self.tableLineElementDefinitionEditor = createTableEditorEmbedded(
            table_view=self.tableLineElementDefinition,
            headers=[
                "ID",           # Column 0
                "GLEN",         # Column 1
                "IOPT",         # Column 2
                "Material Id",  # Column 3
                "Set As Output",# Column 4
                "IPOLY Usage"   # Column 5
            ],
            config_data=_data,  # Your prepared config data
            on_save=on_save_element_definition,
            on_cancel=on_cancel_element_definition,
            apply_dark_style=True,      # Match your existing style
            combo_display_mode="both"   # Show both key and value
        )
        
        # STEP 5: Show the editor
        # Option A: Show as modal dialog
        self.tableLineElementDefinitionEditor.show()
        
        # Option B: Add to MDI area (if using MDI application)
        # sub = self.mdi_area.addSubWindow(self.tableLineElementDefinitionEditor)
        # sub.show()
```

## What Stays the Same

✅ Your data loading logic  
✅ Your config structures  
✅ Your ViewModel integration  
✅ Your callback pattern  
✅ Dark theme styling  
✅ Column definitions  
✅ Material data preparation  

## What Changes

🔄 Handler creation → Single editor function call  
🔄 Signal binding → Callback function parameter  
🔄 Manual show → Built-in editor window  

## Advanced: Multiple Tables with Same Pattern

If you have multiple config-based tables, create a helper:

```python
def __create_config_editor(self, group: str, subgroup: str, headers: list, on_save=None):
    """Helper to create editors from your dataLoader pattern."""
    from nays.ui.handler import createTableEditorEmbedded
    
    # Get config
    config = self.vm.dataLoader.getGroup(group).getSubgroup(subgroup).get()
    
    # Default callback
    if on_save is None:
        method_name = f'on{subgroup.title()}Changed'
        callback = getattr(self.vm, method_name)
        on_save = lambda data: callback(data['dict'])
    
    # Create editor
    return createTableEditorEmbedded(
        table_view=QTableView(),
        headers=headers,
        config_data=config,
        on_save=on_save,
        apply_dark_style=True
    )

# Usage:
editor1 = self.__create_config_editor(
    group='line',
    subgroup='elementDefinition',
    headers=['ID', 'GLEN', ...]
)

editor2 = self.__create_config_editor(
    group='panel',
    subgroup='elementDefinition',
    headers=['ID', 'TYPE', ...]
)
```

## Testing Your Changes

```python
def test_embedded_editor_integration():
    """Verify the embedded editor works with your data."""
    from nays.ui.handler import createTableEditorEmbedded
    
    # Mock VM
    class MockVM:
        class DataLoader:
            def getGroup(self, g): return self
            def getSubgroup(self, s): return self
            def get(self):
                return [
                    {'name': 'IPOLY', 'type': 'combobox'},
                    {'name': 'IOPT', 'type': 'checkbox'},
                ]
    
    vm = MockVM()
    config = vm.dataLoader.getGroup('line').getSubgroup('elementDefinition').get()
    
    # Create editor
    editor = createTableEditorEmbedded(
        table_view=QTableView(),
        headers=['ID', 'GLEN', 'IOPT', 'Material Id'],
        config_data=config,
        on_save=lambda d: print(f"Saved {len(d['dict'])} rows"),
        apply_dark_style=True,
        combo_display_mode="both"
    )
    
    assert editor is not None
    assert editor.handler is not None
    print("✓ Embedded editor creation successful")
```

## Summary

| Step | Old Way | New Way |
|------|---------|---------|
| 1. Get data | `vm.dataLoader.getGroup(...).get()` | Same |
| 2. Prepare data | Manual `next()` and loop | Same |
| 3. Create handler | `TableViewHandler(...)` | Automatic |
| 4. Apply style | `handler.applyDarkStyle()` | Automatic |
| 5. Load config | `handler.loadFromConfigAsColumns(...)` | Automatic |
| 6. Bind callback | `vm.bind(signal, callback)` | `on_save=callback` |
| 7. Show | Implicit (table already visible) | `editor.show()` |
| **Features** | Basic table | Toolbar + Status Bar + Save/Cancel |

---

**Next Step:** Copy the exact code from the "Complete Working Example" section above into your method and adjust as needed for your specific case.

**Questions?** See `EMBEDDED_EDITOR_INTEGRATION.md` for detailed reference or `test/example_embedded_editor_integration.py` for working examples.
