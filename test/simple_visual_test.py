"""
Simple test: Visual verification that table displays when button clicked
"""

import sys
from typing import Any, Dict, List

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from nays.ui.handler import createTableEditorEmbedded


class SimpleTestApp(QMainWindow):
    """Simple test application."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Test: Click Button to Open Table Editor")
        self.resize(600, 400)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Title
        title = QLabel("Click the button below to open the table editor")
        title.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(title)

        # Info
        info = QLabel("You should see a window with a table containing 3 rows and 3 columns")
        layout.addWidget(info)

        # Button
        btn = QPushButton("Open Table Editor")
        btn.clicked.connect(self.open_editor)
        layout.addWidget(btn)

        layout.addStretch()
        self.setStatusBar(QStatusBar())

    def open_editor(self):
        """Open the table editor."""
        print("\n>>> Opening table editor...")

        # Data
        config_data = [
            {"name": "Column1", "description": "First column", "type": "text"},
            {"name": "Column2", "description": "Second column", "type": "text"},
            {"name": "Column3", "description": "Third column", "type": "text"},
        ]

        headers = ["ID", "Column1", "Column2", "Column3"]

        def on_save(data):
            print(f"\n✅ Data saved: {data['rowCount']} rows, {data['colCount']} columns")
            print(f"   Headers: {data['headers']}")

        def on_cancel():
            print("\n❌ Operation cancelled")

        # Create editor
        editor = createTableEditorEmbedded(
            headers=headers,
            config_data=config_data,
            on_save=on_save,
            on_cancel=on_cancel,
            apply_dark_style=True,
        )

        # Show it
        editor.setWindowTitle("Table Editor - Check if table is visible!")
        editor.resize(700, 500)
        editor.show()

        print(">>> Table editor window should now be visible")
        print(">>> Check if you can see the table with data")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleTestApp()
    window.show()

    print("\n" + "=" * 70)
    print("APPLICATION STARTED")
    print("=" * 70)
    print("1. Click 'Open Table Editor' button")
    print("2. A new window should appear with a table")
    print("3. The table should have 3 rows and 3 columns")
    print("4. You should see toolbar buttons above the table")
    print("=" * 70 + "\n")

    sys.exit(app.exec())
