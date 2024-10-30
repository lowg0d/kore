import re
from ast import Dict
from operator import methodcaller
from sys import flags
from typing import Any

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
    QTime,
    QUrl,
    Signal,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QKeySequenceEdit,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(856, 40)
        Form.setMinimumSize(QSize(0, 40))
        Form.setMaximumSize(QSize(16777215, 40))
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.container = QFrame(Form)
        self.container.setObjectName("setting_container")
        self.container.setMinimumSize(QSize(0, 40))
        self.container.setMaximumSize(QSize(16777215, 40))
        self.container.setFrameShape(QFrame.Shape.NoFrame)
        self.container.setFrameShadow(QFrame.Shadow.Plain)
        self.horizontalLayout = QHBoxLayout(self.container)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 0, 10, 0)
        self.name_label = QLabel(self.container)
        self.name_label.setObjectName("name_label")

        self.horizontalLayout.addWidget(self.name_label)

        self.description_label = QLabel(self.container)
        self.description_label.setObjectName("description_label")

        self.horizontalLayout.addWidget(self.description_label)

        self.horizontalSpacer = QSpacerItem(
            379, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        QMetaObject.connectSlotsByName(Form)


class SettingFormWidget(QWidget):
    function_map = {}

    def __init__(self, key: str, data: dict, config_instance):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setKeyAndData(key, data)
        self.key = "settings." + key

        self.config = config_instance

        _type = data.get("custom_type", None)
        if not _type:
            _type = type(data.get("default_value")).__name__

        self.custom_flag = data.get("custom_flag", False)
        self.og_description = self.ui.description_label.text()
        self.flag_visible = True
        self.update_flag = True

        self.function_map = {
            "str": self._setup_string,
            "bool": self._setup_bool,
            "list": self._setup_list,
            "int": self._setup_int,
            "float": self._setup_float,
            "CustomType": self._setup_custom,
        }

        setup_function = self.function_map.get(_type, None)
        if not setup_function:
            print(f"Type Not Valid '{_type}' in {self.ui.name_label.text()}")
            return

        print(self.config.get(key), "settings.json")

        setup_function()

    def _toggle_flag_visibility(self):
        if self.update_flag:
            if self.flag_visible:
                self.custom_flag = f"{self.og_description} • {self.custom_flag}"
                self.ui.description_label.setText(self.custom_flag)

            else:
                self.ui.description_label.setText(self.og_description)

            self.update_flag = False

    def _update_data(self):
        if self.custom_flag:
            self._toggle_flag_visibility()

    def _setup_string(self):
        line_edit = QLineEdit(self.ui.container)
        line_edit.setObjectName("line_edit")

        line_edit.setFixedHeight(30)
        line_edit.setFixedWidth(200)
        line_edit.setFocusPolicy(Qt.ClickFocus)

        line_edit.textChanged.connect(self._update_data)
        self.ui.horizontalLayout.addWidget(line_edit)
        self.ui.verticalLayout.addWidget(self.ui.container)

    def _setup_bool(self):
        checkbox = QCheckBox(self.ui.container)
        checkbox.setObjectName("checkbox")
        checkbox.setCursor(QCursor(Qt.PointingHandCursor))

        checkbox.setFixedHeight(30)
        checkbox.setFixedWidth(30)
        checkbox.setFocusPolicy(Qt.ClickFocus)
        checkbox.stateChanged.connect(self._update_data)

        self.ui.horizontalLayout.addWidget(checkbox)
        self.ui.verticalLayout.addWidget(self.ui.container)

    def _setup_list(self):
        combo_box = QComboBox(self.ui.container)
        combo_box.setObjectName("combo_box")

        combo_box.setFixedHeight(30)
        combo_box.setFixedWidth(200)
        combo_box.setFocusPolicy(Qt.ClickFocus)
        combo_box.currentIndexChanged.connect(self._update_data)

        combo_box.addItems(["test", "test2", "test3"])

        self.ui.horizontalLayout.addWidget(combo_box)
        self.ui.verticalLayout.addWidget(self.ui.container)

    def _setup_int(self):
        spinbox = QSpinBox(self.ui.container)
        spinbox.setObjectName("spinbox")
        spinbox.setCursor(QCursor(Qt.PointingHandCursor))

        spinbox.setFixedHeight(30)
        spinbox.setFixedWidth(200)
        spinbox.setFocusPolicy(Qt.ClickFocus)
        spinbox.valueChanged.connect(self._update_data)

        self.ui.horizontalLayout.addWidget(spinbox)
        self.ui.verticalLayout.addWidget(self.ui.container)

    def _setup_float(self):
        spinbox = QDoubleSpinBox(self.ui.container)
        spinbox.setObjectName("doublespinbox")
        spinbox.setCursor(QCursor(Qt.PointingHandCursor))

        spinbox.setFixedHeight(30)
        spinbox.setFixedWidth(200)
        spinbox.setFocusPolicy(Qt.ClickFocus)
        spinbox.valueChanged.connect(self._update_data)

        self.ui.horizontalLayout.addWidget(spinbox)
        self.ui.verticalLayout.addWidget(self.ui.container)

    def _setup_custom(self):
        combo_box = QComboBox(self.ui.container)
        combo_box.setObjectName("combo_box")

        combo_box.setFixedHeight(30)
        combo_box.setFixedWidth(200)
        combo_box.setFocusPolicy(Qt.ClickFocus)
        combo_box.currentIndexChanged.connect(self._update_data)

        combo_box.addItems(["Theme", "Custom Type"])

        self.ui.horizontalLayout.addWidget(combo_box)
        self.ui.verticalLayout.addWidget(self.ui.container)

    def _transform_link(self, input_string: str) -> str:

        # Define the pattern for markdown links
        pattern = r"\[([^\]]+)\]\((https?://[^\)]+)\)"

        # Function to replace markdown link with HTML anchor tag
        def replace_with_html(match):
            link_text, url = match.groups()
            return f'<a style="color:#5E81AC" href="{url}">{link_text}</a>'

        # Replace all matches in the input string
        return re.sub(pattern, replace_with_html, input_string)

    def setKeyAndData(self, key: str, data: dict):
        # Example of setting up the UI elements based on key and data
        self.ui.name_label.setText(data.get("name", ""))

        description = data.get("description", "")
        self.ui.description_label.setText(self._transform_link(description))
        self.ui.description_label.setOpenExternalLinks(True)
