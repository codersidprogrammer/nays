"""
Table Editor Component - High-level interface for creating editable tables

This module provides a convenient createTableEditor() function to create reusable,
editable table components with support for:
- List of dictionaries
- Numpy arrays
- Mixed data types
- Custom column configurations
- Data validation
- Export capabilities
- Toolbar with edit, undo, filter, copy, paste, refresh actions
- Status bar with row/column information
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from copy import deepcopy

from PySide6.QtWidgets import (
    QTableView, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QMessageBox, QToolBar, QStatusBar,
    QLineEdit, QComboBox, QApplication
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QAction, QIcon

from nays.ui.handler.table_view_handler import TableViewHandler


class TableEditorWidget(QWidget):
    """
    A complete table editor widget with toolbar buttons for common operations.
    
    Features:
    - Professional toolbar with edit, undo, filter, copy, paste, refresh actions
    - Save/Cancel buttons with confirmation dialogs
    - Status bar showing row/column information
    - Data display and editing
    - Add/Delete/Filter row functionality
    - Undo/Redo support
    - Copy/Paste support
    - Data export (to list of dicts, numpy array)
    - Custom styling
    - Designed for use as subwindow
    - Signals for data save callbacks
    """
    
    # Signals for callbacks
    dataSaved = Signal(dict)  # Emitted when data is saved
    operationCancelled = Signal()  # Emitted when operation is cancelled
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Table Editor")
        self.resize(1000, 600)
        
        # Data history for undo/redo
        self.undoStack: List[List[Dict[str, Any]]] = []
        self.redoStack: List[List[Dict[str, Any]]] = []
        self.maxUndoSteps = 20
        
        # Clipboard for copy/paste
        self.clipboard: Optional[List[Dict[str, Any]]] = None
        
        # Filter state
        self.filter_active = False
        self.original_data = None
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # ===== TOOLBAR =====
        self.toolbar = QToolBar("Editor Toolbar")
        self.toolbar.setIconSize(QSize(24, 24))
        self.toolbar.setMovable(False)
        layout.addWidget(self.toolbar)
        
        # Edit button
        self.editBtn = QAction("Edit", self)
        self.editBtn.setToolTip("Edit selected cell (double-click to edit)")
        self.editBtn.triggered.connect(self._onEdit)
        self.toolbar.addAction(self.editBtn)
        
        # Undo button
        self.undoBtn = QAction("Undo", self)
        self.undoBtn.setToolTip("Undo last action (Ctrl+Z)")
        self.undoBtn.triggered.connect(self._onUndo)
        self.undoBtn.setEnabled(False)
        self.toolbar.addAction(self.undoBtn)
        
        # Redo button
        self.redoBtn = QAction("Redo", self)
        self.redoBtn.setToolTip("Redo last undone action (Ctrl+Y)")
        self.redoBtn.triggered.connect(self._onRedo)
        self.redoBtn.setEnabled(False)
        self.toolbar.addAction(self.redoBtn)
        
        self.toolbar.addSeparator()
        
        # Copy button
        self.copyBtn = QAction("Copy", self)
        self.copyBtn.setToolTip("Copy selected rows (Ctrl+C)")
        self.copyBtn.triggered.connect(self._onCopy)
        self.toolbar.addAction(self.copyBtn)
        
        # Paste button
        self.pasteBtn = QAction("Paste", self)
        self.pasteBtn.setToolTip("Paste rows (Ctrl+V)")
        self.pasteBtn.triggered.connect(self._onPaste)
        self.pasteBtn.setEnabled(False)
        self.toolbar.addAction(self.pasteBtn)
        
        self.toolbar.addSeparator()
        
        # Filter button
        self.filterBtn = QAction("Filter", self)
        self.filterBtn.setToolTip("Filter table by column value")
        self.filterBtn.triggered.connect(self._onFilter)
        self.toolbar.addAction(self.filterBtn)
        
        # Refresh button
        self.refreshBtn = QAction("Refresh", self)
        self.refreshBtn.setToolTip("Refresh table view")
        self.refreshBtn.triggered.connect(self._onRefresh)
        self.toolbar.addAction(self.refreshBtn)
        
        self.toolbar.addSeparator()
        
        # Add Row button
        self.addRowBtn = QAction("Add Row", self)
        self.addRowBtn.setToolTip("Add new row")
        self.addRowBtn.triggered.connect(self._onAddRow)
        self.toolbar.addAction(self.addRowBtn)
        
        # Delete Row button
        self.deleteRowBtn = QAction("Delete Row", self)
        self.deleteRowBtn.setToolTip("Delete selected row")
        self.deleteRowBtn.triggered.connect(self._onDeleteRow)
        self.toolbar.addAction(self.deleteRowBtn)
        
        # Clear All button
        self.clearBtn = QAction("Clear All", self)
        self.clearBtn.setToolTip("Clear all rows")
        self.clearBtn.triggered.connect(self._onClear)
        self.toolbar.addAction(self.clearBtn)
        
        self.toolbar.addSeparator()
        
        # Export buttons
        self.exportDictBtn = QAction("Export as List", self)
        self.exportDictBtn.setToolTip("Export data as list of dictionaries")
        self.exportDictBtn.triggered.connect(self._onExportDict)
        self.toolbar.addAction(self.exportDictBtn)
        
        self.exportNumpyBtn = QAction("Export as NumPy", self)
        self.exportNumpyBtn.setToolTip("Export data as numpy array")
        self.exportNumpyBtn.triggered.connect(self._onExportNumpy)
        self.toolbar.addAction(self.exportNumpyBtn)
        
        self.toolbar.addSeparator()
        
        # Save button
        self.saveBtn = QAction("Save", self)
        self.saveBtn.setToolTip("Save changes and emit callback (Ctrl+S)")
        self.saveBtn.triggered.connect(self._onSave)
        self.toolbar.addAction(self.saveBtn)
        
        # Cancel button
        self.cancelBtn = QAction("Cancel", self)
        self.cancelBtn.setToolTip("Cancel changes and revert to original")
        self.cancelBtn.triggered.connect(self._onCancel)
        self.toolbar.addAction(self.cancelBtn)
        
        # ===== TABLE VIEW =====
        self.tableView = QTableView()
        self.tableView.setAlternatingRowColors(False)
        self.tableView.setShowGrid(True)
        layout.addWidget(self.tableView)
        
        # ===== STATUS BAR =====
        self.statusBar = QStatusBar()
        self.statusBar.setMaximumHeight(24)
        layout.addWidget(self.statusBar)
        
        # Status label
        self.statusLabel = QLabel("Ready")
        self.statusBar.addWidget(self.statusLabel)
        
        # Row/Column info
        self.infoLabel = QLabel("Rows: 0 | Cols: 0")
        self.statusBar.addPermanentWidget(self.infoLabel)
        
        # Handler
        self.handler = None
        
        # Connect keyboard shortcuts
        self.setFocusPolicy(Qt.StrongFocus)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
            self._onUndo()
        elif event.key() == Qt.Key_Y and event.modifiers() == Qt.ControlModifier:
            self._onRedo()
        elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            self._onCopy()
        elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            self._onPaste()
        elif event.key() == Qt.Key_S and event.modifiers() == Qt.ControlModifier:
            event.accept()
            self._onSave()
        else:
            super().keyPressEvent(event)
    
    def _saveState(self):
        """Save current state for undo."""
        if self.handler:
            # Clear redo stack when new action is performed
            self.redoStack.clear()
            self.redoBtn.setEnabled(False)
            
            # Save state
            current_data = deepcopy(self.handler.getData())
            self.undoStack.append(current_data)
            
            # Limit undo stack size
            if len(self.undoStack) > self.maxUndoSteps:
                self.undoStack.pop(0)
            
            self.undoBtn.setEnabled(len(self.undoStack) > 0)
    
    def _onEdit(self):
        """Edit selected cell."""
        selected = self.tableView.currentIndex()
        if selected.isValid():
            self.tableView.edit(selected)
            self._updateStatus("Editing...")
    
    def _onUndo(self):
        """Undo last action."""
        if not self.handler or not self.undoStack:
            return
        
        # Save current state to redo stack
        current_data = deepcopy(self.handler.getData())
        self.redoStack.append(current_data)
        
        # Restore previous state
        previous_data = self.undoStack.pop()
        self.handler.loadData(previous_data, shouldEmit=False)
        
        # Update UI
        self.undoBtn.setEnabled(len(self.undoStack) > 0)
        self.redoBtn.setEnabled(len(self.redoStack) > 0)
        self._updateStatus("Undone")
        self._updateInfo()
    
    def _onRedo(self):
        """Redo last undone action."""
        if not self.handler or not self.redoStack:
            return
        
        # Save current state to undo stack
        current_data = deepcopy(self.handler.getData())
        self.undoStack.append(current_data)
        
        # Restore next state
        next_data = self.redoStack.pop()
        self.handler.loadData(next_data, shouldEmit=False)
        
        # Update UI
        self.undoBtn.setEnabled(len(self.undoStack) > 0)
        self.redoBtn.setEnabled(len(self.redoStack) > 0)
        self._updateStatus("Redone")
        self._updateInfo()
    
    def _onCopy(self):
        """Copy selected rows."""
        if not self.handler:
            return
        
        selected = self.tableView.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select rows to copy")
            return
        
        # Get unique rows
        rows = sorted(set(idx.row() for idx in selected))
        data = self.handler.getData()
        
        self.clipboard = [deepcopy(data[row]) for row in rows if row < len(data)]
        self.pasteBtn.setEnabled(bool(self.clipboard))
        self._updateStatus(f"Copied {len(self.clipboard)} row(s)")
    
    def _onPaste(self):
        """Paste rows from clipboard."""
        if not self.handler or not self.clipboard:
            QMessageBox.warning(self, "Warning", "Clipboard is empty")
            return
        
        # Save state for undo
        self._saveState()
        
        # Add rows from clipboard
        for row_data in deepcopy(self.clipboard):
            self.handler.addRow(row_data)
        
        self._updateStatus(f"Pasted {len(self.clipboard)} row(s)")
        self._updateInfo()
    
    def _onFilter(self):
        """Show filter dialog."""
        if not self.handler or self.handler.rowCount == 0:
            QMessageBox.warning(self, "Warning", "No data to filter")
            return
        
        # Create simple filter dialog
        from PySide6.QtWidgets import QDialog, QComboBox, QLineEdit, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Filter")
        dialog.setGeometry(self.x() + 100, self.y() + 100, 400, 150)
        
        layout = QVBoxLayout(dialog)
        
        # Column selector
        col_layout = QHBoxLayout()
        col_layout.addWidget(QLabel("Column:"))
        col_combo = QComboBox()
        col_combo.addItems(self.handler.model.headers)
        col_layout.addWidget(col_combo)
        layout.addLayout(col_layout)
        
        # Filter value
        val_layout = QHBoxLayout()
        val_layout.addWidget(QLabel("Contains:"))
        val_input = QLineEdit()
        val_layout.addWidget(val_input)
        layout.addLayout(val_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        def apply_filter():
            col_idx = col_combo.currentIndex()
            filter_text = val_input.text().lower()
            
            if not filter_text:
                self._onRefresh()
                dialog.close()
                return
            
            # Save original data
            if not self.filter_active:
                self.original_data = deepcopy(self.handler.getData())
            
            # Filter rows
            all_rows = self.original_data or self.handler.getData()
            key = self.handler.model.columnKeys[col_idx]
            
            filtered = [row for row in all_rows 
                       if filter_text in str(row.get(key, '')).lower()]
            
            self.handler.loadData(filtered, shouldEmit=False)
            self.filter_active = True
            
            self._updateStatus(f"Filtered: {len(filtered)} of {len(all_rows)} rows")
            self._updateInfo()
            dialog.close()
        
        applyBtn = QPushButton("Apply")
        applyBtn.clicked.connect(apply_filter)
        btn_layout.addWidget(applyBtn)
        
        resetBtn = QPushButton("Reset")
        resetBtn.clicked.connect(lambda: (self._onRefresh(), dialog.close()))
        btn_layout.addWidget(resetBtn)
        
        layout.addLayout(btn_layout)
        dialog.exec()
    
    def _onRefresh(self):
        """Refresh table to original data."""
        if self.filter_active and self.original_data:
            self.handler.loadData(self.original_data, shouldEmit=False)
            self.filter_active = False
            self._updateStatus("Filter cleared")
            self._updateInfo()
    
    def _onAddRow(self):
        """Add a new row to the table."""
        if self.handler:
            self._saveState()
            self.handler.addRow()
            self._updateStatus(f"Row added | Rows: {self.handler.rowCount}")
            self._updateInfo()
    
    def _onDeleteRow(self):
        """Delete selected row from the table."""
        if self.handler:
            selected = self.handler.getSelectedRow()
            if selected >= 0:
                self._saveState()
                self.handler.deleteRow(selected)
                self._updateStatus(f"Row deleted | Rows: {self.handler.rowCount}")
                self._updateInfo()
            else:
                QMessageBox.warning(self, "Warning", "Please select a row to delete")
    
    def _onClear(self):
        """Clear all rows from the table."""
        if self.handler:
            reply = QMessageBox.question(
                self, "Confirm", "Clear all data?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self._saveState()
                self.handler.clearAll()
                self._updateStatus("Table cleared")
                self._updateInfo()
    
    def _onExportDict(self):
        """Export table data as list of dictionaries."""
        if self.handler:
            data = self.handler.getData()
            QMessageBox.information(
                self, "Export Successful",
                f"Exported {len(data)} rows as list of dictionaries.\n\n"
                f"Data available via getDataAsDict() method."
            )
    
    def _onExportNumpy(self):
        """Export table data as numpy array."""
        if self.handler:
            try:
                array = self.handler.getAllAsNumpy()
                QMessageBox.information(
                    self, "Export Successful",
                    f"Exported {len(array)} rows as numpy array.\n"
                    f"Shape: {array.shape}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", str(e))
    
    def _onSave(self):
        """Save current data and emit callback."""
        if not self.handler:
            return
        
        # Ask for confirmation
        reply = QMessageBox.question(
            self, "Confirm Save",
            "Save changes and emit callback?\n\n"
            "This will notify any connected listeners about the data changes.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            # Get data in both formats
            data_dict = self.handler.getData()
            data_numpy = self.handler.getAllAsNumpy()
            
            # Emit signal with data
            callback_data = {
                'dict': data_dict,
                'numpy': data_numpy,
                'rowCount': len(data_dict),
                'colCount': self.handler.columnCount,
                'headers': self.handler.model.headers
            }
            
            self.dataSaved.emit(callback_data)
            
            # Clear undo/redo stacks after successful save
            self.undoStack.clear()
            self.redoStack.clear()
            self.undoBtn.setEnabled(False)
            self.redoBtn.setEnabled(False)
            
            self._updateStatus(f"✓ Saved {len(data_dict)} rows")
            
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Error saving data: {str(e)}")
    
    def _onCancel(self):
        """Cancel current changes."""
        if not self.handler:
            return
        
        # Ask for confirmation only if there are unsaved changes
        has_changes = len(self.undoStack) > 0 or len(self.redoStack) > 0
        
        if has_changes:
            reply = QMessageBox.question(
                self, "Confirm Cancel",
                "Discard all changes and revert to last saved state?\n\n"
                "This action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
        
        # Clear undo/redo stacks
        self.undoStack.clear()
        self.redoStack.clear()
        self.undoBtn.setEnabled(False)
        self.redoBtn.setEnabled(False)
        
        # Emit cancel signal
        self.operationCancelled.emit()
        
        self._updateStatus("Operation cancelled")
    
    def _updateStatus(self, message: str):
        """Update status label."""
        self.statusLabel.setText(message)
    
    def _updateInfo(self):
        """Update row/column info."""
        if self.handler:
            rows = self.handler.rowCount
            cols = self.handler.columnCount
            self.infoLabel.setText(f"Rows: {rows} | Cols: {cols}")
    
    def getDataAsDict(self) -> List[Dict[str, Any]]:
        """Get table data as list of dictionaries."""
        return self.handler.getData() if self.handler else []
    
    def getDataAsNumpy(self) -> np.ndarray:
        """Get table data as numpy array."""
        return self.handler.getAllAsNumpy() if self.handler else np.array([])
    
    def setData(self, data: Union[List[Dict[str, Any]], np.ndarray]):
        """Set table data."""
        if self.handler:
            if isinstance(data, np.ndarray):
                # Numpy array - convert to list of dicts
                rows = []
                for row_vals in data:
                    row_dict = {header: val for header, val in zip(
                        self.handler.model.headers, row_vals)}
                    rows.append(row_dict)
                self.handler.loadData(rows)
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                # List of dicts
                self.handler.loadData(data)
            self._updateStatus(f"Data loaded | Rows: {self.handler.rowCount}")
            self._updateInfo()
            self.undoStack.clear()
            self.redoStack.clear()



def createTableEditor(
    headers: List[str],
    data: Optional[Union[List[Dict[str, Any]], np.ndarray]] = None,
    column_types: Optional[Dict[str, str]] = None,
    combo_options: Optional[Dict[str, List[str]]] = None,
    enable_toolbar: bool = True,
    apply_style: bool = True,
    dark_mode: bool = False,
    parent=None
) -> TableEditorWidget:
    """
    Create a reusable table editor component with professional UI.
    
    This function creates a fully-featured editable table widget suitable for use as
    a subwindow or modal dialog. Includes toolbar with edit, undo, filter, copy, paste,
    and refresh actions, plus status bar for information display.
    
    Features:
    - Professional toolbar with common actions
    - Status bar showing row/column count
    - Undo/Redo support (Ctrl+Z / Ctrl+Y)
    - Copy/Paste support (Ctrl+C / Ctrl+V)
    - Filter functionality with restore
    - Data export capabilities
    - Full keyboard shortcuts
    - Light and dark themes
    
    Args:
        headers (List[str]): Column headers/names that define the table structure.
            Example: ['Name', 'Age', 'Email', 'Active']
        
        data (Optional[Union[List[Dict[str, Any]], np.ndarray]]): Initial data to populate the table.
            Can be:
            - List of dictionaries: [{'name': 'John', 'age': 30}, {'name': 'Jane', 'age': 25}]
            - Numpy 2D array: np.array([['John', 30], ['Jane', 25]])
            - None: Creates empty table
        
        column_types (Optional[Dict[str, str]]): Column data types.
            Keys: column names (from headers)
            Values: 'text', 'checkbox', 'combo'
            Example: {'Active': 'checkbox', 'Status': 'combo'}
        
        combo_options (Optional[Dict[str, List[str]]]): ComboBox options for combo columns.
            Keys: column names
            Values: list of options
            Example: {'Status': ['Active', 'Inactive', 'Pending']}
        
        enable_toolbar (bool): Show toolbar with actions (default: True)
        
        apply_style (bool): Apply default professional styling (default: True)
        
        dark_mode (bool): Use dark theme (default: False). Only applies if apply_style=True
        
        parent: Parent widget (typically for use as subwindow)
    
    Returns:
        TableEditorWidget: Fully-featured table editor widget
        
    Toolbar Actions:
        - Edit: Edit the selected cell
        - Undo: Undo last action (Ctrl+Z)
        - Redo: Redo last undone action (Ctrl+Y)
        - Copy: Copy selected rows (Ctrl+C)
        - Paste: Paste rows from clipboard (Ctrl+V)
        - Filter: Filter table by column value
        - Refresh: Refresh and clear filter
        - Add Row: Add new empty row
        - Delete Row: Delete selected row
        - Clear All: Clear all data
        - Export as List: Export as list of dicts
        - Export as NumPy: Export as numpy array
        - Save: Save changes with callback (Ctrl+S)
        - Cancel: Cancel changes and revert
        
    Keyboard Shortcuts:
        - Ctrl+Z: Undo
        - Ctrl+Y: Redo
        - Ctrl+C: Copy
        - Ctrl+V: Paste
        - Ctrl+S: Save
        - Double-click: Edit cell
    
    Signals (Callbacks):
        - dataSaved: Emitted when data is saved
          Carries: {'dict': list_of_dicts, 'numpy': numpy_array, 'rowCount': int, 'colCount': int, 'headers': list}
        - operationCancelled: Emitted when operation is cancelled
        
    Examples:
        # Simple table with list of dicts
        >>> data = [
        ...     {'name': 'Alice', 'age': 28, 'email': 'alice@example.com'},
        ...     {'name': 'Bob', 'age': 35, 'email': 'bob@example.com'},
        ... ]
        >>> table = createTableEditor(
        ...     headers=['name', 'age', 'email'],
        ...     data=data
        ... )
        >>> table.show()
        
        # Table with numpy array and column types
        >>> import numpy as np
        >>> data = np.array([
        ...     ['John', 30, True],
        ...     ['Jane', 25, False],
        ... ])
        >>> table = createTableEditor(
        ...     headers=['Name', 'Age', 'Active'],
        ...     data=data,
        ...     column_types={'Active': 'checkbox'}
        ... )
        >>> table.show()
        
        # Table with combobox columns
        >>> data = [
        ...     {'name': 'Product A', 'status': 'Active'},
        ...     {'name': 'Product B', 'status': 'Inactive'},
        ... ]
        >>> table = createTableEditor(
        ...     headers=['name', 'status'],
        ...     data=data,
        ...     column_types={'status': 'combo'},
        ...     combo_options={'status': ['Active', 'Inactive', 'Pending']}
        ... )
        >>> table.show()
        
        # As subwindow in MDI application
        >>> from PySide6.QtWidgets import QMainWindow, QMdiArea
        >>> main = QMainWindow()
        >>> mdi = QMdiArea()
        >>> main.setCentralWidget(mdi)
        >>> editor = createTableEditor(headers=['Name', 'Email'], data=data)
        >>> sub = mdi.addSubWindow(editor)
        >>> sub.show()
        
        # Export data after editing
        >>> edited_data = table.getDataAsDict()
        >>> edited_array = table.getDataAsNumpy()
    """
    
    # Validate headers
    if not headers or not isinstance(headers, list):
        raise ValueError("headers must be a non-empty list of strings")
    
    # Create widget
    editor = TableEditorWidget(parent)
    
    # Create table view and handler
    table_view = editor.tableView
    handler = TableViewHandler(table_view, headers, applyDefaultStyle=False)
    editor.handler = handler
    
    # Apply styling if requested
    if apply_style:
        if dark_mode:
            handler.applyDarkStyle()
        else:
            handler.applyStyle()
    
    # Setup columns with types
    column_types = column_types or {}
    column_config = []
    
    for header in headers:
        cell_type = column_types.get(header, 'text')
        column_config.append((header, cell_type))
    
    handler.setupColumns(column_config)
    
    # Setup combobox options
    combo_options = combo_options or {}
    for i, header in enumerate(headers):
        if header in combo_options:
            handler.setColumnComboItems(i, combo_options[header])
    
    # Load data if provided
    if data is not None:
        if isinstance(data, np.ndarray):
            # Numpy array - convert to list of dicts
            rows = []
            for row_vals in data:
                row_dict = {header: val for header, val in zip(headers, row_vals)}
                rows.append(row_dict)
            handler.loadData(rows)
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            # List of dicts
            handler.loadData(data)
        else:
            raise ValueError(
                "data must be either a numpy 2D array or a list of dictionaries"
            )
    
    # Update status and info
    editor._updateStatus("Ready")
    editor._updateInfo()
    
    # Hide toolbar if not requested
    if not enable_toolbar:
        editor.toolbar.setVisible(False)
    
    return editor


def createTableEditorEmbedded(
    table_view: 'QTableView' = None,
    headers: List[str] = None,
    config_data: List[Dict[str, Any]] = None,
    on_save: Optional[callable] = None,
    on_cancel: Optional[callable] = None,
    apply_dark_style: bool = True,
    combo_display_mode: str = "both",
    parent=None
) -> TableEditorWidget:
    """
    Create a standalone table editor widget with config-based data loading.
    
    This function creates an independent table editor window that can be
    opened alongside your existing UI. Your original QTableView stays in
    your UI layout unchanged.
    
    Args:
        table_view (QTableView, optional): Reference to existing table (for compatibility, not used)
        headers (List[str]): Column headers
        config_data (List[Dict[str, Any]]): Configuration data for loadFromConfigAsColumns()
        on_save (Optional[callable]): Callback when data is saved
        on_cancel (Optional[callable]): Callback when operation is cancelled
        apply_dark_style (bool): Apply dark theme (default: True)
        combo_display_mode (str): How to display combo values - "key", "value", or "both"
        parent: Parent widget
    
    Returns:
        TableEditorWidget that can be shown as a separate window
    
    Usage Example:
        # Your UI has this (and it stays there):
        self.tableLineElementDefinition = QTableView(self.tab_15)
        self.verticalLayout_16.addWidget(self.tableLineElementDefinition)
        
        # To open a separate editor window:
        def on_save(data):
            self.vm.onLineElementDefinitionChanged(data['dict'])
        
        editor = createTableEditorEmbedded(
            headers=[...],
            config_data=_data,
            on_save=on_save,
            apply_dark_style=True
        )
        
        # Show as separate window
        editor.setWindowTitle("Line Element Definition Editor")
        editor.resize(900, 600)
        editor.show()
    
    """
    # Create the editor widget
    editor = TableEditorWidget(parent)
    
    # Use the editor's built-in table view
    # The table_view parameter lets you keep your original widget in the UI
    # The editor creates its own synchronized table view
    actual_table_view = editor.tableView
    
    # Create and configure handler with the editor's table view
    handler = TableViewHandler(
        actual_table_view,
        headers,
        applyDefaultStyle=True
    )
    editor.handler = handler
    
    # Apply styling
    if apply_dark_style:
        handler.applyDarkStyle()
    
    # Load data from config
    handler.loadFromConfigAsColumns(
        config_data,
        addDefaultRow=True,
        comboDisplayMode=combo_display_mode
    )
    
    # Update editor status
    editor._updateStatus("Ready")
    editor._updateInfo()
    
    # Connect callbacks
    if on_save:
        editor.dataSaved.connect(on_save)
    if on_cancel:
        editor.operationCancelled.connect(on_cancel)
    
    return editor



def createTableEditorWithCallback(
    headers: List[str],
    data: Optional[Union[List[Dict[str, Any]], np.ndarray]] = None,
    column_types: Optional[Dict[str, str]] = None,
    combo_options: Optional[Dict[str, List[str]]] = None,
    on_save: Optional[callable] = None,
    on_cancel: Optional[callable] = None,
    apply_style: bool = True,
    dark_mode: bool = False,
    parent=None
) -> TableEditorWidget:
    """
    Create a table editor with pre-connected save/cancel callbacks.
    
    This is a convenience function that wraps createTableEditor() and automatically
    connects the save and cancel signals to callback functions.
    
    Args:
        headers: Column headers
        data: Initial data (list of dicts or numpy array)
        column_types: Column type definitions
        combo_options: ComboBox options
        on_save: Callback function when data is saved
                Receives dict: {'dict': data_list, 'numpy': data_array, ...}
        on_cancel: Callback function when operation is cancelled
        apply_style: Apply default styling
        dark_mode: Use dark theme
        parent: Parent widget
    
    Returns:
        TableEditorWidget with callbacks connected
    
    Example:
        def handle_save(data):
            print(f"Data saved with {data['rowCount']} rows")
            data_list = data['dict']
            data_array = data['numpy']
            # Process the data
        
        def handle_cancel():
            print("Operation cancelled")
        
        editor = createTableEditorWithCallback(
            headers=['Name', 'Age'],
            data=[{'Name': 'Alice', 'Age': 28}],
            on_save=handle_save,
            on_cancel=handle_cancel
        )
        editor.show()
    
    """
    
    editor = createTableEditor(
        headers=headers,
        data=data,
        column_types=column_types,
        combo_options=combo_options,
        enable_toolbar=True,
        apply_style=apply_style,
        dark_mode=dark_mode,
        parent=parent
    )
    
    # Connect callbacks if provided
    if on_save:
        editor.dataSaved.connect(on_save)
    if on_cancel:
        editor.operationCancelled.connect(on_cancel)
    
    return editor
