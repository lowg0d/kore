import re
from collections import deque
from typing import Tuple

from PySide6.QtCore import (
    QAbstractAnimation,
    QDateTime,
    QEvent,
    QPoint,
    QPropertyAnimation,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
)

from . import LinkHoverLabel


class NotificationHistoryWdgt(QFrame):
    closed = Signal()
    started = Signal()
    dnd_changed = Signal(bool)

    def __init__(self, root, dnd_state: bool):
        super().__init__(root)
        self.root = root

        self.dnd_state = dnd_state
        self.LINK_COLOR = "#063970"
        self.FADE_ANI_DURATION = 100
        self.BOTTOM_MARGIN = -22
        self.MAX_HEIGHT = 400
        self.WIDTH = 310
        self.SPACING = 5
        self.RIGHT_MARGIN = 5
        self.MAX_MSG_LENGTH = 23
        self.MAX_NOTIFICATIONS = 10
        self.FIXED_HEIGHT = 28
        self.STYLE = """
            QFrame{
                border-radius: 4px; 
                padding-left: 4px;
                padding-right: 4px;
                color: #eeeeed;
                background-color: #0c0c0c;
            }
            QLabel{
                background-color:transparent;  
                padding: 3px;
                padding: 3px;
            }
        """
        self.TOP_LABEL_STYLE = """
            QLabel{
                padding:0px;margin:0px;font: 1000 9pt "Video";color:#e4e4e4;
            }
                """
        self.DND_BTN_STYLE = """
            QToolButton {
                background-color: transparent;
                border:0px;
                height:10px;
                width:10px;
                border-radius:4px;
                padding:4px;
                margin-right:1px
            } 
            QToolButton:checked{
                background-color:#4020BF6B;
                border:1px solid #8020BF6B
            }"""
        self.MESSAGE_STYLE = """
            QLabel{
                background-color: transparent;
                color:#070707;
                font: 10pt "Video";
            }"""
        self.TIME_LABEL_STYLE = (
            "QLabel{color: #070707;background-color: transparent;font:9pt 'Video';}"
        )
        self.CLOSE_BUTTON_STYLE = """QToolButton {
                background: transparent;
                color: &color;
                font: 1000 9pt "Video";
                border:0px
                }"""
        self.FRAME_STYLE = """
            QFrame{
                background-color: #99&color;
                border: 1px solid #&color;
                border-radius: 4px;
            }
            QLabel{border:none;}"""
        self.INITIAL_MARGIN = -22
        self.DND_ICON_PATH = "./src/ui/assets/icons/dnd.svg"

    def setup(self):
        self.current_index = 0
        self.label_map = deque()

        self.timestamp_timer = QTimer(self)
        self.timestamp_timer.setInterval(1000)
        self.timestamp_timer.timeout.connect(self.refresh)

        ## Animation
        self.setup_frame()
        self.setup_fade_ani()
        self.setup_top_and_layout(self.dnd_state)

        ## Geometry=
        self.raise_()
        self.adjustSize()
        self.adjust_geo()

    ## SETUPS

    def setup_frame(self):
        QGridLayout(self)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)  # type:ignore
        self.setStyleSheet(self.STYLE)
        self.setFixedWidth(self.WIDTH)
        self.setMaximumHeight(self.MAX_HEIGHT)

        self.close()

    def setup_fade_ani(self) -> None:
        self.opacityEffect = QGraphicsOpacityEffect(opacity=0)  # type:ignore
        self.setGraphicsEffect(self.opacityEffect)

        self.fade_ani = QPropertyAnimation(self.opacityEffect, b"opacity")
        self.parent().installEventFilter(self)

        self.fade_ani.setStartValue(0.0)
        self.fade_ani.setEndValue(1.0)
        self.fade_ani.setDuration(self.FADE_ANI_DURATION)
        self.fade_ani.finished.connect(self.hide)

    def setup_top_and_layout(self, dnd_state: bool) -> None:
        label = QLabel("Recent Notifications")
        label.setStyleSheet(self.TOP_LABEL_STYLE)

        self.dndButton = QToolButton()
        self.dndButton.setIcon(QIcon(self.DND_ICON_PATH))
        self.dndButton.setAutoRaise(True)
        self.dndButton.setCheckable(True)
        self.dndButton.setChecked(dnd_state)
        self.dndButton.setStyleSheet(self.DND_BTN_STYLE)
        self.dndButton.setCursor(Qt.PointingHandCursor)  # type:ignore
        self.dndButton.setToolTip("Activate Do Not Disturb Mode")
        self.dndButton.clicked.connect(self.update_dnd)

        self.QLayout = self.layout()
        self.QLayout.addWidget(label, 0, 0)  # type:ignore
        self.QLayout.addWidget(
            self.dndButton, 0, 0, Qt.AlignmentFlag.AlignRight  # type:ignore
        )

        self.QLayout.setSpacing(self.SPACING)
        self.QLayout.setContentsMargins(6, 6, 6, 9)

    ## ITEMS

    def add_item(self, color: str, msg: str) -> None:
        """
        Adds a new item with the specified color and message to the notification list.
        """
        current_time = QDateTime.currentDateTime()
        frame, layout = self._create_frame()

        label = self._create_message_label(msg)
        layout.addWidget(label)

        time_label = self._create_time_label()
        closeButton = self._create_close_button(color, frame)

        self._assemble_layout(layout, time_label, closeButton)
        self._configure_frame(frame, color)

        # Update mappings and layout.
        self.current_index += 1
        self.label_map.append((layout, time_label, current_time, frame))
        self._update_layout(frame)

    def _create_frame(self) -> Tuple[QFrame, QHBoxLayout]:
        """
        Creates a new frame and its corresponding layout.
        """
        frame = QFrame(self)
        layout = QHBoxLayout(frame)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        return frame, layout

    def _create_message_label(self, msg: str) -> QLabel:
        """
        Creates a message label, truncating the message if necessary and adding a tooltip with the full message.
        """
        label = LinkHoverLabel()
        msg = self.__transform_link(msg)

        if len(msg) > self.MAX_MSG_LENGTH:
            label.setToolTip(msg)
            msg = msg[: (self.MAX_MSG_LENGTH - 3)] + "..."
        label.setText(msg)
        label.setStyleSheet(self.MESSAGE_STYLE)
        return label

    def _create_time_label(self) -> QLabel:
        """
        Creates a label to display the time.
        """
        time_label = QLabel()
        time_label.setStyleSheet(self.TIME_LABEL_STYLE)
        return time_label

    def _create_close_button(self, color: str, frame: QFrame) -> QToolButton:
        """
        Creates a close button with the specified color and connects its clicked signal to the close_frame method.
        """
        closeButton = QToolButton()
        closeButton.setText("x")
        closeButton.setAutoRaise(True)
        closeButton.setStyleSheet(self.CLOSE_BUTTON_STYLE.replace("&color", color))
        closeButton.clicked.connect(lambda: self.close_frame(frame))
        closeButton.setToolTip("Erase Notification From List")
        closeButton.setCursor(Qt.PointingHandCursor)  # type:ignore
        return closeButton

    def _assemble_layout(
        self, layout: QHBoxLayout, time_label: QLabel, closeButton: QToolButton
    ) -> None:
        """
        Assembles the components into the layout.
        """
        layout.addStretch(1)
        layout.addWidget(time_label)
        layout.addWidget(closeButton)

    def _configure_frame(self, frame: QFrame, color: str) -> None:
        """
        Configures the frame's appearance and displays it.
        """
        frame.setFixedHeight(self.FIXED_HEIGHT)
        frame.setStyleSheet(self.FRAME_STYLE.replace("&color", color))
        frame.show()

    def _update_layout(self, frame: QFrame) -> None:
        """
        Updates the main layout to include the new frame and refreshes the display.
        """
        self.QLayout.addWidget(frame, self.current_index, 0)  # type:ignore
        self.QLayout.update()
        self.adjustSize()
        self.repaint()

    ## BUTTON ACTION

    def update_dnd(self) -> None:
        """
        Emits a signal indicating the change of the 'Do Not Disturb Mode'.
        """
        toggled = self.dndButton.isChecked()
        self.dnd_changed.emit(toggled)

    def close_frame(self, frame: QFrame) -> None:
        """
        Closes the specified frame and triggers a refresh of the layout.
        """
        frame.close()
        self.refresh()

    ## HELPERS

    def __transform_link(self, input_string: str) -> str:

        # Define the pattern for markdown links
        pattern = r"\[([^\]]+)\]\((https?://[^\)]+)\)"

        # Function to replace markdown link with HTML anchor tag
        def replace_with_html(match):
            link_text, url = match.groups()
            return f'<a style="color:{self.LINK_COLOR}" href="{url}">{link_text}</a>'

        # Replace all matches in the input string
        return re.sub(pattern, replace_with_html, input_string)

    def format_time(self, seconds: int) -> str:
        """
        Formats a given time in seconds into a more readable format, displaying hours, minutes, and seconds as necessary.

        Args:
            seconds (int): The time duration in seconds to be formatted.

        Returns:
            str: A formatted string representing the time duration.
        """
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{int(hours)}h {int(minutes)}m"
        elif minutes > 0:
            return f"{int(minutes)}m {int(seconds)}s"
        else:
            return f"{int(seconds)}s"

    ## DISPLAY

    def display(self, toggle: bool) -> None:
        """
        Controls the display of the panel based on the toggle parameter. If true,
        it shows and starts the fade-in animation along with the timer. If false, it stops
        the timer and initiates the fade-out animation.

        Args:
            toggle (bool): Determines whether to show or hide the panel.
        """
        if toggle:
            self.show()
            self.fade_ani.setDirection(QAbstractAnimation.Direction.Forward)
            self.fade_ani.start()
            self.refresh()

            self.timestamp_timer.start()
            self.started.emit()

        else:
            self.timestamp_timer.stop()
            self.fade_ani.setDirection(QAbstractAnimation.Direction.Backward)
            self.fade_ani.start()

    def hide(self) -> None:
        """
        Closes the panel when the fade-out animation is complete, ensuring
        that the panel is only closed if the animation is in the backward direction.
        """
        if self.fade_ani.direction() == QAbstractAnimation.Direction.Backward:
            self.close()

    def refresh(self) -> None:
        """
        Updates the notification list by removing excess items and refreshing the time
        labels of remaining items to reflect the current time.
        """
        current_time = QDateTime.currentDateTime()

        # Remove excess items to maintain the maximum item display limit.
        while len(self.label_map) > self.MAX_NOTIFICATIONS:
            _, _, _, frame = (
                self.label_map.popleft()
            )  # Remove the oldest item from the deque.
            frame.deleteLater()  # Ensure the removed frame is deleted.

        self.adjustSize()  # Adjust the size of the notification container.
        self.adjust_geo()  # Adjust the geometry to reposition the notification.

        # Update the time labels for all remaining notifications.
        for _, time_label, old_time, _ in self.label_map:
            time_difference = old_time.secsTo(
                current_time
            )  # Calculate the time difference.
            time_str = self.format_time(time_difference)  # Format the time difference.
            time_label.setText(time_str)  # Update the time label text.

    ## POSITION

    def move_up(self, new_bottom_margin: int) -> None:
        """
        Adjusts the panels's bottom margin to move it upwards and then updates its geometry.

        Args:
            new_bottom_margin (int): The new bottom margin value to move the panel up..
        """
        margin = -(new_bottom_margin + 25)  # adjust for the the notification height
        self.BOTTOM_MARGIN = margin
        self.adjust_geo()

    def move_down(self):
        """
        Resets the panel's bottom margin to its default value and updates its geometry.
        """
        self.BOTTOM_MARGIN = self.INITIAL_MARGIN
        self.adjust_geo(self)

    def adjust_geo(self, e=None) -> None:
        """
        Adjusts the geometry of the panel frame relative to its parent, considering
        specified right and bottom margins.
        """
        parentRect = self.parent().rect()  # type:ignore
        geo = self.geometry()
        geo.moveBottomRight(
            parentRect.bottomRight() + QPoint(-self.RIGHT_MARGIN, self.BOTTOM_MARGIN)
        )
        self.setGeometry(geo)

    ## EVENTS

    def closeEvent(self, event):
        self.closed.emit()

    def eventFilter(self, watched, event):
        if watched == self.parent() and event.type() == QEvent.Resize:  # type:ignore
            self.adjust_geo()

        return super(NotificationHistoryWdgt, self).eventFilter(watched, event)

    def resizeEvent(self, event):
        super(NotificationHistoryWdgt, self).resizeEvent(event)
        self.clearMask()
