# Embedded Editor Integration Guide

## Quick Answer: Your Use Case

Your existing code that uses `TableViewHandler` with `loadFromConfigAsColumns()` can now be wrapped with Save/Cancel editor capabilities using the new `createTableEditorEmbedded()` function.

## Your Current Code → New Code

### Your Current Approach

```python
def __setTableElementDefinition(self):
    # Load data from config
    _data: list[dict[str, any]] = self.vm.dataLoader.getGroup('line')\
            .getSubgroup('elementDefinition')\
                .get()

    # Prepare material data
    materialSegmentData = next(
        (item for item in _data if item.get('name') == 'IPOLY'),
        None
    )
    materialSegmentData['items'] = [
        {mat.id: mat.eahigh}
        for _, mat in enumerate(self.vm.charm3dMaterialPolyService.getAll())
    ]

    # Update data
    for i, item in enumerate(_data):
        if item.get('name') == 'IPOLY':
            _data[i] = materialSegmentData
            break

    # Create handler
    self.tableLineElementDefinitionHandler = TableViewHandler(
        self.tableLineElementDefinition,
        ["ID", "GLEN", "IOPT", "Material Id", "Set As Output", "IPOLY Usage"],
        applyDefaultStyle=True
    )
    self.tableLineElementDefinitionHandler.applyDarkStyle()
    self.tableLineElementDefinitionHandler.loadFromConfigAsColumns(_data, comboDisplayMode="both")
    
    # Bind to ViewModel
    self.vm.bind(
        self.tableLineElementDefinitionHandler.dataChanged,
        self.vm.onLineElementDefinitionChanged
    )
```

### New Approach (With Save/Cancel Editor)

```python
from nays.ui.handler import createTableEditorEmbedded

def __setTableElementDefinition(self):
    # Load data from config (same as before)
    _data = self.vm.dataLoader.getGroup('line')\
            .getSubgroup('elementDefinition')\
                .get()

    # Prepare material data (same as before)
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

    # Define save callback (instead of bind)
    def on_save_line_definition(callback_data):
        # Your existing callback still works
        self.vm.onLineElementDefinitionChanged(callback_data['dict'])
    
    def on_cancel_line_definition():
        # Optional: handle cancellation
        pass

    # Create embedded editor (NEW!)
    self.tableLineElementDefinitionEditor = createTableEditorEmbedded(
        table_view=self.tableLineElementDefinition,  # Use your existing table view!
        headers=["ID", "GLEN", "IOPT", "Material Id", "Set As Output", "IPOLY Usage"],
        config_data=_data,
        on_save=on_save_line_definition,
        on_cancel=on_cancel_line_definition,
        apply_dark_style=True,
        combo_display_mode="both"
    )
    
    # Show the editor
    self.tableLineElementDefinitionEditor.show()
```

## Key Differences

| Aspect | Old | New |
|--------|-----|-----|
| Data Loading | `loadFromConfigAsColumns()` | Same, still used |
| Table Setup | Manual handler creation | Automatic |
| Callbacks | `vm.bind()` signal connection | `on_save`, `on_cancel` parameters |
| User Actions | Edit only (no save confirmation) | **Save/Cancel with confirmation** |
| Features | Basic table | Toolbar, status bar, undo/redo, keyboard shortcuts |
| Usage | Standalone table | **Embedded in modal/subwindow with editor** |

## What You Keep

✅ Your `loadFromConfigAsColumns()` logic - **unchanged**  
✅ Your data loading from ViewModel - **unchanged**  
✅ Your callback pattern - **works the same**  
✅ Dark theme - **applied automatically**  
✅ Material data preparation - **unchanged**  

## What You Gain

