"""
Example: Table Editor with Save/Cancel Callbacks

This example demonstrates how to use the new Save and Cancel buttons with callbacks
to handle data changes in other components or services.

Features shown:
- Save button with confirmation dialog
- Cancel button for reverting changes
- Data callback pattern using PySide6 signals
- Using createTableEditorWithCallback() convenience function
- Processing saved data in callback handlers
"""

import sys

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from nays.ui.handler import createTableEditor, createTableEditorWithCallback

# ============================================================================
# Example 1: Using signals directly
# ============================================================================


def example_1_with_signals():
    """Example 1: Connect to dataSaved and operationCancelled signals directly."""

    data = [
        {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "active": True},
        {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "active": True},
        {"id": 3, "name": "Charlie Brown", "email": "charlie@example.com", "active": False},
        {"id": 4, "name": "Diana Prince", "email": "diana@example.com", "active": True},
    ]

    # Create the editor
    table = createTableEditor(
        headers=["id", "name", "email", "active"],
        data=data,
        column_types={"active": "checkbox"},
        dark_mode=False,
    )

    # Define callback handlers
    def on_data_saved(callback_data):
        """Handle saved data."""
        data_dict = callback_data["dict"]
        data_numpy = callback_data["numpy"]
        row_count = callback_data["rowCount"]
        col_count = callback_data["colCount"]
        headers = callback_data["headers"]

        print("\n" + "=" * 60)
        print("✓ DATA SAVED CALLBACK TRIGGERED")
        print("=" * 60)
        print(f"Rows: {row_count}, Columns: {col_count}")
        print(f"Headers: {headers}")
        print(f"\nData as List of Dicts:")
        for i, row in enumerate(data_dict, 1):
            print(f"  Row {i}: {row}")
        print(f"\nData as NumPy Array shape: {data_numpy.shape}")
        print(f"NumPy Data:\n{data_numpy}")
        print("=" * 60 + "\n")

    def on_cancel():
        """Handle cancel operation."""
        print("\n" + "=" * 60)
        print("✗ OPERATION CANCELLED")
        print("All changes have been discarded")
        print("=" * 60 + "\n")

    # Connect signals to callbacks
    table.dataSaved.connect(on_data_saved)
    table.operationCancelled.connect(on_cancel)

    table.setWindowTitle("Example 1: Save/Cancel with Signals")
    table.resize(700, 500)
    table.show()
    return table


# ============================================================================
# Example 2: Using createTableEditorWithCallback convenience function
# ============================================================================


def example_2_with_convenience_function():
    """Example 2: Use createTableEditorWithCallback for automatic signal connection."""

    # Sample data
    products = [
        {"id": 101, "product": "Laptop", "price": 1200, "stock": 25, "available": True},
        {"id": 102, "product": "Mouse", "price": 25, "stock": 150, "available": True},
        {"id": 103, "product": "Keyboard", "price": 75, "stock": 80, "available": True},
        {"id": 104, "product": "Monitor", "price": 300, "stock": 0, "available": False},
    ]

    def save_to_database(callback_data):
        """Simulate saving to database."""
        print("\n" + "🔒 " + "=" * 56 + " 🔒")
        print("  SAVING DATA TO DATABASE/SERVICE")
        print("🔒 " + "=" * 56 + " 🔒")

        data_dict = callback_data["dict"]
        headers = callback_data["headers"]

        # Simulate database operations
        print(f"\nDatabase Operation:")
        print(f"  └─ Updating {callback_data['rowCount']} records")

        for i, row in enumerate(data_dict, 1):
            print(f"\n  Record {i}:")
            for key, value in row.items():
                if isinstance(value, bool):
                    print(f"    - {key}: {value} (boolean)")
                else:
                    print(f"    - {key}: {value}")

        print(f"\n✅ Successfully saved {callback_data['rowCount']} rows to database")
        print("🔒 " + "=" * 56 + " 🔒\n")

    def handle_cancel():
        """Handle cancel - perhaps revert to previous state."""
        print("\n⚠️  User cancelled the operation - no changes saved")

    # Create editor with callbacks
    table = createTableEditorWithCallback(
        headers=["id", "product", "price", "stock", "available"],
        data=products,
        column_types={"available": "checkbox"},
        on_save=save_to_database,
        on_cancel=handle_cancel,
        dark_mode=True,
    )

    table.setWindowTitle("Example 2: Save/Cancel with Convenience Function")
    table.resize(750, 500)
    table.show()
    return table


