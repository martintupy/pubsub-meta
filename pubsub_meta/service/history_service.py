from typing import List, Optional

from pubsub_meta import const
from pubsub_meta.config import Config
from pubsub_meta.service.topic_service import TopicService
from pubsub_meta.service.subscription_service import SubscriptionService
from pubsub_meta.util import bash_util
from rich.console import Console
from rich.live import Live
from google.pubsub_v1.types.pubsub import Subscription, Topic


class HistoryService:
    def __init__(
        self,
        console: Console,
        config: Config,
        topic_service: TopicService,
        subscription_service: SubscriptionService,
    ) -> None:
        self.console = console
        self.config = config
        self.topic_service = topic_service
        self.subscription_service = subscription_service
        self.topic_path = const.PUBSUB_META_TOPIC_HISTORY
        self.subscription_path = const.PUBSUB_META_SUBSCRIPTION_HISTORY

    def list_topics(self) -> List[str]:
        topics = open(self.topic_path, "r").read().splitlines()
        return topics

    def list_subscriptions(self) -> List[str]:
        subs = open(self.subscription_path, "r").read().splitlines()
        return subs

    def save_topic(self, topic: Topic):
        topics = self.list_topics()
        try:
            topics.remove(topic.name)
        except ValueError:
            pass
        topics.append(topic.name)
        with open(self.topic_path, "w") as f:
            f.write("\n".join(topics))

    def save_subscription(self, sub: Subscription):
        subs = self.list_subscriptions()
        try:
            subs.remove(sub.name)
        except ValueError:
            pass
        subs.append(sub.name)
        with open(self.subscription_path, "w") as f:
            f.write("\n".join(subs))

    def pick_topic(self, live: Live) -> Optional[Topic]:
        topics = self.list_topics()
        topic_name = bash_util.pick_one(topics, live)
        topic = self.topic_service.get_topic(topic_name)
        return topic

    def pick_subscription(self, live: Live) -> Optional[Subscription]:
        subs = self.list_subscriptions()
        sub_name = bash_util.pick_one(subs, live)
        subscription = self.subscription_service.get_subscription(sub_name)
        return subscription
