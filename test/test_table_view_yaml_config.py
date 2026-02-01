"""
Test TableViewHandler with YAML config loading.

This demonstrates per-cell type support where different rows in the same column
can have different cell types (editable text vs combobox).
"""

import sys
import os
import unittest

import yaml
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableView, QPushButton, QLabel
from PySide6.QtCore import Qt

from nays.ui.handler.table_view_handler import TableViewHandler, MultiTypeCellDelegate


# ---------------------------------
# Sample YAML Config (same as config.yml)
# ---------------------------------

SAMPLE_CONFIG = """
hydrodynamics:
  generalConfig:
    - name: USERID_PATH  
      description: Path to the user ID file like USERID.WAM
      type: 'editable'
      defaultValueIndex: 'C:\\\\'
      items: []

    - name: IDIAG
      description: Characteristic length for analytical integration
      type: 'combobox'
      defaultValueIndex: 0
      items: [
        {0: "Square root of panel's area"},
        {1: "Panel's maximum diagonal"},
      ]

    - name: IFORCE
      description: Parameter specifying FORCE subprogram is executed
      type: 'combobox'
      defaultValueIndex: 1
      items: [
        {0: "Do not executed FORCE"},
        {1: "Do executed FORCE"},
      ]

    - name: IPOTEN
      description: Parameter specifying POTEN subprogram is executed
      type: 'combobox'
      defaultValueIndex: 1
      items: [
        {0: "Do not executed POTEN"},
        {1: "Do executed POTEN"},
      ]

    - name: MAXITT  
      description: Maximum number of itteration
      type: 'editable'
      defaultValueIndex: 35
      items: []

    - name: MAXSCR  
      description: RAM Usage in Program in KB
      type: 'editable'
      defaultValueIndex: 1024000
      items: []
"""


