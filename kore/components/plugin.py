from PySide6.QtCore import QObject


class Plugin(QObject):
    def __init__(self, parent: QObject | None) -> None:
        super().__init__(parent)
