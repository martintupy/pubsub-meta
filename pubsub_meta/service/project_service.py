from typing import List

from pubsub_meta import const
from pubsub_meta.client import Client
from pubsub_meta.config import Config
from rich.console import Console

from pubsub_meta.util.rich_utils import progress


class ProjectService:
    def __init__(self, console: Console, config: Config, client: Client) -> None:
        self.console = console
        self.config = config
        self.client = client
        self.projects_path = const.PUBSUB_META_PROJECTS

    def list_projects(self) -> List[str]:
        projects = open(self.projects_path, "r").read().splitlines()
        return projects

    def fetch_projects(self):
        projects_ids = []
        projects = self.client.projects_client.search_projects()
        for project in progress(self.console, "projects", projects):
            if not str(project.project_id).startswith("sys-"):
                projects_ids.append(project.project_id)
        projects_ids.sort()
        with open(self.projects_path, "w") as f:
            f.write("\n".join(projects_ids))
