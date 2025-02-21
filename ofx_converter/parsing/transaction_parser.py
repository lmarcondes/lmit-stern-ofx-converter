from typing import Any, Iterable
from abc import ABC, abstractmethod

from ofx_converter.logger import LogMixin
from ofx_converter.parsing.transaction import Transaction

class TransactionParser(LogMixin, ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def parse(self, record: dict[str, Any]) -> Transaction | None:
        ...

    def parse_multiple(self, records: Iterable[dict[str, Any]]) -> list[Transaction | None]:
        transactions = list(map(self.parse, records))
        self.log.info("Parsed %i records into transactions", len(transactions))
        return transactions
