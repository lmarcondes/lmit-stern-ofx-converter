from re import compile
from datetime import datetime
from typing import Any

from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.date_parser import DateParser
from ofx_converter.parsing.money_parser import MoneyParser
from ofx_converter.parsing.transaction import Transaction
from ofx_converter.parsing.transaction_parser import TransactionParser


class XPTransactionParser(TransactionParser):
    DATE_COL = "Data"
    DESCRIPTION_COL = "Descricao"
    VALUE_COL = "Valor"
    BALANCE_COL = "Saldo"
    _date_pattern = "^(?P<day>\\d{2})/(?P<month>\\d{2})/(?P<year>\\d{2})[\\s\\w]+(?P<hour>\\d{2}):(?P<min>\\d{2}):(?P<sec>\\d{2})$"
    _value_pattern = "(?P<sign>-)?R\\$ (?P<value>[\\d\\.,]+)$"

    def __init__(self, account: AccountConfig) -> None:
        super().__init__(account)
        date_regex = compile(self._date_pattern)
        value_regex = compile(self._value_pattern)
        self._money_parser = MoneyParser(account, value_regex)
        self._date_parser = DateParser(date_regex)

    def parse(self, record: dict[str, Any]) -> Transaction | None:
        (date, desc, value, balance) = (
            record.get(self.DATE_COL),
            record.get(self.DESCRIPTION_COL),
            record.get(self.VALUE_COL),
            record.get(self.BALANCE_COL),
        )
        date_parsed = self._date_parser.parse(date)
        value_converted = self._money_parser.parse(value)
        balance_converted = self._money_parser.parse(balance)
        transaction = Transaction(date_parsed, desc, value_converted, balance_converted)  # type: ignore
        self._log.info(str(transaction))
        if not transaction.is_valid:
            return None
        return transaction


class XPCardTransactionParser(XPTransactionParser):
    DESCRIPTION_COL = "Estabelecimento"
    _date_pattern = "^(?P<day>\\d{2})/(?P<month>\\d{2})/(?P<year>\\d{4})$"
    _value_pattern = "R\\$ (?P<sign>-)?(?P<value>[\\d\\.,]+)$"
