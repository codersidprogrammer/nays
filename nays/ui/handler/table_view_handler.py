from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np

from PySide6.QtWidgets import QComboBox, QStyledItemDelegate, QApplication, QTableView, QLineEdit
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QObject, Signal, QEvent


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
            return None  # Checkbox handled via editorEvent
        else:
            # Default text editor
            return QLineEdit(parent)
    
    def editorEvent(self, event, model, option, index):
        """Handle checkbox toggle on mouse click."""
        cellType = index.data(Qt.UserRole)
        
        if cellType == "checkbox":
            # Handle mouse button release to toggle checkbox
            if event.type() == QEvent.MouseButtonRelease:
                currentState = index.data(Qt.CheckStateRole)
                newState = Qt.Unchecked if currentState == Qt.Checked else Qt.Checked
                return model.setData(index, newState, Qt.CheckStateRole)
        
        return super().editorEvent(event, model, option, index)
    
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
        
        # Checkbox labels: (row, col) -> (checked_label, unchecked_label)
        self.cellCheckboxLabels: Dict[Tuple[int, int], Tuple[str, str]] = {}
    
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
                    keyToDisplay: Dict[Any, str] = None, displayToKey: Dict[str, Any] = None,
                    checkboxLabels: Tuple[str, str] = None):
        """Set cell type for a specific cell."""
        self.cellTypeOverrides[(row, col)] = cellType
        if comboItems:
            self.cellComboItems[(row, col)] = comboItems
        if keyToDisplay:
            self.cellKeyToDisplay[(row, col)] = keyToDisplay
        if displayToKey:
            self.cellDisplayToKey[(row, col)] = displayToKey
        if checkboxLabels:
            self.cellCheckboxLabels[(row, col)] = checkboxLabels
    
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
                # Return checkbox label if configured
                labels = self.cellCheckboxLabels.get((row, col))
                if labels:
                    checkedLabel, uncheckedLabel = labels
                    return checkedLabel if value else uncheckedLabel
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
    def addRow(self, rowData: Dict[str, Any] = None, shouldEmit: bool = True):
        """Add a new row to the table."""
        if rowData is None:
            rowData = {key: "" for key in self.columnKeys}
        
        self.beginInsertRows(QModelIndex(), len(self.rows), len(self.rows))
        self.rows.append(rowData)
        self.endInsertRows()
        if shouldEmit:
            self.dataModified.emit()
    
    def deleteRow(self, row: int, shouldEmit: bool = True):
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
        keysToRemove = [k for k in self.cellCheckboxLabels if k[0] == row]
        for k in keysToRemove:
            del self.cellCheckboxLabels[k]
        
        if shouldEmit:
            self.dataModified.emit()
    
    def insertRow(self, row: int, rowData: Dict[str, Any] = None, shouldEmit: bool = True):
        """Insert a row at a specific position."""
        if rowData is None:
            rowData = {key: "" for key in self.columnKeys}
        
        self.beginInsertRows(QModelIndex(), row, row)
        self.rows.insert(row, rowData)
        self.endInsertRows()
        if shouldEmit:
            self.dataModified.emit()
    
    def clearRows(self, shouldEmit: bool = True):
        """Clear all rows."""
        if len(self.rows) > 0:
            self.beginRemoveRows(QModelIndex(), 0, len(self.rows) - 1)
            self.rows.clear()
            self.cellTypeOverrides.clear()
            self.cellComboItems.clear()
            self.cellKeyToDisplay.clear()
            self.cellDisplayToKey.clear()
            self.cellKeyValues.clear()
            self.cellCheckboxLabels.clear()
            self.endRemoveRows()
            if shouldEmit:
                self.dataModified.emit()


# ---------------------------------
# Table View Handler
# ---------------------------------

