import sys
from abc import ABC
from logging import INFO, Formatter, Logger, StreamHandler

from ofx_converter.config import get_settings


def get_logger(name: str, level: int = INFO) -> Logger:
    logger = Logger(name, level)
    formatter = Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    handler = StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class LogMixin(ABC):

    def __init__(self, level: int | None = None) -> None:
        super().__init__()
        self._level = level
        if level is None:
            default_level = get_settings().get("log").get("level")
            if default_level is not None:
                level = int(default_level)
            else:
                level = INFO
        self._log = get_logger(self.__class__.__name__, level)

    @property
    def log(self) -> Logger:
        return self._log
