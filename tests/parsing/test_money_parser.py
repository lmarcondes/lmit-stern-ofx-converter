from decimal import Decimal
import re

from ofx_converter.parsing.account import Account
from ofx_converter.parsing.account_config import AccountConfig
from ofx_converter.parsing.money_parser import MoneyParser
from tests.base_test_case import BaseTestCase


class MoneyParsingTestSuite(BaseTestCase):

    @staticmethod
    def _round_decimal(decimal: Decimal | None, places: int = 2) -> Decimal | None:
        decimal_rounded = round(decimal, places) if decimal is not None else decimal
        return decimal_rounded

    def test_xp_credit_card_account(self):
        account = Account("xpi-cartao")
        config = AccountConfig(account)
        regex = re.compile("R\\$ (?P<sign>-)?(?P<value>[\\d\\.,]+)$")
        parser = MoneyParser(config, value_regex=regex)
        test_cases = [
            ("R$ 1.439,80", Decimal(-1439.80)),
            ("R$ -5.186,66", Decimal(5186.66)),
            ("-R$ 1.439,80", None),
        ]
        for input, expected in test_cases:
            result = parser.parse(input)
            expected_rounded = self._round_decimal(expected)
            result_rounded = self._round_decimal(result)
            self.assertEqual(result_rounded, expected_rounded)

    def test_xp_checking_account(self):
        account = Account("xpi-conta")
        config = AccountConfig(account)
        regex = re.compile("(?P<sign>-)?R\\$ (?P<value>[\\d\\.,]+)$")
        parser = MoneyParser(config, value_regex=regex)
        test_cases = [
            ("R$ 1.439,80", Decimal(1439.80)),
            ("R$ -5.186,66", None),
            ("-R$ 1.439,80", Decimal(-1439.80)),
        ]
        for input, expected in test_cases:
            result = parser.parse(input)
            expected_rounded = self._round_decimal(expected)
            result_rounded = self._round_decimal(result)
            self.assertEqual(result_rounded, expected_rounded)
