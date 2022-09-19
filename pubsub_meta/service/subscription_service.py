from typing import Optional

from google.pubsub_v1.services.subscriber.pagers import ListSubscriptionsPager
from google.pubsub_v1.types.pubsub import Subscription
from pubsub_meta.client import Client
from pubsub_meta.config import Config
from pubsub_meta.service.project_service import ProjectService
from pubsub_meta.util import bash_util
from pubsub_meta.util.rich_utils import progress
from rich.console import Console
from rich.live import Live


class SubscriptionService:
    def __init__(
        self,
        console: Console,
        config: Config,
        client: Client,
        project_service: ProjectService,
    ) -> None:
        self.console = console
        self.config = config
        self.client = client
        self.project_service = project_service

    def get_subscription(self, sub_name: str) -> Optional[Subscription]:
        return self.client.subscriber_client.get_subscription(subscription=sub_name)

    def pick_subscription(self, live: Live) -> Optional[Subscription]:
        subscription = None
        sub_name = None
        project_id = self._pick_project_id(live)
        if project_id:
            sub_name = self._pick_subscription(project_id, live)
        if sub_name:
            subscription = self.client.subscriber_client.get_subscription(subscription=sub_name)
        return subscription

    # ======================   Pick   ======================

    def _pick_project_id(self, live: Live) -> Optional[str]:
        project_ids = self.project_service.list_projects()
        return bash_util.pick_one(project_ids, live)

    def _pick_subscription(self, project_id: str, live: Live) -> Optional[str]:
        subscriptions = []
        subs = self.client.subscriber_client.list_subscriptions(project=f"projects/{project_id}")
        subs_progress: ListSubscriptionsPager = progress(self.console, "subscriptions", subs)
        for subscription in subs_progress:
            subscriptions.append(subscription.name)
        return bash_util.pick_one(subscriptions, live)
