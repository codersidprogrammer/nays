import re
import numpy as np
from PySide6.QtWidgets import QWidget, QComboBox, QLabel, QTableWidget, QTableWidgetItem, QCheckBox, QHBoxLayout, QApplication
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import Qt, QTimer
from functools import partial

from PySide6.QtCore import QObject, Signal

from nays.core.initializer import YamlInitializer
from nays.ui.based_tabular_model import TableHandlerDataModel

def defaultComboCallback(row: int, combo: QComboBox, param: str):
        """
        Callback for combobox changes.
        This method can be overridden to handle combobox changes.
        
        Args:
            row (int): The row index of the combobox.
            combo (QComboBox): The combobox widget.
            param (str): Additional parameter, e.g., the name of the setting.
        """
        print(f"Combobox changed at row {row}, param: {param}, value: {combo.currentData()}")


class DataTableHandler(QObject):
    rowCountChange = Signal(int)
    dataChange = Signal(np.ndarray)
    
    def __init__(self, table: QTableWidget, setDefaultStyle:bool = False):
        super().__init__()
        self.table = table
        self.rowCount = table.rowCount()
        self.columnCount = table.columnCount()
        self.allowEmitDataChange = True
        self.table.cellChanged.connect(self.__emitDataChange)
        self.table.cellChanged.connect(self.__emitDataChange)
        
        if setDefaultStyle:
            self.table.setStyleSheet("""
                                    QTableWidget {
                                        border: 1px solid #e8ebee; /* This sets the outer border */
                                    }
                                    QTableWidget::item {
                                        /* You can also style individual cell borders here if needed */
                                        /* For example: border: 1px solid red; */
                                    }
                                    QHeaderView::section {
                                        background-color: #f0f4f9; /* Green background */
                                        color: #626263;             /* text color */
                                        padding: 5px;             /* Padding inside the header cell */
                                        font-weight: bold;        /* Bold font */
                                    }
                                    /* Style for the first column header specifically */
                                    QHeaderView::section:nth-child(1) {
                                        background-color: #FF5722; /* Orange background for the first column */
                                        border: 1px solid #E64A19;
                                    }
                                    """)

            self.table.horizontalHeader().setStretchLastSection(True)
            self.table.verticalHeader().setDefaultSectionSize(14)
        
        # Optional: Automatically connect key press event if subclassing table
        self._install_key_event()
    
    def _install_key_event(self):
        orig_keyPressEvent = self.table.keyPressEvent

        def new_keyPressEvent(event: QKeyEvent):
            if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_C:
                self.copySelection()
            elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_V:
                self.pasteSelection()
            else:
                orig_keyPressEvent(event)

        self.table.keyPressEvent = new_keyPressEvent

    def resetTable(self):
        """
        Resets the table by clearing all rows and columns.
        """
        self.table.setRowCount(0)  # Clears all rows
        # self.table.setColumnCount(self.columnCount)  # Keep original number of columns
        # Optionally, you can reset the content of all cells if needed, but usually, clearing rows is sufficient
        self.rowCount = 0  # Reset row count to 0

        # Emit signal if row count changes
        self.rowCountChange.emit(self.rowCount)
        print("Table has been reset.")
        
    def resetTableValue(self, defaultValue=None):
        for row in range(self.table.rowCount()):
            for column in range(self.table.columnCount()):
                item = QTableWidgetItem()
                if defaultValue is not None:
                    # Handle different data types appropriately
                    if isinstance(defaultValue, (int, float)):
                        item.setData(Qt.DisplayRole, defaultValue)
                    else:
                        item.setText(str(defaultValue))
                self.table.setItem(row, column, item)

    def copySelection(self):
        selection = self.table.selectedRanges()
        if not selection:
            return
        range_ = selection[0]
        data = ""
        for row in range(range_.topRow(), range_.bottomRow() + 1):
            row_data = []
            for col in range(range_.leftColumn(), range_.rightColumn() + 1):
                item = self.table.item(row, col)
                row_data.append("" if item is None else item.text())
            data += "\t".join(row_data) + "\n"
        QApplication.clipboard().setText(data.strip())
        
    def pasteSelection(self):
        start_row = self.table.currentRow()
        start_col = self.table.currentColumn()

        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()

        if not text:
            return

        lines = text.splitlines()
        max_col = self.table.columnCount()

        for i, line in enumerate(lines):
            if not line.strip():
                continue

            # Split by tab or 2+ spaces
            columns = re.split(r'\s+', line.strip())

            for j, value in enumerate(columns):
                r = start_row + i
                c = start_col + j

                if c >= max_col:
                    continue  # Skip pasting beyond fixed column count

                # Auto-add row if needed
                if r >= self.table.rowCount():
                    self.table.insertRow(self.table.rowCount())
                    self.rowCountChange.emit(self.table.rowCount())

                try:
                    val = float(value)
                    if 'e' in value.lower():
                        display = f"{val:.4E}"
                    else:
                        display = str(int(val) if val.is_integer() else val)

                    item = QTableWidgetItem(display)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(r, c, item)
                except ValueError:
                    # Handle non-numeric gracefully
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(r, c, item)                
    
    def getColumnVectorAsNumpy(self, column: int):
        """
        Get a column vector from the table as a numpy array.
        
        Args:
            column (int): The index of the column to retrieve.
        
        Returns:
            np.ndarray: A numpy array containing the values from the specified column.
        """
        return np.array([float(self.table.item(row, column).text()) for row in range(self.rowCount) if self.table.item(row, column)])
    
    def getRowVectorAsNumpy(self, row: int):
        """
        Get a row vector from the table as a numpy array.
        
        Args:
            row (int): The index of the row to retrieve.
        
        Returns:
            np.ndarray: A numpy array containing the values from the specified row.
        """
        return np.array([float(self.table.item(row, column).text()) for column in range(self.columnCount) if self.table.item(row, column)])
    
    def setTableRows(self, rowCount: int, defaultValue: any = 0.0):
        """
        Set the number of rows in the table and fill them with a default value.
        
        If the new row count is less than the current, it will delete rows from the bottom.
        If greater, it adds rows and fills them with default values.

        Args:
            rowCount (int): The number of rows to set.
            defaultValue (float): The default value to fill the new cells with.
        """
        currentRowCount = self.table.rowCount()
        columnCount = self.table.columnCount()

        if rowCount < currentRowCount or rowCount == 0:
            # Remove rows from the bottom
            self.table.setRowCount(rowCount)
        else:
            # Add rows
            self.table.setRowCount(rowCount)
            for row in range(currentRowCount, rowCount):
                for column in range(columnCount):
                    item = QTableWidgetItem(str(defaultValue))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, column, item)
                    
        self.rowCountChange.emit(self.table.rowCount())
        
    def immediatelyEmitChange(self):
        self.dataChange.emit(self.getTableData())
                    
    def getTableData(self) -> np.ndarray:
        """
        Get all data from the table as a 2D numpy array.

        Returns:
            np.ndarray: A 2D numpy array containing all values from the table.
        """
        rowCount = self.table.rowCount()
        columnCount = self.table.columnCount()

        data = []
        for row in range(rowCount):
            row_data = []
            for column in range(columnCount):
                item = self.table.item(row, column)
                try:
                    value = float(item.text()) if item else 0.0
                except ValueError:
                    value = 0.0  # Fallback for invalid input
                row_data.append(value)
            data.append(row_data)

        return np.array(data)
    
    def loadDataFromNumpy(self, data: np.ndarray | list, is_override: bool = True, is_formatted: bool = False):
        """
        Load a 2D NumPy array into the QTableWidget.
        
        Args:
            data (np.ndarray): A 2D array where each row represents a table row.
        """
        
        # Convert to numpy array if it's a list or not already an ndarray
        if not isinstance(data, np.ndarray):
            try:
                data = np.array(data)
            except Exception as e:
                print(e)
                raise ValueError(f"Failed to convert data to NumPy array: {e}")

        # Ensure it's 2D
        if data.ndim != 2:
            if not is_override:
                raise ValueError("Input data must be a 2D array")
            data = np.zeros((1,1))
        
        rows, cols = data.shape
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)

        for row in range(rows):
            for col in range(cols):
                value = data[row, col]
                # Format using scientific notation for floats
                if isinstance(value, (float, np.floating)) and is_formatted:
                    text = f"{value:.7E}"
                else:
                    text = str(value)
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)
    
    def loadDataFromNumpyThenChange(self, data: np.ndarray, allowEmit: bool=True, isFormatted: bool=False):
        oldValue = self.allowEmitDataChange
        self.allowEmitDataChange = allowEmit
        self.loadDataFromNumpy(data=data, is_formatted=isFormatted)
        self.allowEmitDataChange = oldValue
        
    def __emitDataChange(self, data):
        if self.allowEmitDataChange:
            self.dataChange.emit(self.getTableData())
            
    

