from google.cloud.pubsub_v1 import PublisherClient
from google.cloud.pubsub_v1 import SubscriberClient
from google.cloud.resourcemanager import ProjectsClient
from google.oauth2.credentials import Credentials
from rich.console import Console
from rich.text import Text

from pubsub_meta import const
from pubsub_meta.config import Config


class Client:
    def __init__(self, console: Console, config: Config):
        self._projects_client = None
        self._publisher_client = None
        self._subscriber_client = None
        self.console = console
        self.config = config
        
    @property
    def credentials(self) -> ProjectsClient:
        return Credentials.from_authorized_user_info(self.config.credentials)

    @property
    def publisher_client(self) -> PublisherClient:
        if not self._publisher_client:
            with self.console.status(Text("Connecting to the API", style=const.darker_style), spinner="point"):
                self._publisher_client = PublisherClient(credentials=self.credentials)
        return self._publisher_client
    
    @property
    def subscriber_client(self) -> SubscriberClient:
        if not self._subscriber_client:
            with self.console.status(Text("Connecting to the API", style=const.darker_style), spinner="point"):
                self._subscriber_client = SubscriberClient(credentials=self.credentials)
        return self._subscriber_client

    @property
    def projects_client(self) -> ProjectsClient:
        if not self._projects_client:
            with self.console.status(Text("Connecting to the API", style=const.darker_style), spinner="point"):
                self._projects_client = ProjectsClient(credentials=self.credentials)
        return self._projects_client
