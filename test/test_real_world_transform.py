"""
Test: Transform existing QTableView from UI file into Table Editor

This demonstrates the key use case: you have a QTableView already in your
UI file/layout, and you want to transform it into a table editor.
"""

import sys
from typing import Any, Dict, List

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QLabel, QPushButton, QStatusBar, QTableView
)

from nays.ui.handler import createTableEditorEmbedded


class RealWorldApp(QMainWindow):
    """Simulates how you would use this in your actual code."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real World Test: Create Independent Editor from UI Table")
        self.resize(1000, 700)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel("Simulate Your UI: Transform Existing Table View")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        # Info
        info_label = QLabel(
            "This simulates having self.tableLineElementDefinition in your UI.\n"
            "Click the button to open a separate editor window for the same data."
        )
        layout.addWidget(info_label)
        
        # Create a container that simulates your tab/panel
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        # Label (like your UI has)
        label = QLabel("Line Element Definition:")
        container_layout.addWidget(label)
        
        # THIS IS THE KEY: Create the table view like it would be in your UI file
        # In your code: self.tableLineElementDefinition = QTableView(self.tab_15)
        self.tableLineElementDefinition = QTableView(container)
        self.tableLineElementDefinition.setObjectName("tableLineElementDefinition")
        self.tableLineElementDefinition.setMinimumHeight(200)
        container_layout.addWidget(self.tableLineElementDefinition)
        
        # Button to transform it
        transform_btn = QPushButton("Open Editor Window")
        transform_btn.clicked.connect(self.transform_table_to_editor)
        container_layout.addWidget(transform_btn)
        
        # Add the container to main layout
        layout.addWidget(container)
        layout.addStretch()
        
        self.setStatusBar(QStatusBar())
    
    def transform_table_to_editor(self):
        """Transform the existing table view into an editor."""
        
        print("\n" + "="*70)
        print("OPENING EDITOR FOR TABLE")
        print("="*70)
        
        # Your config data (from dataLoader)
        _data = [
            {'name': 'IPOLY', 'description': 'Polynomial', 'type': 'combobox'},
            {'name': 'IOPT', 'description': 'Option', 'type': 'checkbox'},
            {'name': 'GLEN', 'description': 'Length', 'type': 'text'},
        ]
        
        # Headers
        headers = ["ID", "GLEN", "IOPT", "Material Id", "Set As Output", "IPOLY Usage"]
        
        # Define callbacks
        def on_save(callback_data):
            print(f"\n✅ SAVE CALLBACK:")
            print(f"   Rows: {callback_data['rowCount']}")
            print(f"   Columns: {callback_data['colCount']}")
            print(f"   Data: {callback_data['dict']}")
            # Here you would call: self.vm.onLineElementDefinitionChanged(data)
            # This would update the original table view in the container
        
        def on_cancel():
            print(f"\n❌ CANCEL CALLBACK")
        
        # Create editor
        # Note: The original self.tableLineElementDefinition stays in the container
        # The editor gets its own table view that's independent
        print("\n✓ Creating editor with config data...")
        
        editor = createTableEditorEmbedded(
            table_view=self.tableLineElementDefinition,  # Reference kept (but editor uses its own internal table)
            headers=headers,
            config_data=_data,
            on_save=on_save,
            on_cancel=on_cancel,
            apply_dark_style=True,
            combo_display_mode="both"
        )
        
        print(f"✓ Editor created successfully!")
        print(f"  - Editor type: {type(editor).__name__}")
        print(f"  - Editor table view object: {editor.tableView}")
        print(f"  - Editor table visible: {editor.tableView.isVisible()}")
        print(f"  - Editor table model rows: {editor.tableView.model().rowCount()}")
        print(f"  - Editor table model cols: {editor.tableView.model().columnCount()}")
        print(f"\n✓ Original table in container: STILL VISIBLE")
        print(f"  - Original table object: {self.tableLineElementDefinition}")
        print(f"  - Original table parent: {self.tableLineElementDefinition.parent()}")
        
        # Show the editor in a new window
        editor.setWindowTitle("Transformed Table Editor")
        editor.resize(900, 600)
        editor.show()
        
        print(f"\n✅ Editor window opened in separate window!")
        print(f"   Original table view stays in container for reference")
        print("="*70 + "\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RealWorldApp()
    window.show()
    
    print("\n" + "="*70)
    print("REAL WORLD TEST: Create Independent Editor")
    print("="*70)
    print("1. You have self.tableLineElementDefinition in your UI")
    print("2. Click 'Open Editor Window' button")
    print("3. A separate editor window opens with independent table")
    print("4. Original table stays in container")
    print("5. Save in editor syncs data back via callback")
    print("="*70 + "\n")
    
    sys.exit(app.exec())
