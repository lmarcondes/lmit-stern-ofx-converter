from abc import ABC
from logging import Logger, INFO, StreamHandler
import sys

def get_logger(name: str, level: int = INFO) -> Logger:
    logger = Logger(name, level)
    logger.addHandler(StreamHandler(sys.stdout))
    return logger

class LogMixin(ABC):

    def __init__(self, level: int = INFO) -> None:
        super().__init__()
        self._level = level
        self._log = get_logger(self.__class__.__name__, level)

    @property
    def log(self) -> Logger:
        return self._log
