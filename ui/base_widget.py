from PySide6.QtWidgets import QWidget

from ui.base_view import BaseView


class BaseWidgetView(BaseView, QWidget):
    def __init__(self, routeData: dict[str, any] = {}):
        QWidget.__init__(self)
        BaseView.__init__(self, self.parent, routeData=routeData)
        
    def closeEvent(self, event):
        return super().closeEvent(event)