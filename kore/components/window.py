import logging
import os

from PySide6.QtCore import QPropertyAnimation, Qt, Signal, SignalInstance
from PySide6.QtGui import QFontDatabase, QIcon
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget
from qframelesswindow import FramelessMainWindow

from ..managers import Config, Theme
from .app import App
from .titlebar import CustomTitleBar

FONTS_PATH = "./src/gui/assets/fonts"
PLUGINS_PATH = "./plugins"
FONT_EXTENSIONS = (
    ".ttf",
    ".otf",
    ".pfa",
    ".pfb",
)


class Interface(FramelessMainWindow):
    restart = Signal()

    name: str
    version: str
    config: Config
    theme: Theme

    def __init__(self, app: App) -> None:
        super().__init__()

        self.log = logging.getLogger("kore.window")
        self.app = app

        self.name = self.app.name
        self.version = self.app.version

        self.log.debug("Loading mangers...")
        self._load_config_manager()
        self._load_theme_manager()
        self._load_fonts()

    def _load_config_manager(self):
        self.config = Config()
        self.log.debug("Confing manager loaded !")

    def _load_theme_manager(self):
        self.log.debug("Theme manager loaded !")

    def _load_fonts(self):
        fonts = os.listdir(FONTS_PATH)

        self.log.debug("Loading fonts...")
        for font in fonts:
            if font.lower().endswith(FONT_EXTENSIONS):
                font_path = os.path.join(FONTS_PATH, font)
                font_id = QFontDatabase.addApplicationFont(font_path)

                if font_id == -1:
                    self.log.error(f"Failed to load the font '{font}'.")

                else:
                    self.log.debug(f"'{font}' loaded !")

    def _load_plugins(self):
        plugins = os.listdir(PLUGINS_PATH)

    def _setup_titlebar(self):
        std_titlebar = CustomTitleBar(self)
        self.app.set_style.connect(std_titlebar._setSheet)
        self.setTitleBar(std_titlebar)
        self.titleBar.raise_()

    def _load_window_properties(self) -> None:

        self.setWindowTitle(self.name)

        icon_path = self.app.app_data["icon_path"]
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(self.app.app_data["icon_path"]))

        else:
            self.log.warning(f"No app icon was foun at '{icon_path}'")

    def apply_style(self, name):
        self.app.set_style.emit(name)

    def mousePressEvent(self, event):
        # Clear focus when clicking anywhere outside of a widget
        if event.button() == Qt.LeftButton:
            self.centralWidget().setFocus(Qt.MouseFocusReason)
        super().mousePressEvent(event)

    def show(self):
        self._setup_titlebar()
        self._load_window_properties()
        super().show()
