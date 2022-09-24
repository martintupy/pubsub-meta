from datetime import datetime

from google.pubsub_v1.types.pubsub import Subscription
from pubsub_meta.graph import Graph
from pubsub_meta.logger import Logger
from pubsub_meta.service.metrics_service import MetricsService
from pubsub_meta.types import SubscriptionParsed
from rich.layout import Layout
from rich.console import NewLine
from rich.panel import Panel


class MetricsView:
    def __init__(self, logger: Logger, metrics_service: MetricsService) -> None:
        self.logger = logger
        self.metrics_service = metrics_service

    def get_metrics_output(self, sub: Subscription, now: datetime) -> Layout:
        layout = Layout()
        row1 = Layout(size=15)
        sub_parsed = SubscriptionParsed.from_subscription(sub.name)

        dates, points = self.metrics_service.get_sent_messages(
            sub_parsed.project_id,
            sub_parsed.subscription_id,
            now,
        )
        sent_message_count = Layout(Graph(dates, points, "sent_message_count"), size=60)

        dates, points = self.metrics_service.get_undelivered_messages(
            sub_parsed.project_id,
            sub_parsed.subscription_id,
            now,
        )
        num_undelivered_messages = Layout(Graph(dates, points, "num_undelivered_messages"), size=60)

        row1.split_row(sent_message_count, num_undelivered_messages, NewLine())
        layout.split_column(row1)
        return layout
