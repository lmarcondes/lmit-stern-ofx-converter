from re import compile
from datetime import datetime
from typing import Any, Iterable
from functools import reduce
from collections.abc import Callable

from ofx_converter.logger import LogMixin
from .transaction import Transaction


class TransactionParser(LogMixin):
    DATE_COL = "Data"
    DESCRIPTION_COL = "Descricao"
    VALUE_COL = "Valor"
    BALANCE_COL = "Saldo"
    _date_pattern = "^(?P<day>\\d{2})/(?P<month>\\d{2})/(?P<year>\\d{2})[\\s\\w]+(?P<hour>\\d{2}):(?P<min>\\d{2}):(?P<sec>\\d{2})$"
    _value_pattern = "(?P<sign>-)?R\\$ (?P<value>[\\d\\.,]+)$"

    def __init__(self) -> None:
        super().__init__()
        self._date_regex = compile(self._date_pattern)
        self._value_regex = compile(self._value_pattern)

    def _parse_date(self, date: str) -> datetime | None:
        date_obj = self._date_regex.match(date)
        if date_obj is None:
            return None
        date_string = "20{year}-{month}-{day}T{hour}:{min}:{sec}.000-03:00".format(
            **date_obj.groupdict()
        )
        date_converted = datetime.fromisoformat(date_string)
        return date_converted

    def _parse_money(self, value: str) -> float | None:
        value_obj = self._value_regex.match(value)
        if value_obj is None:
            return None
        value_extracted = value_obj["value"].replace(".", "").replace(",", ".")
        sign_extracted = value_obj.groupdict().get("sign")
        value_converted = float(
            "{sign}{value}".format(
                sign=sign_extracted if sign_extracted is not None else "",
                value=value_extracted,
            )
        )
        return value_converted

    def parse(self, record: dict[str, Any]) -> Transaction | None:
        (date, desc, value, balance) = (
            record[self.DATE_COL],
            record[self.DESCRIPTION_COL],
            record[self.VALUE_COL],
            record[self.BALANCE_COL],
        )
        date_parsed = self._parse_date(date)
        value_converted = self._parse_money(value)
        balance_converted = self._parse_money(balance)
        valid_conversions = map(
            lambda x: x is not None, [date_parsed, value_converted, balance_converted]
        )
        reducer: Callable[[bool, bool], bool] = lambda x, y: x and y
        is_valid_transaction = reduce(reducer, valid_conversions)
        if not is_valid_transaction:
            return None
        transaction = Transaction(date_parsed, desc, value_converted, balance_converted)  # type: ignore
        return transaction

    def parse_multiple(self, records: Iterable[dict[str, Any]]) -> list[Transaction | None]:
        transactions = list(map(self.parse, records))
        self.log.info("Parsed %i records into transactions", len(transactions))
        return transactions