class TableViewHandler(QObject):
    """Compact handler for QTableView with multi-type cell support."""
    
    rowCountChanged = Signal(int)
    dataChanged = Signal(list)  # emits list of dicts
    cellChanged = Signal(int, int, object)  # row, col, value
    
    # Default professional stylesheet
    DEFAULT_STYLE = """
        QTableView {
            border: 1px solid #d0d7de;
            border-radius: 4px;
            background-color: #ffffff;
            gridline-color: #e8ebee;
            selection-background-color: #0969da;
            selection-color: #ffffff;
            font-size: 13px;
        }
        QTableView::item {
            padding: 6px 8px;
            border-bottom: 1px solid #e8ebee;
        }
        QTableView::item:selected {
            background-color: #ddf4ff;
            color: #1f2328;
        }
        QTableView::item:hover {
            background-color: #f6f8fa;
        }
        QHeaderView::section {
            background-color: #f6f8fa;
            color: #1f2328;
            padding: 8px 6px;
            font-weight: 600;
            border: none;
            border-bottom: 2px solid #d0d7de;
            border-right: 1px solid #e8ebee;
        }
        QHeaderView::section:horizontal:last {
            border-right: none;
        }
        QHeaderView::section:hover {
            background-color: #eaeef2;
        }
        QScrollBar:vertical {
            background: #f6f8fa;
            width: 10px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background: #c9d1d9;
            border-radius: 5px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background: #8b949e;
        }
        QScrollBar:horizontal {
            background: #f6f8fa;
            height: 10px;
            border-radius: 5px;
        }
        QScrollBar::handle:horizontal {
            background: #c9d1d9;
            border-radius: 5px;
            min-width: 20px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #8b949e;
        }
        QScrollBar::add-line, QScrollBar::sub-line {
            border: none;
            background: none;
        }
    """
    
    # Dark theme stylesheet
    DARK_STYLE = """
        QTableView {
            border: 1px solid #30363d;
            border-radius: 4px;
            background-color: #0d1117;
            gridline-color: #21262d;
            selection-background-color: #388bfd;
            selection-color: #ffffff;
            font-size: 13px;
            color: #c9d1d9;
        }
        QTableView::item {
            padding: 6px 8px;
            border-bottom: 1px solid #21262d;
        }
        QTableView::item:selected {
            background-color: #1f6feb;
            color: #ffffff;
        }
        QTableView::item:hover {
            background-color: #161b22;
        }
        QHeaderView::section {
            background-color: #161b22;
            color: #c9d1d9;
            padding: 8px 6px;
            font-weight: 600;
            border: none;
            border-bottom: 2px solid #30363d;
            border-right: 1px solid #21262d;
        }
        QHeaderView::section:horizontal:last {
            border-right: none;
        }
        QHeaderView::section:hover {
            background-color: #21262d;
        }
        QScrollBar:vertical {
            background: #161b22;
            width: 10px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background: #30363d;
            border-radius: 5px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background: #484f58;
        }
        QScrollBar:horizontal {
            background: #161b22;
            height: 10px;
            border-radius: 5px;
        }
        QScrollBar::handle:horizontal {
            background: #30363d;
            border-radius: 5px;
            min-width: 20px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #484f58;
        }
        QScrollBar::add-line, QScrollBar::sub-line {
            border: none;
            background: none;
        }
    """
    
    def __init__(self, tableView: QTableView, headers: List[str] = None, applyDefaultStyle: bool = False):
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
        
        # Apply default style if requested
        if applyDefaultStyle:
            self.applyStyle()
    
    # ===== Styling =====
    
    def applyStyle(self, style: str = None):
        """
        Apply a stylesheet to the table view.
        
        Args:
            style: CSS stylesheet string. If None, applies DEFAULT_STYLE.
                   Use TableViewHandler.DARK_STYLE for dark theme.
        """
        if style is None:
            style = self.DEFAULT_STYLE
        self.tableView.setStyleSheet(style)
        
        # Apply some sensible defaults
        self.tableView.setAlternatingRowColors(False)
        self.tableView.setShowGrid(True)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.verticalHeader().setDefaultSectionSize(32)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
    
    def applyDarkStyle(self):
        """Apply dark theme styling to the table view."""
        self.applyStyle(self.DARK_STYLE)
    
    def setCustomStyle(self, stylesheet: str):
        """
        Apply a custom stylesheet to the table view.
        
        Args:
            stylesheet: Custom CSS stylesheet string.
        """
        self.tableView.setStyleSheet(stylesheet)
    
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
    
    def setCellType(self, row: int, col: int, cellType: str, comboItems: List[str] = None,
                    checkboxLabels: Tuple[str, str] = None):
        """
        Set cell type for a specific cell.
        
        Args:
            row: Row index
            col: Column index
            cellType: 'text', 'combobox', or 'checkbox'
            comboItems: List of combo items (for combobox type)
            checkboxLabels: Tuple of (checked_label, unchecked_label) for checkbox display
        """
        self.model.setCellType(row, col, cellType, comboItems, checkboxLabels=checkboxLabels)
    
    # ===== Config Loading =====
    
    def loadFromConfigAsColumns(
        self,
        config: List[Dict[str, Any]],
        addDefaultRow: bool = True,
        comboDisplayMode: str = "value"
    ):
        """
        Load config as COLUMNS instead of rows. Each config item defines a column.
        
        Use this when you want a table where:
        - Each config item is a COLUMN (header, type, default value)
        - Rows represent data entries (e.g., segments, items, records)
        
        Example:
            config = [
                {'name': 'Segment Name', 'type': 'editable', 'defaultValueIndex': 'New Segment'},
                {'name': 'Length', 'type': 'editable', 'defaultValueIndex': 0},
                {'name': 'Material', 'type': 'combobox', 'defaultValueIndex': 0, 'items': [{0: "Steel"}, {1: "Concrete"}]}
            ]
            handler.loadFromConfigAsColumns(config)
            # Results in table:
            # | Segment Name | Length | Material |
            # | New Segment  | 0      | Steel    |
        
        Args:
            config: List of config dictionaries defining columns
            addDefaultRow: If True, adds a row with default values
            comboDisplayMode: How to display combo items ("value", "key", or "both")
        """
        self.enableMultiTypeCells()
        self.model.clearRows()
        
        # Extract column headers from config
        headers = [item.get("name", f"Column {i}") for i, item in enumerate(config)]
        self.model.headers = headers
        self.model.columnKeys = headers
        
        # Update table view headers
        self.headers = headers
        
        # Prepare default row data if needed
        if addDefaultRow:
            defaultRow = {}
            
            for colIdx, item in enumerate(config):
                name = item.get("name", f"Column {colIdx}")
                itemType = item.get("type", "editable")
                defaultValueIndex = item.get("defaultValueIndex", "")
                items = item.get("items", [])
                
                # Determine cell type
                if itemType == "combobox":
                    cellType = "combobox"
                elif itemType == "checkbox":
                    cellType = "checkbox"
                else:
                    cellType = "text"
                
                # Parse combo items for combobox type
                if cellType == "combobox" and items:
                    comboItems = []
                    keyToDisplay = {}
                    displayToKey = {}
                    itemsList = []
                    
                    for itemDict in items:
                        for key, val in itemDict.items():
                            keyInt = int(key)
                            itemsList.append((keyInt, val))
                            
                            # Format based on display mode
                            if comboDisplayMode == "key":
                                displayText = str(key)
                            elif comboDisplayMode == "both":
                                displayText = f"{key}: {val}"
                            else:  # "value"
                                displayText = val
                            
                            comboItems.append(displayText)
                            keyToDisplay[keyInt] = displayText
                            displayToKey[displayText] = keyInt
                    
                    # Get default value
                    if isinstance(defaultValueIndex, int) and 0 <= defaultValueIndex < len(itemsList):
                        actualKeyValue = itemsList[defaultValueIndex][0]
                        displayValue = keyToDisplay.get(actualKeyValue, str(actualKeyValue))
                        defaultRow[name] = displayValue
                    else:
                        defaultRow[name] = comboItems[0] if comboItems else ""
                    
                    # Store column metadata for future rows
                    self.model.cellTypes[colIdx] = cellType
                    # Store mappings for this column (will apply to row 0)
                    self.model.cellComboItems[(0, colIdx)] = comboItems
                    self.model.cellKeyToDisplay[(0, colIdx)] = keyToDisplay
                    self.model.cellDisplayToKey[(0, colIdx)] = displayToKey
                    if isinstance(defaultValueIndex, int) and 0 <= defaultValueIndex < len(itemsList):
                        self.model.cellKeyValues[(0, colIdx)] = itemsList[defaultValueIndex][0]
                        
                elif cellType == "checkbox":
                    # Handle checkbox default
                    if isinstance(defaultValueIndex, bool):
                        defaultRow[name] = defaultValueIndex
                    elif isinstance(defaultValueIndex, (int, float)):
                        defaultRow[name] = bool(defaultValueIndex)
                    else:
                        defaultRow[name] = False
                    self.model.cellTypes[colIdx] = cellType
                else:
                    # Text/editable
                    defaultRow[name] = defaultValueIndex
                    self.model.cellTypes[colIdx] = cellType
            
            # Add the default row
            self.model.addRow(defaultRow)
        
        self.tableView.resizeColumnsToContents()
        self.rowCountChanged.emit(self.model.rowCount())
    
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
                            For checkbox, use True/False or 1/0 for checked state.
        - items: List of dicts for combobox options [{-1: "Option A"}, {0: "Option B"}, {1: "Option C"}]
        - checkedLabel: Optional label to display when checkbox is checked (e.g., "Set as 1")
        - uncheckedLabel: Optional label to display when checkbox is unchecked (e.g., "Set as 0")
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
        
        # Ensure columnKeys is set from headers if not already set
        if not self.model.columnKeys and self.model.headers:
            self.model.columnKeys = list(self.model.headers)
        
        for rowIdx, item in enumerate(config):
            name = item.get("name", "")
            itemType = item.get("type", "editable")
            defaultValueIndex = item.get("defaultValueIndex", "")
            items = item.get("items", [])
            description = item.get("description", "")
            # Checkbox labels
            checkedLabel = item.get("checkedLabel", None)
            uncheckedLabel = item.get("uncheckedLabel", None)
            
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
            
            # Build checkbox labels tuple if provided
            checkboxLabels = None
            if cellType == "checkbox" and (checkedLabel or uncheckedLabel):
                checkboxLabels = (checkedLabel or "", uncheckedLabel or "")
            
            # Set cell type for the value column with mappings
            self.model.setCellType(
                rowIdx, valueColumn, cellType, comboItems,
                keyToDisplay=keyToDisplay,
                displayToKey=displayToKey,
                checkboxLabels=checkboxLabels
            )
            
            # Store the actual key value
            if actualKeyValue is not None:
                self.model.setKeyValue(rowIdx, valueColumn, actualKeyValue)
        
        self.tableView.resizeColumnsToContents()
        self.rowCountChanged.emit(self.model.rowCount())
    
    def addRowForColumnConfig(self, config: List[Dict[str, Any]], comboDisplayMode: str = "value"):
        """
        Add a new row based on column config (used after loadFromConfigAsColumns).
        
        This applies the same cell types and combo items from the config to the new row.
        
        Args:
            config: Same config list used in loadFromConfigAsColumns
            comboDisplayMode: How to display combo items ("value", "key", or "both")
        """
        rowIdx = len(self.model.rows)
        rowData = {}
        
        for colIdx, item in enumerate(config):
            name = item.get("name", f"Column {colIdx}")
            itemType = item.get("type", "editable")
            defaultValueIndex = item.get("defaultValueIndex", "")
            items = item.get("items", [])
            
            # Determine cell type
            if itemType == "combobox":
                cellType = "combobox"
            elif itemType == "checkbox":
                cellType = "checkbox"
            else:
                cellType = "text"
            
            # Set default value based on type
            if cellType == "combobox" and items:
                comboItems = []
                keyToDisplay = {}
                displayToKey = {}
                itemsList = []
                
                for itemDict in items:
                    for key, val in itemDict.items():
                        keyInt = int(key)
                        itemsList.append((keyInt, val))
                        
                        if comboDisplayMode == "key":
                            displayText = str(key)
                        elif comboDisplayMode == "both":
                            displayText = f"{key}: {val}"
                        else:
                            displayText = val
                        
                        comboItems.append(displayText)
                        keyToDisplay[keyInt] = displayText
                        displayToKey[displayText] = keyInt
                
                # Set default value
                if isinstance(defaultValueIndex, int) and 0 <= defaultValueIndex < len(itemsList):
                    actualKeyValue = itemsList[defaultValueIndex][0]
                    displayValue = keyToDisplay.get(actualKeyValue, str(actualKeyValue))
                    rowData[name] = displayValue
                else:
                    rowData[name] = comboItems[0] if comboItems else ""
                
                # Store cell metadata
                self.model.cellComboItems[(rowIdx, colIdx)] = comboItems
                self.model.cellKeyToDisplay[(rowIdx, colIdx)] = keyToDisplay
                self.model.cellDisplayToKey[(rowIdx, colIdx)] = displayToKey
                self.model.cellTypeOverrides[(rowIdx, colIdx)] = cellType
                if isinstance(defaultValueIndex, int) and 0 <= defaultValueIndex < len(itemsList):
                    self.model.cellKeyValues[(rowIdx, colIdx)] = itemsList[defaultValueIndex][0]
            elif cellType == "checkbox":
                if isinstance(defaultValueIndex, bool):
                    rowData[name] = defaultValueIndex
                elif isinstance(defaultValueIndex, (int, float)):
                    rowData[name] = bool(defaultValueIndex)
                else:
                    rowData[name] = False
                self.model.cellTypeOverrides[(rowIdx, colIdx)] = cellType
            else:
                rowData[name] = defaultValueIndex
        
        # Add the row
        self.model.addRow(rowData)
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
    
    def updateValuesFromSaved(
        self, 
        savedData: List[Dict[str, Any]], 
        nameField: str = "name",
        valueField: str = "value",
        valueColumn: int = 1,
        shouldEmit: bool = True
    ):
        """
        Update table values from saved data (e.g., from SQL persistence).
        This preserves the structure (cell types, combo items, descriptions) from YAML config
        and only updates the values.
        
        Args:
            savedData: List of dicts with name-value pairs, e.g.:
                       [{'name': 'IRAD', 'value': '1'}, {'name': 'IDIFF', 'value': '0'}]
            nameField: Key for the name field in savedData (default 'name')
            valueField: Key for the value field in savedData (default 'value')
            valueColumn: Column index for values (default 1)
            shouldEmit: If True, emit dataChanged signal after update (default True).
                       Set to False to prevent triggering persistence callbacks during load.
        
        Note:
            - For combobox cells: value should be the key (e.g., -1, 0, 1), not the index
            - For checkbox cells: value should be True/False, 1/0, or '1'/'0'
            - For text cells: value is used directly
        
        Example workflow:
            # 1. Load structure from YAML
            handler.loadFromYamlConfig(yaml_config)
            
            # 2. Load saved values from SQL (without triggering save callback)
            saved = [{'name': 'IRAD', 'value': 1}, {'name': 'IDIFF', 'value': -1}]
            handler.updateValuesFromSaved(saved, shouldEmit=False)
        """
        if len(self.model.columnKeys) < 2:
            return
        
        nameKey = self.model.columnKeys[0]
        valueKey = self.model.columnKeys[1]
        
        # Build lookup: name -> row index
        nameToRow = {}
        for rowIdx, row in enumerate(self.model.rows):
            name = row.get(nameKey, "")
            if name:
                nameToRow[name] = rowIdx
        
        # Update values
        for item in savedData:
            name = item.get(nameField)
            value = item.get(valueField)
            
            if name not in nameToRow:
                continue
            
            rowIdx = nameToRow[name]
            cellType = self.model.getCellType(rowIdx, valueColumn)
            
            if cellType == "combobox":
                # Value is the key, need to convert to display text
                # Try to parse as int if it's a string
                try:
                    keyValue = int(value) if isinstance(value, str) else value
                except (ValueError, TypeError):
                    keyValue = value
                
                # Get the key-to-display mapping
                keyToDisplay = self.model.cellKeyToDisplay.get((rowIdx, valueColumn), {})
                
                if keyValue in keyToDisplay:
                    displayText = keyToDisplay[keyValue]
                    self.model.rows[rowIdx][valueKey] = displayText
                    self.model.setKeyValue(rowIdx, valueColumn, keyValue)
                else:
                    # Key not found in mapping, store as-is
                    self.model.rows[rowIdx][valueKey] = str(keyValue)
                    self.model.setKeyValue(rowIdx, valueColumn, keyValue)
                    
            elif cellType == "checkbox":
                # Convert to boolean
                if isinstance(value, bool):
                    boolValue = value
                elif isinstance(value, (int, float)):
                    boolValue = bool(value)
                elif isinstance(value, str):
                    boolValue = value.lower() in ('true', '1', 'yes', 'on')
                else:
                    boolValue = bool(value)
                
                self.model.rows[rowIdx][valueKey] = boolValue
                
            else:
                # Text cell - use value directly
                self.model.rows[rowIdx][valueKey] = value
        
        # Notify that data changed (only if shouldEmit is True)
        if shouldEmit and self.model.rows:
            topLeft = self.model.index(0, 0)
            bottomRight = self.model.index(len(self.model.rows) - 1, self.model.columnCount() - 1)
            self.model.dataChanged.emit(topLeft, bottomRight)
        
        self.tableView.resizeColumnsToContents()

    # ===== Data Operations =====
    
    def loadData(self, data: List[Dict[str, Any]], shouldEmit: bool = True):
        """Load data into the table.
        
        Args:
            data: List of row dictionaries to load
            shouldEmit: If True, emit dataChanged signal after loading (default True).
                       Set to False to prevent triggering callbacks during load.
        """
        self.model.clearRows(shouldEmit)
        for rowData in data:
            self.model.addRow(rowData, shouldEmit=shouldEmit)
        
        # Always emit Qt's dataChanged signal to refresh the view
        if self.model.rows:
            topLeft = self.model.index(0, 0)
            bottomRight = self.model.index(len(self.model.rows) - 1, self.model.columnCount() - 1)
            self.model.dataChanged.emit(topLeft, bottomRight)
        
        # Only emit rowCountChanged if shouldEmit is True
        if shouldEmit:
            self.rowCountChanged.emit(self.model.rowCount())
    
    def addRow(self, rowData: Dict[str, Any] = None, shouldEmit: bool = True):
        """Add a new row.
        
        Args:
            rowData: Dictionary with row data
            shouldEmit: If True, emit signals after adding (default True).
                       Set to False to prevent triggering callbacks.
        """
        self.model.addRow(rowData)
        if shouldEmit:
            self.rowCountChanged.emit(self.model.rowCount())
    
    def deleteRow(self, row: int, shouldEmit: bool = True):
        """Delete a specific row.
        
        Args:
            row: Row index to delete
            shouldEmit: If True, emit signals after deletion (default True).
                       Set to False to prevent triggering callbacks.
        """
        self.model.deleteRow(row, shouldEmit=shouldEmit)
        if shouldEmit:
            self.rowCountChanged.emit(self.model.rowCount())
    
    def insertRow(self, row: int, rowData: Dict[str, Any] = None, shouldEmit: bool = True):
        """Insert a row at a specific position.
        
        Args:
            row: Row index to insert at
            rowData: Dictionary with row data
            shouldEmit: If True, emit signals after insertion (default True).
                       Set to False to prevent triggering callbacks.
        """
        self.model.insertRow(row, rowData, shouldEmit=shouldEmit)
        if shouldEmit:
            self.rowCountChanged.emit(self.model.rowCount())
    
    def clearAll(self, shouldEmit: bool = True):
        """Clear all rows.
        
        Args:
            shouldEmit: If True, emit signals after clearing (default True).
                       Set to False to prevent triggering callbacks.
        """
        self.model.clearRows(shouldEmit=shouldEmit)
        if shouldEmit:
            self.rowCountChanged.emit(0)
    
    def getData(self) -> List[Dict[str, Any]]:
        """Get all data from the table."""
        return self.model.rows.copy()
    
    def getRowData(self, row: int) -> Dict[str, Any]:
        """Get data from a specific row."""
        if 0 <= row < len(self.model.rows):
            return self.model.rows[row].copy()
        return {}
    
    def setRowData(self, row: int, data: Dict[str, Any], shouldEmit: bool = True):
        """Set data for a specific row.
        
        Args:
            row: Row index
            data: Dictionary with row data to update
            shouldEmit: If True, emit dataChanged signal after update (default True).
                       Set to False to prevent triggering callbacks.
        """
        if 0 <= row < len(self.model.rows):
            self.model.rows[row].update(data)
            # Emit data changed for entire row if requested
            if shouldEmit:
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