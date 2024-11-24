import re
from typing import Optional

from PySide6.QtCore import (
    QAbstractAnimation,
    QDateTime,
    QEvent,
    QPoint,
    QPropertyAnimation,
    Qt,
    QTimer,
    Signal,
    SignalInstance,
)
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
)

from . import LinkHoverLabel


class NotificationWdgt(QFrame):
    """
    A Notification component that displays alerts or messages within a given root window.
    """

    closed = Signal()
    move_up = Signal(int)

    def __init__(
        self,
        root,
        message: str,
        duration: int,
        timestamp: bool,
        background: str,
        permanent: bool,
        timestamp_msg: str,
        color: str,
    ):
        """Initializes the notification with various customizable options.

        Args:
            root (QMainWindow or Ui): The parent window for this notification.
            message (str): The main message to be displayed.
            duration (int): How long (in milliseconds) the notification should be displayed.
            timestamp (bool): Whether to display a timestamp.
            background (str): The background color of the notification.
            permanent (bool): Whether the notification is auto-closed or manual closing.
            timestamp_msg (str): Optional custom message to display alongside the timestamp.
            color (str, optional): The text color of the notification. Defaults to DEFAULT_COLOR.
        """
        super().__init__(root)
        self.root = root

        self.LINK_COLOR = "#063970"
        self.RIGHT_MARGIN = 5
        self.BOTTOM_MARGIN = 22
        self.SPACING = 5
        self.WIDTH = 310
        self.LABEL_FIXED_WIDTH = 300
        self.FADE_DURATION = 200

        self.FRAME_STYLE = """
            QFrame{
                border-radius: 5px; 
                padding-left: 2px;
                padding-right: 2px;
                color: #&color;
                border-style: outset;
                background-color: #&bg;
                border:3px solid #99&bg;
            } 
            QLabel{
                border:none;
            }
        """
        self.MESSAGE_STYLE = """
            QLabel{
                color: #&color;
                background-color: transparent;
                font: 900 10pt "JetBrains Mono";
            }
        """
        self.CLOSE_BTN_STYLE = """
            QToolButton{
                color: #99&color;
                background: transparent;
                font: 1000 8pt "JetBrains Mono";
                border:0px;
            }
            QToolButton:hover{
                color: #&color;
            }
        """
        self.TIMESTAMP_STYLE = """
            QLabel{
                color: #99&color;
                background-color: transparent;
                font:  8pt "JetBrains Mono";
            }
        """

        self.permanent = permanent
        self.message = message

        self.color = color
        self.bg = background
        self.duration = duration
        self.timestamp = timestamp
        self.timestamp_msg = timestamp_msg

    ## Setups.

    def setup(self):
        ## Setup frame.
        self.setup_frame()
        self.setup_fade_animation()

        ## Setup Notifications
        self.add_timestamp()
        self.set_attributes()

        ## Raise the widget and adjust its size to the minimum.
        self.raise_()
        self.adjustSize()
        self.adjust_geo()

    def setup_frame(self) -> None:
        """
        Sets up the frame's dimensions, style, and layout. It fixes the frame width and
        applies a specified style to the frame.
        """
        self.parentRect = self.root.window().rect()
        self.setFixedWidth(self.WIDTH)

        ## Set up the frame with specified color and background.
        QGridLayout(self)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)  # type:ignore
        self.setStyleSheet(self._format_style(self.FRAME_STYLE))

    def setup_fade_animation(self) -> None:
        """
        Initializes the fade animation for the frame, including setting up a timer for
        the animation duration and configuring the opacity effect for the fade-in and fade-out animations.
        """
        ## Set up the close timer.
        self.fade_timer = QTimer(singleShot=True, timeout=self.fade)  # type:ignore
        self.fade_timer.setInterval(self.duration)

        ## Set up the opacity effect for show/fade animation.
        self.opacityEffect = QGraphicsOpacityEffect(opacity=0)  # type:ignore
        self.setGraphicsEffect(self.opacityEffect)

        self.fade_ani = QPropertyAnimation(self.opacityEffect, b"opacity")
        self.parent().installEventFilter(self)

        self.fade_ani.setStartValue(0.0)
        self.fade_ani.setEndValue(1)
        self.fade_ani.setDuration(self.FADE_DURATION)
        if not self.permanent:
            self.fade_ani.finished.connect(self.hide)

    def set_attributes(self) -> None:
        """
        Configures the attributes of the notification frame, including the message label and
        the close button, and sets their properties like text, style, and tooltips.
        """
        self.message_label = LinkHoverLabel()
        self.message_label.setOpenExternalLinks(True)
        self.message_label.setWordWrap(True)
        self.message_label.setFixedWidth(self.LABEL_FIXED_WIDTH)

        transformed_message = self.__transform_link(self.message)
        self.message_label.setText(transformed_message)
        self.message_label.setStyleSheet(self._format_style(self.MESSAGE_STYLE))

        ## Set up close button.
        self.closeButton = QToolButton()
        self.closeButton.setText("x")
        self.closeButton.setAutoRaise(True)
        self.closeButton.setStyleSheet(self._format_style(self.CLOSE_BTN_STYLE))
        self.closeButton.clicked.connect(self.close)
        self.closeButton.setToolTip("Close Notification")
        self.closeButton.setCursor(Qt.PointingHandCursor)  # type:ignore

        self.layout().addWidget(self.message_label, 0, 1)  # type:ignore
        self.layout().addWidget(
            self.closeButton, 0, 2, alignment=Qt.AlignTop  # type:ignore
        )  # type:ignore
        self.layout().setSpacing(self.SPACING)

    ## Helpers

    def add_timestamp(self) -> None:
        """
        Adds a timestamp label to the notification if requested, with an optional
        additional message appended to the timestamp.
        """
        timestamp = self.timestamp
        timestamp_msg = self.timestamp_msg
        timestamp_string = ""
        # Display timestamp if specified.
        if timestamp:
            time = QDateTime.currentDateTime()
            time = time.toString("HH:mm:ss")
            timestamp_string = f"{time}"

        if timestamp_msg:
            timestamp_string = (
                "" if timestamp_string == "" else f"{timestamp_string} - "
            )
            timestamp_string += f"{timestamp_msg}"

        if timestamp_string != "":
            self.timestamp_label = QLabel(timestamp_string)
            self.timestamp_label.setStyleSheet(self._format_style(self.TIMESTAMP_STYLE))

            self.layout().addWidget(self.timestamp_label, 1, 1)  # type:ignore

    def adjust_geo(self) -> None:
        """
        Adjusts the geometry of the notification frame relative to its parent, considering
        specified right and bottom margins.
        """
        parentRect = self.parent().rect()  # type:ignore
        geo = self.geometry()
        geo.moveBottomRight(
            parentRect.bottomRight() + QPoint(-self.RIGHT_MARGIN, -self.BOTTOM_MARGIN)
        )
        self.setGeometry(geo)

    def _format_style(self, style: str) -> str:
        """
        Formats the given style string by replacing placeholders with actual values
        for color and background.
        """
        style = style.replace("&color", self.color).replace("&bg", self.bg)
        return style

    def __transform_link(self, input_string: str) -> str:

        # Define the pattern for markdown links
        pattern = r"\[([^\]]+)\]\((https?://[^\)]+)\)"

        # Function to replace markdown link with HTML anchor tag
        def replace_with_html(match):
            link_text, url = match.groups()
            return f'<a style="color:{self.LINK_COLOR}" href="{url}">{link_text}</a>'

        # Replace all matches in the input string
        return re.sub(pattern, replace_with_html, input_string)

    ## Display.

    def display(self) -> None:
        """
        Displays the notification with a fade-in animation,
        starts the move-up animation for the recent notifications panel,
        and initiates the fade timer and fade animation.
        """
        self.setup()

        self.show()

        self.fade_timer.start()
        self.fade_ani.start()
        self.move_up.emit(self.height())

    def hide(self) -> None:
        """
        Hides the notification when the fade-out animation is complete, ensuring
        that the notification is only closed if the animation is in the backward direction.
        """
        if self.fade_ani.direction() == QAbstractAnimation.Direction.Backward:
            self.close()

    def fade(self) -> Optional[SignalInstance]:
        """
        Triggers the fade-out animation if the notification is not marked as permanent.
        """
        if not self.permanent:
            self.fade_ani.setDirection(QAbstractAnimation.Direction.Backward)
            self.fade_ani.start()
            return self.fade_ani.finished

        return None

    def pause_fade(self) -> None:
        """
        Pauses the fade-out animation and timer, setting the notification's opacity to full.
        """
        self.fade_timer.stop()
        self.fade_ani.stop()
        if self.parent():
            self.opacityEffect.setOpacity(1.0)
        else:
            self.setWindowOpacity(1.0)

    ## Events.

    def enterEvent(self, event) -> None:
        # Pause the timer when mouse enters.
        self.pause_fade()

    def leaveEvent(self, event) -> None:
        # Restore the fade timer when mouse leaves.
        self.fade_timer.start()

    def closeEvent(self, event) -> None:
        # Close the notification and emit closed signal.
        self.deleteLater()
        self.closed.emit()

    def eventFilter(self, watched, event) -> bool:
        # Handle resize event for the parent and adjust the notification accordingly.
        if watched == self.parent() and event.type() == QEvent.Resize:  # type:ignore
            self.adjust_geo()

        return super(NotificationWdgt, self).eventFilter(watched, event)

    def resizeEvent(self, event) -> None:
        # Clear the mask on resize.
        super(NotificationWdgt, self).resizeEvent(event)
        self.clearMask()
