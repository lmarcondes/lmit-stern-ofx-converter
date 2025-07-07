from abc import ABC, abstractmethod
from typing import Iterable

from ofx_converter.config import get_settings
from ofx_converter.logger import LogMixin
from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.transaction import Transaction


class TransactionParser[A](LogMixin, ABC):

    def __init__(self, account: AccountConfig) -> None:
        super().__init__()
        self._settings = get_settings()
        self._account_config = account

    @abstractmethod
    def parse(self, record: A) -> Transaction | None: ...

    def parse_multiple(self, records: Iterable[A]) -> list[Transaction | None]:
        transactions = list(map(self.parse, records))
        self.log.info("Parsed %i records into transactions", len(transactions))
        return transactions
