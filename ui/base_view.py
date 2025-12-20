import logging
from PySide6.QtWidgets import QWidget, QDialog, QMessageBox
from colorama import Fore, Style, init

init(autoreset=True)
class BaseView:
    def __init__(self, parent=None, routeData: dict[str, any] = {}):
        self.parent = parent
        self.routeParams = routeData
        self.view = self
        self.logger = None  # Will be injected from RootModule