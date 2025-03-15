from typing import Literal
from ofx_converter.logger import LogMixin
from ofx_converter.parsing.abstract_value_parser import StringParser
from ofx_converter.parsing.account_config import AccountConfig
from decimal import Decimal
import re


class MoneyParser(LogMixin, StringParser[Decimal]):
    _value_regex = re.compile("(?P<sign>-)?R\\$ (?P<value>[\\d\\.,]+)$")

    def __init__(
        self, account: AccountConfig, value_regex: re.Pattern[str] = _value_regex
    ) -> None:
        super().__init__()
        self._account_config = account
        self._value_regex = value_regex

    def extract_value(self, value: str) -> Decimal | None:
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
        return Decimal(value_converted)

    def parse(self, input: str | None) -> Decimal | None:
        if input is None:
            return None
        value_converted = self.extract_value(input)
        if value_converted is None:
            return None
        value_signed = self.get_credit_debit_sign() * value_converted
        return value_signed

    def get_credit_debit_sign(self) -> Literal[-1, 1]:
        if self._account_config.account_type.is_liability:
            sign = -1
        else:
            sign = 1
        return sign
