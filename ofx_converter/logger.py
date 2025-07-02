from abc import ABC
from logging import Logger, INFO, StreamHandler
import sys

from ofx_converter.config import get_settings


def get_logger(name: str, level: int = INFO) -> Logger:
    logger = Logger(name, level)
    logger.addHandler(StreamHandler(sys.stdout))
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
