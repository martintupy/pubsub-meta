from typing import Optional
from pubsub_meta.config import Config
from pubsub_meta.client import Client
from rich.console import Console
from rich.live import Live
from pubsub_meta.util.rich_utils import progress
from pubsub_meta.util import bash_util
from google.pubsub_v1.types.pubsub import Topic
from pubsub_meta.service.project_service import ProjectService
from google.pubsub_v1.services.publisher.pagers import ListTopicsPager


class TopicService:
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

    def get_topic(self, topic_name: str) -> Optional[Topic]:
        return self.client.publisher_client.get_topic(topic=topic_name)

    def pick_topic(self, live: Live) -> Optional[Topic]:
        topic = None
        topic_name = None
        project_id = self._pick_project_id(live)
        if project_id:
            topic_name = self._pick_topic_name(project_id, live)
        if topic_name:
            topic = self.client.publisher_client.get_topic(topic=topic_name)
        return topic

    # ======================   Pick   ======================

    def _pick_project_id(self, live: Live) -> Optional[str]:
        project_ids = self.project_service.list_projects()
        return bash_util.pick_one(project_ids, live)

    def _pick_topic_name(self, project_id: str, live: Live) -> Optional[str]:
        topic_names = []
        topics = self.client.publisher_client.list_topics(project=f"projects/{project_id}")
        topics_progress: ListTopicsPager = progress(self.console, "topics", topics)
        for topic in topics_progress:
            topic_names.append(topic.name)
        return bash_util.pick_one(topic_names, live)
