from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ofx_converter.logger import LogMixin
from ofx_converter.parsing.transaction import Transaction
from ofx_converter.parsing.transaction_parser import TransactionParser


class AbstractReader(LogMixin, ABC):

    @abstractmethod
    def read_transactions(
        self, parser: TransactionParser[Any], file_path: Path
    ) -> list[Transaction | None]: ...


class BaseReader(AbstractReader):

    def __init__(self, log_level: int | None = None) -> None:
        super().__init__(log_level)