class DataTableBuilderHandler(DataTableHandler):
    
    dataDictChange = Signal(dict)
    dataModelChange = Signal(TableHandlerDataModel)
    
    def __init__(self, table: QTableWidget, tableType: str = 'rows'):
        super().__init__(table)
        self.tempDataDict: dict = {}
        self.__dataModel: list[list[TableHandlerDataModel]] = []
        self.data: list[dict] = None
        self.tableType = tableType
        self.allowEmitDataChange = True
        self.table.cellChanged.connect(self.__emitDataDictChange)
        self.table.cellChanged.connect(self.__emitDataModelChange) 
        
    def setData(self, data):
        self.data = data
        return self
    
    def setHorizontalHeaders(self, headers: list[str]):
        self.table.setColumnCount(len(headers))
        for i, value in enumerate(headers):
            self.table.setHorizontalHeaderItem(i, QTableWidgetItem(value))
        return self
    
    def buildAsVertical(self, isComboKey: bool = False):
        return self.__buildRows(self.data, isComboKey=isComboKey)
    
    def buildAsHorizontal(self, isComboKey: bool = False):
        return self.__buildColumns(self.data, isComboKey=isComboKey)

    def __emitDataDictChange(self, data):
        if self.allowEmitDataChange:
            self.dataDictChange.emit(self.getValuesAsDict())
            
    def __emitDataModelChange(self):
        if self.tableType == 'rows':
            model = self.getValueAsModel()
        else:
            model = self.getValueAsModelFromRows()
            
        self.__dataModel = model 
        if self.allowEmitDataChange:
            self.dataModelChange.emit(self.__dataModel)


    def getValuesAsDict(self, getKeyFromHeaderText: bool = True) -> dict:
        """
        Extracts values from the table as a dictionary using the header's user role to determine the type.
        Returns:
            dict: A dictionary with row names as keys and their extracted values.
        """
        values = {}

        for row in range(self.table.rowCount()):
            header_item = self.table.verticalHeaderItem(row)
            if not header_item:
                continue

            row_name = header_item.text() if getKeyFromHeaderText else header_item.data(Qt.ItemDataRole.WhatsThisPropertyRole)
            row_type = header_item.data(Qt.ItemDataRole.UserRole)
            

            match row_type:
                case 'combobox':
                    widget = self.table.cellWidget(row, 0)
                    if isinstance(widget, QComboBox):
                        # get current selected key (stored as data)
                        values[row_name] = widget.currentData()

                case 'checkbox':
                    container = self.table.cellWidget(row, 0)
                    if isinstance(container, QWidget):
                        checkbox = container.findChild(QCheckBox)
                        if checkbox:
                            values[row_name] = checkbox.isChecked()

                case _:
                    item = self.table.item(row, 0)
                    if item:
                        try:
                            values[row_name] =  {
                                'data': float(item.text()),
                                'index': None,
                            }
                        except ValueError:
                            values[row_name] =  {
                                'data': item.text(),
                                'index': None,
                            }

        return values

    def getValueAsModel(self, getKeyFromHeaderText: bool = True) -> list[list[TableHandlerDataModel]]:  
        """
        Extracts values from the table columns as a dictionary using the header's user role to determine the type.
        Returns:
            dict: A dictionary with column names as keys and their extracted values.
        """
        results: list[list[TableHandlerDataModel]] = []
        for row in range(self.table.rowCount()):
            row_header_item = self.table.verticalHeaderItem(row)
            row_header_id = row_header_item.data(Qt.ItemDataRole.WhatsThisPropertyRole) if row_header_item else None
            
            values = []
            for col in range(self.table.columnCount()):
                header_item = self.table.horizontalHeaderItem(col)
                if not header_item:
                    continue

                col_name = header_item.text() if getKeyFromHeaderText else header_item.data(Qt.ItemDataRole.WhatsThisPropertyRole)
                col_type = header_item.data(Qt.ItemDataRole.UserRole)
                

                match col_type:
                    case 'combobox':
                        widget = self.table.cellWidget(row, col)  # row 0 for horizontal layout
                        if isinstance(widget, QComboBox):
                            # get current selected key (stored as data)
                            
                            values.insert(col, TableHandlerDataModel(
                                id=row_header_id,
                                name=col_name,
                                description=header_item.toolTip(),
                                type='combobox',
                                defaultValueIndex=widget.currentIndex(),
                                items=[{i:widget.itemText(i)} for i in range(widget.count())]
                            ))

                    case 'checkbox':
                        container = self.table.cellWidget(row, col)  # row 0 for horizontal layout
                        if isinstance(container, QWidget):
                            checkbox = container.findChild(QCheckBox)
                            if checkbox:
                                values.insert(col, TableHandlerDataModel(
                                    id=row_header_id,
                                    name=col_name,
                                    description=header_item.toolTip(),
                                    type='checkbox',
                                    defaultValueIndex=checkbox.isChecked(),
                                    items=[{i:widget.itemText(i)} for i in range(widget.count())]
                                ))

                    case _:
                        item = self.table.item(row, col)  # row 0 for horizontal layout
                        if item:
                            try:
                                values.insert(col, TableHandlerDataModel(
                                    id=row_header_id,
                                    name=col_name,
                                    description=header_item.toolTip(),
                                    type='editable',
                                    defaultValueIndex=float(item.text()),
                                    items=[]
                                ))

                            except ValueError:
                                values.insert(col, TableHandlerDataModel(
                                    id=row_header_id,
                                    name=col_name,
                                    description=header_item.toolTip(),
                                    type='editable',
                                    defaultValueIndex=item.text(),
                                    items=[]
                                ))
            results.insert(row, values)

        return results

    def getValueAsModelFromRows(self, getKeyFromHeaderText: bool = True) -> list[list[TableHandlerDataModel]]:  
        """
        Extracts values from the table rows using the vertical header's user role to determine the type.
        Similar to getValueAsModel but works with row-based layout instead of column-based.
        Returns:
            list[list[TableHandlerDataModel]]: A list of lists where each inner list contains TableHandlerDataModel objects for a row.
        """
        results: list[list[TableHandlerDataModel]] = []
        for row in range(self.table.rowCount()):
            
            values = []
            for col in range(self.table.columnCount()):
                header_item = self.table.verticalHeaderItem(row)
                if not header_item:
                    continue

                row_name = header_item.text() if getKeyFromHeaderText else header_item.data(Qt.ItemDataRole.WhatsThisPropertyRole)
                row_type = header_item.data(Qt.ItemDataRole.UserRole)
                

                match row_type:
                    case 'combobox':
                        widget = self.table.cellWidget(row, col)
                        if isinstance(widget, QComboBox):
                            # get current selected key (stored as data)
                            
                            values.append(TableHandlerDataModel(
                                name=f"{row_name}_col{col}",
                                description=header_item.toolTip(),
                                type='combobox',
                                defaultValueIndex=widget.currentIndex(),
                                items=[{i:widget.itemText(i)} for i in range(widget.count())]
                            ))

                    case 'checkbox':
                        container = self.table.cellWidget(row, col)
                        if isinstance(container, QWidget):
                            checkbox = container.findChild(QCheckBox)
                            if checkbox:
                                values.append(TableHandlerDataModel(
                                    name=f"{row_name}_col{col}",
                                    description=header_item.toolTip(),
                                    type='checkbox',
                                    defaultValueIndex=checkbox.isChecked(),
                                    items=[]  # Checkboxes don't have items
                                ))

                    case _:
                        item = self.table.item(row, col)
                        if item:
                            try:
                                values.append(TableHandlerDataModel(
                                    name=f"{row_name}_col{col}",
                                    description=header_item.toolTip(),
                                    type='editable',
                                    defaultValueIndex=float(item.text()),
                                    items=[]
                                ))

                            except ValueError:
                                values.append(TableHandlerDataModel(
                                    name=f"{row_name}_col{col}",
                                    description=header_item.toolTip(),
                                    type='editable',
                                    defaultValueIndex=item.text(),
                                    items=[]
                                ))
            results.append(values)

        return results

    def setValueFromModelThenChange(self, models: list[list[TableHandlerDataModel]], allowEmit: bool = True, rebuildHeaders: bool = True):
        oldValue = self.allowEmitDataChange
        self.allowEmitDataChange = allowEmit
        self.setValueFromModel(models, rebuildHeaders)
        self.allowEmitDataChange = oldValue

    def setValueFromModelAsColumnsThenChange(self, models: list[list[TableHandlerDataModel]], allowEmit: bool = True, rebuildHeaders: bool = True):
        oldValue = self.allowEmitDataChange
        self.allowEmitDataChange = allowEmit
        self.setValueFromModelAsColumns(models, rebuildHeaders)
        self.allowEmitDataChange = oldValue

    def setValueFromModel(self, models: list[list[TableHandlerDataModel]], rebuildHeaders: bool = True):
        """
        Set table values from a list of TableHandlerDataModel lists.
        Each inner list represents a row, and each TableHandlerDataModel represents a column.
        
        Args:
            models: List of lists, where each inner list contains TableHandlerDataModel objects for a row
        """
        if not models:
            return
            
        # Set table dimensions
        row_count = len(models)
        col_count = len(models[0]) if models[0] else 0
        
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        
        # Set headers and populate data
        for row_idx, row_models in enumerate(models):
            # Store id from the first model in the row (if available)
            first_model = row_models[0] if row_models else None
            if first_model and hasattr(first_model, 'id') and first_model.id is not None:
                # Create or get vertical header item for this row
                idString = str(first_model.id)
                header_item = QTableWidgetItem(idString)
                header_item.setData(Qt.ItemDataRole.UserRole, 'row_id')
                header_item.setData(Qt.ItemDataRole.WhatsThisPropertyRole, first_model.id)
                self.table.setVerticalHeaderItem(row_idx, header_item)
            
            for col_idx, model in enumerate(row_models):
                # Set horizontal header if it's the first row
                if row_idx == 0 and rebuildHeaders:
                    header_item = QTableWidgetItem(model.name)
                    header_item.setToolTip(model.description)
                    header_item.setData(Qt.ItemDataRole.UserRole, model.type)
                    header_item.setData(Qt.ItemDataRole.WhatsThisPropertyRole, model.name)
                    self.table.setHorizontalHeaderItem(col_idx, header_item)
                
                # Create appropriate widget/item based on type
                match model.type:
                    case 'combobox':
                        combo = QComboBox()
                        
                        # Store the model id as a property on the combobox
                        if hasattr(model, 'id') and model.id is not None:
                            combo.setProperty('model_id', model.id)
                        
                        # Add items from model
                        for item_dict in model.items:
                            for key, value in item_dict.items():
                                combo.addItem(str(value), key)
                        
                        # Set current selection
                        if isinstance(model.defaultValueIndex, int) and model.defaultValueIndex < combo.count():
                            combo.setCurrentIndex(model.defaultValueIndex)
                        
                        # Connect callback
                        combo.currentIndexChanged.connect(
                            partial(self.comboCallback, row_idx, combo, model.name)
                        )
                        
                        self.table.setCellWidget(row_idx, col_idx, combo)
                    
                    case 'checkbox':
                        checkbox_label = QLabel('Set as = 0')
                        checkbox = QCheckBox()
                        
                        # Set checked state
                        is_checked = bool(model.defaultValueIndex) if model.defaultValueIndex is not None else False
                        checkbox.setChecked(is_checked)
                        
                        # Update label
                        checkbox_label.setText(f'Set as = {1 if is_checked else 0}')
                        
                        # Connect callback
                        checkbox.stateChanged.connect(
                            partial(self.checkboxCallback, row_idx, checkbox_label, model.name)
                        )
                        
                        # Create container widget
                        layout = QHBoxLayout()
                        layout.addWidget(checkbox)
                        layout.addWidget(checkbox_label)
                        layout.setContentsMargins(0, 0, 0, 0)
                        
                        widget = QWidget()
                        widget.setLayout(layout)
                        self.table.setCellWidget(row_idx, col_idx, widget)
                    
                    case _:  # 'editable' or any other type
                        # Create regular table item
                        value_text = str(model.defaultValueIndex) if model.defaultValueIndex is not None else "0"
                        item = QTableWidgetItem(value_text)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.table.setItem(row_idx, col_idx, item)
                        
        self.__emitDataModelChange()

    def setValueFromModelAsColumns(self, models: list[list[TableHandlerDataModel]], rebuildHeaders: bool = True):
        """
        Set table values from a list of TableHandlerDataModel lists for column-based layout.
        Each inner list represents a column, and each TableHandlerDataModel represents a row.
        This is the transpose version of setValueFromModel.
        
        Args:
            models: List of lists, where each inner list contains TableHandlerDataModel objects for a column
        """
        if not models:
            return
            
        # Set table dimensions - transpose the structure
        col_count = len(models)  # Number of columns = number of inner lists
        row_count = len(models[0]) if models[0] else 0  # Number of rows = length of first inner list
        
        self.table.setRowCount(row_count)
        self.table.setColumnCount(col_count)
        
        # Set headers and populate data
        for col_idx, col_models in enumerate(models):
            
            for row_idx, model in enumerate(col_models):
                # Set vertical header if it's the first column
                if col_idx == 0 and rebuildHeaders:
                    # Extract row name from model name (remove _col suffix)
                    row_name = model.name.split('_col')[0] if '_col' in model.name else model.name
                    header_item = QTableWidgetItem(row_name)
                    header_item.setToolTip(model.description)
                    header_item.setData(Qt.ItemDataRole.UserRole, model.type)
                    header_item.setData(Qt.ItemDataRole.WhatsThisPropertyRole, row_name)
                    self.table.setVerticalHeaderItem(row_idx, header_item)
                
                # Create appropriate widget/item based on type
                match model.type:
                    case 'combobox':
                        combo = QComboBox()
                        
                        # Add items from model
                        for item_dict in model.items:
                            for key, value in item_dict.items():
                                combo.addItem(str(value), key)
                        
                        # Set current selection
                        if isinstance(model.defaultValueIndex, int) and model.defaultValueIndex < combo.count():
                            combo.setCurrentIndex(model.defaultValueIndex)
                        
                        # Connect callback
                        combo.currentIndexChanged.connect(
                            partial(self.comboCallback, row_idx, combo, model.name)
                        )
                        
                        self.table.setCellWidget(row_idx, col_idx, combo)
                    
                    case 'checkbox':
                        checkbox_label = QLabel('Set as = 0')
                        checkbox = QCheckBox()
                        
                        # Set checked state
                        is_checked = bool(model.defaultValueIndex) if model.defaultValueIndex is not None else False
                        checkbox.setChecked(is_checked)
                        
                        # Update label
                        checkbox_label.setText(f'Set as = {1 if is_checked else 0}')
                        
                        # Connect callback
                        checkbox.stateChanged.connect(
                            partial(self.checkboxCallback, row_idx, checkbox_label, model.name)
                        )
                        
                        # Create container widget
                        layout = QHBoxLayout()
                        layout.addWidget(checkbox)
                        layout.addWidget(checkbox_label)
                        layout.setContentsMargins(0, 0, 0, 0)
                        
                        widget = QWidget()
                        widget.setLayout(layout)
                        self.table.setCellWidget(row_idx, col_idx, widget)
                    
                    case _:  # 'editable' or any other type
                        # Create regular table item
                        value_text = str(model.defaultValueIndex) if model.defaultValueIndex is not None else "0"
                        item = QTableWidgetItem(value_text)
                        item.setTextAlignment(Qt.AlignCenter)
                        self.table.setItem(row_idx, col_idx, item)
                        
        self.__emitDataModelChange()
    
    def getValuesAsDictFromColumns(self, getKeyFromHeaderText: bool = True) -> dict:
        """
        Extracts values from the table columns as a dictionary using the header's user role to determine the type.
        Returns:
            dict: A dictionary with column names as keys and their extracted values.
        """
        results = {}
        for row in range(self.table.rowCount()):
            
            values = {}
            for col in range(self.table.columnCount()):
                header_item = self.table.horizontalHeaderItem(col)
                if not header_item:
                    continue

                col_name = header_item.text() if getKeyFromHeaderText else header_item.data(Qt.ItemDataRole.WhatsThisPropertyRole)
                col_type = header_item.data(Qt.ItemDataRole.UserRole)
                

                match col_type:
                    case 'combobox':
                        widget = self.table.cellWidget(row, col)  # row 0 for horizontal layout
                        if isinstance(widget, QComboBox):
                            # get current selected key (stored as data)
                            
                            values[col_name] = {
                                'name': col_name,
                                'description': header_item.toolTip(),
                                'type': 'combobox',
                                'defaultValueIndex': widget.currentIndex(),
                                'items': [{i:widget.itemText(i)} for i in range(widget.count())]
                            }

                    case 'checkbox':
                        container = self.table.cellWidget(row, col)  # row 0 for horizontal layout
                        if isinstance(container, QWidget):
                            checkbox = container.findChild(QCheckBox)
                            if checkbox:
                                values[col_name] = {
                                    'name': col_name,
                                    'description': header_item.toolTip(),
                                    'type': 'checkbox',
                                    'defaultValueIndex': checkbox.isChecked(),
                                    'items': []
                                }

                    case _:
                        item = self.table.item(row, col)  # row 0 for horizontal layout
                        if item:
                            try:
                                values[col_name] =  {
                                    'name': col_name,
                                    'description': header_item.toolTip(),
                                    'type': 'editable',
                                    'defaultValueIndex': float(item.text()),
                                    'items': []
                                }

                            except ValueError:
                                values[col_name] =  {
                                    'name': col_name,
                                    'description': header_item.toolTip(),
                                    'type': 'editable',
                                    'defaultValueIndex': item.text(),
                                    'items': []
                                }
            results[row] = values
            
        return results

    def comboCallback(self, row: int, combo: QComboBox, param: str, index: int = None):
        self.tempDataDict[param] =  {
                        'data': combo.currentData(),
                        'index': combo.currentIndex(),
                    }
        self.dataDictChange.emit(self.tempDataDict)
        
        # get from latest
        models = self.getValueAsModelFromRows() if self.tableType == 'columns' else self.getValueAsModel()
        rowModel = models[row]
        
        # filter rowModel by name and get first match using next() with index tracking
        first_model = None
        found_index = -1
        
        for idx, model in enumerate(rowModel):
            if self.tableType == 'columns':
                # extract row name from model name
                model_name = model.name.split('_col')[0] if '_col' in model.name else model.name
                if model_name == param:
                    first_model = model
                    found_index = idx
                    break
            else:
                if model.name == param:
                    first_model = model
                    found_index = idx
                    break
        
        if first_model:
            first_model.defaultValueIndex = combo.currentIndex()
            rowModel[found_index] = first_model
            models[row] = rowModel
            self.dataModelChange.emit(models)
        else:
            print(f'Current row: {row}, index: {index}, table_mode: {self.tableType}')
            print(f"No model found with param: {param}")
        # TODO: Make signal while combobox change
        
        
    

    def checkboxCallback(self, row: int, checkbox_label: QLabel, param: str, state: int):
        __temp = 1 if state == 2 else 0
        self.tempDataDict[param] = {
            'data': __temp,
            'index': None,
        }
        checkbox_label.setText(f'Set as = {__temp}')
        self.dataDictChange.emit(self.tempDataDict)    
        
        # get from latest
        models = self.getValueAsModelFromRows() if self.tableType == 'columns' else self.getValueAsModel()
        rowModel = models[row]
        
        # filter rowModel by name and get first match using next() with index tracking
        first_model = None
        found_index = -1
        
        for idx, model in enumerate(rowModel):
            if self.tableType == 'columns':
                # extract row name from model name
                model_name = model.name.split('_col')[0] if '_col' in model.name else model.name
                if model_name == param:
                    first_model = model
                    found_index = idx
                    break
            else:
                if model.name == param:
                    first_model = model
                    found_index = idx
                    break
        
        if first_model:
            first_model.defaultValueIndex = __temp
            rowModel[found_index] = first_model
            models[row] = rowModel
            self.dataModelChange.emit(models)
        else:
            print(f'Current row: {row}, state: {state}, table_mode: {self.tableType}')
            print(f"No model found with param: {param}")
         
    def __buildRows(self, wamitconf: list[dict], isComboKey: bool = False):
        """
        Build rows automatically from the provided data dictionary based on group and subkey.
        Stores row 'type' metadata in vertical header using Qt.UserRole.
        """
        if not self.data:
            raise ValueError("Data is not set. Use setDataDict() first.")

        # self.resetTable()
        self.table.setRowCount(0)
        self.table.setRowCount(len(wamitconf))
        
        for i, rowDict in enumerate(wamitconf):
            row_name = rowDict.get('name', '')
            row_type = rowDict.get('type', 'editable')
            row_desc = rowDict.get('description', 'default')

            self.table.setRowHeight(i, 40)

            # Set vertical header with name and store type metadata
            header_item = QTableWidgetItem(row_name)
            header_item.setToolTip(row_desc)
            header_item.setData(Qt.ItemDataRole.UserRole, row_type)
            header_item.setData(Qt.ItemDataRole.WhatsThisPropertyRole, row_name)
            self.table.setVerticalHeaderItem(i, header_item)

            # Set description as label in column 1
            label = QLabel(rowDict.get('description', ''))
            label.setStyleSheet("QLabel { padding-left: 4px; }")
            self.table.setCellWidget(i, 1, label)

            match row_type:
                case 'combobox':
                    combo = QComboBox()
                    for item in rowDict.get('items', []):
                        for key, strValue in item.items():
                            if isComboKey:
                                combo.addItem(str(key), key)
                            else:
                                combo.addItem(str(strValue), key)

                    combo.currentIndexChanged.connect(
                        partial(self.comboCallback, i, combo, row_name)
                    )

                    combo.setCurrentIndex(int(rowDict.get('defaultValueIndex', 0)))
                    self.table.setCellWidget(i, 0, combo)
                    self.tempDataDict[row_name] = {
                        'data': combo.currentData(),
                        'index': combo.currentIndex(),
                    }

                case 'checkbox':
                    checkbox_label = QLabel('Set as = 0')
                    checkbox = QCheckBox()
                    checkbox.setChecked(False)

                    checkbox.stateChanged.connect(
                        partial(self.checkboxCallback, i, checkbox_label, row_name)
                    )

                    checkbox.setChecked(bool(rowDict.get('defaultValueIndex', False)))
                    layout = QHBoxLayout()
                    layout.addWidget(checkbox)
                    layout.addWidget(checkbox_label)
                    layout.setContentsMargins(0, 0, 0, 0)

                    widget = QWidget()
                    widget.setLayout(layout)
                    self.table.setCellWidget(i, 0, widget)
                    self.tempDataDict[row_name] = {
                        'data': 1 if checkbox.checkState() == Qt.CheckState.Checked else 0,
                        'index': None,
                    }

                case _:
                    item = QTableWidgetItem(str(rowDict.get('defaultValueIndex', 0.0)))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, 0, item)
                    self.tempDataDict[row_name] = {
                        'data': item.text(),
                        'index': None,
                    }

        return self
    
    def __buildColumns(self, wamitconf: list[dict], isComboKey: bool = False):
        """
        Build columns automatically from the provided data dictionary.
        Stores column 'type' metadata in horizontal header using Qt.UserRole.
        """
        if not self.data:
            raise ValueError("Data is not set. Use setDataDict() first.")

        # Reset table and set column count
        self.table.setRowCount(1)  # Only one row for horizontal layout
        self.table.setColumnCount(len(wamitconf))
        
        for i, colDict in enumerate(wamitconf):
            col_name = colDict.get('name', '')
            col_type = colDict.get('type', 'default')
            col_desc = colDict.get('description', 'default')

            self.table.setColumnWidth(i, 150)  # Set default column width

            # Set horizontal header with name and store type metadata
            header_item = QTableWidgetItem(col_name)
            header_item.setToolTip(col_desc)
            header_item.setData(Qt.ItemDataRole.UserRole, col_type)
            header_item.setData(Qt.ItemDataRole.WhatsThisPropertyRole, col_name)
            self.table.setHorizontalHeaderItem(i, header_item)

            match col_type:
                case 'combobox':
                    combo = QComboBox()
                    for item in colDict.get('items', []):
                        for key, strValue in item.items():
                            if isComboKey:
                                combo.addItem(str(key), key)
                            else:
                                combo.addItem(str(strValue), key)

                    combo.currentIndexChanged.connect(
                        partial(self.comboCallback, 0, combo, col_name, i)  # row 0 for horizontal
                    )

                    # Safely handle defaultValueIndex - ensure it's a valid integer
                    default_index = colDict.get('defaultValueIndex', 0)
                    if default_index is None:
                        default_index = 0
                    combo.setCurrentIndex(int(default_index))
                    self.table.setCellWidget(0, i, combo)
                    self.tempDataDict[col_name] = {
                        'data': combo.currentData(),
                        'index': combo.currentIndex(),
                    }

                case 'checkbox':
                    checkbox_label = QLabel('Set as = 0')
                    checkbox = QCheckBox()
                    checkbox.setChecked(False)

                    checkbox.stateChanged.connect(
                        partial(self.checkboxCallback, 0, checkbox_label, col_name)  # row 0 for horizontal
                    )

                    # Safely handle defaultValueIndex for checkbox
                    default_checked = colDict.get('defaultValueIndex', False)
                    if default_checked is None:
                        default_checked = False
                    checkbox.setChecked(bool(default_checked))
                    layout = QHBoxLayout()
                    layout.addWidget(checkbox)
                    layout.addWidget(checkbox_label)
                    layout.setContentsMargins(0, 0, 0, 0)

                    widget = QWidget()
                    widget.setLayout(layout)
                    self.table.setCellWidget(0, i, widget)
                    self.tempDataDict[col_name] = {
                        'data': 1 if checkbox.checkState() == Qt.CheckState.Checked else 0,
                        'index': None,
                    }

                case _:
                    # Safely handle defaultValueIndex for regular items
                    default_value = colDict.get('defaultValueIndex', 0.0)
                    if default_value is None:
                        default_value = 0.0
                    item = QTableWidgetItem(str(default_value))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(0, i, item)
                    self.tempDataDict[col_name] = {
                        'data': item.text(),
                        'index': None,
                    }
                    
        self.dataModelChange.emit(self.getValueAsModel())
        return self

    def setTableRowsForColumnsThenChange(self, rowCount: int, defaultValue = None, allowEmit: bool = True):
        oldValue = self.allowEmitDataChange
        self.allowEmitDataChange = allowEmit
        self.setTableRowsForColumns(rowCount, defaultValue)
        self.allowEmitDataChange = oldValue

    def setTableRowsForColumns(self, rowCount: int, defaultValue = None):
        """
        Set the number of rows in the table for column-based layout while maintaining the column structure.
        Similar to setTableRows but preserves the column widgets and metadata created by __buildColumns.
        
        Args:
            rowCount (int): The number of rows to set.
            defaultValue (list | any): Default values to fill the new cells with. 
                                     If list, should match column count. If single value or None, 
                                     will use 0.0 for all columns.
        """
        currentRowCount = self.table.rowCount()
        columnCount = self.table.columnCount()
        
        # Process defaultValue parameter
        if defaultValue is None:
            # Use 0.0 for all columns
            default_values = [0.0] * columnCount
        elif isinstance(defaultValue, list):
            if len(defaultValue) == columnCount:
                # Use provided list as-is
                default_values = defaultValue
            elif len(defaultValue) < columnCount:
                # Extend with 0.0 for missing columns
                default_values = defaultValue + [0.0] * (columnCount - len(defaultValue))
            else:
                # Truncate to match column count
                default_values = defaultValue[:columnCount]
        else:
            # Single value - repeat for all columns
            default_values = [defaultValue] * columnCount

        if rowCount < currentRowCount or rowCount == 0:
            # Remove rows from the bottom
            self.table.setRowCount(rowCount)
        else:
            # Add rows
            self.table.setRowCount(rowCount)
            
            # Fill new rows with appropriate widgets/items based on column metadata
            for row in range(currentRowCount, rowCount):
                for col in range(columnCount):
                    # Get the default value for this column
                    col_default_value = default_values[col] if col < len(default_values) else 0.0
                    
                    header_item = self.table.horizontalHeaderItem(col)
                    if not header_item:
                        # No header metadata, add simple item
                        item = QTableWidgetItem(str(col_default_value))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.table.setItem(row, col, item)
                        continue
                    
                    col_type = header_item.data(Qt.ItemDataRole.UserRole)
                    col_name = header_item.data(Qt.ItemDataRole.WhatsThisPropertyRole) or header_item.text()
                    
                    match col_type:
                        case 'combobox':
                            # Copy combobox structure from first row (row 0)
                            source_widget = self.table.cellWidget(0, col)
                            
                            if source_widget is None:
                                # If no source widget, create a new combobox using data from self.data
                                combo = QComboBox()
                                
                                # Find the column configuration in self.data
                                if self.data:
                                    for colDict in self.data:
                                        if colDict.get('name') == col_name and colDict.get('type') == 'combobox':
                                            # Add items from configuration
                                            for item in colDict.get('items', []):
                                                for key, strValue in item.items():
                                                    combo.addItem(str(strValue), key)
                                            
                                            # Set default selection
                                            combo.setCurrentIndex(int(colDict.get('defaultValueIndex', 0)))
                                            break
                                
                                # Connect to callback
                                combo.currentIndexChanged.connect(
                                    partial(self.comboCallback, row, combo, col_name)
                                )
                                
                                self.table.setCellWidget(row, col, combo)
                            
                            elif isinstance(source_widget, QComboBox):
                                
                                combo = QComboBox()
                                # Copy all items from source combobox
                                for i in range(source_widget.count()):
                                    text = source_widget.itemText(i)
                                    data = source_widget.itemData(i)
                                    combo.addItem(text, data)
                                
                                # Set default selection
                                combo.setCurrentIndex(source_widget.currentIndex())
                                
                                # Connect to callback
                                combo.currentIndexChanged.connect(
                                    partial(self.comboCallback, row, combo, col_name)
                                )
                                
                                self.table.setCellWidget(row, col, combo)
                        
                        case 'checkbox':
                            # Copy checkbox structure from first row (row 0)
                            source_container = self.table.cellWidget(0, col)
                            
                            if source_container is None:
                                # If no source widget, create a new checkbox using data from self.data
                                checkbox_label = QLabel('Set as = 0')
                                checkbox = QCheckBox()
                                
                                # Find the column configuration in self.data
                                if self.data:
                                    for colDict in self.data:
                                        if colDict.get('name') == col_name and colDict.get('type') == 'checkbox':
                                            checkbox.setChecked(bool(colDict.get('defaultValueIndex', False)))
                                            break
                                else:
                                    checkbox.setChecked(False)

                                checkbox.stateChanged.connect(
                                    partial(self.checkboxCallback, row, checkbox_label, col_name)
                                )

                                layout = QHBoxLayout()
                                layout.addWidget(checkbox)
                                layout.addWidget(checkbox_label)
                                layout.setContentsMargins(0, 0, 0, 0)

                                widget = QWidget()
                                widget.setLayout(layout)
                                self.table.setCellWidget(row, col, widget)
                                
                            elif isinstance(source_container, QWidget):
                                source_checkbox = source_container.findChild(QCheckBox)
                                if source_checkbox:
                                    checkbox_label = QLabel('Set as = 0')
                                    checkbox = QCheckBox()
                                    checkbox.setChecked(source_checkbox.isChecked())

                                    checkbox.stateChanged.connect(
                                        partial(self.checkboxCallback, row, checkbox_label, col_name)
                                    )

                                    layout = QHBoxLayout()
                                    layout.addWidget(checkbox)
                                    layout.addWidget(checkbox_label)
                                    layout.setContentsMargins(0, 0, 0, 0)

                                    widget = QWidget()
                                    widget.setLayout(layout)
                                    self.table.setCellWidget(row, col, widget)
                        
                        case _:
                            # Default case: add simple item with column-specific default value
                            item = QTableWidgetItem(str(col_default_value))
                            item.setTextAlignment(Qt.AlignCenter)
                            self.table.setItem(row, col, item)
                    
        self.rowCountChange.emit(self.table.rowCount())
        self.__emitDataModelChange()
    
    
    def setTableColumnsForRowsThenChange(self, colCount: int, defaultValue = None, allowEmit: bool = True):
        oldValue = self.allowEmitDataChange
        self.allowEmitDataChange = allowEmit
        self.setTableColumnsForRows(colCount, defaultValue)
        self.allowEmitDataChange = oldValue
        
    def setTableColumnsForRows(self, columnCount: int, defaultValue: any = 0.0):
        """
        Set the number of columns in the table for row-based layout while maintaining the row structure.
        Similar to setTableRowsForColumns but works with columns and preserves row widgets/metadata created by __buildRows.
        
        Args:
            columnCount (int): The number of columns to set.
            defaultValue (list | any): Default values to fill the new cells with. 
                                     If list of lists like [[1], [0.0], ['Segment']], each inner list contains 
                                     the default value for that row. If simple list, should match rows count. 
                                     If single value or None, will use 0.0 for all rows.
        """
        currentColumnCount = self.table.columnCount()
        rowCount = self.table.rowCount()
        
        row_defaults = []
        if isinstance(defaultValue, list):
            if len(defaultValue) > 0 and isinstance(defaultValue[0], list):
                # Handle list of lists format: [[1], [0.0], ['Segment']]
                for i in range(rowCount):
                    if i < len(defaultValue) and len(defaultValue[i]) > 0:
                        row_defaults.append(defaultValue[i][0])  # Take first value from inner list
                    else:
                        row_defaults.append(0.0)  # Default fallback
            else:
                # Handle simple list format: [1, 0.0, 'Segment']
                for i in range(rowCount):
                    if i < len(defaultValue):
                        row_defaults.append(defaultValue[i])
                    else:
                        row_defaults.append(0.0)  # Default fallback
        else:
            # Single value or None - use same value for all rows
            default_val = defaultValue if defaultValue is not None else 0.0
            row_defaults = [default_val] * rowCount

        if columnCount < currentColumnCount or columnCount == 0:
            # Remove columns from the right
            self.table.setColumnCount(columnCount)
        else:
            # Add columns
            self.table.setColumnCount(columnCount)
            
            # Fill new columns with appropriate widgets/items based on row metadata
            for col in range(currentColumnCount, columnCount):
                for row in range(rowCount):
                    # Get the default value for this specific row
                    row_default_value = row_defaults[row] if row < len(row_defaults) else 0.0
                
                    # Get row metadata from vertical header
                    source_header_item = self.table.verticalHeaderItem(row)
                    
                    if source_header_item:
                        # Copy the row structure from the source row
                        row_type = source_header_item.data(Qt.ItemDataRole.UserRole)
                        row_name = source_header_item.data(Qt.ItemDataRole.WhatsThisPropertyRole) or source_header_item.text()
                        
                        match row_type:
                            case 'combobox':
                                # Copy combobox structure from existing column (if any) or create new from data
                                source_widget = None
                                # Look for an existing combobox widget in any existing column for this row
                                for existing_col in range(currentColumnCount):
                                    widget = self.table.cellWidget(row, existing_col)
                                    if isinstance(widget, QComboBox):
                                        source_widget = widget
                                        break
                                
                                if source_widget is None:
                                    # If no source widget, create a new combobox using data from self.data
                                    combo = QComboBox()
                                    
                                    # Find the row configuration in self.data
                                    if self.data:
                                        for rowDict in self.data:
                                            if rowDict.get('name') == row_name and rowDict.get('type') == 'combobox':
                                                # Add items from configuration
                                                for item in rowDict.get('items', []):
                                                    for key, strValue in item.items():
                                                        combo.addItem(str(strValue), key)
                                                
                                                # Set default selection - use row_default_value if it's an integer
                                                if isinstance(row_default_value, int) and 0 <= row_default_value < combo.count():
                                                    combo.setCurrentIndex(row_default_value)
                                                else:
                                                    combo.setCurrentIndex(int(rowDict.get('defaultValueIndex', 0)))
                                                break
                                    
                                    # Connect to callback
                                    combo.currentIndexChanged.connect(
                                        partial(self.comboCallback, row, combo, f"{row_name}_{col}")
                                    )
                                    
                                    self.table.setCellWidget(row, col, combo)
                                
                                elif isinstance(source_widget, QComboBox):
                                    combo = QComboBox()
                                    # Copy all items from source combobox
                                    for i in range(source_widget.count()):
                                        text = source_widget.itemText(i)
                                        data = source_widget.itemData(i)
                                        combo.addItem(text, data)
                                    
                                    # Set default selection - use row_default_value if it's an integer
                                    if isinstance(row_default_value, int) and 0 <= row_default_value < combo.count():
                                        combo.setCurrentIndex(row_default_value)
                                    else:
                                        combo.setCurrentIndex(source_widget.currentIndex())
                                    
                                    # Connect to callback
                                    combo.currentIndexChanged.connect(
                                        partial(self.comboCallback, row, combo, f"{row_name}_{col}")
                                    )
                                    
                                    self.table.setCellWidget(row, col, combo)
                            
                            case 'checkbox':
                                # Copy checkbox structure from existing column (if any) or create new
                                source_container = None
                                # Look for an existing checkbox widget in any existing column for this row
                                for existing_col in range(currentColumnCount):
                                        widget = self.table.cellWidget(row, existing_col)
                                        if isinstance(widget, QWidget):
                                            checkbox = widget.findChild(QCheckBox)
                                            if checkbox:
                                                source_container = widget
                                                break
                                
                                if source_container is None:
                                    # If no source widget, create a new checkbox using data from self.data
                                    checkbox_label = QLabel('Set as = 0')
                                    checkbox = QCheckBox()
                                    
                                    # Set checkbox state - use row_default_value if it's boolean or convertible
                                    checkbox_state = False
                                    if isinstance(row_default_value, bool):
                                        checkbox_state = row_default_value
                                    elif isinstance(row_default_value, (int, float)):
                                        checkbox_state = bool(row_default_value)
                                    else:
                                        # Find the row configuration in self.data
                                        if self.data:
                                            for rowDict in self.data:
                                                if rowDict.get('name') == row_name and rowDict.get('type') == 'checkbox':
                                                    checkbox_state = bool(rowDict.get('defaultValueIndex', False))
                                                    break
                                    
                                    checkbox.setChecked(checkbox_state)

                                    checkbox.stateChanged.connect(
                                        partial(self.checkboxCallback, row, checkbox_label, f"{row_name}_{col}")
                                    )

                                    layout = QHBoxLayout()
                                    layout.addWidget(checkbox)
                                    layout.addWidget(checkbox_label)
                                    layout.setContentsMargins(0, 0, 0, 0)

                                    widget = QWidget()
                                    widget.setLayout(layout)
                                    self.table.setCellWidget(row, col, widget)
                                    
                                elif isinstance(source_container, QWidget):
                                    source_checkbox = source_container.findChild(QCheckBox)
                                    if source_checkbox:
                                        checkbox_label = QLabel('Set as = 0')
                                        checkbox = QCheckBox()
                                        
                                        # Set checkbox state - use row_default_value if it's boolean or convertible
                                        if isinstance(row_default_value, bool):
                                            checkbox.setChecked(row_default_value)
                                        elif isinstance(row_default_value, (int, float)):
                                            checkbox.setChecked(bool(row_default_value))
                                        else:
                                            checkbox.setChecked(source_checkbox.isChecked())

                                        checkbox.stateChanged.connect(
                                            partial(self.checkboxCallback, row, checkbox_label, f"{row_name}_{col}")
                                        )

                                        layout = QHBoxLayout()
                                        layout.addWidget(checkbox)
                                        layout.addWidget(checkbox_label)
                                        layout.setContentsMargins(0, 0, 0, 0)

                                        widget = QWidget()
                                        widget.setLayout(layout)
                                        self.table.setCellWidget(row, col, widget)
                            
                            case _:
                                # Default case: add simple item with row-specific default value
                                item = QTableWidgetItem(str(row_default_value))
                                item.setTextAlignment(Qt.AlignCenter)
                                self.table.setItem(row, col, item)
                    else:
                        # No header metadata, add simple item with row-specific default value
                        item = QTableWidgetItem(str(row_default_value))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.table.setItem(row, col, item)
                    
        # Note: No columnCountChange signal exists in base Qt, but we could emit a custom one if needed
        # For now, we'll emit rowCountChange to indicate table structure changed
        self.rowCountChange.emit(self.table.rowCount())
        self.__emitDataModelChange()
    
    def loadDataFromArray2D(self, data_array: list, column_headers: list[str] = None, allowEmit: bool=True):
        oldValue = self.allowEmitDataChange
        self.allowEmitDataChange = allowEmit
        self.__loadDataFromArray2D(data_array, column_headers)
        self.allowEmitDataChange = oldValue
        return self
    
    def __loadDataFromArray2D(self, data_array: list, column_headers: list[str] = None):
        """
        Load data from a 2D array and build the table structure using columns.
        Each row in the array represents table data, and columns are built dynamically based on data types.
        
        Args:
            data_array: 2D array where each row contains mixed data types:
                       [string, float, int, dict_with_combo_data, ...]
            column_headers: Optional list of column header names. If None, will use default names.
        
        Example data_array:
        [
            ["Segment 1", 0.00, 0.0, {'defaultValueIndex': 1, 'items': [{1: 'Chain', 2: 'Wire'}]}],
            ["Segment 2", 0.00, 0.0, {'defaultValueIndex': 1, 'items': [{1: 'Chain', 2: 'Wire'}]}],
            ["Segment 3", 0.00, 0.0, {'defaultValueIndex': 2, 'items': [{1: 'Chain', 2: 'Wire'}]}],
        ]
        """
        if not data_array or not data_array[0]:
            return self
        
        # Analyze first row to determine column structure
        first_row = data_array[0]
        column_count = len(first_row)
        
        # Generate default headers if not provided
        if column_headers is None:
            column_headers = [f'Column {i+1}' for i in range(column_count)]
        elif len(column_headers) != column_count:
            # Adjust headers to match column count
            if len(column_headers) < column_count:
                column_headers.extend([f'Column {i+1}' for i in range(len(column_headers), column_count)])
            else:
                column_headers = column_headers[:column_count]
        
        # Build column configuration based on data types
        column_config = []
        for i, (header, value) in enumerate(zip(column_headers, first_row)):
            col_dict = {
                'name': header,
                'description': f'Auto-generated column for {header}',
                'type': 'editable',  # default type
                'defaultValueIndex': 0
            }
            
            # Determine column type based on value type
            if isinstance(value, dict) and 'items' in value:
                # Combobox column
                col_dict['type'] = 'combobox'
                col_dict['items'] = value['items']
                col_dict['defaultValueIndex'] = value.get('defaultValueIndex', 0)
            elif isinstance(value, bool):
                # Checkbox column
                col_dict['type'] = 'checkbox'
                col_dict['defaultValueIndex'] = value
            else:
                # Regular editable column (string, int, float)
                col_dict['type'] = 'editable'
                col_dict['defaultValueIndex'] = value
            
            column_config.append(col_dict)
        
        # Set the data for the builder
        self.data = column_config
        
        # Build columns using the existing __buildColumns method
        self.__buildColumns(column_config, isComboKey=False)
        
        # Add additional rows and populate with data
        if len(data_array) > 1:
            # Process defaultValue for setTableRowsForColumns
            default_values = []
            for col_data in first_row:
                if isinstance(col_data, dict) and 'defaultValueIndex' in col_data:
                    default_values.append(col_data['defaultValueIndex'])
                else:
                    default_values.append(col_data)
            
            # Set the number of rows and fill with data
            self.setTableRowsForColumns(len(data_array), default_values)
            
            # Populate each row with specific data
            for row_idx, row_data in enumerate(data_array):
                for col_idx, cell_value in enumerate(row_data):
                    header_item = self.table.horizontalHeaderItem(col_idx)
                    if header_item:
                        col_type = header_item.data(Qt.ItemDataRole.UserRole)
                        
                        if col_type == 'combobox':
                            widget = self.table.cellWidget(row_idx, col_idx)
                            if isinstance(widget, QComboBox) and isinstance(cell_value, dict):
                                # Set the combobox to the specified index
                                target_index = cell_value.get('defaultValueIndex', 0)
                                if target_index < widget.count():
                                    widget.setCurrentIndex(target_index)
                        
                        elif col_type == 'checkbox':
                            container = self.table.cellWidget(row_idx, col_idx)
                            if isinstance(container, QWidget):
                                checkbox = container.findChild(QCheckBox)
                                if checkbox:
                                    checkbox.setChecked(bool(cell_value))
                        
                        else:
                            # Regular cell
                            item = self.table.item(row_idx, col_idx)
                            if item:
                                item.setText(str(cell_value))
        
        return self
    
    
