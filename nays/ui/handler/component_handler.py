from PySide6.QtWidgets import QTreeWidgetItem, QTreeWidget, QSpinBox, QCheckBox, QComboBox, QLineEdit, QTableWidget, QStyledItemDelegate
from PySide6.QtCore import QTimer, QObject, Signal, SignalInstance, Qt

class ComboBoxDelegate(QStyledItemDelegate):
    """
    Delegate for displaying a QComboBox as the editor for a QTreeWidget item.
    """
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = items

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.addItems(self.items)
        return combo

    def setEditorData(self, editor, index):
        value = index.data()
        i = editor.findText(value)
        if i >= 0:
            editor.setCurrentIndex(i)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText())


class TreeHandler(QObject):
    currentItemChanged = Signal(QTreeWidgetItem)
    currentParentItemChanged = Signal(QTreeWidgetItem)

    def __init__(self, treeWidget: QTreeWidget, parent=None):
        super().__init__(parent)
        self.treeWidget = treeWidget
        self.treeWidget.currentItemChanged.connect(self.__onCurrentItemChanged)
        self.allowEmit = True

    def setComboBoxDelegate(self, column: int, items: list[str]):
        """
        Set a ComboBoxDelegate for a specific column in the tree widget.
        """
        delegate = ComboBoxDelegate(items, self.treeWidget)
        self.treeWidget.setItemDelegateForColumn(column, delegate)

    def setCurrentItem(self, item: QTreeWidgetItem, allowEmit: bool = True):
        oldValue = self.allowEmit
        self.allowEmit = allowEmit
        self.treeWidget.setCurrentItem(item)
        self.allowEmit = oldValue

    def clearItems(self, allowEmit: bool = True):
        oldValue = self.allowEmit
        self.allowEmit = allowEmit
        self.treeWidget.clear()
        self.allowEmit = oldValue

    def addItemTree(self, item: QTreeWidgetItem, parent: QTreeWidgetItem = None, allowEmit: bool = True):
        if parent is not None:
            parent.addChild(item)
            parent.setExpanded(True)
        else:
            self.treeWidget.addTopLevelItem(item)

    def getTopItemCount(self):
        return self.treeWidget.topLevelItemCount()

    def loadFromList(self, data: list[any]):
        _topLevelItem = []
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            _topLevelItem.append(item)

    def __onCurrentItemChanged(self, item: QTreeWidgetItem):
        if item:
            # update also parent
            if item.parent() is not None:
                if self.allowEmit:
                    self.currentParentItemChanged.emit(item.parent())

            # main update
            if self.allowEmit:
                self.currentItemChanged.emit(item)

class SpinboxHandler(QObject):
    valueChanged = Signal(int)
    
    def __init__(self, spinbox: QSpinBox, parent=None):
        super().__init__(parent)
        self.spinbox = spinbox
        self.spinbox.valueChanged.connect(self.__onValueChanged)
        self.allowEmit = True
        
    def setValue(self, value: int, allowEmit: bool = True):
        oldValue = self.allowEmit
        self.allowEmit = allowEmit
        self.spinbox.setValue(value)
        self.allowEmit = oldValue
        
    def getValue(self):
        return self.spinbox.value()
        
    def __onValueChanged(self, data: int): 
        if self.allowEmit:
            self.valueChanged.emit(data)

class CheckboxHandler(QObject):
    stateChanged = Signal(bool)
    
    def __init__(self, checkbox: QCheckBox, parent=None):
        super().__init__(parent)
        self.checkbox = checkbox
        self.checkbox.checkStateChanged.connect(self.__onCheckStateChanged)
        self.allowEmit = True
        
    def setState(self, state: bool, allowEmit: bool = True):
        _stateCheck = Qt.CheckState.Checked if state else Qt.CheckState.Unchecked
        oldValue = self.allowEmit
        self.allowEmit = allowEmit
        self.checkbox.setCheckState(_stateCheck)
        self.allowEmit = oldValue
        
    def getState(self):
        return self.checkbox.isChecked()
        
    def __onCheckStateChanged(self, data: Qt.CheckState): 
        _data = data == Qt.CheckState.Checked
        if self.allowEmit:
            self.stateChanged.emit(_data)
        

class ComboboxHandler(QObject):
    textChanged = Signal(str)
    indexChanged = Signal(int)
    dataChanged = Signal(object)
    
    def __init__(self, combobox: QComboBox, parent=None):
        super().__init__(parent)
        self.combobox = combobox
        self.allowEmit = True
        self.combobox.currentTextChanged.connect(self.__onTextChanged)
        self.combobox.currentIndexChanged.connect(self.__onIndexChanged)
        
    def addItem(self, text: str, data: any = None):
        oldValue = self.allowEmit
        self.allowEmit = False
        self.combobox.addItem(text, data)
        self.allowEmit = oldValue
    
    def setText(self, text: str, allowEmit: bool = True):
        oldValue = self.allowEmit
        self.allowEmit = allowEmit
        self.combobox.setCurrentText(text)
        self.allowEmit = oldValue
        
    def setIndex(self, index: int, allowEmit: bool = True):
        oldValue = self.allowEmit
        self.allowEmit = allowEmit
        self.combobox.setCurrentIndex(index)
        self.allowEmit = oldValue
        
    def getComboData(self) -> list[dict]:
        """
        Get all data items collected in the comboHullSelection.
        
        Returns:
            list[dict]: List of dictionaries containing text and data for each item
        """
        allItems = []
        for index in range(self.combobox.count()):
            text = self.combobox.itemText(index)
            data = self.combobox.itemData(index)
            allItems.append({
                'index': index,
                'text': text,
                'data': data
            })
        return allItems
    
    def __onTextChanged(self, data: str):
        if self.allowEmit:
            self.textChanged.emit(data)
            self.dataChanged.emit(self.combobox.currentData(Qt.ItemDataRole.UserRole))
        
    def __onIndexChanged(self, data: int):
        if self.allowEmit:
            self.indexChanged.emit(data)
            self.dataChanged.emit(self.combobox.currentData(Qt.ItemDataRole.UserRole))
            
        

class DebouncedLineEditHandler(QObject):
    debouncedTextChanged = Signal(str)

    def __init__(self, line_edit: QLineEdit, debounce_ms=300, parent=None):
        super().__init__(parent)
        self.line_edit = line_edit
        self.debounce_timer = QTimer(self)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._emit_debounced_text)
        self.line_edit.textChanged.connect(self._on_text_changed)
        self.debounce_interval = debounce_ms
        self.shouldEmit = True

    def setText(self, text: str, shouldEmit=True):
        oldValue = self.shouldEmit
        self.shouldEmit = shouldEmit
        self.line_edit.setText(text)
        self.shouldEmit = oldValue
        
    def _on_text_changed(self, text):
        if self.shouldEmit:
            self.debounce_timer.start(self.debounce_interval)

    def _emit_debounced_text(self):
        if self.shouldEmit:
            self.debouncedTextChanged.emit(self.line_edit.text())
            