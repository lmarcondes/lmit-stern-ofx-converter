from csv import DictReader
from pathlib import Path
from typing import Any

from ofx_converter.parsing.transaction import Transaction
from ofx_converter.parsing.transaction_parser import TransactionParser
from ofx_converter.reader.abstract_reader import BaseReader


class CSVReader(BaseReader):

    def __init__(
        self,
        delimiter: str,
        encoding: str = "utf-8",
        quote_char: str = '"',
        newline: str = "",
        **_: Any
    ) -> None:
        self._delimiter = delimiter
        self._encoding = encoding
        self._quote_char = quote_char
        self._newline = newline

    def read_transactions(
        self, parser: TransactionParser[dict[str, Any]], file_path: Path
    ) -> list[Transaction | None]:
        with open(
            file_path, newline=self._newline, mode="r", encoding=self._encoding
        ) as csvfile:
            reader = DictReader(
                csvfile, delimiter=self._delimiter, quotechar=self._quote_char
            )
            transactions = parser.parse_multiple(reader)
        return transactions
