from PySide6.QtWidgets import QWidget


class Component(QWidget):

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
