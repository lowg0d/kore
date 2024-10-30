import logging
import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget
from qframelesswindow import FramelessMainWindow, StandardTitleBar, TitleBar


class CustomTitleBar(TitleBar):

    def __init__(self, parent: FramelessMainWindow, icon_size: int = 20):
        super().__init__(parent)

        self.icon_size: int = icon_size
        self.log = logging.getLogger("kore.titlebar")

        # add window icon
        self.iconLabel = QLabel(self)
        self.iconLabel.setObjectName("tb_iconlabel")
        self.iconLabel.setFixedSize(self.icon_size, self.icon_size)

        self.hBoxLayout.insertSpacing(0, 10)
        self.hBoxLayout.insertWidget(1, self.iconLabel, 0, Qt.AlignLeft)  # type: ignore

        # add title label
        self.titleLabel = QLabel(self)
        self.titleLabel.setObjectName("tb_titlelabel")
        self.hBoxLayout.insertWidget(2, self.titleLabel, 0, Qt.AlignLeft)  # type: ignore

        self.window().windowIconChanged.connect(self._setIcon)
        self.window().windowTitleChanged.connect(self._setTitle)

        self.styles = {}

        self.minBtn.setObjectName("tb_minbtn")
        self.maxBtn.setObjectName("tb_maxbtn")
        self.closeBtn.setObjectName("tb_closebtn")

        self.setObjectName("tb_titlebar")

        self.btns = [self.minBtn, self.maxBtn, self.closeBtn]

    def _setTitle(self, title):
        """set the title of title bar
        Parameters
        ----------
        title: str
            the title of title bar
        """
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def _setIcon(self, icon):
        """set the icon of title bar
        Parameters
        ----------
        icon: QIcon | QPixmap | str
            the icon of title bar
        """
        self.iconLabel.setPixmap(QIcon(icon).pixmap(self.icon_size, self.icon_size))

    def _setSheet(self, sheet: str):
        for btn in self.btns:
            btn_name = btn.objectName()
            btn_style = self.extract_qss_properties(sheet, btn_name)

            if not btn_style:
                self.log.warning(f"no style for the button '{btn_name}'")
                return

            for state in ["normal", "hover", "pressed"]:
                # sprint(btn_style)
                color = btn_style[state].get("color", "white")
                bg_color = btn_style[state].get("background-color", "blue")

                # Directly setting values using method references
                (
                    btn.setNormalColor(color)
                    if state == "normal"
                    else (
                        btn.setHoverColor(color)
                        if state == "hover"
                        else btn.setPressedColor(color)
                    )
                )
                (
                    btn.setNormalBackgroundColor(bg_color)
                    if state == "normal"
                    else (
                        btn.setHoverBackgroundColor(bg_color)
                        if state == "hover"
                        else btn.setPressedBackgroundColor(bg_color)
                    )
                )

    def extract_qss_properties(self, qss, object_name):
        properties = {"normal": {}, "hover": {}, "pressed": {}}

        # Patterns for different states
        patterns = {
            "normal": rf"(^|[^a-zA-Z0-9-])#{object_name}(?!:)(?:[^{{]*,\s*[^{{]+)*\s*{{([^}}]*)}}",
            "hover": rf"(^|[^a-zA-Z0-9-])#{object_name}:hover[^{{]*{{([^}}]*)}}",
            "pressed": rf"(^|[^a-zA-Z0-9-])#{object_name}:pressed[^{{]*{{([^}}]*)}}",
        }

        for state, pattern in patterns.items():
            matches = re.findall(pattern, qss, re.MULTILINE)
            for match in matches:
                content = match[-1]  # The last group contains the CSS properties
                # Extract background-color and color
                bg_color = re.search(r"background-color:\s*([^;]+)", content)
                color = re.search(r"(?<!-)\bcolor:\s*([^;]+)", content)

                if bg_color:
                    properties[state]["background-color"] = bg_color.group(1).strip()
                if color:
                    properties[state]["color"] = color.group(1).strip()

        return properties

    def add_button(self, text: str):
        self.questionButton = QPushButton(text)
        self.hBoxLayout.insertWidget(
            4, self.questionButton, Qt.AlignRight  # type:ignore
        )
