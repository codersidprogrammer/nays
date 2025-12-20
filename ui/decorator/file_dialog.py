from PySide6.QtWidgets import QLineEdit, QFileDialog
from functools import wraps

def OnFileDialog(target=None, filter='All Files (*);;Exe file (*.exe)'):
    def decorator(func):
        @wraps(func)
        def wrapper(self):
            file_path, _ = QFileDialog.getOpenFileName(self, 'Select file', '', filter)
            if file_path:
                if target is not None:
                    line_edit = target(self)
                    line_edit.setText(file_path)
                return func(self, file_path)
            return None
        return wrapper
    return decorator

def OnFolderDialog(target):
    def decorator(func):
        @wraps(func)
        def wrapper(self):
            folder_path = QFileDialog.getExistingDirectory(None, 'Select Folder')
            if folder_path:
                if target is not None:
                    line_edit = target(self)
                    line_edit.setText(folder_path)
                return func(self, folder_path)
            return None
        return wrapper
    return decorator

def OnSaveDialog(target, filter='All Files (*);;Exe file (*.exe)'):
    def decorator(func):
        @wraps(func)
        def wrapper(self):
            # Open save file dialog
            file_path, _ = QFileDialog.getSaveFileName(
                None,  # Or self if you want parent
                'Save File',
                '',  # Start directory
                filter  # File filter
            )
            
            if file_path:  # If user didn't cancel
                # Get the target widget and set text
                widget = target(self)
                widget.setText(file_path)
                
                # Call the original function with file_path
                return func(self, file_path)
            return None
        return wrapper
    return decorator

