from datetime import datetime
from enum import Enum
from typing import List, Optional

import click
import readchar
from readchar import key
from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.live import Live
from google.pubsub_v1.types.pubsub import Topic
from google.pubsub_v1.types.pubsub import Subscription
from rich.panel import Panel
from rich.padding import Padding
from rich.text import Text
from rich.console import Group

from pubsub_meta import const, output
from pubsub_meta.config import Config
from pubsub_meta.logger import Logger
from pubsub_meta.service.metrics_service import MetricsService
from pubsub_meta.service.subscription_service import SubscriptionService
from pubsub_meta.service.topic_service import TopicService
from pubsub_meta.service.history_service import HistoryService
from pubsub_meta.types import SubscriptionParsed
from pubsub_meta.util.rich_utils import flash_panel


class View(Enum):
    topic = 1
    subscription = 2
    snapshots = 3
    schemas = 4


class Tab(Enum):
    detail = 1
    metrics = 2


class Window:
    def __init__(
        self,
        console: Console,
        logger: Logger,
        config: Config,
        topic_service: TopicService,
        subscription_service: SubscriptionService,
        history_service: HistoryService,
        metrics_service: MetricsService,
    ):
        self.console = console
        self.logger = logger
        self.config = config
        self.subscription_service = subscription_service
        self.topic_service = topic_service
        self.history_service = history_service
        self.metrics_service = metrics_service
        self.layout: Layout = Layout()
        self.content: Optional[RenderableType] = None
        self.view: View = View.topic
        self.tab: Tab = Tab.detail
        self.subtitle: str = "open (o) | refresh (r) | history (h) | quit (q)"
        self.sub: Optional[Subscription] = None
        self.sub_parsed: Optional[SubscriptionParsed] = None
        self.topic: Optional[Topic] = None
        self.now: datetime = None

    def live_window(self):
        with Live(self.layout, auto_refresh=False, screen=True, transient=True) as live:
            self._loop(live)

    def _update_panel(self, live: Live) -> None:
        window_layout = Layout(name="window")
        body_layout = Layout(name="body")
        tabs_content_layout = Layout(name="tabs_content")
        header_layout = output.header_layout(self.config)
        views_layout = output.views_layout(View, self.view)
        content_layout = output.content_layout(self.content)
        tabs_layout = output.tabs_layout(Tab, self.tab)
        tabs_content_layout.split_column(tabs_layout, content_layout)
        body_layout.split_row(views_layout, tabs_content_layout)
        window_layout.split_column(header_layout, body_layout)
        self.now = datetime.now()
        self.panel = Panel(
            title=self.now.strftime("%Y-%m-%d %H:%M:%S"),
            title_align="right",
            subtitle=self.subtitle,
            renderable=window_layout,
            border_style=const.border_style,
        )
        self.layout = Layout(self.panel)
        live.update(self.layout, refresh=True)

    def _update_content(self):
        self.logger.info(f"update content: {self.view}, {self.tab}")
        match (self.view, self.tab):
            case (View.topic, Tab.detail) if self.topic:
                self.content = output.get_topic_output(self.topic)
            case (View.subscription, Tab.detail) if self.sub:
                self.content = output.get_subscription_output(self.sub)
            case (View.subscription, Tab.metrics) if self.sub_parsed:
                dates, points = self.metrics_service.undelivered_messages(
                    self.sub_parsed.project_id,
                    self.sub_parsed.subscription_id,
                    self.now,
                )
                self.content = output.get_subscription_metrics_output(dates, points)
            case _:
                self.content = None

    def _update_subscription(self, sub: Optional[Subscription]):
        if sub:
            self.sub = sub
            self.sub_parsed = SubscriptionParsed.from_subscription(sub.name)
            self.history_service.save_subscription(sub)

    def _update_topic(self, topic: Optional[Topic]):
        if topic:
            self.topic = topic
            self.history_service.save_topic(topic)

    def _loop(self, live: Live):
        """
        Loop listening on specific keypress, updating live CLI
        """
        self._update_panel(live)
        char = readchar.readkey()

        match char:
            case key.UP:
                idx = max([list(View)[0].value, self.view.value - 1])
                self.view = View(idx)

            case key.DOWN:
                idx = min([list(View)[-1].value, self.view.value + 1])
                self.view = View(idx)

            case key.LEFT:
                idx = max([list(Tab)[0].value, self.tab.value - 1])
                self.tab = Tab(idx)

            case key.RIGHT:
                idx = min([list(Tab)[-1].value, self.tab.value + 1])
                self.tab = Tab(idx)

            case "1":
                self.view = View.topic

            case "2":
                self.view = View.subscription

            case "3":
                self.view = View.snapshots

            case "4":
                self.view = View.schemas

            case key.F1:
                self.tab = Tab.detail

            case key.F2:
                self.tab = Tab.metrics

            # Open - topic
            case "o" if self.view == View.topic:
                topic = self.topic_service.pick_topic(live)
                self._update_topic(topic)

            # Open - subscription
            case "o" if self.view == View.subscription:
                sub = self.subscription_service.pick_subscription(live)
                self._update_subscription(sub)

            # Refresh - topic
            case "r" if self.view == View.topic and self.topic:
                flash_panel(live, self.layout, self.panel)
                self._update_topic(self.topic)

            # Refresh - subscription
            case "r" if self.view == View.subscription and self.sub:
                flash_panel(live, self.layout, self.panel)
                self._update_subscription(self.sub)

            # History - topic
            case "h" if self.view == View.topic:
                topic = self.history_service.pick_topic(live)
                self._update_topic(topic)

            # History - subscription
            case "h" if self.view == View.subscription:
                sub = self.history_service.pick_subscription(live)
                self._update_subscription(sub)

            # Quit program
            case "q":
                live.stop()
                click.get_current_context().exit()

        # Infinite loop, until quitted (q)
        self._update_content()
        self._loop(live)
