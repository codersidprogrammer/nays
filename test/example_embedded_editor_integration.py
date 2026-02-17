"""
Example: Embedding Table Editor into Existing TableViewHandler Setup

This example shows how to transform existing TableViewHandler code (like your
__setTableElementDefinition) into an editor with Save/Cancel callbacks.

The pattern demonstrates:
1. Your existing data loading approach (loadFromConfigAsColumns)
2. Integration with your ViewModel/Service architecture
3. Save callbacks that work with your existing data handlers
4. Dark theme matching your existing setup
"""

import sys
from typing import Any, Dict, List
import numpy as np

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QLabel, QPushButton, QMessageBox, QStatusBar
)
from PySide6.QtCore import Qt, QTimer

# Import the new embedded editor function
from nays.ui.handler import (
    createTableEditorEmbedded,
    createTableEditor,
    TableViewHandler
)
from nays.ui.handler.table_view_handler import QTableView


# ============================================================================
# Example 1: Direct Replacement of Existing Code
# ============================================================================

class ExistingTableSetupExample:
    """
    Shows how to replace your existing __setTableElementDefinition pattern
    with the new embedded editor.
    """
    
    def setup_old_way(self):
        """The traditional approach you're currently using."""
        
        # Your data structure (same as your code)
        _data: List[Dict[str, Any]] = [
            {'name': 'IPOLY', 'description': 'Material Type', 'type': 'combobox'},
            {'name': 'IOPT', 'description': 'Option Flag', 'type': 'checkbox'},
            {'name': 'GLEN', 'description': 'Length', 'type': 'text'},
        ]
        
        # Create table view (would be self.tableLineElementDefinition in your code)
        table_view = QTableView()
        
        # Create handler
        handler = TableViewHandler(
            table_view,
            ["ID", "GLEN", "IOPT", "Material Id", "Set As Output", "IPOLY Usage"],
            applyDefaultStyle=True
        )
        handler.applyDarkStyle()
        
        # Load your config
        handler.loadFromConfigAsColumns(_data, comboDisplayMode="both")
        
        # Bind to your ViewModel
        # vm.bind(handler.dataChanged, vm.onLineElementDefinitionChanged)
        
        return table_view, handler
    
    def setup_new_way(self):
        """The new approach with save/cancel editor."""
        
        # Your data structure (same as your code)
        _data: List[Dict[str, Any]] = [
            {'name': 'IPOLY', 'description': 'Material Type', 'type': 'combobox'},
            {'name': 'IOPT', 'description': 'Option Flag', 'type': 'checkbox'},
            {'name': 'GLEN', 'description': 'Length', 'type': 'text'},
        ]
        
        # Define your save callback (replaces vm.bind pattern)
        def on_save_line_definition(callback_data):
            """Called when user clicks Save."""
            print("\n" + "="*70)
            print("✓ LINE ELEMENT DEFINITION SAVED")
            print("="*70)
            
            # Your existing callback receives the data
            data = callback_data['dict']
            headers = callback_data['headers']
            
            print(f"Saved {callback_data['rowCount']} rows")
            print(f"Headers: {headers}")
            
            # Process the data like your vm.onLineElementDefinitionChanged would
            for row in data:
                print(f"  Row: {row}")
            
            # Now you can:
            # 1. Update your ViewModel: vm.onLineElementDefinitionChanged(data)
            # 2. Save to database
            # 3. Update other UI components
            # 4. Trigger any other handlers
            
            print("="*70 + "\n")
        
        def on_cancel_line_definition():
            """Called when user clicks Cancel."""
            print("Line definition edit cancelled - no changes applied")
        
        # Create the embedded editor (ONE LINE replaces all the old setup!)
        editor = createTableEditorEmbedded(
            table_view=QTableView(),  # Your existing table view from UI file
            headers=["ID", "GLEN", "IOPT", "Material Id", "Set As Output", "IPOLY Usage"],
            config_data=_data,
            on_save=on_save_line_definition,
            on_cancel=on_cancel_line_definition,
            apply_dark_style=True,
            combo_display_mode="both"
        )
        
        return editor


# ============================================================================
# Example 2: Integration with Your ViewModel Pattern
# ============================================================================

class MockViewModel:
    """Mock ViewModel similar to your self.vm structure."""
    
    class Material:
        def __init__(self, id, high_value):
            self.id = id
            self.eahigh = high_value
    
    class DataLoader:
        def getGroup(self, name):
            self._group = name
            return self
        
        def getSubgroup(self, name):
            self._subgroup = name
            return self
        
        def get(self):
            # Return mock element definition data
            return [
                {
                    'name': 'IPOLY',
                    'description': 'Polynomial Order',
                    'type': 'combobox',
                    'items': [
                        {1: 'Linear'},
                        {2: 'Quadratic'},
                        {3: 'Cubic'}
                    ]
                },
                {
                    'name': 'IOPT',
                    'description': 'Option',
                    'type': 'checkbox',
                    'defaultValue': False
                },
                {
                    'name': 'GLEN',
                    'description': 'Length',
                    'type': 'text',
                    'defaultValue': '1.0'
                }
            ]
    
    class MaterialPolyService:
        def getAll(self):
            return [
                MockViewModel.Material(1, 0.0),
                MockViewModel.Material(2, 1.0),
                MockViewModel.Material(3, 2.0),
            ]
    
    def __init__(self):
        self.dataLoader = self.DataLoader()
        self.charm3dMaterialPolyService = self.MaterialPolyService()
        self.callbacks = {}
    
    def bind(self, signal, callback):
        """Bind a signal to a callback."""
        signal.connect(callback)
    
    def onLineElementDefinitionChanged(self, data):
        """Your existing callback logic."""
        print(f"\nViewModel: Processing {len(data)} line definitions...")
        for row in data:
            print(f"  - {row.get('name', 'unknown')}")


