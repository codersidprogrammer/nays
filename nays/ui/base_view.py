import logging

from colorama import Fore, Style, init
from PySide6.QtWidgets import QDialog, QMessageBox, QWidget

init(autoreset=True)


class BaseView:
    def __init__(self, parent=None, routeData: dict[str, any] = {}):
        self.parent = parent
        self.routeParams = routeData
        self.view = self
        self.logger = None  # Will be injected from RootModule
