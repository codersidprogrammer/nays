"""
Example usage of createTableEditor - Table Editor Component

This script demonstrates how to use the createTableEditor function to create
reusable, editable table components for different data editing scenarios.
"""

import sys

import numpy as np
from PySide6.QtWidgets import QApplication

# Import the createTableEditor function
from nays.ui.handler import createTableEditor


def example_1_simple_list_of_dicts():
    """Example 1: Simple list of dictionaries"""
    print("\n=== Example 1: Simple List of Dictionaries ===")

    # Define headers
    headers = ["Name", "Age", "Email", "Department"]

    # Define data as list of dictionaries
    data = [
        {
            "Name": "Alice Johnson",
            "Age": 28,
            "Email": "alice@company.com",
            "Department": "Engineering",
        },
        {"Name": "Bob Smith", "Age": 35, "Email": "bob@company.com", "Department": "Sales"},
        {"Name": "Carol White", "Age": 32, "Email": "carol@company.com", "Department": "Marketing"},
        {
            "Name": "David Chen",
            "Age": 29,
            "Email": "david@company.com",
            "Department": "Engineering",
        },
    ]

    # Create table editor
    editor = createTableEditor(headers=headers, data=data, apply_style=True)

    editor.setWindowTitle("Example 1: Simple Employee Data")
    editor.show()

    return editor


def example_2_numpy_array():
    """Example 2: Numpy array with typed columns"""
    print("\n=== Example 2: NumPy Array ===")

    # Define headers
    headers = ["ID", "Value", "Status", "Selected"]

    # Define data as numpy array (like your screenshot)
    data = np.array(
        [
            [0, 52, "Institution and ...", True],
            [1, 272, "Institution and ...", False],
            [2, 134, "Institution and ...", True],
            [3, 834, "Institution and ...", False],
            [4, 552, "Institution and ...", True],
            [5, 266, "Institution and ...", False],
            [6, 607, "Institution and ...", True],
            [7, 351, "Institution and ...", False],
            [8, 46, "Institution and ...", True],
        ]
    )

    # Define column types
    column_types = {"ID": "text", "Value": "text", "Status": "text", "Selected": "checkbox"}

    # Create table editor
    editor = createTableEditor(
        headers=headers, data=data, column_types=column_types, apply_style=True, dark_mode=False
    )

    editor.setWindowTitle("Example 2: Data Grid with Checkbox")
    editor.show()

    return editor


def example_3_with_combobox():
    """Example 3: Table with ComboBox columns for dropdown selection"""
    print("\n=== Example 3: With ComboBox Columns ===")

    # Define headers
    headers = ["Product Name", "Category", "Status", "Quantity"]

    # Define data
    data = [
        {"Product Name": "Laptop", "Category": "Electronics", "Status": "Active", "Quantity": 15},
        {
            "Product Name": "Desk Chair",
            "Category": "Furniture",
            "Status": "Inactive",
            "Quantity": 8,
        },
        {"Product Name": "Monitor", "Category": "Electronics", "Status": "Active", "Quantity": 22},
        {"Product Name": "Notebook", "Category": "Stationery", "Status": "Pending", "Quantity": 50},
    ]

    # Define column types
    column_types = {
        "Product Name": "text",
        "Category": "combo",
        "Status": "combo",
        "Quantity": "text",
    }

    # Define combo options
    combo_options = {
        "Category": ["Electronics", "Furniture", "Stationery", "Office Supply"],
        "Status": ["Active", "Inactive", "Pending", "Discontinued"],
    }

    # Create table editor
    editor = createTableEditor(
        headers=headers,
        data=data,
        column_types=column_types,
        combo_options=combo_options,
        apply_style=True,
        dark_mode=False,
    )

    editor.setWindowTitle("Example 3: Product Inventory Manager")
    editor.show()

    return editor