class DataTableBuilder(DataTableHandler):
    dataDictChange = Signal(dict)
    
    def __init__(self, table: QTableWidget):
        super().__init__(table)
        self.data: YamlInitializer = None
        self.comboCallback = None
        self.checkboxCallback = None
        self.table.cellChanged.connect(self.__emitDataDictChange)
    
    def __emitDataDictChange(self, data):
        if self.allowEmitDataChange:
            self.dataDictChange.emit(self.getValuesAsDict())
        
    def setHorizontalHeaders(self, headers: list[str]):
        self.table.setColumnCount(len(headers))
        for i, value in enumerate(headers):
            self.table.setHorizontalHeaderItem(i, QTableWidgetItem(value))
        return self
    
    def setColumnsWidth(self, size: int):
        for colNumber in range(self.table.columnCount()):
            self.table.setColumnWidth(colNumber, size)
        return self
    
    def setDataDict(self, data: YamlInitializer):
        self.data = data
        return self
    
    def setComboCallback(self, callback):
        """
        Set callback for combobox changes.
        callback(row: int, combo: QComboBox)
        """
        self.comboCallback = callback
        return self

    def setCheckboxCallback(self, callback):
        """
        Set callback for checkbox changes.
        callback(row: int, state: int, label: QLabel, param: str)
        """
        self.checkboxCallback = callback
        return self
    
    def getValuesAsDict(self, getKeyFromHeaderText: bool = True) -> dict:
        """
        Extracts values from the table as a dictionary using the header's user role to determine the type.
        Returns:
            dict: A dictionary with row names as keys and their extracted values.
        """
        values = {}

        for row in range(self.table.rowCount()):
            header_item = self.table.verticalHeaderItem(row)
            if not header_item:
                continue

            row_name = header_item.text() if getKeyFromHeaderText else header_item.data(Qt.ItemDataRole.WhatsThisPropertyRole)
            row_type = header_item.data(Qt.ItemDataRole.UserRole)
            

            match row_type:
                case 'combobox':
                    widget = self.table.cellWidget(row, 0)
                    if isinstance(widget, QComboBox):
                        # get current selected key (stored as data)
                        values[row_name] = widget.currentData()

                case 'checkbox':
                    container = self.table.cellWidget(row, 0)
                    if isinstance(container, QWidget):
                        checkbox = container.findChild(QCheckBox)
                        if checkbox:
                            values[row_name] = checkbox.isChecked()

                case _:
                    item = self.table.item(row, 0)
                    if item:
                        try:
                            values[row_name] = float(item.text())
                        except ValueError:
                            values[row_name] = item.text()

        return values
    
    def getFullValuesAsDict(self, getKeyFromHeaderText: bool = True) -> dict:
        """
        Extracts values from the table as a dictionary using the header's user role to determine the type.
        Returns:
            dict: A dictionary with row names as keys and their extracted values.
        """
        result = []
        for row in range(self.table.rowCount()):
            values = {}
            header_item = self.table.verticalHeaderItem(row)
            if not header_item:
                continue

            row_name = header_item.text() if getKeyFromHeaderText else header_item.data(Qt.ItemDataRole.WhatsThisPropertyRole)
            row_type = header_item.data(Qt.ItemDataRole.UserRole)
            
            values['description'] = header_item.text() if getKeyFromHeaderText else header_item.data(Qt.ItemDataRole.WhatsThisPropertyRole)
            values['name'] = row_name
            values['items'] = []
            values['type'] = 'editable'
            
            match row_type:
                case 'combobox':
                    widget = self.table.cellWidget(row, 0)
                    if isinstance(widget, QComboBox):
                        # get current selected key (stored as data)
                        values['type'] = 'combobox'
                        values['defaultValueIndex'] = widget.currentData()
                        values['items'] = [{i: widget.itemText(i)} for i in range(widget.count())]

                case 'checkbox':
                    container = self.table.cellWidget(row, 0)
                    if isinstance(container, QWidget):
                        checkbox = container.findChild(QCheckBox)
                        values['type'] = 'checkbox'
                        
                        if checkbox:
                            values[row_name] = checkbox.isChecked()
                            values['defaultValueIndex'] = checkbox.isChecked()

                case _:
                    item = self.table.item(row, 0)
                    if item:
                        try:
                            values['defaultValueIndex'] = float(item.text())
                        except ValueError:
                            values['defaultValueIndex'] = item.text()
                            
            result.append(values)
        return result

    def overrideDefaultValue(self, groupKey: str, subKey: str, fieldName: str, defaultValue: any):
        """
        Override the default value for a specific group and subkey.
        """
        if not self.data:
            raise ValueError("Data is not set. Use setDataDict() first.")

        wamitconf = self.data.getByGroupAndSub(groupKey, subKey) or []
        for rowDict in wamitconf:
            if rowDict.get('name') == fieldName:
                # Update the default value
                rowDict['defaultValueIndex'] = defaultValue
                break
            
        # Set data with updated
        self.data.setByGroupAndSub(groupKey, subKey, wamitconf)
        return self

    def buildRowsFromDict(self, groupKey: str, subKey: str):
        """
        Build rows automatically from the provided data dictionary based on group and subkey.
        Stores row 'type' metadata in vertical header using Qt.UserRole.
        """
        if not self.data:
            raise ValueError("Data is not set. Use setDataDict() first.")

        # self.resetTable()
        self.table.setRowCount(0)
        
        wamitconf = self.data.getByGroupAndSub(groupKey, subKey) or []
        self.table.setRowCount(len(wamitconf))

        for i, rowDict in enumerate(wamitconf):
            row_name = rowDict.get('name', '')
            row_type = rowDict.get('type', 'default')

            self.table.setRowHeight(i, 40)

            # Set vertical header with name and store type metadata
            header_item = QTableWidgetItem(row_name,)
            header_item.setData(Qt.UserRole, row_type)
            self.table.setVerticalHeaderItem(i, header_item)

            # Set description as label in column 1
            label = QLabel(rowDict.get('description', ''))
            label.setStyleSheet("QLabel { padding-left: 4px; }")
            self.table.setCellWidget(i, 1, label)

            match row_type:
                case 'combobox':
                    combo = QComboBox()
                    for item in rowDict.get('items', []):
                        for key, strValue in item.items():
                            combo.addItem(f'{key}', key)

                    if self.comboCallback:
                        combo.currentIndexChanged.connect(
                            partial(self.comboCallback, i, combo, row_name)
                        )

                    combo.setCurrentIndex(int(rowDict.get('defaultValueIndex', 0)))
                    self.table.setCellWidget(i, 0, combo)

                case 'checkbox':
                    checkbox_label = QLabel('Set as = 0')
                    checkbox = QCheckBox()
                    checkbox.setChecked(False)

                    if self.checkboxCallback:
                        checkbox.stateChanged.connect(
                            partial(self.checkboxCallback, i, checkbox_label, row_name)
                        )

                    checkbox.setChecked(bool(rowDict.get('defaultValueIndex', False)))
                    layout = QHBoxLayout()
                    layout.addWidget(checkbox)
                    layout.addWidget(checkbox_label)
                    layout.setContentsMargins(0, 0, 0, 0)

                    widget = QWidget()
                    widget.setLayout(layout)
                    self.table.setCellWidget(i, 0, widget)

                case _:
                    item = QTableWidgetItem(str(rowDict.get('defaultValueIndex', 0.0)))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, 0, item)

        return self
    
    def buildColumnsFromDict(self, groupKey: str, subKey: str):
        """
        Build rows automatically from the provided data dictionary based on group and subkey.
        Stores row 'type' metadata in vertical header using Qt.UserRole.
        """
        if not self.data:
            raise ValueError("Data is not set. Use setDataDict() first.")

        # self.resetTable()
        self.table.setRowCount(1)
        
        wamitconf = self.data.getByGroupAndSub(groupKey, subKey) or []
        self.table.setColumnCount(len(wamitconf))

        for i, columnDict in enumerate(wamitconf):
            row_name = columnDict.get('name', '')
            row_type = columnDict.get('type', 'default')

            self.table.setRowHeight(i, 40)

            # Set vertical header with name and store type metadata
            header_item = QTableWidgetItem(row_name,)
            header_item.setData(Qt.UserRole, row_type)
            self.table.setHorizontalHeaderItem(i, header_item)

            # Set description as label in column 1
            label = QLabel(columnDict.get('description', ''))
            label.setStyleSheet("QLabel { padding-left: 4px; }")
            self.table.setCellWidget(i, 1, label)

            match row_type:
                case 'combobox':
                    combo = QComboBox()
                    for item in columnDict.get('items', []):
                        for key, strValue in item.items():
                            combo.addItem(f'{key}', key)

                    if self.comboCallback:
                        combo.currentIndexChanged.connect(
                            partial(self.comboCallback, i, combo, row_name)
                        )

                    combo.setCurrentIndex(int(columnDict.get('defaultValueIndex', 0)))
                    self.table.setCellWidget(0, i, combo)

                case 'checkbox':
                    checkbox_label = QLabel('Set as = 0')
                    checkbox = QCheckBox()
                    checkbox.setChecked(False)

                    if self.checkboxCallback:
                        checkbox.stateChanged.connect(
                            partial(self.checkboxCallback, i, checkbox_label, row_name)
                        )

                    checkbox.setChecked(bool(columnDict.get('defaultValueIndex', False)))
                    layout = QHBoxLayout()
                    layout.addWidget(checkbox)
                    layout.addWidget(checkbox_label)
                    layout.setContentsMargins(0, 0, 0, 0)

                    widget = QWidget()
                    widget.setLayout(layout)
                    self.table.setCellWidget(0, i, widget)

                case _:
                    item = QTableWidgetItem(str(columnDict.get('defaultValueIndex', 0.0)))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(0, i, item)

        return self
    
    def buildRowsFromDictCustom(self, groupKey: str, subKey: str):
        """
        Build rows automatically from the provided data dictionary based on group and subkey.
        Stores row 'type' metadata in vertical header using Qt.UserRole.
        """
        if not self.data:
            raise ValueError("Data is not set. Use setDataDict() first.")

        # self.resetTable()
        self.table.setRowCount(0)
        
        wamitconf = self.data.getByGroupAndSub(groupKey, subKey) or []
        self.table.setRowCount(len(wamitconf))

        for i, rowDict in enumerate(wamitconf):
            row_name = rowDict.get('name', '')
            row_type = rowDict.get('type', 'default')
            row_desc = rowDict.get('description', 'default')

            self.table.setRowHeight(i, 40)

            # Set vertical header with name and store type metadata
            header_item = QTableWidgetItem(row_name,)
            header_item.setData(Qt.ItemDataRole.UserRole, row_type)
            header_item.setData(Qt.ItemDataRole.WhatsThisPropertyRole, row_name)
            header_item.setText(row_desc)
            self.table.setVerticalHeaderItem(i, header_item)

            # Set description as label in column 1
            label = QLabel(rowDict.get('description', ''))
            label.setStyleSheet("QLabel { padding-left: 4px; }")
            self.table.setCellWidget(i, 1, label)

            match row_type:
                case 'combobox':
                    combo = QComboBox()
                    for item in rowDict.get('items', []):
                        for key, strValue in item.items():
                            combo.addItem(str(strValue), key)

                    if self.comboCallback:
                        combo.currentIndexChanged.connect(
                            partial(self.comboCallback, i, combo, row_name)
                        )

                    combo.setCurrentIndex(int(rowDict.get('defaultValueIndex', 0)))
                    self.table.setCellWidget(i, 0, combo)

                case 'checkbox':
                    checkbox_label = QLabel('Set as = 0')
                    checkbox = QCheckBox()
                    checkbox.setChecked(False)

                    if self.checkboxCallback:
                        checkbox.stateChanged.connect(
                            partial(self.checkboxCallback, i, checkbox_label, row_name)
                        )

                    checkbox.setChecked(bool(rowDict.get('defaultValueIndex', False)))
                    layout = QHBoxLayout()
                    layout.addWidget(checkbox)
                    layout.addWidget(checkbox_label)
                    layout.setContentsMargins(0, 0, 0, 0)

                    widget = QWidget()
                    widget.setLayout(layout)
                    self.table.setCellWidget(i, 0, widget)

                case _:
                    item = QTableWidgetItem(str(rowDict.get('defaultValueIndex', 0.0)))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, 0, item)

        return self
    
    def loadDataFromNumpy(self, data, is_formatted: bool = False):
        """
        Load a 2D NumPy array or list into the QTableWidget using existing row type metadata.
        
        Each row in `data` corresponds to a row in the table.
        Each cell value is assigned based on the row's type (from Qt.UserRole).

        Args:
            data (np.ndarray | list): A 2D array-like structure.
        """
        # Convert list to numpy array if needed
        if not isinstance(data, np.ndarray):
            try:
                data = np.array(data)
            except Exception as e:
                raise ValueError(f"Failed to convert data to NumPy array: {e}")

        # Ensure it's 2D
        if data.ndim != 2:
            raise ValueError("Input data must be a 2D array")

        rows, cols = data.shape

        if rows != self.table.rowCount():
            raise ValueError(f"Data row count ({rows}) does not match table row count ({self.table.rowCount()})")

        for row in range(rows):
            header_item = self.table.verticalHeaderItem(row)
            if not header_item:
                continue

            row_type = header_item.data(Qt.UserRole)
            value = data[row, 0]  # We assume value column is at 0

            match row_type:
                case 'combobox':
                    widget = self.table.cellWidget(row, 0)
                    if isinstance(widget, QComboBox):
                        
                        # count = widget.count()
                        # print("widgetBox Items:")
                        # for i in range(count):
                        #     text = widget.itemText(i)
                        #     data = widget.itemData(i)
                        #     print(f"  Index {i}: Text = '{text}', Data = {data}")
                                            
                        # Try to set by matching key (data) not the display text
                        index = widget.findData(int(value))
                        print(f'index = {index} is for value = {value}')
                        if index >= 0:
                            widget.setCurrentIndex(index)
                case 'checkbox':
                    container = self.table.cellWidget(row, 0)
                    if isinstance(container, QWidget):
                        checkbox = container.findChild(QCheckBox)
                        if checkbox:
                            checkbox.setChecked(bool(value))
                case _:
                    item = self.table.item(row, 0)
                    if item:
                        item.setText(str(value))


def fromCheckboxDictValueToNumpy(data: dict) -> np.ndarray:
    values = list(data.values())
    numerical_values = [2.0 if val else 0.0 for val in values]
    numpy_array = np.array(numerical_values, dtype=float).reshape(-1, 1)
    return numpy_array

def fromDictValueToNumpy(data: dict) -> np.ndarray:
    values = list(data.values())
    numerical_values = [val for val in values]
    numpy_array = np.array(numerical_values, dtype=float).reshape(-1, 1)
    return numpy_array