from datetime import datetime
from typing import List
import plotext
from rich.ansi import AnsiDecoder
from rich.console import Console, ConsoleOptions, Group, RenderResult
from rich.jupyter import JupyterMixin


class Graph(JupyterMixin):
    def __init__(
        self,
        dates: List[datetime],
        points: List[int],
        title: str = None,
    ):
        self.decoder = AnsiDecoder()
        self.title = title
        self.dates = dates
        self.points = points

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        width = options.max_width or console.width
        height = options.height or console.height
        plotext.clear_figure()
        plotext.date_form("H:M:S")
        plotext.plot_size(width, height)
        plotext.canvas_color("default")
        plotext.axes_color("default")
        plotext.ticks_color("default")
        plotext.title(self.title)
        dates_str = plotext.datetimes_to_string(self.dates)
        plotext.plot(dates_str, self.points)
        canvas = plotext.build()
        self.rich_canvas = Group(*self.decoder.decode(canvas))
        yield self.rich_canvas
