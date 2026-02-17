"""
Debug: Detailed investigation of why table isn't showing
"""

import sys
from typing import Any, Dict, List

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QLabel, QPushButton, QMessageBox, QStatusBar
)
from PySide6.QtCore import Qt

from nays.ui.handler import createTableEditorEmbedded
from nays.ui.handler.table_view_handler import QTableView


class DebugApplication(QMainWindow):
    """Debug application to diagnose the table display issue."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Debug: Embedded Table Editor")
        self.resize(800, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel("Debug: Click button to open editor and check details")
        title.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(title)
        
        # Open editor button
        open_btn = QPushButton("Open Embedded Editor & Debug")
        open_btn.clicked.connect(self.debug_open_editor)
        layout.addWidget(open_btn)
        
        layout.addStretch()
        self.setStatusBar(QStatusBar())
    
    def debug_open_editor(self):
        """Debug version with detailed output."""
        
        print("\n" + "="*80)
        print("DEBUG: Starting editor creation")
        print("="*80)
        
        # Prepare data
        _data = [
            {'name': 'IPOLY', 'description': 'Material Type', 'type': 'combobox'},
            {'name': 'IOPT', 'description': 'Option Flag', 'type': 'checkbox'},
            {'name': 'GLEN', 'description': 'Length', 'type': 'text'},
        ]
        
        headers = ["ID", "GLEN", "IOPT", "Material Id", "Set As Output", "IPOLY Usage"]
        
        print(f"✓ Data prepared: {len(_data)} config items")
        print(f"✓ Headers: {headers}")
        
        # Create fresh table view
        table_view = QTableView()
        print(f"\n✓ QTableView created")
        print(f"  - Is visible (before): {table_view.isVisible()}")
        print(f"  - Parent: {table_view.parent()}")
        print(f"  - Model: {table_view.model()}")
        
        # Callbacks
        def on_save_handler(callback_data):
            print(f"\n✅ SAVE CALLBACK TRIGGERED:")
            print(f"   Rows: {callback_data['rowCount']}")
            print(f"   Cols: {callback_data['colCount']}")
            print(f"   Data: {callback_data['dict']}")
        
        def on_cancel_handler():
            print(f"\n❌ CANCEL CALLBACK TRIGGERED")
        
        # Create embedded editor
        print(f"\n✓ Creating embedded editor...")
        
        editor = createTableEditorEmbedded(
            table_view=table_view,
            headers=headers,
            config_data=_data,
            on_save=on_save_handler,
            on_cancel=on_cancel_handler,
            apply_dark_style=True,
            combo_display_mode="both"
        )
        
        print(f"✓ Editor created")
        print(f"  - Editor visible: {editor.isVisible()}")
        print(f"  - Editor size: {editor.width()} x {editor.height()}")
        
        print(f"\n✓ Table view after creation:")
        print(f"  - Same object: {editor.tableView is table_view}")
        print(f"  - Is visible: {editor.tableView.isVisible()}")
        print(f"  - Parent: {editor.tableView.parent()}")
        print(f"  - Parent is editor: {editor.tableView.parent() is editor}")
        
        print(f"\n✓ Table model:")
        model = editor.tableView.model()
        print(f"  - Model exists: {model is not None}")
        if model:
            print(f"  - Model type: {type(model).__name__}")
            print(f"  - Row count: {model.rowCount()}")
            print(f"  - Column count: {model.columnCount()}")
            
            # Try to read data
            for row in range(min(2, model.rowCount())):
                row_data = []
                for col in range(model.columnCount()):
                    item = model.item(row, col)
                    if item:
                        row_data.append(item.text())
                print(f"  - Row {row}: {row_data}")
        
        print(f"\n✓ Handler:")
        if editor.handler:
            print(f"  - Handler exists: True")
            print(f"  - Handler table: {editor.handler.tableView is editor.tableView}")
            data = editor.handler.getData()
            print(f"  - Handler data count: {len(data)}")
        else:
            print(f"  - Handler exists: False (!!! PROBLEM)")
        
        print(f"\n✓ Editor layout:")
        layout = editor.layout()
        print(f"  - Layout type: {type(layout).__name__}")
        print(f"  - Widget count: {layout.count()}")
        for i in range(layout.count()):
            w = layout.itemAt(i).widget()
            if w:
                print(f"  - [{i}] {type(w).__name__} - visible: {w.isVisible()}")
        
        # Show the editor
        print(f"\n✓ Showing editor...")
        editor.setWindowTitle("Debug: Line Element Definition Editor")
        editor.resize(900, 600)
        editor.show()
        
        print(f"\nAfter show():")
        print(f"  - Editor visible: {editor.isVisible()}")
        print(f"  - Table visible: {editor.tableView.isVisible()}")
        
        print("\n" + "="*80)
        print("✅ Editor should be visible now. Check the window!")
        print("="*80 + "\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DebugApplication()
    window.show()
    
    # Run a bit so we can see console output
    from PySide6.QtCore import QTimer
    def close_after():
        # Don't auto-close, let user interact
        pass
    
    sys.exit(app.exec())
