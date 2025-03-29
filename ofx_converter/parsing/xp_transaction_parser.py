from re import compile
from datetime import datetime
from typing import Any, Literal

from ofx_converter.parsing.account_config import AccountConfig
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
        self._date_regex = compile(self._date_pattern)
        self._value_regex = compile(self._value_pattern)

    def _make_iso_string(self, **match_dict: str) -> str:
        date_string = "20{year}-{month}-{day}T{hour}:{min}:{sec}.000-03:00".format(
            **match_dict
        )
        return date_string

    def _parse_date(self, date: str | None) -> datetime | None:
        if date is None:
            return None
        date_obj = self._date_regex.match(date)
        if date_obj is None:
            return None
        date_string = self._make_iso_string(**date_obj.groupdict())
        date_converted = datetime.fromisoformat(date_string)
        return date_converted

    def _extract_value(self, value: str) -> float | None:
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

    def _get_credit_debit_sign(self) -> Literal[-1, 1]:
        if self._account_config.account_type.is_liability:
            sign = -1
        else:
            sign = 1
        return sign

    def _parse_money(self, value: str | None) -> float | None:
        if value is None:
            return None
        value_converted = self._extract_value(value)
        if value_converted is None:
            return None
        value_signed = self._get_credit_debit_sign() * value_converted
        return value_signed

    def parse(self, record: dict[str, Any]) -> Transaction | None:
        (date, desc, value, balance) = (
            record.get(self.DATE_COL),
            record.get(self.DESCRIPTION_COL),
            record.get(self.VALUE_COL),
            record.get(self.BALANCE_COL),
        )
        date_parsed = self._parse_date(date)
        value_converted = self._parse_money(value)
        balance_converted = self._parse_money(balance)
        transaction = Transaction(date_parsed, desc, value_converted, balance_converted)  # type: ignore
        self._log.info(str(transaction))
        if not transaction.is_valid:
            return None
        return transaction


class XPCardTransactionParser(XPTransactionParser):
    DESCRIPTION_COL = "Estabelecimento"
    _date_pattern = "^(?P<day>\\d{2})/(?P<month>\\d{2})/(?P<year>\\d{4})$"

    def _make_iso_string(self, **match_dict: str) -> str:
        date_string = "{year}-{month}-{day}".format(**match_dict)
        return date_string