# ============================================================================
# Example 3: Multi-window with data synchronization
# ============================================================================


class DataManager(QMainWindow):
    """Main window managing data synchronization between components."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Example 3: Multi-Component Data Sync")
        self.resize(1000, 700)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Top section: Information display
        info_group = QHBoxLayout()
        info_group.addWidget(QLabel("Current Data Status:"))
        self.status_label = QLabel("No data loaded")
        self.status_label.setStyleSheet("color: gray;")
        info_group.addWidget(self.status_label)
        layout.addLayout(info_group)

        # Middle section: Live data preview
        layout.addWidget(QLabel("Live Data Preview (updates after save):"))
        self.data_preview = QTextEdit()
        self.data_preview.setReadOnly(True)
        self.data_preview.setMaximumHeight(250)
        layout.addWidget(self.data_preview)

        # Bottom section: Button to open table editor
        button_layout = QHBoxLayout()
        open_btn = QPushButton("Open Table Editor")
        open_btn.clicked.connect(self.open_editor)
        button_layout.addWidget(open_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.editor = None
        self.current_data = None

    def open_editor(self):
        """Open the table editor window."""
        if self.editor is None or not self.editor.isVisible():
            sample_data = [
                {
                    "task": "Design UI",
                    "assignee": "Alice",
                    "status": "In Progress",
                    "priority": "High",
                },
                {
                    "task": "API Implementation",
                    "assignee": "Bob",
                    "status": "In Progress",
                    "priority": "High",
                },
                {
                    "task": "Testing",
                    "assignee": "Charlie",
                    "status": "Pending",
                    "priority": "Medium",
                },
                {
                    "task": "Documentation",
                    "assignee": "Diana",
                    "status": "Pending",
                    "priority": "Low",
                },
            ]

            self.editor = createTableEditorWithCallback(
                headers=["task", "assignee", "status", "priority"],
                data=sample_data,
                column_types={"status": "combo", "priority": "combo"},
                combo_options={
                    "status": ["Pending", "In Progress", "Completed"],
                    "priority": ["Low", "Medium", "High", "Urgent"],
                },
                on_save=self.handle_data_saved,
                on_cancel=self.handle_cancel,
                dark_mode=False,
            )

            self.editor.setWindowTitle("Task Manager - Table Editor")
            self.editor.resize(800, 500)

        self.editor.show()
        self.editor.raise_()
        self.editor.activateWindow()

    def handle_data_saved(self, callback_data):
        """Handle saved data and update the preview."""
        self.current_data = callback_data

        # Update status
        self.status_label.setText(
            f"✓ Data updated: {callback_data['rowCount']} rows, "
            f"{callback_data['colCount']} columns"
        )
        self.status_label.setStyleSheet("color: green; font-weight: bold;")

        # Update preview
        preview_text = "CURRENT DATA (as List of Dicts):\n"
        preview_text += "-" * 80 + "\n"

        for i, row in enumerate(callback_data["dict"], 1):
            preview_text += f"\n[Row {i}]\n"
            for key, value in row.items():
                preview_text += f"  {key}: {value}\n"

        preview_text += "\n" + "-" * 80 + "\n"
        preview_text += "CURRENT DATA (as NumPy Array):\n"
        preview_text += str(callback_data["numpy"])

        self.data_preview.setText(preview_text)

        print(f"\n📊 Data Manager: Received {callback_data['rowCount']} rows")

    def handle_cancel(self):
        """Handle cancel operation."""
        self.status_label.setText("Last operation cancelled - no changes applied")
        self.status_label.setStyleSheet("color: orange;")


# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    print("\n" + "=" * 70)
    print(" TABLE EDITOR: SAVE/CANCEL CALLBACKS EXAMPLE")
    print("=" * 70)
    print("\nThis example shows 3 ways to handle Save/Cancel operations:")
    print("\n  1. Using signals directly (dataSaved, operationCancelled)")
    print("  2. Using createTableEditorWithCallback() convenience function")
    print("  3. Multi-window with data synchronization")
    print("\nInstructions:")
    print("  - Make changes to the table data")
    print("  - Click Save to trigger callback with data in both formats")
    print("  - Click Cancel to discard changes")
    print("  - All callbacks are executed in the console")
    print("\n" + "=" * 70 + "\n")

    # Create all three examples
    window1 = example_1_with_signals()
    window1.move(50, 50)

    window2 = example_2_with_convenience_function()
    window2.move(850, 50)

    window3 = DataManager()
    window3.move(50, 600)

    sys.exit(app.exec())
