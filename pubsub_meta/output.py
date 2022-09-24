from typing import List, Optional

from google.pubsub_v1.types.pubsub import Subscription, Topic
from packaging import version
from rich.align import Align
from rich.columns import Columns
from rich.console import Group, NewLine, RenderableType
from rich.layout import Layout
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from pubsub_meta import const
from pubsub_meta.config import Config
from pubsub_meta.window import Nav, Tab

title = """
█▀▄ █ █ ██▄ ▄▀▀ █ █ ██▄   █▄ ▄█ ██▀ ▀█▀ ▄▀▄ █▀▄ ▄▀▄ ▀█▀ ▄▀▄
█▀  ▀▄█ █▄█ ▄██ ▀▄█ █▄█   █ ▀ █ █▄▄  █  █▀█ █▄▀ █▀█  █  █▀█
"""


def header_layout(config: Config) -> Layout:
    header_title = Align(title, align="center", style=const.info_style)
    header = Layout(name="header", size=4)
    left = version_layout(config)
    mid = Layout(header_title)
    right = Layout(NewLine(), size=20)
    header.split_row(left, mid, right)
    return header


def version_layout(config: Config) -> Layout:
    if config.current_version and config.available_version:
        current = version.parse(config.current_version)
        available = version.parse(config.available_version)
        if current < available:
            version_text = Text(f"{current} ► {available}", style=const.darker_style)
        else:
            version_text = Text(f"{current}", style=const.darker_style)
    else:
        version_text = Text(" ", style=const.darker_style)
    return Layout(version_text, size=20)


def nav_layout(navs: List[Nav], selected: Nav) -> Layout:
    separator = Rule(style=const.darker_style)
    nav_list: list[RenderableType] = []
    for nav in navs:
        if nav == selected:
            text = Text(f"● {nav.name}", style=const.info_style)
        else:
            text = Text(f"  {nav.name}", style="default")
        nav_list.extend([text, separator])
    panel = Panel(Group(*nav_list), style=const.darker_style)
    return Layout(panel, name="nav", size=20)


def tabs_layout(tabs: List[Tab], selected: Tab) -> Layout:
    separator = Text("|", style=const.darker_style)
    tab_list = []
    for tab in tabs:
        if tab == selected:
            text = Text(f"{tab.name}", style=const.info_style)
        else:
            text = Text(f"{tab.name}", style="default")
        tab_list.extend([text, separator])
    panel = Panel(Columns(tab_list), style=const.darker_style)
    return Layout(panel, name="tab", size=3)


def content_layout(renderable: Optional[RenderableType]) -> Layout:
    if renderable:
        content = Panel(renderable, style=const.darker_style)
    else:
        content = Panel(NewLine(), style=const.darker_style)
    return Layout(content, name="content")


def get_init_output() -> Panel:
    return Panel(
        title="Not initialized, run",
        renderable=Text("pubsub-meta --init"),
        expand=False,
        padding=(1, 3),
        border_style=const.request_style,
    )


def get_config_info(config: Config) -> Group:
    return Group(text_tuple("Account", config.account))


def get_subscription_output(sub: Subscription) -> Group:
    return Group(
        text_tuple("Name", sub.name),
        text_tuple("Topic", sub.topic),
        text_tuple("Labels", sub.labels),
        text_tuple("Ack deadline seconds", sub.ack_deadline_seconds),
        text_tuple("Topic message duration", sub.topic_message_retention_duration),
        Rule(style=const.darker_style),
        text_tuple("Enable exactly once delivery", sub.enable_exactly_once_delivery),
        text_tuple("Enable message ordering", sub.enable_message_ordering),
        text_tuple("Retain acked messages", sub.retain_acked_messages),
        text_tuple("Detached", sub.detached),
        Rule(style=const.darker_style),
        text_tuple("Push config", sub.bigquery_config),
        text_tuple("BigQuery config", sub.bigquery_config),
        Rule(style=const.darker_style),
        text_tuple("Dead letter policy", sub.dead_letter_policy),
        text_tuple("Retry policy", sub.retry_policy),
        text_tuple("Expiration policy", sub.expiration_policy),
        Rule(style=const.darker_style),
        text_tuple("Filter", sub.filter),
        text_tuple("State", sub.state),
    )


def get_topic_output(topic: Topic) -> Group:
    return Group(
        text_tuple("Topic name", topic.name),
        text_tuple("Labels", topic.labels),
        text_tuple("Schema settings", topic.schema_settings),
    )


def text_tuple(name: str, value) -> Text:
    text = None
    if isinstance(value, Text):
        text = value
    else:
        text = Text(str(value), style="default")
    return Text(name, style=const.key_style).append(" = ", style=const.darker_style).append(text)
