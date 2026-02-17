# How to Transform Your Existing QTableView into a Table Editor

## Your Current UI Code

You have code like this in your UI file:

```python
self.tabWidget_2.addTab(self.tab_9, "")
self.tab_15 = QWidget()
self.tab_15.setObjectName(u"tab_15")
self.verticalLayout_16 = QVBoxLayout(self.tab_15)
self.verticalLayout_16.setObjectName(u"verticalLayout_16")

self.label_9 = QLabel(self.tab_15)
self.label_9.setObjectName(u"label_9")
self.verticalLayout_16.addWidget(self.label_9)

# THIS IS THE KEY WIDGET:
self.tableLineElementDefinition = QTableView(self.tab_15)
self.tableLineElementDefinition.setObjectName(u"tableLineElementDefinition")
self.verticalLayout_16.addWidget(self.tableLineElementDefinition)
```

## How to Transform It

### Option 1: Simple Transformation (Recommended)

In your code where you would set up the handler, change from:

```python
# OLD: Traditional TableViewHandler
handler = TableViewHandler(
    self.tableLineElementDefinition,
    headers,
    applyDefaultStyle=True
)
handler.applyDarkStyle()
handler.loadFromConfigAsColumns(_data, comboDisplayMode="both")
```

To:

```python
# NEW: Transform with createTableEditorEmbedded
from nays.ui.handler import createTableEditorEmbedded

def on_save_line_definition(callback_data):
    # Your existing callback logic
    self.vm.onLineElementDefinitionChanged(callback_data['dict'])
    # Save to database, etc.

editor = createTableEditorEmbedded(
    table_view=self.tableLineElementDefinition,  # PASS YOUR EXISTING WIDGET!
    headers=[...],  # Your headers
    config_data=_data,  # Your config data
    on_save=on_save_line_definition,
    apply_dark_style=True,
    combo_display_mode="both"
)
```

### Option 2: Replace in Layout

If you want to replace the bare table view in the layout with the editor:

```python
# OLD: Just the table view in the layout
self.verticalLayout_16.addWidget(self.tableLineElementDefinition)

# NEW: Replace with editor
editor = createTableEditorEmbedded(
    table_view=self.tableLineElementDefinition,
    headers=[...],
    config_data=_data,
    on_save=on_save_handler,
)

# Replace the widget in the layout
index = self.verticalLayout_16.indexOf(self.tableLineElementDefinition)
self.verticalLayout_16.removeWidget(self.tableLineElementDefinition)
self.verticalLayout_16.insertWidget(index, editor)
```

## What Happens Internally

When you call `createTableEditorEmbedded()` with your existing table view:

1. **Your table view is removed from its current parent layout**
2. **A new TableEditorWidget is created** (this is the wrapper)
3. **Your table view is added inside the TableEditorWidget**
4. **The editor gets wrapped with:**
   - Toolbar (Edit, Undo, Redo, Copy, Paste, Filter, Refresh, Add Row, Delete Row, Clear, Export, Save, Cancel)
   - Your table view (centered, taking all available space)
   - Status bar (showing row/column count)

5. **The TableViewHandler is configured with your data**

## The Result

Your existing `QTableView` widget is now:
- ✅ Wrapped in a professional editor
- ✅ Has a toolbar with useful actions
- ✅ Has Save/Cancel buttons with confirmations
- ✅ Has Undo/Redo functionality
- ✅ Has Copy/Paste support
- ✅ Has Filter capability
- ✅ Still loads data using `loadFromConfigAsColumns()` (your existing approach)
- ✅ Still calls your existing callbacks
- ✅ Has a status bar showing feedback

## Complete Example for Your Use Case

```python
# In your ViewModel/Dialog class where you set up tables:

def __setTableElementDefinition(self):
    """Setup the line element definition table."""
    
    # Get your data (existing pattern)
    _data = self.vm.dataLoader \
        .getGroup('line') \
        .getSubgroup('elementDefinition') \
        .get()
    
    headers = [
        "ID",
        "GLEN", 
        "IOPT",
        "Material Id",
        "Set As Output",
        "IPOLY Usage"
    ]
    
    # Define save callback (what happens when user clicks Save)
    def on_save_line_definition(callback_data):
        """Handle the save event."""
        # Call your existing ViewModel method with the data
        self.vm.onLineElementDefinitionChanged(callback_data['dict'])
        
        # Optional: Show confirmation
        QMessageBox.information(
            self,
            "Saved",
            f"✓ {callback_data['rowCount']} rows saved"
        )
    
    # Define cancel callback (optional)
    def on_cancel_line_definition():
        """Handle the cancel event."""
        print("Edit cancelled")
    
    # TRANSFORM: Create editor from your existing table view!
    editor = createTableEditorEmbedded(
        table_view=self.tableLineElementDefinition,  # ← Your existing widget!
        headers=headers,
        config_data=_data,
        on_save=on_save_line_definition,
        on_cancel=on_cancel_line_definition,
        apply_dark_style=True,
        combo_display_mode="both"
    )
    
    # Optional: Replace in layout if using MDI or sub-window
    # index = self.verticalLayout_16.indexOf(self.tableLineElementDefinition)
    # self.verticalLayout_16.removeWidget(self.tableLineElementDefinition)
    # self.verticalLayout_16.insertWidget(index, editor)
```

## Important: The Transformation Process

The key insight is:
1. Your existing `self.tableLineElementDefinition` QTableView widget is passed to the function
2. It gets **removed from its current parent** (if it has one)
3. It gets **added as a child of the new TableEditorWidget**
4. The whole editor is returned for you to use

This means:
- ✅ Your widget reference (`self.tableLineElementDefinition`) still points to the same object
- ✅ But it's now contained within an editor widget
- ✅ All your data loading logic works the same
- ✅ All your callbacks work the same

## Testing Your Transformation

To test if everything is working:

1. Call the transformation function in your code
2. Your table view should now appear inside an editor with:
   - A toolbar above (with buttons)
   - The table data proper rendering
   - A status bar below (showing row/column count)

## Troubleshooting

**Q: The table is not visible?**
- A: Make sure you're passing your existing `QTableView` widget to the function
- A: The function returns an editor widget - use this returned widget in your layout

**Q: My data is not showing?**
- A: Make sure `config_data` is the correct format for `loadFromConfigAsColumns()`
- A: Check that `headers` match your expected structure

**Q: Callbacks are not working?**
- A: Make sure you defined `on_save` and `on_cancel` functions
- A: These are called when the user clicks Save or Cancel buttons

## Files to Reference

- [nays/ui/handler/table_editor.py](nays/ui/handler/table_editor.py#L766) - Complete implementation
- [test/test_real_world_transform.py](test/test_real_world_transform.py) - Working example
- [test/example_embedded_editor_integration.py](test/example_embedded_editor_integration.py) - Full integration example
