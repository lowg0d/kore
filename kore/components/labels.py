from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QLabel, QToolTip


class LinkHoverLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpenExternalLinks(True)
        self.setTextInteractionFlags(Qt.TextBrowserInteraction)  # type:ignore
        self.linkHovered.connect(self.handleLinkHovered)

    def handleLinkHovered(self, link):
        if link:
            QToolTip.showText(QCursor.pos(), link)
        else:
            QToolTip.hideText()
