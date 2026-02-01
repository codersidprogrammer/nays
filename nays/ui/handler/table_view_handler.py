from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np

from PySide6.QtWidgets import QComboBox, QStyledItemDelegate, QApplication, QTableView, QLineEdit
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QObject, Signal


# ---------------------------------
# Cell Delegates
# ---------------------------------

class ComboBoxDelegate(QStyledItemDelegate):
    """Delegate for ComboBox cells with customizable items."""
    
    def __init__(self, items: List[str] = None, parent=None):
        super().__init__(parent)
        self.items = items or []
    
    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.addItems(self.items)
        return combo
    
    def setEditorData(self, editor: QComboBox, index: QModelIndex):
        value = index.data(Qt.EditRole)
        if value is not None:
            editor.setCurrentText(str(value))
    
    def setModelData(self, editor: QComboBox, model, index: QModelIndex):
        model.setData(index, editor.currentText(), Qt.EditRole)


class CheckBoxDelegate(QStyledItemDelegate):
    """Delegate for CheckBox cells."""
    
    def createEditor(self, parent, option, index):
        return super().createEditor(parent, option, index)
    
    def setEditorData(self, editor, index: QModelIndex):
        pass
    
    def setModelData(self, editor, model, index: QModelIndex):
        pass


class MultiTypeCellDelegate(QStyledItemDelegate):
    """
    Delegate that supports different cell types per cell based on model data.
    Uses Qt.UserRole to retrieve cell type and Qt.UserRole + 1 for combo items.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def createEditor(self, parent, option, index):
        cellType = index.data(Qt.UserRole)
        
        if cellType == "combobox":
            combo = QComboBox(parent)
            items = index.data(Qt.UserRole + 1) or []
            combo.addItems(items)
            return combo
        elif cellType == "checkbox":
            return None  # Checkbox handled via flags
        else:
            # Default text editor
            return QLineEdit(parent)
    
    def setEditorData(self, editor, index: QModelIndex):
        cellType = index.data(Qt.UserRole)
        value = index.data(Qt.EditRole)
        
        if cellType == "combobox" and isinstance(editor, QComboBox):
            if value is not None:
                editor.setCurrentText(str(value))
        elif isinstance(editor, QLineEdit):
            editor.setText(str(value) if value is not None else "")
    
    def setModelData(self, editor, model, index: QModelIndex):
        cellType = index.data(Qt.UserRole)
        
        if cellType == "combobox" and isinstance(editor, QComboBox):
            model.setData(index, editor.currentText(), Qt.EditRole)
        elif isinstance(editor, QLineEdit):
            model.setData(index, editor.text(), Qt.EditRole)


# ---------------------------------
# Table Model
# ---------------------------------

class TableViewModel(QAbstractTableModel):
    """Generic table model with support for multiple cell types."""
    
    dataModified = Signal()
    
    def __init__(self, headers: List[str] = None, parent=None):
        super().__init__(parent)
        self.headers = headers or []
        self.rows: List[Dict[str, Any]] = []
        self.cellTypes: Dict[int, str] = {}  # column -> type mapping (for column-based)
        self.columnKeys: List[str] = []  # Maps columns to dict keys
        
        # Per-cell type configuration: (row, col) -> type
        self.cellTypeOverrides: Dict[Tuple[int, int], str] = {}
        # Per-cell combo items: (row, col) -> list of display items
        self.cellComboItems: Dict[Tuple[int, int], List[str]] = {}
        
        # Combo key/value mappings for each cell
        # (row, col) -> {key: display_text}
        self.cellKeyToDisplay: Dict[Tuple[int, int], Dict[Any, str]] = {}
        # (row, col) -> {display_text: key}
        self.cellDisplayToKey: Dict[Tuple[int, int], Dict[str, Any]] = {}
        # Store actual key values: (row, col) -> key
        self.cellKeyValues: Dict[Tuple[int, int], Any] = {}
    
    # ===== Basics =====
    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.rows)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.headers)
    
    def getCellType(self, row: int, col: int) -> str:
        """Get cell type for a specific cell, checking overrides first."""
        # Check per-cell override first
        if (row, col) in self.cellTypeOverrides:
            return self.cellTypeOverrides[(row, col)]
        # Fall back to column-based type
        return self.cellTypes.get(col, "text")
    
    def setCellType(self, row: int, col: int, cellType: str, comboItems: List[str] = None,
                    keyToDisplay: Dict[Any, str] = None, displayToKey: Dict[str, Any] = None):
        """Set cell type for a specific cell."""
        self.cellTypeOverrides[(row, col)] = cellType
        if comboItems:
            self.cellComboItems[(row, col)] = comboItems
        if keyToDisplay:
            self.cellKeyToDisplay[(row, col)] = keyToDisplay
        if displayToKey:
            self.cellDisplayToKey[(row, col)] = displayToKey
    
    def setKeyValue(self, row: int, col: int, keyValue: Any):
        """Set the key value for a combobox cell."""
        self.cellKeyValues[(row, col)] = keyValue
    
    def getKeyValue(self, row: int, col: int) -> Any:
        """Get the key value for a combobox cell."""
        return self.cellKeyValues.get((row, col))
    
    # ===== Data Display & Editing =====
    def data(self, index: QModelIndex, role=Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        
        row = index.row()
        col = index.column()
        
        rowData = self.rows[row]
        key = self.columnKeys[col] if col < len(self.columnKeys) else None
        value = rowData.get(key) if key else None
        
        cellType = self.getCellType(row, col)
        
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if cellType == "checkbox":
                return ""
            return value
        
        if role == Qt.CheckStateRole and cellType == "checkbox":
            return Qt.Checked if value else Qt.Unchecked
        
        # Return cell type for delegate
        if role == Qt.UserRole:
            return cellType
        
        # Return combo items for delegate
        if role == Qt.UserRole + 1:
            return self.cellComboItems.get((row, col), [])
        
        return None
    
    def setData(self, index: QModelIndex, value: Any, role=Qt.EditRole) -> bool:
        if not index.isValid():
            return False
        
        row = index.row()
        col = index.column()
        key = self.columnKeys[col] if col < len(self.columnKeys) else None
        if not key:
            return False
        
        cellType = self.getCellType(row, col)
        
        if cellType == "checkbox" and role == Qt.CheckStateRole:
            self.rows[row][key] = value == Qt.Checked
        elif role == Qt.EditRole:
            self.rows[row][key] = value
            # Update key value if this is a combobox cell
            if cellType == "combobox" and (row, col) in self.cellDisplayToKey:
                displayToKey = self.cellDisplayToKey[(row, col)]
                if value in displayToKey:
                    self.cellKeyValues[(row, col)] = displayToKey[value]
        else:
            return False
        
        self.dataChanged.emit(index, index)
        self.dataModified.emit()
        return True
    
    # ===== Flags =====
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        base = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        row = index.row()
        col = index.column()
        cellType = self.getCellType(row, col)
        
        if cellType == "checkbox":
            return base | Qt.ItemIsUserCheckable
        return base
    
    # ===== Headers =====
    def headerData(self, section: int, orientation, role=Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section < len(self.headers):
                return self.headers[section]
        return None
    
    # ===== Row Operations =====
    def addRow(self, rowData: Dict[str, Any] = None):
        """Add a new row to the table."""
        if rowData is None:
            rowData = {key: "" for key in self.columnKeys}
        
        self.beginInsertRows(QModelIndex(), len(self.rows), len(self.rows))
        self.rows.append(rowData)
        self.endInsertRows()
        self.dataModified.emit()
    
    def deleteRow(self, row: int):
        """Delete a row from the table."""
        if row < 0 or row >= len(self.rows):
            return
        
        self.beginRemoveRows(QModelIndex(), row, row)
        self.rows.pop(row)
        self.endRemoveRows()
        
        # Clean up cell type overrides for deleted row
        keysToRemove = [k for k in self.cellTypeOverrides if k[0] == row]
        for k in keysToRemove:
            del self.cellTypeOverrides[k]
        keysToRemove = [k for k in self.cellComboItems if k[0] == row]
        for k in keysToRemove:
            del self.cellComboItems[k]
        keysToRemove = [k for k in self.cellKeyToDisplay if k[0] == row]
        for k in keysToRemove:
            del self.cellKeyToDisplay[k]
        keysToRemove = [k for k in self.cellDisplayToKey if k[0] == row]
        for k in keysToRemove:
            del self.cellDisplayToKey[k]
        keysToRemove = [k for k in self.cellKeyValues if k[0] == row]
        for k in keysToRemove:
            del self.cellKeyValues[k]
        
        self.dataModified.emit()
    
    def insertRow(self, row: int, rowData: Dict[str, Any] = None):
        """Insert a row at a specific position."""
        if rowData is None:
            rowData = {key: "" for key in self.columnKeys}
        
        self.beginInsertRows(QModelIndex(), row, row)
        self.rows.insert(row, rowData)
        self.endInsertRows()
        self.dataModified.emit()
    
    def clearRows(self):
        """Clear all rows."""
        if len(self.rows) > 0:
            self.beginRemoveRows(QModelIndex(), 0, len(self.rows) - 1)
            self.rows.clear()
            self.cellTypeOverrides.clear()
            self.cellComboItems.clear()
            self.cellKeyToDisplay.clear()
            self.cellDisplayToKey.clear()
            self.cellKeyValues.clear()
            self.endRemoveRows()
            self.dataModified.emit()


# ---------------------------------
# Table View Handler
# ---------------------------------

class TableViewHandler(QObject):
    """Compact handler for QTableView with multi-type cell support."""
    
    rowCountChanged = Signal(int)
    dataChanged = Signal(list)  # emits list of dicts
    cellChanged = Signal(int, int, object)  # row, col, value
    
    def __init__(self, tableView: QTableView, headers: List[str] = None):
        super().__init__()
        self.tableView = tableView
        self.headers = headers or []
        
        # Create and set model
        self.model = TableViewModel(headers=self.headers)
        self.tableView.setModel(self.model)
        
        # Connect signals
        self.model.dataModified.connect(self._onDataModified)
        self.tableView.clicked.connect(self._onCellClicked)
        
        # Store delegates by column
        self.delegates: Dict[int, QStyledItemDelegate] = {}
        
        # Multi-type delegate for per-cell type support
        self._multiTypeDelegate: Optional[MultiTypeCellDelegate] = None
    
    # ===== Column Configuration =====
    
    def setupColumns(self, columns: List[Tuple[str, str]]):
        """
        Setup columns with types.
        
        Args:
            columns: List of (key, type) tuples where type is 'text', 'combo', or 'checkbox'
        """
        self.model.columnKeys = [col[0] for col in columns]
        self.model.cellTypes = {i: col[1] for i, col in enumerate(columns)}
        self.tableView.resizeColumnsToContents()
    
    def setColumnComboItems(self, column: int, items: List[str]):
        """Set combo items for a specific column."""
        delegate = ComboBoxDelegate(items)
        self.delegates[column] = delegate
        self.tableView.setItemDelegateForColumn(column, delegate)
    
    def setColumnType(self, column: int, cellType: str):
        """Set cell type for a column ('text', 'combo', 'checkbox')."""
        if cellType == "combo" and column not in self.delegates:
            delegate = ComboBoxDelegate([])
            self.delegates[column] = delegate
            self.tableView.setItemDelegateForColumn(column, delegate)
        elif cellType == "checkbox":
            delegate = CheckBoxDelegate()
            self.delegates[column] = delegate
            self.tableView.setItemDelegateForColumn(column, delegate)
        
        self.model.cellTypes[column] = cellType
    
    def enableMultiTypeCells(self):
        """Enable per-cell type support using MultiTypeCellDelegate."""
        if self._multiTypeDelegate is None:
            self._multiTypeDelegate = MultiTypeCellDelegate()
        # Apply to all columns
        for col in range(len(self.headers)):
            self.tableView.setItemDelegateForColumn(col, self._multiTypeDelegate)
    
    def setCellType(self, row: int, col: int, cellType: str, comboItems: List[str] = None):
        """Set cell type for a specific cell."""
        self.model.setCellType(row, col, cellType, comboItems)
    
    # ===== YAML Config Loading =====
    
    def loadFromYamlConfig(
        self, 
        config: List[Dict[str, Any]], 
        valueColumn: int = 1,
        comboDisplayMode: str = "value"
    ):
        """
        Load table data from YAML config format.
        
        Each config item should have:
        - name: The row label/key
        - type: 'editable', 'combobox', or 'checkbox'
        - defaultValueIndex: For combobox, this is the INDEX into the items list (0-based).
                            For editable, this is the default value.
        - items: List of dicts for combobox options [{-1: "Option A"}, {0: "Option B"}, {1: "Option C"}]
        - description: Optional description
        
        Args:
            config: List of config dictionaries
            valueColumn: Column index for the value (default 1, assuming column 0 is name)
            comboDisplayMode: How to display combo items:
                - "value": Show the text value (e.g., "Square root of panel's area")
                - "key": Show the key/index (e.g., "0")
                - "both": Show "key: value" format (e.g., "0: Square root of panel's area")
        
        Note:
            defaultValueIndex is the position in the items list (0, 1, 2, ...), not the key.
            For example, if items = [{-1: "A"}, {0: "B"}, {1: "C"}] and defaultValueIndex = 2,
            the selected item is {1: "C"} with key=1.
        """
        self.enableMultiTypeCells()
        self.model.clearRows()
        
        for rowIdx, item in enumerate(config):
            name = item.get("name", "")
            itemType = item.get("type", "editable")
            defaultValueIndex = item.get("defaultValueIndex", "")
            items = item.get("items", [])
            description = item.get("description", "")
            
            # Map YAML type to cell type
            if itemType == "combobox":
                cellType = "combobox"
            elif itemType == "checkbox":
                cellType = "checkbox"
            else:
                cellType = "text"
            
            # Parse combo items from [{key: "text"}, ...] format
            comboItems = []  # Display items for dropdown
            keyToDisplay = {}  # Maps key to display text
            displayToKey = {}  # Maps display text to key
            itemsList = []  # List of (key, value) tuples in order
            
            if items and cellType == "combobox":
                for itemDict in items:
                    for key, val in itemDict.items():
                        keyInt = int(key)
                        itemsList.append((keyInt, val))
                        
                        # Format combo item based on display mode
                        if comboDisplayMode == "key":
                            displayText = str(key)
                        elif comboDisplayMode == "both":
                            displayText = f"{key}: {val}"
                        else:  # "value" (default)
                            displayText = val
                        
                        comboItems.append(displayText)
                        keyToDisplay[keyInt] = displayText
                        displayToKey[displayText] = keyInt
            
            # Determine display value and actual key based on defaultValueIndex
            displayValue = defaultValueIndex
            actualKeyValue = None
            
            if cellType == "combobox" and isinstance(defaultValueIndex, int) and itemsList:
                # defaultValueIndex is the index in the items list
                if 0 <= defaultValueIndex < len(itemsList):
                    actualKeyValue = itemsList[defaultValueIndex][0]  # The key
                    displayValue = keyToDisplay.get(actualKeyValue, str(actualKeyValue))
            
            # Build row data based on column keys
            rowData = {}
            if len(self.model.columnKeys) >= 1:
                rowData[self.model.columnKeys[0]] = name
            if len(self.model.columnKeys) >= 2:
                rowData[self.model.columnKeys[1]] = displayValue
            if len(self.model.columnKeys) >= 3:
                rowData[self.model.columnKeys[2]] = description
            
            # Add the row
            self.model.addRow(rowData)
            
            # Set cell type for the value column with mappings
            self.model.setCellType(
                rowIdx, valueColumn, cellType, comboItems,
                keyToDisplay=keyToDisplay,
                displayToKey=displayToKey
            )
            
            # Store the actual key value
            if actualKeyValue is not None:
                self.model.setKeyValue(rowIdx, valueColumn, actualKeyValue)
        
        self.tableView.resizeColumnsToContents()
        self.rowCountChanged.emit(self.model.rowCount())
    
    def getConfigValues(self, valueColumn: int = 1, returnKeys: bool = True) -> Dict[str, Any]:
        """
        Get values as a dictionary mapping names to values.
        Useful for extracting config values after editing.
        
        Args:
            valueColumn: Column index for values (default 1)
            returnKeys: If True, return the key values for combobox cells.
                       If False, return the display text.
        
        Returns:
            Dict mapping row names (column 0) to values (column 1).
            For combobox cells, returns the key (e.g., -1, 0, 1) if returnKeys=True.
        """
        result = {}
        if len(self.model.columnKeys) < 2:
            return result
        
        nameKey = self.model.columnKeys[0]
        valueKey = self.model.columnKeys[1]
        
        for rowIdx, row in enumerate(self.model.rows):
            name = row.get(nameKey, "")
            
            # Check if this cell has a key value stored
            if returnKeys:
                keyValue = self.model.getKeyValue(rowIdx, valueColumn)
                if keyValue is not None:
                    result[name] = keyValue
                    continue
            
            # Fall back to display value
            value = row.get(valueKey, "")
            result[name] = value
        
        return result
    
    # ===== Data Operations =====
    
    def loadData(self, data: List[Dict[str, Any]]):
        """Load data into the table."""
        self.model.clearRows()
        for rowData in data:
            self.model.addRow(rowData)
    
    def addRow(self, rowData: Dict[str, Any] = None):
        """Add a new row."""
        self.model.addRow(rowData)
        self.rowCountChanged.emit(self.model.rowCount())
    
    def deleteRow(self, row: int):
        """Delete a specific row."""
        self.model.deleteRow(row)
        self.rowCountChanged.emit(self.model.rowCount())
    
    def insertRow(self, row: int, rowData: Dict[str, Any] = None):
        """Insert a row at a specific position."""
        self.model.insertRow(row, rowData)
        self.rowCountChanged.emit(self.model.rowCount())
    
    def clearAll(self):
        """Clear all rows."""
        self.model.clearRows()
        self.rowCountChanged.emit(0)
    
    def getData(self) -> List[Dict[str, Any]]:
        """Get all data from the table."""
        return self.model.rows.copy()
    
    def getRowData(self, row: int) -> Dict[str, Any]:
        """Get data from a specific row."""
        if 0 <= row < len(self.model.rows):
            return self.model.rows[row].copy()
        return {}
    
    def setRowData(self, row: int, data: Dict[str, Any]):
        """Set data for a specific row."""
        if 0 <= row < len(self.model.rows):
            self.model.rows[row].update(data)
            # Emit data changed for entire row
            topLeft = self.model.index(row, 0)
            bottomRight = self.model.index(row, self.model.columnCount() - 1)
            self.model.dataChanged.emit(topLeft, bottomRight)
            self.model.dataModified.emit()
    
    def getCellValue(self, row: int, column: int) -> Any:
        """Get value from a specific cell."""
        if 0 <= row < len(self.model.rows) and 0 <= column < len(self.model.columnKeys):
            key = self.model.columnKeys[column]
            return self.model.rows[row].get(key)
        return None
    
    def setCellValue(self, row: int, column: int, value: Any):
        """Set value for a specific cell."""
        index = self.model.index(row, column)
        self.model.setData(index, value, Qt.EditRole)
    
    # ===== NumPy Helpers =====
    
    def getColumnAsNumpy(self, column: int, dtype=float) -> np.ndarray:
        """Get a column as numpy array."""
        if column >= len(self.model.columnKeys):
            return np.array([])
        
        key = self.model.columnKeys[column]
        values = [row.get(key) for row in self.model.rows]
        
        try:
            return np.array(values, dtype=dtype)
        except (ValueError, TypeError):
            return np.array(values)
    
    def getRowAsNumpy(self, row: int, dtype=float) -> np.ndarray:
        """Get a row as numpy array."""
        if row >= len(self.model.rows):
            return np.array([])
        
        values = list(self.model.rows[row].values())
        
        try:
            return np.array(values, dtype=dtype)
        except (ValueError, TypeError):
            return np.array(values)
    
    def getAllAsNumpy(self, dtype=float) -> np.ndarray:
        """Get all table data as 2D numpy array."""
        if not self.model.rows:
            return np.array([])
        
        data = []
        for row in self.model.rows:
            values = list(row.values())
            data.append(values)
        
        try:
            return np.array(data, dtype=dtype)
        except (ValueError, TypeError):
            return np.array(data)
    
    def loadFromNumpy(self, array: np.ndarray, columnKeys: List[str] = None):
        """Load data from numpy array."""
        if array.ndim != 2:
            raise ValueError("Array must be 2D")
        
        if columnKeys is None:
            columnKeys = self.model.columnKeys
        
        self.model.clearRows()
        
        for row in array:
            rowData = {key: value for key, value in zip(columnKeys, row)}
            self.model.addRow(rowData)
    
    # ===== Utility Methods =====
    
    def getSelectedRow(self) -> int:
        """Get currently selected row index."""
        index = self.tableView.currentIndex()
        return index.row() if index.isValid() else -1
    
    def getSelectedColumn(self) -> int:
        """Get currently selected column index."""
        index = self.tableView.currentIndex()
        return index.column() if index.isValid() else -1
    
    def copySelection(self):
        """Copy selected cells to clipboard (tab-separated)."""
        selection = self.tableView.selectedIndexes()
        if not selection:
            return
        
        # Sort by row then column
        selection.sort(key=lambda x: (x.row(), x.column()))
        
        dataStr = ""
        prevRow = -1
        
        for index in selection:
            if index.row() != prevRow and prevRow != -1:
                dataStr += "\n"
            elif prevRow != -1:
                dataStr += "\t"
            
            dataStr += str(index.data() or "")
            prevRow = index.row()
        
        QApplication.clipboard().setText(dataStr)
    
    def pasteFromClipboard(self):
        """Paste data from clipboard starting at current position."""
        startRow = self.getSelectedRow()
        startCol = self.getSelectedColumn()
        
        if startRow < 0 or startCol < 0:
            return
        
        text = QApplication.clipboard().text()
        if not text:
            return
        
        lines = text.strip().split("\n")
        
        for rowOffset, line in enumerate(lines):
            currentRow = startRow + rowOffset
            if currentRow >= self.model.rowCount():
                break
            
            values = line.split("\t")
            for colOffset, value in enumerate(values):
                currentCol = startCol + colOffset
                if currentCol >= self.model.columnCount():
                    break
                
                self.setCellValue(currentRow, currentCol, value)
    
    # ===== Callbacks =====
    
    def onRowCountChanged(self, callback: Callable[[int], None]):
        """Register callback for row count changes."""
        self.rowCountChanged.connect(callback)
    
    def onDataChanged(self, callback: Callable[[List[Dict]], None]):
        """Register callback for data changes."""
        self.dataChanged.connect(callback)
    
    def onCellChanged(self, callback: Callable[[int, int, Any], None]):
        """Register callback for cell changes."""
        self.cellChanged.connect(callback)
    
    # ===== Internal Slots =====
    
    def _onDataModified(self):
        """Internal slot for data modifications."""
        self.dataChanged.emit(self.getData())
    
    def _onCellClicked(self, index: QModelIndex):
        """Internal slot for cell clicks."""
        if index.isValid():
            value = self.getCellValue(index.row(), index.column())
            self.cellChanged.emit(index.row(), index.column(), value)