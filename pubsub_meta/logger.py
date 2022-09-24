import logging
from logging import LogRecord

from pubsub_meta import const

COLORS = {"INFO": "00AD3A", "WARNING": "EF8D49", "ERROR": "CD0F0F", "DEBUG": "FFFFFF"}


def rgb(r: int, g: int, b: int):
    def inner(text):
        return f"\x1b[38;2;{r};{g};{b}m{text}\x1b[0m"

    return inner


def hex(hexstr: str):
    return rgb(*tuple(int(hexstr.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)))


class ColoredFormatter(logging.Formatter):
    def format(self, record: LogRecord) -> str:
        levelname = record.levelname
        record.threadName = hex("BD4CBF")(record.threadName)
        record.filename = hex("D28CCA")(f"{record.filename}:{record.lineno}")
        if levelname in COLORS:
            record.levelname = hex(COLORS[levelname])(levelname)
        return super().format(record)

    def formatTime(self, record: LogRecord, datefmt) -> str:
        dt = super().formatTime(record, datefmt=datefmt).split(" ")
        date = hex("0F72CD")(dt[0])
        time = hex("4393DC")(dt[1])
        return f"{date} {time}"


class Logger(logging.Logger):
    def __init__(self, name):
        logging.Logger.__init__(self, name)
        fmt = "%(levelname)s %(asctime)s %(threadName)s %(filename)s - %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        color_formatter = ColoredFormatter(fmt, datefmt)
        console = logging.FileHandler(const.PUBSUB_META_LOG)
        console.setFormatter(color_formatter)
        self.addHandler(console)
