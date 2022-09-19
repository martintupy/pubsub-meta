import os

import click
from rich.console import Console

from pubsub_meta import const, output
from pubsub_meta.client import Client
from pubsub_meta.config import Config
from pubsub_meta.initialize import initialize
from pubsub_meta.service.history_service import HistoryService
from pubsub_meta.service.metrics_service import MetricsService
from pubsub_meta.service.topic_service import TopicService
from pubsub_meta.service.subscription_service import SubscriptionService
from pubsub_meta.service.project_service import ProjectService
from pubsub_meta.service.version_service import VersionService
from pubsub_meta.window import Window
from pubsub_meta.logger import Logger
import plotext


@click.command()
@click.option("--init", help="Initialize 'pubsub-meta' configuration", is_flag=True)
@click.option("--info", help="Print info of currently used account", is_flag=True)
@click.option("--fetch-projects", help="Fetch available google projects", is_flag=True)
@click.version_option()
def cli(
    init: bool,
    info: bool,
    fetch_projects: bool,
):
    """Pub/Sub metadata"""

    ctx = click.get_current_context()
    console = Console(theme=const.theme, soft_wrap=True, force_interactive=True)
    config = Config()
    logger = Logger("pubsub-meta")
    client = Client(console, config)
    project_service = ProjectService(console, config, client)
    topic_service = TopicService(console, config, client, project_service)
    subscription_service = SubscriptionService(console, config, client, project_service)
    history_service = HistoryService(console, config, topic_service, subscription_service)
    metrics_service = MetricsService(client, logger)
    window = Window(console, logger, config, topic_service, subscription_service, history_service, metrics_service)
    logger.info("Init")

    plotext.date_form("H:M:S")
    plotext.plot_size(60, 15)
    plotext.canvas_color("default")
    plotext.axes_color("default")
    plotext.ticks_color("default")

    if os.path.exists(const.PUBSUB_META_CONFIG):
        version_service = VersionService()
        version_service.update_config(config)

    if init:
        initialize(config, console, project_service)
        ctx.exit()
    elif not os.path.exists(const.PUBSUB_META_HOME):
        console.print(output.get_init_output())
        ctx.exit()
    elif info:
        console.print(output.get_config_info(config))
        ctx.exit()
    elif fetch_projects:
        project_service.fetch_projects()
        ctx.exit()

    window.live_window()
