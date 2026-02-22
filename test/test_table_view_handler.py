"""
Test and Usage Example for TableViewHandler

This demonstrates how to use the TableViewHandler with different cell types:
- Text cells (default)
- ComboBox cells
- CheckBox cells
"""

import sys

import numpy as np
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from nays.ui.handler.table_view_handler import TableViewHandler


class TestTableViewWindow(QWidget):
    """Test window demonstrating TableViewHandler usage."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TableViewHandler Test")
        self.resize(700, 500)

        self.setupUi()
        self.setupHandler()
        self.loadSampleData()

    def setupUi(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)

        # Table View
        self.tableView = QTableView()
        layout.addWidget(self.tableView)

        # Status label
        self.statusLabel = QLabel("Status: Ready")
        layout.addWidget(self.statusLabel)

        # Buttons row
        btnLayout = QHBoxLayout()

        self.addBtn = QPushButton("Add Row")
        self.deleteBtn = QPushButton("Delete Row")
        self.clearBtn = QPushButton("Clear All")
        self.printDataBtn = QPushButton("Print Data")
        self.numpyBtn = QPushButton("To NumPy")

        btnLayout.addWidget(self.addBtn)
        btnLayout.addWidget(self.deleteBtn)
        btnLayout.addWidget(self.clearBtn)
        btnLayout.addWidget(self.printDataBtn)
        btnLayout.addWidget(self.numpyBtn)

        layout.addLayout(btnLayout)

    def setupHandler(self):
        """Setup the TableViewHandler with columns."""
        # Define headers
        headers = ["Name", "Type", "Enabled", "Value"]

        # Create handler
        self.handler = TableViewHandler(self.tableView, headers)

        # Setup column types: (key, type)
        self.handler.setupColumns(
            [
                ("name", "text"),
                ("type", "combo"),
                ("enabled", "checkbox"),
                ("value", "text"),
            ]
        )

        # Set combo items for "Type" column (index 1)
        self.handler.setColumnComboItems(1, ["AC", "DC", "Servo", "Stepper"])

        # Connect buttons
        self.addBtn.clicked.connect(self.onAddRow)
        self.deleteBtn.clicked.connect(self.onDeleteRow)
        self.clearBtn.clicked.connect(self.handler.clearAll)
        self.printDataBtn.clicked.connect(self.onPrintData)
        self.numpyBtn.clicked.connect(self.onToNumpy)

        # Connect handler signals
        self.handler.onRowCountChanged(self.onRowCountChanged)
        self.handler.onDataChanged(self.onDataChanged)
        self.handler.onCellChanged(self.onCellChanged)

    def loadSampleData(self):
        """Load sample data into the table."""
        sampleData = [
            {"name": "Motor 1", "type": "AC", "enabled": True, "value": "100"},
            {"name": "Motor 2", "type": "DC", "enabled": False, "value": "200"},
            {"name": "Motor 3", "type": "Servo", "enabled": True, "value": "150"},
            {"name": "Motor 4", "type": "Stepper", "enabled": True, "value": "75"},
        ]
        self.handler.loadData(sampleData)

    # ===== Button Handlers =====

    def onAddRow(self):
        """Add a new row with default values."""
        self.handler.addRow(
            {
                "name": "New Motor",
                "type": "AC",
                "enabled": False,
                "value": "0",
            }
        )

    def onDeleteRow(self):
        """Delete currently selected row."""
        row = self.handler.getSelectedRow()
        if row >= 0:
            self.handler.deleteRow(row)
        else:
            self.statusLabel.setText("Status: No row selected")

    def onPrintData(self):
        """Print all table data to console."""
        data = self.handler.getData()
        print("\n=== Table Data ===")
        for i, row in enumerate(data):
            print(f"Row {i}: {row}")
        print("==================\n")

    def onToNumpy(self):
        """Demonstrate NumPy conversion."""
        # Get single column as numpy
        valueColumn = self.handler.getColumnAsNumpy(3, dtype=str)
        print(f"\nValue column as numpy: {valueColumn}")

        # Get all data (note: mixed types may need object dtype)
        allData = self.handler.getAllAsNumpy(dtype=object)
        print(f"All data shape: {allData.shape}")
        print(f"All data:\n{allData}\n")

    # ===== Signal Handlers =====

    def onRowCountChanged(self, count: int):
        """Handle row count changes."""
        self.statusLabel.setText(f"Status: {count} rows")

    def onDataChanged(self, data: list):
        """Handle data changes."""
        print(f"Data changed: {len(data)} rows")

    def onCellChanged(self, row: int, col: int, value):
        """Handle cell clicks."""
        print(f"Cell clicked: ({row}, {col}) = {value}")


# ---------------------------------
# Unit Tests
# ---------------------------------


def testBasicOperations():
    """Test basic handler operations without GUI."""
    app = QApplication.instance() or QApplication(sys.argv)

    tableView = QTableView()
    handler = TableViewHandler(tableView, ["A", "B", "C"])
    handler.setupColumns([("a", "text"), ("b", "text"), ("c", "text")])

    # Test addRow
    handler.addRow({"a": "1", "b": "2", "c": "3"})
    handler.addRow({"a": "4", "b": "5", "c": "6"})
    assert handler.model.rowCount() == 2, "Row count should be 2"

    # Test getData
    data = handler.getData()
    assert len(data) == 2, "Should have 2 rows"
    assert data[0]["a"] == "1", "First cell should be '1'"

    # Test getCellValue
    assert handler.getCellValue(0, 0) == "1", "Cell (0,0) should be '1'"
    assert handler.getCellValue(1, 2) == "6", "Cell (1,2) should be '6'"

    # Test setCellValue
    handler.setCellValue(0, 0, "X")
    assert handler.getCellValue(0, 0) == "X", "Cell (0,0) should be 'X'"

    # Test deleteRow
    handler.deleteRow(0)
    assert handler.model.rowCount() == 1, "Row count should be 1"

    # Test clearAll
    handler.clearAll()
    assert handler.model.rowCount() == 0, "Row count should be 0"

    print("✅ All basic operation tests passed!")


def testNumpyOperations():
    """Test NumPy helper operations."""
    app = QApplication.instance() or QApplication(sys.argv)

    tableView = QTableView()
    handler = TableViewHandler(tableView, ["X", "Y", "Z"])
    handler.setupColumns([("x", "text"), ("y", "text"), ("z", "text")])

    # Load data
    handler.loadData(
        [
            {"x": 1.0, "y": 2.0, "z": 3.0},
            {"x": 4.0, "y": 5.0, "z": 6.0},
            {"x": 7.0, "y": 8.0, "z": 9.0},
        ]
    )

    # Test getColumnAsNumpy
    col = handler.getColumnAsNumpy(0, dtype=float)
    expected = np.array([1.0, 4.0, 7.0])
    assert np.array_equal(col, expected), f"Column should be {expected}, got {col}"

    # Test getRowAsNumpy
    row = handler.getRowAsNumpy(1, dtype=float)
    expected = np.array([4.0, 5.0, 6.0])
    assert np.array_equal(row, expected), f"Row should be {expected}, got {row}"

    # Test getAllAsNumpy
    allData = handler.getAllAsNumpy(dtype=float)
    assert allData.shape == (3, 3), f"Shape should be (3, 3), got {allData.shape}"

    # Test loadFromNumpy
    newData = np.array([[10, 20, 30], [40, 50, 60]])
    handler.loadFromNumpy(newData, ["x", "y", "z"])
    assert handler.model.rowCount() == 2, "Should have 2 rows after loading"
    assert handler.getCellValue(0, 0) == 10, "First cell should be 10"

    print("✅ All NumPy operation tests passed!")


def testColumnTypes():
    """Test different column types."""
    app = QApplication.instance() or QApplication(sys.argv)

    tableView = QTableView()
    handler = TableViewHandler(tableView, ["Name", "Type", "Active"])
    handler.setupColumns(
        [
            ("name", "text"),
            ("type", "combo"),
            ("active", "checkbox"),
        ]
    )

    # Set combo items
    handler.setColumnComboItems(1, ["Option A", "Option B", "Option C"])

    # Verify column types
    assert handler.model.cellTypes[0] == "text"
    assert handler.model.cellTypes[1] == "combo"
    assert handler.model.cellTypes[2] == "checkbox"

    # Load data with checkbox boolean
    handler.loadData(
        [
            {"name": "Item 1", "type": "Option A", "active": True},
            {"name": "Item 2", "type": "Option B", "active": False},
        ]
    )

    data = handler.getData()
    assert data[0]["active"] == True, "First checkbox should be True"
    assert data[1]["active"] == False, "Second checkbox should be False"

    print("✅ All column type tests passed!")


def runAllTests():
    """Run all unit tests."""
    print("\n" + "=" * 50)
    print("Running TableViewHandler Tests")
    print("=" * 50 + "\n")

    testBasicOperations()
    testNumpyOperations()
    testColumnTypes()

    print("\n" + "=" * 50)
    print("All tests completed successfully! ✅")
    print("=" * 50 + "\n")


# ---------------------------------
# Run
# ---------------------------------

if __name__ == "__main__":
    # Run tests first
    runAllTests()

    # Then show interactive demo
    print("Starting interactive demo...")
    app = QApplication.instance() or QApplication(sys.argv)
    window = TestTableViewWindow()
    window.show()
    sys.exit(app.exec())