✨ **Save Button** - User can save with confirmation dialog  
✨ **Cancel Button** - User can cancel changes with confirmation  
✨ **Toolbar** - Edit, Undo, Redo, Copy, Paste, Filter, etc.  
✨ **Status Bar** - Real-time feedback on actions  
✨ **Undo/Redo** - Ctrl+Z and Ctrl+Y support  
✨ **Keyboard Shortcuts** - All standard shortcuts work  
✨ **Professional UX** - Confirmation dialogs prevent accidents  

## Integration Example: Full Method Replacement

```python
from nays.ui.handler import createTableEditorEmbedded

class YourModelClass:
    def __init__(self, vm):
        self.vm = vm
        self.tableLineElementDefinition = QTableView()
        self.tableLineElementDefinitionEditor = None
    
    def __setTableElementDefinition(self):
        """
        Replace your existing method with this.
        All your existing logic stays the same, but now
        you get Save/Cancel editor functionality.
        """
        
        # Step 1: Load data (your existing code)
        _data = self.vm.dataLoader.getGroup('line')\
                .getSubgroup('elementDefinition').get()
        
        materialSegmentData = next(
            (item for item in _data if item.get('name') == 'IPOLY'),
            None
        )
        
        if materialSegmentData:
            # Enrich with material data from service
            materialSegmentData['items'] = [
                {mat.id: mat.eahigh}
                for _, mat in enumerate(self.vm.charm3dMaterialPolyService.getAll())
            ]
            
            # Update in data list
            for i, item in enumerate(_data):
                if item.get('name') == 'IPOLY':
                    _data[i] = materialSegmentData
                    break
        
        # Step 2: Define save handler
        def handle_save(callback_data):
            """
            Called when user clicks Save and confirms.
            Receives data in multiple formats.
            """
            # Option 1: Use dict format (row-by-row)
            data_dict = callback_data['dict']
            
            # Option 2: Use numpy format (bulk operations)
            data_numpy = callback_data['numpy']
            
            # Option 3: Your existing callback
            self.vm.onLineElementDefinitionChanged(data_dict)
            
            # Additional operations
            # - Save to database
            # - Update other UI components
            # - Trigger validators
            # - Emit signals
        
        def handle_cancel():
            """Optional: Called when user clicks Cancel and confirms."""
            print("Edit cancelled - no changes applied")
        
        # Step 3: Create embedded editor (replaces old handler setup!)
        self.tableLineElementDefinitionEditor = createTableEditorEmbedded(
            table_view=self.tableLineElementDefinition,
            headers=[
                "ID", "GLEN", "IOPT", "Material Id",
                "Set As Output", "IPOLY Usage"
            ],
            config_data=_data,
            on_save=handle_save,
            on_cancel=handle_cancel,
            apply_dark_style=True,
            combo_display_mode="both"
        )
        
        # Step 4: Show the editor
        self.tableLineElementDefinitionEditor.show()
        # Or use as MDI subwindow:
        # sub = self.mdi_area.addSubWindow(self.tableLineElementDefinitionEditor)
        # sub.show()
```

## Advanced: Multiple Tables with Same Pattern

If you have multiple tables using this pattern, create a helper function:

```python
def create_config_editor(
    vm,
    group_name: str,
    subgroup_name: str,
    headers: list,
    on_save_handler=None
):
    """Helper for creating embedded editors from your existing pattern."""
    from nays.ui.handler import createTableEditorEmbedded
    
    # Get config data
    config_data = vm.dataLoader.getGroup(group_name)\
                     .getSubgroup(subgroup_name).get()
    
    # Default save handler
    if on_save_handler is None:
        def on_save_handler(data):
            getattr(vm, f'on{subgroup_name.title()}Changed')(data['dict'])
    
    # Create editor
    return createTableEditorEmbedded(
        table_view=QTableView(),
        headers=headers,
        config_data=config_data,
        on_save=on_save_handler,
        apply_dark_style=True,
        combo_display_mode="both"
    )

# Usage:
editor = create_config_editor(
    vm=self.vm,
    group_name='line',
    subgroup_name='elementDefinition',
    headers=["ID", "GLEN", "IOPT", "Material Id", "Set As Output", "IPOLY Usage"]
)
editor.show()
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│ Your ViewModel / Service                                │
│  ├─ dataLoader.getGroup('line').getSubgroup(...)       │
│  ├─ charm3dMaterialPolyService.getAll()                │
│  └─ onLineElementDefinitionChanged(data)               │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ Step 3: Data flows back
                          │ on Save
┌─────────────────────────────────────────────────────────┐
│ Embedded Table Editor                                   │
│  ├─ loadFromConfigAsColumns(_data)                     │
│  ├─ User edits table                                    │
│  ├─ User clicks Save button                             │
│  └─ Callback triggered: on_save(callback_data)          │
└─────────────────────────────────────────────────────────┘
           ▲
           │ Step 1: Config data
           │
           │ Step 2: Column headers
           │
```