def example_4_mixed_types():
    """Example 4: Complex table with mixed column types"""
    print("\n=== Example 4: Mixed Column Types ===")

    # Define headers
    headers = ["ID", "Feature", "Test Result 1", "Test Result 2", "Test Result 3", "Enabled"]

    # Define data
    data = [
        {
            "ID": 1,
            "Feature": "Installation algorithm",
            "Test Result 1": False,
            "Test Result 2": False,
            "Test Result 3": True,
            "Enabled": True,
        },
        {
            "ID": 2,
            "Feature": "Installation algorithm",
            "Test Result 1": True,
            "Test Result 2": False,
            "Test Result 3": True,
            "Enabled": True,
        },
        {
            "ID": 3,
            "Feature": "Installation algorithm",
            "Test Result 1": True,
            "Test Result 2": False,
            "Test Result 3": True,
            "Enabled": False,
        },
    ]

    # Define column types
    column_types = {
        "Test Result 1": "checkbox",
        "Test Result 2": "checkbox",
        "Test Result 3": "checkbox",
        "Enabled": "checkbox",
    }

    # Create table editor
    editor = createTableEditor(
        headers=headers, data=data, column_types=column_types, apply_style=True, dark_mode=False
    )

    editor.setWindowTitle("Example 4: Test Results Matrix")
    editor.show()

    return editor


def example_5_empty_table():
    """Example 5: Empty table for user to fill in"""
    print("\n=== Example 5: Empty Table ===")

    # Define headers only
    headers = ["First Name", "Last Name", "Email", "Phone", "Active"]

    # Define column types
    column_types = {"Active": "checkbox"}

    # Create empty table editor
    editor = createTableEditor(
        headers=headers, data=None, column_types=column_types, apply_style=True  # No initial data
    )

    editor.setWindowTitle("Example 5: Contact Form (Empty)")
    editor.show()

    return editor


def example_6_dark_theme():
    """Example 6: Same data with dark theme"""
    print("\n=== Example 6: Dark Theme ===")

    headers = ["Task", "Assignee", "Priority", "Completed"]

    data = [
        {"Task": "Design UI mockups", "Assignee": "Alice", "Priority": "High", "Completed": True},
        {
            "Task": "Implement backend API",
            "Assignee": "Bob",
            "Priority": "High",
            "Completed": False,
        },
        {
            "Task": "Write documentation",
            "Assignee": "Carol",
            "Priority": "Medium",
            "Completed": True,
        },
        {"Task": "Setup deployment", "Assignee": "David", "Priority": "Medium", "Completed": False},
    ]

    column_types = {"Completed": "checkbox"}

    # Create with dark mode
    editor = createTableEditor(
        headers=headers,
        data=data,
        column_types=column_types,
        apply_style=True,
        dark_mode=True,  # Enable dark theme
    )

    editor.setWindowTitle("Example 6: Task Manager (Dark Theme)")
    editor.show()

    return editor


def run_all_examples():
    """Run all examples"""
    app = QApplication(sys.argv)

    # Create all example editors
    editors = [
        example_1_simple_list_of_dicts(),
        example_2_numpy_array(),
        example_3_with_combobox(),
        example_4_mixed_types(),
        example_5_empty_table(),
        example_6_dark_theme(),
    ]

    # Position windows
    for i, editor in enumerate(editors):
        editor.move(100 + i * 30, 100 + i * 30)

    print(
        "\nAll examples created. Double-click windows to showcase different table editor capabilities."
    )
    print("Try editing cells, adding/deleting rows, and exporting data.")

    sys.exit(app.exec())


def run_single_example(example_num=1):
    """Run a single example"""
    app = QApplication(sys.argv)

    examples = {
        1: example_1_simple_list_of_dicts,
        2: example_2_numpy_array,
        3: example_3_with_combobox,
        4: example_4_mixed_types,
        5: example_5_empty_table,
        6: example_6_dark_theme,
    }

    example_func = examples.get(example_num, example_1_simple_list_of_dicts)
    editor = example_func()
    editor.show()

    print(f"Running example {example_num}...")
    print(f"Edit cells, add/delete rows, and use Export buttons to see functionality.")

    sys.exit(app.exec())


if __name__ == "__main__":
    # Run all examples
    run_all_examples()

    # Or run a single example:
    # run_single_example(1)  # Run example 1