class TestYamlConfigLoading(unittest.TestCase):
    """Unit tests for YAML config loading functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Ensure QApplication exists."""
        cls.app = QApplication.instance() or QApplication(sys.argv)
    
    def testLoadFromYamlConfig(self):
        """Test loading table data from YAML config format."""
        # Parse YAML
        config = yaml.safe_load(SAMPLE_CONFIG)
        generalConfig = config['hydrodynamics']['generalConfig']
        
        # Create table handler
        tableView = QTableView()
        headers = ["Parameter", "Value", "Description"]
        handler = TableViewHandler(tableView, headers)
        
        # Setup columns
        handler.setupColumns([
            ("name", "text"),
            ("value", "text"),  # Will be overridden per-cell
            ("description", "text"),
        ])
        
        # Load from YAML config
        handler.loadFromYamlConfig(generalConfig, valueColumn=1)
        
        # Verify row count
        self.assertEqual(handler.model.rowCount(), 6, "Should have 6 rows")
        
        # Verify data loaded correctly
        data = handler.getData()
        
        # First row: USERID_PATH (editable)
        self.assertEqual(data[0]["name"], "USERID_PATH")
        self.assertEqual(data[0]["value"], "C:\\\\")
        
        # Second row: IDIAG (combobox)
        self.assertEqual(data[1]["name"], "IDIAG")
        self.assertEqual(data[1]["value"], "Square root of panel's area")
        
        # Third row: IFORCE (combobox with defaultValueIndex=1)
        self.assertEqual(data[2]["name"], "IFORCE")
        self.assertEqual(data[2]["value"], "Do executed FORCE")
        
        print("✅ loadFromYamlConfig test passed!")
    
    def testPerCellTypes(self):
        """Test that per-cell types are correctly set."""
        # Parse YAML
        config = yaml.safe_load(SAMPLE_CONFIG)
        generalConfig = config['hydrodynamics']['generalConfig']
        
        # Create table handler
        tableView = QTableView()
        headers = ["Parameter", "Value", "Description"]
        handler = TableViewHandler(tableView, headers)
        
        handler.setupColumns([
            ("name", "text"),
            ("value", "text"),
            ("description", "text"),
        ])
        
        handler.loadFromYamlConfig(generalConfig, valueColumn=1)
        
        # Verify cell types
        # Row 0 (USERID_PATH): should be text
        self.assertEqual(handler.model.getCellType(0, 1), "text")
        
        # Row 1 (IDIAG): should be combobox
        self.assertEqual(handler.model.getCellType(1, 1), "combobox")
        
        # Row 2 (IFORCE): should be combobox
        self.assertEqual(handler.model.getCellType(2, 1), "combobox")
        
        # Row 4 (MAXITT): should be text
        self.assertEqual(handler.model.getCellType(4, 1), "text")
        
        print("✅ Per-cell types test passed!")
    
    def testComboItemsStoredCorrectly(self):
        """Test that combo items are correctly stored for each cell."""
        config = yaml.safe_load(SAMPLE_CONFIG)
        generalConfig = config['hydrodynamics']['generalConfig']
        
        tableView = QTableView()
        headers = ["Parameter", "Value", "Description"]
        handler = TableViewHandler(tableView, headers)
        
        handler.setupColumns([
            ("name", "text"),
            ("value", "text"),
            ("description", "text"),
        ])
        
        handler.loadFromYamlConfig(generalConfig, valueColumn=1)
        
        # Check combo items for IDIAG (row 1)
        comboItems = handler.model.cellComboItems.get((1, 1), [])
        self.assertEqual(len(comboItems), 2)
        self.assertIn("Square root of panel's area", comboItems)
        self.assertIn("Panel's maximum diagonal", comboItems)
        
        # Check combo items for IFORCE (row 2)
        comboItems = handler.model.cellComboItems.get((2, 1), [])
        self.assertEqual(len(comboItems), 2)
        self.assertIn("Do not executed FORCE", comboItems)
        self.assertIn("Do executed FORCE", comboItems)
        
        # Check editable row has no combo items
        comboItems = handler.model.cellComboItems.get((0, 1), [])
        self.assertEqual(len(comboItems), 0)
        
        print("✅ Combo items storage test passed!")
    
    def testGetConfigValues(self):
        """Test extracting config values as dictionary."""
        config = yaml.safe_load(SAMPLE_CONFIG)
        generalConfig = config['hydrodynamics']['generalConfig']
        
        tableView = QTableView()
        headers = ["Parameter", "Value", "Description"]
        handler = TableViewHandler(tableView, headers)
        
        handler.setupColumns([
            ("name", "text"),
            ("value", "text"),
            ("description", "text"),
        ])
        
        handler.loadFromYamlConfig(generalConfig, valueColumn=1)
        
        # Get config values
        values = handler.getConfigValues()
        
        self.assertEqual(values["USERID_PATH"], "C:\\\\")
        self.assertEqual(values["IDIAG"], "Square root of panel's area")
        self.assertEqual(values["IFORCE"], "Do executed FORCE")
        self.assertEqual(values["MAXITT"], 35)
        self.assertEqual(values["MAXSCR"], 1024000)
        
        print("✅ getConfigValues test passed!")
    
    def testLoadRealYamlFile(self):
        """Test loading from actual config.yml file."""
        # Get the path to config.yml
        configPath = os.path.join(
            os.path.dirname(__file__), 
            "..", "nays", "ui", "handler", "config.yml"
        )
        
        if not os.path.exists(configPath):
            self.skipTest("config.yml not found")
        
        # Load YAML file
        with open(configPath, 'r') as f:
            config = yaml.safe_load(f)
        
        generalConfig = config['hydrodynamics']['generalConfig']
        
        # Create table handler
        tableView = QTableView()
        headers = ["Parameter", "Value", "Description"]
        handler = TableViewHandler(tableView, headers)
        
        handler.setupColumns([
            ("name", "text"),
            ("value", "text"),
            ("description", "text"),
        ])
        
        handler.loadFromYamlConfig(generalConfig, valueColumn=1)
        
        # Verify all rows loaded
        self.assertGreater(handler.model.rowCount(), 0, "Should have rows")
        
        # Check for specific items
        values = handler.getConfigValues()
        self.assertIn("IDIAG", values)
        self.assertIn("IFORCE", values)
        
        print("✅ Real YAML file loading test passed!")
    
    def testMultiTypeCellDelegate(self):
        """Test the MultiTypeCellDelegate is correctly applied."""
        tableView = QTableView()
        headers = ["Parameter", "Value"]
        handler = TableViewHandler(tableView, headers)
        
        handler.setupColumns([
            ("name", "text"),
            ("value", "text"),
        ])
        
        # Enable multi-type cells
        handler.enableMultiTypeCells()
        
        # Verify delegate is set
        self.assertIsNotNone(handler._multiTypeDelegate)
        self.assertIsInstance(handler._multiTypeDelegate, MultiTypeCellDelegate)
        
        print("✅ MultiTypeCellDelegate test passed!")
    
    def testMixedCellTypesInSameColumn(self):
        """Test setting different cell types manually in the same column."""
        tableView = QTableView()
        headers = ["Name", "Value"]
        handler = TableViewHandler(tableView, headers)
        
        handler.setupColumns([
            ("name", "text"),
            ("value", "text"),
        ])
        
        # Enable per-cell types
        handler.enableMultiTypeCells()
        
        # Add rows
        handler.addRow({"name": "Text Field", "value": "Hello"})
        handler.addRow({"name": "Combo Field", "value": "Option A"})
        handler.addRow({"name": "Another Text", "value": "World"})
        
        # Set different types for cells in column 1
        handler.setCellType(0, 1, "text")
        handler.setCellType(1, 1, "combobox", ["Option A", "Option B", "Option C"])
        handler.setCellType(2, 1, "text")
        
        # Verify cell types
        self.assertEqual(handler.model.getCellType(0, 1), "text")
        self.assertEqual(handler.model.getCellType(1, 1), "combobox")
        self.assertEqual(handler.model.getCellType(2, 1), "text")
        
        # Verify combo items
        self.assertEqual(
            handler.model.cellComboItems.get((1, 1)), 
            ["Option A", "Option B", "Option C"]
        )
        
        print("✅ Mixed cell types test passed!")
    
    def testComboDisplayModeValue(self):
        """Test comboDisplayMode='value' shows text values."""
        config = yaml.safe_load(SAMPLE_CONFIG)
        generalConfig = config['hydrodynamics']['generalConfig']
        
        tableView = QTableView()
        headers = ["Parameter", "Value", "Description"]
        handler = TableViewHandler(tableView, headers)
        
        handler.setupColumns([
            ("name", "text"),
            ("value", "text"),
            ("description", "text"),
        ])
        
        # Load with value mode (default)
        handler.loadFromYamlConfig(generalConfig, valueColumn=1, comboDisplayMode="value")
        
        # Check displayed value shows the text
        data = handler.getData()
        self.assertEqual(data[1]["value"], "Square root of panel's area")
        self.assertEqual(data[2]["value"], "Do executed FORCE")
        
        # Check combo items show values
        comboItems = handler.model.cellComboItems.get((1, 1), [])
        self.assertIn("Square root of panel's area", comboItems)
        self.assertIn("Panel's maximum diagonal", comboItems)
        
        print("✅ comboDisplayMode='value' test passed!")
    
    def testComboDisplayModeKey(self):
        """Test comboDisplayMode='key' shows index keys."""
        config = yaml.safe_load(SAMPLE_CONFIG)
        generalConfig = config['hydrodynamics']['generalConfig']
        
        tableView = QTableView()
        headers = ["Parameter", "Value", "Description"]
        handler = TableViewHandler(tableView, headers)
        
        handler.setupColumns([
            ("name", "text"),
            ("value", "text"),
            ("description", "text"),
        ])
        
        # Load with key mode
        handler.loadFromYamlConfig(generalConfig, valueColumn=1, comboDisplayMode="key")
        
        # Check displayed value shows the key/index
        data = handler.getData()
        self.assertEqual(data[1]["value"], "0")  # IDIAG defaultValueIndex=0
        self.assertEqual(data[2]["value"], "1")  # IFORCE defaultValueIndex=1
        
        # Check combo items show keys
        comboItems = handler.model.cellComboItems.get((1, 1), [])
        self.assertIn("0", comboItems)
        self.assertIn("1", comboItems)
        
        print("✅ comboDisplayMode='key' test passed!")
    
    def testComboDisplayModeBoth(self):
        """Test comboDisplayMode='both' shows 'key: value' format."""
        config = yaml.safe_load(SAMPLE_CONFIG)
        generalConfig = config['hydrodynamics']['generalConfig']
        
        tableView = QTableView()
        headers = ["Parameter", "Value", "Description"]
        handler = TableViewHandler(tableView, headers)
        
        handler.setupColumns([
            ("name", "text"),
            ("value", "text"),
            ("description", "text"),
        ])
        
        # Load with both mode
        handler.loadFromYamlConfig(generalConfig, valueColumn=1, comboDisplayMode="both")
        
        # Check displayed value shows "key: value" format
        data = handler.getData()
        self.assertEqual(data[1]["value"], "0: Square root of panel's area")
        self.assertEqual(data[2]["value"], "1: Do executed FORCE")
        
        # Check combo items show "key: value" format
        comboItems = handler.model.cellComboItems.get((1, 1), [])
        self.assertIn("0: Square root of panel's area", comboItems)
        self.assertIn("1: Panel's maximum diagonal", comboItems)
        
        print("✅ comboDisplayMode='both' test passed!")


