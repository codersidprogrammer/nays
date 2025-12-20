from PySide6.QtWidgets import QMessageBox


def showMessageConfirmationBox(title: str, message: str, detailedText: str = None, icon=QMessageBox.Icon.Question):
    msg = QMessageBox()
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(message)
    if detailedText:
        msg.setDetailedText(detailedText)
    msg.setStandardButtons(
        QMessageBox.StandardButton.Yes | 
        QMessageBox.StandardButton.No
    )
        # msgBox.setDefaultButton(QMessageBox.StandardButton.No)
    return msg.exec() == QMessageBox.StandardButton.Yes

def showMessageBox(title: str, message: str, detailedText: str = None, icon=QMessageBox.Icon.Information):
    msg = QMessageBox()
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(message)
    if detailedText:
        msg.setDetailedText(detailedText)   
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()


def showErrorMessageBox(title: str = "Error", message: str = "", detailedText: str = None):
    """Show an error message box with a Critical icon.

    Args:
        title: Window title (default: "Error").
        message: Main message text.
        detailedText: Optional detailed text shown in the dialog.
    """
    return showMessageBox(title=title, message=message, detailedText=detailedText, icon=QMessageBox.Icon.Critical)