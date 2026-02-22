"""
Unit tests for Table Editor Component

Tests the createTableEditor function and TableEditorWidget class
"""

import sys

import numpy as np
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from nays.ui.handler import TableEditorWidget, createTableEditor


@pytest.fixture(scope="session")
def qt_app():
    """Create QApplication for all tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


class TestCreateTableEditor:
    """Test createTableEditor function"""

    def test_create_with_list_of_dicts(self, qt_app):
        """Test creating table with list of dictionaries"""
        headers = ["Name", "Age", "Active"]
        data = [
            {"Name": "Alice", "Age": 28, "Active": True},
            {"Name": "Bob", "Age": 35, "Active": False},
        ]

        editor = createTableEditor(headers=headers, data=data)

        assert isinstance(editor, TableEditorWidget)
        assert editor.handler.rowCount == 2
        assert editor.handler.columnCount == 3

        # Get data back
        exported = editor.getDataAsDict()
        assert len(exported) == 2
        assert exported[0]["Name"] == "Alice"
        assert exported[1]["Age"] == 35

    def test_create_with_numpy_array(self, qt_app):
        """Test creating table with numpy array"""
        headers = ["ID", "Value", "Status"]
        data = np.array(
            [
                [1, 100, "Active"],
                [2, 200, "Inactive"],
                [3, 300, "Active"],
            ]
        )

        editor = createTableEditor(headers=headers, data=data)

        assert editor.handler.rowCount == 3
        assert editor.handler.columnCount == 3

        # Get data back as numpy
        exported = editor.getDataAsNumpy()
        assert exported.shape[0] == 3
        assert exported.shape[1] == 3

    def test_create_empty_table(self, qt_app):
        """Test creating empty table"""
        headers = ["Name", "Email", "Phone"]

        editor = createTableEditor(headers=headers, data=None)

        assert editor.handler.rowCount == 0
        assert editor.handler.columnCount == 3

    def test_column_types_checkbox(self, qt_app):
        """Test table with checkbox column type"""
        headers = ["Name", "Active"]
        data = [
            {"Name": "Item 1", "Active": True},
            {"Name": "Item 2", "Active": False},
        ]
        column_types = {"Active": "checkbox"}

        editor = createTableEditor(headers=headers, data=data, column_types=column_types)

        # Check that checkbox type was set
        assert editor.handler.model.cellTypes[1] == "checkbox"

    def test_column_types_combo(self, qt_app):
        """Test table with combobox column type"""
        headers = ["Product", "Status"]
        data = [
            {"Product": "A", "Status": "Active"},
            {"Product": "B", "Status": "Inactive"},
        ]
        column_types = {"Status": "combo"}
        combo_options = {"Status": ["Active", "Inactive", "Pending"]}

        editor = createTableEditor(
            headers=headers, data=data, column_types=column_types, combo_options=combo_options
        )

        # Check that combo type was set
        assert editor.handler.model.cellTypes[1] == "combo"

    def test_add_row(self, qt_app):
        """Test adding rows to table"""
        headers = ["Name", "Value"]
        data = [{"Name": "Item 1", "Value": 100}]

        editor = createTableEditor(headers=headers, data=data)
        initial_count = editor.handler.rowCount

        # Add row
        editor.handler.addRow({"Name": "Item 2", "Value": 200})

        assert editor.handler.rowCount == initial_count + 1

    def test_delete_row(self, qt_app):
        """Test deleting rows from table"""
        headers = ["Name", "Value"]
        data = [
            {"Name": "Item 1", "Value": 100},
            {"Name": "Item 2", "Value": 200},
        ]

        editor = createTableEditor(headers=headers, data=data)
        initial_count = editor.handler.rowCount

        # Delete first row
        editor.handler.deleteRow(0)

        assert editor.handler.rowCount == initial_count - 1

        # Verify data
        remaining = editor.getDataAsDict()
        assert remaining[0]["Name"] == "Item 2"

    def test_export_as_dict(self, qt_app):
        """Test exporting data as list of dictionaries"""
        headers = ["Name", "Age", "City"]
        data = [
            {"Name": "Alice", "Age": 28, "City": "New York"},
            {"Name": "Bob", "Age": 35, "City": "San Francisco"},
        ]

        editor = createTableEditor(headers=headers, data=data)
        exported = editor.getDataAsDict()

        assert isinstance(exported, list)
        assert len(exported) == 2
        assert all("Name" in row and "Age" in row and "City" in row for row in exported)

    def test_export_as_numpy(self, qt_app):
        """Test exporting data as numpy array"""
        headers = ["X", "Y", "Z"]
        data = np.array(
            [
                [1, 2, 3],
                [4, 5, 6],
            ]
        )

        editor = createTableEditor(headers=headers, data=data)
        exported = editor.getDataAsNumpy()

        assert isinstance(exported, np.ndarray)
        assert exported.shape == (2, 3)

    def test_invalid_headers(self, qt_app):
        """Test that invalid headers raise error"""
        with pytest.raises(ValueError):
            createTableEditor(headers=[], data=None)

        with pytest.raises(ValueError):
            createTableEditor(headers=None, data=None)

    def test_invalid_data_format(self, qt_app):
        """Test that invalid data format raises error"""
        headers = ["Name", "Age"]

        # Invalid: list of strings instead of dicts
        with pytest.raises(ValueError):
            createTableEditor(headers=headers, data=["a", "b"])

        # Invalid: 1D array
        with pytest.raises(ValueError):
            createTableEditor(headers=headers, data=np.array([1, 2, 3]))

    def test_styling_enabled(self, qt_app):
        """Test styling application"""
        headers = ["Data"]
        data = [{"Data": "test"}]

        editor = createTableEditor(headers=headers, data=data, apply_style=True)

        # Check that stylesheet was applied
        assert editor.tableView.styleSheet() != ""

    def test_dark_mode(self, qt_app):
        """Test dark theme"""
        headers = ["Data"]
        data = [{"Data": "test"}]

        editor = createTableEditor(headers=headers, data=data, apply_style=True, dark_mode=True)

        # Check that dark stylesheet was applied
        assert (
            "dark" in editor.tableView.styleSheet().lower()
            or "#0d1117" in editor.tableView.styleSheet()
        )

    def test_toolbar_visibility(self, qt_app):
        """Test toolbar visibility option"""
        headers = ["Data"]
        data = [{"Data": "test"}]

        # With toolbar
        editor_with = createTableEditor(headers=headers, data=data, enable_toolbar=True)
        assert editor_with.addRowBtn.isVisible()

        # Without toolbar
        editor_without = createTableEditor(headers=headers, data=data, enable_toolbar=False)
        assert not editor_without.addRowBtn.isVisible()

    def test_mixed_data_types(self, qt_app):
        """Test table with mixed data types"""
        headers = ["Name", "Age", "Active", "Score", "Status"]
        data = [
            {"Name": "Alice", "Age": 28, "Active": True, "Score": 95.5, "Status": "Excellent"},
            {"Name": "Bob", "Age": 35, "Active": False, "Score": 87.3, "Status": "Good"},
        ]

        column_types = {"Active": "checkbox", "Status": "combo"}
        combo_options = {"Status": ["Excellent", "Good", "Fair", "Poor"]}

        editor = createTableEditor(
            headers=headers, data=data, column_types=column_types, combo_options=combo_options
        )

        assert editor.handler.rowCount == 2
        assert editor.handler.columnCount == 5

        # Verify mixed types work
        exported = editor.getDataAsDict()
        assert isinstance(exported[0]["Age"], int)
        assert isinstance(exported[0]["Score"], float)
        assert isinstance(exported[0]["Active"], bool)


class TestTableEditorWidget:
    """Test TableEditorWidget class"""

    def test_widget_creation(self, qt_app):
        """Test creating widget without handler"""
        widget = TableEditorWidget()
        assert widget is not None
        assert widget.handler is None

    def test_get_data_empty(self, qt_app):
        """Test getting data from empty widget"""
        widget = TableEditorWidget()
        data = widget.getDataAsDict()
        assert data == []

    def test_status_update(self, qt_app):
        """Test status label update"""
        widget = TableEditorWidget()
        widget._updateStatus("Test message")
        assert widget.statusLabel.text() == "Test message"


def run_tests():
    """Run all tests"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()