# ---------------------------------
# Interactive Demo Window
# ---------------------------------

class YamlConfigDemoWindow(QWidget):
    """Demo window showing YAML config loaded into table."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YAML Config TableView Demo")
        self.resize(900, 600)
        
        self.setupUi()
        self.loadConfig()
    
    def setupUi(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        
        # Info label
        infoLabel = QLabel(
            "This table demonstrates per-cell type support:\n"
            "- Some rows have editable text cells\n"
            "- Some rows have combobox cells (click to see dropdown)"
        )
        layout.addWidget(infoLabel)
        
        # Table view
        self.tableView = QTableView()
        layout.addWidget(self.tableView)
        
        # Status label
        self.statusLabel = QLabel("Click on cells to edit")
        layout.addWidget(self.statusLabel)
        
        # Print button
        self.printBtn = QPushButton("Print Config Values")
        self.printBtn.clicked.connect(self.onPrintValues)
        layout.addWidget(self.printBtn)
    
    def loadConfig(self):
        """Load config from YAML."""
        # Parse embedded YAML
        config = yaml.safe_load(SAMPLE_CONFIG)
        generalConfig = config['hydrodynamics']['generalConfig']
        
        # Setup handler
        headers = ["Parameter", "Value", "Description"]
        self.handler = TableViewHandler(self.tableView, headers)
        
        self.handler.setupColumns([
            ("name", "text"),
            ("value", "text"),
            ("description", "text"),
        ])
        
        # Load from YAML config
        self.handler.loadFromYamlConfig(generalConfig, valueColumn=1)
        
        # Connect cell changed signal
        self.handler.onCellChanged(self.onCellChanged)
    
    def onCellChanged(self, row: int, col: int, value):
        """Handle cell changes."""
        cellType = self.handler.model.getCellType(row, col)
        self.statusLabel.setText(f"Cell ({row}, {col}) - Type: {cellType}, Value: {value}")
    
    def onPrintValues(self):
        """Print current config values."""
        values = self.handler.getConfigValues()
        print("\n=== Config Values ===")
        for name, value in values.items():
            print(f"  {name}: {value}")
        print("=====================\n")


# ---------------------------------
# Run
# ---------------------------------

def runAllTests():
    """Run all unit tests."""
    print("\n" + "=" * 60)
    print("Running TableViewHandler YAML Config Tests")
    print("=" * 60 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestYamlConfigLoading)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run tests first
    success = runAllTests()
    
    if success and "--demo" in sys.argv:
        # Show interactive demo
        print("\nStarting interactive demo...")
        app = QApplication.instance() or QApplication(sys.argv)
        window = YamlConfigDemoWindow()
        window.show()
        sys.exit(app.exec())
    elif not success:
        sys.exit(1)
