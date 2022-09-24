from datetime import datetime
from enum import Enum
from typing import Optional

import click
import readchar
from google.pubsub_v1.types.pubsub import Subscription, Topic
from readchar import key
from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel

from pubsub_meta import const, output
from pubsub_meta.config import Config
from pubsub_meta.logger import Logger
from pubsub_meta.service.history_service import HistoryService
from pubsub_meta.service.metrics_service import MetricsService
from pubsub_meta.view.metrics_view import MetricsView
from pubsub_meta.service.subscription_service import SubscriptionService
from pubsub_meta.service.topic_service import TopicService
from pubsub_meta.types import SubscriptionParsed
from pubsub_meta.util.rich_utils import flash_panel


class Nav(Enum):
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
        self.console: Console = console
        self.logger: Logger = logger
        self.config: Config = config
        self.subscription_service: SubscriptionService = subscription_service
        self.topic_service: TopicService = topic_service
        self.history_service: HistoryService = history_service
        self.metrics_service: MetricsService = metrics_service
        self.metrics_view: MetricsView = MetricsView(logger, metrics_service)
        self.layout: Layout = Layout()
        self.content: Optional[RenderableType] = None
        self.nav: Nav = Nav.topic
        self.tab: Tab = Tab.detail
        self.subtitle: str = "open (o) | refresh (r) | history (h) | quit (q)"
        self.sub: Optional[Subscription] = None
        self.sub_parsed: Optional[SubscriptionParsed] = None
        self.topic: Optional[Topic] = None
        self.now: datetime = datetime.utcnow()

    def live_window(self):
        self.now = datetime.utcnow()
        self.topic = self.history_service.last_topic()
        self.sub = self.history_service.last_subscription()
        with Live(self.layout, auto_refresh=False, screen=True, transient=True) as live:
            self._loop(live)

    def _update_panel(self, live: Live) -> None:
        window_layout = Layout(name="window")
        body_layout = Layout(name="body")
        tabs_content_layout = Layout(name="tabs_content")
        header_layout = output.header_layout(self.config)
        nav_layout = output.nav_layout(list(Nav), self.nav)
        content_layout = output.content_layout(self.content)
        tabs_layout = output.tabs_layout(list(Tab), self.tab)
        tabs_content_layout.split_column(tabs_layout, content_layout)
        body_layout.split_row(nav_layout, tabs_content_layout)
        window_layout.split_column(header_layout, body_layout)
        self.panel = Panel(
            title=self.now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            title_align="right",
            subtitle=self.subtitle,
            renderable=window_layout,
            border_style=const.border_style,
            padding=0,
        )
        self.layout = Layout(self.panel)
        live.update(self.layout, refresh=True)

    def _update_content(self):
        self.logger.info(f"Content: {self.nav}, {self.tab}")
        match (self.nav, self.tab):
            case (Nav.topic, Tab.detail) if self.topic:
                self.content = output.get_topic_output(self.topic)
            case (Nav.subscription, Tab.detail) if self.sub:
                self.content = output.get_subscription_output(self.sub)
            case (Nav.subscription, Tab.metrics) if self.sub:
                self.content = self.metrics_view.get_metrics_output(self.sub, self.now)
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
        self._update_content()
        self._update_panel(live)
        char = readchar.readkey()

        match char:
            case key.UP:
                idx = max([list(Nav)[0].value, self.nav.value - 1])
                self.nav = Nav(idx)

            case key.DOWN:
                idx = min([list(Nav)[-1].value, self.nav.value + 1])
                self.nav = Nav(idx)

            case key.LEFT:
                idx = max([list(Tab)[0].value, self.tab.value - 1])
                self.tab = Tab(idx)

            case key.RIGHT:
                idx = min([list(Tab)[-1].value, self.tab.value + 1])
                self.tab = Tab(idx)

            case "1":
                self.nav = Nav.topic

            case "2":
                self.nav = Nav.subscription

            case "3":
                self.nav = Nav.snapshots

            case "4":
                self.nav = Nav.schemas

            case key.F1:
                self.tab = Tab.detail

            case key.F2:
                self.tab = Tab.metrics

            # Open - topic
            case "o" if self.nav == Nav.topic:
                topic = self.topic_service.pick_topic(live)
                self._update_topic(topic)

            # Open - subscription
            case "o" if self.nav == Nav.subscription:
                sub = self.subscription_service.pick_subscription(live)
                self._update_subscription(sub)

            # Refresh
            case "r":
                flash_panel(live, self.layout, self.panel)
                self.now = datetime.utcnow()
                self._update_topic(self.topic)
                self._update_subscription(self.sub)

            # History - topic
            case "h" if self.nav == Nav.topic:
                topic = self.history_service.pick_topic(live)
                self._update_topic(topic)

            # History - subscription
            case "h" if self.nav == Nav.subscription:
                sub = self.history_service.pick_subscription(live)
                self._update_subscription(sub)

            # Quit program
            case "q":
                live.stop()
                click.get_current_context().exit()

        # Infinite loop, until quitted (q)
        self._loop(live)
