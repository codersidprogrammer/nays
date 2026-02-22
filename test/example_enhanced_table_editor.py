#!/usr/bin/env python3
"""
Example: Enhanced Table Editor with Toolbar and Status Bar

Demonstrates the professional table editor component with:
- Professional toolbar (Edit, Undo, Redo, Copy, Paste, Filter, Refresh, etc.)
- Status bar with row/column information
- Undo/Redo support (Ctrl+Z / Ctrl+Y)
- Copy/Paste support (Ctrl+C / Ctrl+V)
- Filter functionality
- Full keyboard shortcuts
"""

import sys

import numpy as np
from PySide6.QtWidgets import QApplication

from nays.ui.handler import createTableEditor


def example_enhanced_editor():
    """Example: Enhanced table editor with toolbar and status bar like your image"""
    print("\n=== Enhanced Table Editor Example ===")

    # Define headers (matching your image)
    headers = ["id", "value", "test", "COLUMN_1", "COLUMN_2", "COLUMN_3", "COLUMN_4", "COLUMN_5"]

    # Define data (similar to your screenshot)
    data = np.array(
        [
            [0, 52, "Institution and ...", False, False, True, True, True],
            [1, 272, "Institution and ...", True, False, True, True, True],
            [2, 134, "Institution and ...", True, False, True, True, False],
            [3, 834, "Institution and ...", False, False, True, True, True],
            [4, 552, "Institution and ...", True, True, False, True, True],
            [5, 266, "Institution and ...", False, False, False, False, False],
            [6, 607, "Institution and ...", False, True, True, False, False],
            [7, 351, "Institution and ...", False, False, True, False, False],
            [8, 46, "Institution and ...", False, True, False, True, False],
        ]
    )

    # Define column types
    column_types = {
        "COLUMN_1": "checkbox",
        "COLUMN_2": "checkbox",
        "COLUMN_3": "checkbox",
        "COLUMN_4": "checkbox",
        "COLUMN_5": "checkbox",
    }

    # Create table editor with toolbar and status bar
    editor = createTableEditor(
        headers=headers,
        data=data,
        column_types=column_types,
        apply_style=True,
        dark_mode=False,
        enable_toolbar=True,  # Show the professional toolbar
    )

    editor.setWindowTitle("Enhanced Table Editor - Features Demo")
    editor.resize(1200, 700)

    print("\nToolbar Actions Available:")
    print("  • Edit - Edit selected cell")
    print("  • Undo - Undo last action (Ctrl+Z)")
    print("  • Redo - Redo last undone action (Ctrl+Y)")
    print("  • Copy - Copy selected rows (Ctrl+C)")
    print("  • Paste - Paste rows (Ctrl+V)")
    print("  • Filter - Filter by column value")
    print("  • Refresh - Refresh and clear filter")
    print("  • Add Row - Add new row")
    print("  • Delete Row - Delete selected row")
    print("  • Clear All - Clear all data")
    print("  • Export as List - Export as dictionary list")
    print("  • Export as NumPy - Export as numpy array")

    print("\nStatus Bar:")
    print("  Shows current row count, column count, and action messages")

    print("\nKeyboard Shortcuts:")
    print("  • Ctrl+Z - Undo")
    print("  • Ctrl+Y - Redo")
    print("  • Ctrl+C - Copy")
    print("  • Ctrl+V - Paste")
    print("  • Double-click - Edit cell")

    return editor


def example_simple_with_toolbar():
    """Example: Simple data with toolbar"""
    print("\n=== Simple Data with Toolbar ===")

    headers = ["Name", "Email", "Active", "Department"]

    data = [
        {
            "Name": "Alice Johnson",
            "Email": "alice@company.com",
            "Active": True,
            "Department": "Engineering",
        },
        {"Name": "Bob Smith", "Email": "bob@company.com", "Active": False, "Department": "Sales"},
        {
            "Name": "Carol White",
            "Email": "carol@company.com",
            "Active": True,
            "Department": "Marketing",
        },
    ]

    column_types = {"Active": "checkbox"}

    editor = createTableEditor(
        headers=headers, data=data, column_types=column_types, enable_toolbar=True, apply_style=True
    )

    editor.setWindowTitle("Simple Table with Professional Toolbar")
    editor.resize(900, 500)

    return editor


def example_combo_and_checkboxes():
    """Example: ComboBox and Checkbox columns with toolbar"""
    print("\n=== ComboBox and Checkbox Columns ===")

    headers = ["Task", "Assignee", "Status", "Priority", "Completed"]

    data = [
        {
            "Task": "Design UI mockups",
            "Assignee": "Alice",
            "Status": "In Progress",
            "Priority": "High",
            "Completed": True,
        },
        {
            "Task": "Implement backend API",
            "Assignee": "Bob",
            "Status": "To Do",
            "Priority": "High",
            "Completed": False,
        },
        {
            "Task": "Write documentation",
            "Assignee": "Carol",
            "Status": "Done",
            "Priority": "Medium",
            "Completed": True,
        },
        {
            "Task": "Setup deployment",
            "Assignee": "David",
            "Status": "In Progress",
            "Priority": "Medium",
            "Completed": False,
        },
    ]

    column_types = {"Status": "combo", "Priority": "combo", "Completed": "checkbox"}

    combo_options = {
        "Status": ["To Do", "In Progress", "Done"],
        "Priority": ["Low", "Medium", "High", "Urgent"],
    }

    editor = createTableEditor(
        headers=headers,
        data=data,
        column_types=column_types,
        combo_options=combo_options,
        enable_toolbar=True,
        apply_style=True,
    )

    editor.setWindowTitle("Task Manager with Toolbar")
    editor.resize(1000, 550)

    return editor


def run_all_examples():
    """Run all enhanced examples"""
    app = QApplication(sys.argv)

    # Create all example editors
    editors = [
        example_enhanced_editor(),
        example_simple_with_toolbar(),
        example_combo_and_checkboxes(),
    ]

    # Position windows
    for i, editor in enumerate(editors):
        editor.move(50 + i * 40, 50 + i * 40)

    print("\n" + "=" * 60)
    print("Enhanced Table Editor Examples Running")
    print("=" * 60)
    print("\nFeatures available:")
    print("  ✓ Professional toolbar with 12 action buttons")
    print("  ✓ Status bar with row/column information")
    print("  ✓ Undo/Redo functionality")
    print("  ✓ Copy/Paste functionality")
    print("  ✓ Filter by column value")
    print("  ✓ Full keyboard shortcut support")
    print("  ✓ Light and dark theme support")
    print("  ✓ Ready for use as subwindow in MDI applications")
    print("\nTry:")
    print("  • Editing cells")
    print("  • Using Ctrl+Z / Ctrl+Y to undo/redo")
    print("  • Selecting rows and pressing Ctrl+C to copy")
    print("  • Pressing Ctrl+V to paste")
    print("  • Using Filter button to filter data")
    print("  • Using Refresh button to clear filter")

    sys.exit(app.exec())


if __name__ == "__main__":
    run_all_examples()
