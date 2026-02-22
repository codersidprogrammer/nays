from PySide6.QtWidgets import QDialog, QMessageBox

from nays.ui.base_view import BaseView


class BaseDialogView(BaseView, QDialog):
    def __init__(self, routeData: dict[str, any] = {}):
        QDialog.__init__(self, parent=None)  # No parent - allows independent windows
        self.setModal(False)  # Non-modal so it doesn't block other windows
        BaseView.__init__(self, routeData=routeData)

    def closeEvent(self, arg__1):
        return super().closeEvent(arg__1)
