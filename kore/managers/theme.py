import logging

from PySide6.QtCore import QObject, Signal


class Theme(QObject):

    def __init__(self) -> None:
        super().__init__()

        self.log = logging.getLogger("kore.config")
        self.log.debug("Loading theme manager...")

    def update_theme(self, sheet: str):
        pass
