from pathlib import Path

from rich.console import Console, Group, NewLine
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from pubsub_meta import const
from pubsub_meta.auth import Auth
from pubsub_meta.config import Config
from pubsub_meta.service.project_service import ProjectService


def initialize(config: Config, console: Console, project_service: ProjectService):
    pubsub_meta_home = Prompt.ask(
        Text("", style=const.darker_style).append("Enter pubsub_meta home path", style=const.request_style),
        default=const.DEFAULT_PUBSUB_META_HOME,
        console=console,
    )

    Path(pubsub_meta_home).mkdir(parents=True, exist_ok=True)
    _print_created(console, pubsub_meta_home)
    Path(const.PUBSUB_META_CONFIG).touch()
    config.write_default()
    _print_created(console, const.PUBSUB_META_CONFIG)
    Path(const.PUBSUB_META_PROJECTS).touch()
    _print_created(console, const.PUBSUB_META_PROJECTS)
    Path(const.PUBSUB_META_LOG).touch()
    _print_created(console, const.PUBSUB_META_LOG)
    Path(const.PUBSUB_META_HISTORY).mkdir(parents=True, exist_ok=True)
    _print_created(console, const.PUBSUB_META_HISTORY)
    Path(const.PUBSUB_META_TOPIC_HISTORY).touch()
    _print_created(console, const.PUBSUB_META_TOPIC_HISTORY)
    Path(const.PUBSUB_META_SUBSCRIPTION_HISTORY).touch()
    _print_created(console, const.PUBSUB_META_SUBSCRIPTION_HISTORY)

    Prompt.ask(
        Text("", style=const.darker_style).append("Login to google account", style=const.request_style),
        choices=None,
        default="Press enter",
        console=console,
    )
    auth = Auth(config, console)
    auth.login()

    project_service.fetch_projects()

    if pubsub_meta_home != const.DEFAULT_PUBSUB_META_HOME:
        group = Group(Text(f"export PUBSUB_META_HOME={pubsub_meta_home}"))
        console.print(
            NewLine(),
            Panel(
                title="Export following to your environment",
                renderable=group,
                expand=False,
                padding=(1, 3),
                border_style=const.request_style,
            ),
        )


def _print_created(console: Console, path: str):
    console.print(Text("Created", style=const.info_style).append(f": {path}", style=const.darker_style))
