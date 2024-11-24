import logging
from typing import List, Optional, Tuple

from ..components import NotificationWdgt


class NotificationManager:

    def __init__(
        self,
        root,
        initial_do_not_disturb: bool,
        durations: dict,
        levels: dict,
        notification_widget,
        recent_notifications_widget,
        override_by_importance: bool = False,
    ):
        """
        Initialize the Notifications class.

        Args:
            root: The root object containing shared resources and configurations.
        """
        self.root = root
        self.log = logging.getLogger(("notifications"))
        self.config = root.config

        self.dnd = initial_do_not_disturb
        self.durations = durations
        self.levels = levels
        self.override_by_importance = override_by_importance

        self.notification_widget: NotificationWdgt = notification_widget
        self.recent_notifications_widget = recent_notifications_widget

        self.queue: List[Tuple[NotificationWdgt, int]] = []
        self.current_notification: Optional[NotificationWdgt] = None
        self.showing = False
        self.index = 0
        self.priority = 0
        self.recent_notifications_toggled = False
        self.setup_recent_notifications()

    def new(
        self,
        message: str = "Notification Message",
        level: str = "I",
        duration: str = "S",
        timestamp: bool = False,
        timestamp_message: Optional[str] = None,
        link: Optional[str] = None,
        override_dnd=False,
        require_close=False,
    ) -> None:
        """
        Create a new notification and add it to the queue.

        Args:
            message: The notification message.
            level: The notification level indicating its importance.
            duration: The duration for which the notification should be displayed.
            timestamp: Flag to indicate if a timestamp should be added.
            link: An optional link associated with the notification.
        """

        message = message.replace("\n", "")
        background = self.levels[level]
        background = self.levels[level]["bg"]

        self.recent_notifications.add_item(background, message)
        if self.dnd and not override_dnd:
            return

        duration = self.durations[duration]
        text_color = self.levels[level]["text"]
        new_priority = self.levels[level]["priority"]

        if timestamp_message:
            timestamp_message = timestamp_message.replace("\n", "")

        self.log.debug(f"[{level}]: '{message}'")
        notification = self.notification_widget(  # type:ignore
            root=self.root,
            message=message,
            duration=duration,
            timestamp=timestamp,
            background=background,
            permanent=require_close,
            timestamp_msg=timestamp_message,
            color=text_color,
        )

        notification.move_up.connect(self.recent_notifications.move_up)
        notification.closed.connect(self.recent_notifications.move_down)
        self.queue.append((notification, new_priority))
        if len(self.queue) == 1:
            self.showing = notification
            notification.display()

        if self.override_by_importance:
            if self.priority < new_priority:
                if isinstance(self.showing, NotificationWdgt):
                    self.update_queue()

        else:
            notification.closed.connect(self.update_queue)

    def update_queue(self) -> None:
        """
        Advance to the next notification in the queue and display it, or reset the queue if there are no more notifications.
        """
        try:
            self.index += 1
            if self.index < len(self.queue):
                self.showing, self.priority = self.queue[self.index]
                self.showing.display()
            else:
                self.queue = []
                self.index = 0

        except Exception as e:
            self.log.error(f"Error Processing Queue: {e}")

    def setup_recent_notifications(self) -> None:
        """Initialize the recent notifications panel."""
        self.recent_notifications = self.recent_notifications_widget(
            root=self.root, dnd_state=self.dnd
        )
        self.recent_notifications.setup()
        self.recent_notifications.dnd_changed.connect(self.toggle_dnd)

    def toggle_recent_notification_panel(self) -> None:
        """Toggle the visibility of the recent notifications panel."""
        self.recent_notifications_toggled = not self.recent_notifications_toggled
        self.recent_notifications.display(self.recent_notifications_toggled)

    def toggle_dnd(self, toggle: bool) -> None:
        """
        Toggle the 'Do Not Disturb' mode and update the configuration.

        Args:
            toggle: A boolean value to enable or disable Do Not Disturb mode.
        """
        self.dnd = toggle
        self.config.put("notifications.do_not_disturb", self.dnd)

    """
    ##############################


    ##############################

    def new(
        self,
        message: str = "Notification Message",
        level: str = "I",
        duration: str = "S",
        timestamp: bool = False,
        timestamp_message: Optional[str] = None,
        link: Optional[str] = None,
        override_dnd=False,
    ) -> None:
        ""
        Create a new notification and add it to the queue.

        Args:
            message: The notification message.
            level: The notification level indicating its importance.
            duration: The duration for which the notification should be displayed.
            timestamp: Flag to indicate if a timestamp should be added.
            link: An optional link associated with the notification.
        ""
        message = message.replace("\n", " ")
        background = self.levels[level][0]
        importance = self.levels[level][1]

        permanent, duration_converted = (
            ("perma" == duration, 100)
            if duration == "perma"
            else (False, self.durations[duration])
        )

        self.recent_notifications.add_item(background, message)  # type:ignore
        self.log.debug(f"(notification) [{level}]: '{message}'")

        if self.dnd:
            if override_dnd:
                pass

            else:
                return

        notification = Notification(
            root=self.root,
            link=link,
            message=message,
            permanent=permanent,
            duration=duration_converted,
            timestamp=timestamp,
            timestamp_msg=timestamp_message,
            background=background,
        )
        notification.move_up.connect(self.recent_notifications.move_up)
        notification.closed.connect(self.recent_notifications.move_down)
        notification.closed.connect(self.next_queue)

        self.queue.append((notification, importance))
        if len(self.queue) == 1:
            self.index = 0
            self.showing = notification
            self.current_importance = importance
            notification.display()

        if (
            self.override_by_importance
            and self.current_importance < importance
            and isinstance(self.showing, Notification)
        ):
            self.log.debug("overriding current notification by importance")
            self.showing.fade()
            self.next_queue()

    def next_queue(self) -> None:
        ""
        Advance to the next notification in the queue and display it, or reset the queue if there are no more notifications.
        ""
        try:
            self.index += 1
            if self.index < len(self.queue):
                self.showing, self.current_importance = self.queue[self.index]
                self.showing.display()
            else:
                self.queue = []
                self.index = 0
        except Exception as e:
            self.log.error(f"Error Processing Queue: {e}")

    """
