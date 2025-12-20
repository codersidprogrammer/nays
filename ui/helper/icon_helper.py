from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon

def getIconFromResource(path: str, state: QIcon.State=QIcon.State.Off) -> QIcon:
    icon = QIcon()
    icon.addFile(path, QSize(), QIcon.Mode.Normal, state)
    return icon