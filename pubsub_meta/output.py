from typing import List
from packaging import version
from rich.align import Align
from rich.console import Group, NewLine
from rich.layout import Layout
from rich.rule import Rule
from rich.panel import Panel
from rich.text import Text
from google.pubsub_v1.types.pubsub import Topic, Subscription

from pubsub_meta import const
from pubsub_meta.config import Config
from pubsub_meta.window import View

title = """
█▀▄ █ █ ██▄ ▄▀▀ █ █ ██▄   █▄ ▄█ ██▀ ▀█▀ ▄▀▄ █▀▄ ▄▀▄ ▀█▀ ▄▀▄
█▀  ▀▄█ █▄█ ▄██ ▀▄█ █▄█   █ ▀ █ █▄▄  █  █▀█ █▄▀ █▀█  █  █▀█
"""


def header_renderable(config: Config) -> Layout:
    header_title = Align(title, align="center", style=const.info_style)
    header = Layout(name="header", size=4)
    left = version_renderable(config)
    mid = Layout(header_title)
    right = Layout(NewLine(), size=20)
    header.split_row(left, mid, right)
    return header


def version_renderable(config: Config) -> Layout:
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


def nav_renderable(views: List[View], selected: View) -> Layout:
    view_list = []
    for view in views:
        if view == selected:
            view_list.append(Text(view.name, style=const.info_style))
        else:
            view_list.append(Text(view.name, style=const.darker_style))
    nav = Group(*view_list)
    return Layout(nav, name="nav", size=30)


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
        Rule(style=const.darker_style),
        text_tuple("Name", sub.name),
        text_tuple("Topic", sub.topic),
        text_tuple("Ack deadline seconds", sub.ack_deadline_seconds),
        Rule(style=const.darker_style),
    )


def get_topic_output(topic: Topic) -> Group:
    return Group(
        Rule(style=const.darker_style),
        text_tuple("Topic name", topic.name),
        text_tuple("Labels", topic.labels),
        text_tuple("Schema settings", topic.schema_settings),
        Rule(style=const.darker_style),
    )


def text_tuple(name: str, value) -> Text:
    text = None
    if isinstance(value, Text):
        text = value
    else:
        text = Text(str(value), style="default")
    return Text(name, style=const.key_style).append(" = ", style=const.darker_style).append(text)
