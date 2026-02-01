"""Test checkbox labels feature in TableViewHandler."""

import sys
import unittest
from PySide6.QtWidgets import QApplication, QTableView
from PySide6.QtCore import Qt

from nays.ui.handler.table_view_handler import TableViewHandler


class TestCheckboxLabels(unittest.TestCase):
    """Test checkbox labels display feature."""

    @classmethod
    def setUpClass(cls):
        """Create QApplication for all tests."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Set up test fixtures."""
        self.table = QTableView()
        self.handler = TableViewHandler(self.table, ['Name', 'Value', 'Description'])

    def test_checkbox_labels_from_yaml_config(self):
        """Test that checkbox labels are correctly loaded from YAML config."""
        config = [
            {
                'name': 'Enable Feature',
                'type': 'checkbox',
                'defaultValueIndex': True,
                'checkedLabel': 'Set as 1',
                'uncheckedLabel': 'Set as 0',
                'description': 'Enable or disable feature'
            },
            {
                'name': 'Use Cache',
                'type': 'checkbox',
                'defaultValueIndex': False,
                'checkedLabel': 'Enabled',
                'uncheckedLabel': 'Disabled',
                'description': 'Toggle caching'
            }
        ]
        
        self.handler.loadFromYamlConfig(config)
        
        # Row 0 - checked with labels
        value0 = self.handler.model.data(self.handler.model.index(0, 1), Qt.DisplayRole)
        self.assertEqual(value0, 'Set as 1')
        
        # Row 1 - unchecked with labels
        value1 = self.handler.model.data(self.handler.model.index(1, 1), Qt.DisplayRole)
        self.assertEqual(value1, 'Disabled')

    def test_checkbox_labels_toggle(self):
        """Test that labels change when checkbox is toggled."""
        config = [
            {
                'name': 'Toggle Test',
                'type': 'checkbox',
                'defaultValueIndex': True,
                'checkedLabel': 'ON',
                'uncheckedLabel': 'OFF',
                'description': 'Test toggle'
            }
        ]
        
        self.handler.loadFromYamlConfig(config)
        
        # Initially checked
        value = self.handler.model.data(self.handler.model.index(0, 1), Qt.DisplayRole)
        self.assertEqual(value, 'ON')
        
        # Toggle to unchecked
        self.handler.model.setData(self.handler.model.index(0, 1), Qt.Unchecked, Qt.CheckStateRole)
        value = self.handler.model.data(self.handler.model.index(0, 1), Qt.DisplayRole)
        self.assertEqual(value, 'OFF')
        
        # Toggle back to checked
        self.handler.model.setData(self.handler.model.index(0, 1), Qt.Checked, Qt.CheckStateRole)
        value = self.handler.model.data(self.handler.model.index(0, 1), Qt.DisplayRole)
        self.assertEqual(value, 'ON')

    def test_checkbox_without_labels(self):
        """Test that checkbox without labels returns empty string."""
        config = [
            {
                'name': 'No Labels',
                'type': 'checkbox',
                'defaultValueIndex': True,
                'description': 'Checkbox without labels'
            }
        ]
        
        self.handler.loadFromYamlConfig(config)
        
        value = self.handler.model.data(self.handler.model.index(0, 1), Qt.DisplayRole)
        self.assertEqual(value, '')

    def test_checkbox_labels_via_setCellType(self):
        """Test setting checkbox labels directly via setCellType."""
        self.handler.addRow({'Name': 'Direct Test', 'Value': True, 'Description': 'Test'})
        self.handler.enableMultiTypeCells()
        self.handler.setCellType(0, 1, 'checkbox', checkboxLabels=('Active', 'Inactive'))
        
        # Checked state
        self.handler.model.setData(self.handler.model.index(0, 1), Qt.Checked, Qt.CheckStateRole)
        value = self.handler.model.data(self.handler.model.index(0, 1), Qt.DisplayRole)
        self.assertEqual(value, 'Active')
        
        # Unchecked state
        self.handler.model.setData(self.handler.model.index(0, 1), Qt.Unchecked, Qt.CheckStateRole)
        value = self.handler.model.data(self.handler.model.index(0, 1), Qt.DisplayRole)
        self.assertEqual(value, 'Inactive')


if __name__ == '__main__':
    unittest.main()
