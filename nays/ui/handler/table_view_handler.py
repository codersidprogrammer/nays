from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from PySide6.QtWidgets import QComboBox, QStyledItemDelegate, QApplication, QTableView
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
        self.cellTypes: Dict[int, str] = {}  # column -> type mapping
        self.columnKeys: List[str] = []  # Maps columns to dict keys
    
    # ===== Basics =====
    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.rows)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.headers)
    
    # ===== Data Display & Editing =====
    def data(self, index: QModelIndex, role=Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        
        rowData = self.rows[index.row()]
        col = index.column()
        key = self.columnKeys[col] if col < len(self.columnKeys) else None
        value = rowData.get(key) if key else None
        
        cellType = self.cellTypes.get(col, "text")
        
        if role == Qt.DisplayRole or role == Qt.EditRole:
            if cellType == "checkbox":
                return ""
            return value
        
        if role == Qt.CheckStateRole and cellType == "checkbox":
            return Qt.Checked if value else Qt.Unchecked
        
        return None
    
    def setData(self, index: QModelIndex, value: Any, role=Qt.EditRole) -> bool:
        if not index.isValid():
            return False
        
        col = index.column()
        key = self.columnKeys[col] if col < len(self.columnKeys) else None
        if not key:
            return False
        
        cellType = self.cellTypes.get(col, "text")
        
        if cellType == "checkbox" and role == Qt.CheckStateRole:
            self.rows[index.row()][key] = value == Qt.Checked
        elif role == Qt.EditRole:
            self.rows[index.row()][key] = value
        else:
            return False
        
        self.dataChanged.emit(index, index)
        self.dataModified.emit()
        return True
    
    # ===== Flags =====
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        base = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        col = index.column()
        cellType = self.cellTypes.get(col, "text")
        
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