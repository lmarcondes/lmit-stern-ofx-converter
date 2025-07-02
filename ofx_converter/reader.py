from abc import ABC, abstractmethod
from pathlib import Path

from ofx_converter.logger import LogMixin
from ofx_converter.parsing.transaction import Transaction
from ofx_converter.parsing.transaction_parser import TransactionParser
from csv import DictReader


class AbstractReader(LogMixin, ABC):

    @abstractmethod
    def read_transactions(
        self, parser: TransactionParser, file_path: Path
    ) -> list[Transaction | None]: ...


class BaseReader(AbstractReader):

    def __init__(self, log_level: int | None = None) -> None:
        super().__init__(log_level)


class CSVReader(BaseReader):

    def __init__(
        self, delimiter: str, encoding: str = "utf-8", quote_char: str = '"', newline=""
    ) -> None:
        self._delimiter = delimiter
        self._encoding = encoding
        self._quote_char = quote_char
        self._newline = newline

    def read_transactions(
        self, parser: TransactionParser, file_path: Path
    ) -> list[Transaction | None]:
        with open(
            file_path, newline=self._newline, mode="r", encoding=self._encoding
        ) as csvfile:
            reader = DictReader(
                csvfile, delimiter=self._delimiter, quotechar=self._quote_char
            )
            transactions = parser.parse_multiple(reader)
        return transactions
