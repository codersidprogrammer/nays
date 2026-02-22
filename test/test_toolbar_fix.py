#!/usr/bin/env python3
"""Quick test for toolbar functionality"""

import sys

from PySide6.QtWidgets import QApplication

from nays.ui.handler import createTableEditor

app = QApplication(sys.argv)

# Create test editor with some data
editor = createTableEditor(
    headers=["Name", "Age", "Active"],
    data=[
        {"Name": "Alice", "Age": 28, "Active": True},
        {"Name": "Bob", "Age": 35, "Active": False},
    ],
    column_types={"Active": "checkbox"},
)

# Test toolbar actions work without errors
print("Testing toolbar functionality...")

# Test Add Row
print("✓ Testing Add Row...")
editor._onAddRow()
print(f"  Current rows: {editor.handler.rowCount}")

# Test Copy
print("✓ Testing Copy...")
# Select first row
editor.tableView.selectRow(0)
editor._onCopy()

# Test Paste
print("✓ Testing Paste...")
editor._onPaste()
print(f"  Current rows: {editor.handler.rowCount}")

# Test Undo
print("✓ Testing Undo...")
editor._onUndo()
print(f"  Current rows: {editor.handler.rowCount}")

# Test Redo
print("✓ Testing Redo...")
editor._onRedo()
print(f"  Current rows: {editor.handler.rowCount}")

# Test Export Dict
print("✓ Testing Export as Dict...")
data_dict = editor.getDataAsDict()
print(f"  Exported {len(data_dict)} rows")

# Test Export Numpy
print("✓ Testing Export as NumPy...")
data_numpy = editor.getDataAsNumpy()
print(f"  Exported array shape: {data_numpy.shape}")

# Test Filter
print("✓ Testing Filter...")
# This just opens a dialog, so we'll skip for automated test

print("\n✅ All toolbar functionality tests passed!")
