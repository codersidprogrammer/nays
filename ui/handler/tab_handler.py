from PySide6.QtWidgets import (
    QWidget, QTabWidget, QPushButton, QLabel,
    QHBoxLayout, QVBoxLayout, QToolButton, QStyle, QApplication
)
from PySide6.QtCore import Qt


class TabWidgetHandler:
    def __init__(self, tab_widget: QTabWidget):
        self.tab_widget = tab_widget
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.closeTab)

    def addTab(self, content_widget: QWidget, title: str):
        index = self.tab_widget.addTab(content_widget, title)
        self.tab_widget.setCurrentIndex(index)
        return self  # Fluent API style

    def closeTab(self, index: int):
        self.tab_widget.removeTab(index)
        return self

    def clearTabs(self):
        while self.tab_widget.count() > 0:
            self.tab_widget.removeTab(0)
        return self

    def setCloseable(self, closable: bool = True):
        self.tab_widget.setTabsClosable(closable)
        return self
