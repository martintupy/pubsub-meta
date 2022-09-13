from datetime import datetime
from enum import Enum
from typing import Optional

import click
import readchar
from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.live import Live
from google.pubsub_v1.types.pubsub import Topic
from google.pubsub_v1.types.pubsub import Subscription
from rich.panel import Panel

from pubsub_meta import const, output
from pubsub_meta.config import Config
from pubsub_meta.service.subscription_service import SubscriptionService
from pubsub_meta.service.topic_service import TopicService
from pubsub_meta.service.history_service import HistoryService
from pubsub_meta.util.rich_utils import flash_panel


class View(Enum):
    topic = 1
    subscription = 2
    snapshots = 3
    schemas = 4


class Window:
    def __init__(
        self,
        console: Console,
        config: Config,
        topic_service: TopicService,
        subscription_service: SubscriptionService,
        history_service: HistoryService,
    ):
        self.console = console
        self.config = config
        self.subscription_service = subscription_service
        self.topic_service = topic_service
        self.history_service = history_service
        self.layout: Layout = Layout()
        self.content: Optional[RenderableType] = None
        self.view: View = View.topic
        self.subtitle: str = "open (o) | refresh (r) | history (h) | quit (q)"
        self.sub: Optional[Subscription] = None
        self.topic: Optional[Topic] = None

    def live_window(self):
        with Live(self.layout, auto_refresh=False, screen=True, transient=True) as live:
            self._loop(live)

    def _update_panel(self, live: Live) -> None:
        window_layout = Layout()
        view_layout = Layout()
        header = output.header_renderable(self.config)
        if self.content:
            content = Layout(self.content, name="content")
        else:
            content = Layout(name="content", visible=False)
        nav = output.nav_renderable(View, self.view)
        view_layout.split_row(nav, content)
        window_layout.split_column(header, view_layout)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        panel = Panel(
            title=now,
            title_align="right",
            subtitle=self.subtitle,
            renderable=window_layout,
            border_style=const.border_style,
        )
        self.layout = Layout(panel)
        self.panel = panel
        live.update(self.layout, refresh=True)

    def _update_subscription(self, sub: Optional[Subscription]):
        if sub:
            self.sub = sub
            self.content = output.get_subscription_output(self.sub)
            self.history_service.save_subscription(sub)

    def _update_topic(self, topic: Optional[Topic]):
        if topic:
            self.topic = topic
            self.content = output.get_topic_output(self.topic)
            self.history_service.save_topic(topic)

    def _loop(self, live: Live):
        """
        Loop listening on specific keypress, updating live CLI
        """
        self._update_panel(live)
        char = readchar.readkey()

        # Switch to topic view
        if char == "t":
            self.view = View.topic

        # Switch to subscription view
        elif char == "s":
            self.view = View.subscription

        # Open content, based on view
        elif char == "o":
            if self.view == View.topic:
                topic = self.topic_service.get_topic(live)
                self._update_topic(topic)
            elif self.view == View.subscription:
                sub = self.subscription_service.get_subscription(live)
                self._update_subscription(sub)

        # Refresh
        elif char == "r" and self.content:
            flash_panel(live, self.layout, self.panel)
            if self.view == View.topic and self.topic:
                self._update_topic(self.topic)
            elif self.view == View.subscription and self.sub:
                self._update_subscription(self.sub)

        # List history
        elif char == "h":
            if self.view == View.topic:
                topic = self.history_service.pick_topic(live)
                self._update_topic(topic)
            elif self.view == View.subscription:
                sub = self.history_service.pick_subscription(live)
                self._update_subscription(sub)

        # Quit program
        elif char == "q":
            live.stop()
            click.get_current_context().exit()

        # Infinite loop, until quitted (q)
        self._loop(live)