class MyApplication(QMainWindow):
    """Application showing the integration pattern."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Embedded Table Editor - Existing Code Integration")
        self.resize(1000, 700)
        
        # Mock your ViewModel
        self.vm = MockViewModel()
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel("Embedded Table Editor - Integrating with Existing TableViewHandler Code")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        # Info label
        info = QLabel(
            "Click 'Open Editor' to see how your existing TableViewHandler "
            "code transforms into an embedded editor with Save/Cancel."
        )
        layout.addWidget(info)
        
        # Open editor button
        open_btn = QPushButton("Open Embedded Editor")
        open_btn.clicked.connect(self.open_element_definition_editor)
        layout.addWidget(open_btn)
        
        layout.addStretch()
        
        # Status bar
        self.setStatusBar(QStatusBar())
    
    def open_element_definition_editor(self):
        """
        This replaces your __setTableElementDefinition method.
        
        Shows how to integrate the embedded editor with your existing
        data loading and callback patterns.
        """
        
        # Get your data (same as your code)
        _data = self.vm.dataLoader.getGroup('line')\
            .getSubgroup('elementDefinition')\
            .get()
        
        # Prepare material segment data (same as your code)
        material_segment_data = next(
            (item for item in _data if item.get('name') == 'IPOLY'),
            None
        )
        
        if material_segment_data:
            material_segment_data['items'] = [
                {mat.id: mat.eahigh}
                for _, mat in enumerate(self.vm.charm3dMaterialPolyService.getAll())
            ]
            
            # Update data back
            for i, item in enumerate(_data):
                if item.get('name') == 'IPOLY':
                    _data[i] = material_segment_data
                    break
        
        # Define your save callback
        def on_save_handler(callback_data):
            """Handle data save - integrates with your VM."""
            # Your existing callback now works with the data
            self.vm.onLineElementDefinitionChanged(callback_data['dict'])
            
            # Show confirmation
            QMessageBox.information(
                self,
                "Save Successful",
                f"✓ Saved {callback_data['rowCount']} rows\n"
                f"Columns: {callback_data['colCount']}"
            )
            
            self.statusBar().showMessage(
                f"Updated {callback_data['rowCount']} line definitions"
            )
        
        def on_cancel_handler():
            """Handle cancellation."""
            self.statusBar().showMessage("Edit cancelled")
        
        # NEW: Create embedded editor (replaces old handler setup!)
        # Pass your existing table view from the UI file
        editor = createTableEditorEmbedded(
            table_view=QTableView(),  # Your existing self.tableLineElementDefinition
            headers=[
                "ID",
                "GLEN",
                "IOPT",
                "Material Id",
                "Set As Output",
                "IPOLY Usage"
            ],
            config_data=_data,
            on_save=on_save_handler,
            on_cancel=on_cancel_handler,
            apply_dark_style=True,
            combo_display_mode="both"
        )
        
        editor.setWindowTitle("Line Element Definition Editor")
        editor.resize(900, 600)
        editor.show()


# ============================================================================
# Example 3: Side-by-side Comparison
# ============================================================================

def example_3_comparison():
    """Shows the code transformation clearly."""
    
    print("\n" + "="*80)
    print(" CODE TRANSFORMATION: OLD vs NEW")
    print("="*80)
    
    print("\n📋 OLD APPROACH (Your Current Code):")
    print("-" * 80)
    old_code = '''
# Get data
_data = self.vm.dataLoader.getGroup('line').getSubgroup('elementDefinition').get()

# Create handler
handler = TableViewHandler(
    self.tableLineElementDefinition,
    ["ID", "GLEN", "IOPT", "Material Id", ...],
    applyDefaultStyle=True
)
handler.applyDarkStyle()
handler.loadFromConfigAsColumns(_data, comboDisplayMode="both")
self.vm.bind(handler.dataChanged, self.vm.onLineElementDefinitionChanged)
    '''
    print(old_code)
    
    print("\n✨ NEW APPROACH (With Embedded Editor):")
    print("-" * 80)
    new_code = '''
# Same data loading
_data = self.vm.dataLoader.getGroup('line').getSubgroup('elementDefinition').get()

# Define what happens on save
def on_save(data):
    self.vm.onLineElementDefinitionChanged(data['dict'])

# Transform your existing table view (from UI file)!
editor = createTableEditorEmbedded(
    table_view=self.tableLineElementDefinition,  # Your existing widget!
    headers=["ID", "GLEN", "IOPT", "Material Id", ...],
    config_data=_data,
    on_save=on_save,
    apply_dark_style=True,
    combo_display_mode="both"
)

# Replace in layout
self.verticalLayout_X.replaceWidget(self.tableLineElementDefinition, editor)
    '''
    print(new_code)
    
    print("\n" + "="*80)
    print(" BENEFITS OF NEW APPROACH:")
    print("="*80)
    benefits = [
        "✅ Save/Cancel buttons with confirmation dialogs",
        "✅ Keyboard shortcuts (Ctrl+S, Ctrl+Z, etc.)",
        "✅ Undo/Redo history built-in",
        "✅ Status bar with real-time feedback",
        "✅ Data in both dict and numpy formats",
        "✅ Professional UI/UX",
        "✅ Same data loading logic (loadFromConfigAsColumns)",
        "✅ Compatible with your existing callbacks",
        "✅ Can be used as subwindow in MDI",
    ]
    for benefit in benefits:
        print(f"  {benefit}")
    
    print("\n" + "="*80 + "\n")


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    # Show comparison
    example_3_comparison()
    
    # Run application
    app = QApplication(sys.argv)
    
    window = MyApplication()
    window.show()
    
    sys.exit(app.exec())