## Function Signature Reference

```python
def createTableEditorEmbedded(
    table_view: QTableView,              # Your existing table view
    headers: List[str],                  # Column headers
    config_data: List[Dict[str, Any]],   # From your dataLoader
    on_save: Optional[callable] = None,  # Callback when saved
    on_cancel: Optional[callable] = None,# Callback when cancelled
    apply_dark_style: bool = True,       # Apply dark theme
    combo_display_mode: str = "both",    # "key", "value", or "both"
    parent=None                          # Parent widget
) -> TableEditorWidget:
```

## Callback Data Structure

```python
def on_save(callback_data):
    # Access the data
    data_dict = callback_data['dict']    # List[Dict] - row by row
    data_numpy = callback_data['numpy']  # np.ndarray - bulk operations
    row_count = callback_data['rowCount']
    col_count = callback_data['colCount']
    headers = callback_data['headers']
    
    # Use however you need
    for row in data_dict:
        # Process row by row
        pass
    
    # Or use numpy for bulk operations
    # import pandas as pd
    # df = pd.DataFrame(data_numpy, columns=headers)
```

## Common Integration Patterns

### Pattern 1: Direct ViewModel Update
```python
def on_save(data):
    self.vm.onLineElementDefinitionChanged(data['dict'])
```

### Pattern 2: Database Save
```python
def on_save(data):
    for row in data['dict']:
        db.update_element_definition(row)
    self.vm.onLineElementDefinitionChanged(data['dict'])
```

### Pattern 3: Multi-Step Processing
```python
def on_save(data):
    # Validate
    if not validate(data['dict']):
        return
    
    # Save
    save_to_database(data['dict'])
    
    # Update UI
    self.update_display(data['dict'])
    
    # Notify ViewModel
    self.vm.onLineElementDefinitionChanged(data['dict'])
```

### Pattern 4: Numpy Processing
```python
def on_save(data):
    # Use numpy for numerical operations
    array = data['numpy']
    processed = np.apply_along_axis(my_processor, axis=1, arr=array)
    
    # Convert back to dict
    result = [dict(zip(data['headers'], row)) for row in processed]
    self.vm.onLineElementDefinitionChanged(result)
```

## Troubleshooting

**Q: How do I provide an existing table view?**  
A: Pass it directly to `createTableEditorEmbedded()` via the `table_view` parameter.

**Q: Will my loadFromConfigAsColumns() still work?**  
A: Yes! The embedded editor uses it internally.

**Q: Can I still access the handler?**  
A: Yes, it's `editor.handler`. You have full access to the underlying TableViewHandler.

**Q: What if I need custom styling?**  
A: Set `apply_dark_style=False` and customize with `editor.handler.setCustomStyle()`.

**Q: Can I use this in an MDI application?**  
A: Yes! Use `mdi_area.addSubWindow(editor)` to embed it.

---

**See Also:**
- `test/example_embedded_editor_integration.py` - Full working examples
- `SAVE_CANCEL_GUIDE.md` - Complete callback documentation
- `QUICKSTART_SAVE_CANCEL.md` - Quick reference guide
